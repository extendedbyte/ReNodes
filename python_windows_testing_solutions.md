# Система тестирования на Python для Windows: Практическое руководство

## Обзор

Исследование решений для создания системы тестирования на **Python** в **Windows** окружении, включающей:
- UI-автоматизацию Windows приложений
- Командный интерфейс через параметры
- Визуальный интерфейс для управления тестами
- Архитектуру на основе графов и метрик

## 1. Python решения для UI-тестирования Windows

### 1.1 Рекомендуемые инструменты

#### PyAutoGUI - Универсальное решение
```python
import pyautogui
import time

# Основные возможности
def test_notepad():
    # Открыть приложение
    pyautogui.hotkey('win', 'r')
    pyautogui.write('notepad')
    pyautogui.press('enter')
    time.sleep(1)
    
    # Взаимодействие с приложением
    pyautogui.write('Hello from automation!')
    pyautogui.hotkey('ctrl', 's')
    
    # Поиск элементов по изображению
    save_button = pyautogui.locateOnScreen('save_button.png')
    if save_button:
        pyautogui.click(save_button)
```

**Преимущества:**
- Простая установка: `pip install pyautogui`
- Кроссплатформенность
- Встроенные safety features
- Хорошая документация

**Недостатки:**
- Зависимость от разрешения экрана
- Ненадежность image-based поиска

#### pywinauto - Специализация на Windows
```python
from pywinauto.application import Application

def test_calculator():
    # Подключение к приложению
    app = Application(backend="uia").start("calc.exe")
    calculator = app.Calculator
    
    # Взаимодействие через UI Automation
    calculator.Button2.click()
    calculator.ButtonPlus.click()
    calculator.Button3.click()
    calculator.ButtonEquals.click()
    
    # Получение результата
    result = calculator.CalculatorResults.window_text()
    assert "5" in result
```

**Преимущества:**
- Нативная поддержка Windows UI Automation
- Надежная идентификация элементов
- Поддержка UIA и Win32 API

**Недостатки:**
- Только Windows
- Сложность с некоторыми приложениями

#### Appium + WinAppDriver (с осторожностью)
```python
from appium import webdriver

def setup_winapp_driver():
    desired_caps = {
        "app": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App",
        "platformName": "Windows",
        "deviceName": "WindowsPC"
    }
    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4723',
        desired_capabilities=desired_caps
    )
    return driver

# ⚠️ Осторожно: WinAppDriver не поддерживается Microsoft
```

### 1.2 Гибридный подход (рекомендуется)

```python
class WindowsTestAutomation:
    def __init__(self):
        self.pyautogui_enabled = True
        self.pywinauto_enabled = True
        
    def find_element(self, element_id=None, image_path=None):
        """Поиск элемента с fallback стратегией"""
        
        # Попробовать pywinauto
        if element_id and self.pywinauto_enabled:
            try:
                from pywinauto import Application
                app = Application(backend="uia").connect(title_re=".*")
                return app.window(auto_id=element_id)
            except:
                pass
        
        # Fallback на pyautogui
        if image_path and self.pyautogui_enabled:
            try:
                import pyautogui
                return pyautogui.locateOnScreen(image_path, confidence=0.8)
            except:
                pass
                
        raise ElementNotFoundError("Element not found")
```

## 2. Архитектура Python тестового фреймворка

### 2.1 Структура проекта

```
test_framework/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── automation_engine.py    # Основной движок
│   │   ├── element_finder.py       # Поиск элементов
│   │   └── screenshot_manager.py   # Управление скриншотами
│   ├── ui/
│   │   ├── web_interface.py        # Flask/FastAPI веб-интерфейс
│   │   └── cli_interface.py        # Командный интерфейс
│   ├── tests/
│   │   ├── conftest.py            # Pytest конфигурация
│   │   ├── test_calculator.py     # Примеры тестов
│   │   └── test_notepad.py
│   └── utils/
│       ├── graph_builder.py       # Построение графов
│       ├── metrics_collector.py   # Сбор метрик
│       └── config_manager.py      # Управление конфигурацией
├── requirements.txt
├── pytest.ini
└── README.md
```

### 2.2 Основные компоненты

