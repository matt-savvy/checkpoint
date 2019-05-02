var React = require('react')
var ReactDOM = require('react-dom');
import loki from 'lokijs';
import axios from 'axios';
var moment = require('moment');
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
axios.defaults.xsrfCookieName = 'csrftoken'
import {Badge, Button, ButtonGroup, Card, CardDeck, Col, Form, Jumbotron, ListGroup, Nav, NavDropdown, Modal, Row} from 'react-bootstrap';

const DISPLAY_UNASSIGNED = "unassigned";
const DISPLAY_NEW = "new";

const SORT_READY_TIME = "utc_time_ready";
const SORT_DEADLINE = "utc_time_due";
const SORT_CHECKPOINT = "checkpoint";

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

function UnassignDialog(props) {
    return (
        <Modal show={true} onHide={props.handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>Unassign</Modal.Title>
            </Modal.Header>

            <Modal.Body>
                <label>Are you sure you want to unassign this run?</label>
            </Modal.Body>
            <Modal.Footer>
                <Button onClick={props.handleClose} variant="secondary">Cancel</Button>
                <Button onClick={props.handleUnassign} variant="danger">Unassign</Button>
            </Modal.Footer>
        </Modal>
    )

}

function NavBar(props){
   const clock = moment(props.timeNow).format('HH:mm A');
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
		  <NavDropdown.Item active={props.sortMode == SORT_READY_TIME} eventKey={SORT_READY_TIME}>Ready Time</NavDropdown.Item>
		  <NavDropdown.Item active={props.sortMode == SORT_DEADLINE} eventKey={SORT_DEADLINE}>Deadline</NavDropdown.Item>
		  <NavDropdown.Item active={props.sortMode == SORT_CHECKPOINT} eventKey={SORT_CHECKPOINT}>Checkpoint</NavDropdown.Item>
		</NavDropdown>
        <Button onClick={props.refresh} variant="secondary">Refresh</Button>
        <Badge variant="light">{clock}</Badge>
	</Nav>
    )
}

function Checkpoint(props) {
    return (
        <>
            <strong>{props.checkpoint.checkpoint_name}</strong>
            <br />
            {props.checkpoint.address_line_1}
            <br />
            {props.checkpoint.address_line_2}
            <br />
        </>
    )
}

class Run extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            showAssign : false,
            showUnassign : false,
        }
    }
    componentDidMount() {
        console.log("run mount");
    }
    startAssign = () => {
        this.setState({showAssign : true});
    }
    startUnassign = () => {
        this.setState({showUnassign : true});
    }
    handleUnassign = () => {
        this.props.unassign(this.props.run);
        this.setState({showUnassign : false});
    }
    handleClose = () => {
        this.setState({showAssign : false, showUnassign : false});
    }
	render () {
        let run = this.props.run;
        let nowMoment = moment(this.props.timeNow);
        let readyMoment = moment(run.utc_time_ready)
        let deadlineMoment = moment(run.utc_time_due)
        let format = "hh:mm A";
        let readyFromNow = readyMoment.fromNow();
        let readyTime = readyMoment.format(format)
		let deadlineFromNow = deadlineMoment.fromNow();
        let deadline = deadlineMoment.format(format);

        let assignable, unassignable;
        if ((run.status_as_string == "Assigned") || (run.status_as_string == "Unassigned")) {
            assignable = true;
            //TODO picked as well? pass offs allowed?
        }

        if (run.status_as_string == "Assigned") {
            unassignable = true;
        }
        let urgent, late, styleClassName = "";
        let timeRemaining = deadlineMoment - nowMoment;
        if (timeRemaining < 0) {
            late = true;
            styleClassName = "expired";
        } else {
            let totalTime = deadlineMoment - readyMoment;
            urgent = ((timeRemaining / totalTime) < 0.55);
            if (urgent) {
                styleClassName = "urgent";
            }
        }
		return (
            <>
			<div className={`list-group-item ${styleClassName}`}>
    			<Row>
      				<Col>
                        <em>From:</em><br/>
				          <Checkpoint checkpoint={run.job.pick_checkpoint} />
	                       <br />
	                     ({run.job.service}) {readyTime} to {deadline}
		                    <br />
	                       Ready {readyFromNow}
			                        <br />
                           Due {deadlineFromNow}
	      		  </Col>
			      <Col>
				  	<em>To:</em><br/>
			          <Checkpoint checkpoint={run.job.drop_checkpoint} />
                        <br />
                          ${run.job.points} <br />
                          #ID{run.id} <br />
                          {run.status_as_string}

			      </Col>
                </Row>
                <Row>
                  <Col lg="2">
                    <ButtonGroup size="sm">
                        {assignable && <Button variant="light" onClick={this.startAssign}>Assign</Button>}
                        {unassignable && <Button variant="secondary" onClick={this.startUnassign}>UnAssign</Button>}
                    </ButtonGroup>
                  </Col>
		    	</Row>

			</div>
            {this.state.showAssign && <AssignDialog show={this.state.showAssign} handleClose={this.handleClose} {...this.props} />}
            {this.state.showUnassign && <UnassignDialog show={this.state.showUnassign} handleClose={this.handleClose} handleUnassign={this.handleUnassign} />}
            </>
		)
	}
}

