from parser_part import *
from tree import *
from feedback import *

txt = parse('Output.txt')

for i in txt:
    print(i)


tree = Make_tree()
dct = tree.walk(txt)
# tree.show()

# fb(dct, 'Output.txt')

