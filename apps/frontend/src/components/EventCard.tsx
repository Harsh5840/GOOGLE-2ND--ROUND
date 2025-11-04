import React from "react"

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
  return (
    <div
      className={`p-4 rounded-xl border shadow-sm cursor-pointer hover:scale-[1.01] transition-transform duration-200 ${isDarkMode ? "bg-gray-800/60 border-gray-600/30" : "bg-white/60 border-white/40"}`}
      onClick={() => onSelect(event)}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="font-semibold text-sm">{event.title}</span>
        <span className="text-xs text-gray-400">{event.location}</span>
      </div>
      <div className="text-xs text-gray-500">{event.summary}</div>
      {/* Action buttons (like, bookmark) can be added here */}
    </div>
  )
}

export default EventCard 