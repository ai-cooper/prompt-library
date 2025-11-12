import os
import time
import threading
import gc
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# ---- Config (defaults aim for ~15 MB/min) ----
CHUNK_MB_DEFAULT = int(os.getenv("LEAK_CHUNK_MB", "1"))     # MB allocated per tick
TICK_SEC_DEFAULT = int(os.getenv("LEAK_TICK_SEC", "4"))     # 60/4 * 1MB = 15 MB/min
# You can also set LEAK_MB_PER_MIN to auto-derive tick; otherwise defaults apply.

app = FastAPI(title="Intentional Memory Leak Demo")

_leak_store = []                 # holds references so GC can't reclaim
_stop_event = threading.Event()
_worker: Optional[threading.Thread] = None
_stats = {"alloc_chunks": 0, "alloc_bytes": 0, "chunk_mb": CHUNK_MB_DEFAULT, "tick_sec": TICK_SEC_DEFAULT}

def _bytes_from_mb(mb: int) -> int:
    return mb * 1024 * 1024

def _calc_default_params():
    mb_per_min = os.getenv("LEAK_MB_PER_MIN")
    if mb_per_min:
        target = int(mb_per_min)
        # keep chunk size at 1 MB, adjust tick so 60 / tick * 1MB ≈ target
        chunk_mb = 1
        tick = max(1, round(60 / max(1, target)))
    else:
        chunk_mb = CHUNK_MB_DEFAULT
        tick = TICK_SEC_DEFAULT
    return chunk_mb, tick

def _leak_loop(chunk_mb: int, tick_sec: int):
    chunk_bytes = _bytes_from_mb(chunk_mb)
    while not _stop_event.is_set():
        # allocate and KEEP a reference
        _leak_store.append(bytearray(chunk_bytes))
        _stats["alloc_chunks"] += 1
        _stats["alloc_bytes"] += chunk_bytes
        time.sleep(tick_sec)

def _rss_mb() -> float:
    # Try psutil; fall back to /proc/self/statm
    try:
        import psutil
        p = psutil.Process()
        return p.memory_info().rss / (1024 * 1024)
    except Exception:
        try:
            with open("/proc/self/statm") as f:
                parts = f.read().split()
            rss_pages = int(parts[1])
            import resource
            page = resource.getpagesize()
            return (rss_pages * page) / (1024 * 1024)
        except Exception:
            return -1.0

@app.get("/")
def root():
    return {"message": "Intentional memory leak demo. Use /leak/start, /leak/stop, /status."}

@app.post("/leak/start")
def leak_start(mb_per_min: Optional[int] = None, chunk_mb: Optional[int] = None, tick_sec: Optional[int] = None):
    global _worker
    if _worker and _worker.is_alive():
        return JSONResponse({"status": "already_running", **_stats})

    if mb_per_min is not None and (chunk_mb is None and tick_sec is None):
        # derive from mb_per_min with 1 MB chunks
        chunk_mb = 1
        tick_sec = max(1, round(60 / max(1, mb_per_min)))
    else:
        # use provided values or defaults
        if chunk_mb is None or tick_sec is None:
            d_chunk, d_tick = _calc_default_params()
            chunk_mb = d_chunk if chunk_mb is None else chunk_mb
            tick_sec = d_tick if tick_sec is None else tick_sec

    # reset state
    _stop_event.clear()
    _stats.update({"alloc_chunks": 0, "alloc_bytes": 0, "chunk_mb": chunk_mb, "tick_sec": tick_sec})
    _worker = threading.Thread(target=_leak_loop, args=(chunk_mb, tick_sec), daemon=True)
    _worker.start()
    return {"status": "started", "chunk_mb": chunk_mb, "tick_sec": tick_sec, "approx_mb_per_min": (60 / tick_sec) * chunk_mb}

@app.post("/leak/stop")
def leak_stop(free_memory: bool = False):
    _stop_event.set()
    if free_memory:
        _leak_store.clear()
        gc.collect()
    return {"status": "stopped", "freed": bool(free_memory)}

@app.get("/status")
def status():
    return {
        "running": (_worker is not None and _worker.is_alive()),
        "rss_mb": round(_rss_mb(), 2),
        "alloc_chunks": _stats["alloc_chunks"],
        "alloc_mb_total": round(_stats["alloc_bytes"] / (1024 * 1024), 2),
        "chunk_mb": _stats["chunk_mb"],
        "tick_sec": _stats["tick_sec"],
        "approx_mb_per_min": (60 / _stats["tick_sec"]) * _stats["chunk_mb"],
        "leak_store_len": len(_leak_store),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)

