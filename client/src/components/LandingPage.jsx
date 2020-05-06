import React from 'react';
import { Button } from 'antd';

import './LandingPage.css';

const LandingPage = () => {
  return (
    <div className="wrapper">
      <div className="left">
        <Button href="/racing" >RACINGS</Button>
      </div>
      <div className="right">
        <Button href="/racing" >STOCKS</Button>
      </div>
    </div>

  );
};
export default LandingPage;
