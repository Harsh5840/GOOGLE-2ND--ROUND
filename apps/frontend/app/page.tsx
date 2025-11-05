"use client"

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, MapPin, Users, Activity, ArrowRight, Zap } from 'lucide-react'
import AuthenticatedApp from '../components/AuthenticatedApp'

export default function Page() {
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [showHero, setShowHero] = useState(true)

  useEffect(() => {
    // Auto-hide hero after 3 seconds
    const timer = setTimeout(() => {
      setShowHero(false)
    }, 3000)

    return () => clearTimeout(timer)
  }, [])

  if (showHero) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-cosmic-animated relative overflow-hidden">
        {/* Animated background particles */}
        <div className="particles absolute inset-0"></div>

        <motion.div
          className="text-center relative z-10 max-w-4xl mx-auto px-6"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
        >
          {/* Main logo/brand */}
          <motion.div
            className="mb-8"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, duration: 0.8, type: "spring", stiffness: 200 }}
          >
            <div className="w-24 h-24 mx-auto mb-6 relative">
              <div className="absolute inset-0 bg-gradient-primary rounded-2xl animate-pulse opacity-20"></div>
              <div className="absolute inset-2 bg-gradient-secondary rounded-xl animate-pulse opacity-40 animation-delay-100"></div>
              <div className="absolute inset-4 glass-strong rounded-lg flex items-center justify-center">
                <Sparkles className="w-10 h-10 text-white animate-float" />
              </div>
            </div>
            <h1 className="text-6xl md:text-8xl font-black text-gradient-primary mb-4">
              Urban Pulse
            </h1>
          </motion.div>

          {/* Tagline */}
          <motion.p
            className="text-xl md:text-2xl text-white/90 mb-8 font-light"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            Your city's heartbeat, in real-time
          </motion.p>

          {/* Feature highlights */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.8 }}
          >
            <div className="glass p-6 rounded-xl text-center">
              <MapPin className="w-8 h-8 text-blue-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">Live Mapping</h3>
              <p className="text-white/70 text-sm">Real-time city events and navigation</p>
            </div>
            <div className="glass p-6 rounded-xl text-center">
              <Users className="w-8 h-8 text-purple-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">Community</h3>
              <p className="text-white/70 text-sm">Connect with fellow citizens</p>
            </div>
            <div className="glass p-6 rounded-xl text-center">
              <Activity className="w-8 h-8 text-green-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">AI Insights</h3>
              <p className="text-white/70 text-sm">Smart city intelligence</p>
            </div>
          </motion.div>

          {/* CTA Button */}
          <motion.button
            onClick={() => setShowHero(false)}
            className="glass-strong px-8 py-4 rounded-full text-white font-semibold text-lg hover:scale-105 transition-all duration-300 btn-modern glow-primary group"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.2, duration: 0.5 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="flex items-center">
              Enter CityScape
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </span>
          </motion.button>

          {/* Loading indicator */}
          <motion.div
            className="mt-8 flex justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5, duration: 0.5 }}
          >
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce animation-delay-100"></div>
              <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce animation-delay-200"></div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    )
  }

  return (
    <AuthenticatedApp
      isDarkMode={isDarkMode}
      setIsDarkMode={setIsDarkMode}
    />
  )
}
