import pymysql
from config import dbconfig


def get_connection():
    """Подключение к MySQL (sakila)"""
    return pymysql.connect(**dbconfig)


def get_all_categories():
    """Получить список всех жанров (категорий)"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM category ORDER BY name")
            return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_year_range():
    """Получить минимальный и максимальный год выпуска фильмов"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MIN(release_year), MAX(release_year) FROM film")
            result = cursor.fetchone()
            return result[0], result[1]
    finally:
        conn.close()


def search_by_keyword(
    keyword,
    offset=0,
    limit=10,
    allowed_ratings=None,
    include_description=False,
):
    """
    Поиск фильмов по ключевому слову в названии.
    Если include_description=True, поиск также выполняется по описанию.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    title,
                    release_year,
                    length,
                    CASE rating
                        WHEN 'G' THEN 'Для всех возрастов'
                        WHEN 'PG' THEN 'Есть некоторые сомнения насчёт детей'
                        WHEN 'PG-13' THEN 'Не подходит детям до 13 лет'
                        WHEN 'R' THEN 'Детям до 17 можно только вместе со взрослыми'
                        WHEN 'NC-17' THEN 'До 17 лет - ни в коем случае!'
                    END AS rating_description,
                    description
                FROM film
                WHERE (
                    LOWER(title) LIKE LOWER(%s)
            """

            params = [f"%{keyword}%"]

            if include_description:
                sql += " OR LOWER(description) LIKE LOWER(%s)"
                params.append(f"%{keyword}%")

            sql += ")"

            if allowed_ratings is not None and len(allowed_ratings) > 0:
                placeholders = ", ".join(["%s"] * len(allowed_ratings))
                sql += f" AND rating IN ({placeholders})"
                params.extend(allowed_ratings)

            sql += """
                ORDER BY title
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])

            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def count_by_keyword(keyword, allowed_ratings=None, include_description=False):
    """Посчитать общее количество фильмов для поиска по ключевому слову."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT COUNT(*)
                FROM film
                WHERE (
                    LOWER(title) LIKE LOWER(%s)
            """

            params = [f"%{keyword}%"]

            if include_description:
                sql += " OR LOWER(description) LIKE LOWER(%s)"
                params.append(f"%{keyword}%")

            sql += ")"

            if allowed_ratings is not None and len(allowed_ratings) > 0:
                placeholders = ", ".join(["%s"] * len(allowed_ratings))
                sql += f" AND rating IN ({placeholders})"
                params.extend(allowed_ratings)

            cursor.execute(sql, params)
            return cursor.fetchone()[0]
    finally:
        conn.close()


def search_by_category_and_year(
    category, min_year, max_year, offset=0, limit=10, allowed_ratings=None
):
    """
    Поиск фильмов по жанру и диапазону годов.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    f.title,
                    f.release_year,
                    f.length,
                    CASE f.rating
                        WHEN 'G' THEN 'Для всех возрастов'
                        WHEN 'PG' THEN 'Есть некоторые сомнения насчёт детей'
                        WHEN 'PG-13' THEN 'Не подходит детям до 13 лет'
                        WHEN 'R' THEN 'Детям до 17 можно только вместе со взрослыми'
                        WHEN 'NC-17' THEN 'До 17 лет - ни в коем случае!'
                    END AS rating_description,
                    f.description
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE c.name = %s
                  AND f.release_year BETWEEN %s AND %s
            """

            params = [category, min_year, max_year]

            if allowed_ratings is not None and len(allowed_ratings) > 0:
                placeholders = ", ".join(["%s"] * len(allowed_ratings))
                sql += f" AND f.rating IN ({placeholders})"
                params.extend(allowed_ratings)

            sql += """
                ORDER BY f.title
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])

            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def count_by_category_and_year(category, min_year, max_year, allowed_ratings=None):
    """Посчитать общее количество фильмов для поиска по жанру и годам."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT COUNT(*)
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE c.name = %s
                  AND f.release_year BETWEEN %s AND %s
            """

            params = [category, min_year, max_year]

            if allowed_ratings is not None and len(allowed_ratings) > 0:
                placeholders = ", ".join(["%s"] * len(allowed_ratings))
                sql += f" AND f.rating IN ({placeholders})"
                params.extend(allowed_ratings)

            cursor.execute(sql, params)
            return cursor.fetchone()[0]
    finally:
        conn.close()