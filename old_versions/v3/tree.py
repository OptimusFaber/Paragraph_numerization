from bigtree import Node, tree_to_dict, find
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from roman_numeral import *

LETTER_SEARCH = -15     # Сколько шагов назад мы сделаем, чтобы найти подобный буквенный параграф
NUMBER_SEARCH = 70      # Сколько шагов назад/вперед мы сделаем, чтобы найти числовой параграф
NUM_PARAGRAPH_SEARCH = 90   # Сколько шагов назад/вперед мы сделаем, чтобы найти параграф с несколькими цифрами

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
        self.param = None
        self.tree = []      # Тут локальное дерево
        self.trees = []     # Список деревьев
        self.roots = []     # Список верхушек деревьев
        # Special parametrs #
        self.p = True
        self.k = None

    def similarity_check(self, elem1, elem2):       # Метод для проверки что параграф одного типа (элемент и знак)
        if isinstance(elem1, Node):
            return (elem1.data_type == elem2[3] and elem1.sign == elem2[1])
        else:
            return(elem1[3] == elem2[3] and elem1[1] == elem2[1])
    
    def logic_check(self, elem1, elem2):            # Метод для проверки что параграфы могут идти друг за другом
        l_elem = elem2[0]
        f_elem = elem1.node_name if isinstance(elem1, Node) else elem1
        if isinstance(elem1, Node):
            if elem1.data_type == "numbers":
                return False

        node = functions[elem2[3]][0](f_elem) 
        elem = functions[elem2[3]][0](l_elem)

        if node >= elem or (elem - node) > 2:
            return False
        else:
            return True  

    def numeral_check(self, elem1, elem2):          # Прототип logic_check, но для параграфов с несколькью числами
        elem1 = elem1.node_name if isinstance(elem1, Node) else elem1 
        elem2 = elem2.node_name if isinstance(elem2, Node) else elem2
        elem1, elem2 = list(map(int, elem1.split('.'))), list(map(int, elem2.split('.')))
        if len(elem1) == 1 or len(elem2) == 1:
            return False
        if elem1[0] > elem2[0]:
            return False
        if elem1[0] == elem2[0]:
            if elem1[1] > elem2[1]:
                return False
            cnt = 0
            for i in range(1, min(len(elem1), len(elem2))):
                cnt += abs(elem1[i] - elem2[i])
            if cnt > 8:
                return False
            else:
                return True
        if elem2[0] - elem1[0] == 1:
            return True
        elif elem2[0] - elem1[0] > 1:
            return False
        
    def letters_romans(self, elem, k):      # Алгоритм работы с буквенными параграфами
        parent = None
        if self.func(elem[0]) - self.func(self.n) < 2 and self.tree[-1].data_type != elem[3]:
            parent=self.tree[-1]
            if self.func(elem[0]) - self.func(self.n):
                self.tree.append(Node(self.n, sign=elem[1], pos=self.idx, parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
        else:
            for i in range(-1, max(-len(self.tree)-1, LETTER_SEARCH), -1):  
                if self.similarity_check(self.tree[i], elem):
                    if ((self.tree[i+1].parent == self.tree[i].parent) or (self.tree[i].parent == parent)) and i < -1:
                        parent = self.tree[i].parent
                        continue

                    if self.logic_check(self.tree[i], elem):
                        parent = self.tree[i].parent
                        n1, n2 = self.func(elem[0]), self.func(self.tree[i].node_name)
                        if (n1-n2-1) > 2:
                            return
                        for i in range(n2+1, n1):
                            self.tree.append(Node(self.revfunc(i), sign=elem[1], pos=self.idx, parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                        return 
        
    def numbers(self, elem, k):                 # Алгоритм работы с числовами параграфами
        parent = None
        if self.func(elem[0]) - self.func(self.n) < 2 and self.p:
            st = False
            if self.param and self.tree:
                path = self.param.path_name.split('/')[2:]
                for i in range(k+1, min(len(self.lst), k+NUMBER_SEARCH)):
                    if 'number' not in self.lst[i][3]:
                        continue
                    if self.similarity_check(elem, self.lst[i]):
                        if self.logic_check(elem[0], self.lst[i]):
                            st = True
                    for el in path:
                        if self.numeral_check(el, self.lst[i][0]):
                            if st:
                                parent=self.tree[-1]
                            break
                    else:
                        continue
                    break
                else:
                    self.trees.append(tree_to_dict(self.root, all_attrs=True))
                    self.roots.append(self.root)
                    # del self.tree
                    # del self.root
                    self.root, self.tree = Node("txt"), []
                    parent, st = self.root, True  
            else:
                parent, st = self.root, True

            if st:
                if self.func(elem[0]) - self.func(self.n) and not find(self.root, lambda node: node.path_name == parent.path_name + '/1'):
                    self.tree.append(Node(self.n, sign=elem[1], pos=self.idx, parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                self.param = self.tree[-1]
                self.p = self.func(elem[0]) - self.func(self.n)
        else:
            for i in range(-1, max(-len(self.tree)-1, -NUMBER_SEARCH), -1):  
                if self.similarity_check(self.tree[i], elem):
                    if i < -1:
                        if ((self.tree[i+1].parent == self.tree[i].parent) or (self.tree[i].parent == parent)) and self.tree[i+1].data_type == self.tree[i].data_type:
                            parent = self.tree[i].parent
                            continue
                    if self.logic_check(self.tree[i], elem):
                        parent = self.tree[i].parent
                        n1, n2 = self.func(elem[0]), self.func(self.tree[i].node_name)
                        if (n1-n2-1) > 2:
                            return
                        for i in range(n2+1, n1):
                            self.tree.append(Node(self.revfunc(i), sign=elem[1], pos=self.idx, parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                        self.param = self.tree[-1]
                        self.p = True
                        return 

    def numeral_paragraphs(self, elem):                 # Алгоритм работы с параграфами где несколько чисел
        paragraph = elem[0].split('.')
        reletives = [elem[0]]
        delimetrs = [elem[4]]
        delimetr = elem[4]
        parent = None
        idx = elem[2] - len(elem[0]) - len(elem[4])
        # Поиск отсутствующих параграфов
        for i in range(2):
            p = None
            for i in range(-1, max(-len(self.tree), -NUM_PARAGRAPH_SEARCH), -1):
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
                    st = False
                    path = self.param.path_name.split('/')[2:]
                    for i in range(self.k+1, min(len(self.lst), self.k+NUM_PARAGRAPH_SEARCH)):
                        if self.param and self.tree:
                            if 'numbers' not in self.lst[i][3]:
                                continue
                            if self.numeral_check(elem[0], self.lst[i][0]):
                                st = True
                            for el in path:
                                if self.numeral_check(el, self.lst[i][0]):
                                    if st:
                                        parent=self.tree[-1]
                                        if sp[0] > 2:
                                            if not find(self.root, lambda node: node.path_name == parent.path_name + "/{}.1".format(sp[0])):
                                                return False
                                    break
                            else:
                                continue
                            break
                        else:
                            parent, st = self.root, True
                    else:   # Делаем новое дерево
                        self.trees.append(tree_to_dict(self.root, all_attrs=True))
                        self.roots.append(self.root)
                        del self.tree
                        del self.root
                        self.root, self.tree = Node("txt"), []
                        parent, st = self.root, True

                else:
                    if self.param.data_type == 'numbers':
                        if not self.numeral_check(self.param.node_name, elem[0]):
                            return
                    parent, st = self.root, True

                if st:
                    if (sp[0] == 2 or sp[0] == 1) and (not find(self.root, lambda node: node.path_name == parent.path_name + '/1.1') and elem[0] != '1.1'):
                        self.tree.append(Node('{}.{}'.format(sp[0], 1), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                    self.param = self.tree[-1]
            return

        # Восстановка отсутствующих параграфов
        for i in range(-1, -len(reletives), -1):
            start, end = 0, int(reletives[i][-1])
            for j in range(len(self.tree)):
                if self.tree[j].node_name.split('.')[:-1] == reletives[i][:-1]:
                    start = int(self.tree[j].node_name.split('.')[-1])
            if (end - start - 1) > 3:
                return
            for k in range(start+1, end):
                self.tree.append(Node('.'.join(reletives[i][:-1]+[str(k)]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))
            self.tree.append(Node('.'.join(reletives[i]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))               
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
        self.param = self.tree[-1]

    def walk(self, lst):
        self.lst = lst
        for elem, k in zip(self.lst, range(len(self.lst))):
            self.k = k
            if elem[3] == 'numbers':
                self.numeral_paragraphs(elem)  
            else:
                self.idx = elem[2] - len(elem[0]) - len(elem[1])
                self.func, self.revfunc = functions[elem[3]]
                self.n = first_elements[elem[3]]

                if 'letter' in elem[3] or 'roman' in elem[3]:
                    self.letters_romans(elem, k)
                elif elem[3] == 'number':
                    self.numbers(elem, k)
                    
        self.trees.append(tree_to_dict(self.root, all_attrs=True))
        self.roots.append(self.root)
        return self.trees

    def show(self):
        for root in self.roots:
            root.show(attr_list=["pos", "status"])