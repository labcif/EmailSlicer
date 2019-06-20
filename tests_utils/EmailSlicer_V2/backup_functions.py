def process_eml(file_to_open):
    if not file_to_open == '/home/nogueira/Documents/EmailSlicer/EmailSlicer_V2/output_files/ipleiria/Ficheiro de Dados do Outlook/Correio Eletrónico Não Solicitado/27.eml':
        return

    print(file_to_open + '\n')
    # check is message has been read
    has_been_read = False

    # type of encodings to read email
    #encoding_lsit = ['windows-1252', 'utf-8', 'unicode']
    encoding_list = all_encodings()
    with open(file_to_open) as foo:
        line_number = len(foo.readlines())
        #TODO: verify line number
    for encoding in encoding_list:
        try:
            # opens eml message
            with open(file_to_open, encoding=encoding) as file:
                
                # iterates each line of the file
                enumerate(file)
                for count, line in enumerate(file):
        
                    """
                    # iterate only 5 lines (should be enough to get the sender(s))        
                    if count > 40:
                        file.close()
                        break
                    """
                    #print(re.search(r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}=', line).group(1))

                    # get sender
                    search_sender(file_to_open, line)
                    
                    # get receiver(s)
                    search_receivers(file_to_open, line, count)
                
                # file has been read
                has_been_read = True
                
        except:
            # in case of excptio, tries to read with other encoding
            print('ERROR: can\'t open file \'{}\' with {} encoding'.format(file_to_open, encoding))
            pass
        finally:
    
            # in case that file has been read returns 0 (success)
            if has_been_read:
                print(emails_with_sender_receiver[file_to_open])
                return 0
    
    # in case that file has not been read returns -1 (fail)
    return -1
                

def search_sender(file, line):
    # search for the sender (From: ...)
    search_sender = re.search(r'(^\w*From\w*)', line)
    #search_sender.group(1) # get the regex match

    # in case of an 'hit' from the regex
    if search_sender:
        #print(line)
        # split sender(s) from the matched word (From)
        full_sender = line.split(':')

        sender = full_sender[1]
        #print(sender)

        # search emails
        search_email = re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', sender)

        # sender as also an email
        if len(search_email) == 1:
            sender_email = search_email[0]
            sender_name = sender.replace(sender_email, '').replace('<>', '').replace('"', '').strip(' \n')
            #position = sender.find(' ')
            if not re.search('[a-zA-Z]', sender_name):
                sender_name = 'NULL'

        # sender only has email, no name
        elif len(search_email) > 1:
            sender_email = search_email[0]
            sender_name = 'NULL'

        # sender doesn't have email, only name
        else:
            sender_email = 'NULL'
            sender_name = sender.replace('"', '').strip(' \n')

        #db_insert_user(db_name, {'user': sender_name, 'email':sender_email})
        #print('SENDER: ', sender_name, sender_email)
        emails_with_sender_receiver[file] = [{
            'sender': 
            [{                
                'email': sender_email,
                'name': sender_name
            }]
        }]

        #TODO: store 
        # sender_name
        # sender_email


def search_receivers(file, line, n):
    # search for receiver(s) (To: ...)        
    search_receiver = re.search(r'(^\w*To\w*)', line)
    print(line)

    if search_receiver:
        #print(line)
        full_receiver = line.split(':')

        #print(file)
        print(full_receiver[1].strip(' \n') + '#####')

        receiver = full_receiver[1]
        #print(receiver)
        receiver_emails_and_names = []
        # search emails
        search_email = re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', receiver)
        print(n)
        print('OLAAAA')
        print(len(search_email))

        # sender as also an email
        if len(search_email) == 1:
            receiver_email = search_email[0]
            receiver_name = receiver.replace(receiver_email, '').replace('<>', '').replace('"', '').strip(' \n')
            
            if not re.search('[a-zA-Z]', receiver_name):
                receiver_name = 'NULL'
            if '?' in receiver_name:
                receiver_name = encoded_words_to_text(receiver_name)
            receiver_emails_and_names.append(
                {
                    'email': receiver_email,
                    'name': receiver_name
                }
            )
            print(receiver_email)
        # receiver only has email, no name
        elif len(search_email) > 1:
            receivers = receiver.split(',')
            for receiver in receivers:
                receiver_email, receiver_name = process_receiver(file, receiver)
                if not re.search('[a-zA-Z]', receiver_name):
                    receiver_name = 'NULL'
                if '?' in receiver_name:
                    receiver_name = encoded_words_to_text(receiver_name)
                receiver_emails_and_names.append(
                    {
                        'email': receiver_email,
                        'name': receiver_name
                    }
                )
        # receiver doesn't have email, only name
        else:
            #print(receiver)
            return
            """
            receiver_email = 'NULL'
            receiver_name = receiver.replace('"', '').strip(' \n')
            if not re.search('[a-zA-Z]', receiver_name):
                receiver_name = 'NULL'
            if '?' in receiver_name:
                receiver_name = encoded_words_to_text(receiver_name)
            receiver_emails_and_names.append(
                {
                    'email': receiver_email,
                    'name': receiver_name
                }
            )
            """
        #db_insert_user(db_name, {'user': receiver_name, 'email':receiver_email})
        #print('RECEIVER: ', receiver_name, receiver_email)
        #print(emails_with_sender_receiver[file])
        #len(emails_with_sender_receiver[file][1][0]['receiver']) == 0
        for receiver_email_and_name in receiver_emails_and_names:

            if len(emails_with_sender_receiver[file]) == 1:
                emails_with_sender_receiver[file].append([{
                    'receiver': 
                    [[{                
                        'email': receiver_email_and_name['email'],
                        'name': receiver_email_and_name['name']
                    }]]
                }])
            else:
                emails_with_sender_receiver[file][1][0]['receiver'][0].append([
                    {                
                        'email': receiver_email_and_name['email'],
                        'name': receiver_email_and_name['name']
                    }
                ])
        print(emails_with_sender_receiver[file])

def process_receiver(file, receiver):
    search_email = re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', receiver)
    receiver_email = search_email[0]
    receiver_name = receiver.replace(receiver_email, '').replace('<>', '').replace('"', '').strip(' \n')
    if not re.search('[a-zA-Z]', receiver_name):
        receiver_name = 'NULL'
    #print('NAME: {} | EMAIL: {}'.format(receiver_name, receiver_email))
    return receiver_email, receiver_name
            