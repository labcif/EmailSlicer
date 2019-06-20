from graphviz import Digraph
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
if __name__ == "__main__":    
    dot = Digraph(comment='The Round Table')
    
    dot.node('1', 'King Arthur')
    dot.node('2', 'Sir Bedevere the Wise')
    dot.node('3', 'Sir Lancelot the Brave')
    
    dot.edges(['12', '13'])
    dot.edge('2', '3', constraint='false')
    
    print(dot.source)
    
    dot.render('test-output/round-table.gv', view=True) 
    'test-output/round-table.gv.pdf'