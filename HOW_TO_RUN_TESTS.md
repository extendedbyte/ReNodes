# 🧪 Как запустить тесты ReNodes

## 🚀 Самый простой способ (Windows)

**Двойной клик на файл:**
```
run_tests.bat
```

Откроется консоль, установит зависимости и запустит все тесты автоматически.

## 🖥️ Локальный запуск (любая ОС)

```bash
# Установить зависимости
pip install -r requirements-test.txt

# Запустить полный набор тестов
python run_tests_local.py
```

**Или отдельные типы тестов:**
```bash
# Только юнит-тесты (быстро)
pytest tests/ -m "unit or not slow" -v

# Только тесты производительности
pytest tests/test_performance.py -m "slow" -v

# Только интеграционные тесты
pytest tests/test_graph_compilation.py tests/test_application.py -v

# Тестирование запуска приложения
python main.py -noapp -nosplash -debug
```

## 🌐 GitHub Actions (без PR)

### Способ 1: Ручной запуск основного workflow

1. Идите в **GitHub → Actions**
2. Выберите **"ReNodes Testing and Metrics"**
3. Нажмите **"Run workflow"**
4. Выберите ветку и запустите

### Способ 2: Упрощенный ручной запуск

1. Идите в **GitHub → Actions**
2. Выберите **"Manual Test Run"**
3. Нажмите **"Run workflow"**
4. Выберите тип тестов:
   - `all` - все тесты
   - `unit` - только юнит-тесты
   - `performance` - только производительность
   - `integration` - только интеграционные
   - `startup-only` - только тест запуска

## 🔧 Push в ветку develop

Если создать ветку `develop` и сделать push, тесты запустятся автоматически:

```bash
git checkout -b develop
git push origin develop
```

## ⚡ Быстрый тест одного компонента

```bash
# Тест только NodeFactory
pytest tests/test_node_factory.py -v

# Тест только CodeGenerator
pytest tests/test_code_generator.py -v

# Тест только Application
pytest tests/test_application.py -v
```

## 📊 Результаты тестов

### Локально:
- Консольный вывод
- `tests/reports/local_test_results.json`
- `tests/reports/junit.xml` (если запущен pytest)

### GitHub Actions:
- **Artifacts** - скачиваемые отчеты
- **Summary** - краткие результаты на странице workflow
- **Logs** - подробные логи выполнения

## 🐛 Решение проблем

### "pytest не найден"
```bash
pip install pytest pytest-qt pytest-cov
```

### "PyQt5 не найден"
```bash
pip install PyQt5
```

### "Permission denied" в GitHub
- Проверьте права доступа к repository Actions
- Убедитесь что workflow files закоммичены в main/develop

### Тесты зависают
- Используйте `Ctrl+C` для остановки
- Проверьте что нет открытых GUI окон
- Установите переменную окружения: `export QT_QPA_PLATFORM=offscreen`

## 💡 Советы

- **Для разработки**: используйте локальный запуск
- **Для CI/CD**: используйте GitHub Actions
- **Для быстрой проверки**: запускайте только юнит-тесты
- **Для полной проверки**: запускайте все тесты перед коммитом

---

**Быстрая команда для проверки всего:**
```bash
python run_tests_local.py
```