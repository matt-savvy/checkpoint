var React = require('react')
var ReactDOM = require('react-dom');
import loki from 'lokijs';
import axios from 'axios';
var moment = require('moment');
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
axios.defaults.xsrfCookieName = 'csrftoken'
import {Badge, Button, Card, CardDeck, Col, Form, ListGroup, Nav, NavDropdown, Modal, Row} from 'react-bootstrap';

const DISPLAY_UNASSIGNED = "unassigned";
const DISPLAY_NEW = "new";

const SORT_READY_TIME = "utc_time_due";
const SORT_DEADLINE = "utc_time_ready";
const SORT_CHECKPOINT = "job.pick_checkpoint.checkpoint_name";

class AssignDialog extends React.Component{
    constructor(props) {
        super(props);
        var defaultRaceEntry = 0;
        if (props.run.race_entry) {
            defaultRaceEntry = props.run.race_entry.id;
        }
        this.state = {
            value : defaultRaceEntry,
        }
    }
    handleChange = (e) => {
		this.setState({value: e.target.value});
	}
	handleSubmit = (e) => {
		e.preventDefault();
        if (!this.state.value) {
            return;
        }

        if (this.props.run.race_entry && (this.props.run.race_entry.id == this.state.value)){
            console.log("catch");
            this.props.handleClose();
            return;
        }

        this.props.assign(this.props.run, this.state.value);
        this.props.handleClose();

	}
    render () {
        return (
            <Modal show={true} onHide={this.props.handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Assign</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <label>Who would you like to assign this to?</label>
                    <Form>
                         <Form.Label>Racer</Form.Label>
                         <Form.Group controlId="assignForm.ControlSelect1">
                             <Form.Control value={this.state.value} onChange={this.handleChange} as="select">
                                <option key="no-choice" value={0} >------------</option>
                                {this.props.raceEntries.map(raceEntry => <option value={raceEntry.id} key={raceEntry.id}>{raceEntry.racer.racer_number} : {raceEntry.racer.display_name}</option>)}
                            </Form.Control>
                         </Form.Group>
                    </Form>
                </Modal.Body>

                <Modal.Footer>
                    <Button onClick={this.props.handleClose} variant="secondary">Cancel</Button>
                    <Button disabled={this.state.value == 0} onClick={this.handleSubmit} variant="primary">Assign</Button>
                </Modal.Footer>
            </Modal>
        )
    }

}

function NavBar(props){
   return (
      <Nav variant="pills" activeKey={props.viewMode} onSelect={k => props.update(k)}>
        <Nav.Item>
          <Nav.Link eventKey={DISPLAY_UNASSIGNED} href="#">
            Unassigned
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey={DISPLAY_NEW} title="Item">
            New Jobs
          </Nav.Link>
        </Nav.Item>
		<NavDropdown title="Sort" id="nav-dropdown">
		  <NavDropdown.Item active={props.sortMode ==SORT_READY_TIME} eventKey={SORT_READY_TIME}>Ready Time</NavDropdown.Item>
		  <NavDropdown.Item active={props.sortMode == SORT_DEADLINE} eventKey={SORT_DEADLINE}>Deadline</NavDropdown.Item>
		  <NavDropdown.Item active={props.sortMode == SORT_CHECKPOINT} eventKey={SORT_CHECKPOINT}>Checkpoint</NavDropdown.Item>
		</NavDropdown>
        <Button onClick={props.refresh} variant="secondary">Refresh</Button>
	</Nav>
    )
}

class Run extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            showModal : false,
        }
    }
    startAssign = () => {
        this.setState({showModal : true});
    }
    handleClose = () => {
        this.setState({showModal : false});
    }
	render () {
		var deadlineFromNow = moment(this.props.run.utc_time_due).fromNow();
		var readyFromNow = moment(this.props.run.utc_time_ready).fromNow();
		return (
            <>
			<ListGroup.Item onClick={this.startAssign} className="job-info-tile">
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
					  Ready {readyFromNow}
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
                      <br />
                      {this.props.run.id}
			        <p className="job-summary">
			            <span className="text-success">${this.props.run.job.points}</span> <br />
			        </p>
			      </Col>
		    	</Row>
			</ListGroup.Item>
            {this.state.showModal && <AssignDialog show={this.state.showModal} handleClose={this.handleClose} {...this.props} />}
            </>
		)
	}
}

function RunList(props) {
	return (
		<Card>
			<Card.Header>
				{props.category}  <Badge pill variant="primary">{props.count}</Badge>
			</Card.Header>
	        <ListGroup>
				{props.children}
			</ListGroup>
	   </Card>
   )
}

