# Flow Exporter

Утилита для экспорта и импорта графовых JSON-проектов в файловую структуру.  
Позволяет разделять проект на отдельные узлы, код в `.py` файлы и связи между ними, а затем восстанавливать проект обратно в единый  JSON.

## Установка

1. Клонируем проект:

```bash
pip install -r requirements.txt
```

# Использование CLI

## Экспорт проекта

Разделяет JSON-проект на:
- nodes/ — JSON каждого узла
- edges/ — JSON связей
- src/ — исходный код узлов

### Пример:

`python3 -m flow_exporter export tests/input.json output/`

- export — команда экспорта
- tests/input.json — путь к исходному JSON-файлу проекта
- output/ — папка для результата

## Импорт проекта

Собирает обратно проект в единый JSON.

### Пример:

`python3 -m flow_exporter.main import output/flow.json restored/`

- import — команда импорта
- output/flow.json — экспортированный flow.json
- restored/ — папка для восстановленного JSON

## Тестирование
Тесты используют встроенную фикстуру tmp_path pytest и файл tests/input.json.

### Запуск всех тестов:
`pytest -v`
