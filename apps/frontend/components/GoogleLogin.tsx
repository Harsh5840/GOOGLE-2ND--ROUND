"use client"

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  Building, 
  MapPin, 
  Users, 
  Shield, 
  Sparkles, 
  Camera,
  MessageCircle,
  TrendingUp,
  Globe,
  Zap
} from 'lucide-react'
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth'
import { auth } from '../lib/firebase'

interface GoogleLoginProps {
  onLoginSuccess: (userData: any) => void
  isDarkMode?: boolean
}

export default function GoogleLogin({ onLoginSuccess, isDarkMode = false }: GoogleLoginProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [email, setEmail] = useState('')
  const [showEmailLogin, setShowEmailLogin] = useState(false)

  const handleGoogleLogin = async () => {
    setIsLoading(true)
    
    try {
      const provider = new GoogleAuthProvider()
      provider.addScope('profile')
      provider.addScope('email')
      
      const result = await signInWithPopup(auth, provider)
      const user = result.user
      
      const userData = {
        id: user.uid,
        name: user.displayName || 'Smart Citizen',
        email: user.email || 'citizen@smartcity.com',
        avatar: user.photoURL || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.email}`,
        location: 'Current Location',
        joinedDate: new Date().toISOString(),
        isNewUser: true
      }
      
      onLoginSuccess(userData)
      setIsLoading(false)
    } catch (error) {
      console.error('Google login error:', error)
      setIsLoading(false)
      // You could add error state handling here
    }
  }

  const handleEmailLogin = async () => {
    if (!email.trim()) return
    handleGoogleLogin()
  }

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 transition-all duration-500 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50'
    }`}>
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-20 left-20 w-32 h-32 rounded-full opacity-20 animate-pulse ${
          isDarkMode ? 'bg-blue-400' : 'bg-blue-300'
        }`} />
        <div className={`absolute bottom-20 right-20 w-24 h-24 rounded-full opacity-20 animate-pulse delay-1000 ${
          isDarkMode ? 'bg-purple-400' : 'bg-purple-300'
        }`} />
        <div className={`absolute top-1/2 left-10 w-16 h-16 rounded-full opacity-20 animate-pulse delay-500 ${
          isDarkMode ? 'bg-indigo-400' : 'bg-indigo-300'
        }`} />
      </div>

      <div className={`w-full max-w-md relative z-10 backdrop-blur-xl rounded-3xl border shadow-2xl p-8 ${
        isDarkMode 
          ? 'bg-gray-900/80 border-gray-600/30 shadow-blue-900/40' 
          : 'bg-white/80 border-white/30 shadow-blue-500/10'
      }`}>
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className={`w-20 h-20 mx-auto mb-4 rounded-2xl flex items-center justify-center ${
            isDarkMode 
              ? 'bg-gradient-to-br from-blue-600 to-indigo-600' 
              : 'bg-gradient-to-br from-blue-500 to-indigo-500'
          } shadow-lg`}>
            <Building className="w-10 h-10 text-white" />
          </div>
          
          <h1 className={`text-3xl font-bold mb-2 ${
            isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            CityScape
          </h1>
          
          <p className={`text-lg ${
            isDarkMode ? 'text-gray-300' : 'text-gray-600'
          }`}>
            Your gateway to connected urban living
          </p>
        </div>

        {/* Features Preview */}
        <div className="grid grid-cols-2 gap-3 mb-8">
          {[
            { icon: Camera, label: 'AI Reports', color: 'text-blue-500' },
            { icon: MapPin, label: 'Live Map', color: 'text-green-500' },
            { icon: MessageCircle, label: 'City Chat', color: 'text-purple-500' },
            { icon: TrendingUp, label: 'Analytics', color: 'text-orange-500' }
          ].map((feature, index) => (
            <div key={index} className={`p-3 rounded-xl border transition-all duration-300 hover:scale-105 ${
              isDarkMode 
                ? 'bg-gray-800/50 border-gray-600/30 hover:border-blue-500/50' 
                : 'bg-white/50 border-white/40 hover:border-blue-300/50'
            }`}>
              <feature.icon className={`w-5 h-5 mb-2 ${feature.color}`} />
              <p className={`text-sm font-medium ${
                isDarkMode ? 'text-gray-200' : 'text-gray-700'
              }`}>
                {feature.label}
              </p>
            </div>
          ))}
        </div>

        {/* Login Options */}
        {!showEmailLogin ? (
          <div className="space-y-4">
            <Button
              onClick={handleGoogleLogin}
              disabled={isLoading}
              className="w-full h-12 bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 rounded-xl font-semibold shadow-lg transition-all duration-300 hover:scale-105 disabled:opacity-50"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                  <span>Connecting...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-3">
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  <span>Continue with Google</span>
                </div>
              )}
            </Button>

            <div className="relative">
              <div className={`absolute inset-0 flex items-center ${
                isDarkMode ? 'border-gray-600' : 'border-gray-300'
              }`}>
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className={`px-2 ${
                  isDarkMode ? 'bg-gray-900 text-gray-400' : 'bg-white text-gray-500'
                }`}>
                  Or
                </span>
              </div>
            </div>

            <Button
              onClick={() => setShowEmailLogin(true)}
              variant="outline"
              className={`w-full h-12 rounded-xl font-semibold transition-all duration-300 hover:scale-105 ${
                isDarkMode 
                  ? 'border-gray-600 text-gray-200 hover:bg-gray-800' 
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Continue with Email
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className={`block text-sm font-medium mb-2 ${
                isDarkMode ? 'text-gray-200' : 'text-gray-700'
              }`}>
                Email Address
              </label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="citizen@example.com"
                className={`h-12 rounded-xl ${
                  isDarkMode 
                    ? 'bg-gray-800 border-gray-600 text-gray-200' 
                    : 'bg-white border-gray-300'
                }`}
                onKeyPress={(e) => e.key === 'Enter' && handleEmailLogin()}
              />
            </div>

            <Button
              onClick={handleEmailLogin}
              disabled={isLoading || !email.trim()}
              className="w-full h-12 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-semibold shadow-lg transition-all duration-300 hover:scale-105 disabled:opacity-50"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Signing In...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Zap className="w-5 h-5" />
                  <span>Get Started</span>
                </div>
              )}
            </Button>

            <Button
              onClick={() => setShowEmailLogin(false)}
              variant="ghost"
              className={`w-full ${
                isDarkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              ← Back to login options
            </Button>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className={`text-xs ${
            isDarkMode ? 'text-gray-400' : 'text-gray-500'
          }`}>
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  )
}
