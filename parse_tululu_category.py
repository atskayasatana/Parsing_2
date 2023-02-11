import argparse
import json
import os.path
import re

import requests

from bs4 import BeautifulSoup
from functions import parse_book_page, download_img, download_txt, check_for_redirect
from pathlib import Path
from urllib.parse import urljoin
from urllib3.exceptions import HTTPError


if __name__ == '__main__':
    downloaded_books = []
    max_pages_qty = 1

    parser = argparse.ArgumentParser(description='Скачиваем книги с сайта tululu.org')
    parser.add_argument('start_page', nargs='?',help='С какой страницы начинаем', type=int, default=1)
    parser.add_argument('end_page', nargs='?', help='На какой странице заканчиваем', type=int, default=4)
    args = parser.parse_args()
    start_page =args.start_page
    end_page = args.end_page

    url = 'https://tululu.org/l55/'
    response = requests.get(url)
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    pages = soup.select(".center .npage")
    if pages:
        max_pages_qty = pages[-1].text

    if end_page>max_pages_qty:
        end_page = max_pages_qty

    project_dir = os.path.dirname(os.path.realpath(__file__))
    Path(os.path.join(project_dir, 'books')).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(project_dir, 'images')).mkdir(parents=True, exist_ok=True)

    for i in range(start_page, end_page+1):
        try:
            genre_page_url = urljoin(url, f"{i}/")
            print('Жанр:', genre_page_url)
            response = requests.get(genre_page_url)
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            books_selector = ".d_book .bookimage a[href^='/b']"
            selected_books = soup.select(books_selector)
            print("Книг найдено:", len(selected_books))
            for book in selected_books:
                book_id = re.findall(r"\d+", book["href"])[0]
                print('book_id:', book_id)
                book_url = urljoin("https://tululu.org", f"b{book_id}/")
                print('book_url:', book_url)
                response = requests.get(book_url)
                print(response.url)
                check_for_redirect(response)
                book_description = parse_book_page(response)
                book_download_url = f'{urljoin("https://tululu.org/","txt.php")}'
                book_download_params = {'id': book_id}
                book_filename = f'{book_id}. {book_description["title"]}.txt'
                image_filename = f'{book_id}.jpg'
                book_path = download_txt(book_download_url, book_download_params, book_filename)
                image_path = download_img(book_description["cover"], image_filename)
                book_description['book_path'] = book_path
                book_description['image_path'] = image_path
                print(book_path)
                print(image_path)
                downloaded_books.append(book_description)
        except HTTPError:
            print('Проблема при скачивании!')

    with open("books/books_info.json", "w") as books_json_file:
        json.dump(downloaded_books, books_json_file, ensure_ascii=False)
