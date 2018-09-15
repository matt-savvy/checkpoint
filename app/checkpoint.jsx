var React = require('react');
var ReactDOM = require('react-dom');


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
		console.log(e.id);
		console.log("pretend we picked " + e.id);
		this.props.handlePick(e.id);
	}
	render() {
		var PickList;
		
		if (this.props.runs) {
			PickList = this.props.runs.map((run) => 
		 		<p key={run.id} ><button type="button" onClick={this.handlePick.bind(this, run)} key={run.id} value={run.id} className="btn btn-info btn-lg" >{run.job.drop_checkpoint.checkpoint_name}</button></p>
			);
		} else {
			PickList = <div className="alert alert-danger"><h4>There is nothing for this racer to pick up at this checkpoint. Did you mean to drop off? </h4></div>
		}
		
		return (
			<div className="row container">
				<legend>Available Pickups</legend>
				{PickList}
			</div>
		)
	}
}

class Racer extends React.Component {
	constructor(props) {
		super(props);
	}
	handleWrongRacer() {
		this.props.wrongRacer();
	}
	handleMode(x) {
		console.log("mode");
		console.log(x.target.value);
		this.props.changeMode(x.target.value);
	}
	handlePick(run) {
		console.log("handle pick in racer component");
		console.log(run);
		this.props.pick(run);
	}
	render () {		
		return (
			<div className="row state-section" id="pick-or-drop-section" style={{display:'flex'}}>
			<h3 className="text-center" id="racer-name">#{this.props.racer.racer_number} {this.props.racer.first_name} {this.props.racer.nick_name} {this.props.racer.last_name}</h3>
			
			<button type="button" id="wrong-racer-button" onClick={this.handleWrongRacer.bind(this)} className="btn btn-danger btn-sm">CANCEL</button>
			
			{(this.props.mode == MODE_RACER_ENTERED) && <p><button onClick={this.handleMode.bind(this)} value={MODE_PICK} type="button" id="pick-button" className="btn btn-success btn-lg" >Pick Up</button>
            <button onClick={this.handleMode.bind(this)} type="button" value={MODE_DROP} className="btn btn-success btn-lg" >Drop Off</button></p>}
			
			{(this.props.mode == MODE_PICK) && <PickList handlePick={this.handlePick.bind(this)} runs={this.props.runs} />}
			
            <hr />
			
			
			
			
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
			racer:null,
			availableRuns:null,
			error:null,
			error_description:null,
			mode:MODE_LOOKUP_RACER,
		}
	}
	wrongRacer() {
		this.setState({racer: null, availableRuns:null, error:null, error_description:null, mode:MODE_LOOKUP_RACER})
	}
	changeMode(mode) {
		this.setState({mode:mode});
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
					this.setState({racer:data.racer, availableRuns:data.runs, mode:MODE_RACER_ENTERED});
				}
		    }.bind(this));
	
		}.bind(this))
		
	}
	pick(run){
		var csrfToken = getCookie('csrftoken');
		var pickRequest = {}
		pickRequest.racer = this.state.racer.id
		pickRequest.run = run;
		pickRequest.checkpoint = checkpoint;
		var pickRequestJSON = JSON.stringify(pickRequest);
		
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
				if (data.error){
					this.setState({error_description : data.error_description, mode:MODE_LOOKUP_RACER});
				} else {
					this.setState({racer:data.racer, confirmCode:data.confirm, availableRuns:data.runs, mode:MODE_RACER_PICKED});
				}
		    }.bind(this));
	
		}.bind(this))
		
	}
	render(){
		//<PickList pickJob={this.pickJob.bind(this)} runs={this.props.runs} />
				
		if (this.state.mode == MODE_LOOKUP_RACER) {
			return (
				<EnterRacer mode={this.state.mode} racerLookup={this.racerLookup.bind(this)} error_description={this.state.error_description} />
			)
		} else {
			console.log("sanity");
			return (
				<Racer mode={this.state.mode} racer={this.state.racer} wrongRacer={this.wrongRacer.bind(this)} changeMode={this.changeMode.bind(this)} runs={this.state.availableRuns} error_description={this.state.error_description} />
			)
		}
	}
}

ReactDOM.render(
	<Checkpoint />, document.getElementById('react-area')
); 