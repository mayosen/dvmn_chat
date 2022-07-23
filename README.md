# Chat
Подключаемся к подпольному чату.  
Урок 4 курса Асинхронный Python от Devman.

## Зависимости
Установите зависимости
```bash
$ pip install -r requirements.txt
```

## Запуск

### listener.py
Настройте скрипт через переменные окружения
```bash
$ export SERVER_HOST="" SERVER_PORT=0 HISTORY_PATH=""
```

Или через аргументы командной строки
```
usage: listener.py [-h] [--host HOST] [--port PORT]
                   [--history HISTORY]

options:
  -h, --help         show this help message and exit
  --host HOST        Server host
  --port PORT        Server port
  --history HISTORY  Path to logs
```

Запустите проект
```bash
$ python listener.py
```

### sender.py
Настройте скрипт через переменные окружения
```bash
$ export SERVER_HOST="" SERVER_PORT=0 USER_HASH="" \
  NICKNAME="" MESSAGE=""
```

Или через аргументы командной строки
```
usage: sender.py [-h] [--host HOST] [--port PORT]
                 [--hash HASH] [--nickname NICKNAME]
                 [--message MESSAGE]

Pass exactly one option: --hash or --nickname.

options:
  -h, --help           show this help message and exit
  --host HOST          Server host
  --port PORT          Server port
  --hash HASH          Account hash to access host
  --nickname NICKNAME  Preferred nickname to register
  --message MESSAGE    Message to send

```

Запустите проект
```bash
$ python sender.py --nickname Devman --message "Vsem privet"
```
