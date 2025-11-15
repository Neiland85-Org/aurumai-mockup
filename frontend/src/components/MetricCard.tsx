import type { ReactElement } from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  color?: string;
  unit?: string;
}

export default function MetricCard({ label, value, color, unit }: MetricCardProps): ReactElement {
  return (
    <div className="bg-gray-800 p-5 rounded-xl border border-gray-700">
      <h3 className="text-sm text-gray-400 mb-2">{label}</h3>
      <p className={`text-3xl font-bold ${color || 'text-white'}`}>
        {value}
        {unit && <span className="text-lg ml-1">{unit}</span>}
      </p>
    </div>
  );
}
