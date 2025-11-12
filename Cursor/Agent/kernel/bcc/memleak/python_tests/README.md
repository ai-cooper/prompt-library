# Memory Leak Test Application

A FastAPI-based application designed to intentionally create memory leaks for testing memory analysis tools like BCC's `memleak`.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
- [Quick Start](#quick-start)

## Overview

This application simulates controlled memory leaks by allocating memory chunks at configurable intervals and retaining references to prevent garbage collection. It's useful for:

- Testing memory profiling tools
- Learning memory leak detection techniques
- Training on memory analysis with BCC/eBPF tools
- Demonstrating Python memory management issues

## Features

- 🎯 **Configurable leak rate**: Control memory allocation per minute
- 📊 **Real-time monitoring**: REST API to check memory usage
- 🔄 **Start/Stop control**: Toggle leak on demand
- 🧹 **Memory cleanup**: Optional memory release on stop
- 📈 **Statistics tracking**: Track allocations and RSS memory

## Setup

### Prerequisites

- Python 3.12 (or compatible version)
- Linux system (for BCC memleak analysis)
- sudo access (for running memleak)

### Installation

1. **Navigate to the project directory:**

```bash
cd /home/you/test/leak
```

2. **Activate the virtual environment:**

```bash
source venv/bin/activate
```

3. **Verify dependencies are installed:**

```bash
pip list | grep -E "fastapi|uvicorn|psutil"
```

If missing, install:

```bash
pip install fastapi uvicorn psutil
```

## Quick Start

### Terminal 1: Start the Application

```bash
cd /home/you/test/leak
source venv/bin/activate
python app.py
```

The application will start on `http://127.0.0.1:8000`

### Terminal 2: Control the Leak

```bash
# Start the memory leak (default: ~15 MB/min)
curl -X POST http://127.0.0.1:8000/leak/start

# Check status
curl http://127.0.0.1:8000/status

# Stop the leak (keep memory allocated)
curl -X POST http://127.0.0.1:8000/leak/stop

# Stop the leak and free memory
curl -X POST "http://127.0.0.1:8000/leak/stop?free_memory=true"
```

### Terminal 3: Monitor with memleak

```bash
# Get the PID
PID=$(pgrep -f "python app.py")
echo "PID: $PID"

# Run memleak analysis (5 second intervals, 24 samples = 2 minutes)
cd /usr/share/bcc/tools && sudo ./memleak -p $PID 5 24

Or copy and paste the prompt from https://github.com/ai-cooper/prompt-library/blob/main/Cursor/Agent/kernel/bcc/memleak/memleak-sample-prompts.txt
```


