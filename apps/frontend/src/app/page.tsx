"use client"

import { useState } from 'react'
import AuthenticatedApp from '../components/AuthenticatedApp'

export default function Page() {
  const [isDarkMode, setIsDarkMode] = useState(false)

  return (
    <AuthenticatedApp 
      isDarkMode={isDarkMode} 
      setIsDarkMode={setIsDarkMode} 
    />
  )
}
