check_type = "check"
document_type = "word"


if document_type == "excel":
        if check_type == "check":
            from excel_version.main_files.check import Checker
            file = Checker(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/xlsx через FRONT/Processing/19053.json",
                        config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/xlsx через FRONT/Original/19053.json",
                        json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/xlsx через FRONT/Processing/19053_checked_new.json",
                        error_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/xlsx через FRONT/Processing/19053.error",
                        visualize=True,
                        new_format=int("0"))
            file.start()
        elif check_type == "gen":
            from excel_version.report.report import Report_generator
            report = Report_generator(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/341d6e80-5f0a-4154-a4d7-159b8a7f3342/Processing/18364_summary.json",
                                    output_pdf="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/341d6e80-5f0a-4154-a4d7-159b8a7f3342/Export/18364_summary.pdf",
                                    config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/341d6e80-5f0a-4154-a4d7-159b8a7f3342/Original/18364.json",
                                    save_doc=False, 
                                    new_format=int("0"))
            report.start()
        
elif document_type == "word":
    if check_type == "check":
        from docx_version.main_files.check import Checker
        file = Checker(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Техническое_задание_16468020_1_ОтчетИПД_1.doc/Processing/19583.json",
                        config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Техническое_задание_16468020_1_ОтчетИПД_1.doc/Original/19583.json",
                        json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Техническое_задание_16468020_1_ОтчетИПД_1.doc/Processing/19583_new.json",
                        error_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Техническое_задание_16468020_1_ОтчетИПД_1.doc/Processing/19583.error",
                        visualize=True,
                        new_format=int("0"))
        file.start()
    elif check_type == "gen":
        from docx_version.report.report import Report_generator
        report = Report_generator(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/9b675877-0606-4b33-b133-9796aaf9810e/Processing/17203_summary.json",
                                  output_pdf="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/9b675877-0606-4b33-b133-9796aaf9810e/Export/17203_summary.pdf",
                                  config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/9b675877-0606-4b33-b133-9796aaf9810e/Original/17203.json",
                                  save_doc=False, 
                                  new_format=int("0"))
        report.start()

elif document_type == "pdf":
    if check_type == "check":
        from pdf_version.main_files.check import Checker
        file = Checker(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/pdf ошибка обработки 2/Processing/19163.json",
                        config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/pdf ошибка обработки 2/Original/19163.json",
                        json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/pdf ошибка обработки 1/Processing/19163_checked.json",
                        error_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/pdf ошибка обработки 1/Processing/19163.error",
                        visualize=True,
                        new_format=int("0"))
        file.start()
    elif check_type == "gen":
        from pdf_version.report.report import Report_generator
        report = Report_generator(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/f2fc9bb1-13c4-4da9-81fa-382acb480a13/Processing/18693_checked.json",
                                    output_pdf="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/f2fc9bb1-13c4-4da9-81fa-382acb480a13/Processing/Result.pdf",
                                    config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/f2fc9bb1-13c4-4da9-81fa-382acb480a13/Original/18693.json",
                                    save_doc=False, 
                                    new_format=int("1"))
        report.start()