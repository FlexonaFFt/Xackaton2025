document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('acquisitions3');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['PDF', 'TXT', 'PNG', 'JPG', 'JPEG', 'DOCX'],
            datasets: [{
                label: 'Распределение по типам файлов',
                data: [12, 19, 3, 5, 2, 3],
                borderColor: '#34c277',
                backgroundColor: 'rgba(52, 194, 119, 0.2)',
                tension: 0.4,
                fill: true,
                borderWidth: 2,
                pointBackgroundColor: '#34c277',
                pointBorderColor: '#fff',
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
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
});