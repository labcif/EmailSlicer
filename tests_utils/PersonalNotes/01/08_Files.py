if __name__ == '__main__':
    file = open('test.txt')         # default is read only
    print(file.read())              # reads all lines
    file = open('test.txt')         # we need to call it again to reset the line pointer
    print(file.readline())          # reads one line
    file = open('test.txt')
    print(file.readlines())         # creates a string for each line and stores them in a list
    file = open('test.txt', 'w')    # opens for write
    file.write('Last Line\n')       # wite one line
    data = ['Hey\n', 'Hoo\n']
    file.writelines(data)           # write multiple lines
    file.flush()                    # writes any remaining data in buffer to the file
    file.close()                    # closes connection to the file
