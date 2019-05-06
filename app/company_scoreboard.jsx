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

const SORT_COMPLETE_JOBS = "completedRuns";
const SORT_ACTIVE_JOBS = "activeRuns";
const SORT_POINTS = "points_earned";
const SORT_FINAL_SCORE = "grand_total";

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
		<NavDropdown.Item active={props.sortMode == SORT_COMPLETE_JOBS} eventKey={SORT_COMPLETE_JOBS}>Complete Jobs</NavDropdown.Item>
		  <NavDropdown.Item active={props.sortMode == SORT_ACTIVE_JOBS} eventKey={SORT_ACTIVE_JOBS}>Active Jobs</NavDropdown.Item>
		  <NavDropdown.Item active={props.sortMode == SORT_POINTS} eventKey={SORT_POINTS}>Points</NavDropdown.Item>
		  <NavDropdown.Item active={props.sortMode == SORT_FINAL_SCORE} eventKey={SORT_FINAL_SCORE}>Final Score</NavDropdown.Item>
		</NavDropdown>
        <Button onClick={props.refresh} variant="secondary">Refresh</Button>
	</Nav>
    )
}
function RacerRow(props) {
	const raceEntry = props.raceEntry;
	let racerRunsView = props.runs.getDynamicView(raceEntry.id);
	return (
		<tr>
			{(props.viewMode == DISPLAY_RACERS) && <td>{raceEntry.racer.company.name}</td>}
			<td>{raceEntry.racer.display_name}</td>
			<td>{raceEntry.racer.racer_number}</td>
			<td>{raceEntry.racer.gender}</td>
			<td>{raceEntry.entry_status_as_string}</td>
			<td>{raceEntry.activeRuns}</td>
			<td>{raceEntry.completedRuns}</td>
			<td>${raceEntry.points_earned}</td>
			<td>{(raceEntry.grand_total != 0) && <>${raceEntry.grand_total}</>}</td>
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
					<th>Points Earned</th>
					<th>Final Score</th>

				</tr>
			</thead>
			<tbody>
				{props.raceEntries.map(raceEntry => <RacerRow {...props} key={raceEntry.id} raceEntry={raceEntry} />)}
			</tbody>
		</Table>
	)
}

function CompanyList(props) {

	return props.companies.map(company => {
		return (
			<Card key={company.company.name} >
				<Card.Body>
					<Table>
						<thead>
							<tr>
								<th></th>
								<th>Active Jobs</th>
								<th>Complete Jobs</th>
								<th>Late Jobs</th>
								<th>Points Earned</th>
								<th>Final Score</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<td><h2>{company.company.name}</h2></td>
								<td>{company.activeRuns}</td>
								<td>{company.completedRuns}</td>
								<td>{company.lateRuns}</td>
								<td>${company.points_earned}</td>
								<td>{(company.grand_total != 0) && <>${company.grand_total}</>}</td>

							</tr>
						</tbody>
					</Table>
					<RacerList key={company.company.name} runs={props.runs} viewMode={props.viewMode} raceEntries={company.raceEntries} />
				</Card.Body>
			</Card>
		)
	}

	)
}

