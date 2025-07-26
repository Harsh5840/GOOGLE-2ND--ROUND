import React, { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Camera, Upload, X, MapPin, Navigation } from "lucide-react"

interface ReportModalProps {
  isDarkMode: boolean
  show: boolean
  onClose: () => void
  reportForm: any
  setReportForm: (form: any) => void
  handleCameraCapture: () => void
  fileInputRef: React.RefObject<HTMLInputElement>
  handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void
  capturedImage: string | null
  setCapturedImage: (img: string | null) => void
  handleSubmitReport: () => void
  eventTypes: { id: string; label: string; emoji: string }[]
}

const ReportModal: React.FC<ReportModalProps> = ({
  isDarkMode,
  show,
  onClose,
  reportForm,
  setReportForm,
  handleCameraCapture,
  fileInputRef,
  handleFileUpload,
  capturedImage,
  setCapturedImage,
  handleSubmitReport,
  eventTypes,
}) => {
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number; address: string } | null>(null)
  const [isGettingLocation, setIsGettingLocation] = useState(false)
  const [locationError, setLocationError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  // Get user's current location
  useEffect(() => {
    if (show) {
      // Start location detection immediately when modal opens
      console.log('ReportModal: Modal opened, starting automatic location detection...')
      setRetryCount(0)
      getUserLocation()
    }
  }, [show])

  const getUserLocation = () => {
    setIsGettingLocation(true)
    setLocationError(null)
    console.log('ReportModal: Starting location detection... (attempt:', retryCount + 1, ')')

    if (!navigator.geolocation) {
      const errorMsg = "Geolocation is not supported by this browser"
      console.error('ReportModal:', errorMsg)
      setLocationError(errorMsg)
      setIsGettingLocation(false)
      return
    }

    // Request location with high accuracy and reasonable timeout
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords
        console.log('ReportModal: Location obtained successfully:', { latitude, longitude })

        try {
          // Reverse geocode to get address
          const address = await reverseGeocode(latitude, longitude)
          
          const location = {
            lat: latitude,
            lng: longitude,
            address: address
          }

          setUserLocation(location)
          setReportForm((prev: any) => ({ 
            ...prev, 
            location: address,
            coordinates: { lat: latitude, lng: longitude }
          }))
          
          console.log('ReportModal: Location set in form successfully:', location)
        } catch (error) {
          console.error('ReportModal: Error getting address:', error)
          const fallbackAddress = `Location (${latitude.toFixed(4)}, ${longitude.toFixed(4)})`
          setUserLocation({ lat: latitude, lng: longitude, address: fallbackAddress })
          setReportForm((prev: any) => ({ 
            ...prev, 
            location: fallbackAddress,
            coordinates: { lat: latitude, lng: longitude }
          }))
          console.log('ReportModal: Using fallback address:', fallbackAddress)
        }
        
        setIsGettingLocation(false)
      },
      (error) => {
        console.error('ReportModal: Location error:', error)
        let errorMessage = "Unable to get your location"
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = "Location access denied. Please enable location services in your browser settings."
            break
          case error.POSITION_UNAVAILABLE:
            errorMessage = "Location information unavailable. Please check your device location settings."
            break
          case error.TIMEOUT:
            errorMessage = "Location request timed out. Please try again."
            break
          default:
            errorMessage = "Unable to get your location. Please check your browser settings."
        }
        
        setLocationError(errorMessage)
        setIsGettingLocation(false)
        
        // Auto-retry once if it's a timeout or position unavailable error
        if ((error.code === error.TIMEOUT || error.code === error.POSITION_UNAVAILABLE) && retryCount < 1) {
          console.log('ReportModal: Auto-retrying location detection...')
          setRetryCount(prev => prev + 1)
          setTimeout(() => {
            getUserLocation()
          }, 2000) // Wait 2 seconds before retry
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 15000, // Increased timeout to 15 seconds
        maximumAge: 300000 // 5 minutes cache
      }
    )
  }

  const reverseGeocode = async (lat: number, lng: number): Promise<string> => {
    try {
      if (window.google && window.google.maps) {
        const geocoder = new window.google.maps.Geocoder()
        const response = await geocoder.geocode({ location: { lat, lng } })
        
        if (response.results[0]) {
          return response.results[0].formatted_address
        }
      }
      
      // Fallback if Google Maps is not available
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`
      )
      const data = await response.json()
      return data.display_name || `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`
    } catch (error) {
      console.error('Reverse geocoding error:', error)
      return `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`
    }
  }

  if (!show) return null
  return (
    <div className="fixed inset-0 z-[10000] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div
        className={`w-full max-w-2xl backdrop-blur-xl rounded-2xl md:rounded-3xl shadow-2xl border transition-all duration-500 animate-slideUp max-h-[90vh] overflow-y-auto ${
          isDarkMode ? "bg-gray-800/90 border-gray-600/30" : "bg-white/90 border-white/30"
        }`}
      >
        <div className={`p-6 md:p-8 border-b ${isDarkMode ? "border-gray-600/30" : "border-white/30"}`}>
          <div className="flex items-center justify-between">
            <h2 className={`text-xl md:text-2xl font-bold ${isDarkMode ? "text-gray-100" : "text-gray-900"}`}>
              Report New Event
            </h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="rounded-2xl transition-all duration-300 hover:scale-110"
            >
              <X className="w-5 h-5 md:w-6 md:h-6" />
            </Button>
          </div>
          <p className={`text-sm mt-2 ${isDarkMode ? "text-gray-400" : "text-gray-600"}`}>
            📍 Your location will be automatically detected when you open this form
          </p>
        </div>

        <div className="p-6 md:p-8 space-y-6 md:space-y-8">
          {/* Location Status */}
          <div className="group">
            <label className={`block text-sm font-semibold mb-3 ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              Your Location (Auto-detected)
            </label>
            <div className="relative">
              <Navigation className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-blue-500" />
              <div className={`pl-12 pr-4 py-3 backdrop-blur-sm border rounded-xl md:rounded-2xl font-medium shadow-lg transition-all duration-300 ${
                isDarkMode
                  ? "bg-gray-700/60 border-gray-600/40 text-gray-200"
                  : "bg-white/60 border-white/40 shadow-blue-500/5"
              }`}>
                {isGettingLocation ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                    <span>Automatically detecting your location...</span>
                  </div>
                ) : userLocation ? (
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <span className="truncate block">{userLocation.address}</span>
                      <span className="text-xs text-blue-500 block mt-1">📍 Auto-detected via GPS</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={getUserLocation}
                      className="text-blue-500 hover:text-blue-600 ml-2"
                      title="Refresh location"
                    >
                      <Navigation className="w-4 h-4" />
                    </Button>
                  </div>
                ) : locationError ? (
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <span className="text-red-500 block">{locationError}</span>
                      <span className="text-xs text-gray-500 block mt-1">Please enable location access</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={getUserLocation}
                      className="text-blue-500 hover:text-blue-600 ml-2"
                      title="Try again"
                    >
                      <Navigation className="w-4 h-4" />
                    </Button>
                  </div>
                ) : (
                  <span className="text-gray-500">Waiting for location detection...</span>
                )}
              </div>
            </div>
          </div>

          <div className="group">
            <label className={`block text-sm font-semibold mb-3 ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              Event Title
            </label>
            <Input
              value={reportForm.title}
              onChange={(e) => setReportForm((prev: any) => ({ ...prev, title: e.target.value }))}
              placeholder="What's happening?"
              className={`backdrop-blur-sm border rounded-xl md:rounded-2xl h-12 font-medium shadow-lg transition-all duration-300 hover:shadow-xl focus:shadow-xl focus:scale-[1.02] group-focus-within:border-blue-400 ${
                isDarkMode
                  ? "bg-gray-700/60 border-gray-600/40 text-gray-200 placeholder-gray-400"
                  : "bg-white/60 border-white/40 shadow-blue-500/5"
              }`}
            />
          </div>

          <div className="group">
            <label className={`block text-sm font-semibold mb-3 ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              Description
            </label>
            <Textarea
              value={reportForm.description}
              onChange={(e) => setReportForm((prev: any) => ({ ...prev, description: e.target.value }))}
              placeholder="Describe the event in detail..."
              className={`backdrop-blur-sm border rounded-xl md:rounded-2xl min-h-[120px] font-medium shadow-lg transition-all duration-300 hover:shadow-xl focus:shadow-xl focus:scale-[1.02] group-focus-within:border-blue-400 ${
                isDarkMode
                  ? "bg-gray-700/60 border-gray-600/40 text-gray-200 placeholder-gray-400"
                  : "bg-white/60 border-white/40 shadow-blue-500/5"
              }`}
            />
          </div>

          <div className="group">
            <label className={`block text-sm font-semibold mb-3 ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              Event Type
            </label>
            <select
              value={reportForm.type}
              onChange={(e) => setReportForm((prev: any) => ({ ...prev, type: e.target.value }))}
              className={`w-full p-4 backdrop-blur-sm border rounded-xl md:rounded-2xl focus:border-blue-400 focus:ring-blue-400/20 font-medium shadow-lg transition-all duration-300 hover:shadow-xl focus:shadow-xl focus:scale-[1.02] ${
                isDarkMode
                  ? "bg-gray-700/60 border-gray-600/40 text-gray-200"
                  : "bg-white/60 border-white/40 shadow-blue-500/5"
              }`}
            >
              {eventTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.emoji} {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className={`block text-sm font-semibold mb-3 ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              Add Photo
            </label>
            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
              <Button
                type="button"
                onClick={handleCameraCapture}
                className="flex-1 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white rounded-xl md:rounded-2xl h-12 md:h-14 font-semibold shadow-xl shadow-green-500/25 transition-all duration-300 hover:scale-[1.02] group"
              >
                <Camera className="w-5 h-5 md:w-6 md:h-6 mr-2 md:mr-3 group-hover:animate-bounce" />
                Take Photo
              </Button>
              <Button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
                className={`flex-1 rounded-xl md:rounded-2xl h-12 md:h-14 font-semibold shadow-lg transition-all duration-300 hover:scale-[1.02] group ${
                  isDarkMode
                    ? "border-gray-600/40 hover:bg-gray-700/60"
                    : "border-white/40 hover:bg-white/60 shadow-blue-500/5"
                }`}
              >
                <Upload className="w-5 h-5 md:w-6 md:h-6 mr-2 md:mr-3 group-hover:animate-bounce" />
                Upload File
              </Button>
            </div>
            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
          </div>

          {capturedImage && (
            <div className="relative animate-fadeIn">
              <img
                src={capturedImage || "/placeholder.svg"}
                alt="Captured"
                className="w-full h-48 md:h-64 object-cover rounded-xl md:rounded-2xl shadow-lg transition-all duration-300 hover:scale-[1.02]"
              />
              <Button
                onClick={() => {
                  setCapturedImage(null)
                  setReportForm((prev: any) => ({ ...prev, image: null }))
                }}
                variant="ghost"
                size="icon"
                className="absolute top-4 right-4 bg-black/60 hover:bg-black/80 text-white rounded-2xl backdrop-blur-sm transition-all duration-300 hover:scale-110"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
          )}
        </div>

        <div
          className={`p-6 md:p-8 border-t flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 ${isDarkMode ? "border-gray-600/30" : "border-white/30"}`}
        >
          <Button
            variant="outline"
            onClick={onClose}
            className={`flex-1 rounded-xl md:rounded-2xl h-12 md:h-14 font-semibold shadow-lg transition-all duration-300 hover:scale-[1.02] ${
              isDarkMode
                ? "border-gray-600/40 hover:bg-gray-700/60"
                : "border-white/40 hover:bg-white/60 shadow-blue-500/5"
            }`}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmitReport}
            disabled={!userLocation}
            className="flex-1 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 text-white rounded-xl md:rounded-2xl h-12 md:h-14 font-semibold shadow-xl shadow-blue-500/25 transition-all duration-300 hover:scale-[1.02] group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Submit Report
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ReportModal