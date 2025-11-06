import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CityScape',
  description: 'Connected urban living — CityScape',
  generator: 'v0.dev',
  icons: {
    icon: '/images/city-map.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        {/* Explicit favicon link to avoid /favicon.ico 404 in browsers */}
        <link rel="icon" href="/images/city-map.png" />
      </head>
      <body>{children}</body>
    </html>
  )
}
