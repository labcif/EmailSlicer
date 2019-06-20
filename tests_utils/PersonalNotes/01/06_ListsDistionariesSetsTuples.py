if __name__ == '__main__':
    print(type(['elem', 1, 6.0, True, None]))   # list
    print(list('elem'))                         # ['e','l', ...
    print(len([0,1,2,3,4,5,6]))                 # 7
    print(['hello', 'there'][0])                # first elem
    print(['hello', 'there'][-1])               # last elem
    animalList = ['cat', 'dog']
    print(animalList)
    animalList.append('fish')                   # adds to the end
    print(animalList)
    animalList.insert(1, 'mouse')               # spefy thge position
    print(animalList)
    animalList.pop()                            # by index, if nothing is given it removes the last (returns the elem)
    print(animalList)
    animalList.remove('mouse')                  # by object, removes the first he enconters (doesn't return the elem)
    print(animalList)
    print('cat' in animalList)                  # check if elem is in the list
    print(animalList.count('dog'))              # counts number of occurences in the list
    numberList = [0,1,2,3,4,5,6,7,8,9]
    print(numberList[2:5])                      # [x:y:z] x -> start, y -> finish, z -> step (all are optional)
    print(numberList[::-1])                     # reverses the list

    print(type({'elem': 1, 6.0: True, 'ola': None}))        # dict
    print(dict((['elem', 1], [6.0, True], ['ola', None])))  # create dict
    myDict = {'key1':1, 'key2':2}                           # create dict
    print(myDict['key1'])
    myDict['key1'] = 3                                      # change value
    print(myDict['key1'])
    myDict.pop('key1')                                      # remove key/value
    print(myDict)
    print(myDict.keys())                                    # print keys
    print(myDict.values())                                  # print values
    print(myDict.items())                                   # print key/values

    print(type(set([1, 3, 'asd', True])))   # set
    mySet = set(['elem2', 'elem1'])
    print(mySet)                            # orders the set ('elem1' comes first) eventho it doeen't change the order of them
    mySet.pop()                             # removes first elem ('elem2')
    print(mySet)

    print(type(tuple('test')))      # tuple
    myTuple = tuple('foobar')       # == myTuple = ('f', 'o', 'o', ...
    print(myTuple)
    print(myTuple[0])               # first elem ('f')
    print(myTuple[-1])              # last elem ('r')
