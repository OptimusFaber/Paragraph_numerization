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

def abb_finder(text, abbs=True, dicts=(True, True, True), add_info=None, content_strings = None, json_path=None, log_path='myapp.log', new_format=0):
    logging.basicConfig(filename=log_path, level=logging.DEBUG, 
        format=f'%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s func: %(funcName)s %(message)s \nText path: {json_path}\n')
    logger=logging.getLogger(__name__)
    if not abbs and not all(dicts):
        return []
    #& Маски для поиска нужных нам сокращений
    abb_mask1 = re.compile(r"(?<!-)((«?([А-Я]+и)»?\s?){2,}|(«?([А-Я]{2,})»?\s?)+|(«?[A-Z]{2,}»?\s?)+)([^А-Яа-яA-Za-z0-9-—–]|$)")
    abb_mask2 = re.compile(r"(?<!-)(((([А-Я]+[а-я]*){2,})\s?)+|((([A-Z]+[a-z]*){2,})\s?)+)([^А-Яа-яA-Za-z0-9-—–]|$)")
    #&--------------------------------------------------------------------------------------------------------------------
    all_words = ""
    pos, js = [], []
    con = con_end = c = 0
    flag = 1
    for elem in text.keys():
        if elem == 'Paragraphs':
            js.append(text[elem])
            for e in text[elem]:
                all_words += re.sub("[^A-Za-zА-Яа-яЁё\s]", "", e["Text"]) + " "
                match = re.finditer(re.compile(r"(С|с)окращени(я|й)|(Т|т)ермин(ы|ов)", flags=re.IGNORECASE), e['Text'])
                for m in match:
                    pos.append([e['Index'], m.span()[0], m.span()[1]])
                if flag:
                    context = re.search(r"\s*(([С|с]одержание)|([О|о]главление))", e['Text'])
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
    for p in pos:
        counter = p[1]
        flag = True
        while flag:
            buf1 = ''
            block = text['Paragraphs'][p[0]]["Text"][p[1]:].split("\n")
            paragraph = p[0]
            c = index = string = 0
            for i in  range(len(block)):
                if block[i] == '':
                    counter += 1
                    continue
                if c == 7:
                    flag = False
                    break
                f1 = re.search(abb_mask1, block[i])
                f2 = re.search(abb_mask2, block[i])
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
                        if buf1 != "":
                            buf1 += ' ' + f.group()
                        else:
                            c = 0
                            buf1 = f.group()
                            index = counter
                            string = i 
                        #?-----------------------------------
                        
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
                            abb_set[buf1] = (paragraph, string, index)
                        buf1 = ''
                    c += 1
                counter += len(block[i])+1
            if buf1:
                if not buf1[-1].isalpha() and buf1[-1] != "»": buf1=buf1[:-1]
                buf1 = re.sub("[\t\n\r]", "", buf1)
                if not abb_set.get(buf1):
                    abb_set[buf1] = (paragraph, string, index)
            flag = False
    #^--------------------------------------------------------------------------------------------------------------------
                
    #* Дополняем словари если нужно
    if add_info:
        if not new_format:
            if "Corruption" in add_info.keys():
                for elem in add_info["Corruption"]:
                    corruption_factor_set.add(elem["Value"])
            if "Abbreviation" in add_info.keys():
                for elem in add_info["Abbreviation"]:
                    abb_set[elem["Value"]] = (0, 0, 0)
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
    buffer = []
    if con and con_end:
        if con[0] == con_end[0]:
            buffer.extend([(con[0], i) for i in range(con[1], con_end[1])])
        else:
            while con[0] != con_end[0]:
                buffer.extend([(con[0], i) for i in range(con[1], len(text['Paragraphs'][con[0]]["Text"].split('\n')))])
                con[0]+=1
                con[1]=0
            buffer.extend([(con[0], i) for i in range(con[1], con_end[1])])


    forbidden_list = list(set(map(lambda lst: lst[:2], abb_set.values()))) + buffer
    #^ Поиск сокращений в нашем тексте
    feedback_list = []
    js = js[0]
    for i in range(len(js)):
        strings = js[i]['Text'].split('\n')
        counter = 0
        for j in range(len(strings)):
            try:
                buf = []
                orig_text = strings[j]
                strings[j] = strings[j].replace(u'\xa0', u' ')
                strings[j] = re.sub(r'[\u2013\u2014]', '-', strings[j])
                strings[j] = re.sub(r'\u00A0', ' ', strings[j])
                if (js[i]['Index'], j) not in forbidden_list:
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
                                    if abb_set[elem][0] < js[i]['Index'] or (abb_set[elem][0] == js[i]['Index'] and abb_set[elem][2] < counter):
                                        list_of_added_elems.extend(range(element.span()[0], element.span()[1]+1))
                                        
                                        continue
                                #! -------------------------------------------
                                if all(list(map(lambda x: 1<len(x)<11, elem.split(" ")))):
                                    #?Убираем параграф если он весь написан большими буквами
                                    if strings[j].isupper():
                                        
                                        continue
                                    
                                    st = False
                                    exp = elem.split(" ")
                                    for k in range(len(exp)):
                                        if len(exp[k])>=9 and not any(k.islower() for k in exp[k]):
                                            st = True
                                            break
                                        if exp[k].lower() in all_words:
                                            st = True
                                            break
                                    if st: 
                                        
                                        continue
                                        
                                    if element.span()[0] in list_of_added_elems or element.span()[1] in list_of_added_elems:
                                        
                                        continue
                                    f1 = re.search(r"^[\t ]*[-—–]", strings[j][element.span()[1]:])         #* Ситуация типа ООО - ...
                                    f2 = re.search(r"^[\t ]*[-—–]", strings[j][:element.span()[0]][::-1])   #* Ситуацтя типа ... - ООО

                                    if f1:
                                        right_side = strings[j][element.span()[1]:][f1.span()[0]:].replace(')', '').replace('(', '').split(" ")
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
                                            abb_set[elem] = [js[i]['Index'], j, counter+element.span()[0]]
                                            
                                            continue
                                    if f2:
                                        left_side = strings[j][element.span()[0]-1::-1][f2.span()[0]:].replace(')', '').replace('(', '').split(" ")
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
                                            abb_set[elem] = [js[i]['Index'], j, counter+element.span()[0]]
                                            
                                            continue

                                    if ")" in strings[j][element.span()[1]-1:min(element.span()[1]+20, len(strings[j]))] and "(" in strings[j][max(element.span()[0]-20, 0):element.span()[0]]:
                                        ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                        left_side_ind = len(strings[j][element.span()[1]-2::-1]) - re.search("[(]", strings[j][element.span()[1]-2::-1]).span()[0]
                                        bracket_info = strings[j][left_side_ind:element.span()[1]-1]
                                        ## Смотрим есть ли перед аббревиатурой спец слово
                                        for word in special_words:
                                            if word in bracket_info:
                                                st = True
                                                break
                                        if st:
                                            if not abb_set.get(elem):
                                                abb_set[elem] = [js[i]['Index'], j, counter+element.span()[0]]
                                            else:
                                                if abb_set[elem][0] > js[i]['Index'] or (abb_set[elem][0] == js[i]['Index'] and abb_set[elem][2] > counter):
                                                # if js[i]['Index'] < abb_set[elem]:
                                                    abb_set[elem] = [js[i]['Index'], j, counter+element.span()[0]]
                                            
                                            continue
                                        ## (ЕСКД)
                                        if re.search(f"[(]\t*{elem}\t*[)]", strings[j]):
                                            if not abb_set.get(elem):
                                                abb_set[elem] = [js[i]['Index'], j, counter+element.span()[0]]
                                            else:
                                                if abb_set[elem][0] > js[i]['Index'] or (abb_set[elem][0] == js[i]['Index'] and abb_set[elem][2] > counter):
                                                # if js[i]['Index'] < abb_set[elem]:
                                                    abb_set[elem] = [js[i]['Index'], j, counter+element.span()[0]]
                                            
                                            continue

                                        bracket_info = re.search(f"[(][^()]*{elem}[^()]*[)]", strings[j])
                                        if bracket_info:
                                            pos = bracket_info.span()
                                            bracket_info = bracket_info.group().replace('(', '').replace(')', '').replace(elem, '')
                                            bracket_info = bracket_info.split(' ')
                                            bracket_info = list(filter(lambda x: len(x)>1, bracket_info))
                                            bracket_info = list(map(lambda x: x.upper(), list(map(lambda x: x[0], bracket_info))))
                                            elemx = elem + ''.join(bracket_info)
                                            left_side = strings[j][:pos[0]][::-1].replace('(', '').replace(')', '').replace('«', '').replace('»', '').split(" ")
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
                                                abb_set[elem] = [js[i]['Index'], j, counter+element.span()[0]]
                                                
                                                continue

                                            right_side = strings[j][pos[1]:].split(" ")
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
                                                abb_set[elem] = [js[i]['Index'], j, counter+element.span()[0]]
                                                
                                                continue

                                    flag = False
                                    if len(elem.split(" ")) > 1:
                                        elem1 = elem.split(' ')
                                        elem = []
                                        a = ''
                                        for e in range(len(elem1)):
                                            a += elem1[e] + ' '
                                            if a[:-1] in list(abb_set.keys()):
                                                if abb_set[a[:-1]][0] < js[i]['Index'] or (abb_set[a[:-1]][0] == js[i]['Index'] and abb_set[a[:-1]][2] < counter):
                                                    flag = True
                                                else:
                                                    elem.append(elem1[e])
                                            elif elem1[e] in list(abb_set.keys()):
                                                if abb_set[elem1[e]][0] < js[i]['Index'] or (abb_set[elem1[e]][0] == js[i]['Index'] and abb_set[elem1[e]][2] < counter):
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
                        corr_fac = list(filter(lambda x: x[0], zip([re.search("\W"+word+"\W", strings[j].lower()) for word in corruption_factor_set], corruption_factor_set)))
                        for cor in corr_fac:
                            pos = re.search("\W"+cor[1]+"\W", strings[j].lower()).span()
                            sentence = "Фраза «{}»".format(cor[1])
                            feedback_list.append(["Corruption", sentence, js[i]['Index'], (counter+pos[0], counter+pos[1]), cor[1]])
                    if dicts[1]:
                        no_conn  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", strings[j].lower()) for word in no_connection_with_npa_set], no_connection_with_npa_set)))
                        for no in no_conn:
                            pos = re.search("\W"+no[1]+"\W", strings[j].lower()).span()
                            sentence = "Фраза «{}»".format(no[1])
                            feedback_list.append(["NoNPA", sentence, js[i]['Index'], (counter+pos[0], counter+pos[1]), no[1]])
                    if dicts[2]:
                        inc_frm  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", strings[j].lower()) for word in incorrect_formulation_set], incorrect_formulation_set)))
                        for inc in inc_frm:
                            pos = re.search("\W"+inc[1]+"\W", strings[j].lower()).span()
                            sentence = "Фраза «{}»".format(inc[1])
                            feedback_list.append(["IncorrectForm", sentence, js[i]['Index'], (counter+pos[0], counter+pos[1]), inc[1]])  
                #?------------------------------------------------------------------------------------
                if abbs and buf:
                    buf = list(filter(lambda x: (x[1][0] not in list_of_added_elems) and (x[1][1] not in list_of_added_elems), buf))
                    res = set()
                    for b in buf:
                        buf_f = list(filter(lambda x: x[1][0]==b[1][0] or x[1][0]==b[1][0]+1 or x[1][0]==b[1][0]-1, buf))
                        buf_f = sorted(buf_f, key=lambda x: len(x[0]), reverse=True)
                        buf_y = list(filter(lambda x: x[1][1]==b[1][1] or x[1][1]==b[1][1]-1 or x[1][1]==b[1][1]+1, buf))
                        buf_y = sorted(buf_y, key=lambda x: len(x[0]), reverse=True)
                        res.add(max(buf_y[0], buf_f[0], key=lambda x: len(x)))
                    #! ErrorType, LineText, LineNumber, ОШИБКА, PrevLineText, NextLine
                    for r, ind in res:
                        sentence = f"Неизвестная аббревиатура «{r}»"
                        if len(r.split(' ')) > 1:
                            if r not in orig_text:
                                mask=''
                                mask = r.split(' ')
                                mask='.'.join(mask)
                                r = re.search(mask, orig_text).group()
                        feedback_list.append(["Abbreviation", sentence, js[i]['Index'], (counter+ind[0],counter+ind[1]), r])
            except Exception as err:
                logger.error(err)

            counter += len(strings[j])+1
    #^--------------------------------------------------------------------------------------------------------------------
    return feedback_list