document.addEventListener('DOMContentLoaded', function() {
    try {
        // Parse JSON data
        var bookingsChartData = JSON.parse(document.getElementById('bookings-data').textContent);
        var revenueChartDataBookings = JSON.parse(document.getElementById('revenue-data-bookings').textContent);
        var revenueChartDataMatches = JSON.parse(document.getElementById('revenue-data-matches').textContent);
        var combinedRevenueChartData = JSON.parse(document.getElementById('combined-revenue-data').textContent);

        console.log('Bookings Data:', bookingsChartData);
        console.log('Revenue Data (Bookings):', revenueChartDataBookings);
        console.log('Revenue Data (Matches):', revenueChartDataMatches);
        console.log('Combined Revenue Data:', combinedRevenueChartData);

        // Create Bookings Chart
        var bookingsCtx = document.getElementById('bookingsChart').getContext('2d');
        new Chart(bookingsCtx, {
            type: 'line',
            data: {
                labels: bookingsChartData.labels,
                datasets: [{
                    label: 'Bookings',
                    data: bookingsChartData.data,
                    borderColor: 'blue',
                    backgroundColor: 'rgba(0, 0, 255, 0.1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Bookings'
                        }
                    }
                }
            }
        });

        // Create Revenue Charts
        var revenueCtxBookings = document.getElementById('revenueChartBookings').getContext('2d');
        var revenueCtxMatches = document.getElementById('revenueChartMatches').getContext('2d');

        new Chart(revenueCtxBookings, {
            type: 'line',
            data: {
                labels: revenueChartDataBookings.labels,
                datasets: [{
                    label: 'Revenue from Bookings',
                    data: revenueChartDataBookings.data,
                    borderColor: 'green',
                    backgroundColor: 'rgba(0, 255, 0, 0.1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Total Revenue'
                        }
                    }
                }
            }
        });

        new Chart(revenueCtxMatches, {
            type: 'line',
            data: {
                labels: revenueChartDataMatches.labels,
                datasets: [{
                    label: 'Revenue from Matches',
                    data: revenueChartDataMatches.data,
                    borderColor: 'red',
                    backgroundColor: 'rgba(255, 0, 0, 0.1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Total Revenue'
                        }
                    }
                }
            }
        });

        // Create Combined Revenue Chart
        var combinedRevenueCtx = document.getElementById('combinedRevenueChart').getContext('2d');
        new Chart(combinedRevenueCtx, {
            type: 'line',
            data: {
                labels: combinedRevenueChartData.labels,
                datasets: [
                    {
                        label: 'Revenue from Bookings',
                        data: combinedRevenueChartData.data_bookings,
                        borderColor: 'green',
                        backgroundColor: 'rgba(0, 255, 0, 0.1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Revenue from Matches',
                        data: combinedRevenueChartData.data_matches,
                        borderColor: 'red',
                        backgroundColor: 'rgba(255, 0, 0, 0.1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Total Revenue'
                        }
                    }
                }
            }
        });

    } catch (e) {
        console.error('Error parsing JSON data:', e);
    }
});
