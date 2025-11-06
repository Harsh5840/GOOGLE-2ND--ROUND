"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { motion } from "framer-motion"
import {
  Bell,
  Search,
  Camera,
  Users,
  Activity,
  Car,
  Building,
  Calendar,
  Cloud,
  User,
  Send,
  Bot,
  Upload,
  X,
  TrendingUp,
  MapPin,
  Clock,
  AlertTriangle,
  Eye,
  MessageCircle,
  ChevronRight,
  Flame,
  Sun,
  Moon,
  Sparkles,
  ZapIcon,
  Menu,
  Filter,
  BarChart3,
  Shield,
  ArrowUp,
  ArrowDown,
  Layers,
  Heart,
  Share2,
  Bookmark,
  MoreHorizontal,
  ChevronUp,
  ChevronDown,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import GoogleMap from "./components/google-map"
import Header from "./components/Header"
import Sidebar from "./components/Sidebar"
import Notifications from "./components/Notifications"
import Chat from "./components/Chat"
import ReportModal from "./components/ReportModal"

import { getSeverityColor, formatTimeAgo } from "./lib/utils"

import { sendChatMessage, getLocationMoodWithDisplay, getBestRouteWithMood, getMustVisitPlacesWithMood, getAllUserReports } from "@/lib/api"
import { ChatMessage } from "@/types/chat"


interface CityEvent {
  id: number;
  type: string;
  title: string;
  location: string;
  timestamp: Date;
  severity: string;
  summary: string;
  reporter: {
    name: string;
    avatar: string;
    verified: boolean;
    followers: number;
  };
  coordinates: { x: number; y: number };
  likes: number;
  comments: number;
  shares: number;
  bookmarks: number;
  image: string | null;
  tags: string[];
  customEmoji: string;
}

const eventTypes = [
  {
    id: "traffic",
    label: "Traffic & Transport",
    icon: Car,
    color: "#3b82f6",
    gradient: "from-blue-500 via-blue-600 to-indigo-600",
    lightBg: "from-blue-50 to-indigo-100",
    darkBg: "from-blue-950/50 to-indigo-950/50",
    description: "Real-time traffic monitoring",
    emoji: "🚗",
  },
  {
    id: "infrastructure",
    label: "Infrastructure",
    icon: Building,
    color: "#8b5cf6",
    gradient: "from-purple-500 via-violet-600 to-purple-700",
    lightBg: "from-purple-50 to-violet-100",
    darkBg: "from-purple-950/50 to-violet-950/50",
    description: "City systems & utilities",
    emoji: "🏗️",
  },
  {
    id: "events",
    label: "Public Events",
    icon: Calendar,
    color: "#10b981",
    gradient: "from-emerald-500 via-green-600 to-teal-600",
    lightBg: "from-emerald-50 to-green-100",
    darkBg: "from-emerald-950/50 to-green-950/50",
    description: "Community gatherings",
    emoji: "🎉",
  },
  {
    id: "emergency",
    label: "Emergency Services",
    icon: Shield,
    color: "#ef4444",
    gradient: "from-red-500 via-rose-600 to-pink-600",
    lightBg: "from-red-50 to-rose-100",
    darkBg: "from-red-950/50 to-rose-950/50",
    description: "Critical alerts & responses",
    emoji: "🚨",
  },
  {
    id: "weather",
    label: "Weather & Climate",
    icon: Cloud,
    color: "#f59e0b",
    gradient: "from-amber-500 via-orange-600 to-yellow-600",
    lightBg: "from-amber-50 to-orange-100",
    darkBg: "from-amber-950/50 to-orange-950/50",
    description: "Environmental conditions",
    emoji: "🌤️",
  },
]

const trendingLocations = [
  { name: "Downtown Bridge", events: 8, trend: "+12%", change: "up" },
  { name: "Central Park", events: 5, trend: "+8%", change: "up" },
  { name: "5th Avenue", events: 12, trend: "+15%", change: "up" },
  { name: "Park Avenue", events: 3, trend: "-5%", change: "down" },
]

// Zones removed as requested by user

const recentActivity = [
  { user: "Alex Chen", action: "reported traffic jam", location: "Main St", time: "2m ago", type: "traffic" },
  { user: "Maria Garcia", action: "liked event", location: "Central Park", time: "5m ago", type: "events" },
  { user: "John Smith", action: "commented on", location: "5th Avenue", time: "8m ago", type: "infrastructure" },
  { user: "Sarah Wilson", action: "shared alert", location: "Downtown", time: "12m ago", type: "emergency" },
]

const notifications = [
  {
    id: 0,
    type: "traffic",
    title: "Route Alert",
    message: "Your usual work route has a roadblock — suggest alternate routes / Your usual route has more traffic than usual, leave 15 minutes early",
    time: "now",
    read: false,
  },
  {
    id: 1,
    type: "emergency",
    title: "Emergency Alert",
    message: "Fire department response in downtown area",
    time: "2m ago",
    read: false,
  },
  {
    id: 2,
    type: "report",
    title: "New Reports",
    message: "3 citizen reports received in the last hour",
    time: "5m ago",
    read: false,
  },
  {
    id: 3,
    type: "traffic",
    title: "Traffic Update",
    message: "Downtown congestion has decreased by 15%",
    time: "10m ago",
    read: true,
  },
  {
    id: 4,
    type: "weather",
    title: "Weather Alert",
    message: "Heavy rain expected in your area",
    time: "15m ago",
    read: true,
  },
]

interface CityScapeDashboardProps {
  user?: {
    id: string
    name: string
    email: string
    avatar: string
    location: string
    preferences?: any
  }
  onLogout?: () => void
  isDarkMode: boolean
  setIsDarkMode: (darkMode: boolean) => void
}

export default function CityScapeDashboard({ 
  user, 
  onLogout, 
  isDarkMode: propIsDarkMode = false, 
  setIsDarkMode: propSetIsDarkMode = () => {} 
}: CityScapeDashboardProps) {
  const [isDarkMode, setIsDarkMode] = useState(propIsDarkMode)
  
  // Sync dark mode with parent component
  useEffect(() => {
    setIsDarkMode(propIsDarkMode)
  }, [propIsDarkMode])
  
  const handleDarkModeToggle = () => {
    const newDarkMode = !isDarkMode
    setIsDarkMode(newDarkMode)
    propSetIsDarkMode(newDarkMode)
  }
  const [isMobile, setIsMobile] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [mobileChatOpen, setMobileChatOpen] = useState(false)
  const [mobileChatExpanded, setMobileChatExpanded] = useState(false)
  const [activeFilters, setActiveFilters] = useState<string[]>([
    "traffic",
    "infrastructure",
    "events",
    "emergency",
    "weather",
  ])
  const [searchQuery, setSearchQuery] = useState("")
  const [showNotifications, setShowNotifications] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [liveStats, setLiveStats] = useState({
    activeEvents: 35,
    citizensOnline: 1247,
    alertsToday: 12,
    responseTime: 4.2,
  })
  const [selectedEvent, setSelectedEvent] = useState<CityEvent | null>(null)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      sender: "bot",
      text: "Hi! I'm your city assistant. Ask me anything about traffic, events, or city services.",
      timestamp: new Date(Date.now() - 60000),
    },
  ])
  const [chatInput, setChatInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [showReportModal, setShowReportModal] = useState(false)
  const [reportForm, setReportForm] = useState({
    title: "",
    description: "",
    type: "traffic",
    image: null as File | null,
  })
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [userReports, setUserReports] = useState<any[]>([])
  const [loadingReports, setLoadingReports] = useState(false)
  const [rightPanelCollapsed, setRightPanelCollapsed] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [likedEvents, setLikedEvents] = useState<Set<number>>(new Set())
  const [bookmarkedEvents, setBookmarkedEvents] = useState<Set<number>>(new Set())
  const fileInputRef = useRef<HTMLInputElement>(null!)
  const notificationRef = useRef<HTMLDivElement>(null!)
  const mobileChatRef = useRef<HTMLDivElement>(null!)
  const chatMessagesRef = useRef<HTMLDivElement>(null!)
  const [locationMood, setLocationMood] = useState<any>(null)
  const [moodLoading, setMoodLoading] = useState(false)
  const [moodError, setMoodError] = useState<string | null>(null)
  const [locationData, setLocationData] = useState<any>(null)
  const [currentCity, setCurrentCity] = useState<string>("Bangalore") // Store detected city for chatbot

  // Check if mobile
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768
      setIsMobile(mobile)
      if (mobile) {
        setSidebarOpen(false)
        setRightPanelCollapsed(true)
      }
    }

    checkMobile()
    window.addEventListener("resize", checkMobile)
    return () => window.removeEventListener("resize", checkMobile)
  }, [])

  useEffect(() => {
    // Simulate loading
    const loadingTimer = setTimeout(() => {
      setIsLoading(false)
    }, 2000)

    const timer = setInterval(() => {
      setCurrentTime(new Date())
      setLiveStats((prev) => ({
        activeEvents: Math.max(15, prev.activeEvents + Math.floor(Math.random() * 3) - 1),
        citizensOnline: Math.max(1000, prev.citizensOnline + Math.floor(Math.random() * 20) - 10),
        alertsToday: Math.max(5, prev.alertsToday + (Math.random() > 0.95 ? 1 : 0)),
        responseTime: Math.max(2, prev.responseTime + (Math.random() - 0.5) * 0.5),
      }))
    }, 5000)

    return () => {
      clearTimeout(loadingTimer)
      clearInterval(timer)
    }
  }, [])

  // Fetch user reports on component mount
  useEffect(() => {
    const fetchUserReports = async () => {
      setLoadingReports(true)
      try {
        const reports = await getAllUserReports()
        setUserReports(reports)
      } catch (error) {
        console.error('Error fetching user reports:', error)
      } finally {
        setLoadingReports(false)
      }
    }

    fetchUserReports()
  }, [])

  // Listen for new user reports from ReportModal
  useEffect(() => {
    const handleNewUserReport = (event: CustomEvent) => {
      const newReport = event.detail
      setUserReports(prev => [newReport, ...prev])
    }

    window.addEventListener('newUserReport', handleNewUserReport as EventListener)
    return () => {
      window.removeEventListener('newUserReport', handleNewUserReport as EventListener)
    }
  }, [])

  useEffect(() => {
    const detectUserLocation = async () => {
      setMoodLoading(true)
      setMoodError(null)
      
      try {
        // Try to get user's actual location
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            async (position) => {
              const { latitude, longitude } = position.coords
              
              // Reverse geocode to get city name
              try {
                const response = await fetch(
                  `https://api.opencagedata.com/geocode/v1/json?q=${latitude}+${longitude}&key=YOUR_API_KEY&limit=1`
                )
                const data = await response.json()
                const city = data.results[0]?.components?.city || 
                           data.results[0]?.components?.town || 
                           data.results[0]?.components?.village || 
                           "Current Location"
                
                setCurrentCity(city) // Store detected city for chatbot
                const locationData = await getLocationMoodWithDisplay(city)
                setLocationMood(locationData)
                setMoodLoading(false)
              } catch (error) {
                console.error('Error getting city name:', error)
                // Fallback to default location
                setCurrentCity("Bangalore") // Store fallback city for chatbot
                const locationData = await getLocationMoodWithDisplay("Bangalore")
                setLocationMood(locationData)
                setMoodLoading(false)
              }
            },
            async (error) => {
              console.error('Geolocation error:', error)
              // Fallback to default location
              setCurrentCity("Bangalore") // Store fallback city for chatbot
              const locationData = await getLocationMoodWithDisplay("Bangalore")
              setLocationMood(locationData)
              setMoodLoading(false)
            },
            {
              enableHighAccuracy: true,
              timeout: 10000,
              maximumAge: 300000 // 5 minutes
            }
          )
        } else {
          // Geolocation not supported, use default
          setCurrentCity("Bangalore") // Store fallback city for chatbot
          const locationData = await getLocationMoodWithDisplay("Bangalore")
          setLocationMood(locationData)
          setMoodLoading(false)
        }
      } catch (error) {
        console.error('Location detection error:', error)
        setMoodError("Could not fetch city mood data.")
        setMoodLoading(false)
      }
    }
    
    detectUserLocation()
  }, [])

  // Auto-scroll chat messages
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight
    }
  }, [chatMessages])

  // Close notifications when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setShowNotifications(false)
      }
      if (mobileChatRef.current && !mobileChatRef.current.contains(event.target as Node)) {
        if (mobileChatExpanded && isMobile) {
          setMobileChatExpanded(false)
        }
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [mobileChatExpanded, isMobile])

  const toggleFilter = (filterId: string) => {
    setActiveFilters((prev: string[]) => (prev.includes(filterId) ? prev.filter((id: string) => id !== filterId) : [...prev, filterId]))
  }

  // Convert user reports to CityEvent format for live feeds
  const userSubmittedEvents: CityEvent[] = userReports.map((report, index) => ({
    id: 1000 + index, // Unique ID for user reports
    type: report.category || 'general',
    title: report.title || 'Citizen Report',
    location: report.address || `${report.latitude}, ${report.longitude}`,
    timestamp: new Date(report.timestamp || Date.now()),
    severity: report.severity || 'medium',
    summary: report.summary || report.description || 'User-submitted report',
    reporter: {
      name: user?.name || 'Anonymous Citizen',
      avatar: user?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.id || 'anonymous'}`,
      verified: true, // User reports are verified
      followers: 0
    },
    coordinates: { 
      x: report.longitude ? ((report.longitude + 180) / 360) * 100 : 50, // Convert lng to percentage
      y: report.latitude ? ((90 - report.latitude) / 180) * 100 : 50 // Convert lat to percentage
    },
    likes: Math.floor(Math.random() * 50),
    comments: Math.floor(Math.random() * 20),
    shares: Math.floor(Math.random() * 10),
    bookmarks: Math.floor(Math.random() * 15),
    image: report.image_url || null,
    tags: [report.category || 'citizen-report', 'ai-classified'],
    customEmoji: '📸' // Camera emoji for user reports
  }))

  const filteredEvents: CityEvent[] = [...userSubmittedEvents].filter(event => 
    activeFilters.includes(event.type) &&
    (searchQuery === '' || 
     event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
     event.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
     event.location.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: chatInput,
      sender: "user",
      timestamp: new Date(),
    }

    setChatMessages((prev) => [...prev, userMessage])
    setChatInput("")
    setIsTyping(true)

    try {
      const response = await sendChatMessage(currentCity, chatInput)
      
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: response.reply,
        sender: "bot",
        timestamp: new Date(),
        locationData: response.location_data, // Add location data for map display
      }

      setChatMessages((prev) => [...prev, botMessage])
      
      // If there's location data, display it on the map
      if (response.location_data && response.location_data.locations_to_display) {
        // Update the map with location data
        setLocationData(response.location_data)
        console.log("Location data received:", response.location_data.locations_to_display)
      } else {
        // Clear location data if no new data
        setLocationData(null)
      }
      
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I encountered an error. Please try again.",
        sender: "bot",
        timestamp: new Date(),
      }
      setChatMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleLikeEvent = (eventId: number) => {
    setLikedEvents((prev: Set<number>) => {
      const newSet = new Set(prev)
      if (newSet.has(eventId)) {
        newSet.delete(eventId)
      } else {
        newSet.add(eventId)
      }
      return newSet
    })
  }

  const handleBookmarkEvent = (eventId: number) => {
    setBookmarkedEvents((prev: Set<number>) => {
      const newSet = new Set(prev)
      if (newSet.has(eventId)) {
        newSet.delete(eventId)
      } else {
        newSet.add(eventId)
      }
      return newSet
    })
  }

  const handleCameraCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      const video = document.createElement("video")
      video.srcObject = stream
      video.play()

      video.addEventListener("loadedmetadata", () => {
        const canvas = document.createElement("canvas")
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        const ctx = canvas.getContext("2d")
        ctx?.drawImage(video, 0, 0)

        canvas.toBlob(
          (blob) => {
            if (blob) {
              const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" })
              setReportForm((prev: { title: string; description: string; type: string; image: File | null }) => ({ ...prev, image: file }))
              setCapturedImage(canvas.toDataURL())
            }
          },
          "image/jpeg",
          0.8,
        )

        stream.getTracks().forEach((track) => track.stop())
      })
    } catch (error) {
      console.error("Camera access denied:", error)
      fileInputRef.current?.click()
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setReportForm((prev: { title: string; description: string; type: string; image: File | null }) => ({ ...prev, image: file }))
      const reader = new FileReader()
      reader.onload = (e) => {
        setCapturedImage(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmitReport = () => {
    console.log("Report submitted:", reportForm)
    setShowReportModal(false)
    setReportForm({ title: "", description: "", type: "traffic", image: null })
    setCapturedImage(null)
  }

  const handleEventSelect = (event: any) => {
    setSelectedEvent(event)
  }

  const unreadNotifications = notifications.filter((n) => !n.read).length

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-cosmic-animated relative overflow-hidden">
        {/* Animated background particles */}
        <div className="particles absolute inset-0"></div>

        <div className="text-center relative z-10">
          <div className="relative mb-8">
            {/* Morphing logo container */}
            <div className="w-32 h-32 mx-auto mb-6 relative">
              <div className="absolute inset-0 bg-gradient-primary rounded-full animate-pulse opacity-20"></div>
              <div className="absolute inset-2 bg-gradient-secondary rounded-full animate-pulse opacity-40 animation-delay-100"></div>
              <div className="absolute inset-4 bg-gradient-accent rounded-full animate-pulse opacity-60 animation-delay-200"></div>
              <div className="absolute inset-6 glass-strong rounded-full flex items-center justify-center">
                <Sparkles className="w-12 h-12 text-white animate-float" />
              </div>
            </div>

            {/* Enhanced loading spinner */}
            <div className="relative">
              <div className="w-32 h-32 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-8 glow-primary"></div>
              <div className="absolute inset-0 w-32 h-32 border-4 border-transparent border-r-blue-400 rounded-full animate-spin mx-auto animation-delay-150"></div>
              <div className="absolute inset-0 w-32 h-32 border-4 border-transparent border-b-slate-300 rounded-full animate-spin mx-auto animation-delay-300"></div>
            </div>
          </div>

          <div className="space-y-6">
            {/* Animated title with glassmorphism */}
            <div className="glass px-8 py-4 rounded-2xl">
              <h2 className="text-4xl font-black text-gradient-primary animate-gradient mb-2">
                Urban Pulse
              </h2>
              <p className="text-lg font-medium text-white/90 animate-fadeInUp">
                Initializing City Intelligence Platform...
              </p>
            </div>

            {/* Floating status indicators */}
            <div className="flex justify-center space-x-4 mt-8">
              <div className="glass-subtle px-4 py-2 rounded-full flex items-center space-x-2 animate-float">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-white/80 text-sm">AI Systems</span>
              </div>
              <div className="glass-subtle px-4 py-2 rounded-full flex items-center space-x-2 animate-float animation-delay-200">
                <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-white/80 text-sm">Map Data</span>
              </div>
                <div className="glass-subtle px-4 py-2 rounded-full flex items-center space-x-2 animate-float animation-delay-400">
                <div className="w-3 h-3 bg-slate-400 rounded-full animate-pulse"></div>
                <span className="text-white/80 text-sm">User Profile</span>
              </div>
            </div>

            {/* Progress bar */}
            <div className="glass px-6 py-3 rounded-full max-w-xs mx-auto">
              <div className="w-full bg-white/20 rounded-full h-2 overflow-hidden">
                <div className="h-full bg-gradient-primary rounded-full animate-pulse" style={{width: '70%'}}></div>
              </div>
              <p className="text-xs text-white/70 mt-2">Loading city insights...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-cosmic-animated relative overflow-hidden">
      {/* Animated background particles */}
      <div className="particles absolute inset-0 pointer-events-none"></div>

      {/* Enhanced Header */}
      <Header
        isDarkMode={isDarkMode}
        setIsDarkMode={handleDarkModeToggle}
        isMobile={isMobile}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        showNotifications={showNotifications}
        setShowNotifications={setShowNotifications}
        notifications={notifications}
        unreadNotifications={unreadNotifications}
        notificationRef={notificationRef}
        currentTime={currentTime}
        liveStats={liveStats}
        user={user}
        onLogout={onLogout}
      />

      <div className="flex-1 flex overflow-hidden relative">

        {/* Mobile Sidebar Overlay */}
        {isMobile && sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Enhanced Left Sidebar with Social Feed */}
        <motion.div
          initial={{ x: -300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        >
          <Sidebar
            isMobile={isMobile}
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
            isDarkMode={isDarkMode}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            activeFilters={activeFilters}
            toggleFilter={toggleFilter}
            filteredEvents={filteredEvents}
            handleEventSelect={handleEventSelect}
            mobileChatExpanded={mobileChatExpanded}
          />
        </motion.div>

        {/* Main Map Area - Center Focus */}
        <motion.div
          className={`flex-1 p-2 md:p-4 lg:p-8 ${isMobile && mobileChatExpanded ? "pb-80" : ""}`}
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
        >
          <div className="h-full glass-strong rounded-2xl md:rounded-3xl border shadow-2xl overflow-hidden relative transition-all duration-500 card-modern group">
            {/* Enhanced Map Controls */}
            <motion.div
              className="absolute top-4 md:top-6 left-4 md:left-6 z-10"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.4 }}
            >
              <div className="glass px-3 md:px-4 py-2 shadow-lg font-semibold transition-all duration-300 hover:scale-105 text-xs md:text-sm text-white border border-white/20">
                <Activity className="w-3 h-3 md:w-4 md:h-4 mr-1 md:mr-2 animate-pulse text-blue-300" />
                {filteredEvents.length} events visible
              </div>
            </motion.div>

            <GoogleMap
              events={filteredEvents}
              selectedEvent={selectedEvent}
              onEventSelect={handleEventSelect}
              eventTypes={eventTypes}
              isDarkMode={isDarkMode}
              locationData={locationData}
              userReports={userReports}
              loadingReports={loadingReports}
            />

            {/* Enhanced Floating Camera Button */}
            <motion.button
              onClick={() => setShowReportModal(true)}
              className="absolute bottom-4 md:bottom-6 right-4 md:right-6 z-20 w-12 h-12 md:w-14 md:h-14 glass-strong rounded-full shadow-2xl transition-all duration-300 hover:scale-110 active:scale-95 btn-modern glow-primary group"
              title="Report an Event"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 1, duration: 0.5, type: "spring", stiffness: 200 }}
              whileHover={{ scale: 1.1, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
            >
              <Camera className="w-5 h-5 md:w-6 md:h-6 text-white group-hover:text-blue-200 transition-colors" />
            </motion.button>
          </div>
        </motion.div>

        {/* Fixed-Width Chat Panel */}
        <motion.div
          className={`${rightPanelCollapsed ? 'w-0' : 'w-80'} transition-all duration-300 flex-shrink-0 border-l ${isDarkMode ? 'border-gray-600' : 'border-gray-200'}`}
          initial={{ x: 300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3, ease: "easeOut" }}
        >
          <Chat
            isDarkMode={isDarkMode}
            rightPanelCollapsed={rightPanelCollapsed}
            setRightPanelCollapsed={setRightPanelCollapsed}
            chatMessages={chatMessages}
            chatInput={chatInput}
            setChatInput={setChatInput}
            isTyping={isTyping}
            handleSendMessage={handleSendMessage}
            chatMessagesRef={chatMessagesRef}
          />
        </motion.div>
      </div>

      {/* Enhanced Report Modal */}
      <ReportModal
        isDarkMode={isDarkMode}
        show={showReportModal}
        onClose={() => setShowReportModal(false)}
        reportForm={reportForm}
        setReportForm={setReportForm}
        handleCameraCapture={handleCameraCapture}
        fileInputRef={fileInputRef}
        handleFileUpload={handleFileUpload}
        capturedImage={capturedImage}
        setCapturedImage={setCapturedImage}
        handleSubmitReport={handleSubmitReport}
        eventTypes={eventTypes}
      />


    </div>
  )
}