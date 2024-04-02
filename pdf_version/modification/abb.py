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

def abb_finder(text, abbs=True, dicts=True, add_info=None, content_strings = None, json_path=None, log_path='myapp.log'):
    logging.basicConfig(filename=log_path, level=logging.DEBUG, 
        format=f'%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s func: %(funcName)s %(message)s \nText path: {json_path}\n')
    logger=logging.getLogger(__name__)
    if not abbs and not dicts:
        return []
    #& Маски для поиска нужных нам сокращений
    abb_mask1 = re.compile(r"(?<!-)((«?([А-Я]+и)»?\s?){2,}|(«?([А-Я]{2,})»?\s?)+|(«?[A-Z]{2,}»?\s?)+)([^А-Яа-яA-Za-z0-9-—–]|$)")
    abb_mask2 = re.compile(r"(?<!-)(((([А-Я]+[а-я]*){2,})\s?)+|((([A-Z]+[a-z]*){2,})\s?)+)([^А-Яа-яA-Za-z0-9-—–]|$)")
    #&--------------------------------------------------------------------------------------------------------------------

    pos = []
    js = []
    con = 0
    con_end = 0
    c = 0
    flag = 1
    for elem in text.keys():
        if elem == 'Paragraphs':
            js.append(text[elem])
            for e in text[elem]:
                match = re.finditer("[С|с]окращени[я|й]", e['Text'])
                for m in match:
                    pos.append([e['Index'], m.span()[0], m.span()[1]])
                if flag:
                    context = re.search("\s*(([С|с]одержание)|([О|о]главление))", e['Text'])
                    if context is not None and not con:
                        con = [e['Index'], len(e['Text'][:context.span()[0]].split('\n'))]
                    if con and not con_end:
                        if con[0] == e['Index']:
                            ind = len(e['Text'][:con[1]])
                            texti = e['Text'].split('\n')[con[1]+1:]
                        else:
                            ind = 0
                            texti = e['Text'].split('\n')
                        for elem in texti:
                            if c == 5:
                                con_end = [e["Index"], ind]
                                flag = False
                                break
                            list_findings = [re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|((([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.]))", re.ASCII), elem) != None,
                                            re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), elem) != None,
                                            re.search(re.compile(r"((?<=\s)|(?<=^))[(]((\d+[.]?)+|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), elem) != None,
                                            re.search("^\s*[1-9][0-9]*$", elem) != None]
                            if any(list_findings):
                                c = 0
                                continue
                            else:
                                c += 1
                            ind+=1

    #& Объявление наши справочников и словарей
    abb_set = dict()
    special_words = {"далее", "условное обозначение", "условные обозначения", 
                    "сокращенное наименование", "сокращенные наименования"}
    corruption_factor_set = set()
    no_connection_with_npa_set = set()
    incorrect_formulation_set = set()
    costil = []
    #&--------------------------------------------------------------------------------------------------------------------
    spec_param = False
    flag = True
    #^ Если у нас идет слово Сокр
    for p in pos:
        ix = 0
        flag = True
        while flag:
            if not spec_param:
                block = text['Paragraphs'][p[0]]["Text"][p[1]:].split("\n")[1:]
                b, idx = p[1], p[2]
                paragraph = p[0]
                c, st = 0, 0
                buf1, buf2 = '', ''
                spec = 0
            else:
                ix+=1
                block = text['Paragraphs'][p[0]+ix]["Text"].split("\n")
                b, idx = 0, 0
                paragraph = p[0]+ix
                c, st = 0, 0
                buf1, buf2 = '', ''
                spec = 1
            for i in block:
                spec_param = True
                if i == '':
                    continue
                if c == 7:
                    spec_param = False
                    flag = False
                    break
                f1 = re.search(abb_mask1, i)
                f2 = re.search(abb_mask2, i)
                if f1 and f2:
                    f = f1 if (len(f1.group()) > len(f2.group()) and f1.span()[0] < 15) else f2 if f2.span()[0] < 15 else None
                elif f1 or f2:
                    f = f1 if f1 else f2
                    f = f if f.span()[0] < 15 else None
                else:
                    f = None
                if f:
                    if f.span()[0] < 7:
                        #?-----------------------------------
                        if buf1 != "" and buf2 == "":
                            buf1 += f.group()
                            buf2 = i.replace(f.group(), "")
                        else:
                            if buf1:
                                buf1 = re.sub("[\t\n\r]", " ", buf1)
                                buf1 = re.sub("[ ]{2,}", " ", buf1)
                                for _ in range(2):
                                    if not buf1[-1].isalpha():
                                        if buf1[-1] != "»":
                                            buf1 = buf1[:-1]
                                if buf1[-1] == "»" and buf1.count("«") == 0:
                                    buf1 = buf1[:-1]
                                elif buf1[0] == "«" and buf1.count("»") == 0:
                                    buf1 = buf1[1:]
                                if not buf1[-1].isalpha() and buf1[-1] != "»": buf1=buf1[:-1]
                                if not abb_set.get(buf1):
                                    # abb_set[buf1] = (paragraph, st)
                                    strn = text['Paragraphs'][p[0]+ix]["Text"][:st].count('\n')+spec
                                    abb_set[buf1] = (paragraph, strn)
                                    # costil.append([paragraph, strn])
                            c = 0
                            st = idx
                            buf1 = f.group()
                            buf2 = i.replace(buf1, "")
                        #?-----------------------------------
                        
                else:
                    if buf1 != '':
                        buf2 += i
                    c += 1
                idx+=len(i)+1
            if buf1:
                if not buf1[-1].isalpha() and buf1[-1] != "»": buf1=buf1[:-1]
                buf1 = re.sub("[\t\n\r]", "", buf1)
                if not abb_set.get(buf1):
                    abb_set[buf1] = (paragraph, st)
                buf1, buf2 = '', ''    
    #^--------------------------------------------------------------------------------------------------------------------
                
    #* Дополняем словари если нужно
    if add_info:
        if "Corruption" in add_info.keys():
            for elem in add_info["Corruption"]:
                corruption_factor_set.add(elem["Value"])
        if "Abbreviation" in add_info.keys():
            for elem in add_info["Abbreviation"]:
                abb_set[elem["Value"]] = (0, 0)
        if "No_NPA" in add_info.keys():
            for elem in add_info["No_NPA"]:
                no_connection_with_npa_set.add(elem["Value"])
        if "SpecWords" in add_info.keys():                      ## Дополнение к Abbreviation
            for elem in add_info["SpecWords"]:
                special_words.add(elem["Value"])
        if "IncorrectForm" in add_info.keys():
            for elem in add_info["IncorrectForm"]:
                incorrect_formulation_set.add(elem["Value"])
    #*-----------------------------
    buffer = []
    if con[0] == con_end[0]:
        buffer.extend([(con[0], i) for i in range(con[1], con_end[1])])
    else:
        while con[0] != con_end[0]:
            buffer.extend([(con[0], i) for i in range(con[1], len(text['Paragraphs'][con[0]]["Text"].split('\n')))])
            con[0]+=1
            con[1]=0
        buffer.extend([(con[0], i) for i in range(con[1], con_end[1])])


    forbidden_list = list(abb_set.values()) + buffer
    #^ Поиск сокращений в нашем тексте
    feedback_list = []
    js = js[0]
    for i in range(len(js)):
        strings = js[i]['Text'].split('\n')
        counter = 0
        element_n = 0
        for j in range(len(strings)):
            try:
                buf = []
                if (i, j) not in forbidden_list:
                    f = [re.finditer(abb_mask1, strings[j]), re.finditer(abb_mask2, strings[j])]
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
                                    if not elem[-1].isalpha():
                                        if elem[-1] != "»":
                                            elem = elem[:-1]
                                if elem[0] == "«" and elem[-1] == "»":
                                    elem = elem[1:len(elem)-1]
                                if elem[-1] == "»" and elem.count("«") == 0:
                                    elem = elem[:-1]
                                elif elem[0] == "«" and elem.count("»") == 0:
                                    elem = elem[1:]
                                #! Проверяем что это не римская цифра
                                if bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", elem)):
                                    continue
                                #! ----------------------------------
                                st = False 
                                ##----------------------------
                                if elem in buf:
                                    continue
                                ##----------------------------
                                #! Проверяем нет ли нашего элемента в словаре
                                if elem in list(abb_set.keys()):
                                    if abb_set[elem][0] < i or (abb_set[elem][0] == i and abb_set[elem][1] < j):
                                        pos = re.search(elem, strings[j]).span()
                                        list_of_added_elems.extend(range(pos[0], pos[1]))
                                        list_of_added_elems.extend(range(element.span()[0], element.span()[1]+1))
                                        continue
                                    else:
                                        buf.append((elem, element.span()))
                                        st = True
                                #! -------------------------------------------
                                elif all(list(map(lambda x: 1<len(x)<9, elem.split(" ")))):
                                    if element.span()[0] in list_of_added_elems or element.span()[1] in list_of_added_elems:
                                        continue
                                    if strings[j][element.span()[1]-1] == ")":
                                        ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                        txt = strings[j-1] + " " + strings[j] + " " + strings[j+1]
                                        left_side_ind = len(txt[re.search(elem, txt).span()[1]-2::-1]) - re.search("[(]", txt[re.search(elem, txt).span()[1]-2::-1]).span()[0]
                                        bracket_info = txt[left_side_ind:re.search(elem, txt).span()[1]].split(' ')
                                        bracket_info = list((filter(lambda x: len(x)>1 and all(xs.isalpha() for xs in x), bracket_info)))
                                        ## Смотрим есть ли перед аббревиатурой спец слово
                                        for word in bracket_info:
                                            if word in special_words:
                                                ## Если оно есть, то проверяем расшифровк
                                                st = True
                                                break
                                        if st:
                                            if not abb_set.get(elem):
                                                abb_set[elem] = (i, j)
                                            else:
                                                if j < abb_set[elem][0] or (j == abb_set[elem][0] and i < abb_set[elem][1]):
                                                    abb_set[elem] = (i, j)
                                            continue
                                        ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                        left_side = txt[:re.search(elem, txt).span()[0]][::-1].split(" ")
                                        left_side = list(map(lambda x: x[-1], list(filter(lambda x: len(x)>1, left_side))))
                                        line = ""
                                        st = False
                                        elem = elem.upper()
                                        for lef in left_side:
                                            line = lef.upper() + line
                                            if levenstein(line, elem) <= 1:
                                                st = True
                                                break
                                            if len(line) - len(elem) > 4:
                                                break
                                        if st:
                                            if not abb_set.get(elem):
                                                abb_set[elem] = (i, j)
                                            else:
                                                if j < abb_set[elem][0] or (j == abb_set[elem][0] and i < abb_set[elem][1]):
                                                    abb_set[elem] = (i, j)
                                            continue
                                        ## тут лишь справа (ЕСКД) Единая система конструкторской документации
                                        right_side = txt[re.search(elem, txt).span()[1]+1:].split(" ")
                                        right_side = list(map(lambda x: x[0], list(filter(lambda x: len(x)>1, right_side))))
                                        line = ""
                                        st = False
                                        elem = elem.upper()
                                        for rig in right_side:
                                            line += rig.upper()
                                            if levenstein(line, elem) <= 1:
                                                st = True
                                                break
                                            if len(line) - len(elem) > 4:
                                                break
                                        if st:
                                            if not abb_set.get(elem):
                                                abb_set[elem] = (i, j)
                                            else:
                                                if j < abb_set[elem][0] or (j == abb_set[elem][0] and i < abb_set[elem][1]):
                                                    abb_set[elem] = (i, j)
                                            continue
                                    flag = False
                                    if len(elem.split(" ")) > 1:
                                        elem1 = elem.split(' ')
                                        elem = []
                                        a = ''
                                        for e in range(len(elem1)):
                                            a += elem1[e] + ' '
                                            if a[:-1] in list(abb_set.keys()):
                                                flag = True
                                            elif elem1[e] in list(abb_set.keys()):
                                                a = elem1[e] + ' '
                                                flag = True
                                            else:
                                                elem.append(elem1[e])
                                        if elem:
                                            elem = ' '.join(elem)
                                    if not flag:
                                        buf.append((elem, element.span()))
                                        st = True
                                    else:
                                        for e in elem:
                                            buf.append((elem, element.span()))
                                            st = True

                    #^------------------------------------------------------------------------------------

                #? Поиск элементов из наших 3 словарей
                if dicts:
                    corr_fac = list(filter(lambda x: x[0] , zip([re.search("\W"+word+"\W", strings[j].lower()) for word in corruption_factor_set], corruption_factor_set)))
                    no_conn  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", strings[j].lower()) for word in no_connection_with_npa_set], no_connection_with_npa_set)))
                    inc_frm  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", strings[j].lower()) for word in incorrect_formulation_set], incorrect_formulation_set)))

                    for cor in corr_fac:
                        sentence = "Фраза «{}»".format(cor[1])
                        feedback_list.append(["Corruption", sentence, j, cor[1], counter+cor[0].span()[0]])
                    for no in no_conn:
                        sentence = "Фраза «{}»".format(no[1])
                        feedback_list.append(["NoNPA", sentence, j, no[1], counter+no[0].span()[0]])
                    for inc in inc_frm:
                        sentence = "Фраза «{}»".format(inc[1])
                        feedback_list.append(["IncorrectForm", sentence, j, inc[1], counter+inc[0].span()[0]])  
                #?------------------------------------------------------------------------------------
                if abbs and buf:
                    buf = list(filter(lambda x: (x[1][0] not in list_of_added_elems) and (x[1][1] not in list_of_added_elems), buf))
                    res = set()
                    for b in buf:
                        buf_f = list(filter(lambda x: x[1][0]==b[1][0], buf))
                        buf_f = sorted(buf_f, key=lambda x: len(x[0]), reverse=True)
                        buf_y = list(filter(lambda x: x[1][1]==b[1][1], buf))
                        buf_y = sorted(buf_y, key=lambda x: len(x[0]), reverse=True)
                        res.add(max(buf_y[0], buf_f[0], key=lambda x: len(x[0])))
                    #! ErrorType, LineText, LineNumber, ОШИБКА, PrevLineText, NextLine
                    for r in res:
                        sentence = "Неизвестная аббревиатура «{}»".format(r[0])
                        feedback_list.append(["Abbreviation", sentence, i, r[0], counter+r[1][0]])
            except Exception as err:
                logger.error(err)

            counter += len(strings[j])+1
    #^--------------------------------------------------------------------------------------------------------------------           
    return feedback_list