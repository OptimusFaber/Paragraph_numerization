import re
from roman_numeral import *
import logging
import json

roman_numbers = 'IVXLCDM'

def parse(json_text, txt_path, log_path='myapp.log'):
   logging.basicConfig(filename=log_path, level=logging.DEBUG, 
      format=f'%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s func: %(funcName)s %(message)s \nText path: {txt_path}\n')
   logger=logging.getLogger(__name__)
   sign, data_type = 1, None
   res_dct = dict(zip([i['Name'] for i in json_text['Worksheets']], [[] for _ in range(len(json_text['Worksheets']))]))

   for sheet in json_text['Worksheets']:
      text = []
      for st in sheet['Rows']:
         text.append(st['Cells'][0])

      first_elements = {
         'number': {'.': '1', ')': '1', '()': '1', 'таблица': '1', 'рисунок': '1', 'рис': '1', 'схема': '1', 'приложение': '1', 'NaN': '1'}, 
         'ru_up_letter': {'.': 'А', ')': 'А', '()': 'А', 'таблица': 'А', 'рисунок': 'А', 'рис': 'А', 'приложение': 'А', 'схема': 'А'}, 
         'en_up_letter': {'.': 'A', ')': 'A', '()': 'A', 'таблица': 'A', 'рисунок': 'A', 'рис': 'A', 'приложение': 'A', 'схема': 'A'},
         'ru_low_letter': {'.': 'а', ')': 'а', '()': 'а', 'таблица': 'а', 'рисунок': 'а', 'рис': 'а', 'приложение': 'а', 'схема': 'а'},
         'en_low_letter': {'.': 'a', ')': 'a', '()': 'a', 'таблица': 'a', 'рисунок': 'a', 'рис': 'a', 'приложение': 'a', 'схема': 'a'},
         'roman': {'.': 'I', ')': 'I', '()': 'I', 'таблица': 'I', 'рисунок': 'I', 'рис': 'I', 'схема': 'I', 'приложение': 'I'},
      }
      for elem in text:
         try:
            txt = elem['Text']
            posix = elem['Address']
            list_findings = [[re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|((([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.]))", re.ASCII), txt), ".", None, None],
                            [re.search(re.compile(r"((?<=\s)|(?<=^))(((\d+[.])+\d+)|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), txt), ")", None, None],
                            [re.search(re.compile(r"(^|(?<=^\s)\s*)[Рр]исунок [№]?\d+", re.ASCII), txt), "рисунок", None, None],
                            [re.search(re.compile(r"(^|(?<=^\s)\s*)[Рр]ис[.]? [№]?\d+", re.ASCII), txt), "рис", None, None],
                            [re.search(re.compile(r"(^|(?<=^\s)\s*)[Сс]хема [№]?\d+", re.ASCII), txt), "схема", None, None],
                            [re.search(re.compile(r"(^|(?<=^\s)\s*)[Пп]риложение [№]?(\d+|[А-Яа-яA-Za-z]((?=\s)|(?=\w)))", re.ASCII), txt), "приложение", None, None],
                            [re.search(re.compile(r"((?<=\s)|(?<=^))[(]((\d+[.]?)+|([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]((?=\s)|(?=\w))", re.ASCII), txt), "()", None, None],
                            [re.search(re.compile(r"(^\d+((?=\s)|$))|((?<=^\s)\s*\d+((?=\s)|$))", re.ASCII), txt), "NaN", None, None],
                            [re.search(re.compile(r"((?<=\s)|(?<=^))[A-Za-zА-Яа-я][.](((\d+[.])+\d+)|(\d+))[.]*", re.ASCII), txt), ".", None, None]]

            list_findings = list(filter(lambda x: x[0] is not None, list_findings))
            if list_findings:
               list_findings = sorted(list(map(lambda x: [x[0], x[1], x[0].span()[0], x[0].span()[1]], list_findings)), key = lambda x: x[2])         
               posx = list_findings[0][2]
               list_findings = sorted(list(filter(lambda x: x[2] == posx, list_findings)), key = lambda x: x[3], reverse=True)
               sign = list_findings[0][1]
               pos = list_findings[0][3]
               delimetr = txt[0:list_findings[0][2]] if not re.search("[^\s]", txt[0:list_findings[0][2]]) else ""
            else:
               continue
            paragraph = list_findings[0][0].group()
            if re.search("\D.\d", paragraph):
               paragraph = re.sub(re.compile(r"\D[.]", re.ASCII), "", paragraph)
            paragraph = re.sub(r"^\s\s*", "", paragraph)
            if sign == "()":
               paragraph = paragraph[1:len(paragraph)-1]
            elif sign == ")":
               paragraph = paragraph[:-1]
            elif paragraph[-1] == "." and paragraph.count(".") == 1:
               paragraph = paragraph[:-1]
            elif sign != ".":
               paragraph = paragraph.split(" ")[-1].replace("№", "")
            elif sign == "":
               paragraph = re.sub("\t", "", paragraph)
            
            if paragraph == "п" and sign == ".":
               buf = re.search("(\d+[.]?)+", txt[pos:])
               if buf:
                  if buf.span()[0]-pos < 3:
                     continue

            #& Обработчик исключений для чисел
            error = False
            try:
               if paragraph[0] == '0':
                  error = True
               if paragraph[0].isdigit():
                  if '.' in paragraph:
                        for i in paragraph.split('.'):
                           if len(i) >= 3:
                              error = True
                              break
                           if i:
                              if i[0] == '0' and len(i) > 1:
                                 error = True
                                 break
               
                  if txt[pos-1] == '.' or txt[pos-1] == ')':
                     if not re.search("\s|[A-Za-zА-Яа-я]", txt[pos]):   
                        error = True

                  if txt[pos] == ' ':
                     if not re.search("\w|\s", txt[pos]):
                        error = True
            except:
                  pass
            
            if error:
               continue

            cut = txt[:pos][::-1]
            if sign == ')' and cut.count('(') == cut.count(')'):
               continue

            p=None
            if sign == ')':
               p = '(?<=[^А-Яа-яA-Za-z0-9])|^' + paragraph + '[)]'
            elif sign == '()':
               p = '[(]' + paragraph + '[)]'
            elif sign == '.':
               p = paragraph.replace('.', '[.]')
            else:
               p = txt[posx:pos]
            if sign in '.()':
               ##-----------------Отлавливаю тире справа-------------------
               tire = re.search('[-—–]', txt[re.search(p, txt).span()[1]:])
               if tire:
                  if tire.span()[0] < 2:
                     continue
               ##-----------------Отлавливаю тире слева-------------------
               tire = re.search('[-—–]', txt[:re.search(p, txt).span()[0]])
               if tire:
                  if tire.span()[0] < 2:
                     continue
               ##-----------------------------------------------------------

            pos1 = re.search(p, txt).span()[0]      

            pos0 = list(re.finditer('(п[.]|пункт|параграф|р[.]|раздел)', txt[:pos1]))
            if pos0:
               if pos1 - pos0[-1].span()[1] < 5:
                  continue

            if re.search("\w", txt[0:list_findings[0][2]]):
               continue 
               
            if all(i in roman_numbers for i in list(paragraph)):
               data_type = 'roman'
               elem = first_elements[data_type][sign]

               if Roman2Num(paragraph) - Roman2Num(elem) > 7:
                  continue 
               else:
                  first_elements[data_type][sign] = paragraph
            elif paragraph.isalpha():
               if 1040 <= ord(paragraph) <= 1103:
                  data_type = 'ru_up_letter' if paragraph.isupper() else 'ru_low_letter'
               else:
                  data_type = 'en_up_letter' if paragraph.isupper() else 'en_low_letter'

               elem = first_elements[data_type][sign]
               if ord(paragraph) - ord(elem) > 7:
                  continue 
               else:
                  first_elements[data_type][sign] = paragraph
            else:
               data_type = 'numbers' if (paragraph.split('.')[-1].isdigit() and len(paragraph.split('.')) > 1) or (len(paragraph.split('.')) > 2 and paragraph.split('.')[-1]=="") else 'number'
               if data_type == "number":
                  elem = first_elements[data_type][sign]
                  if int(paragraph) - int(elem) > 7:
                     continue 
                  else:
                     first_elements[data_type][sign] = paragraph
            paragraph = paragraph[:-1] if paragraph[-1] == '.' else paragraph
            pos = int(re.search('(?<=![A-Z])\d+', posix).group())
            res_dct[sheet['Name']].append((paragraph, sign, pos, data_type, delimetr, posix))
         except Exception as err:
            logger.error(err)

   return res_dct

