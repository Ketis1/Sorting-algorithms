"""
Thanos Sort works by checking if the list is sorted.
If it is not, it 'snaps' its fingers and deletes half of the elements randomly.
This process continues until the list is sorted or empty.

Time Complexity: O(n log n) - Average (approximate)
Space Complexity: O(n)
"""

import random

def thanos_sort(arr):
    def is_sorted(a):
        for i in range(len(a) - 1):
            if a[i] > a[i+1]:
                return False
        return True
    
    while not is_sorted(arr) and len(arr) > 1:
        n = len(arr)
        half_n = n // 2
        indices_to_remove = random.sample(range(n), half_n)
        for i in sorted(indices_to_remove, reverse=True):
            arr.pop(i)
    return arr
