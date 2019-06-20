


def all_email(email):
    with open('output_files/emails.txt', 'a', encoding='utf-8') as outfile:
        outfile.write(email + '\n')
        outfile.close()