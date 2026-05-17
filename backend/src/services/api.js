import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export async function simplifyExpression(expression) {
  const response = await API.post("/simplify", { expression });
  return response.data;
}

export async function solveSimplex(payload) {
  const response = await API.post("/simplex", payload);
  return response.data;
}