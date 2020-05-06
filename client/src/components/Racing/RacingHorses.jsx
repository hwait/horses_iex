import React from 'react';
import { connect } from 'react-redux';
import { Table, Skeleton, Typography } from 'antd';
import { CheckCircleTwoTone } from '@ant-design/icons'
import { actions as racingsActions, colors } from '../../redux/racings.duck';
import './RacingHorses.css';

const RacingHorses = ({ horses, selectHorse, currentHorse, currentHorseId, loading, currentRid }) => {
    const { Text } = Typography;
    const onHorseClick = (e) => {
        selectHorse(e.key, e.horseName, e.marketTime)
    };

    const columns = [
        {
            title: '#',
            dataIndex: 'position',
            key: 'position',
            render: x => x === 40 ? '' : x,
        },
        {
            title: 'Name',
            dataIndex: 'horseName',
            key: 'horseName',
            render: (text, row) => (row.selected < 0 ? <Text strong>{text}</Text> : <Text strong style={{ backgroundColor: colors[row.selected], color: '#fff' }}>{text}</Text>),
        },
        {
            title: 'Age',
            dataIndex: 'age',
            key: 'age',
        },
        {
            title: 'Odds',
            dataIndex: 'decimalPrice',
            key: 'decimalPrice',
            render: x => Math.round(x * 100) / 100,
        },
        {
            title: 'Trainer',
            dataIndex: 'trainerName',
            key: 'trainerName',
        },
        {
            title: 'Jockey',
            dataIndex: 'jockeyName',
            key: 'jockeyName',
        },
        {
            title: 'RPR',
            dataIndex: 'RPR',
            key: 'rpr',
        },
        {
            title: 'TR',
            dataIndex: 'TR',
            key: 'tr',
        },
        {
            title: 'OR',
            dataIndex: 'OR',
            key: 'or',
        },
        {
            title: 'Winner',
            dataIndex: 'res_win',
            key: 'res_win',
            render: x => x > 0 ? <CheckCircleTwoTone twoToneColor="#52c41a" /> : '',
        },
        {
            title: 'Placed',
            dataIndex: 'res_place',
            key: 'res_place',
            render: x => x > 0 ? <CheckCircleTwoTone twoToneColor="#52c41a" /> : '',
        },

    ];
    const rowSelection = {
        onSelect: onHorseClick,
        hideDefaultSelections: true
    }

    const html = currentRid ? (<Table
        rowSelection={rowSelection}
        columns={columns}
        dataSource={horses}
        pagination={{ hideOnSinglePage: true, pageSize: 50 }}
        onRow={(r) => ({ onClick: () => onHorseClick(r) })}
        rowClassName={(x) => Number.parseInt(x.key) === currentHorseId ? 'active-row' : null}
        loading={loading}
    />) : <Skeleton />

    return html


};
const mapStateToProps = (state) => ({
    horses: state.racings.horses,
    currentHorse: state.racings.currentHorse,
    currentRid: state.racings.currentRid,
    currentHorseId: state.racings.currentHorseId,
    loading: state.racings.loading,

});
export default connect(mapStateToProps, { ...racingsActions })(RacingHorses);
