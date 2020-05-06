import React from 'react';
import { connect } from 'react-redux';
import { Layout } from 'antd';

import RacingMenu from './RacingMenu';
import RacingHorses from './RacingHorses';
import RacingHorse from './RacingHorse';

const RacingPage = ({ currentHorse }) => {
  const { Content } = Layout;
  return (
    <Layout style={{ background: '#fff' }}>
      <Content style={{ padding: '10px 20px' }}>
        <RacingMenu />
        <RacingHorses />
        {currentHorse === "" || <RacingHorse />}
      </Content>
    </Layout>
  )
};
const mapStateToProps = (state) => ({
  currentHorse: state.racings.currentHorse,
});
export default connect(mapStateToProps, null)(RacingPage);
