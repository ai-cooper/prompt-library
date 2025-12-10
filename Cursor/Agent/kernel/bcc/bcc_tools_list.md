# BCC (BPF Compiler Collection) Tools Reference

A comprehensive list of BCC tools available in `/usr/share/bcc/tools/`.

---

## Table of Contents

1. [CPU & Scheduler Tools](#cpu--scheduler-tools)
2. [Memory Tools](#memory-tools)
3. [Disk I/O & Filesystem Tools](#disk-io--filesystem-tools)
4. [Network Tools](#network-tools)
5. [System Calls & Kernel Tools](#system-calls--kernel-tools)
6. [Process & Thread Tools](#process--thread-tools)
7. [Language-Specific Tools](#language-specific-tools)
8. [Tracing & Profiling Tools](#tracing--profiling-tools)
9. [Miscellaneous Tools](#miscellaneous-tools)

---

## CPU & Scheduler Tools

| Tool | Description |
|------|-------------|
| **cpudist** | Summarizes task on-CPU time as a histogram, showing how long tasks spent on CPU before being descheduled. Useful for detecting oversubscription or excessive context switching. |
| **cpuunclaimed** | Samples CPU run queue lengths to determine when there are idle CPUs but queued threads waiting. Reports unclaimed CPU as a system-wide percentage. |
| **profile** | CPU profiler that takes samples of stack traces at timed intervals, frequency counting them in kernel context for efficiency. |
| **runqlat** | Summarizes scheduler run queue latency as a histogram, showing how long tasks spent waiting their turn to run on-CPU. |
| **runqlen** | Summarizes scheduler queue length as a histogram. Shows run queue occupancy by sampling at 99 Hz. |
| **runqslower** | Shows high latency scheduling times between tasks being ready to run and actually running on CPU. |
| **offcputime** | Shows stack traces that were blocked and the total duration they were off-CPU. Measures time threads spent blocked. |
| **offwaketime** | Shows kernel stack traces for blocked threads along with the threads that woke them, and elapsed time from block to wake. |
| **wakeuptime** | Measures when threads block and shows stack traces for threads that performed the wakeup, with total blocked time. |
| **llcstat** | Traces cache reference and cache miss events system-wide, summarizing by PID and CPU. |

---

## Memory Tools

| Tool | Description |
|------|-------------|
| **memleak** | Traces and matches memory allocation/deallocation requests, collects call stacks, and prints allocations that weren't freed. Useful for finding memory leaks. |
| **cachestat** | Shows hits and misses to the file system page cache. |
| **cachetop** | Shows Linux page cache hit/miss statistics including read and write hit % per process in a top-like UI. |
| **slabratetop** | Shows the rate of allocations and total bytes from kernel memory allocation caches (SLAB/SLUB) in a top-like display. |
| **oomkill** | Traces the Linux out-of-memory (OOM) killer and shows basic details per OOM kill event. |
| **swapin** | Counts swapins by process to show which processes are affected by swapping. |
| **shmsnoop** | Traces shm*() syscalls for shared memory operations. |
| **drsnoop** | Traces the direct reclaim system-wide and prints various details. |
| **compactsnoop** | Traces the compact zone system-wide for memory compaction events. |
| **readahead** | Shows performance of read-ahead caching, including unused pages in cache. |

---

## Disk I/O & Filesystem Tools

| Tool | Description |
|------|-------------|
| **biolatency** | Traces block device I/O and records latency distribution as a histogram. |
| **biolatpcts** | Traces block device I/O and prints latency percentiles per I/O type. |
| **biopattern** | Identifies random/sequential disk access patterns. |
| **biosnoop** | Traces block device I/O and prints one line per I/O operation. |
| **biotop** | Block device I/O "top" - summarizes which processes are performing disk I/O. |
| **bitesize** | Shows I/O distribution for requested block sizes by process name. |
| **fileslower** | Shows file-based synchronous reads and writes slower than a threshold. |
| **filetop** | Shows reads and writes by file with process details. |
| **filelife** | Traces short-lived files that were created and deleted during tracing. |
| **filegone** | Traces why files are gone (deleted or renamed). |
| **dirtop** | Shows reads and writes by directory. |
| **vfscount** | Counts VFS calls by tracing kernel functions beginning with "vfs_". |
| **vfsstat** | Traces common VFS calls and prints per-second summaries. |
| **ext4dist** | Traces ext4 reads, writes, opens, and fsyncs; summarizes latency as histogram. |
| **ext4slower** | Shows ext4 operations slower than a threshold. |
| **xfsdist** | Traces XFS reads, writes, opens, and fsyncs; summarizes latency as histogram. |
| **xfsslower** | Shows XFS operations slower than a threshold. |
| **nfsdist** | Traces NFS reads, writes, opens, and getattr; summarizes latency as histogram. |
| **nfsslower** | Shows NFS operations slower than a threshold. |
| **mdflush** | Traces flushes at the md driver level with timing details. |
| **dcstat** | Shows directory entry cache (dcache) statistics. |
| **dcsnoop** | Traces directory entry cache lookups for detailed investigation. |
| **mountsnoop** | Traces mount() and umount syscalls system-wide. |

---

## Network Tools

| Tool | Description |
|------|-------------|
| **tcpconnect** | Traces active TCP connections (via connect() syscall). Shows IP version, source/dest addresses, and port. |
| **tcpaccept** | Traces passive TCP connections (via accept() syscall). |
| **tcpconnlat** | Traces active TCP connections and shows connection latency (SYN to response). |
| **tcplife** | Summarizes TCP sessions that open and close while tracing. |
| **tcpretrans** | Traces kernel TCP retransmit function to show retransmit details. |
| **tcpdrop** | Prints details of TCP packets/segments dropped by kernel, including stack trace. |
| **tcprtt** | Traces TCP round-trip time to analyze network quality. |
| **tcpstates** | Prints TCP state change information with duration in each state. |
| **tcpsubnet** | Summarizes throughput by destination subnet (IPv4 only). |
| **tcpsynbl** | Shows TCP SYN backlog size during SYN arrival as histogram. |
| **tcptop** | Summarizes TCP throughput by host and port. |
| **tcptracer** | Traces TCP connections and closures (connect, accept, close). |
| **tcpcong** | Traces TCP congestion control status changes and calculates duration of each state. |
| **bindsnoop** | Traces socket binding and prints socket options set before bind. |
| **solisten** | Traces when programs want to listen for TCP connections. |
| **gethostlatency** | Traces host name lookup calls (getaddrinfo, gethostbyname) with latency. |
| **sslsniff** | Traces write/send and read/recv functions of OpenSSL, GnuTLS, NSS. Prints data as plain text. |
| **netqtop** | Traces packet transmit and receive on data link layer for a network interface. |
| **sofdsnoop** | Traces FDs passed through unix sockets. |
| **rdmaucma** | Traces RDMA UCMA (Userspace Connection Manager Access) events. |

---

## System Calls & Kernel Tools

| Tool | Description |
|------|-------------|
| **syscount** | Summarizes syscall counts across the system or specific process, with optional latency info. |
| **opensnoop** | Traces open() syscall system-wide and prints various details. |
| **statsnoop** | Traces different stat() syscalls system-wide. |
| **syncsnoop** | Traces sync(), fsync(), fdatasync(), syncfs(), sync_file_range(), msync() calls. |
| **execsnoop** | Traces new processes via execve() syscall. |
| **exitsnoop** | Traces all process terminations and reasons. |
| **killsnoop** | Traces signals sent via kill() syscall. |
| **capable** | Traces calls to cap_capable() function for security capability checks. |
| **hardirqs** | Traces hard interrupts (IRQs) with timing statistics. |
| **softirqs** | Traces soft interrupts with timing statistics. |
| **criticalstat** | Traces atomic critical sections in kernel (spinlocks, disabled interrupts/preemption). |
| **klockstat** | Traces kernel mutex lock events and displays lock statistics. |
| **kvmexit** | Traces VM exit reasons to help reduce frequent exits causing performance problems. |
| **bpflist** | Displays information on running BPF programs and optionally open kprobes/uprobes. |
| **tplist** | Displays kernel tracepoints and USDT probes including their format. |
| **reset-trace** | Resets kernel tracing state if a BCC tool was killed or crashed. |
| **virtiostat** | Traces virtio devices to analyze IO operations and throughput. |

---

## Process & Thread Tools

| Tool | Description |
|------|-------------|
| **pidpersec** | Shows number of new processes created per second by tracing fork(). |
| **threadsnoop** | Traces new threads via pthread_create(). |
| **deadlock** | Detects potential deadlocks by building a mutex wait directed graph and looking for cycles. |
| **cthreads** | Traces thread creation events in Java or raw pthreads. |
| **javathreads** | Traces Java thread creation events with thread names. |
| **ttysnoop** | Watches a tty or pts device and prints the same output appearing on that device. |
| **bashreadline** | Prints bash commands from all running bash shells on the system. |

---

## Language-Specific Tools

### Java Tools

| Tool | Description |
|------|-------------|
| **javacalls** | Summarizes Java method calls with frequency counts and latency. |
| **javaflow** | Traces method entry/exit and prints visual flow graph. |
| **javagc** | Traces garbage collection events in Java. |
| **javaobjnew** | Summarizes new Java object allocations by type and bytes. |
| **javastat** | Top-like tool for monitoring Java events (GC, method calls, allocations). |
| **javathreads** | Traces Java thread creation events. |

### Python Tools

| Tool | Description |
|------|-------------|
| **pythoncalls** | Summarizes Python method calls with frequency and latency. |
| **pythonflow** | Traces Python method entry/exit with visual flow graph. |
| **pythongc** | Traces Python garbage collection events. |
| **pythonstat** | Top-like tool for monitoring Python events. |

### Ruby Tools

| Tool | Description |
|------|-------------|
| **rubycalls** | Summarizes Ruby method calls with frequency and latency. |
| **rubyflow** | Traces Ruby method entry/exit with visual flow graph. |
| **rubygc** | Traces Ruby garbage collection events. |
| **rubyobjnew** | Summarizes Ruby object allocations by type. |
| **rubystat** | Top-like tool for monitoring Ruby events. |

### PHP Tools

| Tool | Description |
|------|-------------|
| **phpcalls** | Summarizes PHP method calls with frequency and latency. |
| **phpflow** | Traces PHP method entry/exit with visual flow graph. |
| **phpstat** | Top-like tool for monitoring PHP events. |

### Perl Tools

| Tool | Description |
|------|-------------|
| **perlcalls** | Summarizes Perl method calls with frequency and latency. |
| **perlflow** | Traces Perl method entry/exit with visual flow graph. |
| **perlstat** | Top-like tool for monitoring Perl events. |

### Tcl Tools

| Tool | Description |
|------|-------------|
| **tclcalls** | Summarizes Tcl method calls with frequency and latency. |
| **tclflow** | Traces Tcl method entry/exit with visual flow graph. |
| **tclobjnew** | Summarizes Tcl object allocations by type. |
| **tclstat** | Top-like tool for monitoring Tcl events. |

### Node.js Tools

| Tool | Description |
|------|-------------|
| **nodegc** | Traces Node.js garbage collection events. |
| **nodestat** | Top-like tool for monitoring Node.js events. |

### C/C++ Object Tools

| Tool | Description |
|------|-------------|
| **cobjnew** | Summarizes C/C++ object allocations by type and bytes. |

---

## Tracing & Profiling Tools

| Tool | Description |
|------|-------------|
| **trace** | Probes functions and displays trace messages if conditions are met. Control message format for arguments and return values. |
| **argdist** | Probes functions and collects parameter values into histograms or frequency counts. |
| **funccount** | Traces functions/tracepoints/USDT probes matching a pattern and prints summary counts. |
| **funclatency** | Times function execution and shows latency distribution. |
| **funcslower** | Shows kernel or user function invocations slower than a threshold. |
| **funcinterval** | Measures intervals between function calls (useful when performance drops due to call frequency, not latency). |
| **stackcount** | Traces functions and frequency counts them with their entire stack trace. |
| **profile** | CPU profiler taking stack trace samples at timed intervals. |

---

## Database Tools

| Tool | Description |
|------|-------------|
| **dbslower** | Traces MySQL or PostgreSQL queries and prints those exceeding a latency threshold. |
| **dbstat** | Traces MySQL or PostgreSQL queries and displays latency histogram. |
| **mysqld_qslower** | Traces MySQL server queries and prints those exceeding a latency threshold. |

---

## Miscellaneous Tools

| Tool | Description |
|------|-------------|
| **wqlat** | Traces work's waiting on workqueue and records queuing latency distribution. |
| **ppchcalls** | Summarizes PowerPC hcall counts with optional latency information. |

---

## Tool Count Summary

| Category | Count |
|----------|-------|
| CPU & Scheduler | 10 |
| Memory | 10 |
| Disk I/O & Filesystem | 22 |
| Network | 18 |
| System Calls & Kernel | 17 |
| Process & Thread | 7 |
| Language-Specific | 27 |
| Tracing & Profiling | 8 |
| Database | 3 |
| Miscellaneous | 2 |
| **Total** | **124** |

---

## Usage Examples

### Basic Examples

```bash
# Trace new processes
sudo /usr/share/bcc/tools/execsnoop

# Trace file opens
sudo /usr/share/bcc/tools/opensnoop

# Trace TCP connections
sudo /usr/share/bcc/tools/tcpconnect

# Disk I/O latency histogram
sudo /usr/share/bcc/tools/biolatency

# CPU profiling
sudo /usr/share/bcc/tools/profile

# Memory leak detection
sudo /usr/share/bcc/tools/memleak -p <PID>

# Syscall counting
sudo /usr/share/bcc/tools/syscount
```

---

## Documentation

Full documentation for each tool is available at:
- `/usr/share/bcc/tools/doc/<toolname>_example.txt`

For example:
```bash
cat /usr/share/bcc/tools/doc/biolatency_example.txt
```

---

*Generated from BCC tools documentation in `/usr/share/bcc/tools/doc/`*

