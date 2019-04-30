var React = require('react')
var ReactDOM = require('react-dom');
import loki from 'lokijs';
import axios from 'axios';
var moment = require('moment');
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
axios.defaults.xsrfCookieName = 'csrftoken'
import {Card, Col, ListGroup, Row} from 'react-bootstrap';


class Run extends React.Component {
	render () {
		var deadlineFromNow = moment(this.props.run.utc_time_due).fromNow();
		return (
			<ListGroup.Item className="job-info-tile">
    			<Row>
      				<Col><i>From:</i><br/>
				          <strong>{this.props.run.job.pick_checkpoint.checkpoint_name}</strong><br />
				          {this.props.run.job.pick_checkpoint.line1}
						  <br />
						  {this.props.run.job.pick_checkpoint.line2}
				          <br />

			        <p>
					  {this.props.run.job.service}
					  <br />

			          <br />
					  Due {deadlineFromNow}
			        </p>
	      		  </Col>
			      <Col>
				  	<i>To:</i><br/>
			          <strong>{this.props.run.job.drop_checkpoint.checkpoint_name}</strong> <br/>
					  {this.props.run.job.drop_checkpoint.line1}
					  <br />
					  {this.props.run.job.drop_checkpoint.line2}

			        <p className="job-summary">
			            <span className="text-success">${this.props.run.job.points}</span> <br />
			        </p>
			      </Col>
		    	</Row>
			</ListGroup.Item>
		)
	}
}

function RunList(props) {
	return (
		<Card>
			<Card.Header>
				{props.category}
			</Card.Header>
	        <ListGroup>
				{props.children}
			</ListGroup>
	   </Card>
   )
}

class App extends React.Component {
	constructor(props) {
		super(props);

		var db = new loki('checkpoint.db');
		var runs = db.addCollection('runs');

		this.state = {
			runs: init['runs'],
		}
	}

	render () {
		return (
			<>
				<RunList category="Unassigned">
					{this.state.runs.map(run => <Run run={run} key={run.id} /> )}
			    </RunList>
			</>
		)
	}
}

ReactDOM.render(
	<App />, document.getElementById('react-area')
);
