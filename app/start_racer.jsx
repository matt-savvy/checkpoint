var React = require('react');
var ReactDOM = require('react-dom');
var Message = require('Message');
var Feedback = require('Feedback');
var EnterRacer = require('EnterRacer');
var Racer = require('RacerSmall');
const raceID = getCookie('raceID');

const MESSAGE_TYPE_DISPATCH = 0
const MESSAGE_TYPE_OFFICE   = 1
const MESSAGE_TYPE_NOTHING  = 2
const MESSAGE_TYPE_ERROR    = 3

const MESSAGE_STATUS_NONE        = 0
const MESSAGE_STATUS_DISPATCHING = 1
const MESSAGE_STATUS_SNOOZED     = 2
const MESSAGE_STATUS_CONFIRMED   = 3

const ENTRY_STATUS_ENTERED = 0

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
			if (!this.props.disabled) {
				disabled = false;
			}
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
	startRacer(unstart) {
		console.log("starting racer");
		console.log("unstart" + unstart);
		this.setState({disabled:'disabled'});
		
		var csrfToken = getCookie('csrftoken');
		var racerRequest = {};
		racerRequest.racer = this.state.currentRacer.racer.racer_number;
		racerRequest.race = raceID;
		racerRequest.unstart = unstart;
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
				
				if(!data.message) {
					this.setState({feedback:data.error_description, disabled:null, mode:MODE_RACER_FOUND, showConfirm:true, currentMessage:null})
				} else {
				this.setState({feedback:null, currentMessage: data.message, disabled:null, mode: MODE_RACER_STARTED, showConfirm:true, dueTime:data.due_back})
				}
				
				}.bind(this));
		}.bind(this)) 
	}
	riderResponse(e) {
		console.log(e.target.value);
		this.setState({disabled:'disabled'});
		var csrfToken = getCookie('csrftoken');
		var riderResponse = {};
		riderResponse.message = this.state.currentMessage.id;
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
				this.setState({feedback:"Confirmed", disabled:null, showConfirm:false, currentMessage:data, mode:MODE_RACER_CONFIRMED})
			      }.bind(this));
		}.bind(this)) 
	}
	undo () {		
		this.setState({disabled:'disabled'});
		
		var csrfToken = getCookie('csrftoken');
		var riderResponse = {};
		riderResponse.message = this.state.currentMessage.id;
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
				console.log(data);
				this.setState({feedback:null, currentMessage: data, disabled:null, mode: MODE_RACER_STARTED, showConfirm:true, dueTime:data.due_back})
			      }.bind(this));
		}.bind(this)) 
	}
	racerLookup(racer) {		
		this.setState({disabled:'disabled', feedback:null, currentMessage: null, error_description:null});
		var url = "/dispatch/lookup/" + racer + "/"
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
						
						if (data.entry_status == ENTRY_STATUS_ENTERED) {
							console.log("status is good to race");
						 	this.setState({currentRacer: data, mode: MODE_RACER_FOUND, currentMessage: null, disabled:null, error_description: null});
						} else {
							console.log("racer is already something");
							var error = data.racer.display_name + " is already " + data.entry_status_as_string;
						 	this.setState({currentRacer: data, mode: MODE_LOOKUP_RACER, currentMessage: null, disabled:"disabled", error_description: error});
						}
					 	
					}
				}.bind(this));
			}
			
	
		}.bind(this))
	}
	reset() {
		
		this.setState({currentRacer:null, mode:MODE_LOOKUP_RACER, currentMessage:null, disabled:null, error_description:null})
		if (this.state.currentMessage) {
			var lastMessage = this.state.currentMessage;
			this.setState({lastMessage : lastMessage})
		}
		
	}
	handleLastRacer(){
		this.setState({currentRacer:null, mode:MODE_RACER_CONFIRMED, currentMessage:this.state.lastMessage, disabled:null, error_description:null})
	}
	render(){
		var currentMessage = this.state.currentMessage;
		var showConfirm = this.state.showConfirm;

		if (this.state.mode == MODE_LOOKUP_RACER) {
			return (
				<div>
					{this.state.lastMessage && <button type="button" id="wrong-racer-button" onClick={this.handleLastRacer.bind(this)} className="btn btn" value="Show Last"><i className="fas fa-caret-left"></i> Prev</button>}
					<EnterRacer racerLookup={this.racerLookup.bind(this)} error_description={this.state.error_description}/>
				</div>
			)
		} else if (this.state.mode == MODE_RACER_FOUND) {
			return (
				<div>
					{this.state.feedback && <div className="alert alert-warning" role="alert"> {this.state.feedback}</div>}
					<Racer racer={this.state.currentRacer} reset={this.reset.bind(this)} mode={this.state.mode}/>	
					<Checklist disable={this.state.disabled} racer={this.state.currentRacer} startRacer={this.startRacer.bind(this)}/>
				</div>
			)
		} else if (this.state.mode == MODE_RACER_STARTED) {
			return (
				<div>
					<div className="alert alert-warning" role="alert">Racer Started. Due back {this.state.dueTime}
						<span className="float-right"><a href="#" onClick={this.startRacer.bind(this, true)}>Un-Start Racer</a></span>
					</div>
						
						<Message message={currentMessage} runs={currentMessage.runs} />
						{showConfirm && <button onClick={this.riderResponse.bind(this)} className="btn btn-success btn-lg" disabled={this.state.disabled} value="CONFIRM"><i className="fas fa-check-circle"></i> Confirmed</button>}
				</div>
				
			)
		} else if (this.state.mode == MODE_RACER_CONFIRMED) {
			return (
				<div>
					<div className="alert alert-success" role="alert">Racer Confirmed. Due back {this.state.dueTime}
					
						<span className="float-right"><a href="#" onClick={this.undo.bind(this)}>Undo</a></span>
					</div>
					<Message message={currentMessage} />
					<button onClick={this.reset.bind(this)} className="btn btn-info btn-lg" disabled={this.state.disabled} value="NEXT RACER"><i className="fas fa-arrow-circle-right"></i> Next Racer</button>
		
				</div>
			)
		} else {
			return null;
		}
		
	}
}

ReactDOM.render(
	<StartRacerScreen />, document.getElementById('react-area')
); 