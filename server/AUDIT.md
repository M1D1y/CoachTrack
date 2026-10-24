# Аудит Backend после структурного рефакторинга

Дата: 2026-10-22. Проверка проводилась в текущем рабочем окружении без доступного PyPI и PostgreSQL.

## Результат

- Статически сверены 33 маршрута: HTTP-метод, путь, имя обработчика, модель ответа, код ответа и тег совпадают со снимком до рефакторинга.
- Подтверждены шесть имён таблиц и неизменный SHA-256 миграции `0001_initial.py` (`8aa93fe8812c6cdbc29499bfc2310a3d32a6906fa36af1c5a92e8537cf175b1f`).
- Все Python-файлы проходят синтаксический разбор. Статический граф внутренних импортов не содержит циклов.
- `npm run build` для клиента прошёл. Исходники frontend не изменялись.
- Проверка исполнения API, Swagger, SQLAlchemy metadata, Alembic и тестов **не проведена**: `uv sync --extra test` не смог загрузить `argon2-cffi` из PyPI из-за DNS; кеш `uv` не содержит `alembic`. Локального `psql` нет, доступ к Docker daemon запрещён. Пропущенные тесты не считаются пройденными.

## Покрытие каждого маршрута

Для каждого публичного маршрута есть интеграционный сценарий в указанном модуле. Состояние исполнения всех строк — **не запущен** до появления зависимостей и отдельной PostgreSQL.

| Метод | Путь | Интеграционный модуль | Исполнение |
| --- | --- | --- | --- |
| GET | `/api/v1/athletes` | `test_athletes.py` | Не запущен |
| GET | `/api/v1/athletes/search` | `test_athletes.py` | Не запущен |
| GET | `/api/v1/athletes/{athlete_id}/injuries` | `test_injuries.py` | Не запущен |
| POST | `/api/v1/athletes/{athlete_id}/injuries` | `test_injuries.py` | Не запущен |
| GET | `/api/v1/athletes/{athlete_id}/nutrition` | `test_nutrition.py` | Не запущен |
| POST | `/api/v1/athletes/{athlete_id}/nutrition` | `test_nutrition.py` | Не запущен |
| GET | `/api/v1/athletes/{athlete_id}/reports/summary` | `test_reports.py` | Не запущен |
| POST | `/api/v1/auth/login` | `test_auth.py` | Не запущен |
| POST | `/api/v1/auth/logout` | `test_auth.py` | Не запущен |
| POST | `/api/v1/auth/refresh` | `test_auth.py` | Не запущен |
| POST | `/api/v1/auth/register` | `test_auth.py` | Не запущен |
| DELETE | `/api/v1/injuries/{injury_id}` | `test_injuries.py` | Не запущен |
| PATCH | `/api/v1/injuries/{injury_id}` | `test_injuries.py` | Не запущен |
| POST | `/api/v1/invitations` | `test_invitations.py` | Не запущен |
| GET | `/api/v1/invitations/incoming` | `test_invitations.py` | Не запущен |
| GET | `/api/v1/invitations/sent` | `test_invitations.py` | Не запущен |
| POST | `/api/v1/invitations/{invitation_id}/accept` | `test_invitations.py` | Не запущен |
| POST | `/api/v1/invitations/{invitation_id}/cancel` | `test_invitations.py` | Не запущен |
| POST | `/api/v1/invitations/{invitation_id}/reject` | `test_invitations.py` | Не запущен |
| DELETE | `/api/v1/nutrition/{nutrition_id}` | `test_nutrition.py` | Не запущен |
| PATCH | `/api/v1/nutrition/{nutrition_id}` | `test_nutrition.py` | Не запущен |
| GET | `/api/v1/reports/summary` | `test_reports.py` | Не запущен |
| DELETE | `/api/v1/team/athletes/{athlete_id}` | `test_team.py` | Не запущен |
| DELETE | `/api/v1/team/my-trainer` | `test_team.py` | Не запущен |
| GET | `/api/v1/team/my-trainer` | `test_team.py` | Не запущен |
| GET | `/api/v1/trainings` | `test_trainings.py` | Не запущен |
| POST | `/api/v1/trainings` | `test_trainings.py` | Не запущен |
| DELETE | `/api/v1/trainings/{training_id}` | `test_trainings.py` | Не запущен |
| GET | `/api/v1/trainings/{training_id}` | `test_trainings.py` | Не запущен |
| PATCH | `/api/v1/trainings/{training_id}` | `test_trainings.py` | Не запущен |
| PATCH | `/api/v1/trainings/{training_id}/attendance` | `test_trainings.py` | Не запущен |
| GET | `/api/v1/users/me` | `test_auth.py` | Не запущен |
| PATCH | `/api/v1/users/me` | `test_auth.py` | Не запущен |

Дополнительно `test_permissions.py` проверяет доступ между ролями и командами; `test_team.py` проходит жизненный цикл с сохранением истории; `test_invitations.py` запускает два принятия через независимые TestClient и сессии.

## Замечания, исправленные по ходу аудита

1. Устранены дублирующие общие Python-файлы, конфликтующие с одноимёнными пакетами.
2. Alembic переведён на `app.db.base.Base` и явную регистрацию всех моделей; миграция не переписывалась.
3. Тестовая PostgreSQL проверяется до `TRUNCATE` и отката миграции: требуется `postgresql+psycopg`, суффикс `_test` и отличие от `DATABASE_URL`. Кеш настроек сбрасывается после установки `TEST_DATABASE_URL`, чтобы Alembic не получил ранее прочитанный рабочий URL.
4. Поиск ID ограничен ASCII-цифрами. Символы вроде `²` больше не приводят к ошибке преобразования в `int`.
5. Добавлена проверка имени из пробелов на уровне Pydantic и отказ от шаблонного JWT-секрета.
6. CORS-адреса очищаются от пробелов в конфигурационной строке.
7. Unit- и интеграционные фикстуры разделены; отсутствие тестовой БД не пропускает unit-тесты.

## Что проверить в среде с PostgreSQL

```bash
cd server
uv sync --extra test
uv run pytest tests/unit -v
TEST_DATABASE_URL=postgresql+psycopg://coachtrack:password@localhost:5432/coachtrack_test uv run pytest tests/integration -v
uv run alembic current
uv run uvicorn app.main:app --reload
```

Создайте выделенную БД `coachtrack_test` до запуска интеграционных тестов и задайте настоящий `JWT_SECRET_KEY` в `.env`. Затем откройте `/docs` и `/openapi.json` и сравните 33 метода и пути с таблицей выше. Команду `alembic upgrade head` для рабочей БД выполняйте только после проверки её URL и резервной копии. До выполнения этих шагов реальное прохождение каждого endpoint и сохранность данных после перезапуска остаются неподтверждёнными.
