import requests


def get_market_news():

    try:

        url = "https://newsapi.org/v2/everything?q=bist&language=en&sortBy=publishedAt&apiKey=demo"

        response = requests.get(url)

        data = response.json()

        titles = []

        for article in data.get("articles", [])[:10]:

            titles.append(article["title"])

        return titles

    except:

        return []
