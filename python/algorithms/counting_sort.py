"""
Counting Sort is an integer sorting algorithm that operates by counting the number of objects
that possess distinct key values. It uses arithmetic on those counts to determine the 
positions of each key value in the output sequence.

Time Complexity: O(n + k) where k is the range of the non-negative key values
Space Complexity: O(n + k)
"""

from _tracking import aux_array, aux_histogram, mark, plain_copy


def counting_sort(arr):
    if not arr:
        return arr

    plain = plain_copy(arr)
    min_val = min(plain)
    max_val = max(plain)

    range_of_elements = max_val - min_val + 1
    count = aux_histogram(arr, "count", size=range_of_elements, fill=0, label="Count")
    output = aux_array(arr, "output", size=len(arr), fill=0, label="Output")

    mark(arr, list(range(len(arr))), "count frequencies")
    for i in range(len(arr)):
        count[plain[i] - min_val] += 1

    for i in range(1, len(count)):
        count[i] += count[i - 1]

    mark(arr, list(range(len(arr))), "build output")
    for i in range(len(arr) - 1, -1, -1):
        key = plain[i] - min_val
        pos = int(count[key]) - 1
        output[pos] = plain[i]
        count[key] = pos

    mark(arr, list(range(len(arr))), "copy to main")
    for i in range(len(arr)):
        arr[i] = output[i]

    return arr
