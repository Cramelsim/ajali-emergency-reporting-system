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