function NothingToShow(props) {
    return (
        <Jumbotron>
          <h2>All Clear!</h2>
              <p>
                {props.message || "Nothing to show right now."}
              </p>
        </Jumbotron>
    )
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
            {runs.length == 0 && <NothingToShow message="This racer has no active jobs."/>}
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
		let unassignedRuns = runs.addDynamicView(DISPLAY_UNASSIGNED, {sortPriority : 'active'});
        unassignedRuns.applySort(this.deadlineSort);

		init['race_entries'].forEach(raceEntry => {
			let raceEntryView = runs.addDynamicView(raceEntry.id, {sortPriority : 'active'});
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
        let db = this.state.db;
        let allRuns = db.getCollection('runs').getDynamicView(DISPLAY_UNASSIGNED);

        if (mode == SORT_READY_TIME) {
            allRuns.applySort(this.readySort);
        } else if (mode == SORT_DEADLINE) {
            allRuns.applySort(this.deadlineSort);
        } else if (mode == SORT_CHECKPOINT) {
            allRuns.applySort(this.checkpointSort);
        }

		this.setState({db: db, sortMode : mode});
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
    readySort = (run1, run2) => {
            let time1 = Date.parse(run1.utc_time_ready);
            let time2 = Date.parse(run2.utc_time_ready);
            if (time1 > time2) {return 1}
            if (time1 < time2) {return -1}
            return 0;
    }
    deadlineSort = (run1, run2) => {
            let time1 = Date.parse(run1.utc_time_due);
            let time2 = Date.parse(run2.utc_time_due);
            if (time1 > time2) {return 1}
            if (time1 < time2) {return -1}
            return 0;
    }
    checkpointSort = (run1, run2) => {
            if (run1.job.pick_checkpoint.checkpoint_name > run2.job.pick_checkpoint.checkpoint_name) {return 1}
            if (run1.job.pick_checkpoint.checkpoint_name < run2.job.pick_checkpoint.checkpoint_name) {return -1}
            return 0;
    }
    render () {

        let timeNow = Date.now();
		var runs, allRuns, allRunsView;
		runs = this.state.db.getCollection('runs')

        allRunsView = runs.getDynamicView(DISPLAY_UNASSIGNED);
        allRunsView.applyFind({'race_entry' : null});

		allRuns = allRunsView.data();

		return (
			<>
			   <div className="mb-2 board-tabs">
					<NavBar timeNow={timeNow} refresh={this.refresh} viewMode={this.state.viewMode} sortMode={this.state.sortMode} update={this.updateNavBar} />
			   </div>
				<RunList category="Unassigned" count={allRuns.length}>
					{allRuns.map(run => <Run timeNow={timeNow} run={run} key={run.id} raceEntries={this.state.raceEntries} assign={this.assign} /> )}
                    {allRuns.length == 0 && <NothingToShow />}
                </RunList>

				<CardDeck>
					{this.state.raceEntries.map(raceEntry => <RacerCard timeNow={timeNow} sortMode={this.state.sortMode} collection={runs} raceEntry={raceEntry} key={raceEntry.id} raceEntries={this.state.raceEntries} assign={this.assign} unassign={this.unassign} />)}
				</CardDeck>
			</>
		)
	}
}

ReactDOM.render(
	<App />, document.getElementById('react-area')
);