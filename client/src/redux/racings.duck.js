import { createSelector } from 'reselect';
import Immutable from '../components/immutable'

export const colors = ['#50514f', '#3A86FF', '#ff006e', '#02c39a', '#8338ec']

export const actiontypes = {
  LOAD_RACES_INIT: 'LOAD_RACES_INIT',
  LOAD_RACES_SUCCESS: 'LOAD_RACES_SUCCESS',
  LOAD_HORSES_INIT: 'LOAD_HORSES_INIT',
  LOAD_HORSES_SUCCESS: 'LOAD_HORSES_SUCCESS',
  COURSE_SELECTED: 'COURSE_SELECTED',
  ACTION_FAILURE: 'ACTION_FAILURE',
  SELECT_HORSE: 'SELECT_HORSE',
};

export const actions = {
  loadRacesInit: (dateString) => ({
    type: actiontypes.LOAD_RACES_INIT,
    payload: dateString,
  }),
  loadRacesSuccess: (races) => ({
    type: actiontypes.LOAD_RACES_SUCCESS,
    payload: races,
  }),
  selectCourse: (course) => ({
    type: actiontypes.COURSE_SELECTED,
    payload: course,
  }),
  loadHorsesInit: (date, rid) => ({
    type: actiontypes.LOAD_HORSES_INIT,
    payload: { date, rid },
  }),
  loadHorsesSuccess: (horses, changes) => ({
    type: actiontypes.LOAD_HORSES_SUCCESS,
    payload: { horses, changes },
  }),
  actionFailure: (error) => ({
    type: actiontypes.ACTION_FAILURE,
    payload: error,
  }),
  selectHorse: (id, name) => ({
    type: actiontypes.SELECT_HORSE,
    payload: { id, name },
  }),
};

const defaultState = {
  currentDate: '',
  racings: [],
  horses: [],
  changes: [],
  currentPlace: '',
  currentHorseId: 0,
  currentHorse: '',
  currentRid: null,
  error: '',
  loading: false,
};

const racingReducer = (state = defaultState, action) => {

  state = { ...state, loading: false }
  switch (action.type) {
    case actiontypes.LOAD_RACES_INIT:
      return {
        ...defaultState,
        currentDate: action.payload,
        loading: true,
      };
    case actiontypes.LOAD_RACES_SUCCESS:
      return {
        ...state,
        racings: action.payload,
      };
    case actiontypes.COURSE_SELECTED:
      return {
        ...state,
        currentPlace: action.payload,
        horses: [],
        changes: [],
        currentHorseId: 0,
        currentHorse: '',
        currentRid: null,
      };
    case actiontypes.LOAD_HORSES_INIT:
      return {
        ...state,
        currentRid: action.payload.rid,
        horses: [],
        changes: [],
        currentHorseId: 0,
        currentHorse: '',
        loading: true
      };
    case actiontypes.LOAD_HORSES_SUCCESS:
      return {
        ...state,
        horses: action.payload.horses,
        changes: action.payload.changes,
      };
    case actiontypes.ACTION_FAILURE:
      return {
        ...state,
        error: action.payload,
        racings: [],
        horses: [],
        changes: [],
      };
    case actiontypes.SELECT_HORSE:
      return {
        ...state,
        currentHorseId: action.payload.id === state.currentHorseId ? 0 : action.payload.id,
        currentHorse: action.payload.name,
        horses: Immutable.setSelectedObjectInArray(state.horses, 'key', action.payload.id, getNumberSelectedHorses(state))
      };
    default:
      return state;
  }
};

const getNumberSelectedHorses = (state) => {
  return state.horses.filter(x => x.selected > -1).length;
};

export const getPlaces = (state) => {
  return state.racings.racings.length === 0 ? [] : [...new Set(state.racings.racings.map((x) => (x.course)))].sort();
};

export const getTimes = (state) => {
  return state.racings.racings.length === 0 ? [] : [...new Set(state.racings.racings
    .filter((x) => x.course === state.racings.currentPlace)
    .map(({ time, rid }) => ({ time, rid })))].sort();
};

export const getRacings = state => {
  return state.racings.racings.filter(x => x.course === state.racings.currentPlace && x.time === state.racings.currentTime);
}
export const getSelectedHorses = state => {
  return state.racings.horses.filter(x => x.selected > -1).map(({ key, selected, horseName }) => ({ key, selected, horseName }));
}
export const getSelectedHorsesNames = createSelector([getSelectedHorses], (horses) => {
  return horses.map(({ horseName }) => (horseName));
});
export const getChanges = state => {
  return state.racings.changes;
}
export const selectChanges = createSelector([getSelectedHorses, getChanges], (horses, changes) => {
  if (horses.length === 1) return changes.map(x => [x.dt, x[`d_${horses[0].key}`]]);
  if (horses.length === 2) return changes.map(x => [x.dt, x[`d_${horses[0].key}`], x[`d_${horses[1].key}`]]);
  if (horses.length === 3) return changes.map(x => [x.dt, x[`d_${horses[0].key}`], x[`d_${horses[1].key}`], x[`d_${horses[2].key}`]]);
  if (horses.length === 4) return changes.map(x => [x.dt, x[`d_${horses[0].key}`], x[`d_${horses[1].key}`], x[`d_${horses[2].key}`], x[`d_${horses[3].key}`]]);
  if (horses.length === 5) return changes.map(x => [x.dt, x[`d_${horses[0].key}`], x[`d_${horses[1].key}`], x[`d_${horses[2].key}`], x[`d_${horses[3].key}`], x[`d_${horses[4].key}`]]);
  return []
});

export const selectPrices = createSelector([getSelectedHorses, getChanges], (horses, changes) => {
  if (horses.length === 1) return changes.map(x => [x.dt, x[`p_${horses[0].key}`]]);
  if (horses.length === 2) return changes.map(x => [x.dt, x[`p_${horses[0].key}`], x[`p_${horses[1].key}`]]);
  if (horses.length === 3) return changes.map(x => [x.dt, x[`p_${horses[0].key}`], x[`p_${horses[1].key}`], x[`p_${horses[2].key}`]]);
  if (horses.length === 4) return changes.map(x => [x.dt, x[`p_${horses[0].key}`], x[`p_${horses[1].key}`], x[`p_${horses[2].key}`], x[`p_${horses[3].key}`]]);
  if (horses.length === 5) return changes.map(x => [x.dt, x[`p_${horses[0].key}`], x[`p_${horses[1].key}`], x[`p_${horses[2].key}`], x[`p_${horses[3].key}`], x[`p_${horses[4].key}`]]);
  return []
});

export default racingReducer;