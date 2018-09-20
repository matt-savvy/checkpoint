var React = require('react');
var ReactDOM = require('react-dom');
var EnterRacer = require('EnterRacer');

const MODE_PICK = "pick";
const MODE_PICKED = "confirm";
const MODE_DROP = "drop";
const MODE_DROPPED = "dropped";
const MODE_LOOKUP_RACER = "lookup";
const MODE_RACER_ENTERED = "entered";

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

class EnterCode extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			entryField:'',
		}
	}
	handleEntry(e){
		this.setState({entryField : e.target.value});
	}
	handleLookup() {
		if (this.state.entryField != ''){
			this.props.drop(this.state.entryField);
		}
		
		this.setState({entryField:''});
	}
	handleSubmit(e) {
		e.preventDefault();
		this.handleLookup();
	}
	render() {
		if (this.props.mode != MODE_DROP){
			return null;
		}
		
		return (
			<div className="row">
				<div className="col">
					<form onSubmit={this.handleSubmit.bind(this)} className="form">
            			<div className="form-group">
                			<label htmlFor="racer-number">Drop Code</label>
                			<input type="number" className="form-control" id="racer-number" placeholder="Drop Code" onChange={this.handleEntry.bind(this)} value={this.state.entryField}/>
            			</div>
					
						<button type="button" className="btn btn-lg btn-success" id="enter-drop-code" onClick={this.handleLookup.bind(this)} data-loading-text="Loading...">Drop Job</button>
					</form>				
					<p className="text-danger" id="drop-error">{this.props.error_description}</p>
				</div>
			</div>
		)
			
	}
}



class PickList extends React.Component {
	handleCancel() {
		this.props.nextRacer();
	}
	handlePick(e) {
		console.log(e.id);
		console.log("pretend we picked " + e.id);
		this.props.handlePick(e.id);
	}
	handleDropMode(){
		this.props.changeMode(MODE_DROP);
	}
	render() {
		var PickList;
		
		if (this.props.runs.length > 0) {
			PickList = this.props.runs.map((run) => 
		 	<div className="col" key={run.id}>
				<br />
				<button type="button" onClick={this.handlePick.bind(this, run)} key={run.id} value={run.id} className="btn btn-info btn-lg" >{run.job.drop_checkpoint.checkpoint_name}</button>
			</div>
			);
		} else {
			return (
				<div className="text-center">
					<div className="alert alert-danger">
						<h4>There is nothing for this racer to pick up at this checkpoint. Did you mean to drop off?</h4>
					</div>
					<div className="row">
						<div className="col">
							<button className="btn btn-primary btn-lg" type="button" onClick={this.handleDropMode.bind(this)}>Drop Off</button>
				        </div>
						<div className="col">
							<button className="btn btn-secondary btn-lg" type="button" onClick={this.handleCancel.bind(this)}>Next Racer</button>
						</div>
					</div>
				
				</div>
			)
		}
		
		return (
			<div>
				<legend>Available Pickups</legend>
				<div className="row">
					{PickList}
				</div>
			</div>
		)
	}
}

class ConfirmCode extends React.Component {
	constructor(props) {
		super(props);
	}
	render () {
		return (
			<div className="alert alert-success">
				<p>Job is marked as picked up.</p>
				<h3>Drop Code : {this.props.confirmCode}</h3>
			</div>
		)
	}
}

class NextActionDialog extends React.Component {
	constructor(props) {
		super(props);
	}
	handleAnotherTransaction(x){
		this.props.anotherTransaction(x);
	}
	handleNextRacer(){
		this.props.nextRacer();
	}
	render () {
		return (
			<div className="row">
				<div className="col">
					<button className="btn btn-primary"  onClick={this.handleAnotherTransaction.bind(this, MODE_PICK)}>Pick Up</button>
				</div>
			
				<div className="col">
					<button className="btn btn-secondary" onClick={this.handleAnotherTransaction.bind(this, MODE_DROP)}>Drop Off</button>
				</div>
				
				<div className="col">
					<button className="btn btn-info" onClick={this.handleNextRacer.bind(this)}>Next Racer</button>
				</div>
			</div>
		)
	}
}

