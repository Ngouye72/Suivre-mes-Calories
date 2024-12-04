import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Authentification
export const login = async (credentials) => {
  const response = await api.post('/login', credentials);
  await AsyncStorage.setItem('token', response.data.token);
  return response.data;
};

export const register = async (userData) => {
  const response = await api.post('/register', userData);
  return response.data;
};

// Journal alimentaire
export const getFoodEntries = async () => {
  const response = await api.get('/food-entries');
  return response.data;
};

export const addFoodEntry = async (entry) => {
  const response = await api.post('/food-entries', entry);
  return response.data;
};

// Scan de code-barres
export const searchFoodByBarcode = async (barcode) => {
  const response = await api.get(`/foods/barcode/${barcode}`);
  return response.data;
};

// Profil utilisateur
export const getUserProfile = async () => {
  const response = await api.get('/user/profile');
  return response.data;
};

export const updateUserProfile = async (profileData) => {
  const response = await api.put('/user/profile', profileData);
  return response.data;
};

// Statistiques
export const getDailyCalories = async () => {
  const response = await api.get('/stats/daily');
  return response.data;
};

export const getWeeklyProgress = async () => {
  const response = await api.get('/stats/weekly');
  return response.data;
};

export default api;
