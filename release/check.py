from parser_part import *
from tree import *
from feedback import *

def check_file(path): 
    txt = parse(path)

    tree = Make_tree()
    dcts = tree.walk(txt)
    # tree.show()

    feedback = fb(dcts, path)
    print(feedback)
    feedback = list(map(lambda x: 'MISSING: ' + ', '.join(map(str, x[:3])), feedback))
    feedback = '\n'.join(feedback)
    f = open("feedback.txt", "w", encoding="utf-8")
    f.write(feedback)
    f.close()