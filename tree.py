from bigtree import Node, find, findall

# root = Node("a", age=90)
# b = Node("b", pos=65, parent=root)
# c = Node("c", pos=60, parent=root)
# d = Node("d", pos=40, parent=b)

# root.show(attr_list=["pos"])

# e = Node("e", pos=89, parent=d)

# root.show(attr_list=["pos"])

# e.parent = c

# root.show(attr_list=["pos"])

def check_types(elem1, elem2):
    if elem1.isdigit() and elem2.isdigit():
        return True
    elif elem1.isalpha() and elem2.isalpha():
        return True
    buf1, buf2 = elem1.split('.'), elem2.split('.')
    if len(buf1) == len(buf2):  # and ((buf1[0].isdigit() and buf2[0].isdigit()) or (buf1[0].isalpha() and buf2[0].isalpha()))
        return True
    else:
        return False

root = Node("txt")
tree = []
lst = [('1.', '.', 2), ('2.', '.', 23), ('a', ')', 20), ('b', ')', 13), ('d', ')', 13), ('1', ')', 14), ('3', ')', 18), ('4.', '.', 16), ('2.', '.', 25), ('1.', '.', 67), ('2.', '.', 13), ('3.', '.', 31), ('a', '.', 37), ('b', '.', 15), ('c', '.', 13), ('3.', '.', 19), ('4.', '.', 13), ('1.', '.', 58), ('3.', '.', 37), ('4.', '.', 36), ('5.', '.', 16), ('1', ')', 80), ('2', ')', 17), ('3', ')', 16)]
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
                            print(tree[i].node_name, elem[0], tree[i].parent)
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
