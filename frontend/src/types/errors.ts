/**
 * Error handling types and utilities
 * Provides Result pattern, typed error responses, and recovery strategies
 */

/**
 * Result type - Either Success<T> or Failure<E>
 * Inspired by Rust's Result type
 */
export type Result<T, E = Error> = Success<T> | Failure<E>;

export interface Success<T> {
  ok: true;
  value: T;
}

export interface Failure<E = Error> {
  ok: false;
  error: E;
}

/**
 * Create success result
 */
export function ok<T>(value: T): Success<T> {
  return { ok: true, value };
}

/**
 * Create failure result
 */
export function err<E>(error: E): Failure<E> {
  return { ok: false, error };
}

/**
 * Map Result value
 */
export function mapResult<T, U, E>(result: Result<T, E>, fn: (value: T) => U): Result<U, E> {
  if (result.ok) {
    return ok(fn(result.value));
  }
  const failure = result as Failure<E>;
  return err(failure.error);
}

/**
 * Flat map Result
 */
export function flatMapResult<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => Result<U, E>
): Result<U, E> {
  if (result.ok) {
    return fn(result.value);
  }
  const failure = result as Failure<E>;
  return err(failure.error);
}

/**
 * API Error Response
 */
export interface APIErrorResponse {
  status: number;
  message: string;
  code?: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

/**
 * Typed error for API responses
 */
export class APIError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly code?: string,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'APIError';
  }

  toJSON(): APIErrorResponse {
    return {
      status: this.status,
      message: this.message,
      code: this.code,
      details: this.details,
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Network/Fetch Error
 */
export class NetworkError extends Error {
  constructor(
    message: string,
    public readonly originalError?: Error
  ) {
    super(message);
    this.name = 'NetworkError';
  }
}

/**
 * Validation Error
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public readonly fields?: Record<string, string[]>
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Timeout Error
 */
export class TimeoutError extends Error {
  constructor(message = 'Request timeout') {
    super(message);
    this.name = 'TimeoutError';
  }
}

/**
 * Abort Error
 */
export class AbortError extends Error {
  constructor(message = 'Request aborted') {
    super(message);
    this.name = 'AbortError';
  }
}

/**
 * Retry configuration
 */
export interface RetryConfig {
  maxAttempts: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
  shouldRetry: (error: Error, attempt: number) => boolean;
}

/**
 * Default retry configuration
 */
export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxAttempts: 3,
  initialDelayMs: 100,
  maxDelayMs: 5000,
  backoffMultiplier: 2,
  shouldRetry: (error: Error, attempt: number) => {
    // Don't retry validation errors or abort errors
    if (error instanceof ValidationError || error instanceof AbortError) {
      return false;
    }
    // Retry on network/timeout errors
    return attempt < 3;
  },
};

/**
 * Execute with exponential backoff retry
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  config: Partial<RetryConfig> = {}
): Promise<T> {
  const cfg = { ...DEFAULT_RETRY_CONFIG, ...config };
  let lastError: Error | null = null;
  let delay = cfg.initialDelayMs;

  for (let attempt = 1; attempt <= cfg.maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (!cfg.shouldRetry(lastError, attempt) || attempt === cfg.maxAttempts) {
        throw lastError;
      }

      // Wait before retrying with exponential backoff
      await new Promise((resolve) => setTimeout(resolve, delay));
      delay = Math.min(delay * cfg.backoffMultiplier, cfg.maxDelayMs);
    }
  }

  throw lastError || new Error('Retry failed');
}

/**
 * Create abortable promise
 */
export function createAbortable<T>(promise: Promise<T>, signal: AbortSignal): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) => {
      if (signal.aborted) {
        reject(new AbortError());
      }
      signal.addEventListener('abort', () => {
        reject(new AbortError());
      });
    }),
  ]);
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof APIError) {
    return error.message || 'API request failed';
  }

  if (error instanceof NetworkError) {
    return 'Network connection error. Please check your connection.';
  }

  if (error instanceof TimeoutError) {
    return 'Request timed out. Please try again.';
  }

  if (error instanceof ValidationError) {
    return error.message || 'Invalid input data';
  }

  if (error instanceof Error) {
    return error.message || 'An unexpected error occurred';
  }

  return 'An unexpected error occurred';
}

/**
 * Check if error is retryable
 */
export function isRetryable(error: Error): boolean {
  if (error instanceof ValidationError || error instanceof AbortError) {
    return false;
  }

  if (error instanceof APIError) {
    // Retry on 5xx errors, not 4xx
    return error.status >= 500;
  }

  if (error instanceof NetworkError || error instanceof TimeoutError) {
    return true;
  }

  return false;
}
