"use client"

import { useState, useEffect } from 'react'
import { onAuthStateChanged, User as FirebaseUser } from 'firebase/auth'
import { doc, getDoc, setDoc } from 'firebase/firestore'
import { auth, db } from '../lib/firebase'
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
  onboardingComplete?: boolean
}

interface AuthenticatedAppProps {
  isDarkMode: boolean
  setIsDarkMode: (darkMode: boolean) => void
}

export default function AuthenticatedApp({ isDarkMode, setIsDarkMode }: AuthenticatedAppProps) {
  const [user, setUser] = useState<User | null>(null)
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null)

  // Listen to Firebase Auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      console.log('🔥 Firebase auth state changed:', firebaseUser?.email)
      console.log('🔥 User exists:', !!firebaseUser)
      setFirebaseUser(firebaseUser)
      
            if (firebaseUser) {
        // Check if user exists in Firestore
        try {
          const userDoc = await getDoc(doc(db, 'users', firebaseUser.uid))
          
          if (userDoc.exists()) {
            const userData = userDoc.data()
            console.log('📄 Existing user data:', userData)
            const appUser: User = {
              id: firebaseUser.uid,
              name: firebaseUser.displayName || userData.displayName || 'Smart Citizen',
              email: firebaseUser.email || 'citizen@smartcity.com',
              avatar: firebaseUser.photoURL || userData.photoURL || `https://api.dicebear.com/7.x/avataaars/svg?seed=${firebaseUser.email}`,
              location: userData.location || 'Current Location',
              joinedDate: userData.createdAt?.toDate?.()?.toISOString() || new Date().toISOString(),
              isNewUser: false,
              preferences: userData.preferences,
              onboardingComplete: userData.onboardingComplete || false
            }
            
            console.log('👤 Setting existing user:', appUser)
            console.log('🎯 Show onboarding:', !userData.onboardingComplete)
            setUser(appUser)
            setShowOnboarding(!userData.onboardingComplete)
          } else {
            // New user - create Firestore document
            console.log('🆕 Creating new user document')
            const newUser: User = {
              id: firebaseUser.uid,
              name: firebaseUser.displayName || 'Smart Citizen',
              email: firebaseUser.email || 'citizen@smartcity.com',
              avatar: firebaseUser.photoURL || `https://api.dicebear.com/7.x/avataaars/svg?seed=${firebaseUser.email}`,
              location: 'Current Location',
              joinedDate: new Date().toISOString(),
              isNewUser: true,
              onboardingComplete: false
            }
            
            // Save to Firestore - only save serializable data
            const userDataToSave = {
              email: firebaseUser.email || '',
              displayName: firebaseUser.displayName || '',
              photoURL: firebaseUser.photoURL || '',
              createdAt: new Date(),
              updatedAt: new Date(),
              onboardingComplete: false,
              uid: firebaseUser.uid
            }
            
            try {
              await setDoc(doc(db, 'users', firebaseUser.uid), userDataToSave)
              console.log('✅ User document created successfully')
            } catch (error) {
              console.error('❌ Error creating user document:', error)
              // Continue with the flow even if Firestore fails
            }
            
            console.log('👤 Setting new user:', newUser)
            console.log('🎯 Show onboarding: true')
            setUser(newUser)
            setShowOnboarding(true)
          }
        } catch (error) {
          console.error('❌ Error reading user document:', error)
          // If Firestore fails, create a basic user object
          const fallbackUser: User = {
            id: firebaseUser.uid,
            name: firebaseUser.displayName || 'Smart Citizen',
            email: firebaseUser.email || 'citizen@smartcity.com',
            avatar: firebaseUser.photoURL || `https://api.dicebear.com/7.x/avataaars/svg?seed=${firebaseUser.email}`,
            location: 'Current Location',
            joinedDate: new Date().toISOString(),
            isNewUser: true,
            onboardingComplete: false
          }
          setUser(fallbackUser)
          setShowOnboarding(true)
        }
      } else {
        // User signed out
        setUser(null)
        setShowOnboarding(false)
      }
      
      setIsLoading(false)
    })

    return () => unsubscribe()
  }, [])

  // Add a function to clear auth state for testing
  const clearAuthForTesting = async () => {
    try {
      await auth.signOut()
      // Also clear any stored data
      localStorage.removeItem('smartcity_user')
      setUser(null)
      setShowOnboarding(false)
      setFirebaseUser(null)
    } catch (error) {
      console.error('Error clearing auth:', error)
    }
  }

  const handleLoginSuccess = (userData: User) => {
    // This is now handled by Firebase Auth state listener
    console.log('Login success handled by Firebase Auth')
  }

  const handleOnboardingComplete = async (completedUser: any, preferences: any) => {
    if (!firebaseUser) return
    
    const updatedUser = {
      ...user,
      ...completedUser,
      preferences,
      isNewUser: false,
      onboardingComplete: true
    }
    
    // Update Firestore - only save serializable data
    const updateData = {
      preferences,
      onboardingComplete: true,
      updatedAt: new Date(),
      location: completedUser.location || updatedUser.location,
      name: completedUser.name || updatedUser.name
    }
    
    try {
      await setDoc(doc(db, 'users', firebaseUser.uid), updateData, { merge: true })
      console.log('✅ User preferences updated successfully')
    } catch (error) {
      console.error('❌ Error updating user preferences:', error)
      // Continue with the flow even if Firestore fails
    }
    
    setUser(updatedUser)
    setShowOnboarding(false)
  }

  const handleLogout = async () => {
    try {
      await auth.signOut()
      setUser(null)
      setShowOnboarding(false)
      setFirebaseUser(null)
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  if (isLoading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${
          isDarkMode 
            ? 'bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900' 
            : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-50'
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

  // Show login screen if no Firebase user
  if (!firebaseUser) {
    return (
      <div>
        <GoogleLogin onLoginSuccess={handleLoginSuccess} isDarkMode={isDarkMode} />
        {/* Development-only: Clear auth state button */}
        {process.env.NODE_ENV === 'development' && (
          <button
            onClick={clearAuthForTesting}
            className="fixed top-4 right-4 bg-red-500 text-white px-3 py-1 rounded text-sm"
          >
            Clear Auth (Dev)
          </button>
        )}
      </div>
    )
  }

  // Show onboarding if user exists but hasn't completed onboarding
  if (showOnboarding && user) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />
  }

  // Show main dashboard if user is authenticated and has completed onboarding
  if (user && !showOnboarding) {
    return (
      <div>
        <CityScapeDashboard 
          user={user}
          onLogout={handleLogout}
          isDarkMode={isDarkMode}
          setIsDarkMode={setIsDarkMode}
        />
        {/* Development-only: Reset onboarding button */}
        {process.env.NODE_ENV === 'development' && (
          <div className="fixed top-4 right-4 flex flex-col gap-2 z-50">
            <button
                          onClick={async () => {
              if (firebaseUser) {
                try {
                  await setDoc(doc(db, 'users', firebaseUser.uid), {
                    onboardingComplete: false,
                    updatedAt: new Date()
                  }, { merge: true })
                  console.log('✅ Onboarding reset successfully')
                  setShowOnboarding(true)
                } catch (error) {
                  console.error('❌ Error resetting onboarding:', error)
                }
              }
            }}
              className="bg-orange-500 text-white px-3 py-1 rounded text-sm"
            >
              Reset Onboarding (Dev)
            </button>
            <button
              onClick={clearAuthForTesting}
              className="bg-red-500 text-white px-3 py-1 rounded text-sm"
            >
              Clear Auth (Dev)
            </button>
          </div>
        )}
      </div>
    )
  }

  // Fallback loading state
  return (
    <div className={`min-h-screen flex items-center justify-center ${
      isDarkMode 
        ? 'bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-50'
    }`}>
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4 shadow-lg"></div>
        <p className={`text-lg font-medium ${
          isDarkMode ? 'text-gray-200' : 'text-gray-800'
        }`}>
          Setting up your experience...
        </p>
      </div>
    </div>
  )
}
