import extract_msg

if __name__ == "__main__":
    '''
    # Read Headers
    msg = extract_msg.Message('../EmailSamples/test.msg')
    print(msg.header)
    '''

    # Read MSG
    f = r'../EmailSamples/relatorio.msg'  # Replace with yours
    msg = extract_msg.Message(f)
    msg_sender = msg.sender
    msg_to = msg.to
    msg_subj = msg.subject
    msg_message = msg.body
    msg_attach = msg.attachments
    # To save attachment
    # msg.save_attachments(True)

    print('Sender: {}'.format(msg_sender))
    print('To: {}'.format(msg_to))
    print('Subject: {}'.format(msg_subj))
    print('Body: {}'.format(msg_message))
    print('Attachments: {}'.format(msg_attach))
    for attach in msg_attach:
        print(dir(attach))
        print(attach._Attachment__data)
