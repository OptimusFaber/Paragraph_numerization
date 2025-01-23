import sys, os, json, codecs
global_path = __file__
global_path = global_path.replace("/check.py", "")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from document_parser.Abbreviations.abb import Abb_finder
from document_parser.Numberings.num import Parse_numberings
from document_parser.Text.txt import Parse_text
from utilities.sentence_compare import compare_single_text
from utilities.logger import log_errors

class Checker:
    def __init__(self, json_path=None, config_path=None, json_output=None, error_path=None, text=False, test=False, visualize=False, new_format=0):
        self.error_path = error_path
        if error_path is None:
            sys.exit("No log file was provided")
        if os.path.exists(self.error_path):
            os.remove(self.error_path)
        else:
            out_error = '/'.join(self.error_path.split('/')[:-1])
            if not os.path.exists(out_error):
                sys.exit("Error while creating log file")

        log_path = error_path.split('/')
        log_path = log_path[:-1] + [log_path[-1].split('.')[0] + '.log']
        self.log_path = '/'.join(log_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

        self.json_path = json_path
        self.config_path = config_path
        self.json_output = json_output
        self.text = text
        self.test = test
        self.visualize = visualize
        self.new_format = new_format
    
    @log_errors
    def read_config(self):
        F = open(self.config_path, encoding='utf-8')
        j = json.load(F)
        add_info = {}

        if not self.new_format:
            paragraph_check = j["Settings"]["CheckNumberList"]
            abb_check = j["Settings"]["CheckAbbreviations"]
            try:
                pref = {"CommonAbbreviations": "Abbreviation", "CorruptionFactor":"Corruption", "FormulationsWoNPA":"No_NPA", "IncorrectWording":"IncorrectForm"}
                for marker, dct in list(pref.items()):
                    if j["Settings"]["DetectReferences"][marker]:
                        add_info[dct] = j["Dictionaries"][dct]
            except:
                add_info = None
        else:
            paragraph_check = j["Settings"]["CheckNumberings"]
            abb_check = j["Settings"]["CheckAbbreviations"]
            try:
                pref = {"CheckAbbreviations": "Abbreviations", "CheckCorruption":"Corruption", "CheckNoNpaConnection":"No_NPA", "CheckIncorrectSentences":"IncorrectForm"}
                for marker, dct in list(pref.items()):
                    if j["Settings"][marker]:
                        add_info[dct] = j[dct]
            except:
                add_info = None

        return paragraph_check, abb_check, add_info

    @log_errors
    def open_json(self, json_path):
        F = codecs.open(json_path, "r", "utf_8_sig")
        json_parsed = json.load(F)
        F.close()
        return json_parsed

    @log_errors
    def set_error_standart(self, dictonaries):
        if not dictonaries:
            return []
        feedback_list = []
        for dct in dictonaries:
            keys = list(dct.keys())
            for i in range(1, len(keys)):
                if dct[keys[i]]['status'] == 'MISSING' or dct[keys[i]]['status'] == 'DUPLICATE' or dct[keys[i]]['status'] == 'INCORRECT':
                    feedback_list.append([dct[keys[i]]['name'], dct[keys[i]]['sign'], dct[keys[i]]['pos'], dct[keys[i]]['string_index'], dct[keys[i]]['data_type'], dct[keys[i]]['status'], dct[keys[i]]['sup'], dct[keys[i]]['elem_name']])

        for i in range(len(feedback_list)):
            text = "Отсутствует " if feedback_list[i][5] == "MISSING" else "Дублирующаяся " if feedback_list[i][1] == "таблица" or feedback_list[i][1] == "схема" else "Неверный " if feedback_list[i][5] == "INCORRECT" else "Дублирующийся "
            
            if feedback_list[i][1] == "()":
                elem = feedback_list[i][0]
                if feedback_list[i][0][0] != "(" and feedback_list[i][0][-1] != ")":
                    elem = "(" + elem  + ")"
                feedback_list[i][3] = feedback_list[i][6]
                if feedback_list[i][6][0] != "(" and feedback_list[i][6][-1] != ")":
                    feedback_list[i][3] = "(" + feedback_list[i][3]  + ")"
            elif feedback_list[i][1] == ")":
                elem = feedback_list[i][0]
                if feedback_list[i][0][-1] != ")":
                    elem += ")"
                feedback_list[i][3] = feedback_list[i][6]
                if feedback_list[i][6][-1] != ")":
                    feedback_list[i][3] += ")"
            elif feedback_list[i][1] == "." and feedback_list[i][4] != "numbers":
                elem = feedback_list[i][0]
                if feedback_list[i][0][-1] != ".":
                    elem += "."
                feedback_list[i][3] = feedback_list[i][6]
                if feedback_list[i][6][-1] != ".":
                    feedback_list[i][3] += "."
            else:
                elem = feedback_list[i][0]
                feedback_list[i][3] = feedback_list[i][6]

            if feedback_list[i][1] == "таблица" or feedback_list[i][1] == "схема" or feedback_list[i][1] == "приложение":
                feedback_list[i][0] = "Numbering"
                feedback_list[i][1] = text + elem
            elif feedback_list[i][1] == "рисунок" or feedback_list[i][1] == "рис":
                feedback_list[i][0] = "Numbering"
                feedback_list[i][1] = text + elem
            else:
                feedback_list[i][0] = "Numbering"
                feedback_list[i][1] = text + "параграф " + elem
            feedback_list[i] = feedback_list[i][:4]
        
        return feedback_list 

    @log_errors
    def report_gen(self, json_parsed, dictionary):
        for elem in json_parsed.keys():
            if elem == 'Paragraphs':
                for e in range(len(json_parsed[elem])):
                    if json_parsed[elem][e]['Index'] in dictionary.keys():
                        if json_parsed[elem][e].get('Errors') is None:
                            json_parsed[elem][e]['Errors'] = dictionary[json_parsed[elem][e]['Index']]
                        else:
                            json_parsed[elem][e]['Errors'].extend(dictionary[json_parsed[elem][e]['Index']])
                    else:
                        if json_parsed[elem][e].get('Errors') is None:
                            json_parsed[elem][e]['Errors'] = None

                    if json_parsed[elem][e]['Entities']:
                        for j in range(len(json_parsed[elem][e]['Entities'])):
                            mistake = compare_single_text(json=json_parsed[elem][e]['Entities'][j], error_path=self.error_path)
                            if mistake and mistake is not None:
                                if json_parsed[elem][e]['Entities'][j]['Errors']:
                                    json_parsed[elem][e]['Entities'][j]['Errors'].append(mistake)
                                else:
                                    json_parsed[elem][e]['Entities'][j]['Errors'] = [mistake]
                                json_parsed[elem][e]['Entities'][j]["Status"] = "Unknown"

        return json_parsed
  
    @log_errors
    def start(self):
        #? CHECKING INPUT CONFIGURATION DIRECTORY
        if self.config_path:
            paragraph_check, abb_check, add_info = self.read_config()
        else:
            add_info = {}
            paragraph_check = abb_check = True
        #* CHECKING INPUT-JSON DIRECTORY
        json_parsed = self.open_json(self.json_path)
        #! CHECKING OUTPUT-JSON DIRECTORY--------------------------------------------------------------------------------------------------------------
        # self.open_json(self.json_output)
        # НАДО ПЕРЕПИСАТЬ ЛОГЕР ЧТОБЫ ВСЕ ПРОВЕРЯТЬ
        #!----------------------------------------------------------------------------------------------------------------------------------------------
        if paragraph_check:
            parser = Parse_text(error_path=self.error_path)
            txt = parser.start(json_parsed)

            parser = Parse_numberings(error_path=self.error_path)
            dcts = parser.start(txt)

            if self.text:
                print(txt)
            if self.visualize:
                parser.show()
        else:
            dcts = {} 
        if self.test:
            return dcts
        else:
            parser = Abb_finder(error_path=self.error_path)
            abbs = parser.start(text=json_parsed, abbs=abb_check, add_info=add_info, new_format=self.new_format)
            nums = self.set_error_standart(dictonaries=dcts)

            feedback = abbs + nums
            dictionary =  {}
            for i in range(len(feedback)):
                if not dictionary.get(feedback[i][2]):
                    dictionary[feedback[i][2]] = [{"Type": feedback[i][0],"Description": feedback[i][1], "Element": feedback[i][3]}]
                else:
                    dictionary[feedback[i][2]].append({"Type": feedback[i][0],"Description": feedback[i][1], "Element": feedback[i][3]})

            json_parsed = self.open_json(self.json_path)
            feedback_json = self.report_gen(json_parsed=json_parsed, dictionary=dictionary)
            
            json_object = json.dumps(feedback_json, indent=4, ensure_ascii=False)
            with codecs.open(self.json_output, "w", encoding='utf-8') as outfile: 
                outfile.write(json_object)
            outfile.close()

            if os.path.exists(self.error_path):
                if os.path.getsize(self.error_path) == 0:
                    os.remove(self.error_path)
            
            if os.path.exists(self.log_path):
                if os.path.getsize(self.log_path) == 0:
                    os.remove(self.log_path)
