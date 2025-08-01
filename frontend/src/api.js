// frontend/src/api.js
import axios from "axios";

// If you added "proxy": "http://127.0.0.1:8000" to package.json, keep this blank:
// const API_BASE = "";
const API_BASE = "http://localhost:8000";

export const fetchRecommendations = async (n = 5) => {
  const { data } = await axios.get(`${API_BASE}/recommendations?n=${n}`);
  return data;
};

export const fetchTop5 = async () => {
  const { data } = await axios.get(`${API_BASE}/screen/top5`);
  return data;
};

export const fetchPortfolioDaily = async (companies) => {
  const { data } = await axios.post(`${API_BASE}/portfolio/daily`, { companies });
  return data;
};

export const fetchStockData = async (ticker) => {
  const { data } = await axios.get(`${API_BASE}/stocks/${ticker}`);
  return data;
};

export const addExpense = async (expense) => {
  return await axios.post("/expenses", expense);
};

