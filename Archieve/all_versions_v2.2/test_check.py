document_type = "word"


if document_type == "excel":
        from excel_version.release.check import check_file
        check_file(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Excel/0296d5e8-2375-44d0-823b-dff50413f444/Processing/18364.json",
                config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Excel/0296d5e8-2375-44d0-823b-dff50413f444/Original/18364.json",
                json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Excel/0296d5e8-2375-44d0-823b-dff50413f444/Processing/18364_checked2.json",
                global_log_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Excel/0296d5e8-2375-44d0-823b-dff50413f444/Processing/18364.error",
                visualize=True,
                new_format=int("0"))
        
elif document_type == "word":
    from docx_version.release.check import check_file
    check_file(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/word/Processing/18654.json",
                config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/word/Original/18654.json",
                json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/word/Processing/18654_checked.json",
                global_log_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/word/Processing/18654.error",
                visualize=True,
                new_format=int("0"))

elif document_type == "pdf":
    from  pdf_version.release.check import check_file
    check_file(json_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Pdf/625bc64c-550f-4a45-b6d5-c06a6a8eacca/Processing/18384.json",
                config_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Pdf/625bc64c-550f-4a45-b6d5-c06a6a8eacca/Original/18384.json",
                json_output="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Pdf/625bc64c-550f-4a45-b6d5-c06a6a8eacca/Processing/18384_checked.json",
                global_log_path="/home/rodrick/Desktop/Work/EasyData/Paragraph_numerization/Pdf/625bc64c-550f-4a45-b6d5-c06a6a8eacca/Processing/18384.error",
                visualize=True,
                new_format=int("0"))