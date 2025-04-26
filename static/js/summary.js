document.getElementById('submit_btn').addEventListener('click', function() {
    var driverID = document.getElementById('driverID').value;

    var startYear = document.getElementById('startYear').value;
    var startMonth = String(document.getElementById('startMonth').value).padStart(2, '0');
    var startDay = String(document.getElementById('startDay').value).padStart(2, '0');
    var startHour = String(document.getElementById('startHour').value).padStart(2, '0');
    var startMinute = String(document.getElementById('startMinute').value).padStart(2, '0');
    var startSecond = String(document.getElementById('startSecond').value).padStart(2, '0');

    var endYear = document.getElementById('endYear').value;
    var endMonth = String(document.getElementById('endMonth').value).padStart(2, '0');
    var endDay = String(document.getElementById('endDay').value).padStart(2, '0');
    var endHour = String(document.getElementById('endHour').value).padStart(2, '0');
    var endMinute = String(document.getElementById('endMinute').value).padStart(2, '0');
    var endSecond = String(document.getElementById('endSecond').value).padStart(2, '0');

    var start_time = `${startYear}-${startMonth}-${startDay} ${startHour}:${startMinute}:${startSecond}`;
    var end_time = `${endYear}-${endMonth}-${endDay} ${endHour}:${endMinute}:${endSecond}`;

    const start_date = new Date(start_time);
    const end_date = new Date(end_time);

    if (start_date > end_date) {
        alert("Start time must be before end time!");
        return; // Stop the fetch request
    }

    document.getElementById('api-text').innerHTML = `Showing result for:<br>Loading...`;

    fetch("/api/summary", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "driverID": driverID,
            "start_time": start_time,
            "end_time": end_time
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('api-text').innerHTML = "";
            alert("No data found for the selected period.");
        } else {
            document.getElementById('api-text').innerHTML =
                `Showing result for:<br><strong>${data.driverID}</strong> between <strong>${start_time}</strong> and <strong>${end_time}</strong>`;

            const keys = [
                "isRapidlySpeedup", "isRapidlySlowDown", "isNeutralSlideFinished",
                "isOverspeedFinished", "isFatigueDriving", "isHthrottleStop", "isOilLeak",
                "neutralSlideDuration", "overspeedDuration"
            ];

            keys.forEach(key => {
                document.getElementById(key).innerText = data[key];
            });
        }
    });
});