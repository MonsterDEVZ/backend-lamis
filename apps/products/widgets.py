"""
Custom Widgets for Products Admin
"""

import json
from django import forms
from django.utils.safestring import mark_safe


class CharacteristicsWidget(forms.Textarea):
    """
    Динамический виджет для управления характеристиками товара.

    Отображает интерфейс с кнопками "+" для добавления характеристик
    и "-" для удаления. Каждая характеристика - это пара ключ-значение.

    Пример данных: [{"key": "Ширина", "value": "60 см"}, {"key": "Материал", "value": "МДФ"}]
    """

    def __init__(self, attrs=None):
        default_attrs = {'style': 'display: none;'}  # Скрываем textarea
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        css = {
            'all': ('admin/css/characteristics_widget.css',)
        }
        js = ('admin/js/characteristics_widget.js',)

    def render(self, name, value, attrs=None, renderer=None):
        # Получаем базовый textarea (скрытый)
        textarea_html = super().render(name, value, attrs, renderer)

        # Парсим текущие характеристики
        try:
            if isinstance(value, str):
                characteristics = json.loads(value) if value else []
            elif isinstance(value, list):
                characteristics = value
            else:
                characteristics = []
        except (json.JSONDecodeError, TypeError):
            characteristics = []

        # Генерируем HTML для интерфейса
        widget_html = f'''
        <div class="characteristics-widget" data-name="{name}">
            <div class="characteristics-header">
                <h3 style="margin: 0 0 10px 0; font-size: 14px; color: #333;">
                    Характеристики товара
                </h3>
                <p style="margin: 0 0 15px 0; font-size: 12px; color: #666;">
                    Добавьте структурированные характеристики товара (например: "Ширина: 60 см", "Материал: МДФ")
                </p>
            </div>

            <div class="characteristics-list">
                {self._render_characteristics(characteristics)}
            </div>

            <button type="button" class="add-characteristic-btn"
                    style="margin-top: 10px; padding: 8px 15px; background: #417690; color: white;
                           border: none; border-radius: 4px; cursor: pointer; font-size: 13px;">
                + Добавить характеристику
            </button>

            {textarea_html}
        </div>
        '''

        return mark_safe(widget_html)

    def _render_characteristics(self, characteristics):
        """Генерирует HTML для списка характеристик"""
        if not characteristics:
            return ''

        html_parts = []
        for idx, char in enumerate(characteristics):
            key = char.get('key', '')
            value = char.get('value', '')
            html_parts.append(f'''
                <div class="characteristic-row" style="display: flex; gap: 10px; margin-bottom: 10px; align-items: center;">
                    <input type="text" class="char-key" placeholder="Название (напр. Ширина)"
                           value="{self._escape_html(key)}"
                           style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px;">
                    <input type="text" class="char-value" placeholder="Значение (напр. 60 см)"
                           value="{self._escape_html(value)}"
                           style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px;">
                    <button type="button" class="remove-characteristic-btn"
                            style="padding: 6px 12px; background: #dc3545; color: white;
                                   border: none; border-radius: 4px; cursor: pointer; font-size: 13px;">
                        ✕
                    </button>
                </div>
            ''')

        return '\n'.join(html_parts)

    def _escape_html(self, text):
        """Экранирует HTML спецсимволы"""
        return (
            str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')
        )
