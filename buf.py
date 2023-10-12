from bigtree import Node, tree_to_dict
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from roman_numeral import *

def compare_paragraphs(p1, p2, par_type):
    if par_type != 'roman':
        return p1 > p2
    else:
        p1, p2 = Roman2Num(p1), Roman2Num(p2)
        return p1 > p2

# Node will have (paragraph, sign, position, type, status)

class Make_tree:

    def __init__(self):
        self.root = Node("txt")
        self.start = True
        self.tree = []

    def similarity_check(self, elem1, elem2):
        if elem1.data_type == elem2[3] and elem1.sign == elem2[1]:
            return True
        else:
            return False
        
    def logic_check(self, elem1, elem2):
        l_elem = elem2[0]
        if not isinstance(elem1, Node):
            f_elem = elem1
        else:
            f_elem = elem1.node_name

        if elem1.data_type == 'number':
            node = int(f_elem) 
            elem = int(l_elem)
        elif elem.data_type == 'letter':
            node = ord(f_elem) 
            elem = ord(l_elem)
        else:
            node = Roman2Num(f_elem)
            elem = Roman2Num(l_elem)
        if node > elem:
            return False
        if elem - node > 6:
            return False
        else:
            return True

        
    def numeral_paragraphs(self, elem):
        paragraph = elem[0].split('.')
        reletives = [elem[0]]
        delimetres = [elem[4]]
        delimetre = elem[4]
        parent = None
        f, st = False, False
        idx = elem[2] - len(elem[0]) - len(elem[4])
        while True:
            if len(paragraph) == 1:
                delimetre = ''
                parent = self.root
                break

            for i in range(-1, -len(self.tree)-1, -1):
                if self.tree[i].sign == '.' and (self.tree[i].data_type == 'number' or self.tree[i].data_type == 'numbers'): 
                    node = self.tree[i].node_name.split('.')
                    if node[:-1] == paragraph[:-1]:
                        parent = self.tree[i].parent
                        delimetre = self.tree[i].delimetre
                        f = True
                        break
                    elif node == paragraph[:-1]:
                        delimetre = self.tree[i].delimetre[:-1]
                        parent = self.tree[i]
                        f = True
            if f:
                break

            delimetre = delimetre[:-1]
            paragraph = paragraph[:-1]
            reletives.append(paragraph)
            delimetres.append('\n' + delimetre)
        for i in range(-1, -len(reletives), -1):
            if parent != self.root:
                end = int(reletives[i][-1])
                start = 0
                for j in range(len(self.tree)):
                    if self.tree[j].node_name.split('.')[:-1] == reletives[i][:-1]:
                        start = int(self.tree[j].node_name.split('.')[-1])
                for k in range(start+1, end):
                    self.tree.append(Node('.'.join(reletives[i][:-1]+[str(k)]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetre = delimetre))
                self.tree.append(Node('.'.join(reletives[i]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetre = delimetre))

            else:
                end = int(reletives[i][-1])
                start = 0
                for j in range(len(self.tree)):
                    if self.tree[j].node_name.split('.')[:-1] == reletives[i][:-1]:
                        start = int(self.tree[j].node_name.split('.')[-1])
                for k in range(start+1, end):
                    self.tree.append(Node('.'.join(reletives[i][:-1]+[str(k)]), sign='.', pos=idx, parent=parent, data_type='number', status='MISSING', delimetre = '\n'))
                self.tree.append(Node('.'.join(reletives[i]), sign='.', pos=idx, parent=parent, data_type='number', status='MISSING', delimetre = '\n'))
                idx -= 1
            parent = self.tree[-1]
            delimetre = delimetres[i]
        for i in range(-1, -len(self.tree)-1, -1):
            if self.tree[i].node_name.split('.')[:-1] == elem[0].split('.')[:-1]:
                if self.tree[i].status == 'MISSING':
                    self.tree[i].delimetre = elem[4]
        
        end = int(elem[0].split('.')[-1])
        start = 0
        for j in range(len(self.tree)):
            if self.tree[j].node_name.split('.')[:-1] == elem[0].split('.')[:-1]:
                start = int(self.tree[j].node_name.split('.')[-1])
        for k in range(start+1, end):
            self.tree.append(Node('.'.join(elem[0].split('.')[:-2]+[str(k)]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetre = elem[4]))

        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetre = elem[4]))

    def walk(self, lst):
        for elem in lst:
            if elem[0].count('.') > 0:
                self.numeral_paragraphs(elem)   
            else:
                res=None
                parent=None
                
                for i in range(-1, -len(self.tree)-1, -1):                          
                    if self.similarity_check(self.tree[i], elem):
                        if self.tree[i+1].parent == self.tree[i].parent or self.tree[i].parent == parent:
                            parent = self.tree[i].parent
                            continue

                        if not self.logic_check(self.tree[i], elem) or self.tree[i].parent == parent:
                            continue

                        else:
                            parent = self.tree[i].parent
                            idx = elem[2] - len(elem[0]) - len(elem[1])
                            func, revfunc = None, None
                            if elem[3] == 'number':
                                func, revfunc = int, str
                            elif elem[3] == 'letter':
                                func, revfunc = ord, chr
                            elif elem[3] == 'roman':
                                func, revfunc = Roman2Num, Num2Roman
                            n1 = func(elem[0])
                            n2 = func(self.tree[i].node_name)
                            for i in range(n2+1, n1):
                                self.tree.append(Node(revfunc(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetre = elem[4]))
                            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetre = elem[4]))
                            res=True
                            break
                if not res:
                    parent = self.tree[-1]
                    idx = elem[2] - len(elem[0]) - len(elem[1])
                    func, revfunc = None, None
                    if elem[3] == 'number':
                        n = '1'
                        func, revfunc = int, str
                    elif elem[3] == 'letter':
                        if elem[3].isupper():
                            n = 'A'
                        else:
                            n='a'
                        func, revfunc = ord, chr
                    elif elem[3] == 'roman':
                        n = 'I'
                        func, revfunc = Roman2Num, Num2Roman
                    if not self.logic_check(n, elem):
                        continue
                        
                    for i in range(func(n), func(elem[0])):                                    
                        self.tree.append(Node(revfunc(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetre = elem[4]))
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetre = elem[4]))

        return tree_to_dict(self.root, all_attrs=True)

    def show(self):
        self.root.show(attr_list=["pos", "status"])
