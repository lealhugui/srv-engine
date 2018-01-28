import React from 'react';
import { Link } from 'react-router-dom';
import './Cards.css';

export const TableCard = (props) => {
    let listWrapperStyles = {
        marginTop: '5px'
    }
    let flds = null;
    if(typeof(props.table) !== 'undefined'){
        flds = props.table.props.fields.map(
            (fld) => (
                <div key={fld.field_name}
                     className="table-field "
                     title={fld.field_name}
                     style={{color: fld.is_primary_key===true ? 'red':'inherit'}} >
                    {fld.field_name}<span className="fld-type">{fld.inner_type}</span>
                </div>
            )
        );
    }
    else{
        return (<div>Ref Error</div>);
    }

    return (
        <article className="table-card-outer">
            <div className="table-card" title={props.table.table_name}>
                <p>{props.table.table_name.toUpperCase()}</p>
                <button className="obj-identifier" href="{'/table/'+ props.table.table_name}"> </button>
                <small style={listWrapperStyles}>{flds}</small>
            </div>
        </article>
    );
}

export const SchemaCard = (props) => {

    let listTables = (<div></div>);
    if (props.schema.tables !== null && props.schema.tables.length > 0)
    {
        listTables = props.schema.tables.map(
            (table) => <TableCard key={table.table_name} table={table} />
        )
    }
    return (
        <div className="schema-card">
            <div>
                <p>Schema Name: <b>{props.schema.schema_name.toUpperCase()}</b></p>
            </div>
            {listTables}
        </div>
    );

}

