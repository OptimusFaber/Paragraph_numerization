from bigtree import Node, tree_to_dict, find
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from roman_numeral import *

LETTER_SEARCH = -15         # Сколько шагов назад мы сделаем, чтобы найти подобный буквенный параграф
NUMBER_SEARCH = 70          # Сколько шагов назад/вперед мы сделаем, чтобы найти числовой параграф
NON_TEXT_SEARCH = -80
NUM_PARAGRAPH_SEARCH = 90   # Сколько шагов назад/вперед мы сделаем, чтобы найти параграф с несколькими цифрами
DUPLICATE = 0

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
        self.func = None        ## Функция для приведения параграфа в числовой вид
        self.revfunc = None     ## Обратная функция, приводит параграф к его нормальному виду
        self.ancestor = None    ## Последний числовой параграф
        self.tree = []          ## Тут локальное дерево
        self.trees = []         ## Список деревьев
        self.roots = []         ## Список верхушек деревьев
        # Special parametrs
        self.p = []
        self.k = None
        self.non_txt_dct = {'таблица':[], 'рисунок':[], 'рис':[], 'схема':[]}

    def similarity_check(self, elem1, elem2):       ## Метод для проверки что параграф одного типа (элемент и знак)
        if isinstance(elem1, Node): dt1, sgn1 = elem1.data_type, elem1.sign
        elif isinstance(elem1, list) or isinstance(elem1, tuple): dt1, sgn1 = elem1[3], elem1[1]

        if isinstance(elem2, Node): dt2, sgn2 = elem2.data_type, elem2.sign
        elif isinstance(elem2, list) or isinstance(elem2, tuple): dt2, sgn2 = elem2[3], elem2[1]
        
        return (dt1 == dt2 and sgn1 == sgn2)
        
    
    def logic_check(self, elem1, elem2):            ## Метод для проверки что параграфы могут идти друг за другом
        l_elem = elem2[0]

        if isinstance(elem1, Node): f_elem = elem1.node_name
        elif isinstance(elem1, list) or isinstance(elem1, tuple): f_elem = elem1[0]
        else: f_elem = elem1

        node = functions[elem2[3]][0](f_elem) 
        elem = functions[elem2[3]][0](l_elem)

        if node >= elem or (elem - node) > 2:
            return False
        else:
            return True  

    def numeral_check(self, elem1, elem2):
        if isinstance(elem1, Node): elem1 = elem1.node_name     ## Прототип logic_check, но для параграфов с несколькью числами    
        elif isinstance(elem1, list) or isinstance(elem1, tuple): elem1 = elem1[0]          

        if isinstance(elem2, Node): elem2 = elem2.node_name
        elif isinstance(elem2, list) or isinstance(elem2, tuple): elem2 = elem2[0]
        
        elem1, elem2 = list(map(int, elem1.split('.'))), list(map(int, elem2.split('.')))

        if len(elem1) == 1 or len(elem2) == 1:                  ## Случай если число одиночное
            if elem1 == elem2:
                return False
            elif len(elem1) == len(elem2):
                if 0 < int(elem2[0]) - int(elem1[0]) <= 2:
                    return True
            else:
                elem = elem1 if len(elem1) > len(elem2) else elem2
                dif = 0
                for i in elem[1:]:
                    dif += i
                if dif > 3:
                    return False
                return True
            return False
        
        if elem1 == elem2:
            return False
        
        if elem1[0] > elem2[0]:                                 ## Случай что если после 2.1 идет 1.9
            return False
        
        if elem1[0] == elem2[0]:                                ## Первое число совпадает 5.6 и 5.7
            cnt = 0
            dif = len(elem2) - len(elem1)
            if dif > 0:
                for _ in range(dif):
                    elem1.append(1)
            elif dif < 0:
                for _ in range(abs(dif)):
                    elem2.append(1)
            for i in range(1, min(len(elem1), len(elem2))):     ## Вдруг после 5.4 идет 5.6 + ищем разницу между параграфами
                cnt += abs(elem1[i] - elem2[i])
                if elem1[i] > elem2[i]:
                    return False
            if cnt > 3:
                return False
            return True
            
        if elem2[0] - elem1[0] <= 2:                            ## После 5.6 идет 6.1
            cnt = 1
            for i in range(1, min(len(elem1), len(elem2))):     ## Главное чтобы после 5.6 не шло 6.4
                cnt += abs(0 - elem2[i])
            if cnt > 3:
                return False
            else:
                return True
        elif elem2[0] - elem1[0] > 1:
            return False
        

    def non_text(self, elem):
        parent = self.root
        for i in range(-1, max(-len(self.tree)-1, NON_TEXT_SEARCH), -1):
            if self.similarity_check(elem, self.tree[i]):
                prev = self.tree[i].node_name.split(" ")[-1]
                if self.logic_check(prev, elem):
                    n1, n2 = self.func(elem[0]), self.func(prev)
                    if (n1-n2-1) > 2:
                        return
                    for i in range(n2+1, n1):
                        if self.revfunc(i) in self.non_txt_dct[elem[1]]:
                            continue
                        try:
                            self.tree.append(Node(elem[1] + " " + self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                            self.non_txt_dct[elem[1]].append(self.revfunc(i))
                        except:
                            self.trees.append({"DUPLICATE": {'name':elem[1] + " " + self.revfunc(i), 'sign':elem[1], 'pos':elem[2], 'parent':parent, 'data_type':elem[3], 'status':'DUPLICATE', 'delimetr':elem[4]}})
                    try:
                        self.tree.append(Node(elem[1] + " " + elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                        self.non_txt_dct[elem[1]].append(elem[0])
                    except:
                        self.trees.append({"DUPLICATE": {'name':elem[1] + " " + elem[0], 'sign':elem[1], 'pos':elem[2], 'parent':parent, 'data_type':elem[3], 'status':'DUPLICATE', 'delimetr':elem[4]}})
                    return
        else:
            if self.func(elem[0]) - self.func(self.n) <= 2:
                for i in range(self.func(self.n), self.func(elem[0])):
                    if self.revfunc(i) in self.non_txt_dct[elem[1]]:
                        continue
                    try:
                        self.tree.append(Node(elem[1] + " " + self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                        self.non_txt_dct[elem[1]].append(self.revfunc(i))
                    except:
                        self.trees.append({"DUPLICATE": {'name':elem[1] + " " + self.revfunc(i), 'sign':elem[1], 'pos':elem[2], 'parent':parent, 'data_type':elem[3], 'status':'DUPLICATE', 'delimetr':elem[4]}})
            try:
                self.tree.append(Node(elem[1] + " " + elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                self.non_txt_dct[elem[1]].append(elem[0])
            except:
                self.trees.append({"DUPLICATE": {'name':elem[1] + " " + elem[0], 'sign':elem[1], 'pos':elem[2], 'parent':parent, 'data_type':elem[3], 'status':'DUPLICATE', 'delimetr':elem[4]}})
        
    def letters_romans(self, elem, k):      ## Алгоритм работы с буквенными параграфами
        parent = None
        if self.func(elem[0]) == self.func(self.n) and self.tree[-1].data_type != elem[3]:   ## Вдруг это первый элемент последовательности
            parent=self.tree[-1]
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
                            self.tree.append(Node(self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                        return 
            else:                                                   ## Первого элемента нет, но есть второй
                if self.func(elem[0]) - self.func(self.n) == 1:
                    parent=self.tree[-1]
                    self.tree.append(Node(self.n, sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
        
    def single_numbers(self, elem, k):                 ## Алгоритм работы с числовами параграфами
        parent = None
        if (self.func(elem[0]) == self.func(self.n)) or (self.func(elem[0]) - self.func(self.n) < 2 and elem[1] not in self.p):
            st = 0
            if self.ancestor and self.tree:    # если это не новое дерево 
                for i in range(k+1, min(len(self.lst), k+NUMBER_SEARCH)):   # иду по нераспределенным элементам, смотрю что впереди
                    param = ok = False
                    if 'number' not in self.lst[i][3]: continue
                    if self.similarity_check(elem, self.lst[i]):
                        if self.logic_check(elem[0], self.lst[i]): 
                            param = True
                            st += 1
                    if self.lst[i][2]-self.ancestor.pos > 100: continue
                    ancestors = [self.ancestor] + list(self.ancestor.ancestors)
                    for n in ancestors[:-1]:
                        if 'number' in n.data_type and n.sign not in ["таблица", "рисунок", "рис", "схема"]:
                            if self.numeral_check(n.name, self.lst[i][0]) and self.lst[i][1] == n.sign:
                                if (st and not param) or st > 1: parent=self.tree[-1]
                                elif param: return False
                                ok = True
                                break
                    if ok: break

                else:
                    if self.tree[-1].sign == 'таблица':
                        parent = self.tree[-1]
                        st = True
                    else:
                        c = 0
                        for obj in self.tree: 
                            if obj.status == "EXISTING":
                                c += 1
                        if c > 1:
                            self.trees.append(tree_to_dict(self.root, all_attrs=True))
                            self.roots.append(self.root)
                        self.root, self.tree, self.ancestor = Node("txt"), [], None
                        parent, st = self.root, True  
            else:
                parent, st = self.root, True

            if st:
                if self.func(elem[0]) == 2:
                    self.tree.append(Node(self.n, sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                    if elem[1] in self.p:
                        self.p.remove(elem[1])
                self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                self.ancestor = self.tree[-1]
                if self.func(elem[0]) == 1:
                    self.p.append(elem[1])
        else:
            black_list = set()
            for i in range(-1, max(-len(self.tree)-1, -NUMBER_SEARCH), -1):  
                if self.similarity_check(self.tree[i], elem):
                    if self.tree[i].parent in black_list:
                        continue
                    if self.logic_check(self.tree[i], elem):
                        parent = self.tree[i].parent
                        n1, n2 = self.func(elem[0]), self.func(self.tree[i].node_name)
                        if (n1-n2-1) > 2:
                            continue
                        for i in range(n2+1, n1):
                            self.tree.append(Node(self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                        self.ancestor = self.tree[-1]
                        return 
                    else:
                        black_list.add(self.tree[i].parent)
            else:
                if self.func(elem[0]) > 2: return
                if self.tree[-1].sign == 'таблица':
                        parent = self.tree[-1]
                        st = True
                else:
                    c = 0
                    for obj in self.tree: 
                        if obj.status == "EXISTING":
                            c += 1
                    if c > 1:
                        self.trees.append(tree_to_dict(self.root, all_attrs=True))
                        self.roots.append(self.root)
                    self.root, self.tree = Node("txt"), []
                    parent = self.root  
                param = True
                if self.func(elem[0]) == 2:
                    self.tree.append(Node(self.n, sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                self.ancestor = self.tree[0]

    def numeral_paragraphs(self, elem):                 # Алгоритм работы с параграфами где несколько чисел
        delimetr = elem[4]
        parent = None
        sp = []
        black_list = set()
        for i in range(-1, max(-len(self.tree)-1, -NUM_PARAGRAPH_SEARCH), -1):
            if 'number' in self.tree[i].data_type and (elem[1] == self.tree[i].sign or self.tree[i].sign == 'NaN'):
                if self.numeral_check(self.tree[i], elem) and (self.tree[i].parent not in black_list):
                    node = self.tree[i]
                    if elem[2] - node.pos > 40: continue
                    ## добавить определение parent-a тк он думает что отец 1.3.1 это 1.2.1
                    parent, delimetr = node, node.delimetr
                    rel = list(map(int, node.node_name.split('.')))
                    sp = list(map(int, elem[0].split('.')))
                    if len(rel) == len(sp):
                        parent = node.parent
                    adress = []
                    k1 = k2 = True
                    dif = len(sp) - len(rel)
                    param = False
                    if len(sp) > len(rel):
                        for _ in range(dif):rel.append(0)
                    for e in range(min(len(rel), len(sp))):
                        if rel[e] == sp[e] and k1:
                            adress.append(sp[e])
                            continue
                        elif k2:
                            for i in range(1, len(rel) - e):
                                if parent != self.root:
                                    parent = parent.parent
                            k1 = k2 = False
                            if e==0:
                                for j in range(rel[e]+1, sp[e]):
                                    self.tree.append(Node('{}.1'.format(j), sign='.', pos=elem[2], parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))  
                                    param = True
                            else:
                                for j in range(rel[e]+1, sp[e]):  
                                    self.tree.append(Node('.'.join(list(map(str, adress+[j]))), sign='.', pos=elem[2], parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))
                                    param = True
                                if len(sp) > e+1:
                                    self.tree.append(Node('.'.join(list(map(str, adress+[sp[e]]))), sign='.', pos=elem[2], parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))
                                    param = True
                            adress.append(sp[e])
                        else:
                            parent = self.tree[-1]
                            for j in range(1, sp[e]):  
                                self.tree.append(Node('.'.join(list(map(str, adress+[j]))), sign='.', pos=elem[2], parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))
                                param = True
                            adress.append(sp[e])
                    
                    if 'number' in self.tree[-1].data_type and (elem[1] == self.tree[-1].sign or self.tree[-1].sign=='NaN'): 
                        if self.numeral_check(self.tree[-1], elem):
                            rel = self.tree[-1].node_name.split(".")
                            parent = self.tree[-1] if len(sp) != len(rel) else self.tree[-1].parent
                            if len(rel) > len(sp):
                                for i in range(len(rel) - len(sp)+1):
                                    parent = parent.parent
                    if len(node.node_name) == 1:
                        parent = parent.parent
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                    self.ancestor = self.tree[-1]  
                    return
                else:
                    black_list.add(self.tree[i].parent)
        else:
            if len(elem[0].split('.')) == 2:
                sp = list(map(int, elem[0].split('.')))
                if sp[0] > 2: return False
                if sp[1] > 3: return False
                st = 0
                if find(self.root, lambda node: node.path_name == "/txt/{}.{}".format(*sp)):
                    for i in range(self.k+1, min(len(self.lst), self.k+NUM_PARAGRAPH_SEARCH)):
                        param = ok = False
                        if 'number' not in self.lst[i][3] and elem[1] != self.lst[i][1]: continue
                        if self.numeral_check(elem[0], self.lst[i][0]):
                            param = True
                            st += 1
                        if self.lst[i][2]-self.ancestor.pos > 40: break
                        ancestors = [self.ancestor] + list(self.ancestor.ancestors) 
                        for n in ancestors[:-1]:
                            if 'number' in n.data_type and n.sign == self.lst[i][1]:
                                if self.numeral_check(n.name, self.lst[i][0]):
                                    if (st and not param) or st > 1: parent=self.tree[-1]
                                    elif param: return False
                                    ok = True
                                    break
                        if ok: break

                    else:   # Делаем новое дерево
                        c = 0
                        for obj in self.tree: 
                            if obj.status == "EXISTING":
                                c += 1
                        if c > 1:
                            self.trees.append(tree_to_dict(self.root, all_attrs=True))
                        self.roots.append(self.root)
                        self.root, self.tree = Node("txt"), []
                        parent= self.root
                        st = True

                else:
                    if not self.tree:
                        parent, st = self.root, True
  
                if st:
                    for i in range(1, sp[0]):
                        try:
                            self.tree.append(Node("{}.1".format(i), sign='.', pos=elem[2], parent=parent, data_type='numbers', status='MISSING', delimetr = elem[4]))
                        except:
                            self.trees.append({"DUPLICATE": {'name':"{}.1".format(i), 'sign':'.', 'pos':elem[2], 'parent':parent, 'data_type':'numbers', 'status':'DUPLICATE', 'delimetr':elem[4]}})
                    for i in range(1, sp[1]):
                        try:
                            self.tree.append(Node("{}.{}".format(sp[0], i), sign='.', pos=elem[2], parent=parent, data_type='numbers', status='MISSING', delimetr = elem[4]))
                        except:
                            self.trees.append({"DUPLICATE": {'name':"{}.{}".format(sp[0], i), 'sign':'.', 'pos':elem[2], 'parent':parent, 'data_type':'numbers', 'status':'DUPLICATE', 'delimetr':elem[4]}})
                    self.tree.append(Node(elem[0], sign='.', pos=elem[2], parent=parent, data_type='numbers', status='EXISTING', delimetr = elem[4]))
                    self.ancestor = self.tree[-1]
                

    def walk(self, lst):
        self.lst = lst
        for elem, k in zip(self.lst, range(len(self.lst))):
            self.k = k
            if elem[1] in ["таблица", "рисунок", "рис", "схема"]:
                self.func, self.revfunc = functions[elem[3]]
                self.n = first_elements[elem[3]]
                self.non_text(elem)
                continue
            if elem[3] == 'numbers':
                self.numeral_paragraphs(elem)  
            else:
                self.func, self.revfunc = functions[elem[3]]
                self.n = first_elements[elem[3]]

                if 'letter' in elem[3] or 'roman' in elem[3]:
                    self.letters_romans(elem, k)
                elif elem[3] == 'number':
                    self.single_numbers(elem, k)
                    
        self.trees.append(tree_to_dict(self.root, all_attrs=True))
        self.roots.append(self.root)
        return self.trees

    def show(self):
        for root in self.roots:
            root.show(attr_list=["pos", "status"])