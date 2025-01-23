check_type = "check"
document_type = "word"


if document_type == "excel":
        if check_type == "check":
            from excel_version.main_files.check import Checker
            file = Checker(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/1aafb121-ccc7-4a71-811d-b079f9e496b0/Processing/1aafb121-ccc7-4a71-811d-b079f9e496b0.json",
                        config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/1aafb121-ccc7-4a71-811d-b079f9e496b0/Original/1aafb121-ccc7-4a71-811d-b079f9e496b0.json",
                        json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/1aafb121-ccc7-4a71-811d-b079f9e496b0/Processing/1aafb121-ccc7-4a71-811d-b079f9e496b0_checked_new.json",
                        error_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/1aafb121-ccc7-4a71-811d-b079f9e496b0/Processing/1aafb121-ccc7-4a71-811d-b079f9e496b0.error",
                        visualize=True,
                        new_format=int("1"))
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
        file = Checker(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/8f00d8f2-2793-425b-93a5-57d2cc18085f/Processing/8f00d8f2-2793-425b-93a5-57d2cc18085f.json",
                        config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/8f00d8f2-2793-425b-93a5-57d2cc18085f/Original/8f00d8f2-2793-425b-93a5-57d2cc18085f.json",
                        json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/8f00d8f2-2793-425b-93a5-57d2cc18085f/Processing/8f00d8f2-2793-425b-93a5-57d2cc18085f_checked_new.json",
                        error_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/8f00d8f2-2793-425b-93a5-57d2cc18085f/Processing/8f00d8f2-2793-425b-93a5-57d2cc18085f.error",
                        visualize=True,
                        new_format=int("1"))
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
        file = Checker(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/96356048-b3c6-4174-ae74-27924a44f870/Processing/96356048-b3c6-4174-ae74-27924a44f870.json",
                        config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/pdf/Original/18791.json",
                        json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/pdf/Processing/18791_checked.json",
                        error_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/pdf/Processing/18791.error",
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