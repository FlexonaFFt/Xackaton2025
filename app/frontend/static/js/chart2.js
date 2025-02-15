document.addEventListener('DOMContentLoaded', async () => {
    const ctx = document.getElementById('acquisitions2');
    
    try {
        const timeStats = await fetchTimeStatistics();
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Успешные', 'Отклоненные', 'Всего'],
                datasets: [{
                    label: 'Статистика запросов',
                    data: [timeStats.success, timeStats.fail, timeStats.total],
                    backgroundColor: [
                        'rgba(52, 194, 119, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)'
                    ],
                    borderColor: [
                        '#34c277',
                        '#ff6384',
                        '#36a2eb'
                    ],
                    borderWidth: 1,
                    borderRadius: 5,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff',
                            font: { size: 14 }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#ffffff'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#ffffff'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating chart:', error);
    }
});