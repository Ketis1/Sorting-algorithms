"""
Radix Sort is a non-comparison-based sorting algorithm that sorts data with integer keys
by grouping the keys by individual digits that share the same significant position and value.

Time Complexity: O(nk) where k is the number of digits
Space Complexity: O(n+k)
"""

def radix_sort(arr):
    if not arr:
        return arr
    
    max_val = max(arr)
    exp = 1

    while max_val // exp > 0:
        n = len(arr)
        output = [0] * n
        count = [0] * 10

        for i in range(n):
            index = arr[i] // exp
            count[index % 10] += 1

        for i in range(1, 10):
            count[i] += count[i - 1]

        i = n - 1
        while i >= 0:
            index = arr[i] // exp
            output[count[index % 10] - 1] = arr[i]
            count[index % 10] -= 1
            i -= 1

        for i in range(n):
            arr[i] = output[i]
            
        exp *= 10
    return arr
