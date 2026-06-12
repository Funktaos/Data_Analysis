from rich import box
from rich.table import Table
from rich.text import Text

def _base_table(title: str) -> Table:
    """
    Создаём базовую таблицу Rich с заданным title
    """
    return Table(
        title=title,
        show_header=True,
        header_style="bold bright_magenta",
        title_style="bold bright_cyan",
        border_style="bright_blue",
        box=box.SQUARE,
        show_lines=True,
    )

def format_films(films, title="Найденные фильмы"):
    """
    Форматировать список фильмов в таблицу Rich.
    films: список кортежей
           (title, release_year, length, rating_description, description).
    В заголовке таблицы результатов писать, если поиск по keywords - "Найденные фильмы",
    а если поиск по жанрам - "Найденные фильмы в жанре {Music}"
    """
    if not films:
        return "Ничего не найдено."

    table = _base_table(title)

    table.add_column("Название фильма", style="cyan", no_wrap=True)
    table.add_column("Год", justify="center")
    table.add_column("Длительность", justify="center")
    table.add_column("Рейтинг", style="green")
    # 5-я колонка — описание, как рейтинг, но dim (визуально «мельче»)
    table.add_column("Описание", style="dim green")

    for title, year, length, rating_description, description in films:
        desc_text = Text(description or "", style="dim green")
        table.add_row(
            str(title),
            str(year),
            f"{length} мин.",
            str(rating_description),
            desc_text,
        )
    return table


def format_categories(categories):
    """
    Форматировать список жанров в таблицу Rich.
    categories: список названий жанров
    """
    if not categories:
        return "Жанров нет."

    table = _base_table("Все жанры")
    table.show_header = False

    table.add_column(justify="right", style="cyan")
    table.add_column(style="green")

    for i, cat in enumerate(categories, start=1):
        table.add_row(str(i), cat)

    return table