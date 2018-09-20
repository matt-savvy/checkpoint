var React = require('react');

const MESSAGE_TYPE_DISPATCH = 0
const MESSAGE_TYPE_OFFICE   = 1
const MESSAGE_TYPE_NOTHING  = 2
const MESSAGE_TYPE_ERROR    = 3

const MESSAGE_STATUS_NONE        = 0
const MESSAGE_STATUS_DISPATCHING = 1
const MESSAGE_STATUS_SNOOZED     = 2
const MESSAGE_STATUS_CONFIRMED   = 3

class Message extends React.Component {
	render() {
		var racerName;
		var runs;
		
		if (this.props.message.runs){
			runs = this.props.message.runs.map(function(run) {
				var service, alertClass;
				if ((run.job.service == "RUSH") || (run.job.service == "DOUBLE RUSH")){
					console.log(run.job.service)
					service = run.job.service;
					alertClass = "alert-danger"
				}
				
				return (<div key={"run " + run.id} className={alertClass} >Pickup from <strong>{run.job.pick_checkpoint.checkpoint_name}</strong> 
					<br/> going to <strong>{run.job.drop_checkpoint.checkpoint_name}</strong>
					{service && <p>{service}, due in {run.job.minutes_due_after_start} minutes!</p>}
					<hr />
					</div>)
			});
		}
		
		if (this.props.message.race_entry){
			racerName = "#" + this.props.message.race_entry.racer.racer_number.toString() + " " + this.props.message.race_entry.racer.display_name;
		}
		
		if (this.props.message.message_type == MESSAGE_TYPE_DISPATCH) {
			return (
				<div><h2>{this.props.message.message_type_as_string} {racerName} </h2>
				<h4>{this.props.message.race_entry.racer.contact_info}</h4>
				<hr width="50%" />
				<h4 className="text-center">{runs.length} Jobs</h4>
				<br /><h3>{runs}</h3>
				</div>
			) 
		} else if (this.props.message.message_type == MESSAGE_TYPE_OFFICE) {
			return (
				<div><h2>{racerName} </h2>
				<hr width="50%" />
				<br /><h3>Come to the Office</h3>
				</div>
			)
		} else if (this.props.message.message_type == MESSAGE_TYPE_NOTHING) {
			return (
				<div><h2>Nothing to Dispatch</h2>
				<hr width="50%" />
				<br /><h3>Refresh soon.</h3>
				</div>
			)
		} else if (this.props.message.message_type == MESSAGE_TYPE_ERROR) {
			return (
				<div><h2>Error</h2>
				<hr width="50%" />
				<br /><h3>{this.props.error_description}</h3>
				</div>
			)
		}
		
		return null;
	}
}

module.exports = Message;