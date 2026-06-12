from mysql_connector import (
    get_all_categories,
    get_year_range,
    search_by_keyword,
    count_by_keyword,
    search_by_category_and_year,
    count_by_category_and_year,
)
from formatter import format_films, format_categories, _base_table
from log_writer import save_search
from log_stats import get_top_5_queries, get_last_5_queries
from rich.console import Console
from rich.panel import Panel

console = Console()

def print_menu():
    console.print(
        Panel(
            "1. Поиск по ключевому слову\n"
            "2. Поиск по жанру и году выхода\n"
            "3. Популярные запросы (топ-5)\n"
            "4. Последние запросы (5)\n"
            "5. Выход",
            title="Поиск фильмов",
            title_align="center",
            border_style="bright_blue",
            padding=(1, 4),
        )
    )


def get_rating_filter():
    """
    Получить возраст ребёнка от пользователя и определить разрешённые рейтинги.
    Возвращает введённый возраст как текст и список разрешённых рейтингов.
    """
    child_age_input = input(
        "Будете смотреть с детьми? Если да, введите возраст младшего ребёнка. "
        "Если нет, просто нажмите Enter: "
    )

    allowed_ratings = None
    child_age_text = child_age_input.strip()

    if child_age_text:
        try:
            child_age = int(child_age_text)
            if child_age < 13:
                allowed_ratings = ["G", "PG"]
            elif 13 <= child_age < 17:
                allowed_ratings = ["G", "PG", "PG-13", "R"]
            else:
                allowed_ratings = None
        except ValueError:
            print("Возраст введён некорректно. Поиск будет выполнен без учёта рейтинга.")
            allowed_ratings = None

    return child_age_text, allowed_ratings


def search_by_keyword_menu():
    keyword = input("Введите ключевое слово для поиска: ").strip()
    if not keyword:
        print("Ключевое слово не указано.")
        return

    search_mode = input(
        "Искать только по названию фильма? "
        "Нажмите Enter для поиска только по названию, "
        "или введите 'd' для поиска ещё и по описанию: "
    ).strip().lower()

    include_description = search_mode == "d"

    child_age_text, allowed_ratings = get_rating_filter()

    offset = 0
    limit = 10

    search_params = {
        "keyword": keyword,
        "include_description": include_description,
    }
    if child_age_text:
        search_params["child_age_input"] = child_age_text
    if allowed_ratings is not None:
        search_params["allowed_ratings"] = allowed_ratings

    results_count = count_by_keyword(
        keyword,
        allowed_ratings=allowed_ratings,
        include_description=include_description,
    )
    save_search("keyword", search_params, results_count)

    while True:
        films = search_by_keyword(
            keyword,
            offset,
            limit,
            allowed_ratings=allowed_ratings,
            include_description=include_description,
        )
        if not films:
            if offset == 0:
                print("Ничего не найдено.")
            else:
                print("Дальше результатов нет.")
            return

        print(f"\nРезультаты {offset + 1}–{offset + len(films)}:")
        console.print(format_films(films))

        more_films = search_by_keyword(
            keyword,
            offset + limit,
            1,
            allowed_ratings=allowed_ratings,
            include_description=include_description,
        )
        if not more_films:
            print("\nВсе результаты показаны.")
            return

        while True:
            choice_raw = input("\nПоказать следующие 10 результатов? (y/n): ")
            choice = choice_raw.strip().lower()

            if choice == "n":
                return

            if choice in ("", "y"):
                offset += limit
                break

            print("Введите 'y' или 'n'!")


