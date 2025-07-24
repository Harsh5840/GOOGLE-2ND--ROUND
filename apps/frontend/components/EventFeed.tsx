import React from "react"
import EventCard from "./EventCard"

interface EventFeedProps {
  events: any[]
  isDarkMode: boolean
  onLike: (id: number) => void
  onBookmark: (id: number) => void
  onSelect: (event: any) => void
  likedEvents: Set<number>
  bookmarkedEvents: Set<number>
}

const EventFeed: React.FC<EventFeedProps> = ({
  events,
  isDarkMode,
  onLike,
  onBookmark,
  onSelect,
  likedEvents,
  bookmarkedEvents,
}) => {
  return (
    <div className="space-y-4">
      {events.map((event) => (
        <EventCard
          key={event.id}
          event={event}
          isDarkMode={isDarkMode}
          onLike={onLike}
          onBookmark={onBookmark}
          onSelect={onSelect}
          liked={likedEvents.has(event.id)}
          bookmarked={bookmarkedEvents.has(event.id)}
        />
      ))}
    </div>
  )
}

export default EventFeed 