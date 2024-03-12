from docxtpl import DocxTemplate
import os,sys
import json
from datetime import datetime   


def generate(dict_list=None, output_pdf="./", inputFileName = "standart_format.docx", output_docx = "./report.docx", originalfilename = "отчёт", save_doc=False): 
    """
    json_path (string) -> path to .json file with statistics,
    output_pdf (string) -> folder where to place pdf file,
    inputFileName (string) -> path to doc standart form,
    output_docx (string) -> path where to save buf docx file with statistics,
    originalfilename (string) -> report name,
    save_doc (boolean) -> save docx with statistics if true
    """
    #? Data
    basedir = os.path.dirname(sys.argv[0]).replace('release', 'modification')
    path = os.path.join(basedir, "", inputFileName)
    if len(output_docx.split('/'))==1:
        output_docx = os.path.join(basedir, "", output_docx)
    template = DocxTemplate(path)
    #?------------------------------------

    #? Manage outputdir for pdf
    if output_pdf is None:
        output_pdf = "./"    
    #?------------------------------
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    #* Containers and dictionaries
    var = {
        'Действует': 0,
        'Не действует': 0,
        'Не определен': 0
    }
    status = {
        'Actual': 'Действует',
        'Awaits': 'Действует',
        'Declined': 'Не действует',
        'NotApplicable': 'Не действует',
        'Changed': 'Не действует',
        'NotFound': 'Не определен',
        'Unknown': 'Не определен'
    }
    data = {
        "Unknown": var.copy(),
        "FZ": var,
        "Moscow": var.copy(),
        "Decree": var,
        "NpaSnip": var.copy(),
        "Gost": var.copy(),
        "SanPin": var.copy()
    }
    context = {
        'file_name': originalfilename,
        'date': date,
        'mistakes': [],
        'statistics': [],
        'fed_npa': [],
        'moscow_npa':[],
        'gost':[],
        'SanPin':[],
        'SNiP': [],
        'others': []
    }
    mistakes = {'Сокращение не введено': 0,
                'Подозрение на неоднозначное требование': 0,
                'Нет связи с НПА (НТА)': 0,
                'Некорректная формулировка': 0,
                'Ошибка нумерации': 0,}
    categories = {
        "Федеральные НПА": "FZ", #! add Decree
        "НПА г. Москвы": "Moscow", 
        "ГОСТ": "Gost",
        "СанПиН": "SanPin", 
        "СНиП": "NpaSnip", 
        "Иные виды НПА и НТА": "Unknown"}
    mstks_frmt = {'AbbreviationError': 'Сокращение не введено',
                'CorruptionFactorError': 'Подозрение на неоднозначное требование',
                'NoConnectionWithNPAError': 'Нет связи с НПА (НТА)',
                'IncorrectFormulationError': 'Некорректная формулировка',
                'TextErrorNumber': 'Ошибка нумерации',
                'PictureErrorNumber': 'Ошибка нумерации',
                'TableErrorNumber': 'Ошибка нумерации'}
    #*------------------------
    
    #! Mistakes statistics
    for elem in dict_list:
        if elem['Error'] != 'Неверные сущности':
            mistakes[mstks_frmt[elem['Feedback']]]+=1
    for key in mistakes.keys():
        if mistakes[key] == 0:
            mistakes[key] = 'Нет'
    mistakes = list(mistakes.items())
    for i, (name, num) in enumerate(mistakes):
        mistakes[i] = {'mistake':name, 'amount':num}
    context['mistakes']=mistakes
    #! -------------------

    #& Filling in data
    for elem in dict_list:
        if elem['Error'] == 'Неверные сущности':
            data[elem['Entities'][0]["document_type"]][status[elem['Entities'][0]["status"]]]+=1


    for elem in categories:
        stat = data[categories[elem]]
        active = stat['Действует'] if stat['Действует'] else "Нет"
        inactive = stat['Не действует'] if stat['Не действует'] else "Нет"
        unknown = stat['Не определен'] if stat['Не определен'] else "Нет"
        row = {"type":elem, "active":"{}".format(active), "inactive":"{}".format(inactive), "unknown":"{}".format(unknown)}
        context['statistics'].append(row)
    #&--------------------------------------------------------
        
    buf = {
        "Unknown": [context['others'], 0],
        "FZ": [context['fed_npa'], 0],
        "Moscow": [context['moscow_npa'], 0],
        "Decree": [context['fed_npa'], 0],
        "NpaSnip": [context['SNiP'], 0],
        "Gost": [context['gost'], 0],
        "SanPin": [context['SanPin'], 0]
    }
    
    #! Create docx file
    res = list(map(lambda x: x['Entities'], list(filter(lambda x: x['Entities'] is not None, dict_list))))
    for i in range(len(res)): 
        tytle = buf[res[i][0]["document_type"]][0]
        buf[res[i][0]["document_type"]][1] += 1
        fed_npa= {'num': buf[res[i][0]["document_type"]][1], 'doc': res[i][0]["document_text"],'status': status[res[i][0]["status"]],'link': "" if res[i][0]["catalog_reference"] is None else res[i][0]["catalog_reference"]}
        tytle.append(fed_npa)
    template.render(context)
    template.save(output_docx)
    #!--------------------------------------------------------
    #^ Save PDF
    os.system("libreoffice \
            --convert-to {} \
            --outdir {} \
            {}".format('pdf', output_pdf, output_docx))
    if not save_doc:
        os.remove(output_docx)
    #^------------------------