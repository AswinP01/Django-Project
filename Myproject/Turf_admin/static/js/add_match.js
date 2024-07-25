$(document).ready(function() {
    // Datepicker setup
    $('#datepicker').datepicker({
        format: 'yyyy-mm-dd',
        startDate: new Date(),
        autoclose: true
    });
});

document.getElementById('bookingForm').addEventListener('submit', function(event) {

// Get the selected time in 12-hour format
const startTime12 = document.querySelector('select[name="start_time"]').value;

// Convert the 12-hour format time to 24-hour format
const [time, period] = startTime12.split(' ');
let [hours, minutes] = time.split(':');
if (period === 'PM' && hours !== '12') {
    hours = parseInt(hours) + 12;
} else if (period === 'AM' && hours === '12') {
    hours = '00';
}

const startTime24 = `${hours}:${minutes}:00`;

// Set the converted time to the hidden input field
document.getElementById('start_time_24').value = startTime24;
});


