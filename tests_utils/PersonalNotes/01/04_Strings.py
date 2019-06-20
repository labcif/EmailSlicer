if __name__ == '__main__':
    print( 'Hello' + ' ' + 'World!' )
    print( 'Are we there yet? ' * 3 )

    print( ':Hello World:'.strip(':') )             # removes from begin/end
    print( 'Hello:World'.replace(':', ' ') )        # removes from anywhere

    print( 'e' in 'Hello World' )                   # true
    print( 'Hello World'.startswith( 'Hello' ) )    # true
    print( 'Hello World'.endswith( 'World' ) )      # true

    print( 'This is a really long line! This should be in two lines.'.split('!') )      # split strings by delimitator
    print(''.join(['ola', ' ', 'adeus']))                                               # join strings

    # unicode string
    print( u'This is a unicode string' )
    # raw string
    print( r'This is a raw string, good to capture characters such as \ which can break strings' )

    # format replaces '{}' with the provided values
    print( '{} {} {} {}'.format( 'Formatted', 'strings', 'are', 'izi!' ) )
    print( '{:06d}'.format( 42 ) )
    print( '{:=^21}'.format('') )
