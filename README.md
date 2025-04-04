# Запуск скрипта

#### Установка 
```bash
pip install pdm
pdm install
```

#### Установка необходимых библиотек
```bash
pip install fastapi uvicorn elasticsearch
```

#### Запуск на своей машине
```bash
uvicorn API_elastic:app --host 0.0.0.0 --port 8000 --reload
```

После запуска UI микросервис адоступен по адресу
```bash
http://localhost:8000/docs
```
