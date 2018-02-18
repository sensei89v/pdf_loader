# pdf_loader
Сервер хранения PDF файлов. Написан на Python 3. Разработка велась на Ubuntu 16.04 (32bit)

## Подготовка к запуску
1) Поставьте python3, pip и virtualenv
2) Настройка виртуальной среды. Выполните `virtualenv -p python3 <virtualenv_dir>`
3) Перейдите в виртуальную среду. `source <virtualenv_dir>/bin/activate`
4) Убедитесь, что в системе установлена утилита convert. Для Ubuntu это пакет imagemagick.
5) Создайте БД. Выполните `python init_db.py <dbpath>`
6) Добавьте пользователей в БД. Выполните `python add_user_to_db.py <dbpath> <login> <password>`

## Запуск
Выполните `python run.py <port> <dbpath>`

## Примечания
Использование утилиты `convert` для конвертации pdf в png является лютым костылем. Используется именно этот
метод в отличии от использования классов Image из пакетов PIL и wand, т.к. работа вышеупомянутыми средствами
приводит к segmentation fault из-за двойного освобождения памяти где-то в своих глубинах. Решить проблему
за адекватное время не удалось - поэтому примен сей "костыль".

## TODO:
* Сделать нормальные куки, чтобы хранился в cookies не user_id, а UUID сессии, Сделать cookie более длительными
* Добавить проверку что загруженный файл - действительно PDF

* Сделать Download и upload файла блоками
* Сделать разбиение на страницы в таблице pdf файлов
* Улучшить работу с сессиями в файле db.py, запихнув их в декоратор
* Добавить xcfr токен

* Запихать запуск в docker
* Добавить тесты
* Добавить механизм регистрации пользователей через web
* Нанять дизайнера и хорошего фронтэндщика чтобы сделать нормальную "морду" для сервиса
* Убрать костыль с использованием утилиты `convert`
* Сделать сервис параллельным либо асинхронным, а не как сейчас
