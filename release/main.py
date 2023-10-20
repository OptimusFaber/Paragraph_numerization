from parser_part import *
from tree import *
from feedback import *

txt = parse('Output.txt')

for i in txt:
    print(i)


tree = Make_tree()
dcts = tree.walk(txt)
tree.show()

fb(dcts, 'Output.txt')