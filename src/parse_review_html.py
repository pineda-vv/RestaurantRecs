from pymongo import MongoClient
from bs4 import BeautifulSoup
import pyspark as ps


def load_html_from_db():
    client = MongoClient()
    yelp_db = client['yelp']
    reviews_table = yelp_db['reviews']

    return (
        (item['yelp_id'], item['html_str'])
        for item in reviews_table.find()
    )


def parse_html(raw_html_data):
    user_list = []
    user_id_list = []
    rating_list = []
    count = 0
    for restaurant_id, html_str in raw_html_data:
        soup = BeautifulSoup(html_str, 'html.parser')

        page = int(
            soup.find('div', class_='page-of-pages')
            .getText()
            .split()[1]
        )

        num_pages = int(
            soup.find('div', class_='page-of-pages')
            .getText()
            .split()[3]
        )

        sidebars = soup.find_all('div', class_='review-sidebar')
        for sidebar in sidebars:
            users = sidebar.find_all('a', class_='user-display-name')
            for user in users:
                user_list.append(user.get_text())
                user_id_list.append(user['href'].split('=')[1])

        reviews = soup.find_all('div', class_='review-content')
        for review in reviews:
            ratings = review.find_all('div', class_='rating-large')
            for rating in ratings:
                rating_list.append(int(rating['title'].split()[0].split('.')[0]))

        print(restaurant_id)
        print('{}/{}'.format(page, num_pages))
        print(len(ratings))

        count = count + 1
        if count == 2:
            break

    for user, user_id, rating in zip(user_list, user_id_list, rating_list):
        print(rating, user_id, user)

    exit()


def main():
    raw_html_data = load_html_from_db()
    parse_html(raw_html_data)


if __name__ == '__main__':
    main()