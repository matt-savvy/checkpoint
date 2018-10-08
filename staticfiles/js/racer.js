$(document).ready(function() {
	
	
	console.log("help");

	$('#racer_table').DataTable({
		"paging":   false,
		 "ordering": true,
	});
	
	var csrftoken = getCookie('csrftoken'); 
	
	function markRacerAsPaid(pk) {
		console.log(pk);
        var request = Object()
        request.racer_pk = pk;
        var json = JSON.stringify(request);
		
	    $.ajax({
	        url: '/ajax/racerpaid/',
	        type: 'POST',
			data :json,
			contentType: 'application/json',
	        beforeSend: function (request) {
	            request.setRequestHeader("X-CSRFToken", csrftoken);
	        },
	        success: function(data, textStatus, xhr) {
	            console.log("success");
				var id = "#paid" + pk;
				$racerSpan = $(id);
				$racerSpan.text("paid");
				$racerSpan.addClass('success');
				$racerSpan.removeClass('danger');
	        },
	        error: function(xhr, textStatus, errorThrown) {

	        }
	    });
	}
	
	$('.paid').click(function() {
		var pk = $(this).val();
		markRacerAsPaid(pk);
		$(this).prop('disabled', true);
	});


    
    //**********************************************
    //* CSRF Protection
    //**********************************************
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

