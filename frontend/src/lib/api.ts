export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function fetchJSON(path: string) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error("API Error");
  return res.json();
}

export async function getMachines() {
  return fetchJSON("/machines/");
}

export async function getMachineMetrics(machineId: string) {
  return fetchJSON(`/machines/${machineId}/metrics`);
}

export async function getPrediction(machineId: string) {
  return fetchJSON(`/predict?machine_id=${machineId}`);
}

export async function getESG(machineId: string) {
  return fetchJSON(`/esg/current?machine_id=${machineId}`);
}

export async function getESGSummary() {
  return fetchJSON("/esg/summary");
}
