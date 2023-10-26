def divide_chunks(_list, n):
    for i in range(0, n):
        yield _list[i::n]
