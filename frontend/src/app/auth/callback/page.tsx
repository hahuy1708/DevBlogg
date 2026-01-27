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
   
    const provider = localStorage.getItem('auth_provider') || 'github'; 

    if (code) {
      const endpoint = provider === 'github' ? '/api/auth/github/' : '/api/auth/google/';
      
      api.post(endpoint, {
        code: code, 
      })
      .then((res) => {
        setStatus('Login success!');
        console.log('Backend Response:', res.data);
        localStorage.setItem('access_token', res.data.access);
        localStorage.setItem('refresh_token', res.data.refresh);
        setTimeout(() => router.push('/'), 2000);
      })
      .catch((err) => {
        setStatus('Error: ' + JSON.stringify(err.response?.data));
        console.error(err);
      });
    }
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <h2 className="text-xl">{status}</h2>
    </div>
  );
}