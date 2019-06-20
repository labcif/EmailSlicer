if __name__ == "__main__":
    numbers = [5, 10, 15, 20, 25]
    for index, number in enumerate(numbers):                    # displays the index and value in list
        print('Item ', index, ' from the list is: ', number)
    for number in range(0, 100):                                # 'xrange' was named 'range' in python3
        print(number)

    while(True):
        pass        # does nothing, acts as a placeholder
        break       # breaks the loop
        continue    # continues on top of the loop

