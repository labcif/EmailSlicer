import pyesedb

EDB = "MDB01.edb"

if __name__ == "__main__":

    esedb_file = pyesedb.file()
    x = esedb_file.open(EDB)


    print(dir(x))
    print(esedb_file.type)
    with open(EDB, "rb") as fp:
        for line in fp:
            print(line)
            exit(1)
    #esedb_file = pyesedb.file()
    #x = esedb_file.open_file_object(file_object)
    
    #print(dir(file_object))
