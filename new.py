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

    def check_types(self, elem1, elem2):
        if elem1.data_type == elem2[3]:
            if '.' not in elem2:
                return True
            buf1, buf2 = elem1.node_name.split('.'), elem2[0].split('.')
            if len(buf1) == len(buf2):  
                return True
        else:
            return False
        
    def numeral_paragraphs(self, elem):
        paragraph = elem[0].split('.')[:-1]
        reletives = [elem[0]]
        delimetres = [elem[4]]
        delimetre = elem[4]
        parent = None
        f, st = False, False
        while True:
            if len(paragraph) == 1:
                delimetre = '\n'
                parent = self.root
                break

            for i in range(-1, -len(self.tree)-1, -1):
                if self.tree[i].sign == '.' and self.tree[i].data_type == 'number': 
                    node = self.tree[i].node_name.split('.')[:-1]
                    if node[:-1] == paragraph[:-1]:
                        parent = self.tree[i].parent
                        delimetre = self.tree[i].delimetre
                        f = True
                        break
                    elif node == paragraph[:-1]:
                        delimetre = self.tree[i].delimetre[:-1]
                        parent = self.tree[i]
                        f, st = True, True
            if f:
                break

            delimetre = delimetre[:-1]
            paragraph = paragraph[:-1]
            reletives.append(paragraph)
            delimetres.append('\n' + delimetre)

        for i in range(-1, -len(reletives), -1):
            idx = elem[2] - len(elem[0]) - len(elem[4])
            if i > -len(reletives)+1:
                self.tree.append(Node('.'.join(reletives[i])+'.', sign='.', pos=idx, parent=parent, data_type='number', status='MISSING', delimetre = delimetre))
            else:
                self.tree.append(Node(delimetre[1:]+'.'.join(reletives[i])+'.', sign='.', pos=idx, parent=parent, data_type='number', status='MISSING', delimetre = '\n'))
            
            parent = self.tree[-1]
            delimetre = delimetres[i]
        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetre = elem[4]))

    def walk(self, lst):
        for elem in lst:
            if self.start:
                if elem[0].count('.') > 1:
                    self.numeral_paragraphs(elem)
                else:
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3], status='EXISTING', delimetre = elem[4]))
                self.start = False
            else:
                if elem[0].count('.') > 1:
                    self.numeral_paragraphs(elem)   
                else:
                    res=None
                    st=True
                    parent=None
                    
                    for i in range(-1, -len(self.tree)-1, -1):                            
                        if self.check_types(self.tree[i], elem) and self.tree[i].sign == elem[1]:
                            if self.tree[i+1].parent != self.tree[i].parent and self.tree[i].parent != parent:
                                st = True

                            if self.tree[i].node_name >= elem[0]:
                                parent = self.tree[i].parent
                                st = False
                            elif compare_paragraphs(elem[0], self.tree[i].node_name, self.tree[i].data_type) and st:
                                    parent = self.tree[i].parent
                                    if elem[0].count('.') > 0:
                                        idx = elem[2] - len(elem[0])
                                    else:
                                        idx = elem[2] - len(elem[0]) - len(elem[1])
                                    if elem[3] != 'roman':
                                        if '.' in elem[0]:
                                            n1 = elem[0].replace('.', '')
                                        else:
                                            n1 = elem[0]
                                        if '.' in self.tree[i].node_name:
                                            n2 = self.tree[i].node_name.replace('.', '')
                                        else:
                                            n2 = self.tree[i].node_name
                                        for o in range(ord(n2)+1, ord(n1)):
                                            self.tree.append(Node(chr(o), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetre = elem[4]))
                                    else:
                                        for o in range(Roman2Num(self.tree[i].node_name)+1, Roman2Num(elem[0])):
                                            self.tree.append(Node(Num2Roman(o), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetre = elem[4]))
                                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetre = elem[4]))
                                    res=True
                                    break
                    if not res:
                        parent = self.tree[-1]
                        if elem[0].count('.') > 0:
                            idx = elem[2] - len(elem[0])
                        else:
                            idx = elem[2] - len(elem[0]) - len(elem[1])
                        if elem[3] != 'roman':
                            if elem[3] == 'number':
                                n = '1'
                            elif elem[3] == 'letter':
                                if elem[3].isupper():
                                    n = 'A'
                                else:
                                    n='a'
                            dif = ord(elem[0].replace('.', '')) - ord(n)
                            
                            for i in range(ord(n), ord(n)+dif):                                    
                                self.tree.append(Node(chr(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetre = elem[4]))
                        else:
                            n = Roman2Num(elem[0])
                            dif = n - 1
                            for i in range(1, 1+dif):
                                self.tree.append(Node(Num2Roman(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetre = elem[4]))
                        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetre = elem[4]))

        return tree_to_dict(self.root, all_attrs=True)

    def show(self):
        self.root.show(attr_list=["pos", "status"])
