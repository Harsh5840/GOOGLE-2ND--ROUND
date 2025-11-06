"use client"

import Link from 'next/link'

export default function Page() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-800">
      <div className="max-w-2xl mx-auto p-8">
        <div className="text-center space-y-6">
          <h1 className="text-4xl font-extrabold">CityScape</h1>
          <p className="text-slate-600">A minimal, modern city intelligence dashboard.</p>

          <div className="flex items-center justify-center gap-4 mt-6">
            <Link href="/event-dashboard" className="px-6 py-3 bg-sky-600 text-white rounded-md hover:bg-sky-700">Open Dashboard</Link>
            <Link href="/auth" className="px-6 py-3 border border-slate-200 rounded-md text-slate-700 hover:bg-slate-100">Sign in</Link>
          </div>

          <p className="text-xs text-slate-400 mt-4">Designed for clarity — purple accents removed for a neutral, minimal look.</p>
        </div>
      </div>
    </main>
  )
}
