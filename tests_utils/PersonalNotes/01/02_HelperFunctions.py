if __name__ == '__main__':
    print( type( 'what am I?' ) )
    print( dir( str ) )
    print( help( str.title ) )

    number = 5
    print( type( number ) )
    print( dir( number ) )
    print( help( number.__add__ ) )
    print( number.__add__( 3 ) )
    print( number + 3 )
