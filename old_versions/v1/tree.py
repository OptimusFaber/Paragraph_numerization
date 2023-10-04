from bigtree import Node, tree_to_dict
from roman_numeral import *

def compare_paragraphs(p1, p2, par_type):
    if par_type != 'roman':
        return p1 > p2
    else:
        p1, p2 = Roman2Num(p1), Roman2Num(p2)
        return p1 > p2


class Make_tree:

    def __init__(self):
        self.root = Node("txt")
        self.start = True

    def check_types(self, elem1, elem2):
        if elem1.data_type == elem2[3]:
            if '.' not in elem2:
                return True
            buf1, buf2 = elem1.node_name.split('.'), elem2[0].split('.')
            if len(buf1) == len(buf2):  
                return True
        else:
            return False

    def walk(self, lst):
        tree = []
        for elem in lst:
            if self.start:
                tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3]))
                self.start = False
            else:
                if elem[1] == tree[-1].sign:
                    if self.check_types(tree[-1], elem):
                        if tree[-1].node_name < elem[0]:
                            tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[-1].parent, data_type=elem[3]))
                        else:
                            res=None
                            parent=None
                            st=True
                            for i in range(-2, -len(tree)-1, -1):
                                if self.check_types(tree[i], elem) and tree[i].sign == elem:
                                    if tree[i+1].parent != tree[i].parent and tree[i].parent != parent:
                                        st = True

                                    if tree[i].node_name >= elem[0]:
                                        parent=tree[i].parent
                                        st = False
                                    elif compare_paragraphs(elem[0], tree[i].node_name, tree[i].data_type) and st:
                                        tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[i].parent, data_type=elem[3]))
                                        res=True
                                        break
                            if not res:
                                tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[-1], data_type=elem[3]))
                    else:
                        res=None
                        st = True
                        parent=None
                        for i in range(-2, -len(tree)-1, -1):
                            if self.check_types(tree[i], elem) and tree[i].sign == elem[1]:
                                if tree[i+1].parent != tree[i].parent and tree[i].parent != parent:
                                    st = True

                                if tree[i].node_name >= elem[0]:
                                    parent = tree[i].parent
                                    st = False
                                elif compare_paragraphs(elem[0], tree[i].node_name, tree[i].data_type) and st:
                                    tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[i].parent, data_type=elem[3]))
                                    res=True
                                    break
                        if not res:
                            tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[-1], data_type=elem[3]))
                else:
                    res=None
                    st=True
                    parent=None
                    for i in range(-2, -len(tree)-1, -1):
                        if self.check_types(tree[i], elem) and tree[i].sign == elem[1]:
                            if tree[i+1].parent != tree[i].parent and tree[i].parent != parent:
                                st = True

                            if tree[i].node_name >= elem[0]:
                                parent = tree[i].parent
                                st = False
                            elif compare_paragraphs(elem[0], tree[i].node_name, tree[i].data_type) and st:
                                    tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[i].parent, data_type=elem[3]))
                                    res=True
                                    break
                    if not res:
                        tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=tree[-1], data_type=elem[3]))

        return tree_to_dict(self.root, all_attrs=True)

    def show(self):
        self.root.show(attr_list=["pos"])