def search_by_category_year_menu():
    categories = get_all_categories()
    console.print(format_categories(categories))

    min_year, max_year = get_year_range()

    category_input = input("Введите жанр (можно 2-3 первые буквы): ").strip()
    if not category_input:
        print("Жанр не указан.")
        return

    category_input_lower = category_input.lower()

    matched_categories = [
        category for category in categories
        if category.lower().startswith(category_input_lower)
    ]

    if not matched_categories:
        print(f"Жанр '{category_input}' не найден.")
        return

    if len(matched_categories) > 1:
        print("Найдено несколько жанров:")
        console.print(format_categories(matched_categories))
        print("Введите больше букв или полное название жанра.")
        return

    category = matched_categories[0]

    child_age_text, allowed_ratings = get_rating_filter()

    while True:
        year_input = input(
            f"\nУ нас есть фильмы, вышедшие с {min_year} по {max_year} год.\n"
            f"Введите нужный Вам год или диапазон (например, 2005 2012)\n"
            f"или просто нажмите Enter, чтобы искать по всем годам: "
        ).strip()

        if not year_input:
            min_year_input = min_year
            max_year_input = max_year
            break

        parts = year_input.split()

        if len(parts) == 1:
            try:
                year = int(parts[0])
                min_year_input = year
                max_year_input = year
            except ValueError:
                print("Некорректный год.")
                continue

        elif len(parts) == 2:
            try:
                min_year_input = int(parts[0])
                max_year_input = int(parts[1])
            except ValueError:
                print("Некорректный год.")
                continue

        else:
            print("Некорректный ввод. Используйте формат: 2005 2012 для диапазона или просто 2010")
            continue

        if min_year_input > max_year_input:
            print("Нижняя граница года не может быть больше верхней.")
            continue

        if min_year_input < min_year or max_year_input > max_year:
            print(f"Годы должны быть в диапазоне от {min_year} до {max_year}.")
            continue

        break

    offset = 0
    limit = 10

    search_params = {
        "category": category,
        "min_year": min_year_input,
        "max_year": max_year_input,
    }
    if child_age_text:
        search_params["child_age_input"] = child_age_text
    if allowed_ratings is not None:
        search_params["allowed_ratings"] = allowed_ratings

    results_count = count_by_category_and_year(
        category,
        min_year_input,
        max_year_input,
        allowed_ratings=allowed_ratings,
    )
    save_search("category_year", search_params, results_count)

    while True:
        films = search_by_category_and_year(
            category,
            min_year_input,
            max_year_input,
            offset,
            limit,
            allowed_ratings=allowed_ratings,
        )
        if not films:
            if offset == 0:
                print("Ничего не найдено.")
            else:
                print("Больше результатов нет.")
            return

        print(f"\nРезультаты {offset + 1}–{offset + len(films)}:")
        console.print(format_films(films, title=f"Найденные фильмы в жанре {category}"))

        more_films = search_by_category_and_year(
            category,
            min_year_input,
            max_year_input,
            offset + limit,
            1,
            allowed_ratings=allowed_ratings,
        )
        if not more_films:
            print("\nВсе результаты показаны.")
            return

        while True:
            choice_raw = input("\nПоказать следующие 10 результатов? (y/n): ")
            choice = choice_raw.strip().lower()

            if choice == "n":
                return
            if choice in ("", "y"):
                offset += limit
                break

            print("Введите 'y' или 'n'!")


def show_top_queries():
    top = get_top_5_queries()
    if not top:
        print("Запросов нет.")
        return

    table = _base_table("5 самых популярных запросов")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Запрос", style="green")
    table.add_column("Количество", justify="center")

    for i, (query, count) in enumerate(top, start=1):
        table.add_row(str(i), query, str(count))

    console.print(table)


def show_last_queries():
    last = get_last_5_queries()
    if not last:
        print("Запросов нет.")
        return

    table = _base_table("Последние запросы")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Запрос", style="green")
    table.add_column("Время", style="yellow")

    for i, (query, ts) in enumerate(last, start=1):
        if ts:
            ts_text = ts.strftime("%Y-%m-%d %H:%M")
        else:
            ts_text = ""

        table.add_row(str(i), query, ts_text)

    console.print(table)


def main():
    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            search_by_keyword_menu()
        elif choice == "2":
            search_by_category_year_menu()
        elif choice == "3":
            show_top_queries()
        elif choice == "4":
            show_last_queries()
        elif choice == "5":
            print("Выход.")
            break
        else:
            print("Некорректный выбор.")


if __name__ == "__main__":
    main()