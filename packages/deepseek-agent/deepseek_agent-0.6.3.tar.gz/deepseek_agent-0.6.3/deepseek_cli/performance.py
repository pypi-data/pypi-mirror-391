"""Performance optimization module with caching, pooling, and async enhancements."""

from __future__ import annotations

import asyncio
import functools
import hashlib
import pickle
import time
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

import aiofiles
import numpy as np
from asyncio import Queue, Semaphore
from contextvars import ContextVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# Context variables for request tracking
request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
request_start_time: ContextVar[Optional[float]] = ContextVar("request_start_time", default=None)


class CacheStrategy(Enum):
    """Cache replacement strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live based


@dataclass
class CacheEntry(Generic[V]):
    """Entry in cache with metadata."""
    value: V
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    ttl: Optional[float] = None

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

    def access(self) -> None:
        """Record an access to this entry."""
        self.access_count += 1
        self.last_access = time.time()


class AdvancedCache(Generic[K, V]):
    """Advanced cache with multiple eviction strategies."""

    def __init__(
        self,
        max_size: int = 1000,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl: Optional[float] = None
    ):
        self.max_size = max_size
        self.strategy = strategy
        self.default_ttl = default_ttl
        self._cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

    async def get(self, key: K) -> Optional[V]:
        """Get value from cache."""
        async with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats["misses"] += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._stats["misses"] += 1
                return None

            # Update access info
            entry.access()
            self._stats["hits"] += 1

            # Move to end for LRU
            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(key)

            return entry.value

    async def set(
        self,
        key: K,
        value: V,
        ttl: Optional[float] = None
    ) -> None:
        """Set value in cache."""
        async with self._lock:
            # Check if we need to evict
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict()

            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl
            )
            self._cache[key] = entry

            # Move to end for LRU
            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(key)

    async def _evict(self) -> None:
        """Evict entry based on strategy."""
        if not self._cache:
            return

        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used (first item)
            self._cache.popitem(last=False)

        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            min_entry = min(
                self._cache.items(),
                key=lambda x: x[1].access_count
            )
            del self._cache[min_entry[0]]

        elif self.strategy == CacheStrategy.FIFO:
            # Remove oldest (first item)
            self._cache.popitem(last=False)

        elif self.strategy == CacheStrategy.TTL:
            # Remove expired entries first
            expired = [
                k for k, v in self._cache.items()
                if v.is_expired()
            ]
            if expired:
                for k in expired:
                    del self._cache[k]
            else:
                # Fall back to FIFO
                self._cache.popitem(last=False)

        self._stats["evictions"] += 1

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0
        return {
            **self._stats,
            "size": len(self._cache),
            "hit_rate": hit_rate
        }


class DiskCache:
    """Persistent disk-based cache for large objects."""

    def __init__(self, cache_dir: Path, max_size_mb: int = 1000):
        self.cache_dir = cache_dir
        self.max_size_mb = max_size_mb
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index: Dict[str, Dict[str, Any]] = {}
        self._load_index()

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"

    def _load_index(self) -> None:
        """Load cache index from disk."""
        index_path = self.cache_dir / "index.json"
        if index_path.exists():
            import json
            try:
                with open(index_path, "r") as f:
                    self._index = json.load(f)
            except Exception:
                self._index = {}

    def _save_index(self) -> None:
        """Save cache index to disk."""
        import json
        index_path = self.cache_dir / "index.json"
        with open(index_path, "w") as f:
            json.dump(self._index, f)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        if key not in self._index:
            return None

        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            del self._index[key]
            return None

        # Check expiration
        meta = self._index[key]
        if meta.get("expires") and time.time() > meta["expires"]:
            await self.delete(key)
            return None

        try:
            async with aiofiles.open(cache_path, "rb") as f:
                data = await f.read()
                return pickle.loads(data)
        except Exception:
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None
    ) -> bool:
        """Set value in disk cache."""
        try:
            data = pickle.dumps(value)
            size_mb = len(data) / (1024 * 1024)

            # Check size limit
            if size_mb > self.max_size_mb:
                return False

            # Evict if necessary
            await self._evict_if_needed(size_mb)

            cache_path = self._get_cache_path(key)
            async with aiofiles.open(cache_path, "wb") as f:
                await f.write(data)

            # Update index
            self._index[key] = {
                "size_mb": size_mb,
                "timestamp": time.time(),
                "expires": time.time() + ttl if ttl else None
            }
            self._save_index()

            return True
        except Exception:
            return False

    async def delete(self, key: str) -> None:
        """Delete entry from cache."""
        if key in self._index:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
            del self._index[key]
            self._save_index()

    async def _evict_if_needed(self, required_mb: float) -> None:
        """Evict old entries if needed."""
        total_size = sum(meta["size_mb"] for meta in self._index.values())

        if total_size + required_mb <= self.max_size_mb:
            return

        # Sort by timestamp and evict oldest
        sorted_entries = sorted(
            self._index.items(),
            key=lambda x: x[1]["timestamp"]
        )

        for key, meta in sorted_entries:
            await self.delete(key)
            total_size -= meta["size_mb"]
            if total_size + required_mb <= self.max_size_mb:
                break


class ConnectionPool:
    """Connection pool for reusing expensive connections."""

    def __init__(
        self,
        create_func: Callable[[], Any],
        max_size: int = 10,
        max_idle_time: float = 300.0
    ):
        self.create_func = create_func
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self._pool: Queue = Queue(maxsize=max_size)
        self._semaphore = Semaphore(max_size)
        self._connections: Dict[int, float] = {}

    async def acquire(self) -> Any:
        """Acquire connection from pool."""
        await self._semaphore.acquire()

        try:
            while not self._pool.empty():
                conn = await self._pool.get()
                conn_id = id(conn)

                # Check if connection is still valid
                if conn_id in self._connections:
                    idle_time = time.time() - self._connections[conn_id]
                    if idle_time < self.max_idle_time:
                        return conn
                    # Connection too old, close it
                    await self._close_connection(conn)

            # Create new connection
            return await asyncio.get_event_loop().run_in_executor(
                None, self.create_func
            )
        except:
            self._semaphore.release()
            raise

    async def release(self, conn: Any) -> None:
        """Release connection back to pool."""
        conn_id = id(conn)
        self._connections[conn_id] = time.time()

        try:
            self._pool.put_nowait(conn)
        except asyncio.QueueFull:
            # Pool is full, close connection
            await self._close_connection(conn)
        finally:
            self._semaphore.release()

    async def _close_connection(self, conn: Any) -> None:
        """Close a connection."""
        conn_id = id(conn)
        if conn_id in self._connections:
            del self._connections[conn_id]

        # Try to close connection if it has a close method
        if hasattr(conn, "close"):
            if asyncio.iscoroutinefunction(conn.close):
                await conn.close()
            else:
                conn.close()


class BatchProcessor:
    """Process items in batches for efficiency."""

    def __init__(
        self,
        process_func: Callable[[List[Any]], Any],
        batch_size: int = 100,
        batch_timeout: float = 1.0
    ):
        self.process_func = process_func
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self._queue: Queue = Queue()
        self._processing = False

    async def add(self, item: Any) -> None:
        """Add item to batch queue."""
        await self._queue.put(item)

        if not self._processing:
            asyncio.create_task(self._process_batches())

    async def _process_batches(self) -> None:
        """Process batches of items."""
        self._processing = True
        batch = []
        last_process = time.time()

        try:
            while True:
                try:
                    timeout = self.batch_timeout - (time.time() - last_process)
                    if timeout <= 0:
                        timeout = 0.01

                    item = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=timeout
                    )
                    batch.append(item)

                    # Process if batch is full
                    if len(batch) >= self.batch_size:
                        await self._process_batch(batch)
                        batch = []
                        last_process = time.time()

                except asyncio.TimeoutError:
                    # Process whatever we have
                    if batch:
                        await self._process_batch(batch)
                        batch = []
                        last_process = time.time()

                    # Stop if queue is empty
                    if self._queue.empty():
                        break

        finally:
            self._processing = False

            # Process remaining items
            if batch:
                await self._process_batch(batch)

    async def _process_batch(self, batch: List[Any]) -> None:
        """Process a single batch."""
        if asyncio.iscoroutinefunction(self.process_func):
            await self.process_func(batch)
        else:
            await asyncio.get_event_loop().run_in_executor(
                None, self.process_func, batch
            )


class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(
        self,
        max_calls: int,
        time_window: float = 1.0,
        burst_size: Optional[int] = None
    ):
        self.max_calls = max_calls
        self.time_window = time_window
        self.burst_size = burst_size or max_calls
        self._calls: List[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait if necessary to respect rate limit."""
        async with self._lock:
            now = time.time()

            # Remove old calls outside window
            self._calls = [
                t for t in self._calls
                if now - t < self.time_window
            ]

            # Check burst limit
            if len(self._calls) >= self.burst_size:
                # Wait until oldest call expires
                sleep_time = self.time_window - (now - self._calls[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()

            # Check rate limit
            if len(self._calls) >= self.max_calls:
                # Calculate when we can make next call
                sleep_time = self.time_window - (now - self._calls[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()

            # Record this call
            self._calls.append(now)


class MemoryOptimizer:
    """Memory optimization utilities."""

    @staticmethod
    def estimate_size(obj: Any) -> int:
        """Estimate memory size of object in bytes."""
        import sys
        size = sys.getsizeof(obj)

        if isinstance(obj, dict):
            size += sum(
                MemoryOptimizer.estimate_size(k) +
                MemoryOptimizer.estimate_size(v)
                for k, v in obj.items()
            )
        elif isinstance(obj, (list, tuple, set)):
            size += sum(MemoryOptimizer.estimate_size(item) for item in obj)

        return size

    @staticmethod
    def compress_data(data: bytes) -> bytes:
        """Compress data using gzip."""
        import gzip
        return gzip.compress(data)

    @staticmethod
    def decompress_data(data: bytes) -> bytes:
        """Decompress gzip data."""
        import gzip
        return gzip.decompress(data)

    @staticmethod
    def optimize_string_storage(strings: List[str]) -> Tuple[List[int], List[str]]:
        """Optimize storage of repeated strings using interning."""
        string_pool = {}
        indices = []

        for s in strings:
            if s not in string_pool:
                string_pool[s] = len(string_pool)
            indices.append(string_pool[s])

        return indices, list(string_pool.keys())


# Decorators for performance optimization

def memoize(maxsize: int = 128, ttl: Optional[float] = None):
    """Memoization decorator with TTL support."""
    def decorator(func: Callable) -> Callable:
        cache = AdvancedCache[str, Any](
            max_size=maxsize,
            strategy=CacheStrategy.LRU,
            default_ttl=ttl
        )

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = str((args, tuple(sorted(kwargs.items()))))

            # Check cache
            result = await cache.get(key)
            if result is not None:
                return result

            # Execute function
            result = await func(*args, **kwargs)
            await cache.set(key, result)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = str((args, tuple(sorted(kwargs.items()))))

            # Check cache
            result = asyncio.run(cache.get(key))
            if result is not None:
                return result

            # Execute function
            result = func(*args, **kwargs)
            asyncio.run(cache.set(key, result))
            return result

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def rate_limit(max_calls: int, time_window: float = 1.0):
    """Rate limiting decorator."""
    limiter = RateLimiter(max_calls, time_window)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            await limiter.acquire()
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            asyncio.run(limiter.acquire())
            return func(*args, **kwargs)

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def profile_performance(func: Callable) -> Callable:
    """Profile function performance."""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        start_memory = MemoryOptimizer.estimate_size(locals())

        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start_time
            end_memory = MemoryOptimizer.estimate_size(locals())
            memory_delta = end_memory - start_memory

            print(f"[PROFILE] {func.__name__}:")
            print(f"  Time: {elapsed:.4f}s")
            print(f"  Memory delta: {memory_delta:,} bytes")

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        start_memory = MemoryOptimizer.estimate_size(locals())

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start_time
            end_memory = MemoryOptimizer.estimate_size(locals())
            memory_delta = end_memory - start_memory

            print(f"[PROFILE] {func.__name__}:")
            print(f"  Time: {elapsed:.4f}s")
            print(f"  Memory delta: {memory_delta:,} bytes")

    # Return appropriate wrapper
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class ExecutorPool:
    """Manage thread and process pools for CPU-bound tasks."""

    def __init__(
        self,
        max_workers: Optional[int] = None,
        use_processes: bool = False
    ):
        self.max_workers = max_workers
        self.use_processes = use_processes
        self._executor = None

    def __enter__(self):
        if self.use_processes:
            self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
        else:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self._executor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._executor:
            self._executor.shutdown(wait=True)

    async def run_in_executor(self, func: Callable, *args, **kwargs) -> Any:
        """Run function in executor."""
        loop = asyncio.get_event_loop()
        with self:
            return await loop.run_in_executor(
                self._executor,
                functools.partial(func, *args, **kwargs)
            )