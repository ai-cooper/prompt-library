# Perf Analysis Report

**Host:** rhel10 | **CPU:** Intel Core i7-8650U @ 1.90GHz (4C/8T) | **Kernel:** 6.12.0-124.13.1.el10_1.x86_64  
**Captured:** Thu Apr 30 16:24:42 2026 | **Duration:** 29,946 ms | **Arch:** x86_64 (Skylake)

---

## Executive Summary

- **Root cause:** V8 garbage collection dominates the Node.js process, consuming **~40%** of total system CPU (82% of Node's own CPU time).
- **Impact:** High
- A Node.js application is under severe GC pressure. The V8 heap is triggering continuous concurrent major marking, incremental marking, and sweeping cycles across multiple worker threads. This leaves minimal CPU budget for actual application logic, indicating the application is allocating and discarding objects at a rate that overwhelms the V8 garbage collector.

---

## Recording Metadata

| Field          | Value                                                    |
|----------------|----------------------------------------------------------|
| Command        | `perf record -F 99 -a -g -- sleep 30`                   |
| Event          | `cycles:P` (PERF_COUNT_HW_CPU_CYCLES, precise_ip=3)     |
| Frequency      | 99 Hz                                                    |
| Call Graph     | Frame-pointer based (`-g`)                               |
| Total Samples  | ~1,024                                                   |
| Est. Cycles    | ~24,058,777,254                                          |
| Lost Samples   | 0                                                        |
| RAM            | 15.2 GB                                                  |

---

## CPU Domain Breakdown

| Domain       | Overhead |
|--------------|----------|
| Kernel Space | 53.54%   |
| User Space   | 46.52%   |

The kernel share is inflated by the idle loop (swapper at 41.7%). Excluding idle, the effective split is:

| Domain (active only) | Overhead |
|-----------------------|----------|
| Kernel (non-idle)     | ~11.8%   |
| User Space            | ~46.5%   |

The active workload is overwhelmingly user-space (Node.js V8 GC).

---

## Top Hotspot Functions

### User Space

| Rank | Overhead | Command | Symbol | Subsystem |
|-----:|----------|---------|--------|-----------|
| 1 | 7.39% | node | `ConcurrentMarking::RunMajor` | V8 GC - Concurrent Mark |
| 2 | 5.47% | node | `Sweeper::RawSweep` | V8 GC - Sweep |
| 3 | 5.41% | node | `ProcessStrongHeapObject` (Concurrent) | V8 GC - Concurrent Mark |
| 4 | 3.44% | node | `MemoryChunk hashmap operator[]` | V8 GC - Metadata Lookup |
| 5 | 2.36% | node | `ProcessStrongHeapObject` (Main) | V8 GC - Incremental Mark |
| 6 | 1.66% | node | `ConcurrentMarkingVisitor::ShouldVisit` | V8 GC - Concurrent Mark |
| 7 | 1.22% | node | `HeapObject::SizeFromMap` | V8 GC - Sweep |
| 8 | 1.07% | node | `IteratePointers` (Concurrent) | V8 GC - Concurrent Mark |
| 9 | 0.99% | node | `MarkCompactCollector::ProcessMarkingWorklist` | V8 GC - Mark-Compact |
| 10 | 0.87% | ls | `__strcoll_l` | libc string collation |
| 11 | 0.86% | node | `MainMarkingVisitor::ShouldVisit` | V8 GC - Incremental Mark |
| 12 | 0.63% | node | `pthread_mutex_lock` | libc - mutex |

### Kernel Space

| Rank | Overhead | Command | Symbol | Subsystem |
|-----:|----------|---------|--------|-----------|
| 1 | 26.84% | swapper | `intel_idle_ibrs` | CPU idle (C-state) |
| 2 | 9.30% | swapper | `intel_idle` | CPU idle (C-state) |
| 3 | 0.73% | node | `syscall_return_via_sysret` | Syscall return path |

---

## V8 GC Subsystem Aggregation

| V8 GC Subsystem | CPU Overhead |
|------------------|-------------|
| Concurrent Marking (total) | 16.37% |
| Marking Visitor (concurrent path) | 8.61% |
| Sweeper | 5.47% |
| Main-thread Marking Visitor | 3.90% |
| MemoryChunk hashmap lookups | 3.46% |
| HeapObject::SizeFromMap | 1.22% |
| MarkCompactCollector | 1.01% |
| IncrementalMarking (misc) | 0.02% |
| **Total V8 GC** | **40.06%** |

V8 GC accounts for **40.06% of total system CPU** and **~82% of Node.js CPU time** (48.71% total for node).

---

## Call Graph Analysis

### Dominant Call Path 1: Concurrent GC Workers (~27% of CPU)

All concurrent GC activity flows through a single call chain:

```
start_thread
  └─ PlatformWorkerThread
       └─ DefaultJobWorker::Run
            ├─ ConcurrentMarking::JobTaskMajor::Run
            │    └─ ConcurrentMarking::RunMajor          [7.39%]
            │         ├─ ProcessStrongHeapObject           [5.41%]
            │         │    └─ IteratePointers               [1.07%]
            │         ├─ MemoryChunk hashmap operator[]     [3.44%]
            │         └─ ShouldVisit                        [1.66%]
            └─ SweeperJob::RunImpl
                 └─ SweepNonNewSpaces
                      └─ ParallelSweepPage
                           └─ RawSweep                     [5.47%]
                                └─ SizeFromMap              [1.22%]
```

V8 is running **parallel GC worker threads** via `PlatformWorkerThread`. These perform concurrent major marking and concurrent sweeping, using the `DefaultJobWorker` V8 platform abstraction.

### Dominant Call Path 2: Main-thread Incremental Marking (~6% of CPU)

```
__libc_start_call_main
  └─ node::Start
       └─ NodeMainInstance::Run
            └─ SpinEventLoopInternal
                 └─ uv_run
                      └─ uv__io_poll
                           └─ uv__async_io
                                └─ FlushForegroundTasksInternal
                                     └─ IncrementalMarkingJob::Task::RunInternal
                                          └─ IncrementalMarking::AdvanceAndFinalizeIfComplete
                                               └─ IncrementalMarking::Step
                                                    └─ ProcessMarkingWorklist  [0.99%]
                                                         └─ ProcessStrongHeapObject [2.36%]
                                                              └─ ShouldVisit  [0.86%]
```

The Node.js main event loop (`uv_run` → `uv__io_poll`) is being interrupted by **incremental marking steps** that run as foreground tasks. This directly impacts event loop latency.

### Key Pattern: GC on Both Main Thread and Worker Threads

The V8 GC is active on:
- **Worker threads:** ConcurrentMarking::RunMajor + Sweeper::RawSweep (background)
- **Main thread:** IncrementalMarking::Step via the event loop (foreground, latency-impacting)

This indicates the heap is large enough that concurrent GC alone cannot keep up, forcing incremental marking work onto the main thread.

---

## Process CPU Share

| Process | CPU % |
|---------|-------|
| node | 48.71% |
| swapper (idle) | 41.70% |
| ls | 4.48% |
| sh | 1.35% |
| dbus-broker | 0.43% |
| irq/169-iwlwifi | 0.38% |
| python | 0.35% |
| All others | < 0.35% each |

---

## Shared Object / Module Breakdown

| DSO | Overhead | Category |
|-----|----------|----------|
| `kernel.kallsyms` | 53.03% | Kernel (mostly idle) |
| `node` (binary) | 38.50% | Node.js / V8 engine |
| `libc.so.6` | 4.35% | C library |
| `[unknown]` | 1.21% | JIT / unmapped |
| `[JIT] tid 194877` | 0.81% | V8 JIT compiled code |

---

## Symbol Resolution Check

| Symbol Status | Overhead | Count |
|---------------|----------|-------|
| Resolved | ~98.6% | Majority |
| `[unknown]` | 1.21% | 5 entries |
| `[JIT]` | 0.88% | 2 entries |

The `[unknown]` entries (1.21%) are primarily JIT-compiled JavaScript code that V8 generates at runtime. These cannot be resolved with debuginfo packages -- they require `perf record` with `--call-graph dwarf` or V8's `--perf-prof` flag to map JIT code to JavaScript function names. The `[JIT]` entries confirm V8 JIT activity.

**Impact on accuracy:** Low for GC analysis (GC functions are in the `node` binary, fully resolved). The 1.21% unknown could contain hot JavaScript functions, but the GC dominance is clear regardless.

---

## Bottleneck Classification

| Category | Evidence | Verdict |
|----------|----------|---------|
| **GC-bound (memory pressure)** | 40% of CPU in V8 GC subsystems | **PRIMARY** |
| CPU-bound | 48.71% node CPU, but 82% is GC, not app logic | Indirectly yes |
| Syscall-heavy | syscall_return_via_sysret at 0.73% | No |
| Lock contention | pthread_mutex_lock at 0.63% | Minor |
| I/O-related | No I/O kernel functions in top hotspots | No |

**Conclusion:** This is a **GC-bound / memory-pressure** workload. The Node.js application is allocating objects faster than V8 can reclaim them, resulting in continuous GC cycles that consume 82% of the process's CPU time.

---

## Root Cause Analysis

### Primary: V8 Heap Under Sustained GC Pressure

**Evidence:**
1. `ConcurrentMarking::RunMajor` (7.39%) runs on worker threads -- this is V8's **major (full) GC marking phase**, indicating the old generation heap is being collected.
2. `Sweeper::RawSweep` (5.47%) is the sweep phase of mark-sweep, iterating pages to free dead objects.
3. `MemoryChunk hashmap operator[]` (3.44%) is metadata tracking overhead -- V8 maintains a hash map of memory chunks for concurrent GC safety. High overhead here suggests a large number of heap pages.
4. `IncrementalMarking::Step` is running on the **main thread** via the event loop, meaning GC is directly blocking application progress.
5. `ProcessStrongHeapObject` appears in both concurrent (5.41%) and main-thread (2.36%) paths, showing heap object graph traversal is the most expensive GC operation.

**Root cause chain:**
1. Application allocates objects at a high rate (or retains a large live object graph)
2. V8 old-generation heap grows, triggering major GC cycles
3. Concurrent workers mark and sweep in parallel, consuming ~27% CPU
4. Main-thread incremental marking adds ~6% CPU and introduces event loop latency
5. MemoryChunk hashmap lookups add ~3.5% overhead (scales with heap size)
6. Only ~8-9% of node CPU remains for actual application logic

### Secondary: Minimal Other System Activity

The system is otherwise lightly loaded. `ls` (4.48%) and `sh` (1.35%) appear to be transient shell commands during the recording window. No other significant workloads compete with node.

---

## Recommendations

### Immediate Actions

| Priority | Action | Rationale |
|----------|--------|-----------|
| **Critical** | Profile V8 heap: run `node --inspect` and take a heap snapshot | Identify which objects fill the old generation |
| **Critical** | Set `--max-old-space-size` appropriately | If heap is oversized, constrain it; if undersized, increase to reduce GC frequency |
| **High** | Enable V8 GC tracing: `node --trace-gc --trace-gc-verbose` | Get timestamps, durations, and sizes of each GC cycle |
| **High** | Use `--perf-prof` flag: `node --perf-prof app.js` then re-record with perf | Map JIT code to JS function names to find allocation hotspots |
| **Medium** | Check for memory leaks with `--expose-gc` + heap timeline | If live object count grows monotonically, it's a leak |

### Code-Level Investigations

| Area | What to Look For |
|------|-----------------|
| Object allocation rate | Functions that create many short-lived objects in loops |
| Closures / callbacks | Closures capturing large scope chains unnecessarily |
| Large data structures | Unbounded caches, growing Maps/Sets, retained DOM trees |
| Buffers | Large Buffer allocations that could use pooling |
| JSON.parse/stringify | Repeated parsing of large JSON payloads creates GC pressure |

### System Tuning

| Tuning | Command / Flag |
|--------|---------------|
| Increase V8 heap limit | `node --max-old-space-size=4096 app.js` (4 GB) |
| Use semi-space sizing | `node --max-semi-space-size=64 app.js` (for short-lived objects) |
| Pin node to CPUs | `taskset -c 0-3 node app.js` (dedicate cores) |
| Reduce GC threads | `UV_THREADPOOL_SIZE=4` (if I/O threads compete with GC threads) |

### Additional Data Collection

| Tool | Command | Purpose |
|------|---------|---------|
| V8 GC log | `node --trace-gc app.js 2>gc.log` | GC cycle frequency, pause times, heap sizes |
| V8 perf integration | `node --perf-prof --interpreted-frames-native-stack app.js` | Map JIT → JS functions |
| Heap snapshot | Chrome DevTools via `--inspect` | Identify retained objects |
| perf + DWARF | `perf record -F 99 -a -g --call-graph dwarf -- sleep 30` | Better user-space unwinding |
| bpftrace allocation | `bpftrace -e 'uprobe:node:_ZN2v88internal4Heap*AllocateRaw* { @[ustack()] = count(); }'` | V8 allocation call sites |

---

## Flamegraph

FlameGraph tools (`stackcollapse-perf.pl`, `flamegraph.pl`) are **not installed**. To generate:

```bash
git clone https://github.com/brendangregg/FlameGraph /opt/FlameGraph
perf script -i /root/test/perf.data > /tmp/out.perf
/opt/FlameGraph/stackcollapse-perf.pl /tmp/out.perf > /tmp/out.folded
/opt/FlameGraph/flamegraph.pl /tmp/out.folded > /tmp/flamegraph.svg
```

---

## Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| 1,024 samples (99 Hz × 30s ÷ 8 CPUs) | Statistical precision is moderate; functions < 0.5% may be noise | Increase `-F` to 999 or extend duration |
| `[unknown]` JIT code (1.21%) | JavaScript function names not visible | Use `node --perf-prof` to generate `/tmp/perf-<pid>.map` |
| Frame-pointer call graphs | Some frames may be missing in optimized code | Use `--call-graph dwarf` for better accuracy |
| No heap size data | Cannot determine absolute heap size or GC pause durations | Use `--trace-gc` to get exact measurements |

---

## Keywords

`GC-bound` · `V8 garbage collection` · `memory pressure` · `ConcurrentMarking` · `Sweeper` · `IncrementalMarking` · `Node.js` · `heap allocation` · `event loop latency` · `mark-compact`

---

*Generated from `/root/test/perf.data` (captured Thu Apr 30 16:24:42 2026, 30s system-wide, 99 Hz with call graphs).*
