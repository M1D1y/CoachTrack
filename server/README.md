# CoachTrack Backend

Учебный Backend на Python 3.12+, FastAPI, PostgreSQL, SQLAlchemy 2, Pydantic 2 и Alembic. React-клиент пока использует локальные демонстрационные данные и к API не подключён.

## Архитектура Backend

```text
app/
  main.py                  FastAPI, CORS, общий API-роутер
  api/                    HTTP-маршруты по предметным областям
    router.py              подключение всех девяти роутеров
    auth.py users.py athletes.py invitations.py team.py
    trainings.py injuries.py nutrition.py reports.py
  models/                 шесть SQLAlchemy-моделей, по одной на файл
  schemas/                Pydantic-схемы запросов и ответов
  services/               правила приложения и операции с данными
  db/base.py              единая декларативная Base
  db/session.py           Engine, SessionLocal и зависимость get_db
  core/config.py          настройки из окружения и .env
  core/security.py        Argon2, JWT, генерация и хеш refresh token
  core/dependencies.py    текущий пользователь, роль и доступ к спортсмену
alembic/                  версия схемы БД и её применение
```

`api` получает HTTP-запрос и вызывает сервис. `models` описывает таблицы PostgreSQL и связи. `schemas` проверяет JSON и задаёт форму ответа; эти классы не являются таблицами. `services` хранит действия и бизнес-правила: поиск, приглашения, команду, записи и отчёты. `db` создаёт одну SQLAlchemy Base и сессии. `core` содержит конфигурацию, криптографию и общие проверки доступа.

FastAPI `Depends` передаёт обработчику сессию БД и пользователя, установленного по access JWT. Роль и `trainer_id` всегда читаются из БД, а не из тела запроса. Пароли хранятся как Argon2-хеши. Access JWT действует 30 минут; непрозрачный refresh token — 7 дней. В БД хранится SHA-256 от refresh token, а обновление ротирует его.

Alembic применяет изменения структуры БД по версиям. Рефакторинг Python-модулей не изменил таблицы, поэтому существующая миграция `0001_initial.py` сохранена без изменений. `alembic/env.py` импортирует Base и все модели для `Base.metadata`.

## Запуск через Docker Compose на Linux Mint

Из каталога `server/`:

```bash
test -f .env || cp .env.example .env
python3 - <<'PY'
from pathlib import Path
import secrets

path = Path('.env')
lines = path.read_text().splitlines()
for index, line in enumerate(lines):
    if line.startswith('JWT_SECRET_KEY='):
        if line.partition('=')[2].startswith('replace_with'):
            lines[index] = 'JWT_SECRET_KEY=' + secrets.token_urlsafe(48)
        break
path.write_text('\n'.join(lines) + '\n')
path.chmod(0o600)
PY
docker compose up --build -d
docker compose ps
```

Compose поднимает PostgreSQL и Backend. Backend ждёт готовности PostgreSQL, применяет `alembic upgrade head` и запускает Uvicorn на `0.0.0.0:8000`. В контейнере `DATABASE_URL` автоматически указывает на сервис `postgres`; локальное значение из `.env` остаётся пригодным для запуска без Docker. Данные PostgreSQL сохраняются в томе `coachtrack_data` после перезапуска контейнеров.

Проверка: <http://localhost:8000/docs> и <http://localhost:8000/openapi.json>. Логи: `docker compose logs -f backend`. Остановка без удаления данных: `docker compose down`. Не запускайте `docker compose down -v`, если хотите сохранить базу. Порт PostgreSQL на хосте не публикуется; консоль БД доступна через `docker compose exec postgres psql -U coachtrack -d coachtrack`.

Для сборки образа необходим доступ Docker к PyPI. Файл `.env` не включается в образ и не должен попадать в Git. Пароль PostgreSQL `password` в Compose предназначен только для локального учебного запуска; перед размещением сервиса вне своего компьютера замените его и обновите `DATABASE_URL` контейнера.

## Запуск без Docker на Linux Mint

Установите Python 3.12+, uv и PostgreSQL. Из корня проекта:

