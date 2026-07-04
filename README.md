# Установка и запуск проекта

## Требования

- Windows
- Git
- Visual Studio Code

---

# 1. Установка Chocolatey (если еще не установлен)

Откройте **PowerShell от имени администратора** и выполните команду:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; `
[System.Net.ServicePointManager]::SecurityProtocol = `
[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Проверьте, что Chocolatey установлен:

```powershell
choco --version
```

---

# 2. Установка Python (если еще не установлен)

Установите последнюю версию Python через Chocolatey:

```powershell
choco install python -y
```

Проверьте установку:

```powershell
python --version
```

---

# 3. Установка uv (если еще не установлен)

Установите менеджер зависимостей **uv**:

```powershell
Set-ExecutionPolicy ByPass; irm https://astral.sh/uv/install.ps1 | iex
```

Проверьте установку:

```powershell
uv --version
```

---

# 4. Установка PostgreSQL (для локального запуска)

> Данный шаг необходим только при запуске проекта с локальной базой данных.

Установите PostgreSQL через Chocolatey (займет 10-15 минут):

```powershell
choco install postgresql -y
```

После установки убедитесь, что PostgreSQL запущен.

Подключитесь к серверу PostgreSQL с помощью `psql`:

```powershell
psql -U postgres
```

Создайте базу данных проекта:

```sql
CREATE DATABASE litscroll;
```

Для подключения используйте одну из следующих строк:

Если используется пользователь `postgres`:

```text
DATABASE_URL=postgres:<пароль>@localhost:5432/litscroll
```
---


# 5. Клонирование проекта

Для клонирования репозитория рекомендуется использовать **GitHub Desktop**.

1. Установите **GitHub Desktop**, если он еще не установлен.
2. Авторизуйтесь в своей учетной записи GitHub.
3. Выберите **File → Clone Repository...**.
4. Перейдите на вкладку **URL**.
5. Вставьте URL репозитория:

```text
https://github.com/PP-BusinessProject/litscroll_backend
```

6. Выберите локальную папку, в которую будет склонирован проект.
7. Нажмите **Clone**.

После завершения клонирования откройте папку проекта в **Visual Studio Code**:

- В GitHub Desktop выберите **Repository → Open in Visual Studio Code**.

Либо откройте папку проекта вручную через **File → Open Folder...** в Visual Studio Code.

---

# 6. Инициализация проекта

Установите все зависимости проекта:

```bash
uv sync --all-groups
```

Команда автоматически создаст виртуальное окружение (при необходимости) и установит все зависимости.

---

# 7. Настройка файла конфигурации

Перед первым запуском необходимо создать файл окружения.

Для разработки `.env.dev`.
Для продакшена `.env.prod`.
Для тестов `.env.test`.

После создания файла при необходимости укажите значения переменных окружения в соответствии с вашей конфигурацией.

### DATABASE_URL

Переменная `DATABASE_URL` определяет строку подключения к базе данных PostgreSQL.

Формат:

```text
<пользователь>:<пароль>@<хост>:<порт>/<база_данных>
```

Пример:

```text
DATABASE_URL=postgres:postgres@localhost:5432/litscroll
```

Если база данных запущена локально через Docker, обычно достаточно изменить только имя базы данных, пользователя и пароль в соответствии с вашей конфигурацией.

---

# 8. Запуск проекта

Откройте проект в **Visual Studio Code**.

Для запуска используйте заранее настроенные конфигурации **Debug**:

1. Откройте вкладку **Run and Debug** (`Ctrl + Shift + D`).
2. Выберите одну из конфигураций из файла `launch.json`.
3. Нажмите **F5** или кнопку **Start Debugging**.

### Доступные конфигурации

#### Создание таблиц в локальной базе данных

Используйте конфигурацию:

```
db (dev)
```

Она создаст все необходимые таблицы в локальной базе данных, указанной в `DATABASE_URL`.

---

#### Запуск API с локальной базой данных

Используйте конфигурацию:

```
api (dev)
```

---

#### Создание таблиц в Supabase

Используйте конфигурацию:

```
db (prod)
```

Она создаст необходимые таблицы в базе данных Supabase, используя настройки из файла `.env`.

---

#### Запуск API с Supabase

Используйте конфигурацию:

```
api (prod)
```

После запуска API будет использовать базу данных Supabase, указанную в `DATABASE_URL`.

---

# 9. Полезные команды

Проверить версию Python:

```bash
uv run python --version
```

Проверить версию uv:

```bash
uv --version
```

Повторно установить или обновить зависимости:

```bash
uv sync --all-groups
```