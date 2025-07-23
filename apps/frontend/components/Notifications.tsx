import React from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Bell, AlertTriangle, MessageCircle, TrendingUp, Cloud } from "lucide-react"

interface Notification {
  id: number
  type: string
  title: string
  message: string
  time: string
  read: boolean
}

interface NotificationsProps {
  isDarkMode: boolean
  showNotifications: boolean
  setShowNotifications: (show: boolean) => void
  notificationRef: React.RefObject<HTMLDivElement>
  notifications: Notification[]
  unreadNotifications: number
}

const Notifications: React.FC<NotificationsProps> = ({
  isDarkMode,
  showNotifications,
  setShowNotifications,
  notificationRef,
  notifications,
  unreadNotifications,
}) => {
  return (
    <div className="relative" ref={notificationRef}>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setShowNotifications(!showNotifications)}
        className={`relative w-9 h-9 md:w-12 md:h-12 rounded-lg md:rounded-2xl shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-xl ${
          isDarkMode ? "hover:bg-gray-700/50" : "hover:bg-white/60"
        }`}
      >
        <Bell className={`w-4 h-4 md:w-5 md:h-5 ${showNotifications ? "animate-swing" : ""}`} />
        {unreadNotifications > 0 && (
          <span className="absolute -top-1 -right-1 w-4 h-4 md:w-5 md:h-5 bg-gradient-to-r from-red-500 to-pink-500 rounded-full animate-pulse shadow-lg shadow-red-500/50 flex items-center justify-center">
            <span className="text-xs text-white font-bold">{unreadNotifications}</span>
          </span>
        )}
      </Button>

      {/* Fixed Notifications Dropdown */}
      {showNotifications && (
        <div
          className={`absolute top-12 md:top-16 right-0 w-80 md:w-96 backdrop-blur-xl rounded-2xl md:rounded-3xl border shadow-2xl p-4 md:p-6 z-[9999] transform transition-all duration-300 animate-slideDown ${
            isDarkMode
              ? "bg-gray-800/90 border-gray-600/30 shadow-blue-900/40"
              : "bg-white/90 border-white/30 shadow-blue-500/10"
          }`}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className={`font-bold text-base md:text-lg ${isDarkMode ? "text-gray-100" : "text-gray-900"}`}>
              Notifications
            </h3>
            <Badge className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-3 py-1 animate-pulse">
              {unreadNotifications} new
            </Badge>
          </div>
          <div className="space-y-3 max-h-80 md:max-h-96 overflow-y-auto">
            {notifications.map((notification, index) => (
              <div
                key={notification.id}
                className={`p-3 md:p-4 rounded-xl md:rounded-2xl border shadow-sm transition-all duration-300 hover:scale-[1.02] hover:shadow-md animate-fadeInUp ${
                  notification.type === "emergency"
                    ? "bg-gradient-to-r from-red-50 to-pink-50 border-red-100 dark:from-red-900/20 dark:to-pink-900/20 dark:border-red-800/30"
                    : notification.type === "report"
                      ? "bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-100 dark:from-blue-900/20 dark:to-indigo-900/20 dark:border-blue-800/30"
                      : notification.type === "traffic"
                        ? "bg-gradient-to-r from-green-50 to-emerald-50 border-green-100 dark:from-green-900/20 dark:to-emerald-900/20 dark:border-green-800/30"
                        : "bg-gradient-to-r from-amber-50 to-orange-50 border-amber-100 dark:from-amber-900/20 dark:to-orange-900/20 dark:border-amber-800/30"
                }`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-start space-x-3">
                  {notification.type === "emergency" && (
                    <AlertTriangle className="w-4 h-4 md:w-5 md:h-5 text-red-600 mt-0.5 animate-pulse" />
                  )}
                  {notification.type === "report" && (
                    <MessageCircle className="w-4 h-4 md:w-5 md:h-5 text-blue-600 mt-0.5" />
                  )}
                  {notification.type === "traffic" && (
                    <TrendingUp className="w-4 h-4 md:w-5 md:h-5 text-green-600 mt-0.5" />
                  )}
                  {notification.type === "weather" && (
                    <Cloud className="w-4 h-4 md:w-5 md:h-5 text-amber-600 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <p
                        className={`text-sm font-semibold ${
                          notification.type === "emergency"
                            ? "text-red-800 dark:text-red-200"
                            : notification.type === "report"
                              ? "text-blue-800 dark:text-blue-200"
                              : notification.type === "traffic"
                                ? "text-green-800 dark:text-green-200"
                                : "text-amber-800 dark:text-amber-200"
                        }`}
                      >
                        {notification.title}
                      </p>
                      {!notification.read && (
                        <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                      )}
                    </div>
                    <p
                      className={`text-xs ${
                        notification.type === "emergency"
                          ? "text-red-600 dark:text-red-300"
                          : notification.type === "report"
                            ? "text-blue-600 dark:text-blue-300"
                            : notification.type === "traffic"
                              ? "text-green-600 dark:text-green-300"
                              : "text-amber-600 dark:text-amber-300"
                      }`}
                    >
                      {notification.message}
                    </p>
                    <p className={`text-xs mt-1 ${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
                      {notification.time}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Notifications 