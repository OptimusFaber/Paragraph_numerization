from parser_part import *
from tree import *
from feedback import *

txt = parse('example.txt')

for i in txt:
    print(i)


tree = Make_tree()
dcts = tree.walk(txt)
tree.show()

feedback = fb(dcts, 'example.txt')
print(feedback)
feedback = list(map(lambda x: 'MISSING: ' + ', '.join(map(str, x[:3])), feedback))
feedback = '\n'.join(feedback)
f = open("feedback.txt", "w")
f.write(feedback)
f.close()