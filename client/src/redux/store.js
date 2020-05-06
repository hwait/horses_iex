import { createStore, applyMiddleware } from 'redux';
import logger from 'redux-logger';
import { combineReducers } from 'redux';
import racingReducer from './racings.duck';

import createSagaMiddleware from 'redux-saga';
import rootSaga from '../sagas/root.saga';

const sagaMiddleware = createSagaMiddleware();

const mw = [sagaMiddleware, logger];

//if (process.env.NODE_ENV==='development') {    mw.push(logger);}

const rootReducer = combineReducers({
    racings: racingReducer,
});
const store = createStore(rootReducer, applyMiddleware(...mw));

sagaMiddleware.run(rootSaga);

export default store;
