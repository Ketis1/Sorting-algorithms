"""
Radix Sort is a non-comparison-based sorting algorithm that sorts data with integer keys
by grouping the keys by individual digits that share the same significant position and value.

Time Complexity: O(nk) where k is the number of digits
Space Complexity: O(n+k)
"""

from _tracking import aux_array, aux_histogram, mark, plain_copy


def radix_sort(arr):
    if not arr:
        return arr

    plain = plain_copy(arr)
    max_val = max(plain)
    exp = 1

    while max_val // exp > 0:
        n = len(arr)
        output = aux_array(arr, "output", size=n, fill=0, label=f"Output (exp={exp})")
        count = aux_histogram(arr, "count", size=10, fill=0, label=f"Digit count (exp={exp})")

        mark(arr, list(range(n)), f"counting digit exp={exp}")
        current = plain_copy(arr)
        for i in range(n):
            digit = (current[i] // exp) % 10
            count[digit] += 1

        for i in range(1, 10):
            count[i] += count[i - 1]

        mark(arr, list(range(n)), f"placing digit exp={exp}")
        i = n - 1
        while i >= 0:
            digit = (current[i] // exp) % 10
            pos = int(count[digit]) - 1
            output[pos] = current[i]
            count[digit] = pos
            i -= 1

        mark(arr, list(range(n)), f"writeback exp={exp}")
        for i in range(n):
            arr[i] = output[i]

        exp *= 10
    return arr
