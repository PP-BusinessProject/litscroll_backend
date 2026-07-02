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
pip install -U uv
```

Проверьте установку:

```powershell
uv --version
```

---

# 4. Клонирование проекта

```bash
git clone https://github.com/PP-BusinessProject/litscroll_backend
cd litscroll_backend
```

---

# 5. Инициализация проекта

Установите все зависимости проекта:

```bash
uv sync --all-groups
```

Команда автоматически создаст виртуальное окружение (при необходимости) и установит все зависимости.

---

# 6. Запуск проекта

Откройте проект в **Visual Studio Code**.

Для запуска используйте заранее настроенную конфигурацию **Debug**:

1. Откройте вкладку **Run and Debug** (`Ctrl + Shift + D`).
2. Выберите конфигурацию из файла `launch.json`.
3. Нажмите **F5** или кнопку **Start Debugging**.

Проект будет запущен с использованием настроек из `launch.json`.

---

# Обновление зависимостей

После получения новых изменений из репозитория выполните:

```bash
uv sync --all-groups
```

---

# Полезные команды

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