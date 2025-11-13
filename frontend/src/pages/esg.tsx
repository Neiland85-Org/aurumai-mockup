import { useState, useEffect } from "react";
import { getESG, getMachines } from "../lib/api";
import MetricCard from "../components/MetricCard";

export default function ESGPage() {
  const [machines, setMachines] = useState([]);
  const [selectedMachine, setSelectedMachine] = useState("TRUCK-21");
  const [esgData, setEsgData] = useState<any>(null);

  useEffect(() => {
    async function fetch() {
      const data = await getMachines();
      setMachines(data);
    }
    fetch();
  }, []);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await getESG(selectedMachine);
        setEsgData(data);
      } catch (error) {
        console.error("Error fetching ESG:", error);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [selectedMachine]);

  return (
    <div className="min-h-screen p-8">
      <div className="mb-6">
        <a href="/" className="text-green-600 hover:underline">← Back to Overview</a>
      </div>

      <h1 className="text-3xl font-bold text-green-600 mb-6">ESG / Carbon Monitoring</h1>

      <div className="mb-6">
        <label className="text-gray-400 block mb-2">Select Machine:</label>
        <select
          value={selectedMachine}
          onChange={(e) => setSelectedMachine(e.target.value)}
          className="bg-gray-800 text-white px-4 py-2 rounded border border-gray-700"
        >
          {machines.map((m: any) => (
            <option key={m.machine_id} value={m.machine_id}>{m.machine_id}</option>
          ))}
        </select>
      </div>

      {esgData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard label="Instant CO₂eq" value={esgData.co2eq_instant.toFixed(2)} unit="kg" color="text-green-400" />
          <MetricCard label="Total CO₂eq" value={esgData.co2eq_total.toFixed(2)} unit="kg" color="text-green-400" />
          <MetricCard label="Fuel Rate" value={esgData.fuel_rate_lh ? esgData.fuel_rate_lh.toFixed(2) : "N/A"} unit="l/h" />
          <MetricCard label="Power" value={esgData.kwh ? esgData.kwh.toFixed(2) : "N/A"} unit="kWh" />
        </div>
      )}

      <div className="mt-8 bg-gray-800 p-6 rounded-xl border border-gray-700">
        <h3 className="text-xl mb-4">Emission Scope</h3>
        <p className="text-gray-400">
          Current emissions are classified as <span className="text-green-400 font-semibold">{esgData?.scope || "N/A"}</span>
        </p>
      </div>
    </div>
  );
}
