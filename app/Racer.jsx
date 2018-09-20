var React = require('react');

class Racer extends React.Component {
	constructor(props) {
		super(props);
	}
	handleNextRacer() {
		this.props.nextRacer();
	}
	handleMode(x) {
		console.log("mode");
		console.log(x)
		this.props.changeMode(x)
		//console.log(e.target.value);
		//this.props.changeMode(e.target.value);
	}
	handlePick(run) {
		console.log("handle pick in racer component");
		console.log(run);
		this.props.pick(run);
	}
	render () {		
		return (
		<div>
			<div className="row">
				<div className="col">
					<CancelButton mode={this.props.mode} nextRacer={this.props.nextRacer.bind(this)} />
			
					<h3 className="text-center">
						#{this.props.racer.racer_number} {this.props.racer.first_name} {this.props.racer.nick_name} {this.props.racer.last_name} 
						<br /> 
						<small>
						{this.props.racer.contact_info}
						</small>	
					</h3>
				</div>
			</div>
						
					{(this.props.mode == MODE_RACER_ENTERED) && 
					<div className="row text-center">
						<div className="col">
							<button onClick={this.handleMode.bind(this, MODE_PICK)} value={MODE_PICK} type="button" id="pick-button" className="btn btn-success btn-lg" >Pick Up</button>
            			</div>
						<div className="col">
							<button onClick={this.handleMode.bind(this, MODE_DROP)} type="button" value={MODE_DROP} className="btn btn-success btn-lg" >Drop Off</button>
						</div>	
					</div>
					}
				
					{(this.props.mode == MODE_PICK) && <PickList nextRacer={this.props.nextRacer.bind(this)} changeMode={this.handleMode.bind(this)} handlePick={this.handlePick.bind(this)} runs={this.props.runs} />}
					{(this.props.mode == MODE_PICKED) && <ConfirmCode confirmCode={this.props.confirmCode} />}
					{(this.props.mode == MODE_DROPPED) && <div className="alert alert-success">Job successfully delivered.</div>}
					{(this.props.mode == MODE_PICKED || this.props.mode == MODE_DROPPED) && <NextActionDialog anotherTransaction={this.props.anotherTransaction.bind(this)} nextRacer={this.handleNextRacer.bind(this)}/>}
			
					<EnterCode mode={this.props.mode} drop={this.props.drop.bind(this)} error_description={this.props.error_description}/>
   			
			</div>
		)
	}
}

module.exports = Racer