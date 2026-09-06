"""
Stalin Sort is a humorous sorting algorithm that iterates through the list.
Any element that is not in order is 'eliminated' (removed) from the list.
The result is always a sorted list, although it might be missing several elements.

Time Complexity: O(n)
Space Complexity: O(1) in-place or O(n) for new list
"""

from _tracking import mark, plain_copy


def stalin_sort(arr):
    if not arr:
        return arr

    plain = plain_copy(arr)
    kept = [plain[0]]
    eliminated = []
    for i in range(1, len(plain)):
        if plain[i] >= kept[-1]:
            kept.append(plain[i])
        else:
            eliminated.append(i)

    if eliminated:
        mark(arr, eliminated, "eliminate out-of-order")

    arr.clear()
    arr.extend(kept)
    mark(arr, list(range(len(arr))), "surviving sorted prefix")
    return arr
