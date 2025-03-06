# scripts.py

import os

# Конфигурация
CONFIG = {
    "target_dirs": {"backend"},  # Множество целевых директорий
    "exclude_list": {".env_backend", "__init__.py"},  # Множество исключений
}


def update_config(action, item_type, item):
    """
    Обновляет конфигурацию добавлением или удалением элементов.

    Args:
        action (str): 'add' или 'remove'
        item_type (str): 'target_dir' или 'exclude'
        item (str): Элемент для добавления/удаления
    """
    if item_type == "target_dir":
        target = CONFIG["target_dirs"]
    elif item_type == "exclude":
        target = CONFIG["exclude_list"]
    else:
        print(f"Неверный тип элемента: {item_type}")
        return

    if action == "add":
        target.add(item)
        print(f"Добавлено {item} в {item_type}")
    elif action == "remove":
        if item in target:
            target.remove(item)
            print(f"Удалено {item} из {item_type}")
        else:
            print(f"{item} не найдено в {item_type}")
    else:
        print(f"Неверное действие: {action}")


def add_file_path_comments(root_dir):
    """
    Добавляет комментарии с относительным путем к Python-файлам в целевых директориях.

    Args:
        root_dir (str): Корневая директория проекта
    """
    try:
        for target_dir in CONFIG["target_dirs"]:
            target_path = os.path.join(root_dir, target_dir)

            if not os.path.exists(target_path):
                print(f"Целевая директория {target_path} не найдена")
                continue

            # Рекурсивно обходим файлы в target_dir
            for dirpath, dirnames, filenames in os.walk(target_path):
                relative_dir = os.path.relpath(dirpath, root_dir)
                # Проверяем директорию на исключение
                if any(excluded in relative_dir for excluded in CONFIG["exclude_list"]):
                    continue

                for filename in filenames:
                    # Пропускаем файлы из exclude_list
                    if filename in CONFIG["exclude_list"]:
                        continue

                    if filename.endswith(".py"):
                        full_path = os.path.join(dirpath, filename)
                        relative_path = os.path.relpath(full_path, root_dir)

                        # Проверяем полный путь на исключение
                        if any(
                            excluded in relative_path
                            for excluded in CONFIG["exclude_list"]
                        ):
                            continue

                        comment = f"# {relative_path}:\n\n"

                        # Читаем файл
                        try:
                            with open(full_path, "r", encoding="utf-8") as file:
                                content = file.read()
                        except (IOError, UnicodeDecodeError) as e:
                            print(f"Ошибка чтения файла {relative_path}: {e}")
                            continue

                        # Проверяем, есть ли уже такой комментарий
                        if not content.startswith(comment):
                            # Пишем новый контент
                            try:
                                with open(full_path, "w", encoding="utf-8") as file:
                                    file.write(comment + content)
                                print(f"Обновлен файл: {relative_path}")
                            except IOError as e:
                                print(f"Ошибка записи в файл {relative_path}: {e}")
                        else:
                            print(
                                f"Пропущен (уже содержит комментарий): {relative_path}"
                            )
    except Exception as e:
        print(f"Произошла общая ошибка: {e}")


if __name__ == "__main__":
    project_root = "."  # Текущая директория

    # Вывод текущей конфигурации
    print("\nТекущая конфигурация:")
    print(f"Целевые директории: {CONFIG['target_dirs']}")
    print(f"Исключения: {CONFIG['exclude_list']}\n")

    # Запуск обработки
    add_file_path_comments(project_root)
