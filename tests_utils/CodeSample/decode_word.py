import base64, quopri, re

def text_to_encoded_words(text, charset, encoding):
    """
    text: text to be transmitted
    charset: the character set for text
    encoding: either 'q' for quoted-printable or 'b' for base64
    """
    byte_string = text.encode(charset)
    if encoding.lower() is 'b':
        encoded_text = base64.b64encode(byte_string)
    elif encoding.lower() is 'q':
        encoded_text = quopri.encodestring(byte_string)
    return "=?{charset}?{encoding}?{encoded_text}?=".format(
        charset=charset.upper(),
        encoding=encoding.upper(),
        encoded_text=encoded_text.decode('ascii'))

def encoded_words_to_text(encoded_words):
    encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}='
    charset, encoding, encoded_text = re.match(encoded_word_regex, encoded_words).groups()
    if encoding is 'B':
        byte_string = base64.b64decode(encoded_text)
    elif encoding is 'Q':
        byte_string = quopri.decodestring(encoded_text)
    return byte_string.decode(charset)

if __name__ == "__main__":
    # EX: encode
    #In [1]: text_to_encoded_words('This is a horsey: \U0001F40E', "utf-8", "b")
    #Out[1]: '=?UTF-8?B?VGhpcyBpcyBhIGhvcnNleTog8J+Qjg==?='

    #In [2]: text_to_encoded_words('This is a horsey: \U0001F40E', "utf-8", "q")
    #Out[2]: '=?UTF-8?Q?This is a horsey: =F0=9F=90=8E?='


    # EX: decode
    #In [3]: encoded_words_to_text('=?UTF-8?B?VGhpcyBpcyBhIGhvcnNleTog8J+Qjg==?=')
    #Out[3]: 'This is a horsey: \U0001f40e'

    #In [4]: encoded_words_to_text('=?UTF-8?Q?This is a horsey: =F0=9F=90=8E?=')
    #Out[4]: 'This is a horsey: \U0001f40e'
    output = encoded_words_to_text('=?utf-8?B?QW5kcsOpIEFnb3N0aW5obyBOb2d1ZWlyYQ==?=')
    print(output)