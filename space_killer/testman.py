import os
import sys
import time
import subprocess
import shutil

from killer import strategy_fast_allocate, strategy_large_chunk, strategy_random, strategy_sparse_ntfs, strategy_standard, strategy_unbuffered, strategy_fill_disk_optimal

def run_benchmark(target_gb=4.0):
    test_filename = "bench_test.dat"
    target_bytes = int(target_gb * 1024**3)
    
    strategies = [
        ("Standard (10MB)", strategy_standard),
        ("Large Chunk (100MB)", strategy_large_chunk),
        ("Unbuffered", strategy_unbuffered),
        ("Fast Allocate", strategy_fast_allocate),
        ("Sparse NTFS", strategy_sparse_ntfs),
        ("Random Data", strategy_random),
        ("Fill disk optimal", strategy_fill_disk_optimal)
    ]

    print(f"--- STARTING BENCHMARK ---")
    print(f"Target Size: {target_gb} GB")
    print(f"Test File:   {os.path.abspath(test_filename)}\n")
    print(f"{'STRATEGY':<25} | {'TIME (s)':<10} | {'SPEED (MB/s)':<15} | {'NOTE'}")
    print("-" * 75)

    results = []

    for name, func in strategies:
        # Cleanup before run
        if os.path.exists(test_filename):
            os.remove(test_filename)
        
        # Start Timer
        start_time = time.time()
        
        try:
            func(test_filename, target_bytes)
        except Exception as e:
            print(f"{name:<25} | FAILED ({str(e)})")
            continue
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate Speed
        if duration > 0:
            speed_mb = (target_bytes / (1024*1024)) / duration
        else:
            speed_mb = 999999 # Infinite speed representation
            
        note = ""
        if "Sparse" in name: note = "Does not fill disk"
        if "Allocate" in name: note = "Instant reserve"

        print(f"{name:<25} | {duration:<10.4f} | {speed_mb:<15.2f} | {note}")
        results.append((name, duration))

    # Cleanup after all tests
    if os.path.exists(test_filename):
        os.remove(test_filename)

    print("-" * 75)
    print("Benchmark Complete.")

if __name__ == "__main__":
    # You can change the size here (e.g., 1.0 for 1GB or 4.0 for 4GB)
    try:
        run_benchmark(target_gb=4.0)
    except KeyboardInterrupt:
        print("\nBenchmark cancelled.")