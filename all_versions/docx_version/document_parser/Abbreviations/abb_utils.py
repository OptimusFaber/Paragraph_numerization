import re, os, sys
from fuzzywuzzy import fuzz
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
global_path = __file__
global_path = "/".join(global_path.split("/")[:-1])
sys.path.append(global_path)
from utilities.logger import log_errors, logger

class Abbreviations_processing:
    def __init__(self, special_words=None, error_path: str = None):
        log_path = error_path.split('/')
        log_path = log_path[:-1] + [log_path[-1].split('.')[0] + '.log']
        log_path = '/'.join(log_path)
        self.log_path = log_path
        self.special_words = special_words or {
            "далее", "условное обозначение", "условные обозначения", 
            "сокращенное наименование", "сокращенные наименования"
        }
        self.abb_mask1 = re.compile(r"(?<![a-zA-Zа-яА-ЯЁё0-9-—–/])((«?([А-ЯЁ]+и)»?(\s|[/])?){2,}|(«?([А-ЯЁ]{2,})»?(\s|[/])?)+|(«?[A-Z]{2,}»?(\s|[/])?)+)([^ЁёА-Яа-яA-Za-z0-9-—–]|$)")
        self.abb_mask2 = None  # Will be set based on defis parameter
        self.abb_set = {}
    
    @logger
    def _setup_masks(self, defis):
        """Setup regex masks based on configuration"""
        if defis:
            self.abb_mask2 = re.compile(r"(?<![a-zA-Zа-яА-ЯЁё0-9-—–])(?<!-)(((([А-ЯЁ]+[а-яё-]*){2,})(\s|[/])?)+|((([A-Z]+[a-z]*){2,})(\s|[/])?)+)([^ЁёА-Яа-яA-Za-z0-9-—–]|$)")
        else:
            self.abb_mask2 = re.compile(r"(?<![a-zA-Zа-яА-ЯЁё0-9-—–])(?<!-)(((([А-ЯЁ]+[а-яё]*){2,})(\s|[/])?)+|((([A-Z]+[a-z]*){2,})(\s|[/])?)+)([^ЁёА-Яа-яA-Za-z0-9-—–]|$)")

    @logger
    def _clean_text(self, text):
        """Clean and normalize text"""
        text = text.replace(u'\xa0', u' ')
        text = re.sub(r'[\u2013\u2014]', '-', text)
        text = re.sub(r'\u00A0', ' ', text)
        return text
    
    @logger
    def _clean_abbreviation(self, abbr):
        """Clean and normalize potential abbreviation"""
        abbr = re.sub("[\t\n\r]", " ", abbr)
        abbr = re.sub("[ ]{2,}", " ", abbr)
        
        # Clean start and end
        for _ in range(2):
            if not abbr[-1].isalpha() and abbr[-1] != "»":
                abbr = abbr[:-1]
            if not abbr[0].isalpha() and abbr[0] != "«":
                abbr = abbr[1:]
                
        # Handle quotes
        # if abbr.count("«") == 1 and abbr.count("»") == 0:
        #     abbr += "»"
        # if abbr.count("«") == 0 and abbr.count("»") == 1:
        #     abbr = "«" + abbr
        if abbr[-1] == "»" and abbr.count("«") == 0:
            abbr = abbr[:-1]
        if abbr[0] == "«" and abbr.count("»") == 0:
            abbr = abbr[1:]
            
        return abbr
    
    @logger
    def _check_dash_pattern(self, text, dash_pos, abbr, abbr_pos, side):
        if side == 'right':
            right_side = text[abbr_pos:][dash_pos:].replace(')', '').replace('(', '').split(" ")
            right_side = self._letter_extractor(right_side, 0)
            line = ""
            st = False
            elemx = abbr.upper().replace(' ', '')
            for rig in right_side:
                line += rig
                if fuzz.token_sort_ratio(line, elemx) > 75:
                    st = True
                    break
                if len(line) - len(elemx) > 4:
                    break
            if st:
                return True
        if side == 'left':
            left_side = text[abbr_pos-1::-1][dash_pos:].replace(')', '').replace('(', '').split(" ")
            left_side = list(map(lambda x: x[::-1], left_side))
            left_side = self._letter_extractor(left_side, 0)
            line = ""
            st = False
            elemx = abbr.upper().replace(' ', '')
            for lef in left_side:
                line = lef + line
                if fuzz.token_sort_ratio(line, elemx) > 75:
                    st = True
                    break
                if len(line) - len(elemx) > 4:
                    break
            if st:
                return True
        return False
    
    @logger
    def _letter_extractor(self, string, ind):
        line = []
        for st in string:
            if len(st) > 1 or st == 'и':
                for s in range(len(st)-1, -1, -1):
                    if st[s].isupper() or s == ind:
                        line.append(st[s].upper())
        return line  
