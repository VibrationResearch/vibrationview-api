"""
Threading Test for VibrationVIEW API

This script tests the thread-safety of the VibrationVIEW API by creating
multiple threads that simultaneously access the COM interface.
"""

import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Handle imports
try:
    from vibrationviewapi import VibrationVIEW, VibrationVIEWContext
except ImportError:
    print("Please ensure vibrationviewapi.py is in the same directory")
    exit(1)


def worker_thread(thread_id, num_operations=5):
    """Worker function that performs VibrationVIEW operations"""
    results = []
    
    print(f"Thread {thread_id}: Starting...")
    
    try:
        with VibrationVIEWContext() as vv:
            for op in range(num_operations):
                start_time = time.time()
                
                try:
                    # Perform various operations
                    version = vv.GetSoftwareVersion()
                    is_ready = vv.IsReady()
                    input_channels = vv.GetHardwareInputChannels()
                    output_channels = vv.GetHardwareOutputChannels()
                    
                    # Add some random delay to simulate real work
                    time.sleep(random.uniform(0.01, 0.1))
                    
                    operation_time = time.time() - start_time
                    
                    results.append({
                        'thread_id': thread_id,
                        'operation': op + 1,
                        'success': True,
                        'time': operation_time,
                        'version': version,
                        'is_ready': is_ready,
                        'input_channels': input_channels,
                        'output_channels': output_channels
                    })
                    
                    print(f"Thread {thread_id}: Operation {op + 1} completed in {operation_time:.3f}s")
                    
                except Exception as e:
                    results.append({
                        'thread_id': thread_id,
                        'operation': op + 1,
                        'success': False,
                        'error': str(e),
                        'time': time.time() - start_time
                    })
                    print(f"Thread {thread_id}: Operation {op + 1} failed: {e}")
    
    except Exception as e:
        print(f"Thread {thread_id}: Context error: {e}")
        results.append({
            'thread_id': thread_id,
            'operation': 'context',
            'success': False,
            'error': str(e)
        })
    
    print(f"Thread {thread_id}: Completed")
    return results


def test_concurrent_access(num_threads=5, operations_per_thread=3):
    """Test concurrent access to VibrationVIEW from multiple threads"""
    print(f"Starting concurrent access test with {num_threads} threads...")
    print(f"Each thread will perform {operations_per_thread} operations")
    print("-" * 60)
    
    start_time = time.time()
    all_results = []
    
    # Use ThreadPoolExecutor for proper thread management
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit all tasks
        futures = {
            executor.submit(worker_thread, i + 1, operations_per_thread): i + 1 
            for i in range(num_threads)
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            thread_id = futures[future]
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as e:
                print(f"Thread {thread_id} raised an exception: {e}")
                all_results.append({
                    'thread_id': thread_id,
                    'success': False,
                    'error': str(e)
                })
    
    total_time = time.time() - start_time
    
    # Analyze results
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    successful_ops = sum(1 for r in all_results if r.get('success', False))
    failed_ops = len(all_results) - successful_ops
    
    print(f"Total operations: {len(all_results)}")
    print(f"Successful: {successful_ops}")
    print(f"Failed: {failed_ops}")
    print(f"Success rate: {successful_ops/len(all_results)*100:.1f}%")
    print(f"Total time: {total_time:.2f} seconds")
    
    if successful_ops > 0:
        avg_time = sum(r.get('time', 0) for r in all_results if r.get('success', False)) / successful_ops
        print(f"Average operation time: {avg_time:.3f} seconds")
    
    # Show per-thread results
    print(f"\nPer-thread breakdown:")
    for thread_id in range(1, num_threads + 1):
        thread_results = [r for r in all_results if r.get('thread_id') == thread_id]
        thread_success = sum(1 for r in thread_results if r.get('success', False))
        print(f"  Thread {thread_id}: {thread_success}/{len(thread_results)} successful")
    
    # Show any errors
    errors = [r for r in all_results if not r.get('success', False)]
    if errors:
        print(f"\nErrors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  Thread {error.get('thread_id', '?')}: {error.get('error', 'Unknown error')}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    
    return all_results


def test_sequential_vs_concurrent():
    """Compare sequential vs concurrent performance"""
    print("Testing sequential vs concurrent performance...")
    
    # Sequential test
    print("\nRunning sequential test...")
    seq_start = time.time()
    sequential_results = worker_thread(0, 10)
    seq_time = time.time() - seq_start
    seq_success = sum(1 for r in sequential_results if r.get('success', False))
    
    # Concurrent test
    print("\nRunning concurrent test...")
    concurrent_results = test_concurrent_access(num_threads=3, operations_per_thread=4)
    concurrent_time = max(r.get('time', 0) for r in concurrent_results if r.get('success', False))
    
    print(f"\nPerformance Comparison:")
    print(f"Sequential: {seq_success} operations in {seq_time:.2f}s")
    print(f"Concurrent: Multiple threads, longest operation: {concurrent_time:.2f}s")


if __name__ == "__main__":
    print("VibrationVIEW Thread-Safety Test")
    print("=" * 60)
    
    try:
        # Basic connectivity test
        print("Testing basic connectivity...")
        with VibrationVIEWContext() as vv:
            version = vv.GetSoftwareVersion()
            print(f"Connected to VibrationVIEW version: {version}")
        
        print("\nBasic connectivity test passed!")
        
        # Run concurrent access test
        print("\n" + "=" * 60)
        test_concurrent_access(num_threads=4, operations_per_thread=3)
        
        # Optional: Run performance comparison
        # test_sequential_vs_concurrent()
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure VibrationVIEW is running and accessible")
