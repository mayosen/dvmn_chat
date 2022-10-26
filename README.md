# Chat
Урок 5. Помогаем клубу анонимных геймеров.  
Курс "Асинхронный Python" от [Devman](https://dvmn.org/modules/async-python/).

## Регистрация в чате
Для регистрации используется вспомогательный скрипт.  
Настройте его через переменные окружения или аргументы CLI.

```bash
$ export SERVER_HOST="example.com" PORT=10
$ python register.py
```
После запуска введите желаемый никнейм.  
Полученные учетные данные будут сохранены в файл `credentials.json`.

## Запуск
Установите зависимости
```bash
$ pip install -r requirements.txt
```

Настройте скрипт через переменные окружения или аргументы CLI
```bash
$ export \
      SERVER_HOST="example.com" \
      LISTEN_PORT=10 \
      SEND_PORT=20 \
      LOG_PATH="." \
      USER_HASH="hash"
```

Запустите проект
```bash
$ python chat.py
```
