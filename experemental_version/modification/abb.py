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
    tables = []
    con = 0
    con_end = 0
    c = 0
    flag = 1
    for elem in text.keys():
        if elem == 'Paragraphs':
            js.append(text[elem])
            for e in text[elem]:
                match = re.search("([С|с]окр)|([Т|т]ермин)", e['Text'])
                if match is not None:
                    pos.append(e['Index'])
                if flag:
                    context = re.search("\s*(([С|с]одержание)|([О|о]главление))", e['Text'])
                    if context is not None and not con:
                        con = e['Index']
                    if con and not con_end:
                        if c == 5:
                            con_end = e['Index']-2
                            flag=0
                        list_findings = [re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|((([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.]))", re.ASCII), e['Text']) != None,
                                        re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), e['Text']) != None,
                                        re.search(re.compile(r"((?<=\s)|(?<=^))[(]((\d+[.]?)+|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), e['Text']) != None]
                        if any(list_findings):
                            c = 0
                            continue
                        else:
                            c += 1

        elif elem == 'Tables':
            for table in text[elem]:
                buf = []
                for cell in table['Rows']:
                    buf.append(cell['Cells'][0]["Paragraphs"][0])
                js.append(buf)
                num = table['Index']
                for p in pos:
                    if 0 < num - p < 5:
                        tables.append(table)

    #& Объявление наши справочников и словарей
    abb_set = dict()
    special_words = {"далее", "условное обозначение", "условные обозначения", 
                    "сокращенное наименование", "сокращенные наименования"}
    corruption_factor_set = set()
    no_connection_with_npa_set = set()
    incorrect_formulation_set = set()
    #&--------------------------------------------------------------------------------------------------------------------

    #^ Если у нас идет слово Сокр
    for tab in tables:
        for row in tab['Rows']:
            for cell in row['Cells']:
                f1 = re.search(abb_mask1, cell['Paragraphs'][0]['Text'])
                f2 = re.search(abb_mask2, cell['Paragraphs'][0]['Text'])
                if f1 and f2:
                    f = f1 if (len(f1.group()) > len(f2.group()) and f1.span()[0] < 7) else f2 if f2.span()[0] < 7 else None
                elif f1 or f2:
                    f = f1 if f1 else f2
                    f = f if f.span()[0] < 7 else None
                else:
                    f = None
                if f:
                    if not abb_set.get(f.group()):
                        abb_set[f.group()] = cell['Paragraphs'][0]['Index']
                break         
    #^--------------------------------------------------------------------------------------------------------------------
                
    #* Дополняем словари если нужно
    if add_info:
        if "Corruption" in add_info.keys():
            for elem in add_info["Corruption"]:
                corruption_factor_set.add(elem["Value"])
        if "Abbreviation" in add_info.keys():
            for elem in add_info["Abbreviation"]:
                abb_set[elem["Value"]] = 0
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


    forbidden_list = list(abb_set.values()) + list(range(con, con_end))
    #^ Поиск сокращений в нашем тексте
    feedback_list = []
    for part in js:
        for string in part:
            try:
                buf = []
                if string['Index'] not in forbidden_list:
                    f = [re.finditer(abb_mask1, string['Text']), re.finditer(abb_mask2, string['Text'])]
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
                                    if abb_set[elem] <= string['Index']:
                                        pos = re.search(elem, string['Text']).span()
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
                                    if string['Text'][element.span()[1]-1] == ")":
                                        ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                        left_side_ind = len(string['Text'][element.span()[1]-2::-1]) - re.search("[(]", string['Text'][element.span()[1]-2::-1]).span()[0]
                                        bracket_info = string['Text'][left_side_ind:element.span()[1]-1].split(' ')
                                        bracket_info = list((filter(lambda x: len(x)>1 and all(xs.isalpha() for xs in x), bracket_info)))
                                        ## Смотрим есть ли перед аббревиатурой спец слово
                                        for word in bracket_info:
                                            if word in special_words:
                                                ## Если оно есть, то проверяем расшифровку
                                                left_side = string['Text'][left_side_ind-1::-1]
                                                left_side = list(map(lambda x: x[-1], list(filter(lambda x: len(x)>1, left_side))))
                                                ## Типа провекрка, left_side содержит первые юуквы слов, стоящих перед скобками
                                                st = True
                                                break
                                        if st:
                                            if not abb_set.get(elem):
                                                abb_set[elem] = string['Index']
                                            else:
                                                if string['Index'] < abb_set[elem]:
                                                    abb_set[elem] = string['Index']
                                            continue
                                        ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                        left_side = string['Text'][:element.span()[0]][::-1].split(" ")
                                        left_side = list(map(lambda x: x[-1], list(filter(lambda x: len(x)>1, left_side))))
                                        left_side.reverse()
                                        line = ""
                                        st = False
                                        elem = elem.upper()
                                        for lef in left_side:
                                            line += lef.upper()
                                            if levenstein(line, elem) <= 1:
                                                st = True
                                                break
                                            if len(line) - len(elem) > 4:
                                                break
                                        if st:
                                            abb_set[elem] = string['Index']+1
                                            continue
                                        ## тут лишь справа (ЕСКД) Единая система конструкторской документации
                                        right_side = string['Text'][element.span()[1]-1:].split(" ")
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
                                            abb_set[elem] = string['Index']+1
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
                    corr_fac = list(filter(lambda x: x[0] , zip([re.search("\W"+word+"\W", string['Text'].lower()) for word in corruption_factor_set], corruption_factor_set)))
                    no_conn  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", string['Text'].lower()) for word in no_connection_with_npa_set], no_connection_with_npa_set)))
                    inc_frm  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", string['Text'].lower()) for word in incorrect_formulation_set], incorrect_formulation_set)))

                    for cor in corr_fac:
                        sentence = "Фраза «{}»".format(cor[1])
                        feedback_list.append(["Corruption", sentence, string['Index'], cor[1]])
                    for no in no_conn:
                        sentence = "Фраза «{}»".format(no[1])
                        feedback_list.append(["NoNPA", sentence, string['Index'], no[1]])
                    for inc in inc_frm:
                        sentence = "Фраза «{}»".format(inc[1])
                        feedback_list.append(["IncorrectForm", sentence, string['Index'], inc[1]])  
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
                        feedback_list.append(["Abbreviation", sentence, string['Index'], r])
            except Exception as err:
                logger.error(err)
    #^--------------------------------------------------------------------------------------------------------------------           
    return feedback_list