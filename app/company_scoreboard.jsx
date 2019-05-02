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
	let racerRunsView = props.runs.getDynamicView(raceEntry.id);
	//console.log(props);
	return (
		<tr>
			{(props.viewMode == DISPLAY_RACERS) && <td>{raceEntry.racer.company.name}</td>}
			<td>{raceEntry.racer.display_name}</td>
			<td>{raceEntry.racer.racer_number}</td>
			<td>{raceEntry.racer.gender}</td>
			<td>{raceEntry.entry_status_as_string}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{racerRunsView.count()}</td>
		</tr>
	)
}

function RacerList(props) {

	return (
		<Table responsive>
			<thead>
				<tr>
					{(props.viewMode == DISPLAY_RACERS) && <th>Company</th>}
					<th>Racer</th>
					<th>Racer Number</th>
					<th>Gender</th>
					<th>Status</th>
					<th>Active Jobs</th>
					<th>Complete Jobs</th>
					<th>Total Points</th>
					<th>All Jobs</th>
				</tr>
			</thead>
			<tbody>
				{props.raceEntries.map(raceEntry => <RacerRow {...props} key={raceEntry.id} raceEntry={raceEntry} />)}
			</tbody>
		</Table>
	)
}

function CompanyList(props) {

	return props.companies.map(company =>
		<Card key={company.name} >
			<Card.Body>
				<Table>
					<thead>
						<tr>
							<th></th>
							<th>Active Jobs</th>
							<th>Complete Jobs</th>
							<th>Late Jobs</th>
							<th>Total Points</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td><h2>{company.name}</h2></td>
							<td></td>
							<td></td>
							<td></td>
							<td></td>
						</tr>
					</tbody>
				</Table>
				<RacerList key={company.name} runs={props.runs} viewMode={props.viewMode} raceEntries={company.raceEntries} />
			</Card.Body>
		</Card>
	)
}

class App extends React.Component {
	constructor(props) {
		super(props);

		let db = new loki('checkpoint-scoreboard.db');
		let runs = db.addCollection('runs');
		runs.ensureUniqueIndex('id');
		//let raceEntries = db.addCollection('raceEntries');
		//raceEntries.ensureUniqueIndex('id');
		let companyList = [];
		let raceEntriesList = [];

		init.forEach((obj) => {
			let company = obj.company;
			delete company['runs'];
			runs.insert(obj['runs']);
			runs.addDynamicView(company.name);
			obj.race_entries.forEach(raceEntry => {
				raceEntriesList.push(raceEntry);
				let raceEntryView = runs.addDynamicView(raceEntry.id);
				raceEntryView.applyWhere(run => (run.race_entry) && (run.race_entry.id == raceEntry.id));
			});


			company['raceEntries'] = obj.race_entries;
			companyList.push(company);
		});

		this.state = {
			viewMode: DISPLAY_COMPANIES,
			sortMode: SORT_JOBS,
			db: db,
            loading: false,
            head: head,
			companies: companyList,
			raceEntries : raceEntriesList,
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
		let runs = this.state.db.getCollection('runs');


		return (
			<>
			   <div className="mb-2 board-tabs">
					<NavBar refresh={this.refresh} viewMode={this.state.viewMode} sortMode={this.state.sortMode} update={this.updateNavBar} />
			   </div>

                {(this.state.viewMode == DISPLAY_COMPANIES) &&
					<CompanyList runs={runs} sortMode={this.state.sortMode} viewMode={this.state.viewMode} companies={this.state.companies} />
                }

				{(this.state.viewMode == DISPLAY_RACERS) &&
					<RacerList key="allRacersList" runs={runs} viewMode={this.state.viewMode} raceEntries={this.state.raceEntries} />
               }
			</>
		)
	}
}

ReactDOM.render(
	<App />, document.getElementById('react-area')
);
