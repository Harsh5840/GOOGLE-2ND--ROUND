"use client"

import { useEffect, useRef, useState } from "react"

// Declare Google Maps types
declare global {
  interface Window {
    google: any
    initMap?: () => void
  }
}

interface EventType {
  id: string
  label: string
  icon: any
  color: string
  gradient: string
  emoji?: string // Added emoji property
}

interface Reporter {
  name: string
  avatar: string | null
  verified: boolean
  followers: number
}

interface Event {
  id: number
  type: string
  title: string
  location: string
  coordinates: { x: number; y: number }
  severity: string
  summary: string
  reporter: Reporter
  timestamp: Date | string
  likes: number
  comments: number
  shares: number
  bookmarks: number
  image: string | null
  tags: string[]
  customEmoji?: string
}

interface Zone {
  id: string
  name: string
  type: "traffic" | "pollution" | "happiness" | "safety"
  color: string
  opacity: number
  coordinates: { x: number; y: number; width: number; height: number }
  description: string
  severity: "low" | "medium" | "high"
  shape?: "blob" | "rectangle"
}

interface MapProps {
  events: Event[]
  selectedEvent: Event | null
  onEventSelect: (event: Event) => void
  eventTypes: EventType[]
  isDarkMode: boolean
  zones?: Zone[]
}

