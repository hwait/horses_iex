import { all, call } from 'redux-saga/effects';
import { racingsSagas } from './racings.sagas';

export default function* rootSaga() {
  yield all([call(racingsSagas)]);
}
