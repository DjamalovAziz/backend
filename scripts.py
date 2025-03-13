#!/usr/bin/env python3
import os
import sys


def extract_content_between_markers(file_path, start_marker, end_marker):
    """Извлекает содержимое между двумя маркерами из файла."""
    content = []
    capturing = False

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if start_marker in line:
                    capturing = True
                    continue
                if capturing and end_marker in line:
                    capturing = False
                    break
                if capturing:
                    content.append(line)
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")

    return "".join(content)


def process_directory():
    """Обрабатывает директорию для извлечения блоков кода между маркерами."""
    # Конфигурация для этой функции
    config = {
        "directory_to_scan": "./backend",  # Директория для сканирования
        "start_marker": "# backend\\user",  # Начальный маркер
        "end_marker": "$",  # Конечный маркер
        "output_file": "code.py",  # Файл для записи результата
    }

    extracted_data = []

    if not os.path.isdir(config["directory_to_scan"]):
        print(f"Директория '{config['directory_to_scan']}' не существует.")
        sys.exit(1)

    print(f"Сканирование директории: {config['directory_to_scan']}")
    print(f"Ищем текст между: '{config['start_marker']}' и '{config['end_marker']}'")

    count_files = 0
    count_matches = 0

    for root, _, files in os.walk(config["directory_to_scan"]):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                count_files += 1
                content = extract_content_between_markers(
                    file_path, config["start_marker"], config["end_marker"]
                )
                if content:
                    count_matches += 1
                    extracted_data.append(f"# Extracted from: {file_path}\n{content}\n")

    try:
        with open(config["output_file"], "w", encoding="utf-8") as output:
            output.write(
                "# Auto-generated file containing extracted code from Python files\n\n"
            )
            output.write("\n".join(extracted_data))
        print(f"Данные успешно записаны в {config['output_file']}")
        print(f"Обработано файлов: {count_files}")
        print(f"Найдено совпадений: {count_matches}")
    except Exception as e:
        print(f"Ошибка при записи в файл {config['output_file']}: {e}")


def add_file_path_comments():
    """Добавляет комментарии с путями к файлам в целевых директориях."""
    # Конфигурация для этой функции
    config = {
        "root_dir": ".",  # Корневая директория
        "target_dirs": {"backend"},  # Целевые директории для обработки
        "exclude_list": {
            ".env_backend",
            "__init__.py",
        },  # Исключаемые файлы и директории
    }

    try:
        for target_dir in config["target_dirs"]:
            target_path = os.path.join(config["root_dir"], target_dir)
            if not os.path.exists(target_path):
                print(f"Целевая директория {target_path} не найдена")
                continue

            for dirpath, _, filenames in os.walk(target_path):
                relative_dir = os.path.relpath(dirpath, config["root_dir"])
                if any(excluded in relative_dir for excluded in config["exclude_list"]):
                    continue

                for filename in filenames:
                    if filename in config["exclude_list"]:
                        continue
                    if filename.endswith(".py"):
                        full_path = os.path.join(dirpath, filename)
                        relative_path = os.path.relpath(full_path, config["root_dir"])
                        if any(
                            excluded in relative_path
                            for excluded in config["exclude_list"]
                        ):
                            continue

                        comment = f"# {relative_path}:\n\n"
                        try:
                            with open(full_path, "r", encoding="utf-8") as file:
                                content = file.read()
                            if not content.startswith(comment):
                                with open(full_path, "w", encoding="utf-8") as file:
                                    file.write(comment + content)
                                print(f"Обновлен файл: {relative_path}")
                            else:
                                print(
                                    f"Пропущен (уже содержит комментарий): {relative_path}"
                                )
                        except (IOError, UnicodeDecodeError) as e:
                            print(f"Ошибка обработки файла {relative_path}: {e}")
    except Exception as e:
        print(f"Произошла общая ошибка: {e}")


def get_user_choice():
    """Получает выбор пользователя из терминала."""
    print("\nДоступные варианты:")
    print("1: Извлечение блоков кода между маркерами")
    print("2: Добавление комментариев с путями к файлам")

    while True:
        choice = input("\nВыберите вариант (введите номер): ").strip()
        if choice in ["1", "2"]:
            return choice
        print("Неверный выбор. Пожалуйста, введите 1 или 2.")


def main():
    choice = get_user_choice()

    if choice == "1":
        print("\nЗапуск варианта 1: Извлечение блоков кода между маркерами")
        process_directory()
    elif choice == "2":
        print("\nЗапуск варианта 2: Добавление комментариев с путями к файлам")
        add_file_path_comments()


if __name__ == "__main__":
    main()
