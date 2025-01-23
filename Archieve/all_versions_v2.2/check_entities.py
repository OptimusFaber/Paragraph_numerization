import argparse
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--entity_json_path", help="полный путь к JSON файлу, который ты загружаешь")
    parser.add_argument("-t", "--task_file_path", help="полный путь к файлу с настройками")
    parser.add_argument("-c", "--checked_entity_path", help="полный путь к JSON файлу, куда ты добавил свои проверки")
    parser.add_argument("-e", "--error_path", default=None, help="полный путь к файлу с ошибкой, если она случилась. Если ошибок нет, то файл не создается")
    parser.add_argument("-d", "--document_type", default=None, help="тип обрабатывемого документа - excel или word")
    parser.add_argument("-n", "--new_format", default=0, help="флаг для нового формата json файла")
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
               json_output=args.checked_entity_path,
               global_log_path=args.error_path,
               new_format=int(args.new_format))
