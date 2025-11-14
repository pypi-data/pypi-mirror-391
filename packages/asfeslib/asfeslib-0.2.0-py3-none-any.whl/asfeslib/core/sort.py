from typing import Any, Callable, List


def bubble_sort(data: List[Any], key: Callable = lambda x: x, reverse: bool = False) -> List[Any]:
    """Пузырьковая сортировка (O(n^2))."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if (key(arr[j]) > key(arr[j + 1])) ^ reverse:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def insertion_sort(data: List[Any], key: Callable = lambda x: x, reverse: bool = False) -> List[Any]:
    """Сортировка вставками (O(n^2), быстрая на почти отсортированных данных)."""
    arr = data[:]
    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1
        while j >= 0 and (key(arr[j]) > key(current)) ^ reverse:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current
    return arr


def selection_sort(data: List[Any], key: Callable = lambda x: x, reverse: bool = False) -> List[Any]:
    """Сортировка выбором (O(n^2))."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        ext = i
        for j in range(i + 1, n):
            if (key(arr[j]) < key(arr[ext])) ^ reverse:
                ext = j
        arr[i], arr[ext] = arr[ext], arr[i]
    return arr


def merge_sort(data: List[Any], key: Callable = lambda x: x, reverse: bool = False) -> List[Any]:
    """Сортировка слиянием (O(n log n))."""
    if len(data) <= 1:
        return data[:]

    mid = len(data) // 2
    left = merge_sort(data[:mid], key, reverse)
    right = merge_sort(data[mid:], key, reverse)

    return _merge(left, right, key, reverse)


def _merge(left, right, key, reverse):
    res = []
    i = j = 0
    while i < len(left) and j < len(right):
        if (key(left[i]) <= key(right[j])) ^ reverse:
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res


def quick_sort(data, key=lambda x: x, reverse=False):
    """Быстрая сортировка (устойчивая, с поддержкой reverse)."""
    if len(data) <= 1:
        return data[:]

    pivot = data[len(data) // 2]
    if reverse:
        less = [x for x in data if key(x) > key(pivot)]
        equal = [x for x in data if key(x) == key(pivot)]
        greater = [x for x in data if key(x) < key(pivot)]
    else:
        less = [x for x in data if key(x) < key(pivot)]
        equal = [x for x in data if key(x) == key(pivot)]
        greater = [x for x in data if key(x) > key(pivot)]

    return quick_sort(less, key, reverse) + equal + quick_sort(greater, key, reverse)


def heap_sort(data: List[Any], key: Callable = lambda x: x, reverse: bool = False) -> List[Any]:
    """Пирамидальная сортировка (O(n log n))."""
    import heapq

    arr = data[:]
    if reverse:
        return sorted(arr, key=key, reverse=True)
    heap = [(key(x), x) for x in arr]
    heapq.heapify(heap)
    return [heapq.heappop(heap)[1] for _ in range(len(heap))]


def sort_builtin(data: List[Any], key: Callable = lambda x: x, reverse: bool = False) -> List[Any]:
    """Обёртка над встроенной функцией sorted() (Timsort)."""
    return sorted(data, key=key, reverse=reverse)


async def async_sort(data: List[Any], key: Callable = lambda x: x, delay: float = 0.0) -> List[Any]:
    """
    Асинхронная пузырьковая сортировка для демонстраций (например, LED-индикация).
    """
    import asyncio
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if key(arr[j]) > key(arr[j + 1]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
            await asyncio.sleep(delay)
    return arr
