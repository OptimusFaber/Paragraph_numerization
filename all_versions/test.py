check_type = "check"
document_type = "pdf"


if document_type == "excel":
    if check_type == "check":
        from excel_version.main_files.check import Checker
        file = Checker(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/e427bb56-f87e-4ce8-90bb-1980b200d9a3/Processing/20492.json",
                    config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/e427bb56-f87e-4ce8-90bb-1980b200d9a3/Original/20492.json",
                    json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/e427bb56-f87e-4ce8-90bb-1980b200d9a3/Processing/20492_checked_new.json",
                    error_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/e427bb56-f87e-4ce8-90bb-1980b200d9a3/Processing/20492.error",
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
        file = Checker(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/e427bb56-f87e-4ce8-90bb-1980b200d9a3/Processing/20492.json",
                        config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/e427bb56-f87e-4ce8-90bb-1980b200d9a3/Original/20492.json",
                        json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/e427bb56-f87e-4ce8-90bb-1980b200d9a3/Processing/20492_new.json",
                        error_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/e427bb56-f87e-4ce8-90bb-1980b200d9a3/Processing/20492.error",
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
        file = Checker(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/83fd79c1-0737-42d0-9cc0-18230613d2be/Processing/20497.json",
                        config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/83fd79c1-0737-42d0-9cc0-18230613d2be/Original/20497.json",
                        json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/83fd79c1-0737-42d0-9cc0-18230613d2be/Processing/20497_checked.json",
                        error_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/83fd79c1-0737-42d0-9cc0-18230613d2be/Processing/20497.error",
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