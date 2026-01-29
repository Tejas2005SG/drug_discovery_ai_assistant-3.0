import axios from "axios";

export const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_NODEJS_BACKENDURL || "http://localhost:5000/api",
  withCredentials: true,
});
