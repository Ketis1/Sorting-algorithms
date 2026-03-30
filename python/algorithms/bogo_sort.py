"""
Bogo Sort (also known as Permutation Sort or Stupid Sort) is a highly inefficient algorithm 
that works by repeatedly shuffling the elements of the list randomly until it happens to be sorted.

Time Complexity: O(n * n!) - Average Case, O(infinity) - Worst Case
Space Complexity: O(1)
"""

import random

def bogo_sort(arr):
    def is_sorted(a):
        for i in range(len(a) - 1):
            if a[i] > a[i+1]:
                return False
        return True
    
    while not is_sorted(arr):
        random.shuffle(arr)
    return arr
