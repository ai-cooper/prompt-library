# COMPREHENSIVE MEMORY LEAK ANALYSIS REPORT
## Python Process 277478 - Dynamic Memory Analysis

**Analysis Date:** November 7, 2025  
**Analyst:** Linux Performance and Memory Debug Expert  
**Target:** Python Process PID 277478  
**Duration:** 2 minutes (24 samples at 5-second intervals)  
**Tool:** BCC memleak (eBPF-based dynamic tracing)

---

## EXECUTIVE SUMMARY

**Critical Finding: CONFIRMED MEMORY LEAK**

A **severe memory leak** was detected in Python process 277478 (`python app.py`). The application exhibits **consistent unbounded memory growth** at a rate of approximately **15-18 MB per minute** (~900-1080 MB/hour).

### Key Metrics

| Metric | Value |
|--------|-------|
| **Target Process** | PID 277478 (Python 3.12) |
| **Current RSS** | 311 MB (and growing) |
| **Leak Rate** | ~15 MB/min |
| **Time Running** | 17+ minutes |
| **Memory Allocated** | ~31.5 MB during 2-minute analysis window |
| **Risk Level** | 🔴 **CRITICAL** - Will exhaust available memory |

**Root Cause:** Intentional memory leak in application code - unbounded list growth storing bytearray objects without eviction policy.

---

## STEP 1: PROCESS INFORMATION

### Initial State

```
PID: 277478
COMMAND: python app.py
RSS: 263,652 KB (257 MB)
VSZ: 643,548 KB (628 MB)
STATUS: Sl+ (Sleeping, multithreaded, foreground)
ELAPSED: 14:33 (14 minutes 33 seconds)
THREADS: 3
```

### Memory Breakdown (from /proc/277478/status)

| Memory Type | Size | Description |
|-------------|------|-------------|
| **VmPeak** | 644 MB | Peak virtual memory |
| **VmSize** | 644 MB | Current virtual memory |
| **VmRSS** | 265 MB | Physical memory (resident) |
| **VmData** | 269 MB | Program data segment |
| **VmStk** | 136 KB | Stack size |
| **VmLib** | 12.5 MB | Shared libraries |

### Memory Growth Validation (10-second interval)

```
Before:  RSS = 307,940 KB (301 MB)
After:   RSS = 311,012 KB (304 MB)
Growth:  3,072 KB (~3 MB) in 10 seconds
Rate:    ~18 MB/minute or 1,080 MB/hour
```

### Loaded Python C Extensions

- **pydantic_core** (4.88 MB) - Data validation library
- **psutil** (146 KB) - System monitoring
- **_ssl** (176 KB) - SSL/TLS support
- **_pickle** (130 KB) - Object serialization

---

## STEP 2: MEMLEAK ANALYSIS OUTPUT

### Analysis Parameters

- **Duration:** 2 minutes (120 seconds)
- **Sampling Interval:** 5 seconds
- **Total Samples:** 24
- **Method:** eBPF-based dynamic tracing via BCC

### Memory Allocation Timeline

| Time | _PyObject_Malloc | sysmalloc_mmap | Total Outstanding |
|------|------------------|----------------|-------------------|
| 10:06:02 | 1.00 MB (1 alloc) | 1.00 MB (1 alloc) | 2.00 MB |
| 10:06:17 | 5.00 MB (5 allocs) | 5.02 MB (5 allocs) | 10.02 MB |
| 10:06:37 | 10.00 MB (10 allocs) | 10.03 MB (10 allocs) | 20.03 MB |
| 10:06:57 | 15.00 MB (15 allocs) | 15.04 MB (15 allocs) | 30.04 MB |
| 10:07:57 | **31.46 MB (30 allocs)** | **31.58 MB (30 allocs)** | **63.04 MB** |

**Growth Pattern:** Linear, consistent ~1 MB allocation every 5 seconds

### Additional Allocations Detected

- **list_resize**: 2,144 bytes (1 allocation) - Python list internal resize
- **PyMem_Malloc**: 2,112 bytes (4 allocations) - Small memory allocations

---

## STEP 3: DETAILED ANALYSIS - TOP 5 ALLOCATION SOURCES

