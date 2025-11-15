import type { ReactElement } from 'react';

interface LineChartProps {
  data: number[];
  color?: string;
  height?: number;
}

interface Point {
  x: number;
  y: number;
}

export default function LineChart({
  data,
  color = '#cc7f32',
  height = 100,
}: LineChartProps): ReactElement {
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-24 bg-gray-800 rounded flex items-center justify-center text-gray-500">
        No data
      </div>
    );
  }

  const maxVal: number = Math.max(...data);
  const minVal: number = Math.min(...data);
  const range: number = maxVal - minVal || 1;

  const points: Point[] = data.map((v, i) => ({
    x: (i / (data.length - 1 || 1)) * 100,
    y: ((v - minVal) / range) * 100,
  }));

  const svgPath: string = points
    .map((p, i) => ` ${i === 0 ? 'M' : 'L'} ${p.x},${100 - p.y}`)
    .join(' ');

  return (
    <div className="w-full bg-gray-800 p-4 rounded-xl border border-gray-700">
      <svg
        viewBox="0 0 100 100"
        className="w-full"
        style={{ height: `${height}px` }}
        preserveAspectRatio="none"
      >
        <path
          d={svgPath}
          fill="none"
          stroke={color}
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
    </div>
  );
}
