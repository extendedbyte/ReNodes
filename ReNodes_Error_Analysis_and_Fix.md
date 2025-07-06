# Анализ и исправление ошибки ReNodes: AttributeError 'NoneType' object has no attribute 'get_zoom'

## Описание проблемы

**Ошибка:** 
```
Date: 2024-12-24 21:29:52.655063
ReNode 1.10.84b1b3c
Необработанное исключение: AttributeError
'NoneType' object has no attribute 'get_zoom'

Exception info: Traceback (most recent call last):
File "NodeGraphQt\qgraphics\node_base.py", line 334, in paint
File "NodeGraphQt\qgraphics\node_base.py", line 237, in _paint_horizontal
AttributeError: 'NoneType' object has no attribute 'get_zoom'

Дополнительная информация:
Последняя команда: delete node: "Создать массив"
```

## Анализ проблемы

### Корень проблемы
Ошибка возникает в методах `_paint_horizontal` и `_paint_vertical` класса `NodeItem` при попытке вызова `self.viewer().get_zoom()`. 

### Причина
Метод `viewer()` в `node_abstract.py` возвращает `None` когда узел удаляется из сцены:

```python
def viewer(self):
    """
    return the main viewer.
    Returns:
        NodeGraphQt.widgets.viewer.NodeViewer: viewer object.
    """
    if self.scene():
        return self.scene().viewer()
```

Если `self.scene()` возвращает `None` (что происходит при удалении узла), то метод `viewer()` также возвращает `None`. Затем при вызове `None.get_zoom()` возникает ошибка `AttributeError`.

### Проблемные строки
В файле `NodeGraphQt/qgraphics/node_base.py`:
- **Строка 237** (в методе `_paint_horizontal`): `pen.setCosmetic(self.viewer().get_zoom() < 0.0)`
- **Строка 314** (в методе `_paint_vertical`): `pen.setCosmetic(self.viewer().get_zoom() < 0.0)`

## Исправление

### Решение
Добавить проверку на `None` перед вызовом `get_zoom()`:

```python
# До исправления:
pen.setCosmetic(self.viewer().get_zoom() < 0.0)

# После исправления:
viewer = self.viewer()
pen.setCosmetic(viewer.get_zoom() < 0.0 if viewer else False)
```

### Примененные изменения

**Файл:** `NodeGraphQt/qgraphics/node_base.py`

**Место 1 (строка ~237 в методе `_paint_horizontal`):**
```python
pen = QtGui.QPen(border_color, border_width)
viewer = self.viewer()
pen.setCosmetic(viewer.get_zoom() < 0.0 if viewer else False)
path = QtGui.QPainterPath()
```

**Место 2 (строка ~314 в методе `_paint_vertical`):**
```python
pen = QtGui.QPen(border_color, border_width)
viewer = self.viewer()
pen.setCosmetic(viewer.get_zoom() < 0.0 if viewer else False)
painter.setBrush(QtCore.Qt.NoBrush)
```

## Объяснение исправления

1. **Получение viewer**: `viewer = self.viewer()` - получаем объект viewer (может быть `None`)
2. **Условная проверка**: `viewer.get_zoom() < 0.0 if viewer else False` - если viewer существует, используем его zoom, иначе возвращаем `False`
3. **Безопасность**: Этот подход предотвращает ошибку `AttributeError` при удалении узлов

## Тестирование

После применения исправления:
- ✅ Узлы должны корректно удаляться без ошибок
- ✅ Отрисовка узлов продолжает работать нормально
- ✅ Метод `paint` больше не вызывает исключений при удалении узлов

## Дополнительные рекомендации

### Профилактические меры
1. **Проверка на None**: Всегда проверять результат `self.viewer()` на `None` перед использованием
2. **Defensive programming**: Использовать паттерн `obj.method() if obj else default_value`
3. **Централизованный helper**: Можно создать вспомогательный метод для безопасного получения zoom:

```python
def get_viewer_zoom(self, default=1.0):
    """Безопасно получить zoom от viewer."""
    viewer = self.viewer()
    return viewer.get_zoom() if viewer else default
```

### Другие потенциальные проблемы
Следует проверить другие места в коде, где используется `self.viewer()` без проверки на `None`, особенно:
- Обработчики событий мыши
- Методы отрисовки
- Методы обновления состояния

## Статус
- ✅ **Проблема проанализирована**
- ✅ **Исправление применено**
- ✅ **Код готов к тестированию**

## Заключение

Проблема была вызвана отсутствием проверки на `None` при работе с объектом viewer во время удаления узлов. Исправление обеспечивает graceful handling ситуации, когда узел находится в процессе удаления и viewer недоступен.