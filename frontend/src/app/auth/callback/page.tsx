// src/app/auth/callback/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import api from '@/lib/axios';

export default function AuthCallback() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState('Processing...');

  useEffect(() => {
    const code = searchParams.get('code');

    const stateProvider = searchParams.get('state');
    const storedProvider = typeof window !== 'undefined' ? localStorage.getItem('auth_provider') : null;
    const provider = (stateProvider === 'google' || stateProvider === 'github')
      ? stateProvider
      : (storedProvider === 'google' || storedProvider === 'github')
        ? storedProvider
        : 'github';

    if (!code) {
      setStatus('Missing OAuth code in callback URL.');
      return;
    }

    const endpoint = provider === 'github' ? '/api/auth/github/' : '/api/auth/google/';

    api.post(endpoint, { code })
      .then((res) => {
        setStatus('Login success!');
        localStorage.setItem('access_token', res.data.access);
        localStorage.setItem('refresh_token', res.data.refresh);
        setTimeout(() => router.push('/'), 1000);
      })
      .catch((err) => {
        const message = err.response?.data ? JSON.stringify(err.response.data) : String(err.message || err);
        setStatus('Error: ' + message);
        console.error(err);
      });
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <h2 className="text-xl">{status}</h2>
    </div>
  );
}