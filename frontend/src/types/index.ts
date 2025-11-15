/**
 * Type definitions for AurumAI Platform Frontend
 * Centralized types for API responses, domain models, and components
 */

/**
 * Machine entity
 */
export interface Machine {
  machine_id: string;
  machine_type: string;
  site: string;
  status: 'operational' | 'offline' | 'error';
  location?: string;
}

/**
 * Prediction result from ML model
 */
export interface Prediction {
  machine_id: string;
  timestamp: string;
  risk_score: number;
  failure_probability: number;
  maintenance_hours: number;
  failure_type?: string | null;
  confidence?: number;
  model_version?: string;
}

/**
 * ESG/Carbon emission data
 */
export interface ESGData {
  machine_id: string;
  timestamp: string;
  instant_co2eq_kg: number;
  cumulative_co2eq_kg: number;
  fuel_rate_lh?: number;
  kwh?: number;
  co2_ppm?: number;
  scope?: 'scope1' | 'scope2' | string;
  breakdown?: Record<string, number>;
  factors_used?: Record<string, number>;
}

/**
 * Machine metrics (combined view)
 */
export interface MachineMetrics {
  machine_id: string;
  machine_type: string;
  latest_measurement?: {
    timestamp: string;
    metrics: Record<string, number>;
  };
  latest_prediction?: Prediction;
  latest_esg?: ESGData;
}

/**
 * API Error response
 */
export interface APIError {
  detail: string;
  status: number;
}

/**
 * Generic API response wrapper
 */
export interface APIResponse<T> {
  data?: T;
  error?: APIError;
}
