var React = require('react');

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
			<div className="row">
				<div className="col">
					<form onSubmit={this.handleSubmit.bind(this)} className="form">
					<div className="form-group">
                		<label htmlFor="racer-number">Racer Number</label>
                		<input type="number" className="form-control" id="racer-number" placeholder="Racer #" onChange={this.handleEntry.bind(this)} value={this.state.entryField}/>
            		</div>

						<button type="button" className="btn btn-lg btn-success" id="lookup-racer-button" onClick={this.handleLookup.bind(this)} data-loading-text="Loading...">Lookup Racer</button>
			
					</form>
         		<p className="text-danger" id="racer-error">{this.props.error_description}</p>
				</div>
			</div>
		)
			
	}
}

module.exports = EnterRacer