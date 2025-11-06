"use client"

import Link from 'next/link'
import { 
  MapPin, 
  Camera, 
  MessageCircle, 
  TrendingUp, 
  Shield, 
  Zap,
  Users,
  Globe,
  ArrowRight,
  CheckCircle,
  Sparkles
} from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Globe className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                CityScape
              </span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-slate-600 hover:text-blue-600 transition-colors">Features</a>
              <a href="#how-it-works" className="text-slate-600 hover:text-blue-600 transition-colors">How it Works</a>
              <a href="#about" className="text-slate-600 hover:text-blue-600 transition-colors">About</a>
            </div>

            <Link 
              href="/auth"
              className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full font-semibold hover:shadow-lg hover:scale-105 transition-all duration-300"
            >
              Sign In
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center space-y-8">
            <div className="inline-block">
              <span className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
                🌆 Your City, Intelligently Connected
              </span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-extrabold text-slate-900 leading-tight">
              Welcome to{" "}
              <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                CityScape
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
              Your AI-powered urban intelligence platform. Monitor events, engage with your community, 
              and stay informed with real-time city insights.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
              <Link 
                href="/auth"
                className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full font-bold text-lg hover:shadow-2xl hover:scale-105 transition-all duration-300 flex items-center space-x-2"
              >
                <span>Get Started Free</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              
              <a 
                href="#features"
                className="px-8 py-4 bg-white text-slate-700 rounded-full font-bold text-lg hover:shadow-lg hover:scale-105 transition-all duration-300 border-2 border-slate-200"
              >
                Learn More
              </a>
            </div>

            <div className="pt-12 flex items-center justify-center space-x-8 text-sm text-slate-500">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span>Free forever</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6 bg-white">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Powerful Features for Urban Living
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Everything you need to stay connected and informed about your city
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: MapPin,
                title: "Live City Map",
                description: "Interactive real-time map showing events, traffic, and activities across your city",
                color: "blue"
              },
              {
                icon: Camera,
                title: "AI Photo Reports",
                description: "Upload geotagged photos and get instant AI-powered analysis of city events",
                color: "green"
              },
              {
                icon: MessageCircle,
                title: "City Assistant",
                description: "Chat with our AI assistant for traffic updates, routes, and local recommendations",
                color: "purple"
              },
              {
                icon: TrendingUp,
                title: "Live Analytics",
                description: "Real-time insights into traffic patterns, event trends, and city metrics",
                color: "orange"
              },
              {
                icon: Shield,
                title: "Safety Alerts",
                description: "Instant notifications for emergencies, weather alerts, and safety updates",
                color: "red"
              },
              {
                icon: Sparkles,
                title: "AI Podcasts",
                description: "Auto-generated city news podcasts personalized to your interests",
                color: "indigo"
              }
            ].map((feature, index) => (
              <div 
                key={index}
                className="group p-8 bg-gradient-to-br from-slate-50 to-white rounded-2xl border border-slate-200 hover:border-blue-300 hover:shadow-xl transition-all duration-300"
              >
                <div className={`w-14 h-14 bg-${feature.color}-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className={`w-7 h-7 text-${feature.color}-600`} />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-6 bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              How CityScape Works
            </h2>
            <p className="text-xl text-slate-600">
              Get started in three simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "1",
                title: "Sign In",
                description: "Create your free account with Google authentication in seconds"
              },
              {
                step: "2",
                title: "Customize",
                description: "Set your location preferences and interests during quick onboarding"
              },
              {
                step: "3",
                title: "Explore",
                description: "Access your personalized dashboard with live city insights and AI features"
              }
            ].map((item, index) => (
              <div key={index} className="relative">
                <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-shadow">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mb-6 shadow-lg">
                    {item.step}
                  </div>
                  <h3 className="text-2xl font-bold text-slate-900 mb-4">{item.title}</h3>
                  <p className="text-slate-600 leading-relaxed">{item.description}</p>
                </div>
                {index < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                    <ArrowRight className="w-8 h-8 text-blue-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            {[
              { number: "10K+", label: "Active Users" },
              { number: "50K+", label: "Events Tracked" },
              { number: "99.9%", label: "Uptime" },
              { number: "24/7", label: "AI Support" }
            ].map((stat, index) => (
              <div key={index} className="space-y-2">
                <div className="text-5xl font-bold">{stat.number}</div>
                <div className="text-blue-100 text-lg">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            Ready to Transform Your Urban Experience?
          </h2>
          <p className="text-xl text-slate-600 mb-10">
            Join thousands of citizens using CityScape to stay connected with their city
          </p>
          <Link 
            href="/auth"
            className="group inline-flex items-center space-x-2 px-10 py-5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full font-bold text-xl hover:shadow-2xl hover:scale-105 transition-all duration-300"
          >
            <span>Start Your Journey</span>
            <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="flex items-center space-x-2">
              <Globe className="w-6 h-6 text-blue-400" />
              <span className="text-xl font-bold text-white">CityScape</span>
            </div>
            
            <div className="flex space-x-6">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
            
            <div className="text-sm">
              © 2025 CityScape. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
