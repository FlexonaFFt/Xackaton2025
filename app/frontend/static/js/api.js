async function fetchFileStatistics() {
    try {
        const response = await fetch('/queries/statistics/files');
        const data = await response.json();
        return data.statistics;
    } catch (error) {
        console.error('Error fetching file statistics:', error);
        return [];
    }
}

async function fetchTimeStatistics() {
    try {
        const response = await fetch('/queries/statistics/time_period?period=day');
        const data = await response.json();
        return {
            success: data.success_count,
            fail: data.fail_count,
            total: data.total_count
        };
    } catch (error) {
        console.error('Error fetching time statistics:', error);
        return { success: 0, fail: 0, total: 0 };
    }
}

async function fetchRecentQueries() {
    try {
        const response = await fetch('/queries/recent_queries');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;  
    } catch (error) {
        console.error('Error fetching recent queries:', error);
        return { queries: [] };  
    }
}

function updateQueriesTable(data) {
    const tableContainer = document.querySelector('.requests-table');
    if (!tableContainer) {
        console.error('Table container not found');
        return;
    }

    // Очищаем существующие строки (кроме заголовка)
    const existingRows = tableContainer.querySelectorAll('.table-row');
    existingRows.forEach(row => row.remove());
    
    // Проверяем наличие данных
    if (!data || !data.queries || data.queries.length === 0) {
        const emptyRow = document.createElement('div');
        emptyRow.className = 'table-row';
        emptyRow.innerHTML = `
            <div class="table-cell" style="grid-column: 1 / -1; text-align: center;">
                Нет доступных запросов
            </div>
        `;
        tableContainer.appendChild(emptyRow);
        return;
    }
    
    // Добавляем новые строки
    data.queries.forEach(query => {
        const row = document.createElement('div');
        row.className = 'table-row';
        row.innerHTML = `
            <div class="table-cell">${query.id || 'N/A'}</div>
            <div class="table-cell">${query.info || 'Нет информации'}</div>
            <div class="table-cell ${query.is_confidential ? 'status-failed' : 'status-success'}">
                ${query.is_confidential ? 'Конфиденциально' : 'Не прошло проверку'}
            </div>
            <div class="table-cell query-text">${query.query || 'Нет текста запроса'}</div>
        `;
        tableContainer.appendChild(row);
    });
}

// Загружаем данные при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const data = await fetchRecentQueries();
        updateQueriesTable(data);
    } catch (error) {
        console.error('Error loading queries:', error);
        updateQueriesTable({ queries: [] });
    }
});