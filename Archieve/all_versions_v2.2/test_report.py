document_type = "excel"


if document_type == "excel":
    from excel_version.report.report import generate
    generate(json_path='/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/341d6e80-5f0a-4154-a4d7-159b8a7f3342/Processing/18364_summary.json', 
             output_pdf='/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/341d6e80-5f0a-4154-a4d7-159b8a7f3342/Export/18364_summary.pdf',
             config_path='/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/341d6e80-5f0a-4154-a4d7-159b8a7f3342/Original/18364.json',
             save_doc=False, 
             new_format=int("0"))
        
elif document_type == "word":
    from docx_version.report.report import generate
    generate(json_path='/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/8a660f44-285a-4826-835e-46853110e3fd/Processing/17091_summary.json', 
             output_pdf='/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/8a660f44-285a-4826-835e-46853110e3fd/Export/17091_Summary.pdf',
             config_path='/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/8a660f44-285a-4826-835e-46853110e3fd/Original/17091.json',
             save_doc=False, 
             new_format=int("0"))

elif document_type == "pdf":
    from  pdf_version.report.report import generate
    generate(json_path='/home/rodrick/Downloads/Telegram Desktop/пример pdf/8c1fc05b-bc95-465d-b3b3-6e725011635a/Processing/17138_checked.json', 
             output_pdf='/home/rodrick/Downloads/Telegram Desktop/пример pdf/8c1fc05b-bc95-465d-b3b3-6e725011635a/Export/17138_result.pdf',
             config_path='/home/rodrick/Downloads/Telegram Desktop/пример pdf/8c1fc05b-bc95-465d-b3b3-6e725011635a/Original/17138.json',
             save_doc=False, 
             new_format=int("0"))