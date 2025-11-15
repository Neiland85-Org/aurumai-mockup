import { useEffect, useState, ReactElement, useCallback } from 'react';
import MachineCard from '../components/MachineCard';
import { getMachines } from '../lib/api';
import { useToast } from '@/components/Toast';
import { getErrorMessage } from '@/types/errors';
import type { Machine } from '@/types';

export default function HomePage(): ReactElement {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { error: showError } = useToast();
  const abortControllerRef = new AbortController();

  const fetchData = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const result = await getMachines({ signal: abortControllerRef.signal });

      if (result.ok) {
        setMachines(result.value);
      } else {
        const failure = result as { ok: false; error: unknown };
        const errorMsg = getErrorMessage(failure.error);
        setError(errorMsg);
        showError(errorMsg);
        console.error('Error fetching machines:', failure.error);
      }
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      setError(errorMsg);
      showError(errorMsg);
      console.error('Unexpected error fetching machines:', err);
    } finally {
      setLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchData();

    // Cleanup: abort requests on unmount
    return () => {
      abortControllerRef.abort();
    };
  }, [fetchData]);

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-600 mb-4"></div>
          <p className="text-gray-400">Loading machines...</p>
        </div>
      </div>
    );
  }

  if (error && machines.length === 0) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 text-4xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Failed to load machines</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button
            onClick={fetchData}
            className="bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-2 px-6 rounded-lg transition"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-2 text-yellow-600">AurumAI Platform</h1>
      <p className="text-gray-400 mb-8">Industrial IoT Monitoring & Predictive Maintenance</p>

      {error && machines.length > 0 && (
        <div className="mb-6 p-4 bg-yellow-900 border border-yellow-700 rounded-lg text-yellow-100">
          <p>{error}</p>
        </div>
      )}

      <h2 className="text-2xl mb-4 text-gray-300">
        Machines Overview {machines.length > 0 && `(${machines.length})`}
      </h2>

      {machines.length === 0 ? (
        <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
          <p className="text-gray-400">No machines available</p>
        </div>
      ) : (
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
      )}

      <div className="flex gap-4 mt-8">
        <a
          href="/predictive"
          className="bg-yellow-600 hover:bg-yellow-700 px-6 py-3 rounded-lg font-semibold transition"
        >
          Predictive Maintenance
        </a>
        <a
          href="/esg"
          className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-semibold transition"
        >
          ESG / Carbon
        </a>
      </div>
    </div>
  );
}
