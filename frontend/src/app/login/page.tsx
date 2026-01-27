// src/app/login/page.tsx
'use client';

import { useState } from 'react';
import api from '@/lib/axios';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/api/auth/login/', { email, password });
      alert('Login success! Token: ' + res.data.access);
      console.log(res.data);
    } catch (error: any) {
      alert('Login failed: ' + JSON.stringify(error.response?.data));
    }
  };

  
  const handleSocialLogin = (provider: 'github' | 'google') => {
    let url = '';
    const redirectUri = 'http://localhost:3000/auth/callback'; 

    if (provider === 'github') {
      const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID; 
      url = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=user:email`;
    } else if (provider === 'google') {
      const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
      url = `https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=${redirectUri}&prompt=consent&response_type=code&client_id=${clientId}&scope=openid%20email%20profile&access_type=offline`;
    }
    
    // Redirect the user to the provider's page
    window.location.href = url;
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 space-y-4">
      <h1 className="text-2xl font-bold">Test Auth System</h1>
      
      {/* Form Login */}
      <form onSubmit={handleLogin} className="flex flex-col gap-2 w-80">
        <input 
          type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} 
          className="p-2 border rounded"
        />
        <input 
          type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} 
          className="p-2 border rounded"
        />
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">Login Normal</button>
      </form>

      <div className="border-t w-80 my-4"></div>

      {/* Social Login Buttons */}
      <div className="flex flex-col gap-2 w-80">
        <button onClick={() => handleSocialLogin('google')} className="bg-red-500 text-white p-2 rounded">
          Login with Google
        </button>
        <button onClick={() => handleSocialLogin('github')} className="bg-gray-800 text-white p-2 rounded">
          Login with GitHub
        </button>
      </div>
    </div>
  );
}