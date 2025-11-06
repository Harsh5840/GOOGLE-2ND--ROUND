"use client"

import GoogleLogin from '../../components/GoogleLogin'
import Link from 'next/link'

export default function AuthPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-800">
      <div className="w-full max-w-md p-6 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-semibold mb-4">Sign in to Urban Pulse</h2>
        <p className="text-sm text-slate-500 mb-6">Use your Google account to sign in and access the dashboard.</p>

        <div className="mb-4">
          <GoogleLogin onLoginSuccess={() => {}} isDarkMode={false} />
        </div>

        <div className="text-center mt-4">
          <Link href="/" className="text-sm text-slate-500 hover:underline">Back to home</Link>
        </div>
      </div>
    </main>
  )
}