#### automation_engine.py
```python
import pyautogui
import pywinauto
from typing import Dict, Any, Optional
import logging

class AutomationEngine:
    """Центральный движок автоматизации"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Настройка pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = config.get('pause_between_actions', 0.5)
        
    def click_element(self, locator: str, method: str = 'auto'):
        """Универсальный клик по элементу"""
        if method == 'auto':
            # Попробовать pywinauto, затем pyautogui
            try:
                return self._click_by_automation_id(locator)
            except:
                return self._click_by_image(locator)
        elif method == 'automation_id':
            return self._click_by_automation_id(locator)
        elif method == 'image':
            return self._click_by_image(locator)
    
    def _click_by_automation_id(self, automation_id: str):
        """Клик через UI Automation"""
        from pywinauto import Application
        app = Application(backend="uia").connect(title_re=".*")
        element = app.window(auto_id=automation_id)
        element.click()
        return True
    
    def _click_by_image(self, image_path: str):
        """Клик по изображению"""
        location = pyautogui.locateOnScreen(
            image_path, 
            confidence=self.config.get('image_confidence', 0.8)
        )
        if location:
            pyautogui.click(location)
            return True
        return False
```

#### web_interface.py (Flask)
```python
from flask import Flask, render_template, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Главная страница с дашбордом"""
    return render_template('dashboard.html')

@app.route('/api/run_tests', methods=['POST'])
def run_tests():
    """API для запуска тестов"""
    data = request.json
    test_suite = data.get('test_suite', '')
    markers = data.get('markers', [])
    
    # Построение команды pytest
    cmd = ['python', '-m', 'pytest']
    if test_suite:
        cmd.append(test_suite)
    if markers:
        cmd.extend(['-m', ' and '.join(markers)])
    
    # Запуск тестов
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        cwd='src/tests'
    )
    
    return jsonify({
        'success': result.returncode == 0,
        'output': result.stdout,
        'errors': result.stderr
    })

@app.route('/api/metrics')
def get_metrics():
    """API для получения метрик"""
    from utils.metrics_collector import MetricsCollector
    collector = MetricsCollector()
    return jsonify(collector.get_current_metrics())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## 3. Командные параметры и CLI интерфейс

### 3.1 Расширенная pytest конфигурация

#### pytest.ini
```ini
[tool:pytest]
markers =
    ui: UI automation tests
    smoke: Smoke tests
    regression: Regression tests
    slow: Slow running tests
    calculator: Calculator app tests
    notepad: Notepad app tests

addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    -p no:cacheprovider

testpaths = src/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

#### conftest.py - расширенная конфигурация
```python
import pytest
import pyautogui
import time
from pathlib import Path

def pytest_addoption(parser):
    """Добавление пользовательских параметров"""
    parser.addoption(
        "--app", 
        action="store", 
        default=None,
        help="Приложение для тестирования"
    )
    parser.addoption(
        "--screenshot-on-failure", 
        action="store_true",
        help="Делать скриншот при падении теста"
    )
    parser.addoption(
        "--delay", 
        action="store", 
        type=float,
        default=0.5,
        help="Задержка между действиями"
    )
    parser.addoption(
        "--confidence", 
        action="store", 
        type=float,
        default=0.8,
        help="Точность распознавания изображений"
    )

@pytest.fixture(scope="session")
def test_config(request):
    """Конфигурация для тестовой сессии"""
    return {
        'app': request.config.getoption("--app"),
        'screenshot_on_failure': request.config.getoption("--screenshot-on-failure"),
        'delay': request.config.getoption("--delay"),
        'confidence': request.config.getoption("--confidence")
    }

@pytest.fixture(autouse=True)
def setup_pyautogui(test_config):
    """Настройка pyautogui для каждого теста"""
    pyautogui.PAUSE = test_config['delay']
    pyautogui.FAILSAFE = True
    yield
    # Cleanup после теста

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для обработки результатов тестов"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        # Скриншот при падении теста
        if item.config.getoption("--screenshot-on-failure"):
            screenshot_path = f"screenshots/failed_{item.name}_{int(time.time())}.png"
            Path("screenshots").mkdir(exist_ok=True)
            pyautogui.screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
```

### 3.2 Примеры использования CLI

```bash
# Базовое выполнение
python -m pytest

# Выполнение с параметрами
python -m pytest --app=calculator --delay=1.0 --screenshot-on-failure

# Выполнение по маркерам
python -m pytest -m "ui and smoke"
python -m pytest -m "not slow"

# Выполнение конкретных тестов
python -m pytest src/tests/test_calculator.py::test_addition
python -m pytest -k "calculator and not division"

# Параллельное выполнение (требует pytest-xdist)
python -m pytest -n 2

# Генерация отчетов
python -m pytest --html=reports/report.html --self-contained-html
```

