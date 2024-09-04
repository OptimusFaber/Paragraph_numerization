import re
import logging

#! Алгоритм Левинштейна
def levenstein(str_1, str_2):
    n, m = len(str_1), len(str_2)
    if n > m:
        str_1, str_2 = str_2, str_1
        n, m = m, n

    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if str_1[j - 1] != str_2[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]
#!--------------------------------------------------------------------------------------------------------------------

def compare(s1, s2):
    n = len(s1)
    if n>=5:
        for i in range(1, min(n, 3)):
            if levenstein(s1[:-i], s2) <= 1:
                return True
    if levenstein(s1, s2) <= 1:
        return True
    else:
        return False
    
def letter_extractor(string, ind):
    line = []
    for st in string:
        if len(st) > 1 or st == 'и':
            for s in range(len(st)-1, -1, -1):
                if st[s].isupper() or s == ind:
                    line.append(st[s].upper())
    return line

def pos_compare(pos1, pos2):
    """
    Finding out if pos1 > pos2
    """
    pos1 = re.search("[A-Z]+[0-9]+", pos1).group()
    num1= alph1 = ''
    for e in pos1:
        if e.isalpha():
            alph1 += e
        else:
            num1 += e
    num1 = int(num1)

    pos2 = re.search("[A-Z]+[0-9]+", pos2).group()
    num2= alph2 = ''
    for e in pos2:
        if e.isalpha():
            alph2 += e
        else:
            num2 += e
    num2 = int(num2)

    if num1 > num2: return True
    if num1 == num2 and alph1 >= alph2: return True
    else: return False


