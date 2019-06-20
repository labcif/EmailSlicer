if __name__ == '__main__':
    # basic catch all ('bare')
    try:
        list.append(1)
    except:
        print('error')
    # catch as variable
    try:
        list.append(1)
    except TypeError as e:
        print(e)
    # catch specific
    try:
        list.append(1)
    except TypeError:
        print('error')
    raise TypeError('This is a TypeError!')     # raise built in error