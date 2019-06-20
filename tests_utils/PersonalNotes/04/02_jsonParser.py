import json

if __name__ == '__main__':
    json_file = open('book.json', 'r')
    data_dict = json.loads(json_file.read())
    #print(data_dict['authors'])     # display authors
    for chapter in data_dict['chapters']:
        number = chapter['chapterNumber']
        title = chapter['chapterTitle']
        page_number = chapter['pageCount']
        print('Chapter #{}: {} (page {})'.format(number, title, page_number))