import re
import psycopg2

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

def abb_finder(t):
    #& Маски для поиска нужных нам сокращений
    abb_mask1 = re.compile(r"(?<!-)((«?([А-Я]+и)»?\s?){2,}|(«?([А-Я]{2,})»?\s?)+|(«?[A-Z]{2,}»?\s?)+)([^А-Яа-я0-9-—–]|$)")
    abb_mask2 = re.compile(r"(?<!-)(((([А-Я]+[а-я]*){2,})\s?)+|((([A-Z]+[a-z]*){2,})\s?)+)([^А-Яа-я0-9-—–]|$)")
    #&--------------------------------------------------------------------------------------------------------------------

    #^ Ищем таблицу с сокращениями и их расшифровками 
    text = t
    pos = []
    for match in re.finditer("[С|с]окр", text):
        idx = match.end()
        string_num = text[:idx].count('\n')+1
        pos.append((idx, string_num))
    #^--------------------------------------------------------------------------------------------------------------------

    #& Объявление наши справочников и словарей
    abb_set = dict()
    special_words = {"далее", "условное обозначение", "условные обозначения", 
                    "сокращенное наименование", "сокращенные наименования"}

    corruption_factor_set = {"вправе", "может", "как правило", "возможно", "допускается", 
                            "и т. д.", "и так далее", "и т. п.", "и тому подобное", 
                            "и тому подобные", "и др.", "и другие" , "и пр.", "и прочие"}

    no_connection_with_npa_set = {"в установленном порядке", "согласно действующему законодательству"}

    incorrect_formulation_set = {"своевременно", "согласно установленным правилам", "в соответствии с действующим законодательством",
                                "в случае необходимости", "по мере необходимости",  "при наличии достаточных оснований", 
                                "в исключительных случаях", "в отдельных случаях", "целесообразно", "при достаточных основаниях"}
    #&--------------------------------------------------------------------------------------------------------------------

    #^ Если у нас идет слово Сокр
    if pos:
        idx = 0
        for p in pos:
            if idx - p[1] > 5:
                break
            b, idx = p[0], p[1]
            s = text[b:].split("\n")[1:]
            c, st = 0, 0
            buf1, buf2 = '', ''
            for i in s:
                if i == '':
                    continue
                if c == 5:
                    break
                f1 = re.search(abb_mask1, i)
                f2 = re.search(abb_mask2, i)
                if f1 and f2:
                    f = f1 if (len(f1.group()) > len(f2.group()) and f1.span()[0] == 0) and f1 else f2 if f2.span()[0] == 0 else None
                elif f1 or f2:
                    f = f1 if f1 else f2
                    f = f if f.span()[0] == 0 else None
                else:
                    f = None
                if f:
                    if f.span()[0] == 0:
                        #?-----------------------------------
                        if buf1 != "" and buf2 == "":
                            buf1 += f.group()
                            buf2 = i.replace(f.group(), "")
                        else:
                            if buf1:
                                buf1 = re.sub("[\t\n\r]", "", buf1)
                                if not buf1[-1].isalpha(): buf1=buf1[:-1]
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
                if not buf1[-1].isalpha(): buf1=buf1[:-1]
                buf1 = re.sub("[\t\n\r]", "", buf1)
                abb_set[buf1] = st
                buf1, buf2 = '', ''
    #^--------------------------------------------------------------------------------------------------------------------


    #^ Подгрузка спец слов из словаря
    try:
        connection = psycopg2.connect(user="name",
                                    password="password",
                                    host="host",
                                    port="port",
                                    database="db")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from mobile"

        cursor.execute(postgreSQL_select_Query)

        mobile_records = cursor.fetchall()

        for row in mobile_records:
            special_words.add(row[0].lower())
            abb_set[row[1].lower()] = 0
            corruption_factor_set.add(row[2].lower())
            no_connection_with_npa_set.add(row[3].lower())
            incorrect_formulation_set.add(row[4].lower())

    except:
        pass
    #^--------------------------------------------------------------------------------------------------------------------

    #^ Поиск сокращений в нашем тексте
    result = ""
    feedback_list = []
    devided_text = text.split("\n")
    for i in range(len(devided_text)):
        if i not in list(abb_set.values()):
            f = [re.finditer(abb_mask1, devided_text[i]), re.finditer(abb_mask2, devided_text[i])]
            buf = []
            #^------------------------------------------------------------------------------------
            for itter in f:       
                for element in itter:
                    if element:
                        st = False
                        elem = element.group()
                        ##----------------------------
                        for _ in range(2):
                            if not elem[-1].isalpha():
                                if elem[-1] != "»":
                                    if elem[-1].isdigit():
                                        continue
                                    elem = elem[:-1]
                        elem = re.sub("[«»]", "", elem)
                        if elem in buf:
                            continue
                        ##----------------------------
                        if elem in list(abb_set.keys()):
                            if abb_set[elem] <= i+1:
                                continue
                            else:
                                buf.append((elem, element.span()))
                                st = True
                        elif all(list(map(lambda x: 1<len(x)<9, elem.split(" ")))) and ((not re.search("[\s.,:;!?]"+elem.lower()+"[\s.,:;!?]", text)) and (not re.search(("[\s.,:;!?]"+elem[0]+elem.lower()[1:])+"[\s.,:;!?]", text))):
                            f1 = re.search("([А-Я]?[а-я]*)?[\t ]*[-—–]", devided_text[i][element.span()[1]:])
                            f2 = re.search("[\t ]*[-—–]", devided_text[i][:element.span()[0]][::-1])
                            if f1:
                                if f1.span()[0] == 0:
                                    abb_set[elem] = i+1
                                    continue
                            if f2:
                                if f2.span()[0] == 0:
                                    abb_set[elem] = i+1
                                    continue 
                            if devided_text[i][element.span()[0]-1] == "(" and (")" in devided_text[i][element.span()[1]-1:element.span()[1]+2]):
                                ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                                left_side = devided_text[i][:element.span()[0]].split(" ")
                                left_side = list(map(lambda x: x[0], list(filter(lambda x: len(x)>1, left_side))))
                                left_side.reverse()
                                line = ""
                                st = False
                                elem = elem.upper()
                                for lef in left_side:
                                    line += lef.upper()
                                    if levenstein(line[::-1], elem) <= 1:
                                        st = True
                                        break
                                    if len(line) - len(elem) > 4:
                                        break
                                if st:
                                    abb_set[elem] = i+1
                                    continue
                            buf.append((elem, element.span()))
                            st = True
                        if any([word in devided_text[i].lower() for word in special_words]):
                            if st:
                                buf.pop(-1)
                            abb_set[elem] = i+1
                        else:
                            continue
            #^------------------------------------------------------------------------------------

            #? Поиск элементов из наших 3 словарей
            # re.search("\W"+word+"\W", devided_text[i].lower())
            corr_fac = list(filter(lambda x: x[0] , zip([re.search("\W"+word+"\W", devided_text[i].lower()) for word in corruption_factor_set], corruption_factor_set)))
            no_conn  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", devided_text[i].lower()) for word in no_connection_with_npa_set], no_connection_with_npa_set)))
            inc_frm  = list(filter(lambda x: x[0],  zip([re.search("\W"+word+"\W", devided_text[i].lower()) for word in incorrect_formulation_set], incorrect_formulation_set)))

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
                feedback_list.append(["CorruptionFactorError", devided_text[i], i+1, cor[1], prev_line, next_line])
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
                feedback_list.append(["NoConnectionWithNPAError", devided_text[i], i+1, no[1], prev_line, next_line])
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
                feedback_list.append(["IncorrectFormulationError", devided_text[i], i+1, inc[1], prev_line, next_line])  
            #?------------------------------------------------------------------------------------

            if buf:
                res = set()
                for b in buf:
                    buf_f = list(filter(lambda x: x[1][0]==b[1][0], buf))
                    buf_f = sorted(buf_f, key=lambda x: len(x[0]), reverse=True)
                    buf_y = list(filter(lambda x: x[1][1]==b[1][1], buf))
                    buf_y = sorted(buf_y, key=lambda x: len(x[0]), reverse=True)
                    res.add(max(buf_y[0][0], buf_f[0][0], key=lambda x: len(x)))
                # print("{} {} ---> ".format(i+1, devided_text[i]), end="")
                #! ErrorType, LineText, LineNumber, ОШИБКА, PrevLineText, NextLine
                for r in res:
                    r = "Неизвестная абревиатура "
                    prev_line, next_line = '', ''
                    for k in range(i-1, -1, -1):
                        if devided_text[k] != '':
                            prev_line = devided_text[k]
                            break
                    for k in range(i+1, len(devided_text)):
                        if devided_text[k] != '':
                            next_line = devided_text[k]
                            break
                    feedback_list.append(["АbbreviationError", devided_text[i], i+1, r, prev_line, next_line])
    #^--------------------------------------------------------------------------------------------------------------------           
    return feedback_list