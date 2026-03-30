"""
Pigeonhole Sort is a sorting algorithm that is suitable for sorting lists of elements where 
the number of elements and the number of possible key values are approximately the same.
It is similar to counting sort, but differs in that it moves items twice: once to the bucket
array and again to the final destination.

Time Complexity: O(n + N) where N is the range of key values
Space Complexity: O(N)
"""

def pigeonhole_sort(arr):
    if not arr:
        return arr
        
    min_val = min(arr)
    max_val = max(arr)
    size = max_val - min_val + 1
    
    holes = [0] * size
    
    for i in arr:
        holes[i - min_val] += 1
        
    i = 0
    for count in range(size):
        while holes[count] > 0:
            holes[count] -= 1
            arr[i] = count + min_val
            i += 1
            
    return arr
