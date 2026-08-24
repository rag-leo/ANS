import json


ARTICLES_FILE = (
    "backend/data/articles.json"
)


def get_articles():

    try:

        with open(
            ARTICLES_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except FileNotFoundError:

        return []