var React = require('react');
var ReactDOM = require('react-dom');

const raceID = getCookie('raceID');

const MESSAGE_TYPE_DISPATCH = 0
const MESSAGE_TYPE_OFFICE   = 1
const MESSAGE_TYPE_NOTHING  = 2
const MESSAGE_TYPE_ERROR    = 3

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




class Message extends React.Component {
	render() {
		var racerName;
		var runs;
		
		if (this.props.message.runs){
			runs = this.props.message.runs.map(function(run) {
				return (<div key={"run " + run.id} >Pickup from <strong>{run.job.pick_checkpoint.checkpoint_name}</strong> 
					<br/> going to <strong>{run.job.drop_checkpoint.checkpoint_name}</strong>
					<hr />
					</div>)
			});
		}
		//"id": 7, 
	    //"race_entry": null, 
	    //"runs": [], 
	    //"message_type": 2, 
	    //"message_type_as_string": "Nothing to dispatch.", 
	    //"message_status_as_string": "N/A"
		
		
		if (this.props.message.race_entry){
			racerName = "#" + this.props.message.race_entry.racer.racer_number.toString() + " " + this.props.message.race_entry.racer.display_name;
		}
		
		return(
			<div><h2>{this.props.message.message_type_as_string} {racerName} </h2>
			<br /><h3>{runs}</h3>
			<br />Message ID #{this.props.message.id}
			</div>
		)
	}
}

class DispatchScreen extends React.Component {
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
			raceID:raceID,
			currentMessage:0,
			messages : [{
    "id": 13, 
    "race_entry": {
        "entry_status_as_string": "Racing", 
        "racer": {
            "racer_number": "89", 
            "first_name": "Ricky", 
            "last_name": "Roma", 
            "nick_name": "", 
            "city": "Philadelphia", 
            "gender": "M", 
            "category": 0, 
            "display_name": "Ricky Roma", 
            "category_as_string": "Working Messenger"
        }, 
        "id": 1, 
        "race": {
            "id": 1, 
            "race_name": "test race one", 
            "race_type": 2, 
            "time_limit": 200, 
            "race_start_time": "2018-09-08T17:14:02Z"
        }, 
        "entry_date": "2018-04-15T02:39:08.739Z", 
        "entry_status": 1, 
        "starting_position": null, 
        "start_time": "2018-09-07T21:57:26Z", 
        "end_time": null, 
        "final_time": 0, 
        "dq_time": null, 
        "dq_reason": "", 
        "points_earned": "6.9", 
        "supplementary_points": "0", 
        "deductions": "0", 
        "grand_total": "6.9", 
        "number_of_runs_completed": 2, 
        "scratch_pad": ""
    }, 
    "runs": [
        {
			"id" : 2,
            "job": {
                "pick_checkpoint": {
                    "id": 7, 
                    "checkpoint_number": 7, 
                    "checkpoint_name": "Trash Bags", 
                    "notes": ""
                }, 
                "drop_checkpoint": {
                    "id": 3, 
                    "checkpoint_number": 3, 
                    "checkpoint_name": "R.E.Load", 
                    "notes": ""
                }
            }, 
            "status": 4
        },
        {
			"id" : 1, 
            "job": {
                "pick_checkpoint": {
                    "id": 8, 
                    "checkpoint_number": 1, 
                    "checkpoint_name": "Abus", 
                    "notes": ""
                }, 
                "drop_checkpoint": {
                    "id": 3, 
                    "checkpoint_number": 9, 
                    "checkpoint_name": "Indy NACCC", 
                    "notes": ""
                }
            }, 
            "status": 4
        }
    ], 
    "message_type": 0, 
    "message_type_as_string": "Dispatching Jobs", 
    "message_status_as_string": "Dispatching / On screen"
},
{
	    "id": 7, 
	    "race_entry": null, 
	    "runs": [], 
	    "message_type": 2,
	    "message_type_as_string": "Nothing to dispatch.", 
	    "message_status_as_string": "N/A"
	},],
		}
	}
	showLastMessage() {
		var lastMessage = this.state.currentMessage + 1;
		this.setState({currentMessage: lastMessage});
	}
	riderResponse(e) {
		console.log(e.target.value);
	}
	getNextMessage() {
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
				messages.unshift(data);
				this.setState({messages: messages, currentMessage:0})
			      }.bind(this));
	
		}.bind(this))
	}
	render(){
		var currentMessage = this.state.messages[this.state.currentMessage]
		var message, showConfirm;
		
		if(currentMessage){
			message = <Message message={currentMessage}/>
		}
		//<i class="fas fa-spinner fa-spin"></i>
		if((currentMessage.message_type== MESSAGE_TYPE_DISPATCH) || (currentMessage.message_type== MESSAGE_TYPE_OFFICE)){
			showConfirm = true;
		}
		
		return (
		<div className="container">
			<div className="row">
				<div className="col-md-6">
						{this.state.messages[this.state.currentMessage+1] && <button onClick={this.showLastMessage.bind(this)} className="btn btn" value="Show Last"><i className="fas fa-undo-alt"></i>Show Last Message</button>}
				</div>
			</div>
			
			<div className="row">
				<div className="col-md-6 text-center">	
					{message}
				</div>
			</div>
						
			<div className="row">
				<div className="col-sm-3 text-center">
					<br />
					{showConfirm && <button onClick={this.riderResponse.bind(this)} className="btn btn-danger" value="SNOOZE"><i className="fas fa-user-slash"></i> No Response</button>}
				</div>
				<div className="col-sm-3 text-center">
					<br />
					{!showConfirm && <button onClick={this.riderResponse.bind(this)} className="btn btn-info" value="NEXT"><i className="fas fa-redo"></i> Refresh</button>}
					{showConfirm && <button onClick={this.riderResponse.bind(this)} className="btn btn-success" value="CONFIRM"><i className="fas fa-check-circle"></i> Rider Confirmed</button>}
				</div>
					
					
			</div>
		
		</div>
		)
	}
}

ReactDOM.render(
	<DispatchScreen />, document.getElementById('react-area')
); 




