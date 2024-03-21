import argparse
from release.check import check_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--entity_json_path", help="полный путь к JSON файлу, который ты загружаешь")
    parser.add_argument("--task_file_path", help="полный путь к файлу с настройками")
    parser.add_argument("--report_path", default=None, help="полный путь к файлу в который сохранится отчет (не папка)")
    parser.add_argument("--checked_entity_path", help="полный путь к JSON файлу, куда ты добавил свои свои проверки")
    parser.add_argument("--error_path", default=None, help="полный путь к файлу с ошибкой, если она случилась. Если ошибок нет, то файл не создается")
    args = parser.parse_args()
    check_file(json_path=args.entity_json_path,
               config_path=args.task_file_path,
               report_output=args.report_path,
               json_output=args.checked_entity_path,
               log_path=args.error_path)

