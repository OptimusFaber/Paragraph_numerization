from difflib import SequenceMatcher
import json
import re

monthes = {1: "января",
           2: "февраля",
           3: "марта",
           4: "апреля",
           5: "мая",
           6: "июня",
           7: "июля",
           8: "августа",
           9: "сентября",
           10: "октября",
           11: "ноября",
           12: "декабря"}

def date_format(st):
    date = re.search(r"\d{1,2}[.]\d{1,2}[.]\d{4}", st)
    if date:
        date = date.group().split(".")
        day = int(date[0])
        month = monthes[int(date[1])]
        year = int(date[2])
        st = st.replace(".".join(date), "{} {} {}".format(day, month, year))
    return st

def compare_single_text(doc, cat, threshold=0.6):
    if doc is not None and cat is not None:
        #? Remove brackets
        doc = re.sub(r"[(].+[)]", "", doc)
        cat = re.sub(r"[(].+[)]", "", cat)
        #? ---------------
        #^ Working with Data
        doc = doc.replace("№", "N").replace("-", " ")
        doc = re.sub(r"\s", " ", doc)
        doc = re.sub(r"[^0-9A-Za-zА-Яа-я. ]", "", doc)
        cat = cat.replace("-", " ")
        cat = re.sub(r"\s", " ", cat)
        cat = re.sub(r"[^0-9A-Za-zА-Яа-я. ]", "", cat)
        #^ -----------------
        #! Change d.m.y format
        doc = date_format(doc)
        cat = date_format(cat)
        #! -------------------
        #& Check N and date
        N1 = re.search("(?<=N)[^\d]*\d+", doc)
        N2 = re.search("(?<=N)[^\d]*\d+", cat)
        if N1 is not None and N2 is not None:
            doc_N = re.sub("[^\d]", "", N1.group())
            cat_N = re.sub("[^\d]", "", N2.group())
            if doc_N != cat_N:
                # N не соответствует
                return "Number Error"
            doc_buf = doc.replace(doc_N, "")
            cat_buf = cat.replace(cat_N, "")
            doc_date = re.search("\d{1,2} [а-я]+ \d\d\d\d", doc_buf)
            cat_date = re.search("\d{1,2} [а-я]+ \d\d\d\d", cat_buf)

        elif N1 is not None:
            doc_N = re.sub("[^\d]", "", N1.group())
            doc_buf = doc.replace(doc_N, "")
            doc_date = re.search("\d{1,2} [а-я]+ \d\d\d\d", doc_buf)
            cat_date = re.search("\d{1,2} [а-я]+ \d\d\d\d", cat)
        
        elif N2 is not None:
            cat_N = re.sub("[^\d]", "", N2.group())
            cat_buf = cat.replace(cat_N, "")
            cat_date = re.search("\d{1,2} [а-я]+ \d\d\d\d", cat_buf)
            doc_date = re.search("\d{1,2} [а-я]+ \d\d\d\d", doc)
        
        else:
            doc_date = re.search("\d{1,2} [а-я]+ \d\d\d\d", doc)
            cat_date = re.search("\d{1,2} [а-я]+ \d\d\d\d", cat)

        if doc_date and cat_date:
            if doc_date.group() != cat_date.group():
                # Даты разные
                return "Date Error"

        #& ----------------
        if len(doc) > len(cat):
            ratio_list = [SequenceMatcher(None, cat, doc[i:len(cat)+i]).ratio() for i in range(len(doc)-len(cat)+1)]  
        elif len(doc) < len(cat):
            ratio_list = [SequenceMatcher(None, doc, cat[i:len(doc)+i]).ratio() for i in range(len(cat)-len(doc)+1)]
        else:
            ratio_list = [SequenceMatcher(None, cat, doc).ratio()]

        if all(num < threshold for num in ratio_list):
            # Предложения различаются по смыслу
            return "Sentence Error"
        else:
            # Предложения схожи по смыслу
            return True
    else:
        # Что-то не нашлось
        return "Sentence Error"