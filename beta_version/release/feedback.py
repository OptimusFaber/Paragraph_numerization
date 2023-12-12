import codecs
import re

def fb(dcts, file_path, new_file_path, correct_spelling=False):
    feedback_list = []
    for dct in dcts:
        keys = list(dct.keys())
        for i in range(1, len(keys)):
            if dct[keys[i]]['status'] == 'MISSING':
                feedback_list.append([dct[keys[i]]['name'], dct[keys[i]]['sign'], dct[keys[i]]['pos'], dct[keys[i]]['delimetr'], dct[keys[i]]['data_type']])

    t = codecs.open(file_path, "r", "utf_8_sig")
    t = ' ' + ''.join(t)
    t_copy = t
    splited_t = t.split("\n")
    buf = 0
    for k, i in zip(list(feedback_list), range(len(feedback_list))):
        if '.' in k[0]:
            text = k[0] + ' ' + 'Missing'
        else:
            if k[1]:
                if len(k[1]) == 1:
                    text = k[0] + k[1] + ' ' + 'Missing'
                else:
                    text = '(' + k[0] + ')' + ' ' + 'Missing'
            else:
                text = '(' + k[0] + ')' + ' ' + 'Missing'
        if k[4] == 'numbers':
            t = t[:k[2]+buf] + k[3] + text + t[k[2]+buf:]
        else:
            t = t[:k[2]+buf] + text + k[3] + t[k[2]+buf:]
        buf+=len(text)+len(k[3])

        ## Строка, в которой проблема
        n = t_copy[:k[2]].count("\n")+1
        ## Строки, которые стоят рядом
        n_prev, n_next = None, None
        for j in range(n-2, -1, -1):
            if re.search("(\w|[А-Яа-я])", splited_t[j]):
                n_prev = splited_t[j].replace("\r", "")
                break
        for j in range(n, len(splited_t)):
            if re.search("(\w|[А-Яа-я])", splited_t[j]):
                n_next = splited_t[j].replace("\r", "")
                break
        ##-----------------------------

        #! ErrorType, LineText, LineNumber, ОШИБКА, PrevLineText, NextLine
        if feedback_list[i][1] == "()":
            feedback_list[i][3] = "(" + feedback_list[i][0]  + ")"
        elif feedback_list[i][1] == ")":
            feedback_list[i][3] = feedback_list[i][0]  + ")"
        elif feedback_list[i][1] == "." and feedback_list[i][4] != "numbers":
            feedback_list[i][3] = feedback_list[i][0]  + "."
        else:
            feedback_list[i][3] = feedback_list[i][0]
        
        if feedback_list[i][1] == "таблица" or feedback_list[i][1] == "схема":
            feedback_list[i][0] = "TableErrorNumber"
            feedback_list[i][3] = "Отсутствует " + feedback_list[i][3]
        elif feedback_list[i][1] == "рисунок" or feedback_list[i][1] == "рис":
            feedback_list[i][0] = "PictureErrorNumber"
            feedback_list[i][3] = "Отсутствует " + feedback_list[i][3]
        else:
            feedback_list[i][0] = "TextErrorNumber"
            feedback_list[i][3] = "Отсутствует параграф " + feedback_list[i][3]
        feedback_list[i][1] = splited_t[n-1].replace("\r", "")
        feedback_list[i][2] = n
        feedback_list[i][4] = n_prev
        feedback_list[i].append(n_next)
        
    if correct_spelling:
        f = open(new_file_path, "w", encoding="utf-8")
        f.write(t)
        f.close()
        print('New file {} was saved'.format(new_file_path))
    
    return feedback_list   