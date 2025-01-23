from docxtpl import DocxTemplate
import os, sys, json, codecs, time
from datetime import datetime  
global_path = __file__
global_path = global_path.replace("report.py", "")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.logger import log_errors

VALUE_DICTIONARY = {"Unknown": ["CustomsUnionDecision", "RD", "RDS", "OST", "MGSN", "CustomsReglament", "SP", "MethodicalRecommendations", "GlobalNPA", "Unknown"],
                    "FZ": ["FederalLaw", "PresidentDecree", "FSTEKDecree", "FSBDecree", "MinkomSvyazDecree", "SanDoctorDecree", "GovermentDecree", "DecreeMinTruda", "DecreeMinZdrav", "DecreeMinStroy", "DecreeMinEnergo", "DecreeMinRegion", "DecreeRosStandard", "DecreeFns", "DecreeMinistryOther"],
                    "Moscow": ["MoscowLaw", "DecreeMoscow", "DecreeITMoscow"],
                    "NpaSnip": ["SNiP"],
                    "Gost": ["GOST"],
                    "SanPin": ["SanPin"]
                    }

STATUS = {'Actual': 'Действует',
          'Awaits': 'Действует',
          'Declined': 'Не действует',
          'NotApplicable': 'Не действует',
          'Changed': 'Не действует',
          'NotFound': 'Не определен',
          'Unknown': 'Не определен'
          }

var = {'Действует': 0,
        'Не действует': 0,
        'Не определен': 0
        }
        
DATA = {"Unknown": var.copy(),
        "FZ": var,
        "Moscow": var.copy(),
        "Decree": var,
        "NpaSnip": var.copy(),
        "Gost": var.copy(),
        "SanPin": var.copy()
        }

MISTAKES = {'Сокращение не введено': 0,
            'Подозрение на неоднозначное требование': 0,
            'Нет связи с НПА (НТА)': 0,
            'Некорректная формулировка': 0,
            'Ошибка нумерации': 0,
            }
CATEGORIES = {"Федеральные НПА": "FZ", 
              "НПА г. Москвы": "Moscow", 
              "ГОСТ": "Gost",
              "СанПиН": "SanPin", 
              "СНиП": "NpaSnip", 
              "Иные виды НПА и НТА": "Unknown"
              }

MISTAKES_FORMAT = {'Abbreviation': 'Сокращение не введено',
                   'Corruption': 'Подозрение на неоднозначное требование',
                   'NoNPA': 'Нет связи с НПА (НТА)',
                   'IncorrectForm': 'Некорректная формулировка',
                   'Numbering': 'Ошибка нумерации',
                   'DuplicateEntity': 'Ошибка нумерации'
                   }

