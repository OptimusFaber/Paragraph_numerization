import re

roman_numbers = 'IVXLCDM'

def parse(file_path):
   lst = []

   sign = True
   counter = 0
   data_type = None 
   first_elem = True

   t = open(file_path).readlines()
   t = ''.join(t)
   t = ' ' + t

   while t and sign:
      dot = re.search(r"(((\W[a-zA-Z])|(\d)+|([IVXLCDM(IV)(IX)(XL)(XC)(CD)(CM)])+)[.])|((\d)+[.])+", t)
      bracket = re.search(r"((\W[a-zA-Z])|(\d)+|([IVXLCDM(IV)(IX)(XL)(XC)(CD)(CM)])+)[)]", t)
      double_bracket = re.search(r"[(](([a-zA-Z])|(/d)+|([IVXLCDM(IV)(IX)(XL)(XC)(CD)(CM)]+))[)]", t)


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
         pos = idx = min(bracket.span()[1]-2, dot.span()[1]-2)
      elif dot and double_bracket:
         sign = '()' if double_bracket.span()[0] < dot.span()[0] else '.'
         pos = idx = min(double_bracket.span()[1]-2, dot.span()[1]-2)
      elif bracket and double_bracket:
         sign = '()' if double_bracket.span()[0] < bracket.span()[0] else '.'
         pos = idx = min(double_bracket.span()[1]-2, bracket.span()[1]-2)
      elif dot:
         sign = '.'
         pos = dot.span()[1]-2
      elif bracket:
         sign = ')'
         pos = bracket.span()[1]-2
      elif double_bracket:
         sign = '()'
         pos  = double_bracket.span()[1]-2
      else:
         sign = None

      # sign это знак параграфа
      if sign:
         if not t[pos].isdigit():   # В случае если имя параграфа это буква
            idx = pos+1
            paragraph = t[pos]
            if pos>0 and paragraph in roman_numbers:
               while t[pos-1] in roman_numbers:
                  paragraph = t[pos-1] + paragraph
                  pos -= 1
         else:
            idx = pos
            paragraph = t[pos]
            while t[pos - 1].isdigit():
                  paragraph = t[pos - 1] + paragraph
                  if pos == 0:
                     break
                  pos -= 1
            pos = idx + 1
            if t[pos] == '.':
                  paragraph += '.'
                  pos_dot = pos
                  pos_digit = pos
                  idx = pos+1
                  while t[pos + 1].isdigit() or t[pos + 1] == '.':
                     paragraph += t[pos + 1]
                     if t[pos + 1].isdigit():
                        pos_digit = pos + 1
                        pos = pos_digit
                     else:
                        pos_dot = pos + 1
                        pos = pos_dot
                     
                     idx = pos

            else:
               idx+=1
            
            # Обработчик исключений
            if t[pos+1] == ')':       
               t = t[pos_dot+1:]
               counter+=(idx+2)
               continue  
            if '.' in paragraph:
               if paragraph[-1] != '.':
                  t = t[pos_digit+1:]
                  counter+=(idx+2)
                  continue
               for i in paragraph.split('.'):
                  if len(i) >= 4:
                     t = t[pos_digit+1:]
                     counter+=(idx+2)
                     continue  
            if paragraph.count('.') == 1 and '.' not in t[pos_digit-5:pos_digit] and '\n' not in t[pos_digit-5:pos_digit] and '\t' not in t[pos_digit-4:pos_digit] and not first_elem and ':' not in t[pos_digit-4:pos_digit] and '   ' not in t[pos_digit-5:pos_digit]:
               t = t[pos_dot+1:]
               counter+=(idx+2)
               continue               
         
         if paragraph in roman_numbers or all(i in roman_numbers for i in list(paragraph)):
            data_type = 'roman'
         elif paragraph.isalpha():
            data_type = 'letter'
         else:
            data_type = 'number'
         t = t[idx+1:]
         counter+=(idx+1)
         if not (len(paragraph.split('.')) == 2 and paragraph.split('.')[1].isdigit()):
            lst.append((paragraph, sign, counter, data_type))
      first_elem = False

   return lst