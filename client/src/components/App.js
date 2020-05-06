import React from 'react';
import { BrowserRouter, Switch, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from '../redux/store';

import 'antd/dist/antd.css';
import RacingPage from './Racing/RacingPage';
import LandingPage from './LandingPage';

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Switch>
          <Route exact path="/" component={LandingPage} />
          <Route exact path="/racing" component={RacingPage} />
        </Switch>
      </BrowserRouter>
    </Provider>
  );
}

export default App;
