import csv
import os
import sys
import utils
from collections import Counter

def folder_message_numbers(headers, output_data):
    with open('output_files/folder_messages.csv', 'w', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)#,dialect='excel')
        writer.writerow(headers)
        for data in output_data.items():
            writer.writerow(data)
        outfile.close()

def all_senders(headers, output_data):
    senders_list = Counter(output_data)
    with open('output_files/senders.csv', 'w', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)#,dialect='excel')
        writer.writerow(headers)
        for sender in senders_list.items():
            writer.writerow(sender)
        outfile.close()