### #1: _PyObject_Malloc - CPython Object Allocator

```
[CRITICAL LEAK SOURCE]
Allocation: 31,457,310 bytes (30.99 MB)
Allocations: 30 calls
Average Size: 1,048,577 bytes (~1 MB per call)
Growth Rate: ~15 MB/minute

Stack Trace:
    0x00007f79a2f6b07c  _PyObject_Malloc+0x12c [libpython3.12.so.1.0]
```

#### Analysis

| Property | Value |
|----------|-------|
| **TYPE** | Application-Level Leak (via CPython allocator) |
| **RISK** | 🔴 CRITICAL |
| **LEAK MECHANISM** | Unbounded container growth |
| **PYTHON OBJECT** | bytearray objects |
| **ROOT CAUSE** | app.py:41 - `_leak_store.append(bytearray(chunk_bytes))` |
| **IMPACT** | Linear memory growth without bound |

#### Application Code Context

```python
37| def _leak_loop(chunk_mb: int, tick_sec: int):
38|     chunk_bytes = _bytes_from_mb(chunk_mb)
39|     while not _stop_event.is_set():
40|         # allocate and KEEP a reference
41|         _leak_store.append(bytearray(chunk_bytes))  ← LEAK SOURCE
42|         _stats["alloc_chunks"] += 1
43|         _stats["alloc_bytes"] += chunk_bytes
44|         time.sleep(tick_sec)
```

#### Global Variable

```python
17| _leak_store = []  # holds references so GC can't reclaim
```

#### CPython vs Application

- **CPython Behavior:** ✅ NORMAL - _PyObject_Malloc is correctly allocating
- **Application Code:** ❌ LEAK - Never releases references from _leak_store
- **Reference Count:** Each bytearray has refcount ≥ 1 (held by list)
- **GC Status:** Cannot collect (reachable from global)

#### Verification

- Default config: 1 MB every 4 seconds = 15 MB/min
- Observed: 1 MB every 5 seconds = 12 MB/min (slightly different timing)
- Pattern: Matches application behavior exactly

#### Recommendation

```python
# Fix #1: Add size limit with LRU eviction
from collections import deque
_leak_store = deque(maxlen=100)  # Keep only last 100 chunks

# Fix #2: Add periodic cleanup
if len(_leak_store) > 1000:
    _leak_store = _leak_store[-100:]  # Keep only recent 100
    gc.collect()

# Fix #3: Use weak references (if objects can be recreated)
import weakref
_leak_store = weakref.WeakValueDictionary()
```

---

### #2: sysmalloc_mmap.isra.0 - System Memory Mapping

```
[UNDERLYING SYSTEM ALLOCATION]
Allocation: 31,580,160 bytes (30.12 MB)
Allocations: 30 calls
Average Size: 1,052,672 bytes (~1 MB per call)

Stack Trace:
    0x00007f79a2cc9308  sysmalloc_mmap.isra.0+0x48 [libc.so.6]
```

#### Analysis

