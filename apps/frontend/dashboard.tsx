"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
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
  TreePine,
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
import OnboardingFlow from "./components/OnboardingFlow"
import ImageUploadModal from "./components/ImageUploadModal"
import { getSeverityColor, formatTimeAgo } from "./lib/utils"

import { sendChatMessage, getLocationMood } from "@/lib/api"
import { ChatMessage } from "@/types/chat"
import { auth, db } from "./lib/firebase"
import { onAuthStateChanged, signOut, User as FirebaseUser } from "firebase/auth"
import { doc, setDoc, getDoc, collection, addDoc, onSnapshot, query, where, orderBy, limit } from "firebase/firestore"

interface UserPreferences {
  interests: string[];
  customInterests: string[];
  location: string;
  radius: number;
  notificationTypes: string[];
}

interface CityEvent {
  id: string;
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
  coordinates: { lat: number; lng: number };
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
    color: "#f59e0b",
    gradient: "from-amber-500 via-orange-500 to-red-500",
    lightBg: "from-amber-50 to-orange-100",
    darkBg: "from-amber-950/50 to-orange-950/50",
    description: "Construction and maintenance",
    emoji: "🏗️",
  },
  {
    id: "events",
    label: "Events & Culture",
    icon: Calendar,
    color: "#8b5cf6",
    gradient: "from-purple-500 via-violet-500 to-indigo-500",
    lightBg: "from-purple-50 to-violet-100",
    darkBg: "from-purple-950/50 to-violet-950/50",
    description: "Local events and activities",
    emoji: "🎉",
  },
  {
    id: "safety",
    label: "Safety & Security",
    icon: Shield,
    color: "#ef4444",
    gradient: "from-red-500 via-pink-500 to-rose-500",
    lightBg: "from-red-50 to-pink-100",
    darkBg: "from-red-950/50 to-pink-950/50",
    description: "Emergency and safety alerts",
    emoji: "🚨",
  },
  {
    id: "environment",
    label: "Environment",
    icon: TreePine,
    color: "#10b981",
    gradient: "from-emerald-500 via-teal-500 to-cyan-500",
    lightBg: "from-emerald-50 to-teal-100",
    darkBg: "from-emerald-950/50 to-teal-950/50",
    description: "Environmental monitoring",
    emoji: "🌱",
  },
  {
    id: "community",
    label: "Community",
    icon: Users,
    color: "#06b6d4",
    gradient: "from-cyan-500 via-blue-500 to-indigo-500",
    lightBg: "from-cyan-50 to-blue-100",
    darkBg: "from-cyan-950/50 to-blue-950/50",
    description: "Community activities",
    emoji: "👥",
  },
]

