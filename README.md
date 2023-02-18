# Парсинг онлайн библиотеки tululu.org

Данный скрипт скачивает книги с сайта tululu.org из раздела "Фантастика" с учетом пользовательских настроек:

- начальная страница для скачивания

- конечная страница скачивания

- пользовательская папка для скачивания

- скачивать книги, обложки или только JSON c данными о книгах

## Требования

Для запуска нужен Python версии не ниже 3, а также библиотеки из файла requirements.txt 

Установка зависимостей:
```
pip install -r requirements.txt
```

Запуск скрипта:

```
python parce_tululu_category.py
```

#### Пользовательские параметры

Пользователь может при запуске задать свои параметры для скачивания:

- '-s', '--start_page' - начальная страница для скачивания, по умолчанию это первая страница

- '-e', '--end_page', - конечная страница для скачивания, по умолчанию это первая страница

- '-df', '--dest_folder' - директория, в которую будут скачиваться книги и/или обложки книг

- '-sk_i', '--skip_imgs' - если указан, то обложки к книгам скачиваться не будут

- '-sk_t','--skip_txt' - если указан, то не скачиваем книги


- '-jp', '--json_path' - путь к файлу JSON с информацией о книгах


                  





