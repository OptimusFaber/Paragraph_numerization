from bigtree import Node, tree_to_dict, find
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from roman_numeral import *

functions = {
    'number': [int, str], 
    'ru_up_letter': [ord, chr], 
    'en_up_letter': [ord, chr], 
    'ru_low_letter': [ord, chr], 
    'en_low_letter': [ord, chr], 
    'roman': [Roman2Num, Num2Roman]
}

first_elements = {
    'number': '1', 
    'ru_up_letter': 'А', 
    'en_up_letter': 'A', 
    'ru_low_letter': 'а', 
    'en_low_letter': 'a', 
    'roman': 'I'
}

class Make_tree:

    def __init__(self):
        self.root = Node("txt")
        self.start = True
        self.tree = []
        self.trees = []

    def similarity_check(self, elem1, elem2):
        if isinstance(elem1, Node):
            return (elem1.data_type == elem2[3] and elem1.sign == elem2[1])
        else:
            return(elem1[3] == elem2[3] and elem1[1] == elem2[1])
    
    def logic_check(self, elem1, elem2):
        l_elem = elem2[0]
        f_elem = elem1.node_name if isinstance(elem1, Node) else elem1
        if isinstance(elem1, Node):
            if elem1.data_type == "numbers":
                return
        node = functions[elem2[3]][0](f_elem) 
        elem = functions[elem2[3]][0](l_elem)

        if isinstance(elem1, Node):
            if node >= elem or (elem - node) > 2:
                return False
            else:
                return True  

        else:
            if node > elem or (elem - node) > 3:
                return False
            else:
                return True       

    def numeral_paragraphs(self, elem):
        paragraph = elem[0].split('.')
        reletives = [elem[0]]
        delimetrs = [elem[4]]
        delimetr = elem[4]
        parent = None
        idx = elem[2] - len(elem[0]) - len(elem[4])
        st = 1
        # Поиск отсутствующих параграфов
        for i in range(2):
            # if len(paragraph) == 1:
            #     delimetr = ''
            #     parent = self.root
            #     break
            p = None
            for i in range(-1, -len(self.tree), -1):
                if self.tree[i].data_type == 'numbers': 
                    node = self.tree[i].node_name.split('.')
                    # Параграфы братья
                    if node[:-1] == paragraph[:-1]:
                        if int(node[-1]) >= int(paragraph[-1]):
                            p = self.tree[i].parent
                            continue
                        if p != self.tree[i].parent:
                            parent, delimetr = self.tree[i].parent, self.tree[i].delimetr
                            break
                    # node это отец текущего параграфа
                    elif node == paragraph[:-1]:
                        parent, delimetr = self.tree[i], self.tree[i].delimetr[:-1]
                        break
                    # # Длина обоих парагпафрв < 2
                    # elif len(paragraph) < 3  and len(node) < 3 and self.tree[i].parent == self.root:
                    #     parent, delimetr = self.tree[i].parent, self.tree[i].delimetr
            if parent:
                break

            delimetr = delimetr[:-1]
            paragraph = paragraph[:-1]
            reletives.append(paragraph)
            delimetrs.append('\n' + delimetr)
        else:
            if len(elem[0].split('.')) == 2:
                sp = list(map(int, elem[0].split('.')))
                if find(self.root, lambda node: node.path_name == "/txt/{}.{}".format(sp[0], sp[1])):
                    return
                if find(self.root, lambda node: node.path_name == "/txt/{}.{}".format(sp[0], int(sp[1])-1)):
                    # self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                    if int(sp[1]) < 3:
                        for i in range(1, sp[1]):
                            self.tree.append(Node('.'.join([sp[0], str(i)]), sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
            return

        # Восстановка отсутствующих параграфов
        buf = []
        for i in range(-1, -len(reletives), -1):
            dt = 'numbers' if parent != self.root else 'number'     # тип параграфа number это параграфы с одним числом, numbers с 2+
            end = int(reletives[i][-1])
            start = 0
            for j in range(len(self.tree)):
                if self.tree[j].node_name.split('.')[:-1] == reletives[i][:-1]:
                    start = int(self.tree[j].node_name.split('.')[-1])
            if (end - start - 1) < 2:
                return
            for k in range(start+1, end):
                buf.append(Node('.'.join(reletives[i][:-1]+[str(k)]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))
            self.tree.extend(buf)
            self.tree.append(Node('.'.join(reletives[i]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))
            if dt == 'number': idx -= 1                
            parent = self.tree[-1]
            delimetr = delimetrs[i]
        # Выравниваем предупреждения по форме предыдущих параграфов
        for i in range(-1, -len(self.tree)-1, -1):
            if self.tree[i].node_name.split('.')[:-1] == elem[0].split('.')[:-1]:
                if self.tree[i].status == 'MISSING':
                    self.tree[i].delimetr = elem[4]
        # Конец проверки
        
        # работаем над параграфом, который нашли и смотрим, каких частей до него не хватает
        end = int(elem[0].split('.')[-1])
        start = 0
        for j in range(len(self.tree)):
            if self.tree[j].node_name.split('.')[:-1] == elem[0].split('.')[:-1]:
                start = int(self.tree[j].node_name.split('.')[-1])
        for k in range(start+1, end):
            self.tree.append(Node('.'.join(elem[0].split('.')[:-1]+[str(k)]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetr = elem[4]))

        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))

    def walk(self, lst):
        for elem, k in zip(lst, range(len(lst))):
            if elem[3] == 'numbers':
                self.numeral_paragraphs(elem)   
            else:
                parent=None
                idx = elem[2] - len(elem[0]) - len(elem[1])
                func, revfunc = functions[elem[3]]
                if 0 < k < len(lst)-1:
                    # Элемент похож на следующий и предыдущий
                    if self.similarity_check(lst[k-1], elem) and self.similarity_check(elem, lst[k+1]):
                        parent = self.tree[-1].parent
                        if self.logic_check(lst[k-1][0], elem) and self.logic_check(elem[0], lst[k+1]):
                            n1, n2 = func(elem[0]), func(self.tree[-1].node_name)
                            for i in range(n2+1, n1):
                                self.tree.append(Node(revfunc(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                            continue
                    # Элемент похож лишь на предыдущий
                    elif self.similarity_check(lst[k-1], elem):
                        parent = self.tree[-1].parent
                        if self.logic_check(self.tree[-1], elem):
                            n1, n2 = func(elem[0]), func(self.tree[-1].node_name)
                            for i in range(n2+1, n1):
                                self.tree.append(Node(revfunc(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                            continue
                    # Элемент похож лишь на следующий
                    # elif self.similarity_check(elem, lst[k+1]):
                    #     if self.logic_check(elem[0], lst[k+1]) and ((lst[k+1][2] - elem[2]) > 10 or '\n' in lst[k+1][4]):
                    #         n1, n2 = func(elem[0]), func(self.tree[-1].node_name)
                    #         for i in range(n2+1, n1):
                    #             self.tree.append(Node(revfunc(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                    #         self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                    #         continue
                    else:
                        if (('\n' not in elem[4]) and (func(elem[0]) - func(first_elements[elem[3]])) > 2) or elem[0] == 'В':
                            continue
                        elif func(elem[0]) == func(first_elements[elem[3]]) and find(self.root, lambda node: node.path_name == "/txt/{}".format(elem[0])):
                            self.trees.append(tree_to_dict(self.root, all_attrs=True))
                            del self.tree
                            del self.root
                            self.root = Node("txt")
                            self.tree = []
                            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                    for i in range(-1, -len(self.tree)-1, -1):                          
                        if self.similarity_check(self.tree[i], elem):
                            if ((self.tree[i+1].parent == self.tree[i].parent) or (self.tree[i].parent == parent)) and i < -1:
                                parent = self.tree[i].parent
                                continue

                            if self.logic_check(self.tree[i], elem):
                                parent = self.tree[i].parent
                                n1, n2 = func(elem[0]), func(self.tree[i].node_name)
                                if (n1-n2-1) > 2:
                                    break
                                for i in range(n2+1, n1):
                                    self.tree.append(Node(revfunc(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                                self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                                break
                    else:
                        parent = self.tree[-1] if self.tree else self.root
                        n = first_elements[elem[3]]
                        if not self.logic_check(n, elem):
                            continue
                            
                        for i in range(func(n), func(elem[0])):                                    
                            self.tree.append(Node(revfunc(i), sign=elem[1], pos=idx, parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                elif k == 0:
                    parent = self.root
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))

        return tree_to_dict(self.root, all_attrs=True)

    def show(self):
        self.root.show(attr_list=["pos", "status"])