export default function GoogleMap({
  events,
  selectedEvent,
  onEventSelect,
  eventTypes,
  isDarkMode,
  zones = [],
}: MapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markersRef = useRef<any[]>([])
  const infoWindowRef = useRef<any>(null)
  const [mapError, setMapError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Convert percentage coordinates to lat/lng (approximate NYC area)
  const convertToLatLng = (x: number, y: number) => {
    // Bengaluru bounds approximately
    const bounds = {
      north: 13.1737,
      south: 12.7343,
      east: 77.8827,
      west: 77.3791,
    }

    const lat = bounds.south + (bounds.north - bounds.south) * (1 - y / 100)
    const lng = bounds.west + (bounds.east - bounds.west) * (x / 100)

    return { lat, lng }
  }

  // Convert zone coordinates to Google Maps polygon coordinates
  const convertZoneToPolygon = (zone: Zone) => {
    const { x, y, width, height } = zone.coordinates
    const bounds = {
      north: 13.1737,
      south: 12.7343,
      east: 77.8827,
      west: 77.3791,
    }

    if (zone.shape === "blob") {
      // Create organic blob-like shape
      const centerX = x + width / 2
      const centerY = y + height / 2
      const radiusX = width / 2
      const radiusY = height / 2
      
      const points = []
      const numPoints = 12
      
      for (let i = 0; i < numPoints; i++) {
        const angle = (i / numPoints) * 2 * Math.PI
        const randomRadiusX = radiusX * (0.7 + Math.random() * 0.6)
        const randomRadiusY = radiusY * (0.7 + Math.random() * 0.6)
        
        const pointX = centerX + randomRadiusX * Math.cos(angle)
        const pointY = centerY + randomRadiusY * Math.sin(angle)
        
        points.push({
          lat: bounds.south + (bounds.north - bounds.south) * (1 - pointY / 100),
          lng: bounds.west + (bounds.east - bounds.west) * (pointX / 100),
        })
      }
      
      return points
    } else {
      // Default rectangle shape
      const topLeft = {
        lat: bounds.south + (bounds.north - bounds.south) * (1 - y / 100),
        lng: bounds.west + (bounds.east - bounds.west) * (x / 100),
      }
      const topRight = {
        lat: bounds.south + (bounds.north - bounds.south) * (1 - y / 100),
        lng: bounds.west + (bounds.east - bounds.west) * ((x + width) / 100),
      }
      const bottomRight = {
        lat: bounds.south + (bounds.north - bounds.south) * (1 - (y + height) / 100),
        lng: bounds.west + (bounds.east - bounds.west) * ((x + width) / 100),
      }
      const bottomLeft = {
        lat: bounds.south + (bounds.north - bounds.south) * (1 - (y + height) / 100),
        lng: bounds.west + (bounds.east - bounds.west) * (x / 100),
      }

      return [topLeft, topRight, bottomRight, bottomLeft]
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "#dc2626"
      case "high":
        return "#ea580c"
      case "medium":
        return "#ca8a04"
      case "low":
        return "#16a34a"
      default:
        return "#6b7280"
    }
  }

  const createCustomMarker = (event: Event) => {
    const eventType = eventTypes.find((type) => type.id === event.type)
    const color = eventType?.color || "#6b7280"
    // Use custom emoji if available, otherwise fall back to event type emoji, then to pin
    const emoji = event.customEmoji || eventType?.emoji || "📍"

    // Check if we're on mobile for optimized marker size
    const isMobile = window.innerWidth < 768
    const markerSize = isMobile ? 36 : 48

    // Create optimized custom marker icon for mobile - removed animations for smoothness
    const svgMarker = `
      <svg width="${markerSize}" height="${markerSize}" viewBox="0 0 ${markerSize} ${markerSize}" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="grad${event.id}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:${color};stop-opacity:1" />
            <stop offset="100%" style="stop-color:${color}90;stop-opacity:1" />
          </linearGradient>
          <filter id="shadow${event.id}" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="rgba(0,0,0,0.3)"/>
          </filter>
        </defs>
        <circle cx="${markerSize/2}" cy="${markerSize/2}" r="${markerSize/2 - 2}" fill="url(#grad${event.id})" stroke="white" stroke-width="2" filter="url(#shadow${event.id})"/>
        <circle cx="${markerSize/2}" cy="${markerSize/2}" r="${markerSize/4}" fill="white" opacity="0.9"/>
        <circle cx="${markerSize/2}" cy="${markerSize/2}" r="${markerSize/8}" fill="${color}" opacity="0.8"/>
        ${event.likes > 10 ? `<circle cx="${markerSize * 0.67}" cy="${markerSize * 0.33}" r="4" fill="#ef4444" stroke="white" stroke-width="1"/>` : ""}
        <text x="${markerSize/2}" y="${markerSize * 0.65}" text-anchor="middle" font-size="${isMobile ? '16' : '20'}" font-family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, sans-serif">${emoji}</text>
      </svg>
    `

    return {
      url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svgMarker)}`,
      scaledSize: window.google ? new window.google.maps.Size(markerSize, markerSize) : undefined,
      anchor: window.google ? new window.google.maps.Point(markerSize/2, markerSize/2) : undefined,
      // Optimize for mobile performance
      optimized: true,
    }
  }

  // Accepts Date or string, returns "now", "Xm", or "Xh"
  const formatTimeAgo = (timestamp: Date | string) => {
    let dateObj: Date
    if (timestamp instanceof Date) {
      dateObj = timestamp
    } else {
      dateObj = new Date(timestamp)
    }
    const minutes = Math.floor((Date.now() - dateObj.getTime()) / 60000)
    if (minutes < 1) return "now"
    if (minutes < 60) return `${minutes}m`
    return `${Math.floor(minutes / 60)}h`
  }

  const initMap = () => {
    if (!mapRef.current || !window.google) return

    try {
      // Initialize map centered on Bengaluru with mobile-optimized settings
      const map = new window.google.maps.Map(mapRef.current, {
        center: { lat: 12.9716, lng: 77.5946 }, // Bengaluru
        zoom: 12,
        styles: [
          {
            featureType: "all",
            elementType: "geometry.fill",
            stylers: [{ color: "#f8fafc" }],
          },
          {
            featureType: "water",
            elementType: "geometry",
            stylers: [{ color: "#dbeafe" }],
          },
          {
            featureType: "road",
            elementType: "geometry",
            stylers: [{ color: "#ffffff" }],
          },
          {
            featureType: "road.highway",
            elementType: "geometry",
            stylers: [{ color: "#e2e8f0" }],
          },
          {
            featureType: "poi.park",
            elementType: "geometry",
            stylers: [{ color: "#ecfdf5" }],
          },
          {
            featureType: "poi",
            elementType: "labels.text",
            stylers: [{ visibility: "off" }],
          },
          {
            featureType: "transit",
            elementType: "labels.text",
            stylers: [{ visibility: "off" }],
          },
          {
            featureType: "administrative",
            elementType: "labels.text.fill",
            stylers: [{ color: "#64748b" }],
          },
          {
            featureType: "road",
            elementType: "labels.text.fill",
            stylers: [{ color: "#475569" }],
          },
        ],
        disableDefaultUI: true,
        zoomControl: true,
        zoomControlOptions: {
          position: window.google.maps.ControlPosition.RIGHT_TOP,
        },
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        // Mobile optimizations
        gestureHandling: "greedy", // Allows single finger panning
        draggable: true,
        scrollwheel: false, // Disable scroll wheel zoom on desktop
        // Performance optimizations
        maxZoom: 18,
        minZoom: 10,
        // Reduce map complexity for better performance
        backgroundColor: "#f8fafc",
        // Disable unnecessary features
        tilt: 0,
        heading: 0,
        // Optimize for mobile rendering
        mapTypeId: window.google.maps.MapTypeId.ROADMAP,
        // Smooth performance settings
        animation: window.google.maps.Animation.NONE,
        // Reduce rendering load
        clickableIcons: false,
      })

      mapInstanceRef.current = map
      infoWindowRef.current = new window.google.maps.InfoWindow()
      setIsLoading(false)
      setMapError(null)
    } catch (error: any) {
      handleGoogleMapsError(error)
    }
  }

  // Handle Google Maps API errors
  const handleGoogleMapsError = (error: any) => {
    setIsLoading(false)

    // Check for specific error types
    if (error && error.message && typeof error.message === "string") {
      if (error.message.includes("ApiTargetBlockedMapError")) {
        setMapError("Google Maps API key is blocked or invalid. Please check your API key configuration.")
      } else if (error.message.includes("RefererNotAllowedMapError")) {
        setMapError("This domain is not authorized to use the Google Maps API key.")
      } else if (error.message.includes("InvalidKeyMapError")) {
        setMapError("Invalid Google Maps API key.")
      } else {
        setMapError("Failed to load Google Maps. Please check your API key and configuration.")
      }
    } else {
      setMapError("Failed to load Google Maps. Please check your API key and configuration.")
    }
  }

  // Fallback map component
  const FallbackMap = () => (
    <div className="w-full h-full relative">
      <div
        className={`w-full h-full rounded-2xl md:rounded-3xl ${
          isDarkMode
            ? "bg-gradient-to-br from-gray-800 via-blue-900 to-indigo-900"
            : "bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"
        } overflow-hidden`}
      >
        {/* Fallback map with event markers */}
        <div className="relative w-full h-full">
          {/* Grid background */}
          <div
            className={`absolute inset-0 opacity-20 ${
              isDarkMode ? "bg-gray-700" : "bg-gray-300"
            }`}
            style={{
              backgroundImage: `linear-gradient(${
                isDarkMode ? "#374151" : "#e5e7eb"
              } 1px, transparent 1px), linear-gradient(90deg, ${
                isDarkMode ? "#374151" : "#e5e7eb"
              } 1px, transparent 1px)`,
              backgroundSize: "20px 20px",
            }}
          ></div>

          {/* NYC area representation */}
          <div
            className={`absolute inset-4 rounded-xl ${
              isDarkMode ? "bg-blue-900/30" : "bg-blue-100/50"
            } border-2 ${isDarkMode ? "border-blue-700" : "border-blue-300"}`}
          >
            <div className="absolute top-2 left-2 text-xs font-bold text-blue-600">
              NYC
            </div>

            {/* Zone overlays */}
            {zones.map((zone) => {
              const centerX = zone.coordinates.x + zone.coordinates.width / 2
              const centerY = zone.coordinates.y + zone.coordinates.height / 2
              const radiusX = zone.coordinates.width / 2
              const radiusY = zone.coordinates.height / 2
              
              // Generate organic blob path
              const points = []
              const numPoints = 12
              for (let i = 0; i < numPoints; i++) {
                const angle = (i / numPoints) * 2 * Math.PI
                const randomRadiusX = radiusX * (0.7 + Math.random() * 0.6)
                const randomRadiusY = radiusY * (0.7 + Math.random() * 0.6)
                
                const pointX = centerX + randomRadiusX * Math.cos(angle)
                const pointY = centerY + randomRadiusY * Math.sin(angle)
                
                points.push(`${pointX}% ${pointY}%`)
              }
              
              return (
                <div
                  key={zone.id}
                  className="absolute cursor-pointer hover:opacity-90 transition-opacity duration-300"
                  style={{
                    left: `${zone.coordinates.x}%`,
                    top: `${zone.coordinates.y}%`,
                    width: `${zone.coordinates.width}%`,
                    height: `${zone.coordinates.height}%`,
                    backgroundColor: zone.color,
                    opacity: isDarkMode ? Math.min(1, zone.opacity + 0.25) : zone.opacity,
                    clipPath: `polygon(${points.join(', ')})`,
                    border: isDarkMode ? '2px solid #fff' : undefined,
                    boxShadow: isDarkMode ? '0 0 12px 4px #0004' : undefined,
                  }}
                  title={`${zone.name} - ${zone.description}`}
                >
                  <div className="absolute top-1 left-1 text-xs font-bold text-white drop-shadow-lg">
                    {zone.type === "traffic" ? "🚗" : zone.type === "pollution" ? "🌫️" : zone.type === "happiness" ? "😊" : "🛡️"}
                  </div>
                </div>
              )
            })}

            {/* Event markers */}
            {events.map((event) => {
              const eventType = eventTypes.find((type) => type.id === event.type)
              const color = eventType?.color || "#6b7280"
              const emoji = event.customEmoji || eventType?.emoji || "📍"

              return (
                <div
                  key={event.id}
                  className="absolute cursor-pointer transform -translate-x-1/2 -translate-y-1/2 hover:scale-110 transition-all duration-300"
                  style={{
                    left: `${event.coordinates.x}%`,
                    top: `${event.coordinates.y}%`,
                  }}
                  onClick={() => onEventSelect(event)}
                >
                  <div
                    className="w-8 h-8 rounded-full border-2 border-white shadow-lg relative flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: color }}
                  >
                    <span className="text-sm">{emoji}</span>
                    {event.likes > 10 && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border border-white"></div>
                    )}
                  </div>
                  <div className="absolute top-10 left-1/2 transform -translate-x-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded whitespace-nowrap opacity-0 hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                    {event.title}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Error message */}
          <div className="absolute bottom-4 left-4 right-4 text-center">
            <div
              className={`inline-block px-4 py-2 rounded-lg ${
                isDarkMode
                  ? "bg-red-900/80 text-red-200 border border-red-700"
                  : "bg-red-100 text-red-800 border border-red-300"
              } text-sm font-medium`}
            >
              ⚠️ {mapError}
            </div>
            <div
              className={`mt-2 text-xs ${
                isDarkMode ? "text-gray-400" : "text-gray-600"
              }`}
            >
              Using fallback map view with event markers
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  useEffect(() => {
    // Only run on client
    if (typeof window === "undefined") return

    // Check if Google Maps is already loaded
    if (window.google && window.google.maps) {
      initMap()
      return
    }

    // Set up global callback
    window.initMap = initMap

    // Prevent duplicate script tags
    if (!document.querySelector('script[data-google-maps]')) {
      const script = document.createElement("script")
      // TODO: Replace 'YOUR_API_KEY_HERE' with your actual Google Maps API key
      script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyAabmFAVOqMWF96Yui6THYrkToNgrbNQXs&callback=initMap&libraries=places&v=weekly`
      script.async = true
      script.defer = true
      script.setAttribute("data-google-maps", "true")
      script.onerror = () => {
        handleGoogleMapsError(new Error("Failed to load Google Maps script"))
      }

      script.onload = () => {
        // Additional check after script loads
        if (!window.google || !window.google.maps) {
          handleGoogleMapsError(new Error("Google Maps API not available"))
        }
      }

      document.head.appendChild(script)
    }

    // Set up a timeout to handle cases where the script loads but Google Maps fails
    const timeoutId = setTimeout(() => {
      if (!mapInstanceRef.current && isLoading) {
        handleGoogleMapsError(new Error("Google Maps initialization timeout"))
      }
    }, 8000) // Reduced timeout for mobile

    return () => {
      // Cleanup: Only clear the timeout and remove the global callback
      clearTimeout(timeoutId)
      if (window.initMap) {
        delete window.initMap
      }
      // Do NOT remove the script tag to avoid double-loading issues
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (
      typeof window === "undefined" ||
      !mapInstanceRef.current ||
      !window.google
    )
      return

    // Always use the light map style
    mapInstanceRef.current.setOptions({
      styles: [
        {
          featureType: "all",
          elementType: "geometry.fill",
          stylers: [{ color: "#f8fafc" }],
        },
        {
          featureType: "water",
          elementType: "geometry",
          stylers: [{ color: "#dbeafe" }],
        },
        {
          featureType: "road",
          elementType: "geometry",
          stylers: [{ color: "#ffffff" }],
        },
        {
          featureType: "road.highway",
          elementType: "geometry",
          stylers: [{ color: "#e2e8f0" }],
        },
        {
          featureType: "poi.park",
          elementType: "geometry",
          stylers: [{ color: "#ecfdf5" }],
        },
        {
          featureType: "poi",
          elementType: "labels.text",
          stylers: [{ visibility: "off" }],
        },
        {
          featureType: "transit",
          elementType: "labels.text",
          stylers: [{ visibility: "off" }],
        },
        {
          featureType: "administrative",
          elementType: "labels.text.fill",
          stylers: [{ color: "#64748b" }],
        },
        {
          featureType: "road",
          elementType: "labels.text.fill",
          stylers: [{ color: "#475569" }],
        },
      ],
    })
  }, [isDarkMode])

  useEffect(() => {
    if (
      typeof window === "undefined" ||
      !mapInstanceRef.current ||
      !window.google ||
      mapError
    )
      return

    // Clear existing markers
    markersRef.current.forEach((marker) => marker.setMap(null))
    markersRef.current = []

    // Add new markers with mobile optimizations
    const isMobile = window.innerWidth < 768
    
    events.forEach((event) => {
      const position = convertToLatLng(event.coordinates.x, event.coordinates.y)
      const marker = new window.google.maps.Marker({
        position,
        map: mapInstanceRef.current,
        icon: createCustomMarker(event),
        title: event.title,
        // Mobile optimizations
        optimized: true,
        zIndex: event.likes > 10 ? 1000 : 100, // Popular events on top
      })

      marker.addListener("click", () => {
        onEventSelect(event)

        // Show optimized info window for mobile
        const content = `
          <div style="padding: ${isMobile ? '16px' : '24px'}; max-width: ${isMobile ? '280px' : '360px'}; font-family: system-ui, -apple-system, sans-serif; border-radius: ${isMobile ? '16px' : '20px'}; box-shadow: 0 4px 24px #0006; border: 1.5px solid #e5e7eb; background: #fff; color: #111827; ${isDarkMode ? 'filter: brightness(1.15);' : ''}">
            <!-- Header with user info -->
            <div style="display: flex; align-items: center; margin-bottom: ${isMobile ? '12px' : '16px'};">
              <div style="width: ${isMobile ? '32px' : '40px'}; height: ${isMobile ? '32px' : '40px'}; border-radius: 50%; background: linear-gradient(135deg, #3b82f6, #8b5cf6); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: ${isMobile ? '8px' : '12px'};">
                ${event.reporter.name.charAt(0)}
              </div>
              <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <span style="font-weight: 700; font-size: ${isMobile ? '13px' : '14px'}; ${
                    isDarkMode ? "color: #f9fafb;" : "color: #111827;"
                  }">${event.reporter.name}</span>
                  ${
                    event.reporter.verified
                      ? `<div style="width: ${isMobile ? '14px' : '16px'}; height: ${isMobile ? '14px' : '16px'}; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: ${isMobile ? '8px' : '10px'};">✓</div>`
                      : ""
                  }
                </div>
                <div style="font-size: ${isMobile ? '11px' : '12px'}; ${
                  isDarkMode ? "color: #9ca3af;" : "color: #6b7280;"
                }">${event.reporter.followers} followers • ${formatTimeAgo(
          event.timestamp
        )}</div>
              </div>
            </div>
            
            <!-- Event title and severity -->
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: ${isMobile ? '8px' : '12px'};">
              <h3 style="margin: 0; font-size: ${isMobile ? '16px' : '18px'}; font-weight: 800; ${
                isDarkMode ? "color: #f9fafb;" : "color: #111827;"
              }">${event.title}</h3>
              <div style="width: ${isMobile ? '10px' : '12px'}; height: ${isMobile ? '10px' : '12px'}; border-radius: 50%; background-color: ${getSeverityColor(
                event.severity
              )}; box-shadow: 0 0 0 3px ${getSeverityColor(
          event.severity
        )}20;"></div>
            </div>
            
            <!-- Location -->
            <p style="margin: 0 0 ${isMobile ? '8px' : '12px'} 0; font-size: ${isMobile ? '13px' : '14px'}; ${
              isDarkMode ? "color: #9ca3af;" : "color: #6b7280;"
            }; display: flex; align-items: center; font-weight: 500;">
              📍 ${event.location}
            </p>
            
            <!-- Description -->
            <p style="margin: 0 0 ${isMobile ? '12px' : '16px'} 0; font-size: ${isMobile ? '13px' : '14px'}; ${
              isDarkMode ? "color: #d1d5db;" : "color: #374151;"
            } line-height: 1.5; font-weight: 500;">${event.summary}</p>
            
            <!-- Tags -->
            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: ${isMobile ? '12px' : '16px'};">
              ${event.tags
                .slice(0, 3)
                .map(
                  (tag) => `
                <span style="background: ${
                  isDarkMode ? "#374151" : "#f1f5f9"
                }; color: ${
                    isDarkMode ? "#9ca3af" : "#64748b"
                  }; padding: 4px 8px; border-radius: 12px; font-size: ${isMobile ? '10px' : '11px'}; font-weight: 600;">#${tag}</span>
              `
                )
                .join("")}
            </div>
            
            ${
              event.image
                ? `<img src="${event.image}" style="width: 100%; height: ${isMobile ? '120px' : '160px'}; object-fit: cover; border-radius: ${isMobile ? '12px' : '16px'}; margin-bottom: ${isMobile ? '12px' : '16px'}; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />`
                : ""
            }
            
            <!-- Social stats -->
            <div style="display: flex; justify-content: space-between; align-items: center; padding: ${isMobile ? '12px' : '16px'} 0; border-top: 2px solid ${
              isDarkMode ? "#374151" : "#f1f5f9"
            };">
              <div style="display: flex; align-items: center; gap: ${isMobile ? '12px' : '16px'}; font-size: ${isMobile ? '12px' : '13px'}; ${
                isDarkMode ? "color: #9ca3af;" : "color: #6b7280;"
              } font-weight: 600;">
                <span style="display: flex; align-items: center; gap: 4px;">❤️ ${
                  event.likes
                }</span>
                <span style="display: flex; align-items: center; gap: 4px;">💬 ${
                  event.comments
                }</span>
                <span style="display: flex; align-items: center; gap: 4px;">🔄 ${
                  event.shares
                }</span>
                <span style="display: flex; align-items: center; gap: 4px;">🔖 ${
                  event.bookmarks
                }</span>
              </div>
            </div>
          </div>
        `

        if (infoWindowRef.current) {
          infoWindowRef.current.setContent(content)
          infoWindowRef.current.open(mapInstanceRef.current, marker)
        }
      })

      markersRef.current.push(marker)
    })

    // Add zone overlays with mobile optimizations
    zones.forEach((zone) => {
      const polygon = new window.google.maps.Polygon({
        paths: convertZoneToPolygon(zone),
        strokeColor: zone.color,
        strokeOpacity: isMobile ? 0.2 : 0.3, // Reduce opacity on mobile for better performance
        strokeWeight: 1,
        fillColor: zone.color,
        fillOpacity: isMobile ? zone.opacity * 0.8 : zone.opacity, // Slightly reduce fill opacity on mobile
        map: mapInstanceRef.current,
        title: zone.name,
        // Mobile optimizations
        clickable: true,
        zIndex: 50, // Lower than markers
      })

      // Add click listener to show zone info
      polygon.addListener("click", () => {
        const content = `
          <div style="padding: ${isMobile ? '12px' : '16px'}; max-width: ${isMobile ? '260px' : '300px'}; font-family: system-ui, -apple-system, sans-serif; border-radius: ${isMobile ? '12px' : '16px'}; ${
            isDarkMode
              ? "background: #1f2937; color: #f9fafb;"
              : "background: #ffffff; color: #111827;"
          }">
            <div style="display: flex; align-items: center; margin-bottom: ${isMobile ? '8px' : '12px'};">
              <div style="width: ${isMobile ? '28px' : '32px'}; height: ${isMobile ? '28px' : '32px'}; border-radius: 50%; background: ${zone.color}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: ${isMobile ? '8px' : '12px'};">
                ${zone.type === "traffic" ? "🚗" : zone.type === "pollution" ? "🌫️" : zone.type === "happiness" ? "😊" : "🛡️"}
              </div>
              <div>
                <h3 style="margin: 0; font-size: ${isMobile ? '14px' : '16px'}; font-weight: 700; ${
                  isDarkMode ? "color: #f9fafb;" : "color: #111827;"
                }">${zone.name}</h3>
                <p style="margin: 0; font-size: ${isMobile ? '11px' : '12px'}; ${
                  isDarkMode ? "color: #9ca3af;" : "color: #6b7280;"
                }">${zone.type.toUpperCase()}</p>
              </div>
            </div>
            <p style="margin: 0; font-size: ${isMobile ? '12px' : '14px'}; ${
              isDarkMode ? "color: #d1d5db;" : "color: #374151;"
            } line-height: 1.4;">${zone.description}</p>
            <div style="margin-top: ${isMobile ? '8px' : '12px'}; padding: ${isMobile ? '6px 10px' : '8px 12px'}; background: ${
              zone.severity === "high" ? "#fee2e2" : zone.severity === "medium" ? "#fef3c7" : "#d1fae5"
            }; color: ${
              zone.severity === "high" ? "#991b1b" : zone.severity === "medium" ? "#92400e" : "#065f46"
            }; border-radius: 8px; font-size: ${isMobile ? '10px' : '12px'}; font-weight: 600; text-align: center;">
              ${zone.severity.toUpperCase()} SEVERITY
            </div>
          </div>
        `

        if (infoWindowRef.current) {
          infoWindowRef.current.setContent(content)
          infoWindowRef.current.setPosition(polygon.getPath().getArray()[0])
          infoWindowRef.current.open(mapInstanceRef.current)
        }
      })

      markersRef.current.push(polygon)
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [events, onEventSelect, eventTypes, isDarkMode, mapError, zones])

  // If there's an error, show the fallback map
  if (mapError) {
    return <FallbackMap />
  }

  return (
    <div className="w-full h-full relative">
      <div 
        ref={mapRef} 
        className="w-full h-full rounded-2xl md:rounded-3xl touch-pan-y touch-pinch-zoom" 
        style={{
          // Mobile optimizations
          WebkitOverflowScrolling: 'touch',
          overscrollBehavior: 'contain',
          touchAction: 'pan-x pan-y pinch-zoom',
        }}
      />
      {isLoading && (
        <div
          className={`absolute inset-0 flex items-center justify-center rounded-2xl md:rounded-3xl ${
            isDarkMode
              ? "bg-gradient-to-br from-gray-800 via-blue-900 to-indigo-900"
              : "bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"
          }`}
        >
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 md:h-16 md:w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4 md:mb-6 shadow-lg"></div>
            <p
              className={`text-lg md:text-xl font-bold mb-2 ${
                isDarkMode ? "text-gray-200" : "text-gray-800"
              }`}
            >
              Loading Interactive Map
            </p>
            <p
              className={`text-sm font-medium ${
                isDarkMode ? "text-gray-400" : "text-gray-600"
              }`}
            >
              Connecting to city social network...
            </p>
          </div>
        </div>
      )}
    </div>
  )
}