class App extends React.Component {
	constructor(props) {
		super(props);

		let db = new loki('checkpoint-scoreboard.db');
		let runs = db.addCollection('runs');
		runs.ensureUniqueIndex('id');
		let companyList = [];
		let raceEntriesList = [];

		init.forEach((obj) => {

			let companyEntry = obj;

			obj['runs'].forEach(run => {
				run.company = companyEntry.company;
			})
			runs.insert(obj['runs']);

			delete companyEntry['runs'];

			let companyView = runs.addDynamicView(companyEntry.company.name);
			companyView = companyView.applyWhere(run => run.company.id == companyEntry.company.id);

			companyEntry.race_entries.forEach(raceEntry => {
				raceEntriesList.push(raceEntry);
				let raceEntryView = runs.addDynamicView(raceEntry.id);
				raceEntryView.applyWhere(run => (run.race_entry) && (run.race_entry.id == raceEntry.id));
			});

			companyEntry['raceEntries'] = companyEntry.race_entries;
			delete companyEntry['race_entries'];
			companyList.push(companyEntry);
		});

		this.state = {
			viewMode: DISPLAY_COMPANIES,
			sortMode: SORT_POINTS,
			db: db,
            loading: false,
            head: head,
			companies: companyList,
			raceEntries : raceEntriesList,
		}
		this.viewModes = [DISPLAY_RACERS, DISPLAY_COMPANIES]
		this.sortModes = [SORT_COMPLETE_JOBS, SORT_ACTIVE_JOBS, SORT_POINTS]
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
        axios.post('/dispatch/scoreboard/refresh/', requestObj)
            .then(response => {
                console.log(response);
                let db = this.updateTable(response.data.runs);

				let companyList = [];
				let raceEntryList = [];
				response.data.company_entries.forEach(companyEntry => {
					//delete companyEntry['runs'];
					//raceEntryList.push(companyEntry[''])
					companyEntry['raceEntries'] = companyEntry['race_entries'];
					delete companyEntry['race_entries'];
					companyList.push(companyEntry);

					companyEntry['raceEntries'].forEach(raceEntry => {
						raceEntryList.push(raceEntry);
					})

				})

                this.setState({db: db, companies:companyList, raceEntries: raceEntryList, loading : false, head: response.data.head});
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
			if (run) {
				let updatedRun = {...run, ...entry}
				collection.update(updatedRun);
			} else {
				collection.insert(entry);
			}
        })

        return db;
    }
    futureFilter = (run) => {
            return Date.parse(run.utc_time_ready) < Date.now();
    }
	createTotals = (object, totalRunsView) => {
		let activeRuns = totalRunsView.resultset.copy().where(run => run.status_as_string != "Completed");
		let completedRuns = totalRunsView.resultset.copy().where(run => run.status_as_string == "Completed");
		let lateRuns = totalRunsView.resultset.copy().where(run => (run.status_as_string == "Completed") && (run.determination_as_string == "Late"));

		//if (object.raceEntries) {
		//	let raceEntryScores = object.raceEntries.map(raceEntry => raceEntry.points_awarded);
        //}

		object.activeRuns = activeRuns.count()
		object.completedRuns = completedRuns.count()
        object.lateRuns = lateRuns.count();
		return object;
	}
	sort = (objects) => {
		let sortMode = this.state.sortMode;

		objects.sort((obj1, obj2) => {
			if (obj1[sortMode] < obj2[sortMode]) {
				return 1
			}
			if (obj1[sortMode] > obj2[sortMode]) {
				return -1
			}
			return 0
		});

		return objects;
	}
    render () {
		let runs = this.state.db.getCollection('runs');

		this.state.companies.map(company => {
			let totalRunsView = runs.getDynamicView(company.company.name);
			return this.createTotals(company, totalRunsView);
		})

		this.state.raceEntries.forEach(raceEntry => {
			let totalRunsView = runs.getDynamicView(raceEntry.id);
			return this.createTotals(raceEntry, totalRunsView);
		})

		let companies = this.sort(this.state.companies);
		let raceEntries = this.sort(this.state.raceEntries);
		let sortMode = this.state.sortMode;

		return (
			<>
			   <div className="mb-2 board-tabs">
					<NavBar refresh={this.refresh} viewMode={this.state.viewMode} sortMode={this.state.sortMode} update={this.updateNavBar} />
			   </div>

                {(this.state.viewMode == DISPLAY_COMPANIES) &&
					<CompanyList runs={runs} sortMode={this.state.sortMode} viewMode={this.state.viewMode} companies={this.state.companies} />
                }

				{(this.state.viewMode == DISPLAY_RACERS) &&
					<RacerList key="allRacersList" runs={runs} viewMode={this.state.viewMode} raceEntries={raceEntries} />
               }
			</>
		)
	}
}

ReactDOM.render(
	<App />, document.getElementById('react-area')
);
