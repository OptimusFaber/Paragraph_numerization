import re
import os, sys
from typing import Dict, List, Tuple
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
global_path = __file__
global_path = "/".join(global_path.split("/")[:-1])
sys.path.append(global_path)
from utilities.roman_numeral import Roman2Num
from utilities.logger import log_errors, logger

# Constants
ROMAN_NUMBERS = 'IVXLCDM'
FIRST_ELEMENTS = {
      'number': {'.': '1', ')': '1', '()': '1', 'таблица': '1', 'рисунок': '1', 'рис': '1', 'схема': '1', 'приложение': '1', 'NaN': '1'}, 
      'ru_up_letter': {'.': 'А', ')': 'А', '()': 'А', 'таблица': 'А', 'рисунок': 'А', 'рис': 'А', 'приложение': 'А', 'схема': 'А'}, 
      'en_up_letter': {'.': 'A', ')': 'A', '()': 'A', 'таблица': 'A', 'рисунок': 'A', 'рис': 'A', 'приложение': 'A', 'схема': 'A'},
      'ru_low_letter': {'.': 'а', ')': 'а', '()': 'а', 'таблица': 'а', 'рисунок': 'а', 'рис': 'а', 'приложение': 'а', 'схема': 'а'},
      'en_low_letter': {'.': 'a', ')': 'a', '()': 'a', 'таблица': 'a', 'рисунок': 'a', 'рис': 'a', 'приложение': 'a', 'схема': 'a'},
      'roman': {'.': 'I', ')': 'I', '()': 'I', 'таблица': 'I', 'рисунок': 'I', 'рис': 'I', 'схема': 'I', 'приложение': 'I'},
   }
