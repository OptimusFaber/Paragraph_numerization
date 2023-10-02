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
        paragraph = elem[0][:-1].split('.')
        if not self.tree:
            buf=''
            parent = self.root
            for e in paragraph[:-1]:
                buf+=e+'.'
                self.tree.append(Node(buf, sign='.', pos=None, parent=parent, data_type='number', status='MISSNG'))
                parent = self.tree[-1]
            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING'))
            return

        for i in range(-1, -len(self.tree)-1, -1):
            if self.tree[i].sign == '.' and self.tree[i].data_type == 'number': 
                node = self.tree[i].node_name.split('.')[:-1]
                if node[:-1] == paragraph[:-1]:
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=self.tree[i].parent, data_type=elem[3], status='EXISTING'))
                    return
        # If algorithm reached this part, it means that we haven't found the brothers of these paragraph => we have to look for his father
        # if paragraph's name is 1.2.1. => his father is 1.2. 
        # We'll try to find it, but if he doesn't exist, we'll have to go deeper and find 1.
        research = True
        reletives = [elem]
        papa = paragraph
        while research:
            for i in range(-1, -len(self.tree)-1, -1):
                if self.tree[i].sign == '.' and self.tree[i].data_type == 'number': 
                    node = self.tree[i].node_name.split('.')[:-1]
                    if node == papa[:-1] or len(papa) == 1:
                        if node == papa[:-1]:
                            parent = self.tree[i]
                        else:
                            parent = self.root
                        for j in range(-1, -len(reletives)-1, -1):
                            idx = elem[2] - len(elem[0])
                            if j != -len(reletives):
                                self.tree.append(Node('.'.join(reletives[j])+'.', sign='.', pos=idx, parent=parent, data_type='number', status='MISSNG'))
                                parent = self.tree[-1]
                            else:
                                self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING'))
                        research = False
                        break
            if research:
                papa = paragraph[:-1]
                reletives.append(papa)

    def walk(self, lst):
        for elem in lst:
            if self.start:
                if elem[0].count('.') > 1:
                    self.numeral_paragraphs(elem)
                else:
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3], status='EXISTING'))
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
                                    if elem[0].count('.') > 1:
                                        idx = elem[2] - len(elem[0]) - 1
                                    else:
                                        idx = elem[2] - len(elem[0]) - len(elem[1]) - 1
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
                                            self.tree.append(Node(chr(o), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING'))
                                            # idx+=1
                                    else:
                                        for o in range(Roman2Num(self.tree[i].node_name)+1, Roman2Num(elem[0])):
                                            self.tree.append(Node(Num2Roman(o), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING'))
                                            # idx+=1
                                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING'))
                                    res=True
                                    break
                    if not res:
                        parent = self.tree[-1]
                        if elem[0].count('.') > 1:
                            idx = elem[2] - len(elem[0]) - 1
                        else:
                            idx = elem[2] - len(elem[0]) - len(elem[1]) - 1
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
                                self.tree.append(Node(chr(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING'))
                                # idx+=1
                        else:
                            n = Roman2Num(elem[0])
                            dif = n - 1
                            for i in range(1, 1+dif):
                                self.tree.append(Node(Num2Roman(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING'))
                                # idx+=1
                        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING'))

        return tree_to_dict(self.root, all_attrs=True)

    def show(self):
        self.root.show(attr_list=["pos", "status"])
