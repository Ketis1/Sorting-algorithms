"""
Shell Sort is a variation of insertion sort that allows the exchange of items that are far apart.
The idea is to arrange the list of elements so that every h-th element (starting anywhere) yields a sorted list.
Such a list is said to be h-sorted.

Time Complexity: O(n^2) - Worst Case, O(n log n) or O(n^(3/2)) - Average Case
Space Complexity: O(1)
"""

def shell_sort(arr):
    n = len(arr)
    gap = n // 2

    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr
