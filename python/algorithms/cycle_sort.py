"""
Cycle Sort is an in-place, unstable sorting algorithm. It is theoretically optimal in terms of 
the total number of writes to the original array, making it useful when writing to memory is costly.
It is based on the idea that the permutation to be sorted can be factored into cycles,
which can individually be rotated to give a sorted result.

Time Complexity: O(n^2) - Worst, Average, and Best Case
Space Complexity: O(1)
"""

def cycle_sort(arr):
    n = len(arr)
    for cycle_start in range(n - 1):
        item = arr[cycle_start]
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            if arr[i] < item:
                pos += 1
        
        if pos == cycle_start:
            continue
            
        while item == arr[pos]:
            pos += 1
            
        arr[pos], item = item, arr[pos]
        
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                if arr[i] < item:
                    pos += 1
                    
            while item == arr[pos]:
                pos += 1
                
            arr[pos], item = item, arr[pos]
            
    return arr
