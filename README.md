# Chat
Урок 5. Помогаем клубу анонимных геймеров.  
Курс Асинхронный Python от Devman.

## Запуск
Установите зависимости
```bash
$ pip install -r requirements.txt
```

Настройте скрипт через переменные окружения
```bash
$ export SERVER_HOST="" \
  LISTEN_PORT=0 \
  SEND_PORT=0 \
  LOG_PATH="" \
  USER_HASH="" \
```

Или через аргументы командной строки
```
  -h, --help       show this help message and exit
  --host HOST      Server host
  --listen LISTEN  Server listen port
  --send SEND      Server send port
  --path PATH      Relative path to logs file
  --hash HASH      Account hash to access host
```

Запустите проект
```bash
$ python chat.py --hash <YOUR_HASH>
```
