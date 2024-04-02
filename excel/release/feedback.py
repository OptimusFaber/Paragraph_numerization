def fb(dictonaries):
    if not dictonaries:
        return []
    feedback_list = []
    for dct in dictonaries:
        keys = list(dct.keys())
        for i in range(1, len(keys)):
            if dct[keys[i]]['status'] == 'MISSING' or dct[keys[i]]['status'] == 'DUPLICATE':
                feedback_list.append([dct[keys[i]]['name'], dct[keys[i]]['sign'], dct[keys[i]]['addinfo'], dct[keys[i]]['delimetr'], dct[keys[i]]['status']])

    for i in range(len(feedback_list)):
        #! ErrorType, LineText, LineNumber, ОШИБКА, PrevLineText, NextLine
        text = "Отсутствует " if feedback_list[i][4] == "MISSING" else "Дублирующаяся " if feedback_list[i][1] == "таблица" or feedback_list[i][1] == "схема" else "Дублирующийся "

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
            feedback_list[i][1] = text + feedback_list[i][3]
        elif feedback_list[i][1] == "рисунок" or feedback_list[i][1] == "рис":
            feedback_list[i][0] = "PictureErrorNumber"
            feedback_list[i][1] = text + feedback_list[i][3]
        else:
            feedback_list[i][0] = "TextErrorNumber"
            feedback_list[i][1] = text + "параграф " + feedback_list[i][3]
        feedback_list[i] = feedback_list[i][:3]
    
    return feedback_list   