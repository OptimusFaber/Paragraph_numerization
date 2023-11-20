from parser_part import *
from tree import *
from feedback import *
import os

def check_file(path): 
    name = os.path.basename(path)
    txt = parse(path)

    tree = Make_tree()
    dcts = tree.walk(txt)
    # tree.show()

    new_path = path.replace(name, "fixed_{}".format(name))
    feedback = fb(dcts, new_path)
    feedback = list(map(lambda x: 'MISSING: ' + ', '.join(map(str, x[:3])), feedback))
    feedback = '\n'.join(feedback)
    f = open("feedback.txt", "w", encoding="utf-8")
    f.write(feedback)
    f.close()