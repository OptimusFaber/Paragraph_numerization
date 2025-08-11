import re, sys, os
from fuzzywuzzy import fuzz
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
global_path = __file__
global_path = "/".join(global_path.split("/")[:-1])
sys.path.append(global_path)
from abb_utils import Abbreviations_processing
from utilities.logger import log_errors, logger
        
class Abb_finder(Abbreviations_processing):
    def __init__(self, special_words: set = None, error_path: str = None):
        super().__init__(special_words=special_words, error_path=error_path)
        self.error_path = error_path
        self.all_words = ""
        self.parsed_text = []
        self.buf_of_added = []
        self.list_of_added_elems = []
        self.abb_set = dict()
        self.abb1 = re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|((([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.]))", re.ASCII)
        self.abb2 = re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII)
        self.abb3 = re.compile(r"((?<=\s)|(?<=^))[(]((\d+[.]?)+|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII)

    @log_errors
    def abb_table_search(self, text: str):
        con = con_end = c = 0
        tables, pos = [], []
        flag = True
        for elem in text.keys():
            if elem == 'Paragraphs':
                self.parsed_text.append(text[elem])
                for e in text[elem]:
                    self.all_words += re.sub("[^A-Za-zА-Яа-яЁё\s]", "", e["Text"]) + " "
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
                                flag=False
                            list_findings = [re.search(self.abb1, e['Text']) != None,
                                             re.search(self.abb2, e['Text']) != None,
                                             re.search(self.abb3, e['Text']) != None]
                            if any(list_findings):
                                c = 0
                                continue
                            else:
                                c += 1

            elif elem == 'Tables':
                prev_table_last_cell_index = 0
                for table in text[elem]:
                    cell_index = 0
                    buf = []
                    for cell in table['Rows']:
                        for n in range(len(cell['Cells'])):
                            for m in range(len(cell['Cells'][n]["Paragraphs"])):
                                buf.append(cell['Cells'][n]["Paragraphs"][m])
                                self.all_words += re.sub("[^A-Za-zА-Яа-яЁё\s]", "", cell['Cells'][n]["Paragraphs"][m]["Text"]) + " "
                                cell_index = cell['Cells'][n]["Paragraphs"][m]['Index']

                    self.parsed_text.append(buf)
                    num = table['Index']
                    for p in pos:
                        if (0 < num - p < 5) or (0 < num - prev_table_last_cell_index < 5):
                            prev_table_last_cell_index = cell_index
                            tables.append(table)
                            break
                        
        
        return tables

    @log_errors
    def abb_table_parser(self, tables):
        for tab in tables:
            for row in tab['Rows']:
                for cell in row['Cells']:
                    txt = self._clean_text(cell['Paragraphs'][0]['Text'])
                    f1 = re.search(self.abb_mask1, txt)
                    f2 = re.search(self.abb_mask2, txt)
                    if f1 and f2:
                        f = f1 if (len(f1.group()) > len(f2.group())) else f2
                    elif f1 or f2:
                        f = f1 if f1 else f2
                        f = f if f.span()[0] < 7 else None
                    else:
                        f = None
                    if f:
                        f = self._clean_abbreviation(f.group())
                        if not self.abb_set.get(f):
                            self.abb_set[f] = cell['Paragraphs'][0]['Index']
                    break
    
    @log_errors
    def abb_finder(self, clean_text, index):
        f = [re.finditer(self.abb_mask1, clean_text), re.finditer(self.abb_mask2, clean_text)]
        #^------------------------------------------------------------------------------------
        self.list_of_added_elems = []
        for itter in f:       
            for element in itter:
                if element:
                    elem = element.group()
                    elem = self._clean_abbreviation(elem)
                    if elem[0] == "«" and elem[-1] == "»":
                        elem_without_quotes = elem[1:-1]
                    else:
                        elem_without_quotes = None
                    #! Проверяем что это не римская цифра
                    if bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", elem)) and elem != "CD":
                        continue
                    #! ----------------------------------
                    status = False 
                    ##----------------------------
                    if elem in self.buf_of_added:
                        continue
                    ##----------------------------
                    #! Проверяем нет ли нашего элемента в словаре
                    if elem in list(self.abb_set.keys()):
                        if self.abb_set[elem] <= index:
                            # d = re.search(elem, element.group()).span()
                            d = element.span()
                            self.list_of_added_elems.extend(range(element.span()[0]+d[0], element.span()[0]+d[1]))
                            continue
                    #! Делаем то же самое для варианта без ковычек
                    if elem_without_quotes is not None:
                        if elem_without_quotes in list(self.abb_set.keys()):
                            if self.abb_set[elem_without_quotes] <= index:
                                d = elem_without_quotes.span()
                                self.list_of_added_elems.extend(range(elem_without_quotes.span()[0]+d[0], elem_without_quotes.span()[0]+d[1]))
                                continue
                    #! -------------------------------------------
                    if all(list(map(lambda x: 1<len(x)<11, elem.split(" ")))):
                        #?Убираем параграф если он весь написан большими буквами
                        if clean_text.isupper():
                            continue
                        
                        status = False
                        exp = elem.split(" ")
                        for i in range(len(exp)):
                            if len(exp[i])>=9 and not any(k.islower() for k in exp[i]):
                                status = True
                                break
                            if exp[i].lower() in self.all_words:
                                status = True
                                break
                        if status: continue
                            
                        if element.span()[0] in self.list_of_added_elems or element.span()[1] in self.list_of_added_elems:
                            continue

                        dash_right = re.search(r"^[\t ]*[-—–]", clean_text[element.span()[1]:])         #* Ситуация типа ООО - ...
                        dash_left = re.search(r"^[\t ]*[-—–]", clean_text[:element.span()[0]][::-1])   #* Ситуацтя типа ... - ООО

                        if dash_right:
                            if self._check_dash_pattern(clean_text, dash_right.span()[0], elem, element.span()[1], 'right'):
                                self.abb_set[elem] = index
                                continue
                        if dash_left:
                            if self._check_dash_pattern(clean_text, dash_left.span()[0], elem, element.span()[0], 'left'):
                                self.abb_set[elem] = index
                                continue

                        if ")" in clean_text[element.span()[1]-1:min(element.span()[1]+20, len(clean_text))] and "(" in clean_text[max(element.span()[0]-20, 0):element.span()[0]]:
                            ## Единая система конструкторской документации (ЕСКД) тут лишь слева
                            left_side_ind = len(clean_text[element.span()[1]-2::-1]) - re.search("[(]", clean_text[element.span()[1]-2::-1]).span()[0]
                            bracket_info = clean_text[left_side_ind:element.span()[1]-1]
                            ## Смотрим есть ли перед аббревиатурой спец слово
                            for word in self.special_words:
                                if word in bracket_info:
                                    status = True
                                    break
                            if status:
                                if not self.abb_set.get(elem):
                                    self.abb_set[elem] = index
                                else:
                                    if index < self.abb_set[elem]:
                                        self.abb_set[elem] = index
                                continue
                            ## (ЕСКД)
                            if re.search(f"[(]\t*{elem}\t*[)]", clean_text):
                                if not self.abb_set.get(elem):
                                    self.abb_set[elem] = index
                                else:
                                    if index < self.abb_set[elem]:
                                        self.abb_set[elem] = index
                                continue

                            bracket_info = re.search(f"[(][^()]*{elem}[^()]*[)]", clean_text)
                            if bracket_info:
                                pos = bracket_info.span()
                                bracket_info = bracket_info.group().replace('(', '').replace(')', '').replace(elem, '')
                                bracket_info = bracket_info.split(' ')
                                bracket_info = list(filter(lambda x: len(x)>1, bracket_info))
                                bracket_info = list(map(lambda x: x.upper(), list(map(lambda x: x[0], bracket_info))))
                                elemx = elem + ''.join(bracket_info)
                                left_side = clean_text[:pos[0]][::-1].replace('(', '').replace(')', '').replace('«', '').replace('»', '').split(" ")
                                left_side = list(map(lambda x: x[::-1], left_side))
                                left_side = self._letter_extractor(left_side, 0)
                                line = ""
                                status = False
                                elemx = elemx.upper()
                                for lef in left_side:
                                    line = lef.upper() + line
                                    if fuzz.token_sort_ratio(line, elemx) > 75:
                                        status = True
                                        break
                                    if len(line) - len(elemx) > 4:
                                        break
                                if status:
                                    self.abb_set[elem] = index
                                    continue

                                right_side = clean_text[pos[1]:].split(" ")
                                right_side = self._letter_extractor(right_side, 0)
                                line = ""
                                status = False
                                for rig in right_side:
                                    line += rig.upper()
                                    if fuzz.token_sort_ratio(line, elemx) > 75:
                                        status = True
                                        break
                                    if len(line) - len(elemx) > 4:
                                        break
                                if status:
                                    self.abb_set[elem] = index
                                    continue

                        flag = False
                        g = elem
                        if len(elem.split(" ")) > 1:
                            elem1 = elem.split(' ')
                            elem = []
                            a = ''
                            for e in range(len(elem1)):
                                a += elem1[e] + ' '
                                if a[:-1] in list(self.abb_set.keys()):
                                    if self.abb_set[a[:-1]] <= index:
                                        flag = True
                                        elem = []
                                    else:
                                        elem.append(elem1[e])
                                elif elem1[e] in list(self.abb_set.keys()):
                                    if self.abb_set[elem1[e]] <= index:
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
                            self.buf_of_added.append((elem, (element.span()[0]+d[0], element.span()[0]+d[1])))
                            status = True
                        else:
                            for e in elem:
                                self.buf_of_added.append((elem, element.span()))
                                status = True

    @log_errors
    def abb_extractor(self, orig_text, index):

        self.buf_of_added.sort(key=lambda x: len(x[0]), reverse=True)

        # Удаляем пересекающиеся элементы
        res = set()
        for name, (start, end) in self.buf_of_added:
            overlap = False
            for _, (s, e) in res:
                # Проверка на пересечение
                if not (end <= s or start >= e):
                    overlap = True
                    break
            if not overlap:
                res.add((name, (start, end)))
                
        #! ErrorType, LineText, LineNumber, ОШИБКА, PrevLineText, NextLine
        for r, _ in res:
            sentence = f"Неизвестная аббревиатура «{r}»"
            if len(r.split(' ')) > 1:
                if r not in orig_text:
                    mask = r''
                    mask = r.split(' ')
                    mask = '.'.join(mask)
                    r = re.search(mask, orig_text, re.DOTALL).group()
            self.feedback_list.append(["Abbreviation", sentence, index, r])

    @log_errors
    def start(self, text, abbs=True, add_info=None, defis=False, new_format=0):
        if not abbs:
            return []
        #& Маски для поиска нужных нам сокращений
        self._setup_masks(defis)
        
        tables = self.abb_table_search(text)
        self.all_words = {word.lower() for word in self._clean_text(self.all_words).split() if len(word) > 1 and any(i.islower() for i in word[1:])}
        self.abb_table_parser(tables)
         
        #* Дополняем словари если нужно
        if add_info:
            if not new_format:
                if "Abbreviation" in add_info.keys():
                    for elem in add_info["Abbreviation"]:
                        self.abb_set[elem["Value"]] = 0
            else:
                if "Abbreviations" in add_info.keys():
                    for elem in add_info["Abbreviations"]:
                        self.abb_set[elem] = 0

        forbidden_list = list(self.abb_set.values())

        #^ Поиск сокращений в нашем тексте
        self.feedback_list = []
        for part in self.parsed_text:
            for string in part:
                self.buf_of_added = []
                orig_text = string['Text']
                index = string['Index']
                clean_text = self._clean_text(string['Text'])
                if index not in forbidden_list and not string['IsToc']:
                    ## Поиск аббревиатур в строке
                    self.abb_finder(clean_text, index)
                    
                if self.buf_of_added:
                    ## Обработка найденных аббревиатур
                    self.abb_extractor(orig_text, index)
        #^--------------------------------------------------------------------------------------------------------------------
        return self.feedback_list