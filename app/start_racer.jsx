var React = require('react');
var ReactDOM = require('react-dom');
var Message = require('Message');
var Feedback = require('Feedback');
var EnterRacer = require('EnterRacer');
const raceID = getCookie('raceID');

const MESSAGE_TYPE_DISPATCH = 0
const MESSAGE_TYPE_OFFICE   = 1
const MESSAGE_TYPE_NOTHING  = 2
const MESSAGE_TYPE_ERROR    = 3

const MESSAGE_STATUS_NONE        = 0
const MESSAGE_STATUS_DISPATCHING = 1
const MESSAGE_STATUS_SNOOZED     = 2
const MESSAGE_STATUS_CONFIRMED   = 3

const MODE_LOOKUP_RACER = "lookup";
const MODE_RACER_FOUND = "found";
const MODE_RACER_CONFIRMED = "confirmed";

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

class Racer extends React.Component {
	constructor(props) {
		super(props);
	}
	handleNextRacer() {
		this.props.reset();
	}
	render () {		
		return (
		<div>
			<div className="row">
				<div className="col">
					
			{this.props.mode == MODE_RACER_FOUND && <button type="button" id="wrong-racer-button" onClick={this.handleNextRacer.bind(this)} className="btn btn-danger btn-sm">RESET</button>}
		
			
					<h3 className="text-center">
						#{this.props.racer.racer.racer_number} {this.props.racer.racer.first_name} {this.props.racer.racer.nick_name} {this.props.racer.racer.last_name} 
						<br /> 
						<small>
						{this.props.racer.racer.contact_info}
						</small>	
					</h3>
				</div>
			</div>	
					
		</div>
		)
	}
}




class StartRacerScreen extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			raceID:raceID,
			feedback: null,
			disabled: null,
			mode : MODE_LOOKUP_RACER,
			currentMessage:null,
			currentRacer:null,
			showConfirm:false,
		}
	}
	riderResponse(e) {
		console.log(e.target.value);
		this.setState({disabled:'disabled'});
		var csrfToken = getCookie('csrftoken');
		var riderResponse = {};
		riderResponse.message = this.state.messages[this.state.currentMessage].id;
		riderResponse.action = e.target.value;
		var riderResponseJSON = JSON.stringify(riderResponse);
		fetch("/dispatch/api/rider_response/", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  //credentials: 'include',
		  method: "POST",
		  body: riderResponseJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log(data);
				var messages = this.state.messages
				messages[this.state.currentMessage] = data.message;
				this.setState({feedback:data.message, disabled:null, showRefresh:true, messages:messages})
			      }.bind(this));
		}.bind(this)) 
	}
	undo () {		
		this.setState({disabled:'disabled'});
		
		var csrfToken = getCookie('csrftoken');
		var riderResponse = {};
		riderResponse.message = this.state.messages[this.state.currentMessage].id;
		riderResponse.action = "UNDO";
		var riderResponseJSON = JSON.stringify(riderResponse);
		fetch("/dispatch/api/rider_response/", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  //credentials: 'include',
		  method: "POST",
		  body: riderResponseJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				//console.log(data);
				var messages = this.state.messages
				messages[this.state.currentMessage] = data.message;
				this.setState({feedback:null, disabled:null, showRefresh:null, messages:messages})
			      }.bind(this));
		}.bind(this)) 
	}
	racerLookup(racer) {		
		this.setState({disabled:'disabled', feedback:null, currentMessage: null, error_description:null});
		var url = "/dispatch/start/" + racer + "/"
		fetch(url, {
		  headers: {
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  method: "GET",
		})
		.then(function(response) {
			console.log(response);
			
        	if (response.status == 500) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			} else if (response.status == 404) {
				console.log("here");
				this.setState({currentRacer: null, mode: MODE_LOOKUP_RACER, currentMessage: null, disabled:null, error_description: "Racer not found with this number."});
				return;
			} else {
				response.json().then(function(data) {
					console.log("promise");
					if ((response.status == 200) && (data.racer)) {
						console.log(data);
					 	this.setState({currentRacer: data, mode: MODE_RACER_FOUND, currentMessage: null, disabled:null, error_description: null});
					}
					
				}.bind(this));
			}
			
	
		}.bind(this))
	}
	reset() {
		this.setState({currentRacer:null, mode:MODE_LOOKUP_RACER, currentMessage:null, disabled:null, error_description:null})
	}
	render(){
		var currentMessage = this.state.currentMessage;
		var showConfirm = this.state.showConfirm;

		if (currentMessage) {
			messageNumber = currentMessage.id;
			
			if ((currentMessage.status == MESSAGE_STATUS_DISPATCHING) || (currentMessage.status == MESSAGE_STATUS_CONFIRMED)){
				messageStatus = currentMessage.message_status_as_string;
			}
		}

		if (this.state.mode == MODE_LOOKUP_RACER) {
			return (
				<EnterRacer racerLookup={this.racerLookup.bind(this)} error_description={this.state.error_description}/>
			)
		} else if (this.state.mode == MODE_RACER_FOUND) {
			return (
				<Racer racer={this.state.currentRacer} reset={this.reset.bind(this)} mode={this.state.mode} currentMessage={this.state.currentMessage}/>	
			)
		}
		
		return (
		<div className="container">
			<div className="row">
				<div className="col text-left">
						<button disabled={showBack} onClick={this.showBackMessage.bind(this)} className="btn btn" value="Show Last"><i className="fas fa-caret-left"></i> Prev</button>
				</div>
				<div className="col text-center">
					{showRefresh && <button onClick={this.getNextMessage.bind(this)} className="btn btn-info" disabled={this.state.disabled} value="NEXT"><i className="fas fa-sync-alt"></i> Refresh</button>}
				</div>
			
				<div className="col text-right">		
						<button disabled={showForward} onClick={this.showNextMessage.bind(this)} className="btn btn" value="Show Next"><i className="fas fa-caret-right"></i> Next</button>
				</div>
			
			</div>
			<div className="row">
				<br />{messageNumber && <span>Message ID #{messageNumber}</span>}
			</div>
			
			
			<div className="row">
				<div className="col-md-6 text-center">
					{message}
				</div>
			</div>
			<div className="row">
					{this.state.feedback && <Feedback object={this.state.feedback} undo={this.undo.bind(this)} />}
					{this.state.messageStatus && <div className="alert alert-warning" role="alert">{messageStatus}</div>}
			</div>
			<div className="row bottom-navbar">
				<div className="col text-left">
					{showConfirm && <button onClick={this.riderResponse.bind(this)} className="btn btn-danger btn-sm" disabled={this.state.disabled}  value="SNOOZE"><i className="fas fa-user-slash"></i> No Response</button>}
				</div>
				
				<div className="col text-right">
					{showConfirm && <button onClick={this.riderResponse.bind(this)} className="btn btn-success btn-sm" disabled={this.state.disabled} value="CONFIRM"><i className="fas fa-check-circle"></i> Confirmed</button>}
				</div>
			</div>

		
		</div>
		)
	}
}

ReactDOM.render(
	<StartRacerScreen />, document.getElementById('react-area')
); 