import { useState, useEffect, ReactElement } from 'react';
import Link from 'next/link';
import { getESG, getMachines } from '../lib/api';
import MetricCard from '../components/MetricCard';
import { useToast } from '@/components/Toast';
import { getErrorMessage } from '@/types/errors';
import type { Machine, ESGData } from '@/types';

export default function ESGPage(): ReactElement {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [selectedMachine, setSelectedMachine] = useState<string>('');
  const [esgData, setEsgData] = useState<ESGData | null>(null);
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

  // Fetch ESG data at intervals
  useEffect(() => {
    // Don't fetch if no machine selected
    if (!selectedMachine) return;

    let isMounted = true;
    let interval: NodeJS.Timeout;

    const fetchESGData = async (): Promise<void> => {
      try {
        const result = await getESG(selectedMachine);

        if (!isMounted) return;

        if (result.ok) {
          setEsgData(result.value);
          setError(null);
        } else {
          const failure = result as { ok: false; error: unknown };
          const errorMsg = getErrorMessage(failure.error);
          setError(errorMsg);
          console.error('Error fetching ESG:', failure.error);
        }
      } catch (err) {
        if (!isMounted) return;
        const errorMsg = getErrorMessage(err);
        setError(errorMsg);
        console.error('Unexpected error fetching ESG:', err);
      }
    };

    // Fetch immediately
    fetchESGData();

    // Set up interval
    interval = setInterval(fetchESGData, 5000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [selectedMachine]);

  return (
    <div className="min-h-screen p-8">
      <div className="mb-6">
        <Link href="/" className="text-green-600 hover:underline">
          ← Back to Overview
        </Link>
      </div>

      <h1 className="text-3xl font-bold text-green-600 mb-6">ESG / Carbon Monitoring</h1>

      {error && (
        <div className="mb-6 p-4 bg-yellow-900 border border-yellow-700 rounded-lg text-yellow-100">
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mb-4"></div>
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

          {esgData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                label="Instant CO₂eq"
                value={esgData.instant_co2eq_kg.toFixed(2)}
                unit="kg"
                color="text-green-400"
              />
              <MetricCard
                label="Total CO₂eq"
                value={esgData.cumulative_co2eq_kg.toFixed(2)}
                unit="kg"
                color="text-green-400"
              />
              <MetricCard
                label="Fuel Rate"
                value={esgData.fuel_rate_lh ? esgData.fuel_rate_lh.toFixed(2) : 'N/A'}
                unit="l/h"
              />
              <MetricCard
                label="Power"
                value={esgData.kwh ? esgData.kwh.toFixed(2) : 'N/A'}
                unit="kWh"
              />
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700 mb-8">
              <p className="text-gray-400">Loading ESG data...</p>
            </div>
          )}

          <div className="mt-8 bg-gray-800 p-6 rounded-xl border border-gray-700">
            <h3 className="text-xl mb-4">Emission Scope</h3>
            <p className="text-gray-400">
              Current emissions are classified as{' '}
              <span className="text-green-400 font-semibold">{esgData?.scope || 'N/A'}</span>
            </p>
          </div>
        </>
      )}
    </div>
  );
}
