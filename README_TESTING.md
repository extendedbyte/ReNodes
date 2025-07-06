# ReNodes Testing System

Система автоматизированного тестирования для ReNodes включает юнит-тесты, интеграционные тесты, тесты производительности и систему сбора метрик.

## 🧪 Структура тестов

### Типы тестов

1. **Юнит-тесты** (`test_node_factory.py`, `test_code_generator.py`)
   - Тестирование отдельных компонентов
   - Быстрое выполнение
   - Высокое покрытие кода

2. **Интеграционные тесты** (`test_application.py`, `test_graph_compilation.py`)
   - Тестирование взаимодействия компонентов
   - Тестирование в headless режиме
   - Компиляция реальных графов

3. **Тесты производительности** (`test_performance.py`)
   - Замер времени запуска (< 60 сек)
   - Замер времени компиляции графов (< 10 сек)
   - Мониторинг использования памяти

## 📊 Метрики производительности

### Пороговые значения

- **Время запуска приложения**: < 60 секунд
- **Время компиляции простого графа**: < 10 секунд
- **Время компиляции сложного графа**: < 10 секунд
- **Загрузка библиотеки**: < 30 секунд
- **Использование памяти**: < 500 МБ

### Собираемые метрики

```json
{
  "application_startup_time": {
    "value": 45.2,
    "threshold": 60.0,
    "unit": "seconds"
  },
  "simple_graph_compilation_time": {
    "value": 3.5,
    "threshold": 10.0,
    "unit": "seconds"
  },
  "library_loading_time": {
    "value": 12.1,
    "threshold": 30.0,
    "unit": "seconds"
  }
}
```

## 🚀 Запуск тестов

### Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements-test.txt

# Все тесты
pytest tests/ -v

# Только юнит-тесты
pytest tests/ -m "unit or not slow" -v

# Только тесты производительности
pytest tests/test_performance.py -m "slow" -v

# Интеграционные тесты
pytest tests/test_graph_compilation.py tests/test_application.py -v

# С покрытием кода
pytest tests/ --cov=ReNode --cov-report=html
```

### Headless режим

```bash
# Установка переменных среды для headless режима
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99

# Запуск в headless режиме
pytest tests/ -v --tb=short
```

## 🤖 GitHub Actions

### Автоматизация

Workflow `.github/workflows/test.yml` автоматически:

1. ✅ Устанавливает окружение Python 3.9
2. ✅ Кэширует зависимости
3. ✅ Запускает все типы тестов
4. ✅ Собирает метрики производительности
5. ✅ Тестирует запуск приложения в headless режиме
6. ✅ Загружает артефакты (отчеты, метрики)
7. ✅ Создает комментарии в PR с результатами

### Триггеры

- **Push** в ветки `main`, `develop`
- **Pull Request** в ветку `main`
- **Ручной запуск** через GitHub UI

### Артефакты

- `test-results-{run_id}` - результаты тестов
- `coverage-reports-{run_id}` - отчеты покрытия
- `external-graph-results-{run_id}` - результаты внешних графов

## 📁 Структура файлов

```
tests/
├── __init__.py                 # Модуль тестов
├── conftest.py                 # Конфигурация pytest и фикстуры
├── test_node_factory.py        # Тесты NodeFactory
├── test_code_generator.py      # Тесты CodeGenerator
├── test_application.py         # Тесты Application
├── test_performance.py         # Тесты производительности
├── test_graph_compilation.py   # Интеграционные тесты графов
└── reports/                    # Отчеты тестов
    ├── junit.xml
    ├── coverage.xml
    └── htmlcov/

pytest.ini                     # Конфигурация pytest
requirements-test.txt           # Зависимости для тестов
performance_results.json        # Результаты метрик
```

## 🛠️ Конфигурация

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    headless: marks tests that run in headless mode
```

### Фикстуры

- `qapp` - QApplication для GUI тестов
- `temp_dir` - временная директория
- `mock_environment` - mock окружение
- `node_factory` - экземпляр NodeFactory
- `performance_metrics` - сборщик метрик

## 📈 Мониторинг производительности

### Automatic Performance Tracking

Система автоматически отслеживает:

1. **Время запуска**: От инициализации до готовности
2. **Время компиляции**: Для различных типов графов
3. **Использование памяти**: Во время операций
4. **Пропускная способность**: Количество графов в секунду

### Performance Dashboard

Результаты доступны в:
- GitHub Actions Summary
- Комментариях PR
- Артефактах workflow
- Файле `performance_results.json`

## 🐛 Отладка тестов

### Локальная отладка

```bash
# Подробный вывод
pytest tests/ -vv -s

# Остановка на первой ошибке
pytest tests/ -x

# Запуск конкретного теста
pytest tests/test_node_factory.py::TestNodeFactory::test_init -v

# Отладка с breakpoint
pytest tests/ --pdb
```

### GitHub Actions отладка

```bash
# Скачивание артефактов
gh run download [run-id]

# Просмотр логов
gh run view [run-id] --log
```

## ⚠️ Известные ограничения

1. **GUI зависимости**: Требуется headless режим для CI/CD
2. **Windows only**: Приложение работает только на Windows
3. **Внешние графы**: Требуется доступ к ReSDK_A3.vr репозиторию
4. **Библиотека узлов**: Необходим файл `lib.obj` для полного тестирования

## 🔧 Настройка окружения

### Для разработки

```bash
# Клонирование репозитория
git clone [repo-url]
cd ReNodes

# Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-test.txt

# Подготовка mock файлов для тестов
python tests/create_mock_files.py
```

### Для CI/CD

Окружение настраивается автоматически через GitHub Actions.

## 📞 Поддержка

При проблемах с тестами:

1. Проверьте логи GitHub Actions
2. Скачайте артефакты для анализа
3. Запустите тесты локально
4. Проверьте конфигурацию pytest.ini
5. Создайте issue с описанием проблемы

---

**Note**: Эта система тестирования обеспечивает высокое качество кода и стабильность приложения ReNodes.