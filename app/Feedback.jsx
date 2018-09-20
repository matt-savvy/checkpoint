var React = require('react');

class Feedback extends React.Component {
	handleUndo() {
		this.props.undo();
	}
	render() {
		var alertClass = "alert alert-success bottom-alert";
		return (
				<div className={alertClass} role="alert">
					{this.props.object.message_status_as_string}
					<span className="float-right"><a href="#" onClick={this.handleUndo.bind(this)}>Undo</a></span>
				</div>		
		)
	}
}

module.exports = Feedback