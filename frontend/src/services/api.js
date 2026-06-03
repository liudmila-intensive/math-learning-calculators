import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 60000,
});

export async function simplifyExpression(expression) {
  const payload =
    typeof expression === "string" ? { expression } : expression;
  const response = await API.post("/simplify", payload);
  return response.data;
}

export async function solveSimplex(payload) {
  const response = await API.post("/simplex", payload);
  return response.data;
}

export async function solveSimplexAlgebraic(payload) {
  const response = await API.post("/simplex-algebraic", payload);
  return response.data;
}

export async function solveTransport(payload) {
  const response = await API.post("/transport", payload);
  return response.data;
}

export async function solveLinearSystem(payload) {
  const response = await API.post("/linear-system", payload);
  return response.data;
}

export async function solveEquation(payload) {
  const response = await API.post("/equation", payload);
  return response.data;
}

async function downloadDocx(path, payload, filename) {
  const response = await API.post(path, payload, { responseType: "blob" });
  const url = window.URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export function downloadSimplifyDocx(payload) {
  return downloadDocx("/simplify/docx", payload, "simplify_solution.docx");
}

export function downloadEquationDocx(payload) {
  return downloadDocx("/equation/docx", payload, "equation_solution.docx");
}

export function downloadSimplexDocx(payload) {
  return downloadDocx("/simplex/docx", payload, "simplex_solution.docx");
}

export function downloadSimplexAlgebraicDocx(payload) {
  return downloadDocx(
    "/simplex-algebraic/docx",
    payload,
    "simplex_algebraic_solution.docx"
  );
}

export function downloadTransportDocx(payload) {
  return downloadDocx("/transport/docx", payload, "transport_solution.docx");
}
