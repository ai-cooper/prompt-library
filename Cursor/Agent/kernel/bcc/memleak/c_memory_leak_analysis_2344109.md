# Memory Leak Analysis Report — PID 2344109 (`memleak`)

**Date:** 2026-03-27  
**Analyst:** Automated C/C++ Memory Debug Expert  
**Target Binary:** `/root/tmp/memleak`  
**Source File:** `/root/tmp/memleak.c`  
**Analysis Duration:** ~4 minutes of observation  

---

## 1. Executive Summary

| Question | Answer |
|---|---|
| **Is there a memory leak?** | **Yes — definite, confirmed leak** |
| **Confidence level** | **100% — confirmed via source code, RSS telemetry, strace, and disassembly** |
| **Allocation source** | `malloc(1048576)` (1 MB) called once per second in an infinite loop with no corresponding `free()` |
| **Leak rate** | **~1 MB/second**, continuous and unbounded |
| **Time to OOM (estimated)** | On a system with 32 GB free RAM, approximately 9 hours |

**Bottom line:** The program allocates 1 MB of heap memory every second via `malloc()`, writes to it via `memset()`, and never frees it. The pointer is overwritten on each loop iteration, making the previously allocated block permanently unreachable. This is a textbook, unconditional memory leak.

---

## 2. Process Memory Overview

### 2.1 Process Identity

| Field | Value |
|---|---|
| PID | 2344109 |
| Binary | `/root/tmp/memleak` (19,248 bytes, ELF 64-bit, with debug_info, not stripped) |
| Command | `./memleak` |
| User | root (UID 0) |
| Threads | 1 (single-threaded) |
| State | S (sleeping in `nanosleep` / `sleep(1)`) |

### 2.2 Memory Snapshot Timeline

All values in kB. Times are relative to process start.

| Time (etime) | VmRSS | VmData | RssAnon | VmPeak | Notes |
|---|---|---|---|---|---|
| 01:23 | 86,508 | — | — | — | First `ps` reading |
| 01:30 | 90,468 | 89,612 | 89,272 | 93,792 | `/proc/status` reading |
| 01:37 | 93,636 | 92,696 | — | — | Second VM check |
| ~01:42 | 97,660 | — | — | — | `pmap` reading |
| 02:48 | 176,072 | 174,936 | 174,808 | — | Start of RSS tracking |
| 02:50 | 177,920 | 176,992 | 176,656 | — | +2s |
| 02:52 | 180,032 | 179,048 | 178,768 | — | +4s |
| 02:54 | 182,144 | 181,104 | 180,880 | — | +6s |
| 02:56 | 184,256 | 183,160 | 182,992 | — | +8s |
| 02:58 | 186,368 | 185,216 | 185,104 | — | +10s |
| 03:00 | 188,216 | 187,272 | 186,952 | — | +12s |
| 03:02 | 190,328 | 189,328 | 189,064 | — | +14s |
| 03:04 | 192,440 | 191,384 | 191,176 | — | +16s |
| 03:06 | 194,552 | 193,440 | 193,288 | — | +18s |
| 04:16 | 264,248 | 263,344 | 262,984 | 267,524 | Final snapshot |

### 2.3 Growth Characteristics

- **Growth pattern:** Perfectly linear and continuous — ~1,024 kB/second
- **Computed leak rate:** (264,248 − 86,508) kB ÷ (256 − 83) s = **1,027 kB/s ≈ 1.00 MB/s**
- **Expected vs. observed:** Process uptime of 256 seconds × 1 MB/s = ~256 MB expected; observed RSS of 258 MB matches perfectly (the ~2 MB delta is base process overhead: libc, ld, stack, binary segments)
- **Memory type:** 99.5% is anonymous private dirty pages (RssAnon/RSS ratio), indicating heap-allocated and touched memory
- **No swap usage:** VmSwap = 0 kB

### 2.4 Memory Map Analysis

The process has a very simple address space:

| Region | Size | Description |
|---|---|
| `.text` (0x400000) | 4 kB | Executable code |
| `.rodata/.data` (0x600000–0x602000) | 8 kB | Read-only data + globals |
| `[heap]` (0x17a8000) | 132 kB | Traditional brk-based heap (small — glibc uses mmap for large allocs) |
| Anonymous mmap (0x7fecc…–0x7fecd…) | **~150 MB and growing** | glibc malloc's mmap arena for 1 MB allocations |
| libc-2.28.so | 1,776 kB | C library |
| ld-2.28.so | 176 kB | Dynamic linker |
| `[stack]` | 132 kB | Thread stack |

**Key observation:** The `[heap]` segment is only 132 kB because glibc's `malloc` uses `mmap()` (not `brk()`) for allocations ≥ 128 kB (`MMAP_THRESHOLD`). The 1 MB allocations appear as a single large anonymous region that grows with each `malloc()` call. This is confirmed by strace showing **only `mmap` syscalls, no `brk` calls**.

### 2.5 Strace Confirmation

Over a 58-second strace window:

```
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
100.00    0.000545           9        58           mmap
------ ----------- ----------- --------- --------- ----------------
100.00    0.000545           9        58           total
```