function RacerCard(props) {
    let raceEntryView = props.collection.getDynamicView(props.raceEntry.id);
    raceEntryView.applySimpleSort(props.sortMode);
    let runs = raceEntryView.data();
    //filter runs by active / complete
	return(
		<Card>
			<Card.Header>
				{props.raceEntry.racer.racer_number} - {props.raceEntry.racer.display_name}
				<Badge pill variant="primary">{runs.length}</Badge>
			</Card.Header>
			{runs.map(run => <Run run={run} key={run.id} {...props} />)}
		</Card>
	)
}

class App extends React.Component {
	constructor(props) {
		super(props);

		var db = new loki('checkpoint.db');
		var runs = db.addCollection('runs');

		runs.ensureUniqueIndex('id');
		runs.insert(init['runs']);
		runs.addDynamicView(DISPLAY_UNASSIGNED);
		runs.addDynamicView(DISPLAY_NEW);
		init['race_entries'].forEach(raceEntry => {
			let raceEntryView = runs.addDynamicView(raceEntry.id);
            raceEntryView.applyWhere(function(run){return run.race_entry && run.race_entry.id == raceEntry.id});

		});

		this.state = {
			viewMode: DISPLAY_UNASSIGNED,
			sortMode: SORT_DEADLINE,
			db: db,
			raceEntries: init['race_entries'],
            loading: false,
		}
		this.viewModes = [DISPLAY_UNASSIGNED, DISPLAY_NEW]
		this.sortModes = [SORT_READY_TIME, SORT_DEADLINE, SORT_CHECKPOINT]
	}

	changeSortMode = (mode) => {
		this.setState({sortMode : mode});
	}
	changeViewMode = (mode) => {
		console.log("change view mode", mode);
		this.setState({viewMode : mode});
	}
	updateNavBar = (mode) => {
		if (this.viewModes.includes(mode)) {
			this.changeViewMode(mode);
		}
		else if (this.sortModes.includes(mode)) {
			this.changeSortMode(mode);
		}
	}
    openAssignDialog = () => {
        this.setState({showAssign: true});
    }
    assign = (run, raceEntry) => {
        let url = '/dispatch/assign/';
        let requestObj = {
            run_pk : run.id,
            race_entry_pk: raceEntry,
        }
        this.action(url, requestObj);
    }
    unassign = (run) => {
        let url = '/dispatch/unassign/';
        let requestObj = {
            run_pk : run.id,
        }

        this.action(url, requestObj);
    }
    action = (url, requestObj) => {
        this.setState({loading:true});

        axios.post(url, requestObj)
            .then(response => {
                console.log(response);
                //if {error_description in response}
                let db = this.updateTable([response.data]);
                this.setState({db: db, loading : false});
            })
            .catch(error => {
                alert(error);
                this.setState({loading : false});
            })
    }
    refresh = () => {
        this.setState({loading : true});
        axios.get('/dispatch/refresh/')
            .then(response => {
                console.log(response);
                let db = this.updateTable(response.data);
                this.setState({db: db, loading : false});
            })
            .catch(error => {
                alert(error);
                this.setState({loading : false});
            })
    }
    updateTable = (data) => {
        let db = this.state.db;
        let collection = db.getCollection('runs');
        data.forEach(entry => {
            let run = collection.findOne({'id' : entry.id})
            let updatedRun = {...run, ...entry}
            collection.update(updatedRun);
        })

        return db;
    }
	render () {
		var runs, allRuns, allRunsView;
		runs = this.state.db.getCollection('runs')
        allRunsView = runs.getDynamicView(this.state.viewMode);
        allRunsView.applyFind({'race_entry' : null});
		allRunsView.applySimpleSort(this.state.sortMode);
		allRuns = allRunsView.data();
        // dynamic views based on status
		return (
			<>
			   <div className="mb-2 board-tabs">
					<NavBar refresh={this.refresh} viewMode={this.state.viewMode} sortMode={this.state.sortMode} update={this.updateNavBar} />
			   </div>
				<RunList category="Unassigned" count={allRuns.length}>
					{allRuns.map(run => <Run run={run} key={run.id} raceEntries={this.state.raceEntries} assign={this.assign} /> )}
			    </RunList>

				<CardDeck>
					{this.state.raceEntries.map(raceEntry => <RacerCard sortMode={this.state.sortMode} collection={runs} raceEntry={raceEntry} key={raceEntry.id} raceEntries={this.state.raceEntries} assign={this.assign} />)}
				</CardDeck>
			</>
		)
	}
}

ReactDOM.render(
	<App />, document.getElementById('react-area')
);
