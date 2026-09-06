"""
Bucket Sort is a sorting algorithm that works by distributing the elements of an array into 
a number of buckets. Each bucket is then sorted individually, typically using another sorting 
algorithm like insertion sort, or recursively applying the bucket sorting algorithm.

Time Complexity: O(n + k) - Average and Best Case (where k is the number of buckets)
Space Complexity: O(n + k)
"""

from _tracking import aux_buckets, mark, plain_copy


def _insertion_sort_bucket(bucket):
    for i in range(1, len(bucket)):
        j = i
        while j > 0 and bucket[j] < bucket[j - 1]:
            bucket[j], bucket[j - 1] = bucket[j - 1], bucket[j]
            j -= 1


def bucket_sort(arr):
    if len(arr) == 0:
        return arr

    plain = plain_copy(arr)
    min_val = min(plain)
    max_val = max(plain)
    bucket_count = len(arr)

    bucket_size = max(1, (max_val - min_val) / bucket_count)
    buckets = aux_buckets(arr, "buckets", bucket_count + 1, label="Buckets")

    mark(arr, list(range(len(arr))), "scatter into buckets")
    for value in plain:
        index = int((value - min_val) / bucket_size)
        buckets[index].append(value)

    mark(arr, list(range(len(arr))), "sort buckets")
    for bucket in buckets:
        _insertion_sort_bucket(bucket)

    mark(arr, list(range(len(arr))), "gather from buckets")
    write = 0
    for bucket in buckets:
        for item in bucket:
            arr[write] = item
            write += 1

    return arr