def abb_finder(json_text, abbs=True, dicts=(True, True, True), add_info=None, content_strings = None, excel_path=None, log_path='myapp.log', new_format=0):
    logging.basicConfig(filename=log_path, level=logging.DEBUG, 
        format=f'%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s func: %(funcName)s %(message)s \nText path: {excel_path}\n')
    logger=logging.getLogger(__name__)
    if not abbs and not all(dicts):
        return []
    #& Маски для поиска нужных нам сокращений
    abb_mask1 = re.compile(r"(?<![a-zA-Zа-яА-Я0-9-—–])((«?([А-Я]+и)»?\s?){2,}|(«?([А-Я]{2,})»?\s?)+|(«?[A-Z]{2,}»?\s?)+)([^А-Яа-яA-Za-z0-9-—–]|$)")
    abb_mask2 = re.compile(r"(?<![a-zA-Zа-яА-Я0-9-—–])(?<!-)(((([А-Я]+[а-я]*){2,})\s?)+|((([A-Z]+[a-z]*){2,})\s?)+)([^А-Яа-яA-Za-z0-9-—–]|$)")
    #&--------------------------------------------------------------------------------------------------------------------
    feedback_list = []
    flag = 1
    for sheet in json_text['Worksheets']:
        devided_text = {}
        con_begin = con_end = c = 0
        flag = 1
        pos, con = [], []
        for st in sheet['Rows']:
            for i in range(len(st['Cells'])):
                x = re.search("[A-Z]+[0-9]+", st['Cells'][i]['Address']).group()
                num = alph = ''
                for e in x:
                    if e.isalpha():
                        alph += e
                    else:
                        num += e

                num = int(num)
                key = (num, alph)
                devided_text[st['Cells'][i]['Address']] = [st['Cells'][i]['Text'], key]
                
                match = re.search(re.compile(r"(С|с)окращени(я|й)|(Т|т)ермин(ы|ов)", flags=re.IGNORECASE), st['Cells'][i]['Text'])
                if match is not None:
                    pos.append(st['Cells'][i]['Address'])
                if flag:
                    context = re.search(re.compile(r"\s*(([С|с]одержание)|([О|о]главление))", flags=re.IGNORECASE), st['Cells'][i]['Text'])
                    if context is not None and not con:
                        con.append(st['Cells'][i]['Address'])
                        con_begin = num
                    if con and not con_end:
                        if c == 5:
                            con_end = num
                            flag=0
                        list_findings = [re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|((([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.]))", re.ASCII), st['Cells'][i]['Text']) != None,
                                        re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), st['Cells'][i]['Text']) != None,
                                        re.search(re.compile(r"((?<=\s)|(?<=^))[(]((\d+[.]?)+|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), st['Cells'][i]['Text']) != None]
                        if any(list_findings):
                            c = 0
                            continue
                        else:
                            c += 1
                        con.append(st['Cells'][i]['Address'])
        #^--------------------------------------------------------------------------------------------------------------------
            
        #& Объявление наши справочников и словарей
        abb_set = dict()
        special_words = {"далее", "условное обозначение", "условные обозначения", 
                        "сокращенное наименование", "сокращенные наименования"}
        corruption_factor_set = set()
        no_connection_with_npa_set = set()
        incorrect_formulation_set = set()
        #&--------------------------------------------------------------------------------------------------------------------
        #^ Если у нас идет слово Сокр
        devided_text = dict(sorted(devided_text.items(), key = lambda x: x[1][1]))
        flag = False
        if pos:
            for idx in pos:
                c, st = 0, 0
                buf1, buf2 = '', ''
                for elem in list(devided_text.keys())[list(devided_text.keys()).index(idx):]:
                    # if devided_text[elem] == '':
                    #     continue
                    if devided_text[elem][1][1] not in 'ABC':
                        continue
                    if c == 5:
                        flag = False
                        break
                    f1 = re.search(abb_mask1, devided_text[elem][0])
                    f2 = re.search(abb_mask2, devided_text[elem][0])
                    if f1 and f2:
                        f = f1 if (len(f1.group()) > len(f2.group()) and f1.span()[0] < 7) else f2 if f2.span()[0] < 7 else None
                    elif f1 or f2:
                        f = f1 if f1 else f2
                        f = f if f.span()[0] < 7 else None
                    else:
                        f = None
                    if f is None:
                        c+=1
                        continue
                    f = f.group()
                    f = re.sub("[\t\n\r]", " ", f)
                    f = re.sub("[ ]{2,}", " ", f)
                    for _ in range(2):
                        if not f[-1].isalpha() and f[-1] != "»":
                            f = f[:-1]
                        if not f[0].isalpha() and f[0] != "«":
                            f = f[1:]
                    if f[-1] == "»" and f.count("«") == 0:
                        f = f[:-1]
                    if not f[-1].isalpha() and f[-1] != "»": 
                        f=f[:-1]
                    if f[0] == "«" and f.count("»") == 0:
                        f = f[1:]
                    if not f[0].isalpha() and f[0] != "«":
                        f = f[1:]
                    
                    if f.count("«") == 1 and f.count("»") == 0:
                        f += "»"
                    if f.count("«") == 0 and f.count("»") == 1:
                        f = "«" + f
                    
                    if not abb_set.get(f):
                        abb_set[f] = elem
                    c = 0
                    
                         
        #^--------------------------------------------------------------------------------------------------------------------
                    
        #* Дополняем словари если нужно
        if add_info:
            if not new_format:
                if "Corruption" in add_info.keys():
                    for elem in add_info["Corruption"]:
                        corruption_factor_set.add(elem["Value"])
                if "Abbreviation" in add_info.keys():
                    for elem in add_info["Abbreviation"]:
                        abb_set[elem["Value"]] = f"'{sheet['Name']}'!A0"
                if "No_NPA" in add_info.keys():
                    for elem in add_info["No_NPA"]:
                        no_connection_with_npa_set.add(elem["Value"])
                if "SpecWords" in add_info.keys():                      ## Дополнение к Abbreviation
                    for elem in add_info["SpecWords"]:
                        special_words.add(elem["Value"])
                if "IncorrectForm" in add_info.keys():
                    for elem in add_info["IncorrectForm"]:
                        incorrect_formulation_set.add(elem["Value"])
            else:
                if "Corruption" in add_info.keys():
                    for elem in add_info["Corruption"]:
                        corruption_factor_set.add(elem)
                if "Abbreviation" in add_info.keys():
                    for elem in add_info["Abbreviation"]:
                        abb_set[elem] = 0
                if "No_NPA" in add_info.keys():
                    for elem in add_info["No_NPA"]:
                        no_connection_with_npa_set.add(elem)
                if "SpecWords" in add_info.keys():                      ## Дополнение к Abbreviation
                    for elem in add_info["SpecWords"]:
                        special_words.add(elem)
                if "IncorrectForm" in add_info.keys():
                    for elem in add_info["IncorrectForm"]:
                        incorrect_formulation_set.add(elem)
        #*-----------------------------
        if 5 < con_end - con_begin < 150:
            forbidden_list = list(abb_set.values()) + list(range(con_begin, con_end+1))
        else:
            forbidden_list = list(abb_set.values())

        #^ Поиск сокращений в нашем тексте
        for i in list(devided_text.keys()):
            try:
                buf = []
                devided_text[i][0] = devided_text[i][0].replace(u'\xa0', u' ')
                devided_text[i][0] = re.sub(r'[\u2013\u2014]', '-', devided_text[i][0])
                devided_text[i][0] = re.sub(r'\u00A0', ' ', devided_text[i][0])
                if i not in forbidden_list:
                    f = [re.finditer(abb_mask1, devided_text[i][0]), re.finditer(abb_mask2, devided_text[i][0])]
                    #^------------------------------------------------------------------------------------
                    list_of_added_elems = []
                    for itter in f:       
                        for element in itter:
                            if element:
                                elem = element.group()
                                elem = re.sub("[(\t\n\r)]", " ", elem)
                                elem = re.sub("[ ]{2,}", " ", elem)
                                if elem[-1].isdigit():
                                    continue
                                for _ in range(2):
                                    if not elem[-1].isalpha() and elem[-1] != "»":
                                        elem = elem[:-1]
                                    if not elem[0].isalpha() and elem[0] != "«":
                                        elem = elem[1:]
                                if elem[0] == "«" and elem[-1] == "»":
                                    elem = elem[1:len(elem)-1]
                                if elem[-1] == "»" and elem.count("«") == 0:
                                    elem = elem[:-1]
                                if elem[0] == "«" and elem.count("»") == 0:
                                    elem = elem[1:]
                                if not elem[0].isalpha() and f[0] != "«":
                                    elem = elem[1:]
                                if elem.count("«") == 1 and elem.count("»") == 0:
                                    elem += "»"
                                if elem.count("«") == 0 and elem.count("»") == 1:
                                    elem = "«" + elem
                                #! Проверяем что это не римская цифра
                                if bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", elem)) and elem != "CD":
                                    continue
                                #! ----------------------------------
                                st = False 
                                ##----------------------------
                                if elem in buf:
                                    continue
                                ##----------------------------
                                #! Проверяем нет ли нашего элемента в словаре
                                if elem in list(abb_set.keys()):
                                    if pos_compare(i, abb_set[elem]):
                                        list_of_added_elems.extend(range(element.span()[0], element.span()[1]+1))
                                        continue
                                #! -------------------------------------------
                                elif all(list(map(lambda x: 1<len(x)<11, elem.split(" ")))):
                                    #?Убираем параграф если он весь написан большими буквами
                                    if devided_text[i][0].isupper():
                                        continue
                                    
                                    st = False
                                    exp = elem.split(" ")
                                    for j in range(len(exp)):
                                        if len(exp[j])>=9 and not any(k.islower() for k in exp[i]):
                                            st = True
                                            break
                                        # if exp[i].lower() in text:
                                        #     st = True
                                        #     break
                                    if st: continue
                                        
                                    if element.span()[0] in list_of_added_elems or element.span()[1] in list_of_added_elems:
                                        continue
                                    f1 = re.search(r"^[\t ]*[-—–]", devided_text[i][0][element.span()[1]:])         #* Ситуация типа ООО - ...
                                    f2 = re.search(r"^[\t ]*[-—–]", devided_text[i][0][:element.span()[0]][::-1])   #* Ситуацтя типа ... - ООО

                                    if f1:
                                        right_side = devided_text[i][0][element.span()[1]:][f1.span()[0]:].replace(')', '').replace('(', '').split(" ")
                                        right_side = letter_extractor(right_side, 0)
                                        # right_side = list(map(lambda x: x[0], list(filter(lambda x: len(x)>1, right_side))))
                                        line = ""
                                        st = False
                                        elemx = elem.upper().replace(' ')
                                        for rig in right_side:
                                            line += rig
                                            if levenstein(line, elemx) <= 1:
                                                st = True
                                                break
                                            if len(line) - len(elemx) > 4:
                                                break
                                        if st:
                                            abb_set[elem] = i+1
                                            continue
                                    if f2:
                                        left_side = devided_text[i][0][element.span()[0]-1::-1][f2.span()[0]:].replace(')', '').replace('(', '').split(" ")
                                        left_side = list(map(lambda x: x[::-1], left_side))
                                        left_side = letter_extractor(left_side, 0)
                                        # left_side = list(map(lambda x: x[0], list(filter(lambda x: len(x)>1, left_side))))
                                        # left_side.reverse()
                                        line = ""
                                        st = False
                                        elem = elem.upper().replace(' ')
                                        for lef in left_side:
                                            line = lef + line
                                            if levenstein(line, elemx) <= 1:
                                                st = True
                                                break
                                            if len(line) - len(elemx) > 4:
                                                break
                                        if st:
                                            abb_set[elem] = i+1
                                            continue

                                    if ")" in devided_text[i][0][element.span()[1]:min(element.span()[1]+10, len(devided_text[i][0]))] or "(" in devided_text[i][0][max(element.span()[0]-10, 0):element.span()[0]]:
                                        ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                        left_side_ind = len(devided_text[i][0][element.span()[1]-2::-1]) - re.search("[(]", devided_text[i][0][element.span()[1]-2::-1]).span()[0]
                                        bracket_info = devided_text[i][0][left_side_ind:element.span()[1]-1]
                                        ## Смотрим есть ли перед аббревиатурой спец слово
                                        for word in special_words:
                                            if word in bracket_info:
                                                st = True
                                                break
                                        if st:
                                            if not abb_set.get(elem):
                                                abb_set[elem] = i+1
                                            else:
                                                if i+1 < abb_set[elem]:
                                                    abb_set[elem] = i+1
                                            continue
                                        ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                        if re.search(f"[(]\t**{elem}\t*[)]", devided_text[i][0]):
                                            if not abb_set.get(elem):
                                                abb_set[elem] = i+1
                                            else:
                                                if i+1 < abb_set[elem]:
                                                    abb_set[elem] = i+1
                                            continue
                                        else:
                                            print(devided_text[i][0])
                                    flag = False
                                    if len(elem.split(" ")) > 1:
                                        elem1 = elem.split(' ')
                                        elem = []
                                        a = ''
                                        for e in range(len(elem1)):
                                            a += elem1[e] + ' '
                                            if a[:-1] in list(abb_set.keys()):
                                                if abb_set[a[:-1]] <= i+1:
                                                    flag = True
                                                else:
                                                    elem.append(elem1[e])
                                            elif elem1[e] in list(abb_set.keys()):
                                                if abb_set[elem1[e]] <= i+1:
                                                    a = elem1[e] + ' '
                                                    flag = True
                                                    elem = []
                                                else:
                                                    elem.append(elem1[e])
                                            else:
                                                elem.append(elem1[e])
                                        if elem:
                                            elem = ' '.join(elem)
                                    if not flag or elem:
                                        buf.append((elem, element.span()))
                                        st = True
                                    else:
                                        for e in elem:
                                            buf.append((elem, element.span()))
                                            st = True

                    #^------------------------------------------------------------------------------------

                #? Поиск элементов из наших 3 словарей
                if dicts:
                    if dicts[0]:
                        corr_fac = list(filter(lambda x: x[0] , zip([re.search("\W"+word+"\W", devided_text[i][0].lower()) for word in corruption_factor_set], corruption_factor_set)))
                        for cor in corr_fac:
                            sentence = "Фраза «{}»".format(cor[1])
                            feedback_list.append(["Corruption", sentence, i, cor[1]])
                    if dicts[1]:
                        no_conn  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", devided_text[i][0].lower()) for word in no_connection_with_npa_set], no_connection_with_npa_set)))
                        for no in no_conn:
                            sentence = "Фраза «{}»".format(no[1])
                            feedback_list.append(["NoNPA", sentence, i, no[1]])
                    if dicts[2]:
                        inc_frm  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", devided_text[i][0].lower()) for word in incorrect_formulation_set], incorrect_formulation_set)))
                        for inc in inc_frm:
                            sentence = "Фраза «{}»".format(inc[1])
                            feedback_list.append(["IncorrectForm", sentence, i, inc[1]]) 
                #?------------------------------------------------------------------------------------
                if abbs and buf:
                    buf = list(filter(lambda x: (x[1][0] not in list_of_added_elems) and (x[1][1] not in list_of_added_elems), buf))
                    res = set()
                    for b in buf:
                        buf_f = list(filter(lambda x: x[1][0]==b[1][0], buf))
                        buf_f = sorted(buf_f, key=lambda x: len(x[0]), reverse=True)
                        buf_y = list(filter(lambda x: x[1][1]==b[1][1], buf))
                        buf_y = sorted(buf_y, key=lambda x: len(x[0]), reverse=True)
                        res.add(max(buf_y[0][0], buf_f[0][0], key=lambda x: len(x)))
                    #! ErrorType, LineText, LineNumber, ОШИБКА, PrevLineText, NextLine
                    for r in res:
                        sentence = "Неизвестная аббревиатура «{}»".format(r)
                        feedback_list.append(["Abbreviation", sentence, i, r])
            except Exception as err:
                logger.error(err)
        #^--------------------------------------------------------------------------------------------------------------------           
    return feedback_list