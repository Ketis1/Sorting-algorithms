"""
Heap Sort is a comparison-based sorting algorithm that uses a binary heap data structure.
It is similar to selection sort where we first find the maximum element and place it at the end.
We repeat the same process for the remaining elements.

Time Complexity: O(n log n)
Space Complexity: O(1)
"""

from _tracking import mark


def heap_sort(arr):
    def heapify(arr, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        mark(arr, [i] + ([l] if l < n else []) + ([r] if r < n else []), f"heapify i={i} n={n}")

        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)

    n = len(arr)
    mark(arr, list(range(n)), "build max-heap")
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        mark(arr, list(range(i + 1)), f"heap size={i + 1}")
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)
    return arr
