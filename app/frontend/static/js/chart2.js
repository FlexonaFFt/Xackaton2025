document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('acquisitions2');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['9:00', '12:00', '14:00', '17:00', '19:00', '22:00'],
            datasets: [{
                label: 'Статистика запросов по времени',
                data: [8, 12, 5, 15, 10, 6],
                backgroundColor: 'rgba(52, 194, 119, 0.6)',
                borderColor: '#34c277',
                borderWidth: 1,
                borderRadius: 5,
                hoverBackgroundColor: 'rgba(52, 194, 119, 0.8)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff',
                        font: {
                            size: 14
                        }
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
});