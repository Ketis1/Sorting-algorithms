"""
Introsort (or Introspective Sort) is a hybrid sorting algorithm that provides both fast average
performance and optimal worst-case performance. It begins with quicksort, but switches to 
heapsort when the recursion depth exceeds a level based on the number of elements being sorted.

Time Complexity: O(n log n) - Worst, Average, and Best Case
Space Complexity: O(log n)
"""
import math

def introsort(arr):
    def heapify(arr, n, i, start):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2

        if l < n and arr[start + l] > arr[start + largest]:
            largest = l

        if r < n and arr[start + r] > arr[start + largest]:
            largest = r

        if largest != i:
            arr[start + i], arr[start + largest] = arr[start + largest], arr[start + i]
            heapify(arr, n, largest, start)

    def heap_sort(arr, start, end):
        n = end - start
        for i in range(n // 2 - 1, -1, -1):
            heapify(arr, n, i, start)

        for i in range(n - 1, 0, -1):
            arr[start], arr[start + i] = arr[start + i], arr[start]
            heapify(arr, i, 0, start)

    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def introsort_util(arr, start, end, depth_limit):
        n = end - start
        if n < 16:
            # For small sizes, insertion sort is usually used in actual implementations.
            for i in range(start + 1, end + 1):
                key = arr[i]
                j = i - 1
                while j >= start and arr[j] > key:
                    arr[j + 1] = arr[j]
                    j -= 1
                arr[j + 1] = key
            return

        if depth_limit == 0:
            heap_sort(arr, start, end + 1)
            return

        pivot = partition(arr, start, end)
        introsort_util(arr, start, pivot - 1, depth_limit - 1)
        introsort_util(arr, pivot + 1, end, depth_limit - 1)

    if not arr:
        return arr
    
    max_depth = 2 * math.floor(math.log2(len(arr)))
    if max_depth <= 0:
        max_depth = 1
    introsort_util(arr, 0, len(arr) - 1, max_depth)
    return arr
