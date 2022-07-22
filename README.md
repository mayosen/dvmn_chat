# Chat
Подключаемся к подпольному чату.  
Урок 4 курса Асинхронный Python от Devman.

## Запуск
Установите зависимости
```bash
$ pip install -r requirements.txt
```
Настройте клиент через переменные окружения
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
# Или
$ python.listener.py \
  --host minechat.dvmn.org \
  --port 5000 \
  --history .
```
