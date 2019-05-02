var React = require('react')
var ReactDOM = require('react-dom');
import loki from 'lokijs';
import axios from 'axios';
var moment = require('moment');
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
axios.defaults.xsrfCookieName = 'csrftoken'
import {Badge, Button, ButtonGroup, Card, CardDeck, Col, Form, Jumbotron, ListGroup, Nav, NavDropdown, Modal, Row, Table} from 'react-bootstrap';

const DISPLAY_COMPANIES = "companies";
const DISPLAY_RACERS = "racers";

const SORT_JOBS = "jobs";
const SORT_POINTS = "points";

function NavBar(props){
   return (
      <Nav variant="pills" activeKey={props.viewMode} onSelect={k => props.update(k)}>
        <Nav.Item>
          <Nav.Link eventKey={DISPLAY_COMPANIES} href="#">
            Companies
          </Nav.Link>
        </Nav.Item>

        <Nav.Item>
            <Nav.Link eventKey={DISPLAY_RACERS} title="Item">
                Racers
            </Nav.Link>
        </Nav.Item>


		<NavDropdown title="Sort" id="nav-dropdown">
		  <NavDropdown.Item active={props.sortMode == SORT_JOBS} eventKey={SORT_JOBS}>Ready Time</NavDropdown.Item>
		  <NavDropdown.Item active={props.sortMode == SORT_POINTS} eventKey={SORT_POINTS}>Deadline</NavDropdown.Item>
		</NavDropdown>
        <Button onClick={props.refresh} variant="secondary">Refresh</Button>
	</Nav>
    )
}
function RacerRow(props) {
	const raceEntry = props.raceEntry;	
	return (
		<tr>
			<td>{raceEntry.racer.display_name}</td>
			<td>{raceEntry.racer.racer_number}</td>
			<td>{raceEntry.racer.gender}</td>
			<td>{raceEntry.entry_status_as_string}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
		</tr>
	)
}

function RacerList(props) {
	return (
		<Table responsive>
			<thead>
				<tr>
					<th>Racer</th>
					<th>Racer Number</th>
					<th>Gender</th>
					<th>Status</th>
					<th>Active Jobs</th>
					<th>Complete Jobs</th>
					<th>Total Points</th>

				</tr>
			</thead>
			<tbody>
				{props.raceEntries.map(raceEntry => <RacerRow key={raceEntry.id} raceEntry={raceEntry} />)}
			</	tbody>
		</Table>
	)
}

class App extends React.Component {
	constructor(props) {
		super(props);

		let db = new loki('checkpoint-scoreboard.db');
		let runs = db.addCollection('runs');
		runs.ensureUniqueIndex('id');
		let raceEntries = db.addCollection('raceEntries');
		raceEntries.ensureUniqueIndex('id');

		init.forEach((company) => {
			runs.insert(company['runs']);
			raceEntries.insert(company['race_entries'])
			delete company['runs'];
			delete company['race_entries'];
		})


		this.state = {
			viewMode: DISPLAY_COMPANIES,
			sortMode: SORT_JOBS,
			db: db,
            loading: false,
            head: head,
			companies: init,
		}
		this.viewModes = [DISPLAY_RACERS, DISPLAY_COMPANIES]
		this.sortModes = [SORT_JOBS, SORT_POINTS]
	}
    componentDidMount() {
        this.refreshTimer = setInterval(() => this.refresh(), 30000);
    }
    componentWillUnmount() {
        clearInterval(this.refreshTimer);
    }
	changeSortMode = (mode) => {
        let db = this.state.db;
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
    refresh = () => {
        clearInterval(this.refreshTimer);
        this.setState({loading : true});
        let requestObj = {head: this.state.head}
        axios.post('/dispatch/refresh/', requestObj)
            .then(response => {
                console.log(response.data.runs);
                let db = this.updateTable(response.data.runs);

                this.setState({db: db, loading : false, head: response.data.head});
                this.refreshTimer = setInterval(() => this.refresh(), 30000);
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
    futureFilter = (run) => {
            return Date.parse(run.utc_time_ready) < Date.now();
    }
    render () {
		let timeNow = Date.now();
		let runs, allRuns, raceEntries, runsResults;


		runs = this.state.db.getCollection('runs');
        runsResults = runs.chain();

		raceEntries = this.state.db.getCollection('raceEntries').data;
        raceEntries.forEach(raceEntry =>{
            let racerResults = runsResults.copy();
            racerResults = racerResults.where(function(run){return run.race_entry && run.race_entry.id == raceEntry.id});
            raceEntry['results'] = racerResults;
        })

        runsResults = runsResults.find({'race_entry' : null});

		allRuns = runsResults.data();

		return (
			<>
			   <div className="mb-2 board-tabs">
					<NavBar refresh={this.refresh} viewMode={this.state.viewMode} sortMode={this.state.sortMode} update={this.updateNavBar} />
			   </div>

                {(this.state.viewMode == DISPLAY_COMPANIES) && null

                }

				{(this.state.viewMode == DISPLAY_RACERS) &&
					<RacerList raceEntries={raceEntries} />
               }
			</>
		)
	}
}

ReactDOM.render(
	<App />, document.getElementById('react-area')
);
