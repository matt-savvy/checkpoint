var React = require('react');
var ReactDOM = require('react-dom');
var EnterRacer = require('EnterRacer');
var Racer = require('RacerSmall');

const MODE_LOOKUP_RACER = "lookup";
const MODE_RACER_FOUND = "found";

// cut racer
// dq
// dnf

//display racer status
//display racer start time
//display racer due back time
//display open jobs first
//display current score or whatever else we're working with?
//display what manifest each job is on, if any?

class Run extends React.Component {
	render () {
		return (
				<tr>
					<td>{this.props.job.id}</td>
					
					<td>{this.props.job.pick_checkpoint}</td>
					<td>{this.props.job.drop_checkpoint}</td>
					<td>{this.props.job.utc_time_ready}</td>
					<td>{this.props.job.utc_time_complete}</td>
					<td>{this.props.job.service_level}</td>
					<td>{this.props.job.manifest}</td>
			</tr>
		)
	}
}


class RunTable extends React.Component {
	
}

class DispatchControl extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			feedback: null,
			mode : MODE_LOOKUP_RACER,
			currentRacer:null,
			showConfirm:false,
			disabled: null,
			error_description: null,
		}
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
				
			}.bind(this));
		}.bind(this)) 
	}
	racerLookup(racer) {		
		this.setState({disabled:'disabled', feedback:null, error_description:null});
		var url = "/dispatch/lookup/" + racer + "/?runs=True"
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
				this.setState({currentRacer: null, mode: MODE_LOOKUP_RACER, disabled:null, error_description: "Racer not found with this number."});
				return;
			} else {
				response.json().then(function(data) {
					console.log("promise");
					if ((response.status == 200) && (data.racer)) {
						console.log(data);
						
						this.setState({currentRacer: data.racer, runs: data.runs, mode: MODE_RACER_FOUND, currentMessage: null, disabled:null, error_description: null});
		
					 	
					}
				}.bind(this));
			}
			
	
		}.bind(this))
	}
	reset() {
		this.setState({currentRacer:null, mode:MODE_LOOKUP_RACER, currentMessage:null, disabled:null, error_description:null})
	}
	handleLastRacer(){
		this.setState({currentRacer:null, mode:MODE_RACER_CONFIRMED, currentMessage:this.state.lastMessage, disabled:null, error_description:null})
	}
	render(){
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
				</div>
			)
		} else {
			return null;
		}
		
	}
}



ReactDOM.render(
	<DispatchControl />, document.getElementById('react-area')
); 