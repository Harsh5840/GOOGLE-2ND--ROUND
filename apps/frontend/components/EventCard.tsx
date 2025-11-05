import React from "react"
import { Heart, Bookmark, MapPin, Clock, Users, TrendingUp, AlertTriangle } from "lucide-react"

interface EventCardProps {
  event: any
  isDarkMode: boolean
  onLike: (id: number) => void
  onBookmark: (id: number) => void
  onSelect: (event: any) => void
  liked: boolean
  bookmarked: boolean
}

const EventCard: React.FC<EventCardProps> = ({
  event,
  isDarkMode,
  onLike,
  onBookmark,
  onSelect,
  liked,
  bookmarked,
}) => {
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'text-red-400 border-red-400/30'
      case 'medium':
        return 'text-yellow-400 border-yellow-400/30'
      case 'low':
        return 'text-green-400 border-green-400/30'
      default:
        return 'text-blue-400 border-blue-400/30'
    }
  }

  const getEventTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'traffic':
        return <TrendingUp className="w-4 h-4" />
      case 'accident':
        return <AlertTriangle className="w-4 h-4" />
      case 'construction':
        return <TrendingUp className="w-4 h-4" />
      case 'event':
        return <Users className="w-4 h-4" />
      default:
        return <MapPin className="w-4 h-4" />
    }
  }

  return (
    <div
      className="glass card-modern p-4 rounded-xl cursor-pointer group relative overflow-hidden"
      onClick={() => onSelect(event)}
    >
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header with emoji and type */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{event.customEmoji || '📍'}</span>
            <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(event.severity)} bg-white/10`}>
              {getEventTypeIcon(event.type)}
              <span className="ml-1 capitalize">{event.type}</span>
            </div>
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(event.severity)} bg-white/10 border`}>
            {event.severity}
          </div>
        </div>

        {/* Title and location */}
        <div className="mb-3">
          <h3 className="font-bold text-white text-lg mb-1 group-hover:text-gradient-primary transition-all duration-300">
            {event.title}
          </h3>
          <div className="flex items-center text-white/70 text-sm">
            <MapPin className="w-3 h-3 mr-1" />
            {event.location}
          </div>
        </div>

        {/* Summary */}
        <p className="text-white/80 text-sm mb-4 line-clamp-2">
          {event.summary}
        </p>

        {/* Footer with stats and actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 text-white/60 text-xs">
            <div className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
            <div className="flex items-center">
              <Users className="w-3 h-3 mr-1" />
              {event.likes}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation()
                onLike(event.id)
              }}
              className={`p-2 rounded-full transition-all duration-200 hover:scale-110 ${
                liked ? 'text-red-400 bg-red-400/20' : 'text-white/60 hover:text-red-400 hover:bg-red-400/10'
              }`}
            >
              <Heart className={`w-4 h-4 ${liked ? 'fill-current' : ''}`} />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onBookmark(event.id)
              }}
              className={`p-2 rounded-full transition-all duration-200 hover:scale-110 ${
                bookmarked ? 'text-blue-400 bg-blue-400/20' : 'text-white/60 hover:text-blue-400 hover:bg-blue-400/10'
              }`}
            >
              <Bookmark className={`w-4 h-4 ${bookmarked ? 'fill-current' : ''}`} />
            </button>
          </div>
        </div>

        {/* Reporter info */}
        <div className="mt-3 pt-3 border-t border-white/10">
          <div className="flex items-center space-x-2">
            <img
              src={event.reporter.avatar}
              alt={event.reporter.name}
              className="w-6 h-6 rounded-full border border-white/20"
            />
            <span className="text-white/70 text-xs">{event.reporter.name}</span>
            {event.reporter.verified && (
              <div className="w-2 h-2 bg-green-400 rounded-full" title="Verified reporter"></div>
            )}
          </div>
        </div>
      </div>

      {/* Hover glow effect */}
      <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 neon-border pointer-events-none"></div>
    </div>
  )
}

export default EventCard 