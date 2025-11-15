import type { Machine, Prediction, ESGData, MachineMetrics } from '@/types';
import {
  APIError,
  NetworkError,
  TimeoutError,
  AbortError,
  Result,
  ok,
  err,
  withRetry,
  createAbortable,
  isRetryable,
  type RetryConfig,
} from '@/types/errors';

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

// Request timeout (ms)
const REQUEST_TIMEOUT = 30000;

// Default retry config
const DEFAULT_RETRY_CONFIG: Partial<RetryConfig> = {
  maxAttempts: 3,
  initialDelayMs: 100,
  maxDelayMs: 5000,
  backoffMultiplier: 2,
};

/**
 * Parse error response from API
 */
function parseErrorResponse(response: Response): APIError {
  const status = response.status;
  const statusText = response.statusText || 'Unknown error';

  // Determine error message based on status code
  let message = statusText;
  let code: string | undefined;

  switch (status) {
    case 400:
      code = 'VALIDATION_ERROR';
      message = 'Invalid request data';
      break;
    case 401:
      code = 'UNAUTHORIZED';
      message = 'Unauthorized access';
      break;
    case 403:
      code = 'FORBIDDEN';
      message = 'Access forbidden';
      break;
    case 404:
      code = 'NOT_FOUND';
      message = 'Resource not found';
      break;
    case 409:
      code = 'CONFLICT';
      message = 'Resource conflict';
      break;
    case 429:
      code = 'RATE_LIMITED';
      message = 'Too many requests. Please try again later.';
      break;
    case 500:
      code = 'INTERNAL_SERVER_ERROR';
      message = 'Server error. Please try again later.';
      break;
    case 502:
      code = 'BAD_GATEWAY';
      message = 'Service temporarily unavailable';
      break;
    case 503:
      code = 'SERVICE_UNAVAILABLE';
      message = 'Service temporarily unavailable';
      break;
    default:
      code = 'HTTP_ERROR';
  }

  return new APIError(status, message, code);
}

/**
 * Fetch JSON data from API endpoint with error handling
 */
export async function fetchJSON<T>(
  path: string,
  options?: {
    signal?: AbortSignal;
    timeout?: number;
    retryConfig?: Partial<RetryConfig>;
  }
): Promise<Result<T, APIError | NetworkError | TimeoutError | AbortError>> {
  const timeout = options?.timeout ?? REQUEST_TIMEOUT;
  const retryConfig = options?.retryConfig ?? DEFAULT_RETRY_CONFIG;

  return withRetry(
    async () => {
      // Create abort controller if not provided
      const controller = options?.signal ? undefined : new AbortController();
      const signal = options?.signal ?? controller?.signal;

      // Set timeout
      let timeoutId: NodeJS.Timeout | undefined;
      if (timeout > 0) {
        timeoutId = setTimeout(() => {
          controller?.abort();
        }, timeout);
      }

      try {
        const url = `${API_BASE}${path}`;
        const res = await createAbortable(
          fetch(url, {
            signal,
            headers: {
              'Content-Type': 'application/json',
            },
          }),
          signal!
        );

        // Check response status
        if (!res.ok) {
          // Try to parse error details from response body
          try {
            const errorBody = await res.json();
            const apiError = new APIError(
              res.status,
              parseErrorResponse(res).message,
              parseErrorResponse(res).code,
              errorBody
            );
            return err(apiError);
          } catch {
            return err(parseErrorResponse(res));
          }
        }

        // Parse response body
        try {
          const data = (await res.json()) as T;
          return ok(data);
        } catch (parseError) {
          return err(new NetworkError('Failed to parse response', parseError as Error));
        }
      } catch (fetchError) {
        if (fetchError instanceof Error) {
          if (fetchError.name === 'AbortError' || fetchError instanceof AbortError) {
            return err(new AbortError());
          }
          if (fetchError.message.includes('timeout')) {
            return err(new TimeoutError());
          }
        }
        return err(new NetworkError('Network request failed', fetchError as Error));
      } finally {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
      }
    },
    {
      ...retryConfig,
      shouldRetry: (error, attempt) => {
        return isRetryable(error) && attempt < (retryConfig.maxAttempts ?? 3);
      },
    }
  );
}

/**
 * Get all machines
 */
export async function getMachines(options?: {
  signal?: AbortSignal;
}): Promise<Result<Machine[], APIError | NetworkError | TimeoutError | AbortError>> {
  return fetchJSON<Machine[]>('/machines/', options);
}

/**
 * Get detailed metrics for a specific machine
 */
export async function getMachineMetrics(
  machineId: string,
  options?: { signal?: AbortSignal }
): Promise<Result<MachineMetrics, APIError | NetworkError | TimeoutError | AbortError>> {
  return fetchJSON<MachineMetrics>(`/machines/${machineId}/metrics`, options);
}

/**
 * Get predictive analysis for a machine
 */
export async function getPrediction(
  machineId: string,
  options?: { signal?: AbortSignal }
): Promise<Result<Prediction, APIError | NetworkError | TimeoutError | AbortError>> {
  return fetchJSON<Prediction>(`/predict?machine_id=${machineId}`, options);
}

/**
 * Get current ESG/carbon data for a machine
 */
export async function getESG(
  machineId: string,
  options?: { signal?: AbortSignal }
): Promise<Result<ESGData, APIError | NetworkError | TimeoutError | AbortError>> {
  return fetchJSON<ESGData>(`/esg/current?machine_id=${machineId}`, options);
}

/**
 * Get ESG summary across all machines
 */
export async function getESGSummary(options?: {
  signal?: AbortSignal;
}): Promise<Result<ESGData[], APIError | NetworkError | TimeoutError | AbortError>> {
  return fetchJSON<ESGData[]>('/esg/summary', options);
}
