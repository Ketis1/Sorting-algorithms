"""
Bucket Sort is a sorting algorithm that works by distributing the elements of an array into 
a number of buckets. Each bucket is then sorted individually, typically using another sorting 
algorithm like insertion sort, or recursively applying the bucket sorting algorithm.

Time Complexity: O(n + k) - Average and Best Case (where k is the number of buckets)
Space Complexity: O(n + k)
"""

def bucket_sort(arr):
    if len(arr) == 0:
        return arr

    min_val = min(arr)
    max_val = max(arr)
    bucket_count = len(arr)
    
    # Calculate bucket size to group elements effectively
    bucket_size = max(1, (max_val - min_val) / bucket_count)
    buckets = [[] for _ in range(bucket_count + 1)]

    for i in range(len(arr)):
        # Determine the bucket index for the element
        index = int((arr[i] - min_val) / bucket_size)
        buckets[index].append(arr[i])

    sorted_arr = []
    for bucket in buckets:
        # Sort individual bucket (insertion sort behavior from builtin sort)
        bucket.sort()
        sorted_arr.extend(bucket)

    for i in range(len(arr)):
        arr[i] = sorted_arr[i]

    return arr
