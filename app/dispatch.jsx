var React = require('react');
var ReactDOM = require('react-dom');
var Message = require('Message');
var Feedback = require('Feedback');
const raceID = getCookie('raceID');

const MESSAGE_TYPE_DISPATCH = 0
const MESSAGE_TYPE_OFFICE   = 1
const MESSAGE_TYPE_NOTHING  = 2
const MESSAGE_TYPE_ERROR    = 3

const MESSAGE_STATUS_NONE        = 0
const MESSAGE_STATUS_DISPATCHING = 1
const MESSAGE_STATUS_SNOOZED     = 2
const MESSAGE_STATUS_CONFIRMED   = 3

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

class DispatchScreen extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			raceID:raceID,
			feedback: null,
			disabled: null,
			showRefresh: true,
			currentMessage:0,
			messages : [],
		}
	}
	showBackMessage() {
		var lastMessage = this.state.currentMessage + 1;
		this.setState({currentMessage: lastMessage, feedback: null});
	}
	showNextMessage() {
		var lastMessage = this.state.currentMessage - 1;
		this.setState({currentMessage: lastMessage, feedback: null});
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
  		  credentials: 'include',
  		  method: "POST",
		  body: riderResponseJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log("rider response");
				console.log(data);
				var messages = this.state.messages
				messages
				messages[this.state.currentMessage] = data;
				this.setState({feedback:data, disabled:null, showRefresh:true, messages:messages})
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
		  credentials: 'include',
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
				messages[this.state.currentMessage] = data;
				this.setState({feedback:null, disabled:null, showRefresh:null, messages:messages})
			      }.bind(this));
		}.bind(this)) 
	}
	getNextMessage() {		
		this.setState({disabled:'disabled', feedback:null, currentMessage: 0, error_description:null});
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
		  credentials: 'include',
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
				
				if (data.message.message_type == MESSAGE_TYPE_NOTHING) {
					console.log("timeout init");
					setTimeout(function() { this.getNextMessage() }.bind(this), 45000);
				}
				
				messages.unshift(data.message);
				this.setState({messages: messages, disabled:null, error_description: data.error_description});
				
				
			      }.bind(this));
	
		}.bind(this))
	}
	render(){
		var currentMessage = this.state.messages[this.state.currentMessage];
		var message, messageNumber, messageStatus, showConfirm, showRefresh;
		var showBack = "disabled";
		var showForward = "disabled";
		
		if (this.state.showRefresh) {
			showRefresh = true;
		}
		
		if (currentMessage) {
			messageNumber = currentMessage.id;
			
			if ((currentMessage.status == MESSAGE_STATUS_DISPATCHING) || (currentMessage.status == MESSAGE_STATUS_SNOOZED) || (currentMessage.status == MESSAGE_STATUS_CONFIRMED)){
				messageStatus = currentMessage.message_status_as_string;
			}
			
			if ((currentMessage.message_type == MESSAGE_TYPE_DISPATCH) || (currentMessage.message_type== MESSAGE_TYPE_OFFICE)){
				
				if (currentMessage.status == MESSAGE_STATUS_DISPATCHING) {
					showConfirm = true;
					showRefresh = false;
				}
					
			} else if (currentMessage.message_type == MESSAGE_TYPE_NOTHING ){
				showRefresh = true;
				}
			message = <Message message={currentMessage} error_description={this.state.error_description}/>
		} else {
			showRefresh = true;
		}
		
		
		
		if (this.state.messages[this.state.currentMessage+1]) {
			showBack = null;
		}
		if (this.state.messages[this.state.currentMessage-1]) {
			showForward = null;
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
			<div className="navbar footer">
				<div className="float-left">
					{showConfirm && <button onClick={this.riderResponse.bind(this)} className="btn btn-danger btn-sm" disabled={this.state.disabled}  value="SNOOZE"><i className="fas fa-user-slash"></i> No Response</button>}
				</div>
				
				<div className="float-right">
					{showConfirm && <button onClick={this.riderResponse.bind(this)} className="btn btn-success btn-sm" disabled={this.state.disabled} value="CONFIRM"><i className="fas fa-check-circle"></i> Confirmed</button>}
				</div>
			</div>

		
		</div>
		)
	}
}

ReactDOM.render(
	<DispatchScreen />, document.getElementById('react-area')
); 