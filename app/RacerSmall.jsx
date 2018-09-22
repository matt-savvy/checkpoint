var React = require('react');

const MODE_RACER_FOUND = "found";

class Racer extends React.Component {
	constructor(props) {
		super(props);
	}
	handleNextRacer() {
		this.props.reset();
	}
	render () {		
		return (
		<div>
			<div className="row">
				<div className="col">
					
			{this.props.mode == MODE_RACER_FOUND && <button type="button" id="wrong-racer-button" onClick={this.handleNextRacer.bind(this)} className="btn btn-danger btn-sm">RESET</button>}
		
			
					<h3 className="text-center">
						#{this.props.racer.racer.racer_number} {this.props.racer.racer.first_name} {this.props.racer.racer.nick_name} {this.props.racer.racer.last_name} 
						<br /> 
						<small>
						{this.props.racer.racer.contact_info}
						</small>	
					</h3>
				</div>
			</div>	
					
		</div>
		)
	}
}

module.exports = Racer;