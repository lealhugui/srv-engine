import React, { Component } from 'react';
import JsonApiReq from '../Requests';
import {
	API_URL,
	addLogoAnimation,
	removeLogoAnimation
 } from '../constants';
import { TableCard } from './Cards';
import './TableInfo.css';


class TableInfo extends Component {

	constructor(props){

		super(props);
		this.state = {table: null};
	}

	componentDidMount(){
		addLogoAnimation();
		new JsonApiReq(API_URL, 'api/tableinfo/'+this.props.match.params.name+"/").get()
            .then((jsonData) => {
                if('success' in jsonData){
                    if(jsonData.success===false){
                        throw jsonData.err;
                    }
                }
                this.setState({table_info: jsonData});
            })
            .catch((err) => {
                alert(err);
            })
						.then(removeLogoAnimation);

	}

	render(){
		return (
			<div>
				<div className="app-content">
					{typeof(this.state.table_info) === 'undefined' ?
						(<span>Loading</span>) :
						(
							<div>
								<TableCard table={this.state.table_info} />
								<h2>
									<div className="table-info-wrapper">
										TABLE <small style={{fontStyle: 'italic'}}>"{this.state.table_info.table_name.toUpperCase()}"</small>
									</div>
								</h2>
							</div>
						)
					}
				</div>
			</div>
		);
	}
}

export default TableInfo;