class Report_generator:
    def __init__(self, json_path=None, output_pdf="./report.pdf", config_path=None, word_format = None, save_doc=False, libre_path=None, status_path=global_path, log_path=None, new_format=0): 
        self.json_path = json_path
        self.output_pdf = output_pdf
        self.config_path = config_path
        self.word_format = word_format
        self.save_doc = save_doc
        self.libre_path = libre_path
        if libre_path is None:
            print("No libre office parametr provided, using default libreoffice!!!")
            self.libre_path = 'libreoffice'
        self.status_path = status_path
        self.log_path = log_path
        self.new_format = new_format
        self.value_dictionary = VALUE_DICTIONARY
        self.status = STATUS
        self.data = DATA
        self.mistakes = MISTAKES
        self.categories = CATEGORIES
        self.mistakes_format = MISTAKES_FORMAT

    @log_errors
    def start(self): 
        if self.config_path is not None:
            config = self.open_json(self.config_path)
            NpaNta = self.read_config(config)
        else:
            print('No configuration file was provided, setting NpaNta to True!!!')
            NpaNta = False

        feedback_json = self.open_json(self.json_path)
        try:
            originalfilename = feedback_json["Name"]
        except:
            originalfilename = "отчет"
        mistakes = feedback_json['Errors']
        report = self.feedback_parse(feedback_json, NpaNta)
        if self.word_format is None:
            word_format = __file__
            word_format = word_format.replace("report.py", "standart_format.docx")
        #? Data
        basedir = os.path.dirname(sys.argv[0]).replace('release', 'modification')
        path = os.path.join(basedir, "", word_format)
        output_docx = self.output_pdf[:-3] + "docx"
        self.output_pdf = "/".join(self.output_pdf.split('/')[:-1])
        if len(output_docx.split('/'))==1:
            output_docx = os.path.join(basedir, "", output_docx)
        template = DocxTemplate(path)
        #? Manage outputdir for pdf
        if self.output_pdf is None or self.output_pdf == '.':
            self.output_pdf = "./report.pdf"    
        #?------------------------------
        date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        #* Containers and dictionaries
        
        for j in range(len(report)):
            if report[j]["Error"] == 'Неверные сущности':
                for key in self.value_dictionary.keys():
                    if report[j]["Feedback"]["DocumentType"] in self.value_dictionary[key]:
                        report[j]["Feedback"]["MainStatus"] = key
                        break
                else:
                    report[j]["Feedback"]["MainStatus"] = "Unknown"
        
        context = {
            'file_name': originalfilename,
            'date': date,
            'mistakes': [],
            'statistics': [],
            'tables': [
                {"full": 0, "name": "Федеральные НПА", "info": []},
                {"full": 0, "name": "НПА г. Москвы", "info": []},
                {"full": 0, "name": "ГОСТ", "info": []},
                {"full": 0, "name": "СанПиН", "info": []},
                {"full": 0, "name": "СНиП", "info": []},
                {"full": 0, "name": "Иные виды НПА и НТА", "info": []}
            ]
        }
        
        #*------------------------
        
        #! Mistakes statistics
        mistakes = [{'mistake': 'Сокращение не введено', 'amount': mistakes['Abbreviation']},
                {'mistake':'Подозрение на неоднозначное требование', 'amount': mistakes['Corruption']},
                {'mistake':'Нет связи с НПА (НТА)', 'amount': mistakes['NoNpaConnection']},
                {'mistake':'Некорректная формулировка', 'amount': mistakes['IncorrectStatement']},
                {'mistake':'Ошибка нумерации', 'amount': mistakes['Numeration']}
                ]
        
        context['mistakes']=mistakes
        #! -------------------

        #& Filling in data
        for elem in report:
            if elem['Error'] == 'Неверные сущности':
                self.data[elem["Feedback"]["MainStatus"]][self.status[elem["Feedback"]["Status"]]]+=1


        for elem in self.categories:
            stat = self.data[self.categories[elem]]
            active = stat['Действует'] if stat['Действует'] else "Нет"
            inactive = stat['Не действует'] if stat['Не действует'] else "Нет"
            unknown = stat['Не определен'] if stat['Не определен'] else "Нет"
            if active == inactive == unknown == "Нет":
                continue
            row = {"type":elem, "active":"{}".format(active), "inactive":"{}".format(inactive), "unknown":"{}".format(unknown)}
            context['statistics'].append(row)
        #&--------------------------------------------------------
            
        buf = {
            "Unknown": [context['tables'][5], 0],
            "FZ": [context['tables'][0], 0],
            "Moscow": [context['tables'][1], 0],
            "NpaSnip": [context['tables'][4], 0],
            "Gost": [context['tables'][2], 0],
            "SanPin": [context['tables'][3], 0]
        }
        tic = time.time()
        while os.path.isfile(f"{self.status_path}/libre_status.log"):
            time.sleep(0.5)
            if time.time()-tic>90:
                os.remove(f"{self.status_path}/libre_status.log")
        with open(f"{self.status_path}/libre_status.log", 'w') as fp:
            pass
        #! Create docx file
        res = list(map(lambda x: x['Feedback'],list(filter(lambda x: x['Error'] == 'Неверные сущности', report))))
        for i in range(len(res)): 
            tytle = buf[res[i]["MainStatus"]][0]['info']
            buf[res[i]["MainStatus"]][0]['full']+=1
            buf[res[i]["MainStatus"]][1] += 1
            fed_npa= {'num': buf[res[i]["MainStatus"]][1], 'doc': res[i]["Text"],'status': self.status[res[i]["Status"]],'link': "" if res[i]["CatalogLink"] is None else res[i]["CatalogLink"]}
            tytle.append(fed_npa)
        template.render(context)
        template.save(output_docx)
        #!--------------------------------------------------------
        #^ Save PDF
        res = True
        while res:
            res = os.system("{} \
                    --convert-to {} \
                    --outdir {} \
                    {}".format(self.libre_path, 'pdf', self.output_pdf, output_docx))
            if res != 0:
                time.sleep(2)
        if not self.save_doc:
            os.remove(output_docx)
        os.remove(f"{self.status_path}/libre_status.log")
        #^------------------------

    @log_errors
    def open_json(self, json_path: str):
        F = codecs.open(json_path, "r", "utf_8_sig")
        json_parsed = json.load(F)
        F.close()
        return json_parsed

    @log_errors
    def read_config(self, config):
        if self.new_format:
            try:
                NpaNta = config['Settings']['SkipCorrectNpaNta']
            except:
                sys.exit("Wrong config format, no ['Settings']['SkipCorrectNpaNta'] object was found!")
        else:
            try:
                NpaNta = config['Settings']['NotSelectNpaNta']
            except:
                sys.exit("Wrong config format, no ['Settings']['NotSelectNpaNta'] object was found!")
        return NpaNta

    @log_errors
    def feedback_parse(self, feedback_json, NpaNta: bool):
        report = []
        for sheet in feedback_json['Worksheets']:
            for st in sheet['Rows']:
                for cl in st['Cells']:
                    if cl['Errors']:
                        report.append({"Error": cl['Errors'][0]["Description"],
                                        "Feedback": cl['Errors'][0]["Type"]})
                    else:
                        cl['Errors'] = None
                    if cl['Entities']:
                        for j in range(len(cl['Entities'])):
                            if not cl['Entities'][j]["IsValid"]:
                                continue
                            if NpaNta and cl['Entities'][j]['Status'] == 'Actual':
                                continue 
                            if not cl['Entities'][j]["IsSkip"]:
                                report.append({"Error": "Неверные сущности",
                                                "Feedback": cl['Entities'][j]})
        return report