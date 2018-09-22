var React = require('react');
var ReactDOM = require('react-dom');
var Message = require('Message');
var Feedback = require('Feedback');
var EnterRacer = require('EnterRacer');
var Racer = require('RacerSmall');
const raceID = getCookie('raceID');

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

class RadioForm extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			radio:'------',
		}
		
		this.handleInputChange = this.handleInputChange.bind(this);
	}
    handleInputChange(event) {
      var target = event.target;
      var value = target.type === 'checkbox' ? target.checked : target.value;
      var name = target.name;

      this.setState({
        [name]: value
      });
    }
	componentWillMount() {
		this.setState({radio : this.props.currentRadio})
	}
	handleAssign() {
		this.props.assignRadio(this.state.radio);
	}
	render() {
		var disabled;
		
		if (this.state.radio == '------'){
			disabled = "disabled";
		}
		
		var RadioMap = this.props.radioList.map(function(radio){
			return (<option key={radio} value={radio}>{radio}</option>)
		});
		
		return (
			
			<div className="form-row">
           		<div className="form-group col-auto">
                	<label htmlFor="radio">Radio</label>
        			<select name="radio" className="form-control" value={this.state.radio} onChange={this.handleInputChange}>
					<option value='------'>------</option>
						{RadioMap}
        			</select>
				</div>
				
				<button type="button" disabled={disabled} className="btn btn-lg btn-info" id="assign-radio-button" onClick={this.handleAssign.bind(this)} data-loading-text="Loading...">Assign Radio</button>
			
           	</div>
		)
	}
}

class RadioAssignScreen extends React.Component {
	radioList(){
		fetch("/dispatch/radios/api/", {
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
			} else {
				response.json().then(function(data) {
				this.setState({radioList: data.available_radios});
				}.bind(this));
			}
		
		}.bind(this))
	}
	componentWillMount() {
		this.radioList();
	}
	constructor(props) {
		super(props);
		this.state = {
			feedback: null,
			mode : MODE_LOOKUP_RACER,
			currentRacer:null,
			radioList:[],
		}
	}

	assignRadio(radio) {
		console.log("pretend we assigned this radio");
		console.log(radio);
		this.setState({disabled:'disabled'});
		var csrfToken = getCookie('csrftoken');
		var radioResponse = {};
		radioResponse.racer = this.state.currentRacer.id;
		radioResponse.radio = radio;
		var radioResponseJSON = JSON.stringify(radioResponse);
		fetch("/dispatch/radios/api/", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  //credentials: 'include',
		  method: "POST",
		  body: radioResponseJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log(data);
					this.setState({feedback:"Radio Assigned", disabled:null, mode:MODE_RACER_CONFIRMED})
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
				this.setState({currentRacer: null, mode: MODE_LOOKUP_RACER,  disabled:null, error_description: "Racer not found with this number."});
				return;
			} else {
				response.json().then(function(data) {
					if ((response.status == 200) && (data.racer)) {
						
						if (data.racer.radio_number) {
							var radioList = this.state.radioList;
							radioList.push(data.racer.radio_number);
							radioList.sort();
							this.setState({radioList:radioList});
						}
						
						this.setState({currentRacer: data, mode: MODE_RACER_FOUND, disabled:null, error_description: null});

					 	
					}
				}.bind(this));
			}
			
	
		}.bind(this))
	}
	reset() {
		this.setState({currentRacer:null, mode:MODE_LOOKUP_RACER, error_description:null});
		this.radioList();
	}
	render(){
		if (this.state.mode == MODE_LOOKUP_RACER) {
			return (
				<div>
					<EnterRacer racerLookup={this.racerLookup.bind(this)} error_description={this.state.error_description}/>
				</div>
			)
		} else if (this.state.mode == MODE_RACER_FOUND) {
			return (
				<div>
					{this.state.feedback && <div className="alert alert-warning" role="alert"> {this.state.feedback}</div>}
					<Racer racer={this.state.currentRacer} reset={this.reset.bind(this)} mode={this.state.mode}/>	
					<RadioForm radioList={this.state.radioList} currentRadio={this.state.currentRacer.racer.radio_number} assignRadio={this.assignRadio.bind(this)} />
				</div>
			)
		} else if (this.state.mode == MODE_RACER_CONFIRMED) {
			return (
				<div>
					{this.state.feedback && <div className="alert alert-warning" role="alert"> {this.state.feedback}</div>}
					<Racer racer={this.state.currentRacer} mode={this.state.mode}/>	
					<button onClick={this.reset.bind(this)} className="btn btn-info btn-lg" disabled={this.state.disabled} value="NEXT RACER"><i className="fas fa-arrow-circle-right"></i> Next Racer</button>
		
				</div>
			)
		}  else {
			return null;
		}
		
	}
}

ReactDOM.render(
	<RadioAssignScreen />, document.getElementById('react-area')
); 