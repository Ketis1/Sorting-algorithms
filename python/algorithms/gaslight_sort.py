"""
Gaslight Sort is an esoteric sorting algorithm that doesn't actually sort anything.
Instead, it simply tells the user that the list is already sorted, 
even if it's completely out of order, making the user doubt their own eyes.

Time Complexity: O(1)
Space Complexity: O(1)
"""

def gaslight_sort(arr):
    print("This array is already perfectly sorted, trust me.")
    return arr
