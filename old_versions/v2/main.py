from parser_part import *
from tree import *
from feedback import *

txt = parse('example2.txt')

print(txt)

tree = Make_tree()
dct = tree.walk(txt)
tree.show()

print(dct)

fb(dct, 'example2.txt')

