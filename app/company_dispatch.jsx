var React = require('react')
var ReactDOM = require('react-dom');

class App extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
		}
	}

	render () {
		return (
			<div>hello Word</div>
		)
	}
}

ReactDOM.render(
	<App />, document.getElementById('react-area')
);
