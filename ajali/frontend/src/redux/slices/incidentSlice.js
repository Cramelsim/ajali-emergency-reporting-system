import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { toast } from 'react-toastify';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const fetchIncidents = createAsyncThunk(
  'incidents/fetchIncidents',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const params = new URLSearchParams(filters).toString();
      const response = await axios.get(`${API_URL}/incidents/?${params}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch incidents');
    }
  }
);

export const fetchIncident = createAsyncThunk(
  'incidents/fetchIncident',
  async (id, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/incidents/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch incident');
    }
  }
);

export const createIncident = createAsyncThunk(
  'incidents/createIncident',
  async (formData, { getState, rejectWithValue }) => {
    try {
      const token = getState().auth.token;
      const response = await axios.post(`${API_URL}/incidents/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      toast.success('Incident reported successfully');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to create incident');
    }
  }
);

export const updateIncident = createAsyncThunk(
  'incidents/updateIncident',
  async ({ id, data }, { getState, rejectWithValue }) => {
    try {
      const token = getState().auth.token;
      const response = await axios.put(`${API_URL}/incidents/${id}`, data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success('Incident updated successfully');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to update incident');
    }
  }
);

export const deleteIncident = createAsyncThunk(
  'incidents/deleteIncident',
  async (id, { getState, rejectWithValue }) => {
    try {
      const token = getState().auth.token;
      await axios.delete(`${API_URL}/incidents/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success('Incident deleted successfully');
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to delete incident');
    }
  }
);

export const addMedia = createAsyncThunk(
  'incidents/addMedia',
  async ({ incidentId, file }, { getState, rejectWithValue }) => {
    try {
      const token = getState().auth.token;
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(
        `${API_URL}/incidents/${incidentId}/media`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      toast.success('Media added successfully');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to add media');
    }
  }
);

export const deleteMedia = createAsyncThunk(
  'incidents/deleteMedia',
  async (mediaId, { getState, rejectWithValue }) => {
    try {
      const token = getState().auth.token;
      await axios.delete(`${API_URL}/incidents/media/${mediaId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success('Media deleted successfully');
      return mediaId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to delete media');
    }
  }
);

export const fetchUserIncidents = createAsyncThunk(
  'incidents/fetchUserIncidents',
  async (_, { getState, rejectWithValue }) => {
    try {
      const token = getState().auth.token;
      const response = await axios.get(`${API_URL}/incidents/user/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch user incidents');
    }
  }
);

const incidentSlice = createSlice({
  name: 'incidents',
  initialState: {
    incidents: [],
    currentIncident: null,
    userIncidents: [],
    loading: false,
    error: null,
    filters: {
      status: '',
      type: '',
      severity: '',
    },
  },
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        status: '',
        type: '',
        severity: '',
      };
    },
    clearCurrentIncident: (state) => {
      state.currentIncident = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Incidents
      .addCase(fetchIncidents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchIncidents.fulfilled, (state, action) => {
        state.loading = false;
        state.incidents = action.payload.incidents;
      })
      .addCase(fetchIncidents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch Single Incident
      .addCase(fetchIncident.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchIncident.fulfilled, (state, action) => {
        state.loading = false;
        state.currentIncident = action.payload.incident;
      })
      .addCase(fetchIncident.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Create Incident
      .addCase(createIncident.fulfilled, (state, action) => {
        state.incidents.unshift(action.payload.incident);
      })
      // Update Incident
      .addCase(updateIncident.fulfilled, (state, action) => {
        const index = state.incidents.findIndex(i => i.id === action.payload.incident.id);
        if (index !== -1) {
          state.incidents[index] = action.payload.incident;
        }
        if (state.currentIncident?.id === action.payload.incident.id) {
          state.currentIncident = action.payload.incident;
        }
      })
      // Delete Incident
      .addCase(deleteIncident.fulfilled, (state, action) => {
        state.incidents = state.incidents.filter(i => i.id !== action.payload);
        if (state.currentIncident?.id === action.payload) {
          state.currentIncident = null;
        }
        state.userIncidents = state.userIncidents.filter(i => i.id !== action.payload);
      })
      // Add Media
      .addCase(addMedia.fulfilled, (state, action) => {
        if (state.currentIncident) {
          state.currentIncident.media_files.push(action.payload.media);
        }
      })
      // Delete Media
      .addCase(deleteMedia.fulfilled, (state, action) => {
        if (state.currentIncident) {
          state.currentIncident.media_files = state.currentIncident.media_files.filter(
            m => m.id !== action.payload
          );
        }
      })
      // Fetch User Incidents
      .addCase(fetchUserIncidents.fulfilled, (state, action) => {
        state.userIncidents = action.payload.incidents;
      });
  },
});

export const { setFilters, clearFilters, clearCurrentIncident } = incidentSlice.actions;
export default incidentSlice.reducer;