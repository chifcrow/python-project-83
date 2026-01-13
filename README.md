# Анализатор страниц

[![SonarQube](https://img.shields.io/badge/SonarQube-passing-brightgreen?logo=sonarqube)](https://www.sonarqube.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Hexlet](https://img.shields.io/badge/Hexlet-educational-blueviolet)](https://hexlet.io)

### Статус тестов и линтера Hexlet:
[![Actions Status](https://github.com/chifcrow/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/chifcrow/python-project-83/actions)

**Анализатор страниц** — учебный веб-проект на Flask, реализованный в рамках курса Hexlet.  
Приложение позволяет добавлять сайты, выполнять их проверку на доступность и проводить базовый SEO-анализ (H1, Title, Description).

Проект развёрнут в продакшене и полностью покрыт автоматическими проверками Hexlet.

---

## Возможности

- добавление сайтов с валидацией и нормализацией URL
- проверка доступности сайта (HTTP-запрос)
- сохранение кода ответа
- SEO-анализ страницы:
  - `<h1>`
  - `<title>`
  - `<meta name="description">`
- история проверок для каждого сайта
- отображение последней проверки в общем списке
- обработка ошибок без падения приложения
- интерфейс на Bootstrap, соответствующий эталону Hexlet

---

## Технологии

- **Python 3.10+**
- **Flask**
- **PostgreSQL**
- **Requests**
- **BeautifulSoup**
- **Bootstrap 5**
- **Ruff** (линтинг)
- **Docker / Docker Compose** (локальная БД)
- **Render** (деплой)

---

## Установка и запуск (локально)

### 1. Клонирование репозитория

```bash
git clone https://github.com/chifcrow/python-project-83.git
cd python-project-83
```

### 2. Установка зависимостей

```bash
make install
```

### 3. Настройка переменных окружения

Создайте файл .env на основе примера:

```bash
cp .env.example .env
```

Укажите DATABASE_URL для локальной базы данных.

## Запуск PostgreSQL (через Docker)

```bash
docker compose up -d
```

Применение схемы БД:

```bash
cat database.sql | docker exec -i page_analyzer_db \
  psql -U page_analyzer -d page_analyzer
```

## Запуск приложения

```bash
make dev
```

Приложение будет доступно по адресу:

http://127.0.0.1:5000

## Полезные команды

### Линтинг

```bash
make lint
```

### Тесты

```bash
make test
```
### Деплой

Проект автоматически разворачивается на Render с применением SQL-схемы на этапе сборки (build.sh).

## Структура проекта

```bash
python-project-83/
├── page_analyzer/
│   ├── app.py
│   ├── config.py
│   ├── db.py
│   └── templates/
├── database.sql
├── build.sh
├── render.yaml
├── docker-compose.yml
├── pyproject.toml
├── ruff.toml
├── Makefile
└── README.md
```

## Статус проекта

Проект завершён и соответствует всем требованиям курса Hexlet.
Код чистый, структура прозрачная, автотесты проходят успешно.

## Лицензия

Учебный проект. Используется в образовательных целях.