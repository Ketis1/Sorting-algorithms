"""
Selection Sort is an in-place comparison sorting algorithm. It divides the input list into two parts:
the sublist of items already sorted, which is built up from left to right at the front of the list,
and the sublist of items remaining to be sorted that occupy the rest of the list.

Time Complexity: O(n^2)
Space Complexity: O(1)
"""

def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            if arr[min_idx] > arr[j]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
