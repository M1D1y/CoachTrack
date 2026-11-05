# CoachTrack Backend

Локальный FastAPI backend на Python 3.12+, PostgreSQL, SQLAlchemy 2, Pydantic 2 и Alembic. React-клиент использует реальные API-запросы через Vite proxy.

## Архитектура

```text
app/
  main.py                FastAPI и CORS
  api/                   маршруты auth, users, athletes, invitations, team,
                         trainings, injuries, nutrition, reports
  models/                таблицы SQLAlchemy
  schemas/               формы JSON-запросов и ответов Pydantic
  services/              бизнес-правила и запросы к БД
  db/                    Base, Engine, SessionLocal, get_db
  core/                  настройки, Argon2, JWT, проверки доступа и ФИО
alembic/                 миграции PostgreSQL
tests/unit/              проверки функций без БД
tests/integration/       TestClient и отдельная PostgreSQL
```

FastAPI `Depends` передаёт обработчикам сессию БД и текущего пользователя. JWT проверяется на сервере; роль и связь тренер–спортсмен читаются из PostgreSQL. Основные таблицы: `users`, `invitations`, `trainings`, `injuries`, `nutrition`, `refresh_tokens`. Внешние ключи хранят внутренний `users.id`.

## Регистрация, UUID и токены

```json
{"last_name":"Соколова","first_name":"Мария","patronymic":"Андреевна","password":"StrongPassword123!","role":"athlete"}
```

Отправьте этот JSON в `POST /api/v1/auth/register`. Ответ содержит `public_id`, полное `name`, роль, возраст, вид спорта и дату создания. ФИО сохраняется в `users.name` в порядке «Фамилия Имя Отчество» и уникально без учёта регистра и лишних пробелов. Повторное ФИО даёт 409. После регистрации клиент делает обычный вход.

```json
{"name":"  соколова   МАРИЯ андреевна ","password":"StrongPassword123!"}
```

Отправьте этот JSON в `POST /api/v1/auth/login`. Ответ содержит только `access_token` и `token_type`; сервер устанавливает HttpOnly cookie `coachtrack_refresh` на пути `/api/v1/auth`. Access JWT содержит `public_id` в `sub`, срок действия обычно 30 минут. Сервер сопоставляет UUID со строкой `users` и только затем проверяет права. Старые JWT с числовым `sub` отклоняются, поэтому после обновления приложения требуется повторный вход.

Refresh token действует 7 дней и хранится в PostgreSQL только как SHA-256 хеш. `POST /auth/refresh` читает cookie, отзывает старый token, выдаёт новый access JWT и ротирует cookie. `POST /auth/logout` требует access JWT и отзывает cookie текущей сессии; frontend очищает локальное состояние даже при недоступном сервере. Выданный ранее access JWT остаётся действительным до истечения срока. Cookie имеет `HttpOnly` и `SameSite=Strict`; для локального HTTP `REFRESH_COOKIE_SECURE=false`. При HTTPS установите `true`. Для запросов login/refresh/logout требуется заголовок `Origin`, совпадающий с `CORS_ORIGINS` или адресом самого backend; это защищает cookie-маршруты от межсайтовых запросов. Используйте `localhost` и для Vite, и для FastAPI.

В Swagger для входа укажите ФИО и пароль; браузер сохранит cookie. Для `/users/me` и остальных защищённых маршрутов нажмите **Authorize** и вставьте access JWT. `/auth/refresh` работает с cookie браузера и не принимает token в JSON.

`users.id` сохраняется как числовой ключ БД. `users.public_id` — случайный UUID, который применяется в пользовательских JSON и путях для спортсменов. UUID не является секретом: все маршруты дополнительно проверяют роль и права. Числовые `id` тренировок, приглашений, травм и питания остались идентификаторами этих ресурсов, но запросы к ним также проверяют владение.

## Миграции и старые аккаунты

- `0001_initial.py` создаёт таблицы.
- `0002_unique_user_fio.py` под блокировкой проверяет дубли нормализованных ФИО и создаёт уникальный индекс. Если дубли есть, миграция останавливается без изменения пользователей. Не удаляйте и не переименовывайте их автоматически; согласуйте ФИО с владельцами.
- `0003_user_public_id.py` добавляет `public_id UUID DEFAULT gen_random_uuid() NOT NULL`, заполняет старые строки случайными UUID и создаёт уникальное ограничение. Внешние ключи остаются числовыми.
- `0004_hide_completed_invitation_history.py` добавляет признак скрытия истории тренера. Существующие приглашения и их статусы сохраняются.

Старые пользователи с именем из двух слов сохраняют возможность входа по сохранённому имени и паролю. При изменении профиля новое имя должно иметь три части. Для диагностики конфликтов перед обновлением:

```sql
WITH normalized AS (
  SELECT id, translate(lower(btrim(regexp_replace(name, '[[:space:]]+', ' ', 'g'))),
    'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
    'абвгдеёжзийклмнопрстуфхцчшщъыьэюя') AS name_key FROM users
)
SELECT name_key, array_agg(id ORDER BY id) FROM normalized
GROUP BY name_key HAVING count(*) > 1;
```

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
    if line.startswith('JWT_SECRET_KEY=') and line.partition('=')[2].startswith('replace_with'):
        lines[index] = 'JWT_SECRET_KEY=' + secrets.token_urlsafe(48)
