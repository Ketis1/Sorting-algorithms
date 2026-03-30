"""
Insertion Sort is a simple sorting algorithm that builds the final sorted array (or list) one item at a time.
It is much less efficient on large lists than more advanced algorithms such as quicksort, heapsort, or merge sort.

Time Complexity: O(n^2) - Worst and Average Case
Space Complexity: O(1)
"""

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
