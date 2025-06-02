
from typing import List, Dict
import re, os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
global_path = __file__
global_path = "/".join(global_path.split("/")[:-1])
sys.path.append(global_path)
from txt_utils import Text_processing
from utilities.logger import log_errors


class Parse_text(Text_processing):
    def __init__(self, error_path: str = None):
        super().__init__(error_path)
        # self.log_path = log_path

    @log_errors
    def start(self, json_text: str) -> List[Dict]:
        js = json_text['Worksheets']
        lst = dict(zip([i['Name'] for i in js], [[] for _ in range(len(js))]))
        self.sign, data_type = 1, None
        for n, entity in enumerate(js):
            self.sheet_info = entity
            entity = [i['Cells'][0] for i in entity['Rows']]
            for string in entity:
                self.txt_index = string['Address']
                self.cell_num = int(re.search('(?<=![A-Z])\d+', self.txt_index).group())
                self.txt = self._prepare_text(string)
                self.txt = self._clean_text(self.txt, 'text')

                f_elem = True
                begin = True
                while self.txt and self.sign:
                    self.txt = re.sub(r'\u00A0', ' ', self.txt)
                    while not (self.txt[0].isdigit() or self.txt[0].isalpha() or self.txt[0] == '('):
                        self.txt = self.txt[1:]
                        if self.txt == '':
                            break
                    list_findings = [
                        [re.search(self.PATTERNS['DOT'], self.txt), '.', None, None],
                        [re.search(self.PATTERNS['BRACKET'], self.txt), ')', None, None],
                        [re.search(self.PATTERNS['TABLE'], self.txt) if begin else None, 'таблица', None, None],
                        [re.search(self.PATTERNS['PICTURE'], self.txt) if begin else None, 'рисунок', None, None],
                        [re.search(self.PATTERNS['PIC'], self.txt) if begin else None, 'рис', None, None],
                        [re.search(self.PATTERNS['SCHEME'], self.txt) if begin else None, 'схема', None, None],
                        [re.search(self.PATTERNS['APPENDIX'], self.txt) if begin else None, 'приложение', None, None],
                        [re.search(self.PATTERNS['DOUBLE BRACKET'], self.txt), '()', None, None],
                        [re.search(self.PATTERNS['NAN'], self.txt), 'NaN', None, None],
                        [re.search(self.PATTERNS['DOT2'], self.txt), '.', None, None],
                    ]

                    begin = False 
                    list_findings = list(filter(lambda x: x[0] is not None, list_findings))
                    if list_findings:
                        list_findings = sorted(list(map(lambda x: [x[0], x[1], x[0].span()[0], x[0].span()[1]], list_findings)), key = lambda x: x[2])         
                        posx = list_findings[0][2]
                        list_findings = sorted(list(filter(lambda x: x[2] == posx, list_findings)), key = lambda x: x[3], reverse=True)
                        self.sign = list_findings[0][1]
                        self.pos = list_findings[0][3]
                    else:
                        break

                    if posx > 8:
                        break

                    name = list_findings[0][0].group()
                    name = self._clean_text(name, 'name')
                    promt = name.replace(')', '[)]').replace('(', '[(]').replace('.', '[.]')
                    if re.search(f'{promt}[.]', self.txt) and name[0].isdigit():
                        name+='.'

                    self.paragraph = list_findings[0][0].group()
                    self.paragraph = self._clean_text(self.paragraph, 'paragraph')
                    
                    if self.paragraph == "п" and self.sign == ".":
                        buf = re.search("(\d+[.]?)+", self.txt[self.pos:])
                        if buf:
                            if buf.span()[0]-self.pos < 3:
                                self.txt = self.txt[self.pos+buf.span()[1]:]
                                break

                    #&------------Обработчик исключений для чисел------------
                    try:
                        correct = self._is_valid_number(self.paragraph)
                        if not correct:
                            self.txt = self.txt[self.pos:]
                            break
                    except:
                        pass
                    #&-------------------------------------------------------
                    pattern=None
                    if self.sign == ')':
                        pattern = '(?<=[^А-Яа-яA-Za-z0-9])|^' + self.paragraph + '[)]'
                    elif self.sign == '()':
                        pattern = '[(]' + self.paragraph + '[)]'
                    elif self.sign == '.':
                        pattern = self.paragraph.replace('.', '[.]')
                    else:
                        pattern = self.txt[posx:self.pos]

                    if self.sign in '.()':
                        ##-----------------Отлавливаю тире справа-------------------
                        spawn = self.txt[re.search(pattern, self.txt).span()[1]:]
                        if self._defis_check(spawn):
                            self.txt = self.txt[self.pos:]
                            break
                        ##-----------------Отлавливаю тире слева-------------------
                        spawn = self.txt[:re.search(pattern, self.txt).span()[0]]
                        if self._defis_check(spawn):
                            self.txt = self.txt[self.pos:]
                            break
                        ##-----------------------------------------------------------

                    pos2 = re.search(pattern, self.txt).span()[0]

                    if pos2 >= 3 and lst and not f_elem:
                        pos1 = re.findall('[\w]', self.txt[:pos2])
                        pos1 = len(self.txt[:pos2])-self.txt[:pos2][::-1].index(pos1[-1]) if pos1 else 0 
                        if not re.search('([\t\r]+)|([.:!?;]\W+)', self.txt[pos1:pos2]):
                            try:
                                if ord(self.paragraph) - ord(lst[-1]) <= 3:
                                    pass
                            except:
                                self.txt = self.txt[self.pos:]
                                break  
                    
                    pos1 = list(re.finditer('(п[.]|пункт|параграф|р[.]|раздел)', self.txt[:pos2]))
                    if pos1:
                        if pos2 - pos1[-1].span()[1] < 5:
                            self.txt = self.txt[self.pos:]
                            break

                    if f_elem:
                        if re.search("\w", self.txt[0:list_findings[0][2]]):
                            break
                        f_elem = False   
                    ##-----------------Определяем тип данных-------------------
                    data_type = self._define_data_type()
                    if data_type is None:
                        self.txt = self.txt[self.pos:]
                        break
                    ##---------------------------------------------------------
                    self.txt = self.txt[self.pos:]
                    self.paragraph = self.paragraph[:-1] if self.paragraph[-1] == '.' else self.paragraph
                    fake_delimetr = 0

                    if self.paragraph[-1] == '1' and len(self.paragraph) >= 3:
                        s, l = add_info
                        s = s['Text']
                        for i in range(len(l)):
                            elem = l[i][0]
                            if l[i][0].group()[0].isdigit():
                                if elem.group()[0] == self.paragraph[0]:
                                    second_word_cords = [len(s.split(' ')[0]), len(s.split(' ')[0]) + len(s.split(' ')[1]) + 3]
                                    if second_word_cords[0] <= elem.span()[0] <= second_word_cords[1]:  
                                        prev_paragraph_name = elem.group()[0]
                                        prev_paragraph = self._clean_text(prev_paragraph_name, 'paragraph')
                                        cell_num = int(re.search('(?<=![A-Z])\d+', s['Address']).group())
                                        lst[self.sheet_info['Name']].append((prev_paragraph, self.sign, cell_num, data_type, fake_delimetr, prev_paragraph_name, s['Address']))
                                        break
                    lst[self.sheet_info['Name']].append((self.paragraph, self.sign, self.cell_num, data_type, fake_delimetr, name, self.txt_index))
                add_info = (string, list_findings)

        return lst