### 3.3 Пользовательский CLI интерфейс

#### cli_interface.py
```python
import click
import subprocess
import json
from pathlib import Path

@click.group()
def cli():
    """Test Framework CLI"""
    pass

@cli.command()
@click.option('--suite', help='Test suite to run')
@click.option('--app', help='Application to test')
@click.option('--markers', help='Pytest markers')
@click.option('--parallel', type=int, help='Number of parallel workers')
def run(suite, app, markers, parallel):
    """Запуск тестов"""
    cmd = ['python', '-m', 'pytest']
    
    if suite:
        cmd.append(f'src/tests/{suite}')
    if app:
        cmd.extend(['--app', app])
    if markers:
        cmd.extend(['-m', markers])
    if parallel:
        cmd.extend(['-n', str(parallel)])
    
    click.echo(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

@cli.command()
def dashboard():
    """Запуск веб-интерфейса"""
    click.echo("Starting web dashboard on http://localhost:5000")
    subprocess.run(['python', 'src/ui/web_interface.py'])

@cli.command()
@click.option('--format', type=click.Choice(['json', 'table']), default='table')
def metrics(format):
    """Показать метрики тестирования"""
    from src.utils.metrics_collector import MetricsCollector
    collector = MetricsCollector()
    data = collector.get_current_metrics()
    
    if format == 'json':
        click.echo(json.dumps(data, indent=2))
    else:
        # Табличный вывод
        click.echo("Test Metrics:")
        for key, value in data.items():
            click.echo(f"  {key}: {value}")

if __name__ == '__main__':
    cli()
```

## 4. Графы и метрики на Python

### 4.1 Построение графов зависимостей

#### graph_builder.py
```python
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List
import json

class TestDependencyGraph:
    """Построение графов зависимостей тестов"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def add_test(self, test_name: str, dependencies: List[str] = None):
        """Добавить тест в граф"""
        self.graph.add_node(test_name)
        
        if dependencies:
            for dep in dependencies:
                self.graph.add_edge(dep, test_name)
    
    def build_from_config(self, config_path: str):
        """Построить граф из конфигурации"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        for test_name, test_info in config['tests'].items():
            dependencies = test_info.get('dependencies', [])
            self.add_test(test_name, dependencies)
    
    def get_execution_order(self) -> List[str]:
        """Получить порядок выполнения тестов"""
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXError:
            raise ValueError("Circular dependency detected")
    
    def visualize(self, output_path: str = 'test_dependencies.png'):
        """Визуализация графа"""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # Раскраска узлов по типам
        node_colors = []
        for node in self.graph.nodes():
            if 'setup' in node.lower():
                node_colors.append('lightgreen')
            elif 'teardown' in node.lower():
                node_colors.append('lightcoral')
            else:
                node_colors.append('lightblue')
        
        nx.draw(
            self.graph, pos,
            with_labels=True,
            node_color=node_colors,
            node_size=3000,
            font_size=8,
            arrows=True,
            edge_color='gray'
        )
        
        plt.title("Test Dependencies Graph")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

# Пример использования
if __name__ == '__main__':
    graph = TestDependencyGraph()
    graph.add_test('setup_environment')
    graph.add_test('test_login', ['setup_environment'])
    graph.add_test('test_calculator', ['test_login'])
    graph.add_test('cleanup', ['test_calculator'])
    
    print("Execution order:", graph.get_execution_order())
    graph.visualize()
```

### 4.2 Сбор и анализ метрик

