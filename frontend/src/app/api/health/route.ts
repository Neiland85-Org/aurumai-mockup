/**
 * Health check endpoint for Docker healthcheck
 * Returns 200 OK if the server is running
 */

import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'aurumai-frontend',
    },
    { status: 200 }
  );
}
