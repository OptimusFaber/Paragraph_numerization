import argparse
import json
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--entity_json_path", help="полный путь к JSON файлу, который ты загружаешь")
    parser.add_argument("--task_file_path", help="полный путь к файлу с настройками")
    parser.add_argument("--report_path", default=None, help="полный путь к файлу в который сохранится отчет (не папка)")
    parser.add_argument("--checked_entity_path", help="полный путь к JSON файлу, куда ты добавил свои проверки")
    parser.add_argument("--error_path", default=None, help="полный путь к файлу с ошибкой, если она случилась. Если ошибок нет, то файл не создается")
    parser.add_argument("--libre_path", default='libreoffice', help="полный путь к версии либер офиса")
    parser.add_argument("--document_type", default=None, help="тип обрабатывемого документа - excel или word")
    args = parser.parse_args()
        
    if args.document_type == "excel":
        from excel_version.release.check import check_file
    elif args.document_type == "word":
        from docx_version.release.check import check_file
    elif args.document_type == "pdf":
        from  pdf_version.release.check import check_file
    else:
        sys.exit("Unrecognized document_type occured")

    check_file(args.entity_json_path,
               config_path=args.task_file_path,
               report_output=args.report_path,
               json_output=args.checked_entity_path,
               global_log_path=args.error_path,
               libre_path=args.libre_path)