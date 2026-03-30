"""
Bubble Sort is a simple comparison-based algorithm that repeatedly steps through the list,
compares adjacent elements, and swaps them if they are in the wrong order.
The pass through the list is repeated until the list is sorted.

Time Complexity: O(n^2) - Worst and Average Case
Space Complexity: O(1)
"""

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
