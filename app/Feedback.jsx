var React = require('react');
const MESSAGE_STATUS_SNOOZED = 2;
const MESSAGE_STATUS_CONFIRMED = 3;

class Feedback extends React.Component {
	handleUndo() {
		this.props.undo();
	}
	render() {
		var alertLevel;
		if (this.props.object.status == MESSAGE_STATUS_SNOOZED) {
			alertLevel = "warning";
		} else if (this.props.object.status == MESSAGE_STATUS_CONFIRMED) {
			alertLevel = "success";
		}
		var alertClass = "alert alert-" + alertLevel+ " bottom-alert";
		return (
				<div className={alertClass} role="alert">
					{this.props.object.message_status_as_string}
					<span className="float-right"><a href="#" onClick={this.handleUndo.bind(this)}>Undo</a></span>
				</div>		
		)
	}
}

module.exports = Feedback