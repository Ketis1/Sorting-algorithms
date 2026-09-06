"""
Quick Sort is a divide-and-conquer algorithm that works by selecting a 'pivot' element
from the array and partitioning the other elements into two sub-arrays,
according to whether they are less than or greater than the pivot.

Time Complexity: O(n^2) - Worst Case, O(n log n) - Average Case
Space Complexity: O(log n)
"""

from _tracking import mark


def quick_sort(arr):
    def partition(low, high):
        pivot_index = high
        mark(arr, list(range(low, high + 1)) + [pivot_index], f"partition pivot={pivot_index}")
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def sort_range(low, high):
        if low >= high:
            return
        mark(arr, list(range(low, high + 1)), f"quick [{low},{high}]")
        pivot = partition(low, high)
        mark(arr, [pivot], f"pivot placed @{pivot}")
        sort_range(low, pivot - 1)
        sort_range(pivot + 1, high)

    if len(arr) > 1:
        sort_range(0, len(arr) - 1)
    return arr
