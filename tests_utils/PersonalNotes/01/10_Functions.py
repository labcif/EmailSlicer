def simpleFunction():
    print('This is a function!')

def square(value):
    if isinstance(value, int):
        return value**2
    return 'Not a number!'

if __name__ == "__main__":
    simpleFunction()
    print(square(3))