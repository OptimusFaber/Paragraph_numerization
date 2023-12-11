import re
import codecs

roman_numbers = 'IVXLCDM'

def parse(file_path):
   counter = None
   lst = []

   sign = True
   counter = 0
   data_type = None 

   t = codecs.open(file_path, "r", "utf_8_sig")
   t = ''.join(t)
   t = ' ' + t

   while t and sign:
      list_findings = [[re.search(r"(((\W[a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.])|((\d)+[.])+", t), ".", None, None],
                       [re.search(r"((\W[a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]", t), ")", None, None],
                       [re.search(r"[Тт]аблица [№]?\d+", t), "таблица", None, None],
                       [re.search(r"[Рр]исунок [№]?\d+", t), "рисунок", None, None],
                       [re.search(r"[Рр]ис[.]? [№]?\d+", t), "рис", None, None],
                       [re.search(r"[Сс]хема [№]?\d+", t), "схема", None, None],
                       [re.search(r"[(](([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]", t), "()", None, None]]
      
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
         if not t[pos].isdigit():
            idx = pos+1
            paragraph = t[pos]
            if pos>0 and paragraph in roman_numbers:
               while t[pos-1] in roman_numbers:
                  paragraph = t[pos-1] + paragraph
                  pos -= 1
                  if pos < 0:
                     break
               if pos > 0:
                  if t[pos-1].isalpha() and t[pos-1] not in roman_numbers:
                     t = t[idx+1:]
                     counter+=(idx+1)
                     continue
         else:
            idx = pos + 1
            paragraph = t[pos]
            while t[pos - 1].isdigit() and pos>0:
                  paragraph = t[pos - 1] + paragraph
                  if pos == 0:
                     break
                  pos -= 1
            pos = idx
            if t[pos] == '.':
                  paragraph += '.'
                  pos_dot = pos
                  pos_digit = pos
                  idx = pos
                  while t[pos + 1].isdigit() or t[pos + 1] == '.':
                     paragraph += t[pos + 1]
                     if t[pos + 1].isdigit():
                        pos_digit = pos + 1
                        pos = pos_digit
                     else:
                        pos_dot = pos + 1
                        pos = pos_dot
                     
                  idx = pos
          
            # Обработчик исключений
            if t[pos+1] == ')':    
               t = t[pos+2:]
               counter+=(pos+2)
               continue  
            if '.' in paragraph:
               date = False
               for i in paragraph.split('.'):
                  if len(i) >= 3:
                     t = t[pos_digit+1:]
                     counter+=(pos_digit+1)
                     date = True
                     break
                  if i:
                     if i[0] == '0' and len(i) > 1:
                        t = t[pos_digit+1:]
                        counter+=(pos_digit+1)
                        date = True
                        break

               if date:
                  continue

         if sign in ["таблица", "рисунок", "рис", "схема"]:
            t = t[pos+1:]
            data_type = sign
            paragraph = paragraph[:-1] if paragraph[-1] == "." else paragraph

            lst.append((paragraph, None, counter, data_type, delimetr))
            continue

         p=None
         if sign == ')':
            p = paragraph + '[)]'
         elif sign == '()':
            p = '[(]' + paragraph + '[)]'
         else:
            p = paragraph.replace('.', '[.]')
         pos1 = re.search(p, t).span()[0]
         if pos1 >= 1 and lst:
            pos0 = re.findall('[\w!?()-]', t[:pos1])
            pos0 = len(t[:pos1])-t[:pos1][::-1].index(pos0[-1]) if pos0 else 0 
            if not re.search('[\n\t\r]|([.]\W+)|([:]\W+)|([,]\W+)', t[pos0:pos1]):
               t = t[idx+1:]
               counter+=(idx+1)
               continue  
         elif pos1 < 1 and lst:
            t = t[idx+1:]
            counter+=(idx+1)
            continue 
         if sign == '()' and paragraph.isdigit():
            if len(paragraph) >= 3:
               t = t[idx+1:]
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
         
         cut = t[:idx+1][::-1]
         if sign == ')' and cut.count('(') == cut.count(')'):
            t = t[idx+1:]
            counter+=(idx+1)
            continue

         cut_pos_1 = re.search('[^\n\t\r ' + paragraph + sign + ']', cut)
         if cut_pos_1:
            cut_pos_1 = cut_pos_1.span()[1]
         cut_pos_2 = re.search('[\n\t\r ]', cut)
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
         t = t[idx+1:]
         counter+=(idx+1)
         paragraph = paragraph[:-1] if paragraph[-1] == '.' else paragraph
         lst.append((paragraph, sign, counter, data_type, delimetr))

   return lst