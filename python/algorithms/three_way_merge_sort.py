"""
3-Way Merge Sort is a modification of the standard Merge Sort where the array is split into
three parts instead of two. This reduces the depth of the recursive tree, but increases the
number of comparisons at each node.

Time Complexity: O(n log_3 n) - Worst, Average, Best Case
Space Complexity: O(n)
"""

from _tracking import aux_array, mark, plain_copy


def three_way_merge_sort(arr):
    def merge_ranges(lo, mid1, mid2, hi):
        left_vals = plain_copy(arr[lo:mid1])
        mid_vals = plain_copy(arr[mid1:mid2])
        right_vals = plain_copy(arr[mid2:hi])
        left = aux_array(arr, "left", values=left_vals, label="Left")
        mid = aux_array(arr, "mid", values=mid_vals, label="Middle")
        right = aux_array(arr, "right", values=right_vals, label="Right")

        mark(arr, list(range(lo, hi)), f"3-way merge [{lo},{hi})")
        i = j = k = 0
        for dest in range(lo, hi):
            candidates = []
            if i < len(left):
                candidates.append((left[i], 0))
            if j < len(mid):
                candidates.append((mid[j], 1))
            if k < len(right):
                candidates.append((right[k], 2))
            value, which = min(candidates, key=lambda item: item[0])
            arr[dest] = value
            if which == 0:
                i += 1
            elif which == 1:
                j += 1
            else:
                k += 1

    def sort_range(lo, hi):
        length = hi - lo
        if length <= 1:
            return
        if length == 2:
            mark(arr, [lo, lo + 1], "sort pair")
            if arr[lo] > arr[lo + 1]:
                arr[lo], arr[lo + 1] = arr[lo + 1], arr[lo]
            return

        third = length // 3
        mid1 = lo + max(1, third)
        mid2 = lo + max(2, 2 * third)
        if mid1 >= hi:
            mid1 = lo + 1
        if mid2 <= mid1:
            mid2 = mid1 + 1
        if mid2 >= hi:
            mid2 = hi - 1

        mark(arr, list(range(lo, hi)), f"divide [{lo},{hi})")
        sort_range(lo, mid1)
        sort_range(mid1, mid2)
        sort_range(mid2, hi)
        merge_ranges(lo, mid1, mid2, hi)

    if len(arr) > 1:
        sort_range(0, len(arr))
    return arr
