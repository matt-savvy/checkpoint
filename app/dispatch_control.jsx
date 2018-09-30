var React = require('react');
var ReactDOM = require('react-dom');
var EnterRacer = require('EnterRacer');
var Racer = require('RacerSmall');
const raceID = getCookie('raceID');

const MODE_LOOKUP_RACER = "lookup";
const MODE_RACER_FOUND = "found";


const RUN_STATUS_PICKED      = 0;
const RUN_STATUS_COMPLETED   = 1;
const RUN_STATUS_ASSIGNED    = 2;
const RUN_STATUS_PENDING     = 3;
const RUN_STATUS_DISPATCHING = 4;

// cut racer
// dq
// dnf
//#TODO
//display racer start time
//display racer due back time
//display open jobs first
//display current score or whatever else we're working with?
//display what manifest each job is on, if any?
//display final time if racer is finished

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

class Run extends React.Component {
	render () {
		var tableClass;
		if (this.props.run.late) {
			tableClass = "table expired"
		}
		
		return (
				<tr className={tableClass}>
					<td>{this.props.run.id}</td>
					<td>{this.props.run.job.pick_checkpoint.checkpoint_name}</td>
					<td>{this.props.run.job.drop_checkpoint.checkpoint_name}</td>
					<td>{this.props.run.status_as_string}</td>
					<td>{this.props.run.localized_ready_time}</td>
					<td>{this.props.run.localized_due_time}</td>
					<td>{this.props.run.job.service}</td>
					<td>{this.props.run.job.manifest && this.props.run.job.manifest.manifest_name}</td>
				</tr>
		)
	}
}


class RunTable extends React.Component {
	render () {
		var RunList = this.props.runs.map(function (run) {
			return (<Run key={run.id} run={run} />)
		});
		
		return (
			<div>
				<h2>{this.props.label} <small> <span className="badge badge-pill badge-primary">{this.props.runs.length}</span> </small></h2>
				<table className="table">
					<tbody>
						<tr>
							<th scope="col">Run #</th>
							<th scope="col">Pick</th>
							<th scope="col">Drop</th>
							<th scope="col">Status</th>
							<th scope="col">Ready Time</th>
							<th scope="col">Due Time</th>
							<th scope="col">Service</th>
							<th scope="col">Manifest</th>
						</tr>
						{RunList}
					</tbody>
				</table>
			</div>
		)
	}
}

class DispatchControl extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			feedback: null,
			mode : MODE_LOOKUP_RACER,
			currentRacer:null,
			finalTime: null,
			runs : null,
			showConfirm:false,
			disabled: null,
			error_description: null,
		}
	}
	racerLookup(racer) {		
		this.setState({disabled:'disabled', feedback:null, error_description:null});
		var url = "/dispatch/lookup/" + racer + "/?runs=True"
		fetch(url, {
		  headers: {
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  credentials : 'include',
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
	finishRacer() {
		console.log("finishing racer");
		this.setState({disabled:'disabled'});
		
		var csrfToken = getCookie('csrftoken');
		var finishRequest = {};
		finishRequest.racer = this.state.currentRacer.racer.racer_number;
		finishRequest.race = raceID;
		var finishRequestJSON = JSON.stringify(finishRequest);
		fetch("/ajax/finishracer/", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  credentials: 'include',
		  method: "POST",
		  body: finishRequestJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log(data);
				
				if(!data.final_time) {
					this.setState({feedback:data.error_description, disabled:null, mode:MODE_RACER_FOUND, showConfirm:true, currentMessage:null})
				} else {
					var currentRacer = this.state.currentRacer;
					currentRacer.entry_status_as_string = "Finished!";
					currentRacer.entry_status = 2;
				this.setState({feedback:null, currentRacer: currentRacer, disabled:null, showConfirm:false, finalTime:data.final_time})
				}
				
				}.bind(this));
		}.bind(this)) 
	}
	reset() {
		this.setState({currentRacer:null, mode:MODE_LOOKUP_RACER, currentMessage:null, disabled:null, error_description:null})
	}
	refresh() {
		this.racerLookup(this.state.currentRacer.racer.racer_number);
	}
	handleLastRacer(){
		this.setState({currentRacer:null, mode:MODE_RACER_CONFIRMED, currentMessage:this.state.lastMessage, disabled:null, error_description:null})
	}
	render(){
		var still_racing;
		
		if (this.state.mode == MODE_LOOKUP_RACER) {
			return (
				<div>
					{this.state.lastMessage && <button type="button" id="wrong-racer-button" onClick={this.handleLastRacer.bind(this)} className="btn btn" value="Show Last"><i className="fas fa-caret-left"></i> Prev</button>}
					
					<EnterRacer racerLookup={this.racerLookup.bind(this)} error_description={this.state.error_description}/>
				</div>
			)
		} else if (this.state.mode == MODE_RACER_FOUND) {
			if ((this.state.currentRacer.entry_status == 1) || (this.state.currentRacer.entry_status == 5) | (this.state.currentRacer.entry_status == 6)){
				still_racing = true;
			}
			
			var openRuns = this.state.runs.filter(run => ((run.status == RUN_STATUS_ASSIGNED) || (run.status == RUN_STATUS_PICKED)|| (run.status == RUN_STATUS_DISPATCHING)));
			var pendingRuns = this.state.runs.filter(run => (run.status == RUN_STATUS_PENDING));
			var completeRuns = this.state.runs.filter(run => (run.status == RUN_STATUS_COMPLETED));
			
			return (
				<div>
					{this.state.feedback && <div className="alert alert-warning" role="alert"> {this.state.feedback}</div>}
					{this.state.currentRacer && <p className="text-center"><button onClick={this.refresh.bind(this)} className="btn btn-primary"><i className="fa fa-refresh" aria-hidden="true"></i> Refresh</button></p>}
					{still_racing && <p className="text-center"><button onClick={this.finishRacer.bind(this)} className="btn btn-warning">Finish Racer</button></p>}
					
					<Racer racer={this.state.currentRacer} reset={this.reset.bind(this)} mode={this.state.mode}/>
					<h3 className="text-center">{this.state.currentRacer.entry_status_as_string} {this.state.currentRacer.localized_start_time && <small>Racing since {this.state.currentRacer.localized_start_time}</small>}</h3>
					<h4 className="text-center">Current Earnings : ${this.state.currentRacer.current_score} </h4>
					<RunTable runs={openRuns} label="OPEN"/>
					<RunTable runs={pendingRuns} label="PENDING"/>
					<RunTable runs={completeRuns} label="COMPLETE"/>
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