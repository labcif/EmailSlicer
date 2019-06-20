from email.message import EmailMessage
from email import generator
from re import sub as rep
from string import punctuation as pont
from . import util_writer 

def message_to_writer(message):
    if message['body']:
        _generate_message_eml(message)

def _generate_message_eml(message):
    # Create the base text message.
    msg = EmailMessage()
    msg['Subject'] = message['subject']
    msg['From'] = message['sender']
    msg['To'] = message['receiver']

    try:
        msg.set_content(message['body'].decode('utf-8'))
    except:
        msg.set_content(message['body'])
    #asparagus_cid = make_msgid()
    #    if message['attachment_count'] > 0:
    #        image = message['attachments'][0]
    #        msg.add_attachment(image, 'image', 'png')#, cid=asparagus_cid)

    file_name = util_writer.sanitize_string(message['subject'])
    #file_name = file_name.decode('utf-8', 'ignore')
    
    try:
        with open('output_files/extracted_emails/' + file_name + '.eml', 'w', encoding='utf-8') as file:
            gen = generator.Generator(file)
            gen.flatten(msg)
            file.close()
    except Exception as e:
        print('ERROR: ', e, ' FILE:  ', file_name)
        pass