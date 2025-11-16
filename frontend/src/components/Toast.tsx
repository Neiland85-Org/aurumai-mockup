'use client';

import type { ReactElement } from 'react';
import { useEffect, useState } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

/**
 * Toast notification context (simplified - using state directly in component)
 * For production, consider using Context API or a state management library
 */

interface ToastProps {
  type: ToastType;
  message: string;
  onClose: () => void;
  duration?: number;
}

/**
 * Individual toast notification
 */
function Toast({ type, message, onClose, duration = 4000 }: ToastProps): ReactElement {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const bgColor = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    warning: 'bg-yellow-600',
    info: 'bg-blue-600',
  }[type];

  const icon = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  }[type];

  return (
    <div
      className={`${bgColor} text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-pulse`}
      role="alert"
    >
      <span className="text-lg font-bold">{icon}</span>
      <span>{message}</span>
      <button
        onClick={onClose}
        className="ml-auto text-lg hover:opacity-75 transition"
        aria-label="Close notification"
      >
        ×
      </button>
    </div>
  );
}

/**
 * Toast container - displays multiple toasts
 */
interface ToastContainerProps {
  toasts: ToastMessage[];
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps): ReactElement {
  return (
    <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50 pointer-events-none">
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <Toast
            type={toast.type}
            message={toast.message}
            onClose={() => onRemove(toast.id)}
            duration={toast.duration}
          />
        </div>
      ))}
    </div>
  );
}

/**
 * Hook for managing toasts
 */
export function useToast() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (message: string, type: ToastType = 'info', duration?: number): string => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: ToastMessage = { id, type, message, duration };
    setToasts((prev) => [...prev, newToast]);
    return id;
  };

  const removeToast = (id: string): void => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const success = (message: string, duration?: number): string =>
    addToast(message, 'success', duration);

  const error = (message: string, duration?: number): string =>
    addToast(message, 'error', duration);

  const warning = (message: string, duration?: number): string =>
    addToast(message, 'warning', duration);

  const info = (message: string, duration?: number): string => addToast(message, 'info', duration);

  return { toasts, addToast, removeToast, success, error, warning, info };
}
