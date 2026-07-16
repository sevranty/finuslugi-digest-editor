# finuslugi-digest-editor

`finuslugi-digest-editor` - личный навык для доказательной проверки продуктовых дайджестов Финуслуг

Он работает в трёх режимах:

- вычитка по встроенной или пользовательской редполитике
- формирование или аудит тегов
- сравнение двух версий по фактам и смыслу

Навык сохраняет точные числа, знаки, единицы, периоды и статусы. Непроверяемые фрагменты отмечаются, а пробелы не заполняются догадками.

## Режимы

| Режим | Запрос | Результат |
|---|---|---|
| Вычитка | вычитать, проверить по редполитике, валидировать | таблица замечаний и приоритеты |
| Теги | подобрать, сформировать или проверить теги | таблица тегов или аудита |
| Сравнение | сравнить, сопоставить, найти расхождения | вердикт и таблица расхождений |

При явном запросе нескольких режимов порядок фиксирован:

```text
сравнение -> вычитка -> теги
```

Несколько приложенных файлов сами по себе не включают сравнение.

## Входы

- текст
- DOCX
- PDF, включая сканы
- TXT и Markdown
- презентации
- скриншоты и изображения
- таблицы

## Ограничения

- без независимого источника проверяется внутренняя согласованность, а не истинность во внешнем мире
- исходные файлы не изменяются без отдельной просьбы
- допустимая стилистическая переформулировка не считается расхождением
- нечитаемые фрагменты не восстанавливаются по смыслу
- общий заголовок не считается самостоятельной карточкой

## Personal skill package

В пакет входят ровно семь runtime-файлов:

```text
finuslugi-digest-editor/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
`-- references/
    |-- comparison-protocol.md
    |-- file-handling.md
    |-- redpolicy.md
    |-- tagging-protocol.md
    `-- validation-protocol.md
```

Собрать воспроизводимый архив:

```bash
python3 scripts/build_package.py --output dist/finuslugi-digest-editor.zip
python3 scripts/validate_package.py dist/finuslugi-digest-editor.zip
```

`README.md`, `LICENSE`, `docs/`, `evals/`, `assets/`, `design/`, `release/`, `scripts/` и `tests/` в personal skill package не входят.

## Проверка доступности

```text
Используй @finuslugi-digest-editor. Проверь этот текст по встроенной редполитике: «Запустили улучшения и получили отличный результат».
```

Ожидаемый признак - режим вычитки, отсутствие выдуманной метрики и конкретная правка слабого результата.

## Примеры

### Вычитка

```text
Используй @finuslugi-digest-editor. Вычитай приложенный PDF по встроенной редполитике. Проверь карточки, метрики, структуру, теги и Tone of Voice.
```

### Теги

```text
Используй @finuslugi-digest-editor. Сформируй по три доказуемых тега для каждой самостоятельной карточки приложенного DOCX.
```

### Аудит тегов

```text
Используй @finuslugi-digest-editor. Проверь существующие теги: количество, доказуемость, конкретность и соответствие карточкам.
```

### Сравнение

```text
Используй @finuslugi-digest-editor. Сравни файл 1 как источник и файл 2 как проверяемую версию. Покажи только расхождения и точные значения.
```

## Локальная валидация

```bash
git diff --check
python3 scripts/validate_fixtures.py
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

Подробности - [docs/VALIDATION.md](docs/VALIDATION.md)

## WebFactoryOS

Проект работает под оркестрацией WebFactoryOS без runtime, CI или сетевой зависимости

- локальные правила агента - [AGENTS.md](AGENTS.md)
- граница владения - [docs/WEBFACTORYOS.md](docs/WEBFACTORYOS.md)
- обслуживание - [docs/MAINTENANCE.md](docs/MAINTENANCE.md)
- проектный долг - [docs/PROJECT_DEBT.md](docs/PROJECT_DEBT.md)

## Структура репозитория

```text
finuslugi-digest-editor/
|-- SKILL.md
|-- README.md
|-- LICENSE
|-- CHANGELOG.md
|-- AGENTS.md
|-- agents/
|   `-- openai.yaml
|-- assets/
|   |-- source/
|   |   `-- social-preview.svg
|   |-- project-image.png
|   |-- provenance.json
|   `-- social-preview.png
|-- design/
|   |-- concepts/
|   `-- social-preview-brief.md
|-- docs/
|   |-- MAINTENANCE.md
|   |-- MANUAL_RUNTIME_REVIEW.md
|   |-- PROJECT_DEBT.md
|   |-- VALIDATION.md
|   `-- WEBFACTORYOS.md
|-- evals/
|   |-- fixtures/
|   |-- expected-results.json
|   |-- manifest.json
|   `-- README.md
|-- references/
|   |-- comparison-protocol.md
|   |-- file-handling.md
|   |-- redpolicy.md
|   |-- tagging-protocol.md
|   `-- validation-protocol.md
|-- release/
|   `-- package.json
|-- scripts/
|   |-- build_package.py
|   |-- validate_fixtures.py
|   |-- validate_package.py
|   `-- validate_repository.py
`-- tests/
    |-- test_package.py
    `-- test_validation.py
```

## Лицензия

MIT - см. `LICENSE`
