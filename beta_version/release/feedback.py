import re

def fb(text, dictonaries):
    if not dictonaries:
        return []
    feedback_list = []
    for dct in dictonaries:
        keys = list(dct.keys())
        for i in range(1, len(keys)):
            if dct[keys[i]]['status'] == 'MISSING' or dct[keys[i]]['status'] == 'DUPLICATE' or dct[keys[i]]['status'] == 'INCORRECT':
                feedback_list.append([dct[keys[i]]['name'], dct[keys[i]]['sign'], dct[keys[i]]['pos'], dct[keys[i]]['delimetr'], dct[keys[i]]['data_type'], dct[keys[i]]['status']])

    splited_t = text.split("\n")
    for i in range(len(feedback_list)):
        ## Строка, в которой проблема
        n = feedback_list[i][2]
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
        text = "Отсутствует " if feedback_list[i][5] == "MISSING" else "Дублирующаяся " if feedback_list[i][1] == "таблица" or feedback_list[i][1] == "схема" else "Неверный " if feedback_list[i][5] == "INCORRECT" else "Дублирующийся "

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
            feedback_list[i][3] = text + feedback_list[i][3]
        elif feedback_list[i][1] == "рисунок" or feedback_list[i][1] == "рис":
            feedback_list[i][0] = "PictureErrorNumber"
            feedback_list[i][3] = text + feedback_list[i][3]
        else:
            feedback_list[i][0] = "TextErrorNumber"
            feedback_list[i][3] = text + "параграф " + feedback_list[i][3]
        feedback_list[i][1] = splited_t[n-1].replace("\r", "")
        feedback_list[i][2] = n
        feedback_list[i][4] = n_prev
        feedback_list[i][5] = n_next
    
    return feedback_list   