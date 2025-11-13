import { useEffect, useState } from "react";
import MachineCard from "../components/MachineCard";
import { getMachines, type Machine } from "../lib/api";

export default function HomePage() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getMachines();
        setMachines(data || []);
      } catch (error) {
        console.error("Error fetching machines:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-2 text-yellow-600">
        AurumAI Platform
      </h1>
      <p className="text-gray-400 mb-8">
        Industrial IoT Monitoring & Predictive Maintenance
      </p>

      <h2 className="text-2xl mb-4 text-gray-300">Machines Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {machines.map((m: Machine) => (
          <MachineCard
            key={m.machine_id}
            machineId={m.machine_id}
            machineType={m.machine_type}
            site={m.site}
            status={m.status}
          />
        ))}
      </div>

      <div className="flex gap-4 mt-8">
        <a
          href="/predictive"
          className="bg-yellow-600 hover:bg-yellow-700 px-6 py-3 rounded-lg font-semibold"
        >
          Predictive Maintenance
        </a>
        <a
          href="/esg"
          className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-semibold"
        >
          ESG / Carbon
        </a>
      </div>
    </div>
  );
}