#### metrics_collector.py
```python
import time
import json
import sqlite3
from dataclasses import dataclass
from typing import Dict, List
import matplotlib.pyplot as plt
import pandas as pd

@dataclass
class TestResult:
    name: str
    status: str  # 'passed', 'failed', 'skipped'
    duration: float
    timestamp: float
    error_message: str = None

class MetricsCollector:
    """Сбор и анализ метрик тестирования"""
    
    def __init__(self, db_path: str = 'test_metrics.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                duration REAL NOT NULL,
                timestamp REAL NOT NULL,
                error_message TEXT
            )
        ''')
        conn.close()
    
    def record_test(self, result: TestResult):
        """Записать результат теста"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO test_results 
            (name, status, duration, timestamp, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (result.name, result.status, result.duration, 
              result.timestamp, result.error_message))
        conn.commit()
        conn.close()
    
    def get_metrics_summary(self, days: int = 7) -> Dict:
        """Получить сводку метрик за период"""
        conn = sqlite3.connect(self.db_path)
        
        # Временной фильтр
        since = time.time() - (days * 24 * 3600)
        
        df = pd.read_sql_query('''
            SELECT * FROM test_results 
            WHERE timestamp > ?
        ''', conn, params=(since,))
        conn.close()
        
        if df.empty:
            return {}
        
        total_tests = len(df)
        passed_tests = len(df[df['status'] == 'passed'])
        failed_tests = len(df[df['status'] == 'failed'])
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'pass_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'average_duration': df['duration'].mean(),
            'slowest_tests': df.nlargest(5, 'duration')[['name', 'duration']].to_dict('records'),
            'most_failed_tests': df[df['status'] == 'failed']['name'].value_counts().head().to_dict()
        }
    
    def generate_trend_chart(self, output_path: str = 'test_trends.png'):
        """Генерация графика трендов"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT 
                DATE(timestamp, 'unixepoch') as date,
                status,
                COUNT(*) as count
            FROM test_results 
            WHERE timestamp > ?
            GROUP BY date, status
            ORDER BY date
        ''', conn, params=(time.time() - 30 * 24 * 3600,))  # 30 дней
        conn.close()
        
        if df.empty:
            return
        
        # Создание графика
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # График 1: Количество тестов по дням
        daily_counts = df.groupby('date')['count'].sum()
        ax1.plot(daily_counts.index, daily_counts.values, marker='o')
        ax1.set_title('Daily Test Count')
        ax1.set_ylabel('Number of Tests')
        
        # График 2: Pass Rate
        pass_fail = df.pivot_table(index='date', columns='status', values='count', fill_value=0)
        if 'passed' in pass_fail.columns and 'failed' in pass_fail.columns:
            pass_rate = (pass_fail['passed'] / (pass_fail['passed'] + pass_fail['failed'])) * 100
            ax2.plot(pass_rate.index, pass_rate.values, marker='o', color='green')
            ax2.set_title('Pass Rate Trend')
            ax2.set_ylabel('Pass Rate (%)')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
```

## 5. Практическая реализация

### 5.1 requirements.txt
```
# Core testing
pytest>=7.0.0
pytest-html>=3.1.0
pytest-xdist>=2.5.0
pytest-mock>=3.7.0

# UI Automation
pyautogui>=0.9.54
pywinauto>=0.6.8
Pillow>=9.0.0

# Web Interface
Flask>=2.2.0
Flask-CORS>=3.0.10

# CLI Interface
click>=8.1.0

# Graphs and Metrics
networkx>=2.8
matplotlib>=3.5.0
pandas>=1.4.0

# Utilities
pyyaml>=6.0
requests>=2.28.0
python-dotenv>=0.20.0
```

### 5.2 Пример конфигурации тестов

#### test_config.json
```json
{
  "tests": {
    "setup_environment": {
      "dependencies": [],
      "timeout": 30,
      "retry_count": 2
    },
    "test_calculator_open": {
      "dependencies": ["setup_environment"],
      "app": "calc.exe",
      "timeout": 10
    },
    "test_calculator_addition": {
      "dependencies": ["test_calculator_open"],
      "timeout": 15
    },
    "test_calculator_close": {
      "dependencies": ["test_calculator_addition"],
      "timeout": 5
    }
  },
  "global_settings": {
    "screenshot_on_failure": true,
    "default_timeout": 30,
    "pause_between_actions": 0.5
  }
}
```

### 5.3 Запуск системы

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск веб-интерфейса
python src/ui/web_interface.py

# Запуск тестов через CLI
python src/ui/cli_interface.py run --suite=calculator --markers="smoke"

# Генерация метрик
python src/ui/cli_interface.py metrics --format=json
```

## 6. Заключение и рекомендации

### Рекомендуемый стек для Python + Windows:

1. **Основные инструменты**:
   - pywinauto (приоритет) + PyAutoGUI (fallback)
   - pytest с расширенными fixture'ами
   - Flask для веб-интерфейса

2. **Архитектура**:
   - Слоистая архитектура с четким разделением
   - Конфигурационные файлы в JSON/YAML
   - SQLite для хранения метрик

3. **Метрики и визуализация**:
   - NetworkX для графов зависимостей
   - matplotlib + pandas для аналитики
   - Real-time дашборд через Flask

Эта архитектура обеспечивает гибкость, масштабируемость и простоту сопровождения в Python экосистеме Windows.