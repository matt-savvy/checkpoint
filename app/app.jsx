var React = require('react');
var ReactDOM = require('react-dom');

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
			messages : null,
		}
	}
	updateAssignments(assignment){		
		var sessionID = getCookie('sessionid');
		var csrfToken = getCookie('csrftoken');
		
		assignment.sessionid = sessionID;
		var assignmentJSON = JSON.stringify(assignment);
		fetch("/exercises/api/assign", {
		  headers: {
			'X-CSRFToken': csrfToken,
	      	'Accept': 'application/json',
	      	'Content-Type': 'application/json',
	      },
		  //credentials: 'include',
		  method: "POST",
		  body: assignmentJSON
		})
		.then(function(response) {
			
        	if (response.status !== 200) {
          		alert('Looks like there was a problem. Status Code: ' + response.status);
				return;
			}
			response.json().then(function(data) {
				console.log(data);
					var nextOrder = Number(data.order) + 1;
		  			this.setState({
		  				mode:TABLE_MODE,
		  				selectedExercise:null,
		  				feedback: data,
						nextOrder: nextOrder
		  			});

			      }.bind(this));
	
		}.bind(this))
		
		
		
	}
	render(){
		return (
		<div>
			<h1>Dispatch Screen!</h1>
		</div>
		)
	}
}

ReactDOM.render(
	<DispatchScreen />, document.getElementById('react-area')
); 