export default function UrbanPulseDashboard() {
  // Authentication and onboarding state
  const [user, setUser] = useState<FirebaseUser | null>(null);
  const [userPreferences, setUserPreferences] = useState<UserPreferences | null>(null);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // UI state
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showImageUpload, setShowImageUpload] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<CityEvent | null>(null)
  const [showReportModal, setShowReportModal] = useState(false)
  const [mobileChatExpanded, setMobileChatExpanded] = useState(false)

  // Report form state
  const [reportForm, setReportForm] = useState({
    title: '',
    description: '',
    location: '',
    type: 'traffic',
    image: null as string | null
  })
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Data state
  const [events, setEvents] = useState<CityEvent[]>([])
  const [filteredEvents, setFilteredEvents] = useState<CityEvent[]>([])
  const [activeFilters, setActiveFilters] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [currentTime, setCurrentTime] = useState(new Date())
  const [notifications, setNotifications] = useState<any[]>([])
  const [unreadNotifications, setUnreadNotifications] = useState(0)
  const [zones, setZones] = useState<any[]>([])

  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [newMessage, setNewMessage] = useState("")
  const [isChatLoading, setIsChatLoading] = useState(false)

  // Refs
  const notificationRef = useRef<HTMLDivElement>(null)
  const chatRef = useRef<HTMLDivElement>(null)

  // Live stats
  const liveStats = {
    activeEvents: events.length,
    citizensOnline: Math.floor(Math.random() * 1000) + 500,
  }



  // Report form handlers
  const handleCameraCapture = () => {
    // For now, we'll simulate camera capture
    // In a real app, you'd use the device camera
    const mockImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk1vY2sgSW1hZ2U8L3RleHQ+PC9zdmc+'
    setCapturedImage(mockImage)
    setReportForm(prev => ({ ...prev, image: mockImage }))
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        const imageData = event.target?.result as string
        setCapturedImage(imageData)
        setReportForm(prev => ({ ...prev, image: imageData }))
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmitReport = async () => {
    if (!user) return

    try {
      // Save event to Firestore
      await addDoc(collection(db, 'events'), {
        ...reportForm,
        userId: user.uid,
        reporter: {
          name: user.displayName || 'Anonymous',
          avatar: user.photoURL || '',
          verified: true,
          followers: 0
        },
        timestamp: new Date(),
        severity: 'medium',
        summary: reportForm.description,
        likes: 0,
        comments: 0,
        shares: 0,
        bookmarks: 0,
        tags: [...userPreferences?.interests || [], ...userPreferences?.customInterests || []],
        coordinates: { lat: 0, lng: 0 }, // Will be geocoded later
        customEmoji: eventTypes.find(t => t.id === reportForm.type)?.emoji || '📌',
        createdAt: new Date(),
        updatedAt: new Date()
      })

      // Reset form
      setReportForm({
        title: '',
        description: '',
        location: '',
        type: 'traffic',
        image: null
      })
      setCapturedImage(null)
      setShowReportModal(false)
    } catch (error) {
      console.error('Error saving event:', error)
    }
  }

  const resetReportForm = () => {
    setReportForm({
      title: '',
      description: '',
      location: '',
      type: 'traffic',
      image: null
    })
    setCapturedImage(null)
  }

  // Check mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    checkMobile()
    window.addEventListener("resize", checkMobile)
    return () => window.removeEventListener("resize", checkMobile)
  }, [])

  // Authentication effect
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser);
        // Check if user has completed onboarding
        const userDoc = await getDoc(doc(db, 'users', firebaseUser.uid));
        if (userDoc.exists() && userDoc.data()?.onboardingComplete) {
          setUserPreferences(userDoc.data()?.preferences);
          setShowOnboarding(false);
        } else {
          setShowOnboarding(true);
        }
      } else {
        setUser(null);
        setUserPreferences(null);
        setShowOnboarding(true);
      }
      setIsLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Real-time events listener
  useEffect(() => {
    if (!user) return;

    // Listen to events that match user preferences
    const eventsQuery = query(
      collection(db, 'events'),
      orderBy('timestamp', 'desc'),
      limit(50)
    );

    const unsubscribe = onSnapshot(eventsQuery, (snapshot) => {
      const eventsData: CityEvent[] = [];
      snapshot.forEach((doc) => {
        const data = doc.data();
        eventsData.push({
          id: doc.id,
          ...data,
          timestamp: data.timestamp?.toDate() || new Date(),
        } as CityEvent);
      });
      setEvents(eventsData);
    });

    return () => unsubscribe();
  }, [user]);

  // Function to refresh events (can be called after new reports)
  const refreshEvents = () => {
    // The real-time listener will automatically update the events
    // This function can be used to trigger additional updates if needed
    console.log('Events refreshed');
  };

  // Filter events based on user preferences
  useEffect(() => {
    if (!userPreferences) {
      setFilteredEvents(events);
      return;
    }

    let filtered = events;

    // Filter by user interests
    if (userPreferences.interests.length > 0 || userPreferences.customInterests.length > 0) {
      const allInterests = [...userPreferences.interests, ...userPreferences.customInterests];
      filtered = filtered.filter(event => 
        allInterests.some(interest => 
          (event.title?.toLowerCase() || '').includes(interest.toLowerCase()) ||
          (event.summary?.toLowerCase() || '').includes(interest.toLowerCase()) ||
          (event.tags || []).some(tag => (tag?.toLowerCase() || '').includes(interest.toLowerCase()))
        )
      );
    }

    // Filter by active filters
    if (activeFilters.length > 0) {
      filtered = filtered.filter(event => activeFilters.includes(event.type));
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(event =>
        (event.title?.toLowerCase() || '').includes(searchQuery.toLowerCase()) ||
        (event.location?.toLowerCase() || '').includes(searchQuery.toLowerCase()) ||
        (event.summary?.toLowerCase() || '').includes(searchQuery.toLowerCase())
      );
    }

    setFilteredEvents(filtered);
  }, [events, userPreferences, activeFilters, searchQuery]);

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 60000)
    return () => clearInterval(timer)
  }, [])

  // Click outside handlers
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setShowNotifications(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  // Filter toggle
  const toggleFilter = (filterId: string) => {
    setActiveFilters(prev =>
      prev.includes(filterId)
        ? prev.filter(id => id !== filterId)
        : [...prev, filterId]
    )
  }

  // Chat handlers
  const handleSendMessage = async () => {
    if (!newMessage.trim() || !user) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: newMessage,
      sender: "user",
      timestamp: new Date(),
    }

    setChatMessages(prev => [...prev, userMessage])
    setNewMessage("")
    setIsChatLoading(true)

    try {
      const response = await sendChatMessage(user.uid, newMessage)

      const botMessage: ChatMessage = {
        id: Date.now().toString(),
        text: response.reply,
        sender: "bot",
        timestamp: new Date(),
      }

      setChatMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I'm having trouble processing your request. Please try again.",
        sender: "bot",
        timestamp: new Date(),
      }
      setChatMessages(prev => [...prev, errorMessage])
    } finally {
      setIsChatLoading(false)
    }
  }

  // Event handlers
  const handleLikeEvent = (eventId: string) => {
    setEvents(prev =>
      prev.map(event =>
        event.id === eventId
          ? { ...event, likes: event.likes + 1 }
          : event
      )
    )
  }

  const handleBookmarkEvent = (eventId: string) => {
    setEvents(prev =>
      prev.map(event =>
        event.id === eventId
          ? { ...event, bookmarks: event.bookmarks + 1 }
          : event
      )
    )
  }

  // Image upload handlers
  const handleImageUpload = async (eventData: any) => {
    if (!user) return;

    try {
      // Save event to Firestore
      await addDoc(collection(db, 'events'), {
        ...eventData,
        userId: user.uid,
        reporter: {
          name: user.displayName || 'Anonymous',
          avatar: user.photoURL || '',
          verified: true,
          followers: 0
        },
        likes: 0,
        comments: 0,
        shares: 0,
        bookmarks: 0,
        tags: [...userPreferences?.interests || [], ...userPreferences?.customInterests || []],
        createdAt: new Date(),
        updatedAt: new Date()
      });

      setShowImageUpload(false);
    } catch (error) {
      console.error('Error saving event:', error);
    }
  };

  // Onboarding completion handler
  const handleOnboardingComplete = (user: FirebaseUser, preferences: UserPreferences) => {
    setUserPreferences(preferences);
    setShowOnboarding(false);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Show onboarding if not completed
  if (showOnboarding) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />;
  }

  return (
    <div className={`min-h-screen transition-colors duration-500 ${isDarkMode ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900"}`}>
      {/* Header */}
      <Header
        isDarkMode={isDarkMode}
        isMobile={isMobile}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        liveStats={liveStats}
        currentTime={currentTime}
        showNotifications={showNotifications}
        setShowNotifications={setShowNotifications}
        notificationRef={notificationRef as React.RefObject<HTMLDivElement>}
        notifications={notifications}
        unreadNotifications={unreadNotifications}
      />

      {/* Main Content */}
      <div className="flex h-[calc(100vh-5rem)] pt-16 md:pt-20">
        {/* Sidebar */}
        <Sidebar
          isDarkMode={isDarkMode}
          isMobile={isMobile}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          activeFilters={activeFilters}
          toggleFilter={toggleFilter}
          filteredEvents={filteredEvents}
          handleEventSelect={(event) => setSelectedEvent(event as CityEvent)}
          mobileChatExpanded={mobileChatExpanded}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex">
          {/* Map Section */}
          <div className="flex-1 relative">
            <GoogleMap
              events={filteredEvents}
              selectedEvent={selectedEvent}
              onEventSelect={(event) => setSelectedEvent(event as CityEvent)  }
              eventTypes={eventTypes}
              isDarkMode={isDarkMode}
              zones={zones}
              onEventsUpdate={refreshEvents}
            />
            
            {/* Floating Action Button */}
            <div className="absolute bottom-6 right-6 z-10">
              <Button
                onClick={() => setShowImageUpload(true)}
                className="w-14 h-14 rounded-full shadow-lg bg-blue-600 hover:bg-blue-700"
              >
                <Camera className="w-6 h-6" />
              </Button>
            </div>
          </div>

          {/* Right Panel - Events Feed and Chat */}
          <div className="w-96 border-l border-gray-200 dark:border-gray-700 flex flex-col h-full">
            {/* Events Feed Section */}
            <div className="flex-1 flex flex-col min-h-0">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Live Events</h2>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowReportModal(true)}
                  >
                    Report Event
                  </Button>
                </div>
                
                {/* Search */}
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="Search events..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                {/* Filters */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {eventTypes.map((type) => (
                    <Badge
                      key={type.id}
                      variant={activeFilters.includes(type.id) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => toggleFilter(type.id)}
                    >
                      {type.emoji} {type.label}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Events List */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {filteredEvents.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No events found</p>
                    <p className="text-sm">Try adjusting your filters or search terms</p>
                  </div>
                ) : (
                  filteredEvents.map((event) => (
                    <div
                      key={event.id}
                      className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                        isDarkMode
                          ? "bg-gray-800 border-gray-700 hover:bg-gray-750"
                          : "bg-white border-gray-200 hover:bg-gray-50"
                      }`}
                      onClick={() => setSelectedEvent(event)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="text-2xl">{event.customEmoji}</span>
                          <div>
                            <h3 className="font-semibold text-sm">{event.title}</h3>
                            <p className="text-xs text-gray-500 flex items-center">
                              <MapPin className="w-3 h-3 mr-1" />
                              {event.location}
                            </p>
                          </div>
                        </div>
                        <Badge
                          variant="outline"
                          className={`text-xs ${getSeverityColor(event.severity)}`}
                        >
                          {event.severity}
                        </Badge>
                      </div>
                      
                      <p className="text-sm text-gray-600 dark:text-gray-300 mb-3 line-clamp-2">
                        {event.summary}
                      </p>
                      
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {formatTimeAgo(event.timestamp)}
                        </span>
                        <div className="flex items-center space-x-4">
                          <span className="flex items-center">
                            <Heart className="w-3 h-3 mr-1" />
                            {event.likes}
                          </span>
                          <span className="flex items-center">
                            <MessageCircle className="w-3 h-3 mr-1" />
                            {event.comments}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Chat Section */}
            <div className="h-80 border-t border-gray-200 dark:border-gray-700">
              <Chat
                chatMessages={chatMessages}
                chatInput={newMessage}
                setChatInput={setNewMessage}
                handleSendMessage={handleSendMessage}
                isTyping={isChatLoading}
                isDarkMode={isDarkMode}
                chatMessagesRef={chatRef as React.RefObject<HTMLDivElement>}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <ImageUploadModal
        isOpen={showImageUpload}
        onClose={() => setShowImageUpload(false)}
        onSubmit={handleImageUpload}
        userLocation={userPreferences?.location ? { lat: 0, lng: 0 } : undefined}
      />

      <ReportModal
        show={showReportModal}
        onClose={() => setShowReportModal(false)}
        reportForm={reportForm}
        setReportForm={setReportForm}
        capturedImage={capturedImage}
        setCapturedImage={setCapturedImage}
        handleCameraCapture={handleCameraCapture}
        handleFileUpload={handleFileUpload}
        fileInputRef={fileInputRef as React.RefObject<HTMLInputElement>}
        handleSubmitReport={handleSubmitReport}
        eventTypes={eventTypes}
        isDarkMode={isDarkMode}
      />

      {/* Notifications */}
      <Notifications
        showNotifications={showNotifications}
        setShowNotifications={setShowNotifications}
        notifications={notifications as any}
        unreadNotifications={unreadNotifications}
        notificationRef={notificationRef as React.RefObject<HTMLDivElement>}
        isDarkMode={isDarkMode}
      />
    </div>
  )
}
