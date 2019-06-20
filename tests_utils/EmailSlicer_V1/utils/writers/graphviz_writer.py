from graphviz import Digraph
from collections import defaultdict 
import os
# for windows
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/' # default path

def prepare(message_data):
    dot = Digraph(comment='Communication Frequency')

    senders_with_receivers = defaultdict(list)

    sender_id = -1
    for message in message_data:
        sender = message['sender']

        if not sender or sender in senders_with_receivers:
            continue
        
        sender_id += 1
        senders_with_receivers[sender].append(None)
        
        dot.node(str(sender_id), sender)
        
        for message_from_sender in message_data:
            if message_from_sender['sender'] == sender:
                receiver = message_from_sender['receiver']

                if not receiver or receiver in senders_with_receivers[sender]:
                    continue
    
                receiver_id = sender_id + 1
                senders_with_receivers[sender].append(receiver)

                dot.node(str(receiver_id), receiver)
                dot.edge(str(sender_id), str(receiver_id))
        
                sender_id = receiver_id
    
    #print(dot.source)
    dot.render('output_files/graphviz.gv', view=True) 
