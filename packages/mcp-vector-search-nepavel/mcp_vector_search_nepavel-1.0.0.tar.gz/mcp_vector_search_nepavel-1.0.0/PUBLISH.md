# Публикация на PyPI

## Шаг 1: Регистрация

1. Зайдите на https://pypi.org/account/register/
2. Заполните форму:
   - Username: `NePavel221` (или другой)
   - Email: ваш email
   - Password: придумайте пароль
3. Подтвердите email

## Шаг 2: Создание API токена

1. Зайдите на https://pypi.org/manage/account/token/
2. Нажмите "Add API token"
3. Token name: `mcp-vector-search`
4. Scope: "Entire account" (для первой публикации)
5. Скопируйте токен (начинается с `pypi-`)

## Шаг 3: Публикация

В PowerShell:

```powershell
cd mcp-vector-search-package
python -m twine upload dist/*
```

Когда попросит credentials:
- Username: `__token__`
- Password: вставьте ваш API токен

## Шаг 4: Готово!

После публикации пакет будет доступен:
```bash
uvx mcp-vector-search
```

## Обновление версии

1. Измените версию в `pyproject.toml`
2. Удалите папку `dist/`
3. Соберите заново: `python -m build`
4. Опубликуйте: `python -m twine upload dist/*`
