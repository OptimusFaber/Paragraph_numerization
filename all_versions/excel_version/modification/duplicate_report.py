from docxtpl import DocxTemplate
import os,sys
from datetime import datetime  
import time
import json


def duplicates_info(json_path=None, output_pdf="./report.pdf", inputFileName = None, originalfilename = None, save_doc=False, libre_path=None, status_path=None): 
    dict_list = []
    F = open(json_path, encoding='utf-8')
    j = json.load(F)
    for element in j[0]['CheckElements']:
        dict_list.append((element['DocumentName'], len(element['Results'])))
    #? Data
    basedir = os.path.dirname(sys.argv[0]).replace('release', 'modification')
    if inputFileName is None:
        inputFileName = __file__
        inputFileName = inputFileName.replace("report.py", "standart_format.docx")
    path = os.path.join(basedir, "", inputFileName)
    output_docx = output_pdf.replace("pdf", "docx")
    output_pdf = "/".join(output_pdf.split('/')[:-1])
    if len(output_docx.split('/'))==1:
        output_docx = os.path.join(basedir, "", output_docx)
    #?------------------------------------

    #? Manage outputdir for pdf
    if output_pdf is None or output_pdf == '.':
        output_pdf = "./"    
    #?------------------------------
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    #* Containers and dictionaries
    context = {
        'date': date,
        'results': []
    }

    template = DocxTemplate(path)
    for element in dict_list:
        context['results'].append({'orig_name': originalfilename, 'name': element[0], 'duplicates': element[1]})

    template.render(context)
    template.save(output_docx)
    #!--------------------------------------------------------
    #^ Save PDF
    res = True
    while res:
        res = os.system("{} \
                --convert-to {} \
                --outdir {} \
                {}".format(libre_path, 'pdf', output_pdf, output_docx))
        if res != 0:
            time.sleep(2)
    if not save_doc:
        os.remove(output_docx)
    os.remove(f"{status_path}/libre_status.log")
    #^------------------------