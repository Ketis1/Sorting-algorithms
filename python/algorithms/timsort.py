"""
Timsort is a hybrid stable sorting algorithm, derived from merge sort and insertion sort,
designed to perform well on many kinds of real-world data. It works by finding subsequences
of the data that are already ordered and uses them to sort the remainder more efficiently.
This is the default sorting algorithm used in Python's standard library `sort()` method.

Time Complexity: O(n log n) - Worst and Average Case, O(n) - Best Case
Space Complexity: O(n)
"""

def timsort(arr):
    MIN_MERGE = 32

    def calc_min_run(n):
        r = 0
        while n >= MIN_MERGE:
            r |= n & 1
            n >>= 1
        return n + r

    def insertion_sort(arr, left, right):
        for i in range(left + 1, right + 1):
            j = i
            while j > left and arr[j] < arr[j - 1]:
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
                j -= 1

    def merge(arr, l, m, r):
        len1, len2 = m - l + 1, r - m
        left_arr, right_arr = [], []
        
        for i in range(0, len1):
            left_arr.append(arr[l + i])
        for i in range(0, len2):
            right_arr.append(arr[m + 1 + i])

        i, j, k = 0, 0, l

        while i < len1 and j < len2:
            if left_arr[i] <= right_arr[j]:
                arr[k] = left_arr[i]
                i += 1
            else:
                arr[k] = right_arr[j]
                j += 1
            k += 1

        while i < len1:
            arr[k] = left_arr[i]
            k += 1
            i += 1

        while j < len2:
            arr[k] = right_arr[j]
            k += 1
            j += 1

    n = len(arr)
    if n <= 1:
        return arr

    min_run = calc_min_run(n)

    for start in range(0, n, min_run):
        end = min(start + min_run - 1, n - 1)
        insertion_sort(arr, start, end)

    size = min_run
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min((left + 2 * size - 1), (n - 1))
            
            if mid < right:
                merge(arr, left, mid, right)

        size = 2 * size

    return arr
