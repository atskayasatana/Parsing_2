import os
import re
import requests
import time

from bs4 import BeautifulSoup
from json import JSONDecodeError
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib3.exceptions import HTTPError


def check_response_json(response):
    try:
        decoded_json = response.json()
        if 'error' in decoded_json:
            raise HTTPError
    except JSONDecodeError:
        pass


def download_txt(url, payload, filename, folder='books/'):
    response = requests.get(url, params=payload)
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


def get_books_ids(url, start_page, end_page):

    books_ids = []
    for page in range(start_page, end_page + 1):
        try:
            genre_page_url = urljoin(url, f"{page}/")
            response = requests.get(genre_page_url)
            response.raise_for_status()
            check_response_json(response)
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            books_selector = ".d_book .bookimage a[href^='/b']"
            selected_books = soup.select(books_selector)
            for book in selected_books:
                books_ids.append(int(re.findall(r"\d+", book["href"])[0]))
        except HTTPError:
            print('Искомая страница не найдена.')
        except requests.exceptions.ConnectionError:
            print('Проблемы с подключением!')
            attempts_to_connect = 0
            print('Проблемы с подключением...')
            while attempts_to_connect < 15:
                time.sleep(2.5)
                attempts_to_connect += 1
            pass

    return books_ids


def download_books_w_user_params(url,
                                 books_ids,
                                 skip_txt,
                                 skip_imgs,
                                 dwnld_dir):
    downloaded_books = []

    for book_id in books_ids:
        try:
            book_url = urljoin(url, f"b{book_id}/")
            response = requests.get(book_url)
            check_for_redirect(response)
            book_description = parse_book_page(response)
            if not skip_txt:
                book_download_url = \
                    f'{urljoin("https://tululu.org/", "txt.php")}'
                book_download_params = {'id': book_id}
                book_filename = f'{book_id}. {book_description["title"]}.txt'
                book_path = download_txt(
                    book_download_url,
                    book_download_params,
                    book_filename,
                    os.path.join(dwnld_dir, 'books'))
                book_description['book_path'] = book_path
            if not skip_imgs:
                image_filename = f'{book_id}. {book_description["title"]}.jpg'
                image_path = download_img(
                    book_description["cover"],
                    image_filename,
                    os.path.join(dwnld_dir, 'images'))
                book_description['image_path'] = image_path
            downloaded_books.append(book_description)
        except HTTPError:
            print(f'Книгу {book_description["title"]} скачать не удалось')
        except requests.exceptions.ConnectionError:
            attempt_to_connect = 0
            print('Проблемы с подключением...')
            while attempt_to_connect < 15:
                time.sleep(1.5)
                attempt_to_connect += 1
            pass

    return downloaded_books
