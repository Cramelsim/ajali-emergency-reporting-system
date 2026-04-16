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