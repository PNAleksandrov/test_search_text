1. Убедитесь, что у вас установлен Python 3.6 или выше.
2. Клонируйте репозиторий gh repo clone PNAleksandrov/test_search_text
3. Создайте python3 -m venv .venv и Активируйте виртуальное окружение source .venv/bin/activate (для linux)
4. В корневой папке search_text в командной строке запустите команду docker-compose up --build
5. После запуска по адресу http://0.0.0.0:8000/docs будут доступны эндпоинты по созданию, поиску и удалению документов