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
const MODE_RACER_STARTED = "started";
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

class Checklist extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			infoCorrect:false,
			helmet:false,
			radio:false,
		}
	}
    handleInputChange(event) {
      var target = event.target;
      var value = target.type === 'checkbox' ? target.checked : target.value;
      var name = target.name;

      this.setState({
        [name]: value
      });
    }
	handleStartRacer(){
		console.log("started racer");
		this.props.startRacer();
	}
	render() {
		var disabled = true;
		
		if (this.state.infoCorrect && this.state.helmet && this.state.radio) {
			disabled = false;
		}
		
		return (				
			<div>
				<div className="form-check">
					<input onChange={this.handleInputChange.bind(this)} className="form-check-input" type="checkbox" checked={this.state.infoCorrect} id="infoCorrect" name="infoCorrect" />
					<label className="form-check-label" htmlFor="infoCorrect">
  		  				<h3>Racer Info Correct?</h3>
 		   			</label>
				</div>
			
				<div className="form-check">
					<input onChange={this.handleInputChange.bind(this)} className="form-check-input" type="checkbox" checked={this.state.helmet} id="helmet" name="helmet" />
					<label className="form-check-label" htmlFor="helmet">
  		  				<h3>Helmet?</h3>
 		   			</label>
				</div>
				
				
				<div className="form-check">
					<input onChange={this.handleInputChange.bind(this)} className="form-check-input" type="checkbox" checked={this.state.radio} id="radio" name="radio" />
					<label className="form-check-label" htmlFor="radio">
  		  				<h3>Radio Check?</h3>
 		   			</label>
				</div>
			
				<p>
					<button className="btn btn-lg btn-info" disabled={disabled} onClick={this.handleStartRacer.bind(this)}>Start Racer</button> 
				</p>
				
			</div>
		)
			
	}
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
			feedback: null,
			disabled: null,
			mode : MODE_LOOKUP_RACER,
			currentMessage:null,
			currentRacer:null,
			showConfirm:false,
		}
	}
	startRacer() {
		console.log("starting racer");
		this.setState({disabled:'disabled'});
		
		var csrfToken = getCookie('csrftoken');
		var racerRequest = {};
		racerRequest.racer = this.state.currentRacer.racer.racer_number;
		racerRequest.race = raceID;
		var racerRequestJSON = JSON.stringify(racerRequest);
		fetch("/ajax/startracer/", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  //credentials: 'include',
		  method: "POST",
		  body: racerRequestJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log(data);
				
				this.setState({feedback:null, currentMessage: data.message, disabled:null, mode: MODE_RACER_STARTED, showConfirm:true, dueTime:data.due_time})
			      }.bind(this));
		}.bind(this)) 
	}
	racerLookup(racer) {		
		this.setState({disabled:'disabled', feedback:null, currentMessage: null, error_description:null});
		var url = "/dispatch/start/lookup/" + racer + "/"
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
				<div>
					<Racer racer={this.state.currentRacer} reset={this.reset.bind(this)} mode={this.state.mode}/>	
					<Checklist racer={this.state.currentRacer} startRacer={this.startRacer.bind(this)}/>
				</div>
			)
		} else if (this.state.mode == MODE_RACER_STARTED) {
			console.log("racer started!")
			return (
				<div>
				<Message />	
				</div>
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