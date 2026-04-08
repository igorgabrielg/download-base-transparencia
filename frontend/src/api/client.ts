import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});
