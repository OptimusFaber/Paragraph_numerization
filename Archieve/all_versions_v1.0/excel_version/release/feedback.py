def fb(dictonaries):
    if not dictonaries:
        return []
    feedback_list = []
    for dct in dictonaries:
        keys = list(dct.keys())
        for i in range(1, len(keys)):
            if dct[keys[i]]['status'] == 'MISSING' or dct[keys[i]]['status'] == 'DUPLICATE':
                feedback_list.append([dct[keys[i]]['name'], dct[keys[i]]['sign'], dct[keys[i]]['addinfo'], dct[keys[i]]['delimetr'], dct[keys[i]]['data_type'], dct[keys[i]]['status'], dct[keys[i]]['sup'], dct[keys[i]]['elem_name']])

    for i in range(len(feedback_list)):
        #! ErrorType, LineText, LineNumber, ОШИБКА, PrevLineText, NextLine
        text = "Отсутствует " if feedback_list[i][5] == "MISSING" else "Дублирующаяся " if feedback_list[i][1] == "таблица" or feedback_list[i][1] == "схема" else "Неверный " if feedback_list[i][5] == "INCORRECT" else "Дублирующийся "

        if feedback_list[i][1] == "()":
            elem = "(" + feedback_list[i][0]  + ")"
            feedback_list[i][3] = "(" + feedback_list[i][6]  + ")"
        elif feedback_list[i][1] == ")":
            elem = feedback_list[i][0]  + ")"
            feedback_list[i][3] = feedback_list[i][6]  + ")"
        elif feedback_list[i][1] == "." and feedback_list[i][4] != "numbers":
            elem = feedback_list[i][0]  + "."
            feedback_list[i][3] = feedback_list[i][6]  + "."
        else:
            elem = feedback_list[i][0]
            feedback_list[i][3] = feedback_list[i][7]

        if feedback_list[i][1] == "таблица" or feedback_list[i][1] == "схема" or feedback_list[i][1] == "приложение":
            feedback_list[i][0] = "Numbering"
            feedback_list[i][1] = text + elem
        elif feedback_list[i][1] == "рисунок" or feedback_list[i][1] == "рис":
            feedback_list[i][0] = "Numbering"
            feedback_list[i][1] = text + elem
        else:
            feedback_list[i][0] = "Numbering"
            feedback_list[i][1] = text + "параграф " + elem
        feedback_list[i] = feedback_list[i][:4]
    
    return feedback_list   