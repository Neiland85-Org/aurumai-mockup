import '../styles/globals.css';
import type { AppProps } from 'next/app';
import type { ReactElement } from 'react';
import { useState } from 'react';
import ErrorBoundary from '@/components/ErrorBoundary';
import { ToastContainer, useToast } from '@/components/Toast';

/**
 * Global app wrapper with error boundary and toast notifications
 */
function AppContent({ Component, pageProps }: AppProps): ReactElement {
  const { toasts, removeToast, error: showError } = useToast();

  // Handle unhandled promise rejections
  if (typeof window !== 'undefined') {
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      showError(event.reason?.message || 'An unexpected error occurred. Please refresh the page.');
    });
  }

  return (
    <>
      <Component {...pageProps} />
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </>
  );
}

export default function App(props: AppProps): ReactElement {
  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        console.error('App Error:', error, errorInfo);
      }}
    >
      <AppContent {...props} />
    </ErrorBoundary>
  );
}