- **58 `mmap` calls in 58 seconds** = exactly 1 allocation per second
- **0 `munmap` calls** = no memory is ever freed
- **0 `brk` calls** = all allocations go through mmap, not the traditional heap

---

## 3. Top 5 Suspected Allocation Sources

### #1: `main()` → `malloc(1048576)` — memleak.c:8

| Attribute | Detail |
|---|---|
| **Function** | `main()` at `memleak.c:8` |
| **Stack trace** | `main → malloc → __libc_malloc → mmap` |
| **Allocation size** | 1,048,576 bytes (1 MB) per call |
| **Frequency** | Once per second (controlled by `sleep(1)` on line 17) |
| **Why suspicious** | Pointer `p` is overwritten each iteration; no `free(p)` anywhere in the code |
| **Code location** | Application code (`main()`) |
| **Leak confidence** | **Definite (100%)** |

**This is the only allocation source in the entire program.** There are no other `malloc`, `calloc`, `realloc`, `strdup`, or similar calls.

### #2–#5: Not Applicable

The binary is extremely simple (19 kB, imports only `malloc`, `memset`, `printf`, `perror`, `sleep`, `__libc_start_main`). There are no other allocation sources. The symbol table confirms:
- `malloc@@GLIBC_2.2.5` — imported, used
- `free` — **not imported, never called**

---

## 4. Leak Classification

| Classification | Applicable? | Evidence |
|---|---|---|
| **Heap leak** | **Yes (primary)** | `malloc()` without `free()`; pointer lost each iteration |
| **mmap leak** | **Yes (mechanism)** | glibc services the 1 MB `malloc` via `mmap`; the underlying syscall is `mmap`, but the semantic leak is a heap leak |
| File/resource leak | No | Only stdin/stdout/stderr open; no files, sockets, or other resources |
| Fragmentation / allocator retention | No | Not applicable — memory is genuinely leaked, not retained by the allocator |
| Cache growth | No | No caching logic exists |
| Unknown | No | Leak is fully explained |

**Classification: Definite heap leak via malloc/mmap, 1 MB/second, unbounded.**

---

## 5. Code-Level Hypotheses

### 5.1 Source Code

```c
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void) {
    while (1) {
        size_t size = 1024 * 1024;  // 1 MB
        char *p = malloc(size);
        if (p == NULL) {
            perror("malloc failed");
            return 1;
        }

        memset(p, 'A', size);  // touch the memory so it is really allocated
        printf("Leaked 1 MB at %p\n", (void *)p);

        sleep(1);
    }

    return 0;
}
```

### 5.2 Bug Analysis

**Root cause: Missing `free(p)` before loop iteration**

The variable `p` is declared inside the `while` loop body (line 8). Each iteration:
1. Allocates 1 MB via `malloc` → stores address in `p`
2. Touches all 1 MB via `memset` → forces physical page allocation (RSS growth)
3. Prints the address → confirms the allocation happened
4. Sleeps 1 second → controlled leak rate
5. **Loop restarts** → `p` is reassigned to a new `malloc` result → **the previous 1 MB block's address is permanently lost**

The lost pointer cannot be recovered. The memory is:
- Allocated (glibc knows about it)
- Not referenced by any reachable pointer
- Never freed
- Growing without bound

### 5.3 Specific Bug Pattern

This matches the classic **"lost pointer after reassignment in a loop"** pattern:

```
while (condition) {
    ptr = malloc(N);    // old ptr value lost — previous block leaked
    use(ptr);
    // missing: free(ptr);
}
```

### 5.4 Why `memset` Matters

Without `memset`, Linux would use lazy page allocation (demand paging). The `malloc`'d pages would be mapped but not physically allocated until first write. The `memset(p, 'A', size)` forces the kernel to allocate physical pages, which is why RSS grows in lockstep with the allocation count. This was likely intentional — the program is designed to demonstrate a visible memory leak.

### 5.5 Why the Heap Segment is Small

glibc's `malloc` has a tunable threshold (`MMAP_THRESHOLD`, default 128 kB in glibc 2.28). Allocations larger than this threshold are serviced via `mmap()` rather than `brk()/sbrk()`. Since 1 MB > 128 kB, every allocation creates a new anonymous mmap region. This is why:
- The `[heap]` in `/proc/PID/maps` remains at 132 kB
- The anonymous region at `0x7fecc…` grows continuously
- Strace shows `mmap` calls, not `brk` calls

---

## 6. Risk Assessment Table

| Suspected Source | Severity | Confidence | Operational Impact | Recommended Next Step |
|---|---|---|---|---|
| `malloc(1MB)` in `main()` loop without `free()` | **Critical** | **Definite (100%)** | OOM kill within hours; system instability under memory pressure | Add `free(p)` at end of loop body, or redesign to reuse a single buffer |

---

## 7. Debugging Recommendations

### 7.1 Immediate Fix

Add `free(p)` before the loop continues, or reuse a single buffer:

**Option A — Free each iteration (if the buffer is truly disposable):**
```c
while (1) {
    size_t size = 1024 * 1024;
    char *p = malloc(size);
    if (p == NULL) { perror("malloc failed"); return 1; }
    memset(p, 'A', size);
    printf("Allocated 1 MB at %p\n", (void *)p);
    free(p);       // <-- ADD THIS
    sleep(1);
}
```

**Option B — Allocate once, reuse (more efficient):**
```c
size_t size = 1024 * 1024;
char *p = malloc(size);
if (p == NULL) { perror("malloc failed"); return 1; }
while (1) {
    memset(p, 'A', size);
    printf("Using 1 MB at %p\n", (void *)p);
    sleep(1);
}
free(p);
```

### 7.2 Verification Steps

1. **Rebuild with AddressSanitizer / LeakSanitizer:**
   ```bash
   gcc -g -O0 -fsanitize=address -fsanitize=leak -o memleak_asan memleak.c
   timeout 10 ./memleak_asan
   ```
   LeakSanitizer will report every leaked block at exit.

2. **Valgrind:**
   ```bash
   valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes \
     timeout 10 ./memleak
   ```
   Will report "definitely lost" blocks with full stack traces.

3. **Verify the fix:**
   After applying the fix, monitor RSS:
   ```bash
   ./memleak_fixed &
   watch -n1 'grep VmRSS /proc/$!/status'
   ```
   RSS should stabilize after the first allocation.

### 7.3 General C Memory Leak Prevention Practices

For real-world codebases with similar patterns:

- **Audit all `malloc`/`calloc`/`realloc` calls** — every allocation must have a matching `free` on all code paths (success, error, early return, signal handling)
- **Use ownership conventions** — document which function "owns" a pointer (is responsible for freeing it)
- **Add cleanup labels** — use `goto cleanup;` pattern for C error handling to ensure resources are freed
- **Instrument with counters** — add `alloc_count`/`free_count` globals during development to detect imbalances
- **Use `malloc`/`free` wrapper macros** — log allocations during debug builds
- **Run CI with ASan/LSan** — catch leaks automatically in tests
- **Review loops carefully** — any `malloc` inside a loop without a corresponding `free` in the same loop body is suspect
- **Check `strdup`/`asprintf` return values** — these allocate memory that callers must free
- **Audit error paths** — `if (error) return -1;` before `free(p)` is a common leak source

---

## 8. Plain Language Summary

**What is happening:**  
The program `memleak` is asking the computer for 1 megabyte of memory every second, using it briefly, and then forgetting about it — without ever giving the memory back. Think of it like borrowing a book from a library every second but never returning any of them. Eventually, the library runs out of books (the computer runs out of memory).

**How fast is it growing:**  
Memory usage grows by about 1 MB every second. At this rate, the program would consume all available memory on a typical server within a few hours, at which point the operating system would forcibly kill it (OOM kill) or the system would become unresponsive.

**What was observed:**  
- When first checked (~83 seconds after start): using ~85 MB  
- After ~4 minutes: using ~258 MB  
- Growth is perfectly steady — no pauses, no bursts, just relentless 1 MB/second accumulation

**What needs to happen:**  
The developer needs to add one line of code — `free(p);` — to give back each megabyte after using it. Alternatively, the program should allocate one buffer and reuse it instead of allocating a new one every second.

**Is this urgent:**  
If this pattern exists in a production service, yes. The process will eventually consume all available memory and either crash or destabilize the host. The fix is trivial.

---

## Appendix A: GDB Stack Trace

```
Thread 1 (process 2344109):
#0  __GI___nanosleep (requested_time=0x7ffc601b11c0, remaining=0x7ffc601b11c0)
    at ../sysdeps/unix/sysv/linux/nanosleep.c:28
#1  __sleep (seconds=0) at ../sysdeps/posix/sleep.c:55
#2  0x0000000000400728 in main () at memleak.c:17
```

Confirms the process is single-threaded, spending most of its time in `sleep(1)`, and the leak occurs in `main()` at line 17 (the `sleep` call following the un-freed `malloc`).

## Appendix B: Disassembly Confirmation

```
4006cd:  callq  4005a0 <malloc@plt>     ; malloc(1048576)
4006d2:  mov    %rax,-0x10(%rbp)        ; store result in local 'p'
4006d6:  cmpq   $0x0,-0x10(%rbp)        ; NULL check
4006db:  jne    4006f3 <main+0x3d>      ; branch if non-NULL
```

The binary contains **one call to `malloc@plt`** and **zero calls to `free@plt`**. The `free` symbol does not appear in the import table at all, confirming the leak at the binary level.

## Appendix C: Binary Metadata

| Property | Value |
|---|---|
| Path | `/root/tmp/memleak` |
| Size | 19,248 bytes |
| Format | ELF 64-bit LSB executable, x86-64 |
| Linker | dynamically linked (libc-2.28.so, ld-2.28.so) |
| Debug info | Present (`with debug_info, not stripped`) |
| Symbols | Full symbol table (111 entries) |
| Compiler | GCC (inferred from annotations) |

---

*Report generated: 2026-03-27 | Analysis target: PID 2344109 (`/root/tmp/memleak`)*
