import re
import logging
from fuzzywuzzy import fuzz

#! Алгоритм Левинштейна (вместо него теперь fuzzywuzzy)
    
def letter_extractor(string, ind):
    line = []
    for st in string:
        if len(st) > 1 or st == 'и':
            for s in range(len(st)-1, -1, -1):
                if st[s].isupper() or s == ind:
                    line.append(st[s].upper())
    return line        
        

def abb_finder(text, abbs=True, dicts=(True, True, True), add_info=None, content_strings = None, json_path=None, log_path='myapp.log', defis=False, new_format=0):
    logging.basicConfig(filename=log_path, level=logging.DEBUG, 
        format=f'%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s func: %(funcName)s %(message)s \nText path: {json_path}\n')
    logger=logging.getLogger(__name__)
    if not abbs and not all(dicts):
        return []
    #& Маски для поиска нужных нам сокращений
    abb_mask1 = re.compile(r"(?<![a-zA-Zа-яА-ЯЁё0-9-—–])((«?([А-ЯЁ]+и)»?\s?){2,}|(«?([А-ЯЁ]{2,})»?\s?)+|(«?[A-Z]{2,}»?\s?)+)([^ЁёА-Яа-яA-Za-z0-9-—–]|$)")
    if defis:
        abb_mask2 = re.compile(r"(?<![a-zA-Zа-яА-ЯЁё0-9-—–])(?<!-)(((([А-ЯЁ]+[а-яё-]*){2,})\s?)+|((([A-Z]+[a-z]*){2,})\s?)+)([^ЁёА-Яа-яA-Za-z0-9-—–]|$)")
    else:
        abb_mask2 = re.compile(r"(?<![a-zA-Zа-яА-ЯЁё0-9-—–])(?<!-)(((([А-ЯЁ]+[а-яё]*){2,})\s?)+|((([A-Z]+[a-z]*){2,})\s?)+)([^ЁёА-Яа-яA-Za-z0-9-—–]|$)")
    #&--------------------------------------------------------------------------------------------------------------------
    all_words = ""
    pos, js, tables = [], [], []
    con = con_end = c = 0
    flag = 1
    for elem in text.keys():
        if elem == 'Paragraphs':
            js.append(text[elem])
            for e in text[elem]:
                all_words += re.sub("[^A-Za-zА-Яа-яЁё\s]", "", e["Text"]) + " "
                match = re.search(re.compile(r"(С|с)окращени(я|й)|(Т|т)ермин(ы|ов)", flags=re.IGNORECASE), e['Text'])
                if match is not None:
                    pos.append(e['Index'])
                if flag:
                    context = re.search(re.compile(r"\s*(([С|с]одержание)|([О|о]главление))", flags=re.IGNORECASE), e['Text'])
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
                    for n in range(len(cell['Cells'])):
                        for m in range(len(cell['Cells'][n]["Paragraphs"])):
                            buf.append(cell['Cells'][n]["Paragraphs"][m])
                            all_words += re.sub("[^A-Za-zА-Яа-яЁё\s]", "", cell['Cells'][n]["Paragraphs"][m]["Text"]) + " "

                js.append(buf)
                num = table['Index']
                for p in pos:
                    if 0 < num - p < 5:
                        tables.append(table)
    all_words = list(filter(lambda x: len(x)>1, all_words.split(" ")))
    all_words = list(map(lambda x: x.replace(x[0], x[0].lower()), all_words))
    all_words = set(list(filter(lambda x: all([not i.isupper() for i in x]), all_words)))
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
                txt = cell['Paragraphs'][0]['Text'].replace(u'\xa0', u' ')
                f1 = re.search(abb_mask1, txt)
                f2 = re.search(abb_mask2, txt)
                if f1 and f2:
                    f = f1 if (len(f1.group()) > len(f2.group())) else f2
                elif f1 or f2:
                    f = f1 if f1 else f2
                    f = f if f.span()[0] < 7 else None
                else:
                    f = None
                if f:
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
                        abb_set[f] = cell['Paragraphs'][0]['Index']
                break         
    #^--------------------------------------------------------------------------------------------------------------------
                
    #* Дополняем словари если нужно
    if add_info:
        if not new_format:
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

    # forbidden_list = list(abb_set.values()) + list(range(con, con_end))
    forbidden_list = list(abb_set.values())
    #^ Поиск сокращений в нашем тексте
    feedback_list = []
    for part in js:
        for string in part:
            try:
                buf = []
                orig_text = string['Text']
                string['Text'] = string['Text'].replace(u'\xa0', u' ')
                string['Text'] = re.sub(r'[\u2013\u2014]', '-', string['Text'])
                string['Text'] = re.sub(r'\u00A0', ' ', string['Text'])
                if string["Index"] == 28:
                    print()
                if string['Index'] not in forbidden_list and not string['IsToc']:
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
                                    if abb_set[elem] <= string['Index']:
                                        d = re.search(elem, element.group()).span()
                                        list_of_added_elems.extend(range(element.span()[0]+d[0], element.span()[0]+d[1]))
                                        continue
                                #! -------------------------------------------
                                if all(list(map(lambda x: 1<len(x)<11, elem.split(" ")))):
                                    #?Убираем параграф если он весь написан большими буквами
                                    if string['Text'].isupper():
                                        continue
                                    
                                    st = False
                                    exp = elem.split(" ")
                                    for i in range(len(exp)):
                                        if len(exp[i])>=9 and not any(k.islower() for k in exp[i]):
                                            st = True
                                            break
                                        if exp[i].lower() in all_words:
                                            st = True
                                            break
                                    if st: continue
                                        
                                    if element.span()[0] in list_of_added_elems or element.span()[1] in list_of_added_elems:
                                        continue
                                    f1 = re.search(r"^[\t ]*[-—–]", string['Text'][element.span()[1]:])         #* Ситуация типа ООО - ...
                                    f2 = re.search(r"^[\t ]*[-—–]", string['Text'][:element.span()[0]][::-1])   #* Ситуацтя типа ... - ООО

                                    if f1:
                                        right_side = string['Text'][element.span()[1]:][f1.span()[0]:].replace(')', '').replace('(', '').split(" ")
                                        right_side = letter_extractor(right_side, 0)
                                        line = ""
                                        st = False
                                        elemx = elem.upper().replace(' ', '')
                                        for rig in right_side:
                                            line += rig
                                            if fuzz.token_sort_ratio(line, elemx) > 75:
                                                st = True
                                                break
                                            if len(line) - len(elemx) > 4:
                                                break
                                        if st:
                                            abb_set[elem] = string['Index']
                                            continue
                                    if f2:
                                        left_side = string['Text'][element.span()[0]-1::-1][f2.span()[0]:].replace(')', '').replace('(', '').split(" ")
                                        left_side = list(map(lambda x: x[::-1], left_side))
                                        left_side = letter_extractor(left_side, 0)
                                        line = ""
                                        st = False
                                        elemx = elem.upper().replace(' ', '')
                                        for lef in left_side:
                                            line = lef + line
                                            if fuzz.token_sort_ratio(line, elemx) > 75:
                                                st = True
                                                break
                                            if len(line) - len(elemx) > 4:
                                                break
                                        if st:
                                            abb_set[elem] = string['Index']
                                            continue

                                    if ")" in string['Text'][element.span()[1]-1:min(element.span()[1]+20, len(string['Text']))] and "(" in string['Text'][max(element.span()[0]-20, 0):element.span()[0]]:
                                        ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                        left_side_ind = len(string['Text'][element.span()[1]-2::-1]) - re.search("[(]", string['Text'][element.span()[1]-2::-1]).span()[0]
                                        bracket_info = string['Text'][left_side_ind:element.span()[1]-1]
                                        ## Смотрим есть ли перед аббревиатурой спец слово
                                        for word in special_words:
                                            if word in bracket_info:
                                                st = True
                                                break
                                        if st:
                                            if not abb_set.get(elem):
                                                abb_set[elem] = string['Index']
                                            else:
                                                if string['Index'] < abb_set[elem]:
                                                    abb_set[elem] = string['Index']
                                            continue
                                        ## (ЕСКД)
                                        if re.search(f"[(]\t*{elem}\t*[)]", string['Text']):
                                            if not abb_set.get(elem):
                                                abb_set[elem] = string['Index']
                                            else:
                                                if string['Index'] < abb_set[elem]:
                                                    abb_set[elem] = string['Index']
                                            continue

                                        bracket_info = re.search(f"[(][^()]*{elem}[^()]*[)]", string['Text'])
                                        if bracket_info:
                                            pos = bracket_info.span()
                                            bracket_info = bracket_info.group().replace('(', '').replace(')', '').replace(elem, '')
                                            bracket_info = bracket_info.split(' ')
                                            bracket_info = list(filter(lambda x: len(x)>1, bracket_info))
                                            bracket_info = list(map(lambda x: x.upper(), list(map(lambda x: x[0], bracket_info))))
                                            elemx = elem + ''.join(bracket_info)
                                            left_side = string['Text'][:pos[0]][::-1].replace('(', '').replace(')', '').replace('«', '').replace('»', '').split(" ")
                                            left_side = list(map(lambda x: x[::-1], left_side))
                                            left_side = letter_extractor(left_side, 0)
                                            line = ""
                                            st = False
                                            elemx = elemx.upper()
                                            for lef in left_side:
                                                line = lef.upper() + line
                                                if fuzz.token_sort_ratio(line, elemx) > 75:
                                                    st = True
                                                    break
                                                if len(line) - len(elemx) > 4:
                                                    break
                                            if st:
                                                abb_set[elem] = string['Index']
                                                continue

                                            right_side = string['Text'][pos[1]:].split(" ")
                                            right_side = letter_extractor(right_side, 0)
                                            line = ""
                                            st = False
                                            for rig in right_side:
                                                line += rig.upper()
                                                if fuzz.token_sort_ratio(line, elemx) > 75:
                                                    st = True
                                                    break
                                                if len(line) - len(elemx) > 4:
                                                    break
                                            if st:
                                                abb_set[elem] = string['Index']
                                                continue

                                    flag = False
                                    g = elem
                                    if len(elem.split(" ")) > 1:
                                        elem1 = elem.split(' ')
                                        elem = []
                                        a = ''
                                        for e in range(len(elem1)):
                                            a += elem1[e] + ' '
                                            if a[:-1] in list(abb_set.keys()):
                                                if abb_set[a[:-1]] <= string['Index']:
                                                    flag = True
                                                else:
                                                    elem.append(elem1[e])
                                            elif elem1[e] in list(abb_set.keys()):
                                                if abb_set[elem1[e]] <= string['Index']:
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
                                        d = re.search(elem, g).span()
                                        buf.append((elem, (element.span()[0]+d[0], element.span()[0]+d[1])))
                                        st = True
                                    else:
                                        for e in elem:
                                            buf.append((elem, element.span()))
                                            st = True
                    #^------------------------------------------------------------------------------------
                #? Поиск элементов из наших 3 словарей
                if dicts:
                    if dicts[0]:
                        corr_fac = list(filter(lambda x: x[0] , zip([re.search("\W"+word+"\W", string['Text'].lower()) for word in corruption_factor_set], corruption_factor_set)))
                        for cor in corr_fac:
                            sentence = "Фраза «{}»".format(cor[1])
                            feedback_list.append(["Corruption", sentence, string['Index'], cor[1]])
                    if dicts[1]:
                        no_conn  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", string['Text'].lower()) for word in no_connection_with_npa_set], no_connection_with_npa_set)))
                        for no in no_conn:
                            sentence = "Фраза «{}»".format(no[1])
                            feedback_list.append(["NoNPA", sentence, string['Index'], no[1]])
                    if dicts[2]:   
                        inc_frm  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", string['Text'].lower()) for word in incorrect_formulation_set], incorrect_formulation_set)))
                        for inc in inc_frm:
                            sentence = "Фраза «{}»".format(inc[1])
                            feedback_list.append(["IncorrectForm", sentence, string['Index'], inc[1]])  
                #?------------------------------------------------------------------------------------
                if abbs and buf:
                    buf = list(filter(lambda x: (x[1][0] not in list_of_added_elems) and (x[1][1] not in list_of_added_elems), buf))
                    res = set()
                    for b in buf:
                        buf_f = list(filter(lambda x: x[1][0]==b[1][0] or x[1][0]==b[1][0]+1 or x[1][0]==b[1][0]-1, buf))
                        buf_f = sorted(buf_f, key=lambda x: len(x[0]), reverse=True)
                        buf_y = list(filter(lambda x: x[1][1]==b[1][1] or x[1][1]==b[1][1]-1 or x[1][1]==b[1][1]+1, buf))
                        buf_y = sorted(buf_y, key=lambda x: len(x[0]), reverse=True)
                        res.add(max(buf_y[0][0], buf_f[0][0], key=lambda x: len(x)))
                    #! ErrorType, LineText, LineNumber, ОШИБКА, PrevLineText, NextLine
                    for r in res:
                        sentence = f"Неизвестная аббревиатура «{r}»"
                        if len(r.split(' ')) > 1:
                            if r not in orig_text:
                                mask=''
                                mask = r.split(' ')
                                mask='.'.join(mask)
                                r = re.search(mask, orig_text).group()
                        feedback_list.append(["Abbreviation", sentence, string['Index'], r])
            except Exception as err:
                logger.error(err)
    #^--------------------------------------------------------------------------------------------------------------------
    return feedback_list