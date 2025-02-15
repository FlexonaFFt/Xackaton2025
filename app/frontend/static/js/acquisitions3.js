

import Chart from 'chart.js/auto'
import { fontString } from 'chart.js/helpers';
document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('acquisitions3');
    if (!ctx) {
        console.error('Element with id "myChart" not found');
        return;
    }

    let chart; // Объявляем переменную для хранения экземпляра графика

    function getThemeColors() {
        
        return {
            borderColor: 'rgba(90, 183, 88, 0.5)',
            pointBackgroundColor: 'rgba(90, 183, 88, 1)',
            pointBorderColor: '#fff',
            textColor:  'rgba(0, 0, 0, 0.8)',
            gridColor: 'rgba(0, 0, 0, 0.1)'
        };
    }

    function createChart() {
        const colors = getThemeColors();
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(90, 183, 88, 0.5)');
        gradient.addColorStop(1, 'rgba(75, 192, 192, 0)');

        // Если график уже существует, уничтожаем его
        if (chart) {
            chart.destroy();
        }

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['PDF', 'TXT', 'PDG', 'JPG', 'JPEG', 'DOCX'],
                datasets: [{
                    label: 'Статистика запросов по времени',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: colors.borderColor,
                    backgroundColor: gradient,
                    tension: 0.4,
                    fill: true,
                    borderWidth: 2,
                    pointBackgroundColor: colors.pointBackgroundColor,
                    pointBorderColor: colors.pointBorderColor,
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        align:'end',
                        labels: {
                            color: colors.textColor,
                            font: {
                                family: 'Montserrat',
                                size: 20
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        grid: {
                            color: colors.gridColor,
                            drawBorder: false
                        },
                        ticks: {
                            stepSize: 4,
                            color: colors.textColor,
                            padding: 10,
                            font: {
                                family: 'Montserrat',
                                size: 14
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            
                            color: colors.textColor,
                            padding: 10,
                            font: {
                                family: 'Montserrat',
                                size: 14
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // Создаем начальный график
    createChart();

    // Слушаем изменение темы
    const observer = new MutationObserver(() => {
        createChart();
    });

    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });
});