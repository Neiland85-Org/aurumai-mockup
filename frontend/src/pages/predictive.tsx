import { useEffect, useState } from "react";
import { getPrediction, getMachines } from "../lib/api";
import MetricCard from "../components/MetricCard";
import LineChart from "../components/LineChart";

export default function PredictivePage() {
  const [machines, setMachines] = useState([]);
  const [selectedMachine, setSelectedMachine] = useState("TRUCK-21");
  const [prediction, setPrediction] = useState<any>(null);
  const [history, setHistory] = useState<number[]>([]);

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
        const res = await getPrediction(selectedMachine);
        setPrediction(res);
        setHistory((prev) => [...prev.slice(-50), res.risk_score * 100]);
      } catch (error) {
        console.error("Error fetching prediction:", error);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [selectedMachine]);

  const riskColor = prediction && prediction.risk_score > 0.6 ? "text-red-500" : prediction && prediction.risk_score > 0.3 ? "text-yellow-500" : "text-green-400";

  return (
    <div className="min-h-screen p-8">
      <div className="mb-6">
        <a href="/" className="text-yellow-600 hover:underline">← Back to Overview</a>
      </div>

      <h1 className="text-3xl font-bold text-yellow-600 mb-6">Predictive Maintenance</h1>

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

      {prediction && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <MetricCard label="Failure Risk" value={(prediction.risk_score * 100).toFixed(1)} unit="%" color={riskColor} />
          <MetricCard label="Failure Probability" value={(prediction.failure_probability * 100).toFixed(1)} unit="%" color={riskColor} />
          <MetricCard label="Next Maintenance" value={prediction.next_maintenance_hours || "N/A"} unit="hrs" />
        </div>
      )}

      <div className="mt-8">
        <h3 className="text-xl text-gray-300 mb-4">Risk Trend</h3>
        <LineChart data={history} color="#cc7f32" height={150} />
      </div>
    </div>
  );
}
