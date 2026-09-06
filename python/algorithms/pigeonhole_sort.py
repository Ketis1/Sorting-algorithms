"""
Pigeonhole Sort is a sorting algorithm that is suitable for sorting lists of elements where 
the number of elements and the number of possible key values are approximately the same.
It is similar to counting sort, but differs in that it moves items twice: once to the bucket
array and again to the final destination.

Time Complexity: O(n + N) where N is the range of key values
Space Complexity: O(N)
"""

from _tracking import aux_histogram, mark, plain_copy


def pigeonhole_sort(arr):
    if not arr:
        return arr

    plain = plain_copy(arr)
    min_val = min(plain)
    max_val = max(plain)
    size = max_val - min_val + 1

    holes = aux_histogram(arr, "holes", size=size, fill=0, label="Holes")

    mark(arr, list(range(len(arr))), "fill holes")
    for value in plain:
        holes[value - min_val] += 1

    mark(arr, list(range(len(arr))), "emit from holes")
    i = 0
    for hole_index in range(size):
        while int(holes[hole_index]) > 0:
            holes[hole_index] -= 1
            arr[i] = hole_index + min_val
            i += 1

    return arr
