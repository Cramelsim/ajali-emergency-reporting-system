import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import incidentReducer from './slices/incidentSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    incidents: incidentReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});