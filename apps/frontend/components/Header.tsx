import React from "react"
import { Button } from "@/components/ui/button"
import { Activity, Menu, Users } from "lucide-react"

interface HeaderProps {
  isDarkMode: boolean
  isMobile: boolean
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  liveStats: {
    activeEvents: number
    citizensOnline: number
  }
  currentTime: Date
  showNotifications: boolean
  setShowNotifications: (show: boolean) => void
  notificationRef: React.RefObject<HTMLDivElement>
  notifications: any[]
  unreadNotifications: number
}

const Header: React.FC<HeaderProps> = ({
  isDarkMode,
  isMobile,
  sidebarOpen,
  setSidebarOpen,
  liveStats,
  currentTime,
  showNotifications,
  setShowNotifications,
  notificationRef,
  notifications,
  unreadNotifications,
}) => {
  return (
    <header
      className={`h-16 md:h-20 backdrop-blur-xl border-b flex items-center justify-between px-3 md:px-8 shadow-2xl transition-all duration-500 relative z-50 ${
        isDarkMode
          ? "bg-gray-900/90 border-gray-600/30 shadow-blue-900/40"
          : "bg-white/70 border-white/30 shadow-blue-500/5"
      }`}
    >
      <div className="flex items-center space-x-2 md:space-x-8 flex-1">
        {/* Mobile Menu Button */}
        {isMobile && (
          <Button
            // variant="ghost"
            // size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden w-9 h-9 rounded-xl flex-shrink-0"
          >
            <Menu className="w-4 h-4" />
          </Button>
        )}

        <div className="flex items-center space-x-2 md:space-x-4 group min-w-0">
          <div className="w-8 h-8 md:w-12 md:h-12 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-600 rounded-lg md:rounded-2xl flex items-center justify-center shadow-xl shadow-blue-500/25 group-hover:shadow-2xl group-hover:shadow-blue-500/40 transition-all duration-300 group-hover:scale-110 flex-shrink-0">
            <Activity className="w-4 h-4 md:w-7 md:h-7 text-white animate-pulse" />
          </div>
          <div className="min-w-0">
            <h1 className="text-base md:text-2xl font-black bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent truncate">
              CityScape
            </h1>
            <p
              className={`text-xs md:text-sm font-medium ${isDarkMode ? "text-gray-300" : "text-gray-600"} hidden sm:block`}
            >
              City Social Network
            </p>
          </div>
        </div>

        {/* Desktop Quick Stats */}
        <div className="hidden lg:flex items-center space-x-4">
          <div
            className={`flex items-center space-x-2 backdrop-blur-sm px-3 py-2 rounded-xl border shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-xl ${
              isDarkMode
                ? "bg-gray-800/60 border-gray-600/30 shadow-blue-900/10"
                : "bg-white/60 border-white/40 shadow-blue-500/5"
            }`}
          >
            <div className="w-2 h-2 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
            <span className={`text-sm font-semibold ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              {liveStats.activeEvents}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-2 md:space-x-6 flex-shrink-0">
        <div
          className={`text-xs md:text-sm font-medium backdrop-blur-sm px-2 md:px-5 py-2 md:py-3 rounded-lg md:rounded-2xl border shadow-lg transition-all duration-300 hover:scale-105 ${
            isDarkMode
              ? "text-gray-100 bg-gray-800/60 border-gray-600/30 shadow-blue-900/10"
              : "text-gray-600 bg-white/60 border-white/40 shadow-blue-500/5"
          }`}
        >
          {currentTime.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
      </div>
    </header>
  )
}

export default Header 