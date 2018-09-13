$(document).ready(function() {
    
    var csrftoken = getCookie('csrftoken');
    
    var STATE_RACER_NUMBER  = 'racer-number-section';
    var STATE_PICK_OR_DROP  = 'pick-or-drop-section';
    var STATE_JOB_NUMBER    = 'job-number-section';
    var STATE_CONFIRM       = 'confirm-section';
    var STATE_DROP_NUMBER   = 'drop-id-section';
    
    var currentState;
    var currentRacer;
    
    //***********************************************************
    //* init
    //***********************************************************
    transitionToState(STATE_RACER_NUMBER);
    
    //***********************************************************
    //* State transition
    //***********************************************************
    function transitionToState(state) {
        $('.state-section').hide();
        $('#' + state).show();
        currentState = state;
        didTransitionToState(state);
    }
    
    function didTransitionToState(state) {
        switch (state) {
        case STATE_RACER_NUMBER:
            $('#racer-number').focus();
            break;
        case STATE_JOB_NUMBER:
            $('#job-number').focus();
            $('#pick-error').hide();
            break;
        case STATE_DROP_NUMBER:
            $('#drop-confirm-number').focus();
            $('#drop-error').hide();
        }
    }
    
    //***********************************************************
    //* Network Calls
    //***********************************************************
    function lookupRacer(racerNumber, found, failure) {
        var racer = getRacerOrFalse(racerNumber);
        if (racer) {
            found(racer);
            return;
        }
		
        var request = new Object();
        request.racer_number = racerNumber;
        request.checkpoint = checkpoint;
        var json = JSON.stringify(request);
        
        $.ajax({
            url: '/api/v1/racer/',
            type: 'POST',
			contentType: 'application/json',
			data: json,
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
				console.log(data);
				if (data.racer){
					addRacerToCache(data.racer);
					found(data.racer);
				}
            },
            error: function(xhr, textStatus, errorThrown) {
                failure();
            }
        });
        
    }
    
    function pickJob(jobNumber, success, inputError, failure) {
        var request = new Object();
        request.racer_number = currentRacer.racer_number;
        request.job_number = jobNumber;
        request.checkpoint = checkpoint;
        var json = JSON.stringify(request);
        $.ajax({
            url: '/api/v1/pick/',
            type: 'POST',
            contentType: 'application/json',
            data: json,
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                if (data.error) {
                    inputError(data.error_title, data.error_description);
                }
                else {
                    success(data.confirm_code);
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                failure();
            }
        });
        
    }
    
    function dropJob(confirmNumber, success, inputError, failure) {
        var request = new Object();
        request.racer_number = currentRacer.racer_number;
        request.confirm_code = confirmNumber;
        request.checkpoint = checkpoint;
        var json = JSON.stringify(request);
        $.ajax({
            url: '/api/v1/drop/',
            type: 'POST',
            contentType: 'application/json',
            data: json,
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                if (data.error) {
                    inputError(data.error_title, data.error_description);
                }
                else {
                    success();
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                failure();
            }
        });
    }
    
    //***********************************************************
    //* Racer Cache
    //***********************************************************
    
    var racerCache = new Array();
    
    function getRacerOrFalse(racerNumber) {
        if (racerCache[racerNumber]) {
            return racerCache[racerNumber];
        }
        return false;
    }
    
    function addRacerToCache(racer) {
        racerCache[String(racer.racer_number)] = racer;
    }
    
    function preloadCache() {
        
    }
    
    //***********************************************************
    //* RacerNumber
    //***********************************************************
    
    $('#lookup-racer-button').click(function() {
        $('#racer-error').text("");
        $('#racer-number').prop('disabled', true);
        $('#lookup-racer-button').button('loading');
        lookupRacer($('#racer-number').val(), function(racer) {
            $('#lookup-racer-button').button('reset');
            $('#racer-number').prop('disabled', false);
            currentRacer = racer;
            $('#racer-name').text(racer.first_name + " '" + racer.nick_name + "' " + racer.last_name);
            transitionToState(STATE_PICK_OR_DROP);
            $('#racer-number').val('');
        },
        function() {
            $('#lookup-racer-button').button('reset');
            $('#racer-number').prop('disabled', false);
            $('#racer-error').text("No racer found with racer number " + $('#racer-number').val() + ".");
            $('#racer-number').val('')
            $('#racer-number').focus();
        });
    });
    
    
    //***********************************************************
    //* Pick or Drop
    //***********************************************************
    
    $('#wrong-racer-button').click(function() {
        transitionToState(STATE_RACER_NUMBER);
    });
    
    $('#pick-button').click(function() {
        transitionToState(STATE_JOB_NUMBER);
    });
    
    $('#drop-button').click(function() {
        transitionToState(STATE_DROP_NUMBER);
    });
    
    //***********************************************************
    //* Pick Job
    //***********************************************************
    $('#not-picking-button').click(function() {
        transitionToState(STATE_PICK_OR_DROP);
    });
    
    $('#job-number-button').click(function() {
        $('#pick-error').hide();
        $('#job-number-button').button('loading');
        $('#job-number').prop('disabled', true);
        
        pickJob($('#job-number').val(), function(confirmCode) {
            $('#job-number-button').button('reset');
            $('#job-number').val("");
            $('#job-number').prop('disabled', false);
            $('#confirm-code').text(confirmCode);
            transitionToState(STATE_CONFIRM);
        }, function(title, description) {
            $('#pick-error').show();
            $("#pick-error-title").text(title);
            $('#pick-error-description').text(description);
            $('#job-number-button').button('reset');
            $('#job-number').prop('disabled', false);
            $('#job-number').val("");
            $('#job-number').focus();
        }, function() {
            $('#pick-error').show();
            $("#pick-error-title").text('Unexpected Error');
            $('#pick-error-description').text('Please try again.');
            $('#job-number-button').button('reset');
            $('#job-number').prop('disabled', false);
            $('#job-number').val("");
            $('#job-number').focus();
        });
        
    });
    
    //***********************************************************
    //* Drop Job
    //***********************************************************
    $('#not-dropping-button').click(function() {
        transitionToState(STATE_PICK_OR_DROP);
    });
    
    $('#drop-confirm-button').click(function() {
        dropJob($("#drop-confirm-number").val(), function() {
            $('#drop-confirm-button').button('reset');
            $("#drop-confirm-number").val('');
            $('#drop-success').show();
            transitionToState(STATE_RACER_NUMBER);
        }, function(title, description) {
            $('#drop-error').show();
            $("#drop-error-title").text(title);
            $('#drop-error-description').text(description);
            $('#drop-confirm-button').button('reset');
            $("#drop-confirm-number").val('');
            $("#drop-confirm-number").focus();
        }, function() {
            $('#drop-error').show();
            $("#drop-error-title").text('Unexpected Error');
            $('#drop-error-description').text("Please try again.");
            $('#drop-confirm-button').button('reset');
            $("#drop-confirm-number").val('');
            $("#drop-confirm-number").focus();
        });
    });
    
    //***********************************************************
    //* Confirm Code
    //***********************************************************
    $('#next-racer').click(function() {
        transitionToState(STATE_RACER_NUMBER);
    });
    
    //***********************************************************
    //* CSRF Protection
    //***********************************************************
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

                               
});