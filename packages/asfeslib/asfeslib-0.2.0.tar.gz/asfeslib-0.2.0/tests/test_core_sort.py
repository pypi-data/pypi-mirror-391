from asfeslib.core import sort
import asyncio

def test_all_sorts_agree():
    data = [5, 1, 9, 3, 2]
    expected = sorted(data)
    funcs = [
        sort.bubble_sort,
        sort.insertion_sort,
        sort.selection_sort,
        sort.merge_sort,
        sort.quick_sort,
        sort.heap_sort,
        sort.sort_builtin,
    ]
    for f in funcs:
        assert f(data) == expected

def test_reverse_sort():
    data = [1, 2, 3]
    for f in [sort.quick_sort, sort.merge_sort, sort.sort_builtin]:
        assert f(data, reverse=True) == [3, 2, 1]

def test_async_sort_event_loop():
    data = [4, 3, 2, 1]
    result = asyncio.run(sort.async_sort(data, delay=0))
    assert result == sorted(data)