path.write_text('\n'.join(lines) + '\n')
path.chmod(0o600)
PY
docker compose up --build -d
docker compose ps
```

Compose запускает PostgreSQL и backend, а backend применяет `alembic upgrade head`. База сохраняется в volume `coachtrack_data`; PostgreSQL опубликована только на `127.0.0.1:15432`, поэтому извне компьютера порт недоступен. Проверка: <http://localhost:8000/docs> и `docker compose logs -f backend`. Остановка: `docker compose down` без `-v`. Данные можно смотреть через `docker compose exec postgres psql -U coachtrack -d coachtrack`.

В соседнем терминале:

```bash
cd client
npm ci
npm run dev
```

Откройте <http://localhost:5173>. Vite proxy отправляет `/api` на `http://localhost:8000`. Если открыли frontend через `127.0.0.1`, перейдите на `localhost` и повторите вход.

## Запуск без Docker

Установите PostgreSQL, Python 3.12+ и `uv`, запустите PostgreSQL и создайте отдельную рабочую БД:

```bash
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE USER coachtrack WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE coachtrack OWNER coachtrack;"
cd server
cp .env.example .env
# Замените JWT_SECRET_KEY на случайный секрет; настройте DATABASE_URL.
uv sync --extra test
uv run alembic current
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## API

Все пути имеют префикс `/api/v1`. Ошибки: 401 при отсутствии действительной авторизации, 403 для запрещённой роли, 404 для недоступного объекта, 409 при конфликте, 422 при неверном вводе. Для `POST /auth/login`, `/auth/refresh`, `/auth/logout` браузер отправляет `Origin` автоматически; при ручном HTTP-запросе добавьте `Origin: http://localhost:8000`.

| Метод | Путь | Действие |
| --- | --- | --- |
| POST | `/auth/register` | Регистрация по ФИО |
| POST | `/auth/login` | Вход, access JWT и refresh cookie |
| POST | `/auth/refresh` | Ротация refresh cookie и новый access JWT |
| POST | `/auth/logout` | Отзыв refresh cookie; нужен access JWT |
| GET, PATCH | `/users/me` | Текущий профиль |
| GET | `/athletes` | Команда тренера; необязательный поиск `q` по ФИО |
| GET | `/athletes/search` | Глобальный поиск тренера: минимум 3 символа, максимум 20 результатов |
| POST | `/invitations` | Приглашение с `athlete_public_id` |
| GET | `/invitations/incoming` | Приглашения спортсмена |
| GET | `/invitations/sent` | Отправленные тренером приглашения |
| DELETE | `/invitations/sent/history` | Скрыть завершённые приглашения текущего тренера; ожидающие сохраняются |
| POST | `/invitations/{id}/accept` | Принять приглашение |
| POST | `/invitations/{id}/reject` | Отклонить приглашение |
| POST | `/invitations/{id}/cancel` | Отменить своё приглашение |
| GET | `/team/my-trainer` | Текущий тренер спортсмена или `null` |
| DELETE | `/team/my-trainer` | Самостоятельное открепление |
| DELETE | `/team/athletes/{athlete_id}` | Удалить спортсмена своей команды; параметр UUID |
| GET, POST | `/trainings` | Недельный список и назначение; POST с `athlete_public_id` |
| GET, PATCH, DELETE | `/trainings/{id}` | Просмотр, изменение, удаление тренировки |
| PATCH | `/trainings/{id}/attendance` | Посещаемость: planned/attended/missed |
| GET, POST | `/athletes/{athlete_id}/injuries` | Травмы по UUID спортсмена |
| PATCH, DELETE | `/injuries/{id}` | Изменение, удаление травмы |
| GET, POST | `/athletes/{athlete_id}/nutrition` | Питание по UUID спортсмена |
| PATCH, DELETE | `/nutrition/{id}` | Изменение, удаление записи |
| GET | `/reports/summary` | Недельный отчёт своей команды или спортсмена |
| GET | `/athletes/{athlete_id}/reports/summary` | Отчёт по UUID доступного спортсмена |

Неделя начинается в понедельник; `week_start=YYYY-MM-DD` должен быть понедельником. Посещаемость: `attended / (attended + missed) * 100`, без `planned`; при нуле завершённых тренировок процент равен нулю. Открепление сохраняет аккаунт и историю, но прежний тренер сразу теряет доступ.

## Тестирование

Unit-тесты работают без PostgreSQL. Интеграционные тесты требуют отдельную БД, имя которой оканчивается на `_test`; тестовые фикстуры могут очищать только эту БД. С Docker создайте её в контейнере, затем подключайтесь через локальный порт 15432:

```bash
cd server
uv sync --extra test
uv run pytest tests/unit -v
docker compose exec postgres psql -U coachtrack -d coachtrack -c "CREATE DATABASE coachtrack_test OWNER coachtrack;"
TEST_DATABASE_URL=postgresql+psycopg://coachtrack:password@localhost:15432/coachtrack_test uv run pytest tests/integration -v
```

При ошибке подключения сначала проверьте `docker compose ps` или `systemctl status postgresql`. При 409 на регистрации выберите другое ФИО; при остановке миграции `0002` разберите перечисленные конфликты старых имён. При 401 после обновления версии войдите заново: старые JWT с числовым `sub` не принимаются.
