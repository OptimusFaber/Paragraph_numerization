
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
    def start(self, text: str) -> List[Dict]:
        js, lst = self._extract_paragraphs(text)
        self.sign, counter, data_type = 1, 0, None
        for n, entity in enumerate(js):
            for string in entity:
                if self._should_skip_string(string):
                    # counter += len(string['Text'])
                    continue
                lines = self._prepare_text(string)
                lines = self._clean_text(lines, 'text')
                lines = lines.split('\n')
                counter = 0
                
                for self.txt in lines:
                    f_elem = True
                    begin = True
                    while self.txt and self.sign:
                        while not (self.txt[0].isdigit() or self.txt[0].isalpha() or self.txt[0] == '('):
                            self.txt = self.txt[1:]
                            counter+=1
                            if self.txt == '':
                                break
                        if self.txt == '':
                            counter+=1
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
                            posy = list_findings[0][3]
                            list_findings = sorted(list(filter(lambda x: x[2] == posx, list_findings)), key = lambda x: x[3], reverse=True)
                            self.sign = list_findings[0][1]
                            self.pos = list_findings[0][3]
                        else:
                            counter+=len(self.txt)+1
                            break

                        if posx > 8:
                            counter+=len(self.txt)+1
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
                                    counter+=(self.pos+buf.span()[1])
                                    continue

                        #&------------Обработчик исключений для чисел------------
                        try:
                            correct = self._is_valid_number(self.paragraph)
                            if not correct:
                                self.txt = self.txt[self.pos:]
                                counter+=(self.pos)
                                continue
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
                                counter+=(self.pos)
                                continue
                            ##-----------------Отлавливаю тире слева-------------------
                            spawn = self.txt[:re.search(pattern, self.txt).span()[0]]
                            if self._defis_check(spawn):
                                self.txt = self.txt[self.pos:]
                                counter+=(self.pos)
                                continue
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
                                    counter+=(self.pos)
                                    continue  
                        
                        pos1 = list(re.finditer('(п[.]|пункт|параграф|р[.]|раздел)', self.txt[:pos2]))
                        if pos1:
                            if pos2 - pos1[-1].span()[1] < 5:
                                self.txt = self.txt[self.pos:]
                                counter+=(self.pos)
                                continue

                        if f_elem:
                            if re.search("\w", self.txt[0:list_findings[0][2]]):
                                counter+=len(self.txt)+1
                                break
                            f_elem = False   
                        ##-----------------Определяем тип данных-------------------
                        data_type = self._define_data_type()
                        if data_type is None:
                            self.txt = self.txt[self.pos:]
                            counter+=(self.pos)
                            continue
                        ##---------------------------------------------------------
                        self.txt = self.txt[self.pos:]
                        
                        self.paragraph = self.paragraph[:-1] if self.paragraph[-1] == '.' else self.paragraph
                        lst[n].append((self.paragraph, self.sign, string["Index"], data_type, (counter+posx, counter+posy), name))
                        counter+=(self.pos)
                        if self.txt == "":
                            counter+=1

        return lst
