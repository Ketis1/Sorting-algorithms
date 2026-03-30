"""
3-Way Merge Sort is a modification of the standard Merge Sort where the array is split into
three parts instead of two. This reduces the depth of the recursive tree, but increases the
number of comparisons at each node.

Time Complexity: O(n log_3 n) - Worst, Average, Best Case
Space Complexity: O(n)
"""

def three_way_merge_sort(arr):
    if len(arr) <= 1:
        return arr
        
    def merge(arr, low, mid1, mid2, high, dest):
        i, j, k, l = low, mid1, mid2, low
        
        while i < mid1 and j < mid2 and k < high:
            if arr[i] < arr[j]:
                if arr[i] < arr[k]:
                    dest[l] = arr[i]
                    i += 1
                else:
                    dest[l] = arr[k]
                    k += 1
            else:
                if arr[j] < arr[k]:
                    dest[l] = arr[j]
                    j += 1
                else:
                    dest[l] = arr[k]
                    k += 1
            l += 1
            
        while i < mid1 and j < mid2:
            if arr[i] < arr[j]:
                dest[l] = arr[i]
                i += 1
            else:
                dest[l] = arr[j]
                j += 1
            l += 1
            
        while j < mid2 and k < high:
            if arr[j] < arr[k]:
                dest[l] = arr[j]
                j += 1
            else:
                dest[l] = arr[k]
                k += 1
            l += 1
            
        while i < mid1 and k < high:
            if arr[i] < arr[k]:
                dest[l] = arr[i]
                i += 1
            else:
                dest[l] = arr[k]
                k += 1
            l += 1
            
        while i < mid1:
            dest[l] = arr[i]
            l += 1
            i += 1
            
        while j < mid2:
            dest[l] = arr[j]
            l += 1
            j += 1
            
        while k < high:
            dest[l] = arr[k]
            l += 1
            k += 1

    def sort_recursive(arr, low, high, dest):
        if high - low < 2:
            return
            
        mid1 = low + ((high - low) // 3)
        mid2 = low + 2 * ((high - low) // 3) + 1
        
        sort_recursive(dest, low, mid1, arr)
        sort_recursive(dest, mid1, mid2, arr)
        sort_recursive(dest, mid2, high, arr)
        
        merge(dest, low, mid1, mid2, high, arr)

    if not arr:
        return arr
    dest = arr.copy()
    sort_recursive(dest, 0, len(arr), arr)
    return arr
