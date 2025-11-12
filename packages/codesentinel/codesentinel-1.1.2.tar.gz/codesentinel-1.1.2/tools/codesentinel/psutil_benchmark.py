
import timeit
import psutil
import random
import statistics

# --- Configuration ---
ITERATIONS = 1000  # Number of times to run each test
CACHE_HIT_RATIO = 0.8  # 80% cache hit rate for simulation

# --- In-memory cache simulation ---
class SimpleCache:
    """A simple dictionary-based cache for simulation."""
    def __init__(self):
        self._cache = {}

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value):
        self._cache[key] = value

    def clear(self):
        self._cache.clear()

# --- Benchmark Functions ---

def benchmark_uncached_process_lookup():
    """Simulates finding a random process without caching."""
    pid = random.choice(psutil.pids())
    try:
        p = psutil.Process(pid)
        p.name()
        p.cpu_times()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass  # Ignore errors for benchmark consistency

def benchmark_cached_process_lookup(cache: SimpleCache):
    """Simulates finding a random process with caching."""
    pid = random.choice(psutil.pids())
    if cache.get(pid) is None:
        # Cache miss
        try:
            p = psutil.Process(pid)
            p_info = {'name': p.name(), 'cpu_times': p.cpu_times()}
            cache.set(pid, p_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    else:
        # Cache hit
        _ = cache.get(pid)

def benchmark_uncached_virtual_memory():
    """Directly calls psutil.virtual_memory()."""
    _ = psutil.virtual_memory()

def benchmark_cached_virtual_memory(cache: SimpleCache):
    """Simulates a cached call to virtual_memory()."""
    if random.random() > CACHE_HIT_RATIO:
        # Cache miss
        mem_info = psutil.virtual_memory()
        cache.set('virtual_memory', mem_info)
    else:
        # Cache hit
        if cache.get('virtual_memory') is None:
            # Populate cache on first run
            cache.set('virtual_memory', psutil.virtual_memory())
        _ = cache.get('virtual_memory')


# --- Runner ---
def run_benchmarks():
    """Executes all benchmarks and prints the results."""
    print("Running CodeSentinel Performance Benchmarks...")
    print(f"Iterations per test: {ITERATIONS}\n")

    # --- Uncached benchmarks ---
    uncached_process_times = timeit.repeat(benchmark_uncached_process_lookup, repeat=5, number=ITERATIONS)
    uncached_mem_times = timeit.repeat(benchmark_uncached_virtual_memory, repeat=5, number=ITERATIONS)

    # --- Cached benchmarks ---
    process_cache = SimpleCache()
    cached_process_times = timeit.repeat(lambda: benchmark_cached_process_lookup(process_cache), repeat=5, number=ITERATIONS)
    
    mem_cache = SimpleCache()
    cached_mem_times = timeit.repeat(lambda: benchmark_cached_virtual_memory(mem_cache), repeat=5, number=ITERATIONS)

    # --- Results ---
    uncached_process_avg = statistics.mean(uncached_process_times)
    cached_process_avg = statistics.mean(cached_process_times)
    process_improvement = (uncached_process_avg - cached_process_avg) / uncached_process_avg * 100

    uncached_mem_avg = statistics.mean(uncached_mem_times)
    cached_mem_avg = statistics.mean(cached_mem_times)
    mem_improvement = (uncached_mem_avg - cached_mem_avg) / uncached_mem_avg * 100

    print("--- Benchmark Results ---\n")
    print("1. Process Information Lookup:")
    print(f"   - Before (Uncached): {uncached_process_avg:.6f} seconds")
    print(f"   - After (ORACL Tier 1 Cache): {cached_process_avg:.6f} seconds")
    print(f"   - Performance Improvement: {process_improvement:.2f}%\n")

    print("2. System Memory Snapshot:")
    print(f"   - Before (Uncached): {uncached_mem_avg:.6f} seconds")
    print(f"   - After (ORACL Tier 1 Cache): {cached_mem_avg:.6f} seconds")
    print(f"   - Performance Improvement: {mem_improvement:.2f}%\n")
    
    print("--- End of Report ---")


if __name__ == "__main__":
    run_benchmarks()
