import argparse
import os
import time

import requests

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib3.exceptions import HTTPError


def download_txt(url, payload, filename, folder='books/'):

    response = requests.get(url, params=payload)
    print(response.url)
    response.raise_for_status()
    check_for_redirect(response)
    sanitized_filename = sanitize_filename(filename)
    book_path = os.path.join(folder, sanitized_filename)
    with open(book_path, 'wb') as file:
        file.write(response.content)
    return book_path


def download_img(url, filename, folder='images/'):

    response = requests.get(url)
    response.raise_for_status()
    sanitized_filename = sanitize_filename(filename)
    book_image_path = os.path.join(folder, sanitized_filename)
    with open(book_image_path, 'wb') as file:
        file.write(response.content)
    return book_image_path


def parse_book_page(response):

    soup = BeautifulSoup(response.text, 'lxml')


    title, author = soup.find('h1').text.replace('\xa0', '').split('::')
    author = author.strip()
    title = title.strip()


    raw_comments = soup.find_all('div', class_='texts')
    comments = [comment.find('span').text for comment in raw_comments]


    raw_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in raw_genres]



    img_short_path = soup.find('div', class_='bookimage').find('img')['src']
    img_path = urljoin(response.url, img_short_path)

    book_description = {
        'author': author,
        'title': title,
        'genres': genres,
        'comments': comments,
        'cover': img_path
    }

    return book_description


def check_for_redirect(response):
    if response.history:
        raise HTTPError


