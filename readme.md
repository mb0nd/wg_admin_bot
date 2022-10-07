Этот телеграм бот написан с использованием aiogram3.x.
Бот предназначен для управления вашим wireguard сервером.
Сценарий:
 - Пользователь отправляет команду /start боту.
 - Администратору приходит сообщение в телеграм с кномками "разрешить" и "запретить".
 - После запрета запись о пользователе добавится в БД с пометкой "baned", после этого бот перестанет обрабатывать сообщения этого пользователя.
(файлы конфигурации при это не генерируются)
 - После разрешения доступа для пользователя создается файл конфигурации wireguard и отправляется ботом в личные сообщения телеграм.

Режим администратора:
 - Для входа в режим администратора отправьте комманду /admin (она будет обработана только от пользователя с id указанным в качестве 
администратора при запуске бота)
 Меню администратора содержит:
  - Отправка оповещения об оплате.
	Пользователи которым доступ предоставляется платно помечаются соответсвующим флагом в БД, при нажатии на эту кнопку всем платным пользователям придет
	уведомление о том что подошел срок оплаты. 
  - Потребление трафика.
	Отображает статистику об использовании трафика пользователями сервера.
  - Список реальных пользователей.
	Отображает список пользователей, которым был предоставлен доступ. Каждый элемент списка является кнопкой, которая переводит в режим работы с отдельным пользователем.
	  - Меню управления отдельным пользователем.
		Отображает статистику потребления трафика данным пользователем и содержит список функций.
		  - Забанить / разбанить пользователя
		  - Добавить / убрать флаг оплаты
		  - Удалить пользователя
		  - Кнопка "назад" возврат к приведущему меню
  - Список заблокированных пользователей.
	Отображает аналогичный список пользователей, которым был отклонен доступ. 
	Из внутреннего функционала только удаление такого пользователя для возможности запросить доступ повторно.
  - Перезапустить WG.
	Перезапускает сервис wireguard прямо по команде из телеграм.
  - Закрыть.
	Закрывает меню администратора.

Installation:
    Docker:
- Install docker and docker-compose
- Clone the repository to your server
- Copy next to docker-compose-example named docker-compose
- Fill in impossible variables in it:
- POSTGRES_PASSWORD (Password from the database)
- POSTGRES_USER (Database username)
- API_TOKEN (Telegram token received from BotFather)
- ADMIN_ID (Administrator's Telegram id)
- PG_URL=postgresql+asyncpg://{your db_user}:{your db_password}@db/{your db_user}
- LISTEN_PORT (Port to be used by wireguard)
- HOST (ip address of your server, by access it is available on the Internet)
- PATH_TO_WG=/etc/wireguard/ (wireguard installation path, change if not default installation)
- Run docker-compose up --build

Server:
- install wireguard
- install postgresql
- clone this repository
- make venv
- install requirements
- create shell script (example "run.sh")
- chmod +x run.sh
		#!/usr/bin/env bash

		source YOUR_PATH/venv/bin/activate
		export API_TOKEN=''
		export ADMIN_ID=''
		export PG_URL='postgresql+asyncpg://PG_USER:PG_PASSWORD@localhost/DB_NAME'
		export LISTEN_PORT=''
		export HOST=''
		export PATH_TO_WG='/etc/wireguard/'

		python3 YOUR_PATH/bot/__main__.py
- ./run.sh