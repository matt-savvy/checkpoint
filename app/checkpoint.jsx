var React = require('react');
var ReactDOM = require('react-dom');

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

const checkpoint = getCookie('checkpointID');


class EnterRacer extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			entryField:'',
		}
	}
	handleEntry(e){
		var racerNumber = e.target.value;
		this.setState({entryField : racerNumber});
	}
	handleLookup(racerNumber) {
		this.props.racerLookup(this.state.entryField);
	}
	handleSubmit(e) {
		e.preventDefault();
		this.props.racerLookup(this.state.entryField);
	}
	render() {
		if (this.state.entryField.length >= 3) {
			this.handleLookup()
		}
		
		return (
			<div className="row state-section" id="racer-number-section" style={{display:'flex'}}>
            		<div className="form-group">
                		<label htmlFor="racer-number">Racer Number</label>
                		<p className="text-danger" id="racer-error"></p>
                		<input type="number" className="form-control" id="racer-number" placeholder="Racer #" onChange={this.handleEntry.bind(this)} value={this.state.entryField}/>
            		</div>
            	<button type="button" className="btn btn-success" id="lookup-racer-button" onClick={this.handleLookup.bind(this)} data-loading-text="Loading...">Lookup Racer</button>
			</div>
		)
			
	}
}

class Checkpoint extends React.Component {
	componentWillMount(){
	  /*fetch('/exercises/api/list')
	    .then(function(response) {
	        	if (response.status !== 200) {
	          		console.log('Looks like there was a problem. Status Code: ' + response.status);
					return;
				}
	    		response.json().then(function(data) {
  					this.setState({
  						exercises : data
  					});
	     	 	}.bind(this));
		}.bind(this))
	    .catch(function(err) {
	      console.log('Fetch Error :-S', err);
	    });*/ 
	}
	constructor(props) {
		super(props);
		this.state = {
			availablePickups:null,
			racer:null,
		}
	}
	racerLookup(racer){
		console.log(racer)
		var csrfToken = getCookie('csrftoken');
		var racerRequest = {}
		racerRequest.racer_number = racer;
		racerRequest.checkpoint = checkpoint;
		var racerRequestJOSN = JSON.stringify(racerRequest);
		
		fetch("/api/v1/racer/", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  //credentials: 'include',
		  method: "POST",
		  body: racerRequestJOSN
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log(data);
				
		    }.bind(this));
	
		}.bind(this))
		
	}
	
	getNextMessage() {		
		this.setState({disabled:'disabled', feedback:null, currentMessage: 0});
		var csrfToken = getCookie('csrftoken');
		var nextMessageRequest = {};
		nextMessageRequest.race = this.state.raceID;
		var nextMessageRequestJSON = JSON.stringify(nextMessageRequest);
		fetch("/dispatch/api/next_message/", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  //credentials: 'include',
		  method: "POST",
		  body: nextMessageRequestJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log(data);
				var messages = this.state.messages;
				
				var recentMessage = this.state.messages[0];
				if (recentMessage) {
					if (recentMessage.message_type == MESSAGE_TYPE_NOTHING) {
						messages.shift();
					}
				}
				
				messages.unshift(data);
				this.setState({messages: messages, disabled:null});
				
				
			      }.bind(this));
	
		}.bind(this))
	}
	render(){

		return (
			<EnterRacer racerLookup={this.racerLookup.bind(this)} />
		)
	}
}

ReactDOM.render(
	<Checkpoint />, document.getElementById('react-area')
); 