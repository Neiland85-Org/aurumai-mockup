import React from "react";

interface Props {
  machineId: string;
  machineType: string;
  site: string;
  status: string;
  onClick?: () => void;
}

const MachineCard: React.FC<Props> = ({ machineId, machineType, site, status, onClick }) => {
  const statusColor = status === "operational" ? "text-green-400" : "text-red-400";

  return (
    <div
      onClick={onClick}
      className="cursor-pointer bg-gray-800 p-6 rounded-xl border border-gray-700
        hover:border-yellow-600 transition-all hover:shadow-lg"
    >
      <div className="flex justify-between items-start mb-3">
        <h2 className="text-xl font-bold text-white">{machineId}</h2>
        <span className={`text-sm font-semibold ${statusColor}`}>{status}</span>
      </div>
      <p className="text-sm text-gray-400 mb-1">{machineType.replace("_", " ")}</p>
      <p className="text-xs text-gray-500">{site}</p>
    </div>
  );
};

export default MachineCard;
