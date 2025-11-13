# Flow Exporter

Утилита для экспорта и импорта графовых JSON-проектов в файловую структуру.  
Позволяет разделять проект на отдельные узлы, код в `.py` файлы и связи между ними, а затем восстанавливать проект обратно в единый  JSON.

## Установка

```bash
pip install flow-exporter
```

# Использование CLI

## Экспорт проекта

Разделяет JSON-проект на:
- nodes/ — JSON каждого узла
- edges/ — JSON связей
- src/ — исходный код узлов

### Пример:

`flow-export export tests/input.json output/`

- export — команда экспорта
- tests/input.json — путь к исходному JSON-файлу проекта
- output/ — папка для результата

## Импорт проекта

Собирает обратно проект в единый JSON.

### Пример:

`flow-export import output/flow.json restored/`

- import — команда импорта
- output/flow.json — экспортированный flow.json
- restored/ — папка для восстановленного JSON

## Тестирование
Тесты используют встроенную фикстуру tmp_path pytest и файл tests/input.json.

### Запуск всех тестов:
`pytest -v`
