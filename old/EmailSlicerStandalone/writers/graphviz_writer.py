from graphviz import Digraph
from collections import defaultdict 
import os


# for windows
if os.name == 'nt':
    # default path
    os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/' 



def write(output_directory, file_name, data, single_connection=True):

    # data
    # email_id | sender_id | sender_email | receiver_id | receiver_email
    # [(1, 1, 'a@a.com', 2, 'b@b.com') ,(1, 1, 'a@a.com', 3, 'c@c.com'), ... ,(5, 7, 'g@g.com', 3, 'c@c.com')]  
    
    dot = Digraph(comment='Communication Frequency')

    # get only one connection
    if single_connection:
        edge = []
        for sender_id, sender_email, receiver_id, receiver_email in data:
            
            dot.node(sender_id, sender_email)
            
            dot.node(receiver_id, receiver_email)
                
            if [sender_id, receiver_id] not in edge:
                dot.edge(sender_id, receiver_id)
            edge.append([sender_id, receiver_id])
    else:
        for sender_id, sender_email, receiver_id, receiver_email in data:
            
            dot.node(sender_id, sender_email)
            
            dot.node(receiver_id, receiver_email)
                
            dot.edge(sender_id, receiver_id)

    #print(dot.source)
    dot.render(output_directory + '/' + file_name + '.gv', view=False)