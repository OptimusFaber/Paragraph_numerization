import re
import codecs

roman_numbers = 'IVXLCDM'

def parse(file_path):
   counter = None
   lst = []

   sign = True
   counter = 0
   data_type = None 
   first_elem = True

   t = codecs.open(file_path, "r", "utf_8_sig")
   t = ''.join(t)
   t = ' ' + t

   while t and sign:
      dot = re.search(r"(((\W[a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[.])|((\d)+[.])+", t)
      bracket = re.search(r"((\W[a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]", t)
      double_bracket = re.search(r"[(](([a-zA-Zа-яА-Я])|(\d)+|([IVXLCDM])+)[)]", t)


      if dot and bracket and double_bracket:
         if bracket.span()[0] < dot.span()[0] and bracket.span()[0] < double_bracket.span()[0]:
            sign = ')'
         elif dot.span()[0] < bracket.span()[0] and dot.span()[0] < double_bracket.span()[0]:
            sign = '.'
         else:
            sign = '()'
         pos = min(bracket.span()[1]-2, dot.span()[1]-2, double_bracket.span()[1]-2)
      elif dot and bracket:
         sign = ')' if bracket.span()[0] < dot.span()[0] else '.'
         pos = min(bracket.span()[1]-2, dot.span()[1]-2)
      elif dot and double_bracket:
         sign = '()' if double_bracket.span()[0] < dot.span()[0] else '.'
         pos = min(double_bracket.span()[1]-2, dot.span()[1]-2)
      elif bracket and double_bracket:
         sign = '()' if double_bracket.span()[0] <= bracket.span()[0] else '.'
         pos = min(double_bracket.span()[1]-2, bracket.span()[1]-2)
      elif dot:
         sign = '.'
         pos = dot.span()[1]-2
      elif bracket:
         sign = ')'
         pos = bracket.span()[1]-2
      elif double_bracket:
         sign = '()'
         pos = double_bracket.span()[1]-2
      else:
         sign = None
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
               if paragraph.isupper():
                  data_type = 'ru_up_letter'
               else:
                  data_type = 'ru_low_letter'
            else:
               if paragraph.isupper():
                  data_type = 'en_up_letter'
               else:
                  data_type = 'en_low_letter'
         else:
            if (paragraph.split('.')[-1].isdigit() and len(paragraph.split('.')) > 1) or (len(paragraph.split('.')) > 2 and paragraph.split('.')[-1]==""):
               data_type = 'numbers'
            else:
               data_type = 'number'
         
         # if paragraph[-1] == '.' and paragraph.count('.') > 1:
         #    t = t[idx+1:]
         #    counter+=(idx+1)
         #    continue
         
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
      first_elem = False

   return lst