| Property | Value |
|----------|-------|
| **TYPE** | Native Library Allocation (glibc malloc) |
| **RISK** | 🔴 CRITICAL (mirrors #1) |
| **LEAK MECHANISM** | System-level backing for Python objects |
| **PYTHON OBJECT** | N/A (low-level memory mapping) |
| **ROOT CAUSE** | Same as #1 - backing memory for bytearray objects |
| **IMPACT** | Tracks _PyObject_Malloc exactly |

#### CPython vs Native

- This is NOT a separate leak
- glibc's malloc uses mmap() for large allocations (>128 KB)
- Python's bytearray (1 MB) exceeds threshold
- System automatically mmaps memory pages
- Will be freed when Python releases the objects

#### Relationship

```
Python App → _PyObject_Malloc → malloc → mmap → Kernel
                 ↑                            ↑
              (#1 Leak)                  (#2 Symptom)
```

#### Recommendation

Fix #1 (application code) - this will automatically resolve

---

### #3: list_resize - Python List Growth

```
[MINOR LEAK - List Internal]
Allocation: 2,144 bytes (2.09 KB)
Allocations: 1 call
Average Size: 2,144 bytes

Stack Trace:
    0x00007f79a2f7c0d6  list_resize+0x216 [libpython3.12.so.1.0]
    0x00007f79a33ac320  [unknown]
```

#### Analysis

| Property | Value |
|----------|-------|
| **TYPE** | CPython Internal (list capacity management) |
| **RISK** | 🟡 LOW |
| **LEAK MECHANISM** | List over-allocation strategy |
| **PYTHON OBJECT** | _leak_store (list) |
| **ROOT CAUSE** | Normal list growth behavior |
| **IMPACT** | Minimal (~2 KB) |

#### CPython List Internals

- Lists pre-allocate capacity: `capacity = (actual_size * 9) // 8 + 6`
- `list_resize()` grows internal array when capacity exceeded
- This 2 KB allocation is for the list's internal pointer array
- With 30 elements, list needs: 30 * 8 bytes = 240 bytes minimum
- Over-allocation for efficiency: ~2 KB allocated

#### Is This a Leak?

✅ **NO** - This is normal CPython behavior

- Small overhead for list performance
- Will be freed when list is cleared
- Not growing continuously (one-time resize)

#### Reference

Python list growth pattern (cpython/Objects/listobject.c):
```
new_allocated = (size >> 3) + (size < 9 ? 3 : 6) + size
```

#### Recommendation

No action needed - this is expected behavior

---

### #4: PyMem_Malloc.localalias - Python Memory Allocator

```
[MINIMAL ALLOCATION]
Allocation: 2,112 bytes (2.06 KB)
Allocations: 4 calls
Average Size: 528 bytes

Stack Trace:
    0x00007f79a2f6f745  PyMem_Malloc.localalias+0x145 [libpython3.12.so.1.0]
    0x0000000100000001  [unknown]
```

#### Analysis

| Property | Value |
|----------|-------|
| **TYPE** | CPython Internal (small object allocation) |
| **RISK** | 🟢 NEGLIGIBLE |
| **LEAK MECHANISM** | Unknown (insufficient stack trace) |
| **PYTHON OBJECT** | Small Python objects (likely str/int/tuple) |
| **ROOT CAUSE** | Normal interpreter operation |
| **IMPACT** | Trivial (~2 KB total) |

#### Details

- PyMem_Malloc is Python's raw memory API
- Used for small, fixed-size allocations
- 4 allocations of ~500 bytes each
- Likely interpreter internals (strings, tuples, metadata)
- Stack trace truncated ([unknown]) - can't identify exact source

#### Is This a Leak?

⚠️  **UNCLEAR** - insufficient data

- Total size too small to matter (0.002 MB)
- Not growing significantly
- May be one-time allocations
- Could be Python's string interning or other caching

#### Recommendation

Ignore - size too small to be concerning

---

### #5: No Fifth Source Detected

Only 4 distinct allocation patterns were observed. The primary leak (#1) dominates memory consumption.

---

## REFERENCE COUNTING ANALYSIS

### Application Reference Management

```python
# Current Code (LEAKING):
_leak_store = []                          # Module-level global
def _leak_loop(chunk_mb: int, tick_sec: int):
    while not _stop_event.is_set():
        obj = bytearray(chunk_bytes)      # refcount = 1
        _leak_store.append(obj)           # refcount = 2 (temp var + list)
        # obj goes out of scope           # refcount = 1 (only list holds it)
        # Object NEVER freed - list never shrinks
```

### Reference Count Lifecycle

| Event | Object | Refcount | GC Eligible? |
|-------|--------|----------|--------------|
| `bytearray(...)` created | obj | 1 | ❌ No (referenced) |
| `.append(obj)` | obj | 2 | ❌ No (2 refs) |
| `obj` out of scope | obj | 1 | ❌ No (list still holds) |
| Loop continues | obj | 1 | ❌ No (permanent) |
| App exits | obj | 0 | ✅ Yes (finally freed) |

### Python GC Status

```python
# Garbage Collection Analysis
import gc

# Objects are reachable from _leak_store (module global)
# gc.collect() will NOT free them (not garbage, legitimately referenced)

# Reference chain:
sys.modules['__main__']._leak_store[i] → bytearray object
                ↑
         (strong reference)
```

### No Circular References Detected

✅ **Good News:** No reference cycles found

- bytearray objects don't reference back to the list
- No `__del__` methods creating resurrection issues
- No closure capturing preventing collection

❌ **Bad News:** References are **intentionally kept**

- Objects are NOT garbage - they're actively referenced
- GC is working correctly - there's simply no garbage to collect
- Problem is **application logic**, not Python's memory management

---

## PYTHON-SPECIFIC CHECKS

### ✅ PyObject_* Allocation Patterns

**Observed:** `_PyObject_Malloc` allocating ~1 MB chunks consistently

**Analysis:**
- Normal CPython behavior for large objects
- Uses pymalloc for small objects (<512 bytes)
- Falls back to system malloc for large objects
- bytearray(1 MB) exceeds pymalloc threshold → uses malloc → mmap

**Verdict:** CPython is working correctly

---

### ✅ Third-Party C Extension Leaks

**Extensions Loaded:**
- **pydantic_core** (4.88 MB) - Rust-based validation
- **psutil** (146 KB) - System monitoring
- **_ssl**, **_pickle**, **_decimal** - Standard library

**Analysis:**
- No allocations traced to C extensions
- psutil only used in `/status` endpoint (read-only)
- pydantic_core likely used for FastAPI request validation
- No evidence of extension-based leaks

**Verdict:** C extensions are NOT leaking

---

### ⚠️ NumPy/Pandas Array Allocations

**Status:** NOT APPLICABLE

**Analysis:**
- No NumPy or Pandas imported in application
- No scientific computing libraries detected
- Using plain Python bytearray (native CPython)

**Verdict:** N/A - not used in this application

---

### ✅ Database Connection Pooling

**Status:** NOT APPLICABLE

**Analysis:**
- No database libraries loaded (no SQLAlchemy, psycopg2, etc.)
- No `_psycopg` or `mysqlclient` shared objects
- Application is pure computation/API

**Verdict:** N/A - no database connections

---

### 🔍 FastAPI/Uvicorn Memory Behavior

**Framework:** FastAPI + Uvicorn ASGI server

**Analysis:**
- Minimal memory footprint from framework
- No request/response objects leaking
- Thread-based leak is separate from ASGI event loop
- Framework is working correctly

**Verdict:** Framework is NOT the issue

---

## RISK ASSESSMENT TABLE

### Risk Factors

| Risk Factor | Severity | Current Impact | Projected Impact (24h) | Mitigation Priority |
|-------------|----------|----------------|------------------------|---------------------|
| **Application List Growth** | 🔴 **CRITICAL** | 311 MB (17 min) | ~25 GB | **P0 - IMMEDIATE** |
| **Process OOM Kill** | 🔴 **CRITICAL** | Stable | Certain if RAM < 25 GB | **P0 - IMMEDIATE** |
| **System Memory Pressure** | 🟡 **MEDIUM** | None yet | High (swap thrashing) | **P1 - Today** |
| **Performance Degradation** | 🟡 **MEDIUM** | Minimal | Severe (GC overhead) | **P1 - Today** |
| **List Resize Overhead** | 🟢 **LOW** | 2 KB | 10 KB | **P3 - Future** |
| **CPython Internals** | 🟢 **LOW** | Expected | No change | **P4 - None** |

### Memory Exhaustion Timeline

**Assumptions:** 8 GB available RAM for process

| Time | RSS Size | % of 8 GB | Status |
|------|----------|-----------|--------|
| **Now** | 311 MB | 3.8% | 🟢 Healthy |
| **1 hour** | ~1.4 GB | 17.5% | 🟢 Healthy |
| **4 hours** | ~4.6 GB | 57.5% | 🟡 Warning |
| **8 hours** | ~8.9 GB | **111%** | 🔴 **OOM Kill** |
| **24 hours** | ~25 GB | **312%** | 💀 **System Crash** |

**Time to OOM:** Approximately **7-8 hours** (with 8 GB available)

### Business Impact

| Impact Area | Risk Level | Description |
|-------------|------------|-------------|
| **Service Availability** | 🔴 CRITICAL | Process will be killed by OOM killer |
| **System Stability** | 🔴 CRITICAL | May cause system-wide memory pressure |
| **Data Loss** | 🟡 MEDIUM | In-memory data lost on OOM kill |
| **Performance** | 🟡 MEDIUM | GC pauses increase with memory growth |
| **Cost** | 🟢 LOW | Demo app (not production) |

---

## DEBUGGING RECOMMENDATIONS

### IMMEDIATE ACTIONS (Within 1 Hour)

#### 1. Stop the Leak (Production Emergency)

```bash
# Emergency: Stop the leak thread
curl -X POST http://127.0.0.1:8000/leak/stop?free_memory=true

# Verify memory is freed
curl http://127.0.0.1:8000/status
```

#### 2. Monitor Memory in Real-Time

```bash
# Watch RSS growth
watch -n 5 'ps -p 277478 -o pid,rss,vsz,cmd'

# Or use the app's built-in status endpoint
watch -n 5 'curl -s http://127.0.0.1:8000/status | jq'
```

#### 3. Set Memory Limit (Prevent System Impact)

```bash
# Limit process to 2 GB RAM (prevents system-wide impact)
sudo prlimit --pid 277478 --as=2147483648:2147483648  # 2 GB in bytes

# Or restart with systemd ResourceLimit
# [Service]
# MemoryMax=2G
# MemoryHigh=1.5G
```

---

### SHORT-TERM FIXES (Application Code Changes)

#### Fix #1: Add Maximum Size Limit

```python
# app.py - Add at top
MAX_LEAK_STORE_SIZE = 100  # Keep only last 100 chunks

# app.py:41 - Modify leak loop
def _leak_loop(chunk_mb: int, tick_sec: int):
    chunk_bytes = _bytes_from_mb(chunk_mb)
    while not _stop_event.is_set():
        _leak_store.append(bytearray(chunk_bytes))
        
        # NEW: Evict old entries
        if len(_leak_store) > MAX_LEAK_STORE_SIZE:
            _leak_store.pop(0)  # Remove oldest
            
        _stats["alloc_chunks"] += 1
        _stats["alloc_bytes"] += chunk_bytes
        time.sleep(tick_sec)
```

#### Fix #2: Use deque with maxlen (Better Performance)

```python
from collections import deque

# app.py:17 - Replace list with bounded deque
_leak_store = deque(maxlen=100)  # Automatically evicts oldest

# No other code changes needed!
# deque.append() auto-removes leftmost when full
```

#### Fix #3: Add Periodic Cleanup

```python
def _leak_loop(chunk_mb: int, tick_sec: int):
    chunk_bytes = _bytes_from_mb(chunk_mb)
    iterations = 0
    
    while not _stop_event.is_set():
        _leak_store.append(bytearray(chunk_bytes))
        iterations += 1
        
        # NEW: Periodic cleanup every 100 iterations
        if iterations % 100 == 0:
            _leak_store.clear()
            gc.collect()
            print(f"Cleaned up {iterations} allocations")
            
        _stats["alloc_chunks"] += 1
        _stats["alloc_bytes"] += chunk_bytes
        time.sleep(tick_sec)
```

#### Fix #4: Add Memory Threshold Auto-Stop

```python
def _leak_loop(chunk_mb: int, tick_sec: int):
    chunk_bytes = _bytes_from_mb(chunk_mb)
    MAX_RSS_MB = 500  # Stop at 500 MB
    
    while not _stop_event.is_set():
        # NEW: Check memory before allocating
        current_rss = _rss_mb()
        if current_rss > MAX_RSS_MB:
            print(f"Memory limit reached: {current_rss:.1f} MB. Stopping leak.")
            _stop_event.set()
            break
            
        _leak_store.append(bytearray(chunk_bytes))
        _stats["alloc_chunks"] += 1
        _stats["alloc_bytes"] += chunk_bytes
        time.sleep(tick_sec)
```

---

### ADVANCED DEBUGGING (Root Cause Analysis)

#### 1. Python Memory Profiling with tracemalloc

```python
# Add to app.py
import tracemalloc

@app.on_event("startup")
def startup():
    tracemalloc.start()

@app.get("/debug/memory")
def memory_debug():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    return {
        "top_10_allocations": [
            {
                "file": str(stat.traceback),
                "size_mb": stat.size / (1024 * 1024),
                "count": stat.count
            }
            for stat in top_stats[:10]
        ]
    }
```

#### 2. Use objgraph for Reference Tracking

```python
# Install objgraph
# pip install objgraph

# Add endpoint to app.py
import objgraph

@app.get("/debug/objgraph")
def show_growth():
    return {
        "most_common": objgraph.most_common_types(limit=20),
        "bytearray_count": objgraph.count('bytearray'),
        "list_count": objgraph.count('list')
    }

# Show what's keeping objects alive
@app.get("/debug/refs")
def show_refs():
    bytearrays = objgraph.by_type('bytearray')
    if bytearrays:
        return {"backrefs": objgraph.show_backrefs(bytearrays[0], max_depth=5)}
```

#### 3. Use pympler for Detailed Memory Analysis

```python
from pympler import tracker, muppy, summary

tr = tracker.SummaryTracker()

@app.get("/debug/pympler")
def memory_summary():
    tr.print_diff()
    
    all_objects = muppy.get_objects()
    sum1 = summary.summarize(all_objects)
    return {"summary": summary.format_(sum1)}
```

#### 4. Enable Python's Built-in Memory Debugging

```bash
# Run with memory debugging
PYTHONMALLOC=debug python app.py

# Or enable in code
import sys
import gc

gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS)
```

---

### MONITORING & ALERTING

#### 1. Prometheus Metrics (Production-Ready)

```python
# Install: pip install prometheus-client
from prometheus_client import Counter, Gauge, make_asgi_app

# Metrics
memory_bytes = Gauge('python_memory_bytes', 'Process memory in bytes')
leak_store_size = Gauge('leak_store_size', 'Number of items in leak store')

@app.on_event("startup")
async def startup_metrics():
    # Update metrics every 10 seconds
    import asyncio
    async def update_metrics():
        while True:
            memory_bytes.set(_rss_mb() * 1024 * 1024)
            leak_store_size.set(len(_leak_store))
            await asyncio.sleep(10)
    asyncio.create_task(update_metrics())

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

#### 2. Alerting Thresholds

```yaml
# prometheus-alerts.yml
groups:
  - name: memory_leak_alerts
    rules:
      - alert: HighMemoryGrowth
        expr: rate(python_memory_bytes[5m]) > 15000000  # 15 MB/min
        for: 5m
        annotations:
          summary: "Memory growing at {{ $value }} bytes/sec"
          
      - alert: MemoryLeakDetected
        expr: python_memory_bytes > 5000000000  # 5 GB
        for: 1m
        annotations:
          summary: "Process using {{ $value }} bytes (potential leak)"
```

#### 3. Logging Memory Stats

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def _leak_loop(chunk_mb: int, tick_sec: int):
    chunk_bytes = _bytes_from_mb(chunk_mb)
    while not _stop_event.is_set():
        _leak_store.append(bytearray(chunk_bytes))
        _stats["alloc_chunks"] += 1
        _stats["alloc_bytes"] += chunk_bytes
        
        # Log every 10 iterations
        if _stats["alloc_chunks"] % 10 == 0:
            logger.info(
                f"Memory: RSS={_rss_mb():.1f}MB, "
                f"Store={len(_leak_store)} items, "
                f"Allocated={_stats['alloc_bytes']/(1024*1024):.1f}MB"
            )
        
        time.sleep(tick_sec)
```

---

## PLAIN LANGUAGE SUMMARY

### 🔍 What We Found

Your Python application has a **memory leak** - it's like a bucket with a hole, except in this case, it's a bucket that keeps filling up and never empties.

**The Problem:**
- The app creates 1 MB of data every 5 seconds
- It stores this data in a list called `_leak_store`
- The list **never** gets cleaned up
- After 17 minutes, the app has grown to **311 MB**
- At this rate, it will crash in about **8 hours**

### 🎯 Root Cause (In Simple Terms)

Think of it like this:

```
Every 5 seconds:
1. App creates a 1 MB shopping bag full of items
2. App puts the bag on a shelf (_leak_store)
3. The shelf keeps growing and growing
4. Nobody ever removes old bags from the shelf
```

The code responsible:

```python
_leak_store = []  # The shelf

while True:
    _leak_store.append(bytearray(1_MB))  # Add bag to shelf
    # Never remove old bags! ← THE PROBLEM
```

### 🛠️ How to Fix It

**Option 1: Limit the Shelf Size** (Easiest)

```python
# Keep only the last 100 bags
from collections import deque
_leak_store = deque(maxlen=100)  # Auto-removes oldest
```

**Option 2: Periodic Cleanup**

```python
# Every 100 bags, throw away everything
if len(_leak_store) > 100:
    _leak_store.clear()
```

**Option 3: Stop When Full**

```python
# Stop adding bags when memory reaches 500 MB
if memory_usage > 500_MB:
    stop_adding_bags()
```

### 📊 Impact

**Right Now:**
- ✅ System is fine (only using 311 MB)
- ✅ App still responding normally

**In 8 Hours:**
- ⚠️ App will use ~8 GB of memory
- 🔴 Operating system will kill the app (Out of Memory)
- 💥 Any work in progress will be lost

### ✅ What's Actually Working Fine

- Python itself is working correctly
- Memory allocation system is fine
- No bugs in Python's garbage collector
- Third-party libraries (FastAPI, psutil) are fine

This is purely an **application design issue** - the code is doing exactly what it was told to do (store everything forever).

### 🎯 Recommended Action Plan

**TODAY:**
1. Stop the leak: `curl -X POST http://127.0.0.1:8000/leak/stop?free_memory=true`
2. Add a size limit to `_leak_store`
3. Restart the application

**THIS WEEK:**
1. Add memory monitoring alerts
2. Test with production workloads
3. Document the fix

### 📝 IMPORTANT NOTE

Based on the code analysis, this appears to be an **intentional demonstration application** designed to showcase memory leaks for testing/educational purposes. The leak is by design, not a bug.

**If this is a testing/demo app:**
- ✅ It's working as intended
- ✅ Use the `/leak/stop` endpoint to control it
- ✅ Use `free_memory=true` to clean up when done

**If this is supposed to be a production app:**
- 🔴 Remove the leak mechanism entirely
- 🔴 Redesign to not accumulate unbounded data

---

## CONCLUSION

This comprehensive analysis confirms a **CRITICAL memory leak** in Python process 277478. The leak originates from application code (`app.py:41`) where bytearray objects are continuously added to a global list without any eviction policy.

### Key Findings Summary

✅ **CPython is working correctly** - no bugs in Python's memory management  
✅ **C Extensions are not leaking** - pydantic_core and psutil behaving normally  
✅ **No reference counting issues** - objects are intentionally kept alive  
❌ **Application code intentionally leaks** - by design for demonstration purposes

### Memory Leak Characteristics

- **Type:** Application-level unbounded container growth
- **Rate:** ~15-18 MB/minute (1,080 MB/hour)
- **Source:** `_leak_store.append(bytearray(1048576))`
- **Time to OOM:** ~8 hours (assuming 8 GB available RAM)

### Critical Differentiation

**CPython Internals (✅ Normal):**
- `_PyObject_Malloc`: Correctly allocating memory for Python objects
- `list_resize`: Normal list growth overhead (~2 KB)
- `PyMem_Malloc`: Small allocations for interpreter internals

**Application Code (❌ Leaking):**
- Global list accumulating bytearray objects
- No size limits or eviction policy
- Thread continuously allocating without cleanup
- References prevent garbage collection

### Recommended Immediate Action

```bash
# Stop the leak now
curl -X POST http://127.0.0.1:8000/leak/stop?free_memory=true

# Verify cleanup
curl http://127.0.0.1:8000/status
```

---

**Analysis Complete** ✅

All aspects of the memory leak have been thoroughly analyzed with clear separation between CPython internals and application-level issues. The memory leak has been identified, quantified, and comprehensive remediation steps have been provided.

---

**Report Generated:** November 7, 2025  
**Tool Used:** BCC memleak (eBPF tracing)  
**Python Version:** 3.12  
**System:** RHEL 10 (Kernel 6.12.0)

