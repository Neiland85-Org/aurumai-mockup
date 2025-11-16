import { useEffect, useState, ReactElement, useCallback } from 'react';
import { getPrediction, getMachines } from '../lib/api';
import MetricCard from '../components/MetricCard';
import LineChart from '../components/LineChart';
import { useToast } from '@/components/Toast';
import { getErrorMessage } from '@/types/errors';
import type { Machine, Prediction } from '@/types';

export default function PredictivePage(): ReactElement {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [selectedMachine, setSelectedMachine] = useState<string>('');
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [history, setHistory] = useState<number[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { error: showError } = useToast();

  // Fetch machines on mount
  useEffect(() => {
    let cancelled = false;

    const fetchMachines = async (): Promise<void> => {
      try {
        const result = await getMachines();

        if (cancelled) return;

        if (result.ok) {
          setMachines(result.value);
          // Auto-select first machine if none selected
          if (result.value.length > 0 && !selectedMachine) {
            setSelectedMachine(result.value[0].machine_id);
          }
        } else {
          const failure = result as { ok: false; error: unknown };
          const errorMsg = getErrorMessage(failure.error);
          setError(errorMsg);
          showError(errorMsg);
          console.error('Error fetching machines:', failure.error);
        }
      } catch (err) {
        if (cancelled) return;
        const errorMsg = getErrorMessage(err);
        setError(errorMsg);
        console.error('Unexpected error fetching machines:', err);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchMachines();

    return () => {
      cancelled = true;
    };
  }, [showError]);

  // Fetch prediction at intervals
  useEffect(() => {
    // Don't fetch if no machine selected
    if (!selectedMachine) return;

    let isMounted = true;
    let interval: NodeJS.Timeout;

    const fetchPrediction = async (): Promise<void> => {
      try {
        const result = await getPrediction(selectedMachine);

        if (!isMounted) return;

        if (result.ok) {
          setPrediction(result.value);
          setHistory((prev) => [...prev.slice(-50), result.value.risk_score * 100]);
          setError(null);
        } else {
          const failure = result as { ok: false; error: unknown };
          const errorMsg = getErrorMessage(failure.error);
          setError(errorMsg);
          console.error('Error fetching prediction:', failure.error);
        }
      } catch (err) {
        if (!isMounted) return;
        const errorMsg = getErrorMessage(err);
        setError(errorMsg);
        console.error('Unexpected error fetching prediction:', err);
      }
    };

    // Fetch immediately
    fetchPrediction();

    // Set up interval
    interval = setInterval(fetchPrediction, 5000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [selectedMachine]);

  const riskColor: string =
    prediction && prediction.risk_score > 0.6
      ? 'text-red-500'
      : prediction && prediction.risk_score > 0.3
        ? 'text-yellow-500'
        : 'text-green-400';

  return (
    <div className="min-h-screen p-8">
      <div className="mb-6">
        <a href="/" className="text-yellow-600 hover:underline">
          ← Back to Overview
        </a>
      </div>

      <h1 className="text-3xl font-bold text-yellow-600 mb-6">Predictive Maintenance</h1>

      {error && (
        <div className="mb-6 p-4 bg-yellow-900 border border-yellow-700 rounded-lg text-yellow-100">
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-600 mb-4"></div>
          <p className="text-gray-400">Loading machines...</p>
        </div>
      ) : machines.length === 0 ? (
        <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
          <p className="text-gray-400">No machines available</p>
        </div>
      ) : (
        <>
          <div className="mb-6">
            <label className="text-gray-400 block mb-2">Select Machine:</label>
            <select
              value={selectedMachine}
              onChange={(e) => setSelectedMachine(e.target.value)}
              className="bg-gray-800 text-white px-4 py-2 rounded border border-gray-700"
            >
              {machines.map((m: Machine) => (
                <option key={m.machine_id} value={m.machine_id}>
                  {m.machine_id}
                </option>
              ))}
            </select>
          </div>

          {prediction ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <MetricCard
                label="Failure Risk"
                value={(prediction.risk_score * 100).toFixed(1)}
                unit="%"
                color={riskColor}
              />
              <MetricCard
                label="Failure Probability"
                value={(prediction.failure_probability * 100).toFixed(1)}
                unit="%"
                color={riskColor}
              />
              <MetricCard
                label="Next Maintenance"
                value={prediction.maintenance_hours || 'N/A'}
                unit="hrs"
              />
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700 mb-8">
              <p className="text-gray-400">Loading prediction data...</p>
            </div>
          )}

          <div className="mt-8">
            <h3 className="text-xl text-gray-300 mb-4">Risk Trend</h3>
            <LineChart data={history} color="#cc7f32" height={150} />
          </div>
        </>
      )}
    </div>
  );
}
