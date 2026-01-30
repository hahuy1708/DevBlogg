// src/app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [hasToken, setHasToken] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setHasToken(Boolean(token));
    setReady(true);
    if (!token) router.replace('/login');
  }, [router]);

  if (!ready) return null;
  if (!hasToken) return null;

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold">Logged in</h1>

      <p className="mt-2">OAuth login worked. You can now call protected APIs.</p>
      <button
        className="mt-4 rounded bg-gray-800 px-4 py-2 text-white"
        onClick={() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          router.replace('/login');
        }}
      >
        Logout
      </button>
    </main>
  );
}
