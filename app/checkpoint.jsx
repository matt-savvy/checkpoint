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
	handleLookup() {
		if (this.state.entryField != ''){
			this.props.racerLookup(this.state.entryField);
		}
		
		this.setState({entryField:''});
	}
	handleSubmit(e) {
		e.preventDefault();
		this.handleLookup();
	
	}
	componentDidUpdate(){
		if (this.state.entryField.length >= 3) {
			this.handleLookup();
		}
	}
	render() {
		
		return (
			<div className="row state-section" id="racer-number-section" style={{display:'flex'}}>
            		<div className="form-group">
                		<label htmlFor="racer-number">Racer Number</label>
                		<input type="number" className="form-control" id="racer-number" placeholder="Racer #" onChange={this.handleEntry.bind(this)} value={this.state.entryField}/>
            		</div>
				
            	<button type="button" className="btn btn-success" id="lookup-racer-button" onClick={this.handleLookup.bind(this)} data-loading-text="Loading...">Lookup Racer</button>
				<p className="text-danger" id="racer-error">{this.props.error_description}</p>
			</div>
		)
			
	}
}

var DATA = {
    "racer": {
        "id": 1, 
        "racer_number": "89", 
        "first_name": "Ricky", 
        "last_name": "Roma", 
        "nick_name": "", 
        "email": "matt@1-800-rad-dude.com", 
        "city": "Philadelphia", 
        "gender": "M", 
        "category": 0, 
        "shirt_size": "S", 
        "paid": false, 
        "paypal_tx": "", 
        "team": "track flag", 
        "company": "timecycle"
    }, 
    "error_description": null, 
    "runs": [
        {
            "id": 1, 
            "job": {
                "pick_checkpoint": {
                    "id": 1, 
                    "checkpoint_number": 1, 
                    "checkpoint_name": "Abus", 
                    "notes": ""
                }, 
                "drop_checkpoint": {
                    "id": 9, 
                    "checkpoint_number": 9, 
                    "checkpoint_name": "Indy NACCC", 
                    "notes": ""
                }
            }
        }
    ], 
    "error_title": null, 
    "error": false
}

class PickList extends React.Component {
	handleCancel() {
		//this.props.wrongRacer();
		console.log("pretend we cancelled");
	}
	handlePick(e) {
		console.log("pretend we picked " + e.target.value);
	}
	render() {
		var PickList = this.props.runs.map(function(run){
			return <p><button type="button" onClick={this.handlePick.bind(this)} key={run.id} value={run.id} className="btn btn-success btn-lg" >to {run.pick_checkpoint.checkpoint_name}</button></p>
		});
		
		return (
			<div>
				PickList;
			</div>
		)
	}
}

class Racer extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			mode : null
		}
	}
	handleWrongRacer() {
		this.props.wrongRacer();
	}
	render () {
		
		return (
			<div className="row state-section" id="pick-or-drop-section" style={{display:'flex'}}>
			<h3 className="text-center" id="racer-name">#{this.props.racer.racer_number} {this.props.racer.first_name} {this.props.racer.nick_name} {this.props.racer.last_name}</h3>
            
			<PickList runs={this.props.runs} />
			
			<p><button type="button" id="pick-button" className="btn btn-success btn-lg" >Pick Up</button>
            <button type="button" id="drop-button" className="btn btn-success btn-lg" >Drop Off</button></p>
            <hr />
            <p className="text-center"><button type="button" id="wrong-racer-button" onClick={this.handleWrongRacer.bind(this)} className="btn btn-danger btn-sm">Wrong Racer</button></p>
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
			racer:DATA.racer,
			available_runs:DATA.runs,
			error:null,
			error_description:null,
		}
	}
	wrongRacer() {
		this.setState({racer: null, availableRuns:null, error:null, error_description:null,})
	}
	racerLookup(racer){
		
		if (String(racer).charAt(0) == '0') {
			racer = racer.slice(1,3)
		}
		
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
				if (data.error){
					this.setState({error_description : data.error_description})
				} else {
					this.setState({racer:data.racer, availableRuns:data.runs})
				}
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
		if (this.state.racer) {
			
			return (
				<Racer racer={this.state.racer} wrongRacer={this.wrongRacer.bind(this)} runs={this.state.available_runs} error_description={this.state.error_description} />
			)
		}
		return (
			<EnterRacer racerLookup={this.racerLookup.bind(this)} error_description={this.state.error_description} />
		)
	}
}

ReactDOM.render(
	<Checkpoint />, document.getElementById('react-area')
); 