import argparse
import json
import os.path
import pathlib
import requests

from bs4 import BeautifulSoup
from functions import check_for_redirect, download_books_w_user_params
from functions import get_books_ids
from pathlib import Path

if __name__ == '__main__':

    downloaded_books = []
    max_pages_qty = 1

    project_dir = os.path.dirname(os.path.realpath(__file__))
    default_dwnld_dir = Path(os.path.join(project_dir, 'Downloads'))


    parser = argparse.ArgumentParser(
                description='Скачиваем книги с сайта tululu.org'
                                     )
    parser.add_argument('-s',
                        '--start_page',
                        nargs='?',
                        help='С какой страницы начинаем',
                        type=int,
                        default=1)

    parser.add_argument('-e',
                        '--end_page',
                        nargs='?',
                        help='На какой странице заканчиваем',
                        type=int,
                        default=1)

    parser.add_argument('-df',
                        '--dest_folder',
                        nargs='?',
                        help='Директория для сохранения скачанных файлов',
                        type=pathlib.Path,
                        default=default_dwnld_dir)

    parser.add_argument('-sk_i',
                        '--skip_imgs',
                        help='Пропустить скачивание обложек?',
                        action='store_true')

    parser.add_argument('-sk_t',
                        '--skip_txt',
                        help='Пропустить скачивание книг?',
                        action='store_true')

    parser.add_argument('-jp',
                        '--json_path',
                        nargs='?',
                        help='Путь к JSON-файлу с книгами',
                        type=pathlib.Path)

    args = parser.parse_args()

    start_page = args.start_page
    end_page = args.end_page
    destination_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    books_json_path = args.json_path


    if not (skip_imgs or skip_txt):
        if destination_folder:
            if not os.access(os.path.dirname(destination_folder), os.W_OK):
                destination_folder = default_dwnld_dir
                print('Path to destination folder is invalid.')
                print('Download folder created using default value')
            Path(destination_folder).mkdir(parents=True, exist_ok=True)

    if not books_json_path:
        books_json_path = Path(os.path.join(destination_folder, 'books.json'))

    if not skip_txt:
        Path(os.path.join(destination_folder, 'books'))\
            .mkdir(parents=True, exist_ok=True)
    if not skip_imgs:
        Path(os.path.join(destination_folder, 'images'))\
            .mkdir(parents=True, exist_ok=True)

    url = 'https://tululu.org/l55/'
    response = requests.get(url)
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    pages = soup.select(".center .npage")

    if pages:
        max_pages_qty = int(pages[-1].text)

    if end_page > max_pages_qty:
        end_page = max_pages_qty

    books_ids = get_books_ids(url, start_page, end_page)
    downloaded_books = download_books_w_user_params('https://tululu.org',
                                                    books_ids,
                                                    skip_txt,
                                                    skip_imgs,
                                                    destination_folder)

    try:
        with open(books_json_path, "w") as books_json_file:
            json.dump(downloaded_books, books_json_file, ensure_ascii=False)
    except FileNotFoundError:
        print('JSON не может быть сохранен в указанном месте')
        print('Файл будет сохранен в директорию скачивания как books.json')
        with open(default_json_path, "w") as books_json_file:
            json.dump(downloaded_books, books_json_file, ensure_ascii=False)
