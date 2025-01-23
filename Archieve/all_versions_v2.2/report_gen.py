import argparse
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--json_path", help="полный путь к JSON файлу, который ты загружаешь")
    parser.add_argument("-o", "--output_pdf", help="полный путь к для сохранения отчеиа")
    parser.add_argument("-c", "--task_file_path", help="полный путь к файлу с настройками")
    parser.add_argument("-f", "--word_format", default=None, help="полный путь к файлу в котором информация о формате отчета")
    parser.add_argument("-t", "--document_type", default=None, help="тип обрабатывемого документа - excel или word")
    parser.add_argument("-l", "--libre_path", default='libreoffice', help="полный путь к версии либер офиса")
    parser.add_argument("-e", "--error_path", default=None, help="полный путь к файлу с ошибкой, если она случилась. Если ошибок нет, то файл не создается")
    parser.add_argument("-n", "--new_format", default=0, help="флаг для нового формата json файла")
    args = parser.parse_args()

    if args.document_type == "excel":
        from excel_version.report.report import generate
    elif args.document_type == "word":
        from docx_version.report.report import generate
    elif args.document_type == "pdf":
        from  pdf_version.report.report import generate
    else:
        sys.exit("Unrecognized document_type occured")

    print(args.task_file_path)
    

    generate(json_path=args.json_path,
             output_pdf=args.output_pdf,
             config_path=args.task_file_path,
             word_format=args.word_format,
             libre_path=args.libre_path,
             log_path=args.error_path,
             new_format=int(args.new_format))