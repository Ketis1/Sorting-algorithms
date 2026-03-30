"""
Counting Sort is an integer sorting algorithm that operates by counting the number of objects
that possess distinct key values. It uses arithmetic on those counts to determine the 
positions of each key value in the output sequence.

Time Complexity: O(n + k) where k is the range of the non-negative key values
Space Complexity: O(n + k)
"""

def counting_sort(arr):
    if not arr:
        return arr
        
    min_val = min(arr)
    max_val = max(arr)
    
    range_of_elements = max_val - min_val + 1
    count = [0] * range_of_elements
    output = [0] * len(arr)
    
    for i in range(len(arr)):
        count[arr[i] - min_val] += 1
        
    for i in range(1, len(count)):
        count[i] += count[i - 1]
        
    for i in range(len(arr) - 1, -1, -1):
        output[count[arr[i] - min_val] - 1] = arr[i]
        count[arr[i] - min_val] -= 1
        
    for i in range(len(arr)):
        arr[i] = output[i]
        
    return arr
