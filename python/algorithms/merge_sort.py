"""
Merge Sort is a divide-and-conquer algorithm that works by recursively breaking down a problem
into two or more sub-problems of the same or related type, until these become simple enough to be solved directly.
The solutions to the sub-problems are then combined to give a solution to the original problem.

Time Complexity: O(n log n)
Space Complexity: O(n)
"""

from _tracking import aux_array, mark, plain_copy


def merge_sort(arr):
    def sort_range(lo, hi):
        if hi - lo <= 1:
            return

        mid = (lo + hi) // 2
        mark(arr, list(range(lo, hi)), f"divide [{lo},{hi})")
        sort_range(lo, mid)
        sort_range(mid, hi)

        left_vals = plain_copy(arr[lo:mid])
        right_vals = plain_copy(arr[mid:hi])
        left = aux_array(arr, "left", values=left_vals, label="Left")
        right = aux_array(arr, "right", values=right_vals, label="Right")

        mark(arr, list(range(lo, hi)), f"merge [{lo},{hi})")
        i = j = 0
        for k in range(lo, hi):
            if i < len(left) and (j >= len(right) or left[i] <= right[j]):
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1

    if len(arr) > 1:
        sort_range(0, len(arr))
    return arr
