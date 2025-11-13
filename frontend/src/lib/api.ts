export const API_BASE = (process.env.NEXT_PUBLIC_API_BASE as string) || "http://localhost:8000";

export type Machine = {
  machine_id: string;
  machine_type: string;
  site: string;
  status: string;
};

export async function fetchJSON(path: string) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API Error ${res.status} ${res.statusText}`);
  return res.json();
}

export async function getMachines(): Promise<Machine[]> {
  const data = await fetchJSON("/machines/");
  if (!Array.isArray(data)) return [];
  // Normalize shape defensively
  return data.map((m: any) => ({
    machine_id: String(m.machine_id ?? m.id ?? ""),
    machine_type: String(m.machine_type ?? m.type ?? "unknown"),
    site: String(m.site ?? m.location ?? ""),
    status: String(m.status ?? "unknown"),
  }));
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

