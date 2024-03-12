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

def abb_finder(json_text, abbs=True, dicts=True, add_info=None, content_strings = None, excel_path=None):
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG, 
        format=f'%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s func: %(funcName)s %(message)s \nText path: {excel_path}\n')
    logger=logging.getLogger(__name__)
    if not abbs and not dicts:
        return []
    res_dct = dict(zip([i['Name'] for i in json_text['Worksheets']], [[] for _ in range(len(json_text['Worksheets']))]))
    #& Маски для поиска нужных нам сокращений
    abb_mask1 = re.compile(r"(?<!-)((«?([А-Я]+и)»?\s?){2,}|(«?([А-Я]{2,})»?\s?)+|(«?[A-Z]{2,}»?\s?)+)([^А-Яа-яA-Za-z0-9-—–]|$)")
    abb_mask2 = re.compile(r"(?<!-)(((([А-Я]+[а-я]*){2,})\s?)+|((([A-Z]+[a-z]*){2,})\s?)+)([^А-Яа-яA-Za-z0-9-—–]|$)")
    #&--------------------------------------------------------------------------------------------------------------------
    feedback_list = []
    for sheet in json_text['Worksheets']:
        devided_text = []
        for st in sheet['Rows']:
            devided_text.append(st['Cells'][0])
        text = '\n'.join([e['Text'] for e in devided_text])
        #^ Ищем таблицу с сокращениями и их расшифровками и термины
        pos = []
        for match in re.finditer("[С|с]окр", text):
            if match is not None:
                idx = match.end()
                string_num = text[:idx].count('\n')+1
                pos.append((idx, string_num))
        for match in re.finditer("[Т|т]ермин", text):
            if match is not None:
                idx = match.end()
                string_num = text[:idx].count('\n')+1
                pos.append((idx, string_num))
        #^--------------------------------------------------------------------------------------------------------------------
            
        #? Поиск где начинается содержание документа
        pos1 = pos2 = 1000000000
        idx1 = re.search("\n*\s*[С|с]одержание", text) 
        if idx1:
            pos1 = idx1.span()[0]
        idx2 = re.search("\n*\s*[О|о]главление", text)
        if idx2:
            pos2 = idx2.span()[0]
        idx = {pos1:idx1, pos2:idx2}
        idx = idx[min(idx)]
        if idx is not None:
            idx = idx.end()
            content_begin_pos = text[:idx].count('\n')+1       
        else:
            content_begin_pos = 0
        #?--------------------------------------------------------------------------------------------------------------------

        #& Объявление наши справочников и словарей
        abb_set = dict()
        special_words = {"далее", "условное обозначение", "условные обозначения", 
                        "сокращенное наименование", "сокращенные наименования"}
        corruption_factor_set = set()
        no_connection_with_npa_set = set()
        incorrect_formulation_set = set()
        #&--------------------------------------------------------------------------------------------------------------------

        #^ Если у нас идет слово Сокр
        if pos:
            idx = 0
            for p in pos:
                # if idx - p[1] > 7:
                #     continue
                b, idx = p[0], p[1]
                s = text[b:].split("\n")[1:]
                c, st = 0, 0
                buf1, buf2 = '', ''
                for i in s:
                    if i == '':
                        continue
                    if c == 7:
                        break
                    f1 = re.search(abb_mask1, i)
                    f2 = re.search(abb_mask2, i)
                    if f1 and f2:
                        f = f1 if (len(f1.group()) > len(f2.group()) and f1.span()[0] < 7) else f2 if f2.span()[0] < 7 else None
                    elif f1 or f2:
                        f = f1 if f1 else f2
                        f = f if f.span()[0] < 7 else None
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
                                    abb_set[buf1] = st
                                c = 0
                                st = idx
                                buf1 = f.group()
                                buf2 = i.replace(buf1, "")
                            #?-----------------------------------
                            
                    else:
                        if buf1 != '':
                            buf2 += i
                        c += 1
                    idx+=1
                if buf1:
                    if not buf1[-1].isalpha() and buf1[-1] != "»": buf1=buf1[:-1]
                    buf1 = re.sub("[\t\n\r]", "", buf1)
                    abb_set[buf1] = st
                    buf1, buf2 = '', ''
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

        #?
        c = 0
        content_end_pos = content_begin_pos
        if content_begin_pos > 0:
            for k in range(content_begin_pos+1, len(devided_text)):
                if c == 5:
                    content_end_pos = k-3
                    break
                txt = devided_text[k]
                list_findings = [re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|((([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.]))", re.ASCII), txt) != None,
                                re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), txt) != None,
                                re.search(re.compile(r"((?<=\s)|(?<=^))[(]((\d+[.]?)+|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), txt) != None]
                if any(list_findings):
                    c = 0
                    continue
                else:
                    c += 1
        
        #?-----------------------------

        forbidden_list = list(abb_set.values()) + list(range(content_begin_pos, content_end_pos+1))
        ## ВВЕДЕНИЕ начинается в строке content_begin_pos и кончается в content_end_pos
        if content_strings is not None:
            for c in content_strings:
                try:
                    key = re.sub("[.\d\t\n\r\f\v]", "", devided_text[c-1])
                    key = " ".join(list(filter(lambda x: x, key.split(" ")))).upper()
                    abb_set[key] = 0
                    if " И " in key:
                        new_key = key.split(" И ")
                        for k in new_key:
                            if k[-1] == " ":
                                k = k[:-1]
                            abb_set[k] = 0
                except:
                    pass

        #^ Поиск сокращений в нашем тексте
        for i in range(len(devided_text)):
            try:
                buf = []
                if i not in forbidden_list:
                    f = [re.finditer(abb_mask1, devided_text[i]['Text']), re.finditer(abb_mask2, devided_text[i]['Text'])]
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
                                    if abb_set[elem] <= i+1:
                                        list_of_added_elems.extend(range(element.span()[0], element.span()[1]+1))
                                        continue
                                    else:
                                        buf.append((elem, element.span()))
                                        st = True
                                #! -------------------------------------------
                                elif all(list(map(lambda x: 1<len(x)<9, elem.split(" ")))) and ((not re.search("[\s.,:;!?]"+elem.lower()+"[\s.,:;!?]", text)) and (not re.search(("[\s.,:;!?]"+elem[0]+elem.lower()[1:])+"[\s.,:;!?]", text))):
                                    if element.span()[0] in list_of_added_elems or element.span()[1] in list_of_added_elems:
                                        continue
                                    if devided_text[i]['Text'][element.span()[1]-1] == ")":
                                        ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                        left_side_ind = len(devided_text[i]['Text'][element.span()[1]-2::-1]) - re.search("[(]", devided_text[i]['Text'][element.span()[1]-2::-1]).span()[0]
                                        bracket_info = devided_text[i]['Text'][left_side_ind:element.span()[1]-1].split(' ')
                                        bracket_info = list((filter(lambda x: len(x)>1 and all(xs.isalpha() for xs in x), bracket_info)))
                                        ## Смотрим есть ли перед аббревиатурой спец слово
                                        for word in bracket_info:
                                            if word in special_words:
                                                ## Если оно есть, то проверяем расшифровку
                                                left_side = devided_text[i]['Text'][left_side_ind-1::-1]
                                                left_side = list(map(lambda x: x[-1], list(filter(lambda x: len(x)>1, left_side))))
                                                ## Типа провекрка, left_side содержит первые юуквы слов, стоящих перед скобками
                                                st = True
                                                break
                                        if st:
                                            abb_set[elem] = i+1
                                            continue
                                        ## тут лишь справа (ЕСКД) Единая система конструкторской документации
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
                    corr_fac = list(filter(lambda x: x[0] , zip([re.search("\W"+word+"\W", devided_text[i]['Text'].lower()) for word in corruption_factor_set], corruption_factor_set)))
                    no_conn  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", devided_text[i]['Text'].lower()) for word in no_connection_with_npa_set], no_connection_with_npa_set)))
                    inc_frm  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", devided_text[i]['Text'].lower()) for word in incorrect_formulation_set], incorrect_formulation_set)))

                    for cor in corr_fac:
                        prev_line, next_line = '', ''
                        for k in range(i-1, -1, -1):
                            if devided_text[k] != '':
                                prev_line = devided_text[k]
                                break
                        for k in range(i+1, len(devided_text)):
                            if devided_text[k] != '':
                                next_line = devided_text[k]
                                break
                        feedback_list.append(["CorruptionFactorError", cor[1], devided_text[i]['Address']])
                    for no in no_conn:
                        prev_line, next_line = '', ''
                        for k in range(i-1, -1, -1):
                            if devided_text[k] != '':
                                prev_line = devided_text[k]
                                break
                        for k in range(i+1, len(devided_text)):
                            if devided_text[k] != '':
                                next_line = devided_text[k]
                                break
                        feedback_list.append(["NoConnectionWithNPAError", no[1], devided_text[i]['Address']])
                    for inc in inc_frm:
                        prev_line, next_line = '', ''
                        for k in range(i-1, -1, -1):
                            if devided_text[k] != '':
                                prev_line = devided_text[k]
                                break
                        for k in range(i+1, len(devided_text)):
                            if devided_text[k] != '':
                                next_line = devided_text[k]
                                break
                        feedback_list.append(["IncorrectFormulationError", inc[1], devided_text[i]['Address']])  
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
                        prev_line, next_line = '', ''
                        for k in range(i-1, -1, -1):
                            if devided_text[k] != '':
                                prev_line = devided_text[k]
                                break
                        for k in range(i+1, len(devided_text)):
                            if devided_text[k] != '':
                                next_line = devided_text[k]
                                break
                        feedback_list.append(["AbbreviationError", sentence, devided_text[i]['Address']])
            except Exception as err:
                logger.error(err)
        #^--------------------------------------------------------------------------------------------------------------------           
    return feedback_list