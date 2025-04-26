var clockTimer = null;
var monitorTimer = null;
var currentSimTime = null;
var endSimTime = null;
var interval = null;

document.getElementById('start_btn').addEventListener('click', function() {

    for (var i = 0; i < 10; i++) {
        document.getElementById(`driverSpeed${i}`).innerHTML = 0
    }

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

    startTime = `${startYear}-${startMonth}-${startDay} ${startHour}:${startMinute}:${startSecond}`;
    endTime = `${endYear}-${endMonth}-${endDay} ${endHour}:${endMinute}:${endSecond}`;

    currentSimTime = new Date(startTime)
    endSimTime = new Date(endTime)

    if (currentSimTime >= endSimTime) {
        alert("Start Time must be before End Time!");
        return;
    }

    if (startDay !== endDay) {
        alert("Start Time and End Time must be on same day!");
        return;
    }

    document.getElementById('api-text').innerHTML = `Time:<br>Loading...`;

    interval = parseInt(document.getElementById('monitorInterval').value);

    fetch('/api/monitor_start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_time: startTime })
    })
    .then(response => response.json())
    .then(data => {
        if (monitorTimer) {
            clearInterval(monitorTimer);
        }
        updateMonitor();
        monitorTimer = setInterval(updateMonitor, 5000);
    });
});

document.getElementById('end_btn').addEventListener('click', function() {
    console.log("end clicked");
    if (monitorTimer) {
        clearInterval(monitorTimer);
        document.getElementById('api-text').innerHTML = `Time:<br>Monitoring Interrupted.`;
    }
});

function updateMonitor() {
    if (currentSimTime > endSimTime){
        clearInterval(monitorTimer);
        document.getElementById('api-text').innerHTML = `Time:<br>Monitoring Completed.`;
        return;
    }

    var queryEndTime = new Date(currentSimTime)
    queryEndTime.setSeconds(currentSimTime.getSeconds() + interval)

    fetch("/api/monitor", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "start_time": formatDateTime(currentSimTime),
            "end_time": formatDateTime(queryEndTime)
        })
    })

    .then(response => response.json())
    .then(data => {
        document.getElementById('api-text').innerHTML = `Time:<br>${formatDateTime(currentSimTime)}`;
        data.forEach((driver, index) => {
            var driverElement = document.getElementById(`driverLabel${index}`);
            var speedElement = document.getElementById(`driverSpeed${index}`);
            if (speedElement) {
                speedElement.innerText = driver.details.speed;

                if (driver.details.isOverspeed === "1") {
                    console.log(driver.details.speed);
                    console.log(driver.driver_id);
                    driverElement.style.color = "red";
                    driverElement.style.fontWeight = "bold";
                } else {
                    driverElement.style.color = "black";
                    driverElement.style.fontWeight = "normal";
                }
            }
        });
    });

    currentSimTime.setSeconds(currentSimTime.getSeconds() + interval);
}

function formatDateTime(dateObj) {
    var year = dateObj.getFullYear();
    var month = String(dateObj.getMonth() + 1).padStart(2, '0');
    var day = String(dateObj.getDate()).padStart(2, '0');
    var hour = String(dateObj.getHours()).padStart(2, '0');
    var minute = String(dateObj.getMinutes()).padStart(2, '0');
    var second = String(dateObj.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}