class CancelButton extends React.Component {
	constructor(props) {
		super(props);
	}
	handleNextRacer(){
		this.props.nextRacer();
	}
	render () {
		console.log("MODE CHECK");
		console.log(this.props.mode);
		if ((this.props.mode == MODE_PICKED) || (this.props.mode == MODE_DROPPED)) {
			return null;
		}
		
		return (
			<button type="button" id="wrong-racer-button" onClick={this.handleNextRacer.bind(this)} className="btn btn-danger btn-sm">CANCEL</button>
		)
	}
}

class Checkpoint extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			racer:null,
			availableRuns:[],
			error:null,
			error_description:null,
			mode:MODE_LOOKUP_RACER,
		}
	}
	nextRacer() {
		this.setState({racer: null, availableRuns:[], error:null, error_description:null, mode:MODE_LOOKUP_RACER})
	}
	changeMode(mode) {
		this.setState({mode:mode});
	}
	anotherTransaction(x) {
		this.setState({mode:x});
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
					this.setState({error_description : data.error_description, mode:MODE_LOOKUP_RACER});
				} else {
					this.setState({racer:data.racer, availableRuns:data.runs, mode:MODE_RACER_ENTERED, error_description : null});
				}
		    }.bind(this));
	
		}.bind(this))
		
	}
	pick(run){
		console.log("begin the pick request");
		var csrfToken = getCookie('csrftoken');
		var pickRequest = {}
		pickRequest.racer_number = this.state.racer.racer_number
		pickRequest.run = run;
		pickRequest.checkpoint = Number(checkpoint);
		var pickRequestJSON = JSON.stringify(pickRequest);
		
		//remove the run we're picking from the list anyway
		var availableRuns;
		if (this.state.availableRuns.length > 1) {
			availableRuns = this.state.availableRuns.splice(this.state.availableRuns.indexOf(run), 1);
		} else {
			availableRuns = [];
		}

		console.log(pickRequestJSON);
		fetch("/api/v1/pick/", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  //credentials: 'include',
		  method: "POST",
		  body: pickRequestJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log(data)
							
				if (data.error){
					this.setState({error_description : data.error_description, mode:MODE_LOOKUP_RACER});
				} else {
					this.setState({confirmCode:data.confirm_code, mode:MODE_PICKED, availableRuns:availableRuns, error_description : null});
				}
		    }.bind(this).bind(availableRuns));
	
		}.bind(this).bind(availableRuns));
	}
	drop(code){
		console.log("begin the drop request");
		var csrfToken = getCookie('csrftoken');
		var dropRequest = {}
		dropRequest.racer_number = this.state.racer.racer_number
		dropRequest.confirm_code = code;
		dropRequest.checkpoint = Number(checkpoint);
		var dropRequestJSON = JSON.stringify(dropRequest);
		
		fetch("/api/v1/drop/", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  //credentials: 'include',
		  method: "POST",
		  body: dropRequestJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log(data)
							
				if (data.error){
					this.setState({error_description : data.error_description, mode:MODE_DROP});
				} else {
					this.setState({error_description : null, mode:MODE_DROPPED});
				}
		    }.bind(this));
	
		}.bind(this));
	}
	
	render(){				
		if (this.state.mode == MODE_LOOKUP_RACER) {
			return (
				<EnterRacer mode={this.state.mode} racerLookup={this.racerLookup.bind(this)} error_description={this.state.error_description} />
			)
		} else {
			return (
				<Racer mode={this.state.mode} racer={this.state.racer} nextRacer={this.nextRacer.bind(this)} changeMode={this.changeMode.bind(this)} runs={this.state.availableRuns} error_description={this.state.error_description} pick={this.pick.bind(this)} confirmCode={this.state.confirmCode} anotherTransaction={this.anotherTransaction.bind(this)} drop={this.drop.bind(this)}/>
			)
		}
	}
}

ReactDOM.render(
	<Checkpoint />, document.getElementById('react-area')
); 