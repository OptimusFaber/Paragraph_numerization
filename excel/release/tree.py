from bigtree import Node, tree_to_dict, find
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from roman_numeral import *
import logging

LETTER_SEARCH = -30         # Сколько шагов назад мы сделаем, чтобы найти подобный буквенный параграф
NUMBER_SEARCH = 70          # Сколько шагов назад/вперед мы сделаем, чтобы найти числовой параграф
NON_TEXT_SEARCH = -80
NUM_PARAGRAPH_SEARCH = 70   # Сколько шагов назад/вперед мы сделаем, чтобы найти параграф с несколькими цифрами
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
        self.main_line_num = None
        self.content_set = set()
        self.last_alpha = None
        #! Special parametrs
        self.p = []
        self.k = None
        self.non_txt_dct = {'таблица':[], 'рисунок':[], 'рис':[], 'схема':[], 'приложение':[]}
        self.content = True

    def similarity_check(self, elem1, elem2):
        ## Метод для проверки что параграф одного типа (элемент и знак) ##
        if isinstance(elem1, Node): dt1, sgn1 = elem1.data_type, elem1.sign
        elif isinstance(elem1, list) or isinstance(elem1, tuple): dt1, sgn1 = elem1[3], elem1[1]
        if isinstance(elem2, Node): dt2, sgn2 = elem2.data_type, elem2.sign
        elif isinstance(elem2, list) or isinstance(elem2, tuple): dt2, sgn2 = elem2[3], elem2[1]
        return (dt1 == dt2 and sgn1 == sgn2)
        
    
    def logic_check(self, elem1, elem2):
        ## Метод для проверки что параграфы могут идти друг за другом ##
        if elem1 is None or elem2 is None:
            return
        l_elem = elem2[0]

        if isinstance(elem1, Node): f_elem = elem1.node_name
        elif isinstance(elem1, list) or isinstance(elem1, tuple): f_elem = elem1[0]
        else: f_elem = elem1

        node = functions[elem2[3]][0](f_elem) 
        elem = functions[elem2[3]][0](l_elem)

        if node >= elem or (elem - node) > 4:
            return False
        else:
            return True  

    def numeral_check(self, elem1, elem2):
        ## Прототип logic_check, но для параграфов с несколькью числами ##
        #!-----------Если один из элементов пустой---------------
        if elem1 is None or elem1 is None:
            return False
        if isinstance(elem1, Node): elem1 = elem1.node_name         
        elif isinstance(elem1, list) or isinstance(elem1, tuple): elem1 = elem1[0]          
        if isinstance(elem2, Node): elem2 = elem2.node_name
        elif isinstance(elem2, list) or isinstance(elem2, tuple): elem2 = elem2[0]
        #!---------Приводим всё к числовому типу данных-----------
        elem1, elem2 = list(map(int, elem1.split('.'))), list(map(int, elem2.split('.')))
        #!---Невозможные ситуации, которые мы сразу отбрасываем---
        if elem1[0] > elem2[0] or elem1 == elem2 or (elem2[0] - elem1[0]) > 5:
            return 0
        #!--------Случай если одно число одиночное 4 и 5.2--------
        if len(elem1) == 1 or len(elem2) == 1:
            if len(elem1) == len(elem2):
                if elem2[0] - elem1[0] <= 5:
                    return True
            else:
                if len(elem1) > len(elem2):
                    if elem2[0] - elem1[0] <= 5: return elem2[0] - elem1[0]
                dif = elem2[0] - elem1[0]
                for i in elem2[1:]: dif += i
                if dif > 7: return 0
                return dif+1
        #!---------Первое число совпадает 5.6 и 5.8--------------
        if elem1[0] == elem2[0]:                                
            dif = 0
            if len(elem2) - len(elem1) > 0:
                for _ in range(len(elem2) - len(elem1)):
                    elem1.append(1)
            flag = True
            for i in range(1, min(len(elem1), len(elem2))):
                if flag:
                    if elem1[i] > elem2[i]: return 0
                    elif elem1[i] < elem2[i]:
                        dif += abs(elem2[i] - elem1[i])
                        flag = False
                    else: continue
                else: dif += (elem2[i]-1)
            if dif > 7: return 0
            return dif+1
        #!--------------После 5.6 идет 7.1---------------------- 
        if elem2[0] - elem1[0] <= 7:
            dif = 0
            flag = True
            for i in range(0, min(len(elem1), len(elem2))):
                if flag:
                    dif += abs(elem2[i] - elem1[i] - 1)
                    if elem2[i] != elem1[i]: flag = False
                else:
                    dif += abs(elem2[i])
            if len(elem2) > len(elem1): dif += sum(elem2[len(elem1):])
            if dif > 7: return 0
            else: return dif+1
        #!------------------------------------------------------
        

    def non_text(self, elem):
        parent = self.root
        for i in range(-1, max(-len(self.tree)-1, NON_TEXT_SEARCH), -1):
            if self.similarity_check(elem, self.tree[i]):
                prev = self.tree[i].node_name.split(" ")[-1]
                if self.logic_check(prev, elem):
                    n1, n2 = self.func(elem[0]), self.func(prev)
                    if (n1-n2-1) > 4:
                        return
                    for i in range(n2+1, n1):
                        if self.revfunc(i) in self.non_txt_dct[elem[1]]:
                            continue
                        try:
                            self.tree.append(Node(elem[1] + " " + self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                            self.non_txt_dct[elem[1]].append(self.revfunc(i))
                        except:
                            if self.tree[-1].name == elem[1] and elem[2] - self.tree[-1].pos < 10:
                                return
                            self.tree.append(Node(" " + elem[1] + " " + self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                    try:
                        self.tree.append(Node(elem[1] + " " + elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
                        self.non_txt_dct[elem[1]].append(elem[0])
                    except:
                        if self.tree[-1].name == elem[1] and elem[2] - self.tree[-1].pos < 10:
                            return
                        self.tree.append(Node(" " + elem[1] + " " + elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                    return
        else:
            if self.func(elem[0]) - self.func(self.n) <= 2:
                for i in range(self.func(self.n), self.func(elem[0])):
                    if self.revfunc(i) in self.non_txt_dct[elem[1]]:
                        continue
                    try:
                        self.tree.append(Node(elem[1] + " " + self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                        self.non_txt_dct[elem[1]].append(self.revfunc(i))
                    except:
                        try:
                            if self.tree[-1].name == elem[1] and elem[2] - self.tree[-1].pos < 10:
                                return
                            self.tree.append(Node(" " + elem[1] + " " + self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                        except:
                            return                        
            try:
                self.tree.append(Node(elem[1] + " " + elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
                self.non_txt_dct[elem[1]].append(elem[0])
            except:
                try:
                    if self.tree[-1].name == elem[1] and elem[2] - self.tree[-1].pos < 10:
                        return
                    self.tree.append(Node(" " + elem[1] + " " + elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                except:
                    return
        
    def letters_romans(self, elem):      ## Алгоритм работы с буквенными параграфами
        parent = None
        if self.tree:
            if self.func(elem[0]) == self.func(self.n) and self.tree[-1].data_type != elem[3]:   ## Вдруг это первый элемент последовательности
                for i in range(-1, max(-len(self.tree)-1, -NUM_PARAGRAPH_SEARCH), -1):
                    parent=self.tree[-1]
                    if self.similarity_check(self.tree[i], elem):
                        if self.tree[i].node_name == elem[0]:
                            self.tree.append(Node(" " + elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                            self.last_alpha = self.tree[-1]
                            return
                        break
                self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
                self.last_alpha = self.tree[-1]
                return
            black_list = []
            duplic = False
            for i in range(-1, max(-len(self.tree)-1, LETTER_SEARCH), -1):  
                if self.tree[i].name == elem[0] and self.tree[i].sign == elem[1] and self.tree[i].data_type == elem[3]:
                    if not duplic and i > -10:
                        duplic = self.tree[i]
                if self.similarity_check(self.tree[i], elem):
                    if (self.tree[i].parent in black_list) and i < -1:
                        parent = self.tree[i].parent
                        continue

                    if self.logic_check(self.tree[i], elem):
                        parent = self.tree[i].parent
                        n1, n2 = self.func(elem[0]), self.func(self.tree[i].node_name)
                        if (n1-n2-1) > 4:
                            return
                        for i in range(n2+1, n1):
                            if chr(i) == 'й' or chr(i) == 'Й':
                                continue
                            self.tree.append(Node(self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
                        self.last_alpha = self.tree[-1]
                        return 
                    else:
                        black_list.append(self.tree[i].parent)
            else:                                                   ## Первого элемента нет, но есть второй
                for i in range(-1, max(-len(self.tree)-1, -NUM_PARAGRAPH_SEARCH), -1):
                    if self.similarity_check(self.tree[i], elem):
                        if self.tree[i].node_name == elem[0]:
                            self.tree.append(Node(" " + elem[0], sign=elem[1], pos=elem[2], parent=self.tree[i].parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                            self.last_alpha = self.tree[-1]
                            return
                        break
                if self.func(elem[0]) - self.func(self.n) == 1:
                    parent=self.tree[-1]
                    self.tree.append(Node(self.n, sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
                    self.last_alpha = self.tree[-1]
                    return
                
            #* КОСТЫЛЬ
            #* (спускаемся по нераспределенному дереву вниз на пару элементов)------------------------------------------------------------------------------------------------
            alpha_list = list(filter(lambda par: "number" not in par[3], self.lst[self.k+1:]))
            prev = None
            st = False
            for i in range(min(len(alpha_list), 10)):  
            ## иду по нераспределенным элементам, смотрю что впереди
                if elem[1] == alpha_list[i][1]:
                    if self.logic_check(elem, alpha_list[i]) and (prev is None or not self.logic_check(prev, alpha_list[i])): 
                        parent = self.root
                ## считаем что опечатка может быть лишь в прямой посл-ти (типа 1 2 2 3 4), а не в подпосл-ти (типа 1 2 2.1 2.2 2 3 4)
                ## сюда попадают цифры 1 и 2, так что новую посл-ть не будем делать, если пред. элемент это также 1 или 2
                if self.last_alpha:
                    if self.last_alpha.sign == alpha_list[i][1]:
                        if self.logic_check(self.last_alpha, alpha_list[i]) and (prev is None or not self.logic_check(prev, alpha_list[i])):
                            #! СЛАБОЕ МЕСТО-----------------------------------------------------------------------------
                            if duplic:
                                self.tree.append(Node(" " + elem[0], sign=elem[1], pos=elem[2], parent=duplic.parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                                return
                            #! -----------------------------------------------------------------------------------------
                prev = alpha_list[i]
            else:
                if ord(elem[0].lower()) > ord("б"):
                    return
                parent, st = self.tree[-1], True  
            ## Проверяем статус элемента - надо ли добавлять новую ветку или нет
            if st:
                if self.func(elem[0]) == 2:
                    self.tree.append(Node(self.n, sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
                self.last_alpha = self.tree[-1]
                return
            #* ---------------------------------------------------------------------------------------------------------------------------------------------------------------
            if duplic:
                self.tree.append(Node(" " + elem[0], sign=elem[1], pos=elem[2], parent=duplic.parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                self.last_alpha = self.tree[-1]
                return
        
    def single_numbers(self, elem):                 ## Алгоритм работы с числовами параграфами
        parent = None
        if (self.func(elem[0]) == self.func(self.n)) or (self.func(elem[0]) - self.func(self.n) < 2 and elem[1] not in self.p):
            st = 0
            if self.ancestor and self.tree:    ## если это не новое дерево 
                if (self.tree[-1].sign == 'таблица' or self.tree[-1].sign == 'приложение') and elem[2] - self.tree[-1].pos < 7:
                    parent = self.tree[-1]
                    st = True
                else:
                    num_list = list(filter(lambda par: "number" in par[3], self.lst[self.k+1:]))
                    prev = None
                    for i in range(len(num_list)):   
                        ## иду по нераспределенным элементам, смотрю что впереди
                        param = False
                        if elem[1] == num_list[i][1]:
                            if self.numeral_check(elem[0], num_list[i][0]) and (prev is None or not self.numeral_check(prev, num_list[i])): 
                                param = True
                                st += 1
                                parent = self.root
                        ## считаем что опечатка может быть лишь в прямой посл-ти (типа 1 2 2 3 4), а не в подпосл-ти (типа 1 2 2.1 2.2 2 3 4)
                        ## сюда попадают цифры 1 и 2, так что новую посл-ть не будем делать, если пред. элемент это также 1 или 2
                        if self.main_line_num:
                            flag = False
                            if self.main_line_num.sign == num_list[i][1]:
                                if self.numeral_check(self.main_line_num.name, num_list[i][0]):
                                    if prev is not None:
                                        if self.numeral_check(prev, num_list[i]) and prev[1] != num_list[i][1]:
                                            flag = True
                                    else:
                                        flag = True
                                    if flag:
                                        #! СЛАБОЕ МЕСТО-----------------------------------------------------------------------------
                                        if int(self.main_line_num.name.split('.')[0]) == 1 and int(elem[0]) == 2: parent=self.main_line_num.parent
                                        elif (st and not param) or st > 1: parent=self.tree[-1]
                                        else: parent=self.tree[-1]
                                        #! -----------------------------------------------------------------------------------------
                                        st=True
                                        break
                        prev = num_list[i]
                    else:
                        ## Проверяем, что дерево у нас не пустое
                        c = 0
                        for obj in self.tree:            
                            if obj.status == "EXISTING":
                                c += 1
                        if c > 1:
                            self.content = False
                            self.trees.append(tree_to_dict(self.root, all_attrs=True))
                            self.roots.append(self.root)
                        self.root, self.tree, self.ancestor = Node("txt"), [], None
                        parent, st = self.root, True  
            else:
                parent, st = self.root, True
            ## Проверяем статус элемента - надо ли добавлять новую ветку или нет
            if st:
                if self.func(elem[0]) == 2:
                    self.tree.append(Node(self.n, sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                    if elem[1] in self.p:
                        if elem[0] == '2':
                            self.p.remove(elem[1])
                self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))

                ## Добавляем инфу о параграфе в список
                if self.content: self.content_set.add(elem[2])
                if parent.node_name == 'txt': self.main_line_num = self.tree[-1]
                self.ancestor = self.tree[-1]
                if self.func(elem[0]) == 1:
                    self.p.append(elem[1])
                return

        posible_relatives = []
        black_list = set()
        for i in range(-1, max(-len(self.tree)-1, -NUMBER_SEARCH), -1):  
            if self.tree[i].sign not in ["таблица", "рисунок", "рис", "схема", "приложение"]:
                point = list(self.tree[i].ancestors)      #! СЛАБОЕ МЕСТО
                break
        table = False
        duplic = False
        for i in range(-1, -len(self.tree)-1, -1):  
            if ("таблица" in self.tree[i].parent.name or "приложение" in self.tree[i].parent.name) and table:
                continue
            if "таблица" in self.tree[i].name or "приложение" in self.tree[i].name:
                table = True
                continue
            if self.tree[i].sign != elem[1]:
                continue
            if  self.tree[i].data_type != "number": continue
            if self.tree[i].name == elem[0]:
                if not duplic and i > -20:
                    duplic = self.tree[i]
            if self.logic_check(self.tree[i], elem):
                if len(point) < len(list(self.tree[i].ancestors)): continue
                if self.tree[i].parent in black_list: continue
                n1, n2 = self.func(elem[0]), self.func(self.tree[i].node_name)
                if (n1-n2-1) > 4: continue
                posible_relatives.append(self.tree[i])
                black_list.add(self.tree[i].parent)
            else:
                black_list.add(self.tree[i].parent)
            ## Дальше уже нет смысла искать
            if self.tree[i].parent.name == 'txt':
                if not duplic:
                    if (str(self.tree[i]).split('.')[0]) < (str(elem[0]).split('.')[0]):
                        if self.tree[i].sign == elem[1]:
                            num1 = int(str(elem[0]).split('.')[0])
                            num2 = int(str(self.tree[i].name).split('.')[0])
                            if num2 - num1 < 3:
                                duplic = self.tree[i]
                break
            table = True


        if posible_relatives:
            last_num = list(filter(lambda x: x.data_type=="numbers", list(self.main_line_num.descendants)))
            if last_num:
                last_num = last_num[-1]
                num_list = list(filter(lambda par: "number" in par[3], self.lst[self.k+1:]))
                prev = None
                for i in range(len(num_list)):
                    if self.numeral_check(last_num, num_list[i]) and not self.numeral_check(prev, num_list[i]):
                        if len(posible_relatives) > 1:
                            posible_relatives = list(filter(lambda x: x.parent.name != 'txt', posible_relatives))
                        break
                    prev = num_list[i]
            posible_relatives.sort(key = lambda rel: int(elem[0]) - int(rel.name))
            rel = posible_relatives[0]
            #! ------------------------------------------------------------------
            parent = rel.parent 
            #! ------------------------------------------------------------------
            n1, n2 = self.func(elem[0]), self.func(rel.node_name)
            for i in range(n2+1, n1):
                self.tree.append(Node(self.revfunc(i), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4], addinfo = elem[5]))
            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
            if elem[0] == '2':
                self.p.remove(elem[1])
            if self.content:
                self.content_set.add(elem[2])
            if parent.node_name == 'txt': self.main_line_num = self.tree[-1]
            self.ancestor = self.tree[-1]
            return 
        if self.func(elem[0]) - self.func(self.n) < 2:
            last_num = list(filter(lambda x: x.data_type=="numbers", list(self.main_line_num.descendants)))
            last_num = self.main_line_num if last_num == [] else last_num[-1]
            num_list = list(filter(lambda par: "number" in par[3], self.lst[self.k+1:]))
            prev = None
            for i in range(len(num_list)):
                if self.numeral_check(last_num, num_list[i]) < self.numeral_check(prev, num_list[i]) and num_list[i][3]:
                    parent = self.tree[-1]
                    if self.func(elem[0]) == 2:
                        self.tree.append(Node(self.n, sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
                    return
                prev = num_list[i]
            else:
                c = 0
                for obj in self.tree:            
                    if obj.status == "EXISTING":
                        c += 1
                if c > 1:
                    self.content = False
                    self.trees.append(tree_to_dict(self.root, all_attrs=True))
                    self.roots.append(self.root)
                self.root, self.tree, self.ancestor = Node("txt"), [], None
                parent, st = self.root, True
                if self.func(elem[0]) == 2:
                    self.tree.append(Node(self.n, sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
                return

        for i in range(-1, -len(self.tree)-1, -1):
            if self.similarity_check(self.tree[i], elem):
                if self.tree[i].node_name == elem[0]:
                    try:
                        self.tree.append(Node(" " + elem[0], sign=elem[1], pos=elem[2], parent=self.tree[i].parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                        if elem[0] == '2':
                            self.p.remove(elem[1])
                        if self.content:
                            self.content_set.add(elem[2])
                    except:
                        continue
                    return False
                break
        if duplic:
            self.tree.append(Node(" " + elem[0], sign=elem[1], pos=elem[2], parent=duplic.parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
            if elem[0] == '2':
                self.p.remove(elem[1])
        return False
                

    def numeral_paragraphs(self, elem):
        #! Алгоритм работы с параграфами где несколько цифр
        delimetr, parent, sp, black_list, forbiden_list, duplic = elem[4], None, list(), set(), list(), False
        posible_relatives = list()
        buf = list(map(int, elem[0].split('.')))
        if len(buf) == 2 and buf[0] in [1, 2] and buf[1] in [1, 2, 3] and (self.tree[-1].sign == 'таблица' or self.tree[-1].sign == 'приложение'):
            parent = self.tree[-1]
            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
            return
        for i in range(-1, -len(self.tree)-1, -1):
            if 'number' in self.tree[i].data_type and (elem[1] == self.tree[i].sign or self.tree[i].sign == 'NaN'):
                if self.tree[i].name == elem[0]: 
                    forbiden_list.append(self.tree[i].parent)
                    if not duplic and i > -20:
                        duplic = self.tree[i]
                if self.numeral_check(self.tree[i], elem) and all([ancestor not in black_list for ancestor in self.tree[i].ancestors]) and (self.tree[i] not in forbiden_list):
                    posible_relatives.append(self.tree[i])
                    black_list.add(self.tree[i].parent)
                else:
                    black_list.add(self.tree[i].parent)
        if posible_relatives:
            posible_relatives.sort(key = lambda rel: int(elem[0].split('.')[0]) - int(rel.name.split('.')[0]))
            node = posible_relatives[0]
            ## добавить определение parent-a тк он думает что отец 1.3.1 это 1.2.1
            parent, delimetr = node, node.delimetr
            rel = list(map(int, node.node_name.split('.')))
            sp = list(map(int, elem[0].split('.')))
            f = True
            adress = []
            k1 = k2 = True
            dif = len(sp) - len(rel)
            param = False
            if len(sp) > len(rel):
                if dif > 1 and rel.count('.') == 0: f = False
                for _ in range(dif):rel.append(0)
            for e in range(min(len(rel), len(sp))):
                if rel[e] == sp[e] and k1:
                    adress.append(sp[e])
                    continue
                elif k2:
                    if f:
                        for i in range(1, len(rel) - e):
                            if parent != self.root:
                                parent = parent.parent
                    k1 = k2 = False
                    if e==0:
                        buf_parent = parent
                        for j in range(rel[e]+1, sp[e]):
                            try:
                                self.tree.append(Node('{}.1'.format(j), sign='.', pos=elem[2], parent=buf_parent, data_type='numbers', status='MISSING', delimetr = delimetr, addinfo = elem[5]))  
                                param = True
                            except:
                                continue     
                        if not f: parent = self.tree[-1]
                    else:
                        buf_parent = parent
                        if node.data_type == 'number':
                            if parent.name != 'txt':
                                buf_parent = parent.parent
                        else:
                            if len(buf_parent.name.split('.')) == len(adress)+1:
                                buf_parent = parent.parent
                        for j in range(rel[e]+1, sp[e]):  
                            self.tree.append(Node('.'.join(list(map(str, adress+[j]))), sign='.', pos=elem[2], parent=buf_parent, data_type='numbers', status='MISSING', delimetr = delimetr, addinfo = elem[5]))
                            if not f: parent = self.tree[-1]
                            param = True
                        if len(sp) > e+1:
                            # buf_parent = parent.parent
                            self.tree.append(Node('.'.join(list(map(str, adress+[sp[e]]))), sign='.', pos=elem[2], parent=buf_parent, data_type='numbers', status='MISSING', delimetr = delimetr, addinfo = elem[5]))
                            if not f: parent = self.tree[-1]
                            param = True
                    adress.append(sp[e])
                else:
                    if param:
                        parent = self.tree[-1]
                    for j in range(1, sp[e]):  
                        self.tree.append(Node('.'.join(list(map(str, adress+[j]))), sign='.', pos=elem[2], parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr, addinfo = elem[5]))
                        if not f: parent = self.tree[-1]
                        param = True
                    adress.append(sp[e])
            
            if 'number' in self.tree[-1].data_type and (elem[1] == self.tree[-1].sign or self.tree[-1].sign=='NaN'): 
                if self.numeral_check(self.tree[-1], elem) and self.tree[-1] not in posible_relatives:
                    rel = self.tree[-1].node_name.split(".")
                    parent = self.tree[-1] if len(sp) != len(rel) else self.tree[-1].parent
                    if len(rel) > len(sp):
                        for i in range(len(rel) - len(sp)+1):
                            if parent != self.root:
                                parent = parent.parent

            if ((len(node.node_name) == 1 and parent == node) or (len(parent.node_name.split('.')) == len(elem[0].split('.')) and self.numeral_check(parent, elem))) and parent.node_name != 'txt':
                parent = parent.parent

            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
            if self.content:
                self.content_set.add(elem[2])
            if parent.node_name == 'txt': self.main_line_num = self.tree[-1]
            self.ancestor = self.tree[-1]  
            return
        else:
            if len(elem[0].split('.')) == 2:
                sp = list(map(int, elem[0].split('.')))
                if sp[0] > 2 or sp[1] > 3: 
                    if duplic:
                        self.tree.append(Node(" " + elem[0], sign=elem[1], pos=elem[2], parent=duplic.parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                    return
                st = 0
                if find(self.root, lambda node: node.path_name == "/txt/{}.{}".format(*sp)):
                    num_list = list(filter(lambda par: "number" in par[3], self.lst[self.k+1:]))
                    prev = None
                    for i in range(len(num_list)):
                        param = ok = False
                        if 'number' not in num_list[i][3] or elem[1] != num_list[i][1]: continue
                        if self.numeral_check(self.main_line_num.name, num_list[i][0]) and (prev is None or not self.numeral_check(prev, num_list[i])):
                            param = True
                            st += 1
                        if self.main_line_num:
                            flag = False
                            if self.main_line_num.sign == num_list[i][1]:
                                if self.numeral_check(self.main_line_num.name, num_list[i][0]):
                                    if prev is not None:
                                        if self.numeral_check(prev, num_list[i]) and prev[1] != num_list[i][1]:
                                            flag = True
                                    else:
                                        flag = True
                                    if flag:
                                        #! СЛАБОЕ МЕСТО-----------------------------------------------------------------------------
                                        if int(self.main_line_num.name.split('.')[0]) == 1 and int(elem[0]) == 2: parent=self.main_line_num.parent
                                        elif (st and not param) or st > 1: parent=self.tree[-1]
                                        else: parent=self.tree[-1]
                                        #! -----------------------------------------------------------------------------------------
                                        st=True
                                        break
                            
                        if elem[1] == num_list[i][1]:
                            prev = num_list[i]

                    else:   # Делаем новое дерево
                        c = 0
                        for obj in self.tree: 
                            if obj.status == "EXISTING":
                                c += 1
                        if c > 1:
                            self.content = False
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
                            self.tree.append(Node("{}.1".format(i), sign='.', pos=elem[2], parent=parent, data_type='numbers', status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                        except:
                            self.tree.append(Node(" " + "{}.1".format(i), sign=elem[1], pos=elem[2], parent=parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                    for i in range(1, sp[1]):
                        try:
                            self.tree.append(Node("{}.{}".format(sp[0], i), sign='.', pos=elem[2], parent=parent, data_type='numbers', status='MISSING', delimetr = elem[4], addinfo = elem[5]))
                        except:
                            self.tree.append(Node(" " + "{}.{}".format(sp[0], i), sign=elem[1], pos=elem[2], parent=parent, data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                    self.tree.append(Node(elem[0], sign='.', pos=elem[2], parent=parent, data_type='numbers', status='EXISTING', delimetr = elem[4], addinfo = elem[5]))
                    if self.content:
                        self.content_set.add(elem[2])
                    if parent.node_name == 'txt': self.main_line_num = self.tree[-1]
                    self.ancestor = self.tree[-1]
            else:
                if forbiden_list:
                    self.tree.append(Node(" {}".format(elem[0]), sign=elem[1], pos=elem[2], parent=forbiden_list[0], data_type='None', status='DUPLICATE', delimetr = None, addinfo = elem[5]))
                    if self.content:
                        self.content_set.add(elem[2])

    def walk(self, lst, txt_path, log_path='myapp.log'):
        logging.basicConfig(filename=log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s func:%(funcName)s %(message)s \nText path: {txt_path}\n')
        logger=logging.getLogger(__name__)
        self.lst = lst
        for elem, self.k in zip(self.lst, range(len(self.lst))):
            if elem[1] in ["таблица", "рисунок", "рис", "схема", "приложение"]:
                self.func, self.revfunc = functions[elem[3]]
                self.n = first_elements[elem[3]]
                try: self.non_text(elem)
                except Exception as err: logger.error(err)
                continue
            elif elem[3] == 'numbers':
                try: self.numeral_paragraphs(elem)  
                except Exception as err: logger.error(err)
            else:
                self.func, self.revfunc = functions[elem[3]]
                self.n = first_elements[elem[3]]

                if 'letter' in elem[3] or 'roman' in elem[3]:
                    try: self.letters_romans(elem)
                    except Exception as err: logger.error(err)
                elif elem[3] == 'number':
                    try: self.single_numbers(elem)
                    except Exception as err: logger.error(err)
                    
        self.trees.append(tree_to_dict(self.root, all_attrs=True))
        self.roots.append(self.root)
        if len(self.content_set) > 150: self.content_set = None
        return self.trees

    def show(self):
        for root in self.roots:
            root.show(attr_list=["pos", "status"])