# Wireguard_admin_bot
> Используется aiogram 3.0.0
### Бот предназначен для управления вашим wireguard сервером.
###### Сценарий работы с ботом:
 - Пользователь отправляет команду ___/start___ боту.

 ![](images/start_command.PNG)

 - Администратору приходит сообщение в телеграм с кномками "разрешить" и "запретить".

 ![](/images/access_request.PNG)

 - После запрета запись о пользователе добавится в БД с пометкой "baned", после этого бот перестанет обрабатывать сообщения этого пользователя.
(файлы конфигурации при это не генерируются)
 - После разрешения доступа для пользователя создается файл конфигурации wireguard и отправляется ботом в личные сообщения телеграм.

 ![](/images/send_file.PNG)

###### Режим администратора:
 - Для входа в режим администратора отправьте комманду ___/admin___ (она будет обработана только от пользователя с id указанным в качестве администратора при запуске бота)

 ![](/images/admin_menu.PNG)

 Меню администратора содержит:
  - Отправка оповещения об оплате.
	Пользователи которым доступ предоставляется платно помечаются соответсвующим флагом в БД, при нажатии на эту кнопку всем платным пользователям придет
	уведомление о том что подошел срок оплаты. 
  - Потребление трафика.
	Отображает статистику об использовании трафика пользователями сервера, отсортированную по количеству загруженных данных.

![](/images/stat.PNG)

  - Список реальных пользователей.
	Отображает список пользователей, которым был предоставлен доступ. Каждый элемент списка является кнопкой, которая переводит в режим работы с отдельным пользователем.
- Меню управления отдельным пользователем.
		Отображает статистику потребления трафика данным пользователем и содержит список функций.
		  - Забанить / разбанить пользователя
		  - Добавить / убрать флаг оплаты
		  - Удалить пользователя
		  - Кнопка "назад" возврат к приведущему меню

![](/images/user.PNG)

- Список заблокированных пользователей.
	Отображает аналогичный список пользователей, которым был отклонен доступ. 
	Из внутреннего функционала только удаление такого пользователя для возможности запросить доступ повторно.
- Перезапустить WG.
	Перезапускает сервис wireguard прямо по команде из телеграм.
- Закрыть.
	Закрывает меню администратора.

## Развертывание на сервере:
##### - Развертывание в контейнере Docker:
- Установить docker и docker-compose
- Создать каталоги для хранения данных контейнеров

```bash
mkdir /opt/{wg_data,pg_data}
```

Для запуска:
1. Установить Docker и Docker-compose
2. Создать директории для volume 

```bash
mkdir /opt/{wg_data,pg_data}
```

3. Создать отдельную папку для проекта

```bash
mkdir /srv/wg_bot && cd /srv/wg_bot
```

4. Создать с папке проекта файл docker-compose.yml со следующим содержимым:

``` yaml
version: '3.3'
volumes:
  pgdata:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: /opt/pg_data
  wgdata:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: /opt/wg_data
services:
  db:
    image: postgres:13-alpine
    restart: "unless-stopped"
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_USER: ${POSTGRES_USER}
    volumes:
      - "pgdata:/var/lib/postgresql/data"
  bot:
    image: mb0nd/wg_admin_bot:latest
    stop_signal: SIGINT
    restart: "unless-stopped"
    environment:
      API_TOKEN: ${API_TOKEN}
      ADMIN_ID: ${ADMIN_ID}
      PG_URL: ${PG_URL}
      LISTEN_PORT: ${LISTEN_PORT}
      HOST: ${HOST}
      PATH_TO_WG: ${PATH_TO_WG}
      TZ: ${TZ}
    ports:
      - ${LISTEN_PORT}:${LISTEN_PORT}/udp
    cap_add:
      - "NET_ADMIN"
    volumes:
      - "wgdata:${PATH_TO_WG}"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 10
    depends_on:
      - db
```

5. Создать в папке проекта файл .env со следующим содержимым (значения переменных заменить на свои):

```ini
#Postgres
POSTGRES_PASSWORD=your db_password
POSTGRES_USER=your db_user

#Bot
API_TOKEN=api_tocken
ADMIN_ID=admin_id
PG_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db/${POSTGRES_USER}
LISTEN_PORT=your wg_port
HOST=your host_ip
PATH_TO_WG=/etc/wireguard/
TZ=Europe/Moscow
```

```
- Заполняем переменные окружения:
	- POSTGRES_PASSWORD - (пароль для доступа к БД)
	- POSTGRES_USER - (имя пользователя БД)
	- API_TOKEN - (токен полученный от BotFather)
	- ADMIN_ID - (телеграм id администратора)
	- PG_URL - (URL для подключения к Postgresql)
	- LISTEN_PORT - (порт используемый wireguard)
	- HOST - (ip адрес сервера, по которому он доступен в интернете)
	- PATH_TO_WG - /etc/wireguard/ (путь установки wireguard при установке по умолчанию)
	- TZ - (временная зона)
```

6. Выполнить команду:

```bash
docker-compose up -d
```

##### - Развертывание непосредственно на сервере:
- Установить wireguard [см. для своей ОС](https://www.wireguard.com/install/)
- Установить postgresql _(создать БД и учетные данные)_ [см. для своей ОС](https://www.postgresql.org/download/)
- Клонируем репозиторий к себе на сервер и переходим в каталог проекта 
```bash
git clone https://github.com/mb0nd/wg_admin_bot.git && cd wg_admin_bot
```
- Создаем виртуальное окружение 
```bash
python -m venv venv
```
- Устанавливаем зависимости
```bash
pip install --upgrade pip && pip install -r requirements.txt
```
- Создаем bash скрипт для запуска бота _(прим. "run.sh")_ следующего содержания и заполняем переменные окружения аналогично для варианта с докером.
```bash
#!/usr/bin/env bash

source путь_к_папке_с_проектом/venv/bin/activate
export API_TOKEN=''
export ADMIN_ID=''
export PG_URL='postgresql+asyncpg://PG_USER:PG_PASSWORD@localhost/DB_NAME'
export LISTEN_PORT=''
export HOST=''
export PATH_TO_WG='/etc/wireguard/'

python3 путь_к_папке_с_проектом/bot/__main__.py
```
- Не забываем сделать скрипт исполняемым
```bash
chmod +x run.sh
```
- Зыпускаем бота
```bash
./run.sh
```