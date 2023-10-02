from parser_part import *
from tree import *
from feedback import *

txt = parse('example.txt')

tree = Make_tree()
dct = tree.walk(txt)
tree.show()

fb(dct, 'C:/Users/Rodion/repos/Paragraph_numerization/example.txt')

