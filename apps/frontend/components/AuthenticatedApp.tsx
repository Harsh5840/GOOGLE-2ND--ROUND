"use client"

import { useState, useEffect } from 'react'
import GoogleLogin from './GoogleLogin'
import OnboardingFlow from './OnboardingFlow'
import CityScapeDashboard from '../dashboard'

interface User {
  id: string
  name: string
  email: string
  avatar: string
  location: string
  joinedDate: string
  isNewUser: boolean
  preferences?: any
}

interface AuthenticatedAppProps {
  isDarkMode: boolean
  setIsDarkMode: (darkMode: boolean) => void
}

export default function AuthenticatedApp({ isDarkMode, setIsDarkMode }: AuthenticatedAppProps) {
  const [user, setUser] = useState<User | null>(null)
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in (localStorage)
    const savedUser = localStorage.getItem('smartcity_user')
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser)
        // Only show onboarding if user is new AND hasn't completed onboarding
        if (userData.isNewUser && !userData.onboardingComplete) {
          setUser(userData)
          setShowOnboarding(true)
        } else {
          // User has completed onboarding or is returning user
          setUser(userData)
          setShowOnboarding(false)
        }
      } catch (error) {
        console.error('Error parsing saved user data:', error)
        localStorage.removeItem('smartcity_user')
      }
    }
    setIsLoading(false)
  }, [])

  const handleLoginSuccess = (userData: User) => {
    setUser(userData)
    setShowOnboarding(userData.isNewUser)
    localStorage.setItem('smartcity_user', JSON.stringify(userData))
  }

  const handleOnboardingComplete = (completedUser: any, preferences: any) => {
    const updatedUser = {
      ...user,
      ...completedUser,
      preferences,
      isNewUser: false,
      onboardingComplete: true
    }
    setUser(updatedUser)
    setShowOnboarding(false)
    localStorage.setItem('smartcity_user', JSON.stringify(updatedUser))
  }

  const handleLogout = () => {
    setUser(null)
    setShowOnboarding(false)
    localStorage.removeItem('smartcity_user')
  }

  if (isLoading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${
        isDarkMode 
          ? 'bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900' 
          : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50'
      }`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4 shadow-lg"></div>
          <p className={`text-lg font-medium ${
            isDarkMode ? 'text-gray-200' : 'text-gray-800'
          }`}>
            Loading CityScape...
          </p>
        </div>
      </div>
    )
  }

  // Show login screen if no user
  if (!user) {
    return <GoogleLogin onLoginSuccess={handleLoginSuccess} isDarkMode={isDarkMode} />
  }

  // Show onboarding if user is new and hasn't completed onboarding
  if (showOnboarding) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />
  }

  // Show main dashboard
  return (
    <CityScapeDashboard 
      user={user}
      onLogout={handleLogout}
      isDarkMode={isDarkMode}
      setIsDarkMode={setIsDarkMode}
    />
  )
}