PATTERNS = {
        'DOT': re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|((([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.]))", re.ASCII),
        'BRACKET': re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII),
        'TABLE': re.compile(r"(^|(?<=^\s)\s*)[Тт]аблица [№]?\d+([.]\d+)*", re.ASCII),
        'PICTURE': re.compile(r"(^|(?<=^\s)\s*)[Рр]исунок [№]?\d+([.]\d+)*", re.ASCII),
        "PIC": re.compile(r"(^|(?<=^\s)\s*)[Рр]ис[.]? [№]?\d+([.]\d+)*", re.ASCII),
        "SCHEME": re.compile(r"(^|(?<=^\s)\s*)[Сс]хема [№]?\d+([.]\d+)*", re.ASCII),
        "APPENDIX": re.compile(r"(^|(?<=^\s)\s*)[Пп]риложение [№]?(\d+([.]\d+)*|[А-Яа-яA-Za-z]((?=\s)|(?=\w)))", re.ASCII),
        "DOUBLE BRACKET": re.compile(r"((?<=\s)|(?<=^))[(]((\d+[.]?)+|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII),
        "NAN": re.compile(r"(^\d+)|((?<=^\s)\s*\d+)", re.ASCII),
        "DOT2": re.compile(r"((?<=\s)|(?<=^))[A-Za-zА-Яа-я][.](((\d+[.])+\d+)|(\d+))[.]*", re.ASCII),
    }

class Text_processing:
    def __init__(self, error_path: str = None):
        self.error_path = error_path
        log_path = error_path.split('/')
        log_path = log_path[:-1] + [log_path[-1].split('.')[0] + '.log']
        log_path = '/'.join(log_path)
        self.log_path = log_path
        self.ROMAN_NUMBERS = ROMAN_NUMBERS
        self.FIRST_ELEMENTS = FIRST_ELEMENTS
        self.PATTERNS = PATTERNS
        self.txt = None
        self.paragraph = None
        self.pos = None
        self.sign = None

    @logger
    def _extract_paragraphs(self, text: Dict) -> Tuple[List, List]:
        """Extract paragraphs and tables from text."""
        js = []
        lst = []
        
        # Handle regular paragraphs
        if 'Paragraphs' in text:
            js.append(text['Paragraphs'])
            lst.append([])
        
        # Handle tables
        if 'Tables' in text:
            for table in text['Tables']:
                table_paragraphs = [
                    cell['Cells'][0]["Paragraphs"][j]
                    for cell in table['Rows']
                    for j in range(len(cell['Cells'][0]["Paragraphs"]))
                ]
                js.append(table_paragraphs)
                lst.append([])
        
        return js, lst

    @logger
    def _is_valid_number(self, txt = None) -> bool:
        """Validate number format."""
        if self.paragraph[0] == '0':
            return False
            
        if self.paragraph[0].isdigit():
            if '.' in txt:
                for i in txt.split('.'):
                    if not i:
                        continue
                    if len(i) >= 3 or (i[0] == '0' and len(i) > 1):
                        return False
        
        if txt is not None:
            if txt[self.pos-1] == '.' or txt[self.pos-1] == ')':
                if not re.search("\s|[A-Za-zА-Яа-я]", txt[self.pos]):   
                    return False

            if txt[self.pos] == ' ':
                if not re.search("\w|\s", txt[self.pos]):
                    return False
                
            cut = txt[:self.pos][::-1]
            if self.sign == ')' and cut.count('(') == cut.count(')'):
                return False
        
        return True

    @logger
    def _should_skip_string(self, string: Dict) -> bool:
        """Determine if string should be skipped."""
        if string["IsToc"] and not string["Numbering"]:
            if not re.search(r"(^|(?<=^\s)\s*)[Тт]аблица [№]?\d+", string["Text"]):
                return True
        return string.get('Vanish', False)

    @logger
    def _prepare_text(self, string: Dict) -> str:
        """Prepare text for processing."""
        self.txt = string["Text"]
        if string["Numbering"]:
            self.txt = string["Numbering"] + ' ' + self.txt
        return self.txt

    @logger
    def _clean_text(self, string, type):
        """Clean and normalize text"""
        if type == 'text':
            string = string.replace(u'\xa0', u' ')
            string = re.sub(r'\u00A0', ' ', string)
        elif type == 'name':
            while re.search('\s', string[0]):
                string = string[1:]
            while re.search('\s', string[-1]):
                string = string[:-1]
        elif type == 'paragraph':
            if re.search("\D.\d", string):
                string = re.sub(re.compile(r"\D[.]", re.ASCII), "", string)
            string = re.sub(r"^\s\s*", "", string)
            if self.sign == "()":
                string = string[1:len(string)-1]
            elif self.sign == ")":
                string = string[:-1]
            elif string[-1] == "." and string.count(".") == 1:
                string = string[:-1]
            elif self.sign != ".":
                string = string.split(" ")[-1].replace("№", "")
            elif self.sign == "":
                string = re.sub("\t", "", string)
        return string
    
    @logger
    def _defis_check(self, string):
        """Check for dash."""
        defis = re.search('[-—–]', string)
        if defis:
            if defis.span()[0] < 2:
                return True
        return False
    
    @logger
    def _define_data_type(self):
        """Define data type."""
        if all(i in ROMAN_NUMBERS for i in list(self.paragraph)):
            data_type = 'roman'
            elem = FIRST_ELEMENTS[data_type][self.sign]

            if Roman2Num(self.paragraph) - Roman2Num(elem) > 7:
                return None
            else:
                FIRST_ELEMENTS[data_type][self.sign] = self.paragraph
        elif self.paragraph.isalpha():
            if 1040 <= ord(self.paragraph) <= 1103:
                data_type = 'ru_up_letter' if self.paragraph.isupper() else 'ru_low_letter'
            else:
                data_type = 'en_up_letter' if self.paragraph.isupper() else 'en_low_letter'

            elem = FIRST_ELEMENTS[data_type][self.sign]
            if ord(self.paragraph) - ord(elem) > 7:
                return None
            else:
                FIRST_ELEMENTS[data_type][self.sign] = self.paragraph
        else:
            data_type = 'numbers' if (self.paragraph.split('.')[-1].isdigit() and len(self.paragraph.split('.')) > 1) or (len(self.paragraph.split('.')) > 2 and self.paragraph.split('.')[-1]=="") else 'number'
            if data_type == "number":
                elem = FIRST_ELEMENTS[data_type][self.sign]
                if int(self.paragraph) - int(elem) > 7:
                    return None
                else:
                    FIRST_ELEMENTS[data_type][self.sign] = self.paragraph
                    
        return data_type
        

