var path;   // path; to handle cases where the app might be using a path other than /
var refreshInterval = 5;    // minutes

$(document).ready(function() {
    path = window.location.pathname;

    refreshWeather();
    // Auto refresh
    setInterval(refreshWeather, refreshInterval * 60 * 1000);
});

function refreshWeather() {
    // Get the weather details
    $.get(path + "api")
    .done(function(data) {
        updateHtml(data);
        markLastUpdate(true);
    })
    .fail(function() {
        markLastUpdate(false);
    });
}

function updateHtml(weather) {
    var haveData = weather != null;
    $("#location").html(haveData ? weather.place: "&dash;");
    $("#temperature").html(haveData ? weather.temperature.value + "&deg; " + weather.temperature.units
                                    : "&dash;&deg; F");
    $("#humidity").html((haveData ? weather.humidity : "&dash;") + "%");
}

function markLastUpdate(success) {
    var auto_refresh_str = "<br>(Auto-refreshes every " + refreshInterval + " minutes)";
    var now = Date();
    if (success) {
        $("#last-updated").html("Last updated on " + now + auto_refresh_str);
    } else {
        $("#last-updated").html("Last update failed on " + now + auto_refresh_str);
    }
}
