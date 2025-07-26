"use client"

import { useEffect, useRef, useState } from 'react'
import { Search, MapPin, X } from 'lucide-react'

interface MapSearchBoxProps {
  onLocationSelect: (location: { lat: number; lng: number; address: string }) => void
  onSearchChange?: (query: string) => void
  placeholder?: string
  className?: string
}

declare global {
  interface Window {
    google: any
  }
}

export default function MapSearchBox({
  onLocationSelect,
  onSearchChange,
  placeholder = "Search for a location...",
  className = ""
}: MapSearchBoxProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const autocompleteRef = useRef<any>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isGoogleMapsLoaded, setIsGoogleMapsLoaded] = useState(false)

  // Wait for Google Maps to be fully loaded
  useEffect(() => {
    const checkGoogleMapsLoaded = () => {
      if (window.google && window.google.maps && window.google.maps.places) {
        setIsGoogleMapsLoaded(true)
        return true
      }
      return false
    }

    // Check immediately
    if (checkGoogleMapsLoaded()) {
      return
    }

    // If not loaded, wait for it
    const interval = setInterval(() => {
      if (checkGoogleMapsLoaded()) {
        clearInterval(interval)
      }
    }, 100)

    // Cleanup
    return () => clearInterval(interval)
  }, [])

  // Initialize Autocomplete when Google Maps is loaded
  useEffect(() => {
    if (!isGoogleMapsLoaded || !inputRef.current) return

    try {
      console.log('MapSearchBox: Initializing autocomplete...')
      
      // Try to use the new PlaceAutocompleteElement first
      if (window.google.maps.places.PlaceAutocompleteElement) {
        console.log('MapSearchBox: Using new PlaceAutocompleteElement...')
        
        // Create the new element
        const placeAutocomplete = new window.google.maps.places.PlaceAutocompleteElement({
          types: ['geocode', 'establishment']
        })

        // Set the input element
        placeAutocomplete.inputElement = inputRef.current

        console.log('MapSearchBox: PlaceAutocompleteElement initialized successfully')

        // Add event listeners for the new element
        placeAutocomplete.addEventListener('gmp-placeselect', (event: any) => {
          console.log('MapSearchBox: Place selected event fired')
          const place = event.detail.place
          console.log('MapSearchBox: Selected place:', place)
          
          if (place && place.location) {
            const location = {
              lat: place.location.lat,
              lng: place.location.lng,
              address: place.formattedAddress || place.displayName || searchQuery
            }
            
            setSearchQuery(location.address)
            onLocationSelect(location)
          }
        })

        autocompleteRef.current = placeAutocomplete

      } else {
        // Fallback to old Autocomplete if new one is not available
        console.log('MapSearchBox: PlaceAutocompleteElement not available, using fallback...')
        
        const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
          types: ['geocode', 'establishment']
        })

        // Add listener for place selection
        autocomplete.addListener('place_changed', () => {
          console.log('MapSearchBox: Place changed event fired (fallback)')
          const place = autocomplete.getPlace()
          console.log('MapSearchBox: Selected place (fallback):', place)
          
          if (place.geometry && place.geometry.location) {
            const location = {
              lat: place.geometry.location.lat(),
              lng: place.geometry.location.lng(),
              address: place.formatted_address || place.name || searchQuery
            }
            
            setSearchQuery(location.address)
            onLocationSelect(location)
          }
        })

        autocompleteRef.current = autocomplete
        console.log('MapSearchBox: Google Places Autocomplete initialized successfully (fallback)')
      }

    } catch (error) {
      console.error('MapSearchBox: Error initializing autocomplete:', error)
      
      // Final fallback to old Autocomplete
      try {
        console.log('MapSearchBox: Trying final fallback to old Autocomplete...')
        const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
          types: ['geocode', 'establishment']
        })

        autocomplete.addListener('place_changed', () => {
          console.log('MapSearchBox: Place changed event fired (final fallback)')
          const place = autocomplete.getPlace()
          console.log('MapSearchBox: Selected place (final fallback):', place)
          
          if (place.geometry && place.geometry.location) {
            const location = {
              lat: place.geometry.location.lat(),
              lng: place.geometry.location.lng(),
              address: place.formatted_address || place.name || searchQuery
            }
            
            setSearchQuery(location.address)
            onLocationSelect(location)
          }
        })

        autocompleteRef.current = autocomplete
        console.log('MapSearchBox: Google Places Autocomplete initialized successfully (final fallback)')
      } catch (fallbackError) {
        console.error('MapSearchBox: All autocomplete methods failed:', fallbackError)
      }
    }

    return () => {
      console.log('MapSearchBox: Cleaning up autocomplete...')
      if (autocompleteRef.current) {
        try {
          if (autocompleteRef.current.removeEventListener) {
            // New PlaceAutocompleteElement
            autocompleteRef.current.removeEventListener('gmp-placeselect', () => {})
          } else {
            // Old Autocomplete
            window.google.maps.event.clearInstanceListeners(autocompleteRef.current)
          }
        } catch (error) {
          console.error('MapSearchBox: Error cleaning up Autocomplete:', error)
        }
      }
    }
  }, [isGoogleMapsLoaded, onLocationSelect, searchQuery])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearchQuery(value)
    onSearchChange?.(value)
  }

  const handleClearSearch = () => {
    setSearchQuery("")
    onSearchChange?.("")
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-10">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        
        <input
          ref={inputRef}
          type="text"
          value={searchQuery}
          onChange={handleInputChange}
          placeholder={placeholder}
          className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all duration-200 bg-white text-gray-900 placeholder-gray-500"
        />

        {searchQuery && (
          <button
            onClick={handleClearSearch}
            className="absolute inset-y-0 right-0 pr-3 flex items-center z-10"
          >
            <X className="h-5 w-5 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>

      {/* Loading indicator */}
      {isLoading && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="ml-2 text-sm text-gray-600">Searching...</span>
          </div>
        </div>
      )}

      {/* Debug info - remove in production */}
      {!isGoogleMapsLoaded && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-yellow-50 border border-yellow-200 rounded-lg p-2">
          <span className="text-xs text-yellow-700">Loading Google Maps...</span>
        </div>
      )}
    </div>
  )
} 