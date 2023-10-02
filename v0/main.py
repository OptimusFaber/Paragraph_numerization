import re
from bigtree import Node, find, findall, tree_to_dict

root = Node("txt")
start = True
tree = []

# Parse part

t = open('/home/titan/Documents/example.txt').readlines()
t = ''.join(t)
t = ' ' + t
lst = []

f_elem = True
counter = 0

while t and f_elem:
    dot = re.search(r"(((\W[a-zA-Z])|(\d)+)[.])|((\d)+[.])+", t)
    bracket = re.search(r"((\W[a-zA-Z])|(\d)+)[)]", t)

    if dot and bracket:
        f_elem = ')' if bracket.span()[0] < dot.span()[0] else '.'
        pos = idx = min(bracket.span()[1]-2, dot.span()[1]-2)
    elif dot:
        f_elem = '.'
        pos = idx = dot.span()[1]-2
    elif bracket:
        f_elem = ')'
        pos = idx = bracket.span()[1]-2
    else:
        f_elem = None

    # f_elem это главная нумерация типа
    if f_elem:
        if not t[pos].isdigit():
            idx = pos
            paragraph = t[pos]
        else:
            idx = pos
            paragraph = t[pos]
            while t[pos - 1].isdigit():
                paragraph = t[pos - 1] + paragraph
                if pos == 0:
                    break
                pos -= 1
            pos = idx + 1
            if t[pos] == '.':
                paragraph += '.'
                pos_dot = pos
                pos_digit = pos
                while t[pos + 1].isdigit() or t[pos + 1] == '.':
                    paragraph += t[pos + 1]
                    if t[pos + 1].isdigit():
                        pos_digit = pos + 1
                        pos = pos_digit
                    else:
                        pos_dot = pos + 1
                        pos = pos_dot
                    
                    idx = pos
            if t[pos+1] == ')':       
                t = t[pos_dot+1:]
                continue                        
            if '.' in paragraph:
                if paragraph[-1] != '.':
                    t = t[pos_digit+1:]
                    continue
                for i in paragraph.split('.'):
                    if len(i) >= 4:
                        t = t[pos_digit+1:]
                        continue

        t = t[idx+2:]
        counter+=(idx+1)
        if not (len(paragraph.split('.')) == 2 and paragraph.split('.')[1].isdigit()):
            lst.append((paragraph, f_elem, counter))

# Partition part

def check_types(elem1, elem2):
    if elem1.isdigit() and elem2.isdigit():
        return True
    elif elem1.isalpha() and elem2.isalpha():
        return True
    buf1, buf2 = elem1.split('.'), elem2.split('.')
    if len(buf1) == len(buf2):
        return True
    else:
        return False

root = Node("txt")
tree = []
start = True
for elem in lst:
    if start:
        tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=root))
        start = False
    else:
        if elem[1] == tree[-1].sign:
            if check_types(tree[-1].node_name, elem[0]):
                if tree[-1].node_name < elem[0]:
                    tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[-1].parent))
                else:
                    res=None
                    for i in range(-2, -len(tree)-1, -1):
                        if check_types(tree[i].node_name, elem[0]) and tree[i].sign == elem:
                            if tree[i+1].parent != tree[i].parent:
                                st = True

                            if tree[i].node_name >= elem[0]:
                                st = False
                            elif tree[i].node_name < elem[0] and st:
                                tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[i].parent))
                                res=True
                                break
                    if not res:
                        tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[-1]))
            else:
                res=None
                st = True
                for i in range(-2, -len(tree)-1, -1):
                    if check_types(tree[i].node_name, elem[0]) and tree[i].sign == elem[1]:
                        if tree[i+1].parent != tree[i].parent:
                            st = True

                        if tree[i].node_name >= elem[0]:
                            st = False
                        elif tree[i].node_name < elem[0] and st:
                            tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[i].parent))
                            res=True
                            break
                if not res:
                    tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[-1]))
        else:
            res=None
            for i in range(-2, -len(tree)-1, -1):
                if check_types(tree[i].node_name, elem[0]) and tree[i].sign == elem[1]:
                    if tree[i+1].parent != tree[i].parent:
                        st = True

                    if tree[i].node_name >= elem[0]:
                        st = False
                    elif tree[i].node_name < elem[0] and st:
                            tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[i].parent))
                            res=True
                            break
            if not res:
                tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[-1]))

root.show(attr_list=["pos"])

print(tree_to_dict(root, all_attrs=True))
