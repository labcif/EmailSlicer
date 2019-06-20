import xml.etree.ElementTree as ET

if __name__ == '__main__':
    tree = ET.parse('book.xml')
    root = tree.getroot()
    #print(root.find('authors').text)    # display authors
    for elem in root.findall('chapters/element'):
        print('Chapter #{}: {} (page: {})'.format(elem[0].text, elem[1].text, elem[2].text))