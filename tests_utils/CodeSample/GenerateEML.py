from email import generator
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email.mime.image import MIMEImage
import email
import os
import extract_msg
import mailparser

cwd = os.getcwd()
out_file = os.path.join(cwd, 'message.eml')

class Gen_Emails:
    def __init__(self, msg_file):
        self.EmailGen(msg_file)

    def EmailGen(self, msg_file):
        email_aux = email.message_from_string(str(msg_file._message))
        email_length =  len(email_aux.get_payload())
        if email_length > 1:
            attachment = email_aux.get_payload()[1]
       
        sender = msg_file.from_
        recepiant = msg_file.to
        subject = msg_file.subject

        msg = MIMEMultipart()
        msg['From'] = str(sender[0])
        msg['To'] = str(recepiant[0])
        msg['Subject'] = str(subject)

        sep = '--- mail_boundary ---'
        rest = msg_file.body.split(sep, 1)[0]
        body = rest
        msg.attach(MIMEText(body, 'plain'))
        
        for header in attachment._headers:
            try:
                filename = str(header[1]).split('=')[1].strip('"')
                break
            except:
                continue
        
        payload = MIMEBase('application', 'octet-stream') 
        payload = MIMEImage('application', 'octet-stream') 
        payload.set_payload(attachment._payload) 
        
        
        payload.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
        
        msg.attach(payload) 
        self.SaveToFile(msg)

    def SaveToFile(self, msg):
        with open(out_file, 'w') as file:
            gen = generator.Generator(file)
            gen.flatten(msg)

if __name__ == "__main__":
    f = r'../EmailSamples/pdf.msg'
    #msg_file = extract_msg.Message(f)
    msg_file = mailparser.parse_from_file_msg(f)
    gen = Gen_Emails(msg_file)