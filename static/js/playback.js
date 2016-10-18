$(document).ready(function() {
    var MAX_MINUTES = 180;
    var currentMinutes = 0;
    var isLoading = false;
    
    loadStandings(0);
    updateButtons();
    
    $('#slider').slider({
	formatter: function(value) {
		return secondsToTime(value)
    }
	});
    
    function loadStandings(minute) {
        if (typeof minute == 'undefined') {
            minute = 0;
        }
        if (minute > MAX_MINUTES || minute < 0) {
            return;
        }
        loading();
        $.ajax({
            url: '/events/' + minute + '/',
            type: 'GET',
            success: function(data, textStatus, xhr) {
                currentMinutes = minute;
                updateButtons();
                updateTime();
                updateSlider();
                $('#events').html(data);
                loading();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }
    
    function updateButtons() {
        if (currentMinutes == 0) {
            $('#back-button').prop('disabled', true);
        }
        else {
            $('#back-button').prop('disabled', false);
        }
        
        if (currentMinutes == MAX_MINUTES) {
            $('#forward-button').prop('disabled', true);
        }
        else {
            $('#forward-button').prop('disabled', false);
        }
    }
    
    $('#back-button').click(function() {
        loadStandings(currentMinutes - 1);
    });
    
    $('#forward-button').click(function() {
        loadStandings(currentMinutes + 1);
    });
    
    function updateTime() {
        hours = parseInt(currentMinutes / 60);
        minutes = parseInt(currentMinutes % 60);
        time = pad(hours,2) + ":" + pad(minutes,2);
        $('#current-time').text(time + " / 03:00");
    }
    
    function secondsToTime(seconds) {
        hours = parseInt(seconds / 60);
        minutes = parseInt(seconds % 60);
        return pad(hours,2) + ":" + pad(minutes,2);
    }
    
    
    function updateSlider() {
        $('#slider').slider('setValue', currentMinutes);
    }
    
    $('#slider').on("slideStop", function(event) {
        loadStandings(event.value);
    });
    
    function loading() {
        if (isLoading) {
            $('.btn').button('reset');
            $('#slider').prop('disabled', false);
            isLoading = false;
        }
        else {
            $('.btn').button('loading');
            isLoading = true;
            $('#slider').prop('disabled', false);
        }
    }
    
    //From StackOverflow. 
    function pad(num, size) {
        var s = num+"";
        while (s.length < size) s = "0" + s;
        return s;
    }
});