```bash
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE USER coachtrack WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE coachtrack OWNER coachtrack;"
cd server
cp .env.example .env
# Укажите настоящий пароль БД и случайный JWT_SECRET_KEY длиной не менее 32 символов.
uv sync --extra test
uv run alembic current
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Сервер: <http://localhost:8000>. Swagger: <http://localhost:8000/docs>. OpenAPI: <http://localhost:8000/openapi.json>. Не добавляйте `.env` в Git. Значение `JWT_SECRET_KEY` из `.env.example` является заглушкой и отвергается приложением.

## Тестирование

Unit-тесты проверяют отдельные функции и Pydantic-схемы без PostgreSQL и без HTTP-запросов. Интеграционные тесты используют FastAPI TestClient, сервисы, SQLAlchemy и отдельную PostgreSQL.

```bash
cd server
uv run pytest tests/unit -v
sudo -u postgres psql -c "CREATE DATABASE coachtrack_test OWNER coachtrack;"
TEST_DATABASE_URL=postgresql+psycopg://coachtrack:password@localhost:5432/coachtrack_test uv run pytest tests/integration -v
```

Интеграционные тесты требуют `TEST_DATABASE_URL` с драйвером `postgresql+psycopg` и именем базы, заканчивающимся на `_test`. Без него они явно пропускаются. Только в проверенной тестовой БД фикстура применяет миграцию, очищает таблицы между тестами и откатывает миграцию после тестов. Unit-тесты не зависят от этой переменной. Перед запуском проверьте, что URL не указывает на рабочую БД.

Подробная матрица всех 33 маршрутов и результаты проверки находятся в [AUDIT.md](AUDIT.md).

## Сценарии и права

Спортсмен регистрируется без email и может пользоваться профилем до появления тренера. Тренер ищет его по ID или ФИО и отправляет внутреннее приглашение. Только принятие устанавливает `users.trainer_id`. При принятии строка спортсмена блокируется транзакцией PostgreSQL: две одновременные заявки не создают двух тренеров.

Тренер видит записи только действующей команды; спортсмен — только свои. `DELETE /team/athletes/{athlete_id}` снимает связь, сохраняя аккаунт, тренировки, травмы и питание. Бывший тренер сразу теряет доступ. Спортсмен может принять приглашение другого тренера.

Неделя начинается в понедельник. `week_start` принимает дату понедельника в формате YYYY-MM-DD. Процент посещаемости: `attended / (attended + missed) * 100`; `planned` в знаменатель не входит.

## API

Все пути начинаются с `/api/v1`. Ошибки: 401 для неверной авторизации, 403 для неверной роли, 404 для недоступных объектов, 409 для конфликтов, 422 для невалидного ввода.

| Метод | Путь | Роль | Назначение |
| --- | --- | --- | --- |
| POST | `/auth/register` | любой | Создать аккаунт; получить ID |
| POST | `/auth/login` | любой | Вход по ID и паролю |
| POST | `/auth/refresh` | любой | Ротация refresh token |
| POST | `/auth/logout` | пользователь | Отзыв refresh token |
| GET, PATCH | `/users/me` | пользователь | Профиль |
| GET | `/athletes` | тренер | Команда; `q` — ID или ФИО |
| GET | `/athletes/search` | тренер | Глобальный поиск; обязательный `q`, максимум 20 результатов, минимальные данные |
| GET | `/team/my-trainer` | спортсмен | Тренер или `null` |
| DELETE | `/team/my-trainer` | спортсмен | Самостоятельное открепление |
| DELETE | `/team/athletes/{athlete_id}` | тренер | Удалить из своей команды; 204 |
| POST | `/invitations` | тренер | Пригласить по `athlete_id` |
| GET | `/invitations/incoming` | спортсмен | Входящие приглашения |
| GET | `/invitations/sent` | тренер | Отправленные приглашения |
| POST | `/invitations/{id}/accept` | спортсмен | Принять |
| POST | `/invitations/{id}/reject` | спортсмен | Отклонить |
| POST | `/invitations/{id}/cancel` | тренер | Отменить своё ожидающее приглашение |
| GET, POST | `/trainings` | обе / тренер | Список и назначение; GET принимает `week_start` |
| GET, PATCH, DELETE | `/trainings/{id}` | обе / тренер | Детали, изменение, удаление |
| PATCH | `/trainings/{id}/attendance` | тренер | `{"attendance":"attended"}` |
| GET, POST | `/athletes/{athlete_id}/injuries` | обе / тренер | Список и создание травм |
| PATCH, DELETE | `/injuries/{id}` | тренер | Изменение и удаление травмы |
| GET, POST | `/athletes/{athlete_id}/nutrition` | обе / тренер | Список и создание записей питания |
| PATCH, DELETE | `/nutrition/{id}` | тренер | Изменение и удаление записи |
| GET | `/reports/summary` | обе | Сводка своей команды или себя |
| GET | `/athletes/{athlete_id}/reports/summary` | обе | Сводка доступного спортсмена |

### Быстрая проверка в Swagger

1. Зарегистрируйте тренера и спортсмена, запишите полученные ID.
2. Войдите под каждым по ID; сохраните их токены.
3. У спортсмена проверьте `/team/my-trainer` (`null`) и `/trainings` (`[]`).
4. Под тренером найдите спортсмена через `/athletes/search`, отправьте `/invitations`.
5. Под спортсменом найдите входящее приглашение и примите его.
6. Под тренером создайте тренировку, отметьте посещаемость, добавьте травму и питание.
7. Проверьте чтение и отчёты под обеими ролями.
8. Под тренером вызовите `DELETE /team/athletes/{id}`. Проверьте 204, отсутствие в команде и 404 при доступе к старым ID. Под спортсменом проверьте сохранённую историю и возможность принять приглашение другого тренера.
