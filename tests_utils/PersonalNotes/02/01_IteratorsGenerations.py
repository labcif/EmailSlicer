# generations
def fileSigns():
    sigs = [('jpeg', 'FF D8 FF E0'), ('png', '89 50 4E 47 0A 1A 0A'), ('gif', '47 49 46 38 37 61')]
    for s in sigs:
        yield s     # simillar to 'return', but this will return a generation
    return 'ola'

if __name__ == '__main__':
    # a data type is considered an iterator is an '__iter__' method is defined os the elements can be accessed using indices (list, sets and tuples)
    iterator = iter([1, 2, 3])              # 1 2 3
    reverse_iterator = reversed([4, 5, 6])  # 6 5 4
    print(type(iterator))
    print(type(reverse_iterator))
    print(iterator.__next__())
    print(iterator.__next__())
    print(iterator.__next__())
    print(reverse_iterator.__next__())
    print(reverse_iterator.__next__())
    print(reverse_iterator.__next__())

    # generations
    fs = fileSigns()
    print(fs.__next__())
    print(fs.__next__())
    print(fs.__next__())

