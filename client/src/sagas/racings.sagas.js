import { put, takeLatest, all, call } from 'redux-saga/effects';
import axios from 'axios';

import { actions, actiontypes } from '../redux/racings.duck';

export function* racingsSagas() {
  yield all([call(initRaces),
  call(initHorses)]);
}

//#region RACES
export function* initRaces() {
  yield takeLatest(actiontypes.LOAD_RACES_INIT, fetchRaces);
}

export function* fetchRaces(arg) {
  const date = arg.payload
  try {
    const response = yield axios.get(`/races/${date}`);
    if (Object.keys(response.data).length === 0)
      yield put(actions.actionFailure('There is no racings on that date!'));
    else
      yield put(actions.loadRacesSuccess(response.data));
  } catch (error) {
    yield put(actions.actionFailure(error.message));
  }
}
//#endregion

//#region HORSES
export function* initHorses() {
  yield takeLatest(actiontypes.LOAD_HORSES_INIT, fetchHorses);
}

export function* fetchHorses(arg) {
  const { date, rid } = arg.payload
  try {
    const response = yield axios.get(`/races/${date}/${rid}`);
    if (Object.keys(response.data).length === 0)
      yield put(actions.actionFailure('There is no horces in that race!'));
    else {
      const mid = response.data[0].mid;
      const responseChanges = yield axios.get(`/bf/${date}/${mid}`);
      yield put(actions.loadHorsesSuccess(response.data, responseChanges.data));
    }
  } catch (error) {
    yield put(actions.actionFailure(error.message));
  }
}
//#endregion
