import re
import codecs

roman_numbers = 'IVXLCDM'

def parse(txt):
   counter = None
   lst = []

   sign = True
   counter = 0
   data_type = None 

   while txt and sign:
      list_findings = [[re.search(r"(((\W[a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.])|((\d)+[.])+", txt), ".", None, None],
                       [re.search(r"((\W[a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]", txt), ")", None, None],
                       [re.search(r"[Тт]аблица [№]?\d+", txt), "таблица", None, None],
                       [re.search(r"[Рр]исунок [№]?\d+", txt), "рисунок", None, None],
                       [re.search(r"[Рр]ис[.]? [№]?\d+", txt), "рис", None, None],
                       [re.search(r"[Сс]хема [№]?\d+", txt), "схема", None, None],
                       [re.search(r"[(](([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]", txt), "()", None, None]]
      
      list_findings = list(filter(lambda x: x[0] is not None, list_findings))

      if list_findings:
         for i in range(len(list_findings)):
            list_findings[i][2] = list_findings[i][0].span()[0]
            list_findings[i][3] = list_findings[i][0].span()[1]
         
         list_findings = sorted(list_findings, key = lambda x: x[2])
         sign = list_findings[0][1]
         if sign in ["таблица", "рисунок", "рис", "схема"]:
            pos = list_findings[0][3]-1
         else:
            pos = list_findings[0][3]-2
      else:
         sign = pos = None

      if sign:
         if not txt[pos].isdigit():
            idx = pos+1
            paragraph = txt[pos]
            if pos>0 and paragraph in roman_numbers:
               while txt[pos-1] in roman_numbers:
                  paragraph = txt[pos-1] + paragraph
                  pos -= 1
                  if pos < 0:
                     break
               if pos > 0:
                  if txt[pos-1].isalpha() and txt[pos-1] not in roman_numbers:
                     txt = txt[idx+1:]
                     counter+=(idx+1)
                     continue
         else:
            idx = pos + 1
            paragraph = txt[pos]
            while txt[pos - 1].isdigit() and pos>0:
                  paragraph = txt[pos - 1] + paragraph
                  if pos == 0:
                     break
                  pos -= 1
            pos = idx
            if txt[pos] == '.':
                  paragraph += '.'
                  pos_dot = pos
                  pos_digit = pos
                  idx = pos
                  while txt[pos + 1].isdigit() or txt[pos + 1] == '.':
                     paragraph += txt[pos + 1]
                     if txt[pos + 1].isdigit():
                        pos_digit = pos + 1
                        pos = pos_digit
                     else:
                        pos_dot = pos + 1
                        pos = pos_dot
                     
                  idx = pos
          
            # Обработчик исключений
            if txt[pos+1] == ')':    
               txt = txt[pos+2:]
               counter+=(pos+2)
               continue  
            if '.' in paragraph:
               date = False
               for i in paragraph.split('.'):
                  if len(i) >= 3:
                     txt = txt[pos_digit+1:]
                     counter+=(pos_digit+1)
                     date = True
                     break
                  if i:
                     if i[0] == '0' and len(i) > 1:
                        txt = txt[pos_digit+1:]
                        counter+=(pos_digit+1)
                        date = True
                        break

               if date:
                  continue

         if sign not in ["таблица", "рисунок", "рис", "схема"]:
            p=None
            if sign == ')':
               p = paragraph + '[)]'
            elif sign == '()':
               p = '[(]' + paragraph + '[)]'
            elif sign == '.':
               p = paragraph.replace('.', '[.]')
            pos1 = re.search(p, txt).span()[0]
            if pos1 >= 1 and lst:
               pos0 = re.findall('[\w!?()-]', txt[:pos1])
               pos0 = len(txt[:pos1])-txt[:pos1][::-1].index(pos0[-1]) if pos0 else 0 
               if not re.search('[\n\txt\r]|([.]\W+)|([:]\W+)|([,]\W+)', txt[pos0:pos1]):
                  txt = txt[idx+1:]
                  counter+=(idx+1)
                  continue  
            elif pos1 < 1 and lst:
               txt = txt[idx+1:]
               counter+=(idx+1)
               continue 
            if sign == '()' and paragraph.isdigit():
               if len(paragraph) >= 3:
                  txt = txt[idx+1:]
                  counter+=(idx+1)
                  continue    
         
         if paragraph in roman_numbers or all(i in roman_numbers for i in list(paragraph)):
            data_type = 'roman'
         elif paragraph.isalpha():
            if 1040 <= ord(paragraph) <= 1103:
               data_type = 'ru_up_letter' if paragraph.isupper() else 'ru_low_letter'
            else:
               data_type = 'en_up_letter' if paragraph.isupper() else 'en_low_letter'
         else:
            data_type = 'numbers' if (paragraph.split('.')[-1].isdigit() and len(paragraph.split('.')) > 1) or (len(paragraph.split('.')) > 2 and paragraph.split('.')[-1]=="") else 'number'
         
         if sign in ["таблица", "рисунок", "рис", "схема"]:
            paragraph = paragraph[:-1] if paragraph[-1] == '.' else paragraph
            txt = txt[pos+1:]
            lst.append((paragraph, sign, counter, data_type, delimetr))
            continue

         cut = txt[:idx+1][::-1]
         if sign == ')' and cut.count('(') == cut.count(')'):
            txt = txt[idx+1:]
            counter+=(idx+1)
            continue

         cut_pos_1 = re.search('[^\n\txt\r ' + paragraph + sign + ']', cut)
         if cut_pos_1:
            cut_pos_1 = cut_pos_1.span()[1]
         cut_pos_2 = re.search('[\n\txt\r ]', cut)
         if cut_pos_2:
            cut_pos_2 = cut_pos_2.span()[0]

         if cut_pos_2 is not None and cut_pos_1 is not None:
            delimetr = cut[cut_pos_2:cut_pos_1-1]
            if '.' in delimetr:
               delimetr = delimetr.replace('.', '')
            delimetr = delimetr[::-1]
            if '\n' in delimetr:
               delimetr = '\n' + ''.join(delimetr.split('\n')[-1])
            if '\r' in delimetr:
               delimetr = '\r' + ''.join(delimetr.split('\r')[-1])

         elif cut_pos_1:
            delimetr = ''
         elif cut_pos_2:
            delimetr = cut[cut_pos_2:-1]
            if '.' in delimetr:
               delimetr = delimetr.replace('.', '')
            
            delimetr = delimetr[::-1]

            if '\n' in delimetr:
               delimetr = '\n' + delimetr.split('\n')[-1]
            if '\r' in delimetr:
               delimetr = '\r' + delimetr.split('\r')[-1]
         txt = txt[idx+1:]
         counter+=(idx+1)
         paragraph = paragraph[:-1] if paragraph[-1] == '.' else paragraph
         lst.append((paragraph, sign, counter, data_type, delimetr))

   return lst