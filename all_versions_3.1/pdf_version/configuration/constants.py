from dataclasses import dataclass
import re
from utilities.roman_numeral import *

@dataclass(frozen=True)
class DocumentConfig:
    # Regex patterns
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
    
    # Special words and phrases
    SPECIAL_WORDS = {
        "далее",
        "условное обозначение",
        "условные обозначения", 
        "сокращенное наименование", 
        "сокращенные наименования"
    }

    ABBREVIATION_PATTERNS = {
        'BASIC': re.compile(r"(?<![a-zA-Zа-яА-ЯЁё0-9-—–/])((«?([А-ЯЁ]+и)»?(\s|[/])?){2,}|(«?([А-ЯЁ]{2,})»?(\s|[/])?)+|(«?[A-Z]{2,}»?(\s|[/])?)+)([^ЁёА-Яа-яA-Za-z0-9-—–]|$)"),
        'WITH_HYPHEN': re.compile(r"(?<![a-zA-Zа-яА-ЯЁё0-9-—–])(?<!-)(((([А-ЯЁ]+[а-яё-]*){2,})(\s|[/])?)+|((([A-Z]+[a-z]*){2,})(\s|[/])?)+)([^ЁёА-Яа-яA-Za-z0-9-—–]|$)"),
        'WITHOUT_HYPHEN': re.compile(r"(?<![a-zA-Zа-яА-ЯЁё0-9-—–])(?<!-)(((([А-ЯЁ]+[а-яё]*){2,})(\s|[/])?)+|((([A-Z]+[a-z]*){2,})(\s|[/])?)+)([^ЁёА-Яа-яA-Za-z0-9-—–]|$)")
    }

    ABBREVIATION_CONFIG = {
        'MIN_LENGTH': 2,
        'MAX_LENGTH': 10,
        'SIMILARITY_THRESHOLD': 75,
        'MAX_DISTANCE': 4
    }
    
    # Number types and their properties
    NUMBER_TYPES = {
        'decimal': {'pattern': r'\d+', 'max_sequence': 7},
        'roman': {'pattern': r'[IVXLCDM]+', 'max_sequence': 7},
        'letter': {'pattern': r'[a-zA-Zа-яА-Я]', 'max_sequence': 3}
    }

    TREE_CONFIG = {
        'LETTER_SEARCH': -30,
        'NUMBER_SEARCH': 70,
        'NON_TEXT_SEARCH': -80,
        'NUM_PARAGRAPH_SEARCH': 70,
        'DUPLICATE': 0,
        'SPECIAL_SIGNS': {"таблица", "рисунок", "рис", "схема", "приложение"}
    }

    FUNCTIONS = {
        'number': [int, str], 
        'ru_up_letter': [ord, chr], 
        'en_up_letter': [ord, chr], 
        'ru_low_letter': [ord, chr], 
        'en_low_letter': [ord, chr], 
        'roman': [Roman2Num, Num2Roman]
    }

    FIRST_ELEMENTS = {
        'number': '1', 
        'ru_up_letter': 'А', 
        'en_up_letter': 'A', 
        'ru_low_letter': 'а', 
        'en_low_letter': 'a', 
        'roman': 'I'
    }



CONFIG = DocumentConfig()