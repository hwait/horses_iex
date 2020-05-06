import moment from 'moment'
import React from 'react';
import { connect } from 'react-redux';
import { DatePicker, Menu } from 'antd';
import { HomeOutlined } from '@ant-design/icons';
import { actions as racingsActions, getPlaces, getTimes } from '../../redux/racings.duck';

const RacingMenu = ({ loadRacesInit, selectCourse, loadHorsesInit, currentDate, currentPlace, places, times }) => {
  const { SubMenu } = Menu;
  const onMenuClick = (e) => {
    if (e.key === 'home') console.log('home');
    else if (e.key.includes('course')) {
      selectCourse(places[Number.parseInt(e.key.split('_')[1])])
    }
    else if (e.key.includes('time')) {
      loadHorsesInit(currentDate, e.key.split('_')[1])
    }
  };
  const onDateChoose = (date, dateString) => {
    loadRacesInit(dateString);
  };

  const courses = places.map((x, i) => (<Menu.Item key={`course_${i}`}>{x}</Menu.Item>))
  const timestarts = times.map(({ time, rid }) => (<Menu.Item key={`time_${rid}`}>{time}</Menu.Item>))
  const dateFormat = 'YYYY-MM-DD';
  return (
    <Menu onClick={onMenuClick} mode="horizontal">
      <Menu.Item key="home"><HomeOutlined /></Menu.Item>
      <Menu.Item key="datepicker">
        <DatePicker
          onChange={onDateChoose}
          defaultValue={currentDate}
          defaultPickerValue={moment('2020-01-01', dateFormat)}
          format={dateFormat}
        />
      </Menu.Item>
      <SubMenu title={currentPlace === '' ? "Courses" : currentPlace} disabled={places.length === 0} >
        {courses}
      </SubMenu>
      {timestarts}
    </Menu>
  );
};
const mapStateToProps = (state) => ({
  currentDate: state.racings.currentDate,
  currentPlace: state.racings.currentPlace,
  places: getPlaces(state),
  times: getTimes(state)
});
export default connect(mapStateToProps, { ...racingsActions })(RacingMenu);
