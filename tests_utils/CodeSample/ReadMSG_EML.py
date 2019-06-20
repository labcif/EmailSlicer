import mailparser
import email

if __name__ == "__main__":
    # Read MSG
    f = r'../EmailSamples/test.msg'
    mail = mailparser.parse_from_file_msg(f)

    # Read EML
    #f = r'../EmailSamples/thunderbird.eml'
    #mail = mailparser.parse_from_file(f)

    print(mail._message)
    msg = email.message_from_string(str(mail._message))
    email_length =  len(msg.get_payload())
    print(email_length)
    if email_length > 1:
        attachment = msg.get_payload()[1]
        print(attachment.get_content_type())
        open('test.pdf', 'wb').write(attachment.get_payload(decode=True))
    #print('Sender: {}\n To: {}\n Subject: {}\n Body{}'.format(mail.from_, mail.to, mail.subject, mail.message_as_string))
    # Read Attachments
    #for attach in mail.attachments:
    #    print(attach)
