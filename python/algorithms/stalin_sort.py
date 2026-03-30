"""
Stalin Sort is a humorous sorting algorithm that iterates through the list.
Any element that is not in order is 'eliminated' (removed) from the list.
The result is always a sorted list, although it might be missing several elements.

Time Complexity: O(n)
Space Complexity: O(1) in-place or O(n) for new list
"""

def stalin_sort(arr):
    if not arr:
        return arr
    sorted_arr = [arr[0]]
    for i in range(1, len(arr)):
        if arr[i] >= sorted_arr[-1]:
            sorted_arr.append(arr[i])
    arr.clear()
    arr.extend(sorted_arr)
    return arr
