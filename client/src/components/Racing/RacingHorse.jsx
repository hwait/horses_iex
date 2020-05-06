import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { selectChanges, selectPrices, getSelectedHorsesNames, colors } from '../../redux/racings.duck';
import Dygraph from 'dygraphs';
import moment from 'moment'
import { Typography } from 'antd';

import './RacingHorse.css';

const RacingHorse = ({ changes, prices, horseNames }) => {
    const { Title } = Typography;
    const graph = (series, data, place) => {
        return new Dygraph(document.getElementById(place), data, {
            labels: ['Time', ...horseNames],
            legend: 'always',
            series: series,
            axes: {
                x: {
                    valueFormatter: x => moment.utc(x).format("HH:mm"),
                    axisLabelFormatter: x => moment.utc(x).format("HH:mm"),
                },
                y: {
                    valueFormatter: y => Math.round(y * 100) / 100,
                    axisLabelFormatter: y => Math.round(y * 100) / 100,
                }
            }
        });
    }

    useEffect(() => {
        const series = horseNames.map((x, index) => ({ [x]: { color: colors[index] } })).reduce((a, b) => Object.assign(a, b), {})
        graph(series, prices, 'prices');
        graph(series, changes, 'deviations');
    });
    return (<div>
        <Title>Price moving</Title>
        <div id="prices" className="graph" />
        <Title>Price deviation moving</Title>
        <div id="deviations" className="graph" />
    </div>)
};
const mapStateToProps = (state) => ({
    prices: selectPrices(state),
    changes: selectChanges(state),
    horseNames: getSelectedHorsesNames(state),
    currentHorse: state.racings.currentHorse,
});
export default connect(mapStateToProps, null)(RacingHorse);
