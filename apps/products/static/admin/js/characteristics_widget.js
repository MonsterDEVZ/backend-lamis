/**
 * Динамический виджет для управления характеристиками товара в Django Admin
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем все виджеты характеристик на странице
    document.querySelectorAll('.characteristics-widget').forEach(function(widget) {
        initCharacteristicsWidget(widget);
    });
});

function initCharacteristicsWidget(widget) {
    const textarea = widget.querySelector('textarea');
    const list = widget.querySelector('.characteristics-list');
    const addBtn = widget.querySelector('.add-characteristic-btn');

    // Обработчик добавления новой характеристики
    addBtn.addEventListener('click', function(e) {
        e.preventDefault();
        addCharacteristicRow(list);
        syncToTextarea(widget);
    });

    // Обработчики для существующих строк
    attachRowHandlers(widget);

    // Синхронизируем при изменении
    list.addEventListener('input', function() {
        syncToTextarea(widget);
    });

    // Начальная синхронизация
    syncToTextarea(widget);
}

function addCharacteristicRow(list, key = '', value = '') {
    const row = document.createElement('div');
    row.className = 'characteristic-row';
    row.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px; align-items: center;';

    row.innerHTML = `
        <input type="text" class="char-key" placeholder="Название (напр. Ширина)"
               value="${escapeHtml(key)}"
               style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px;">
        <input type="text" class="char-value" placeholder="Значение (напр. 60 см)"
               value="${escapeHtml(value)}"
               style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px;">
        <button type="button" class="remove-characteristic-btn"
                style="padding: 6px 12px; background: #dc3545; color: white;
                       border: none; border-radius: 4px; cursor: pointer; font-size: 13px;">
            ✕
        </button>
    `;

    list.appendChild(row);

    // Обработчик удаления
    const removeBtn = row.querySelector('.remove-characteristic-btn');
    removeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        row.remove();
        syncToTextarea(row.closest('.characteristics-widget'));
    });
}

function attachRowHandlers(widget) {
    widget.querySelectorAll('.remove-characteristic-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            btn.closest('.characteristic-row').remove();
            syncToTextarea(widget);
        });
    });
}

function syncToTextarea(widget) {
    const textarea = widget.querySelector('textarea');
    const rows = widget.querySelectorAll('.characteristic-row');

    const characteristics = [];
    rows.forEach(function(row) {
        const key = row.querySelector('.char-key').value.trim();
        const value = row.querySelector('.char-value').value.trim();

        // Добавляем только непустые характеристики
        if (key || value) {
            characteristics.push({ key, value });
        }
    });

    textarea.value = JSON.stringify(characteristics);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
