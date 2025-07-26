"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Camera, 
  Upload, 
  MapPin, 
  Calendar, 
  User, 
  Search, 
  Filter,
  Grid3X3,
  Map,
  Plus,
  X,
  Eye,
  Download
} from 'lucide-react'
import GoogleMap from './google-map'
import { uploadEventPhoto, getEventPhotos } from '@/lib/api'
import { toast } from 'sonner'

interface EventPhoto {
  id: string
  filename: string
  file_url: string
  latitude: number
  longitude: number
  user_id: string
  description?: string
  gemini_summary: string
  upload_timestamp: string
  status: string
}

interface UploadForm {
  image: File | null
  latitude: number
  longitude: number
  description: string
}

export default function EventPhotosDashboard() {
  const [photos, setPhotos] = useState<EventPhoto[]>([])
  const [filteredPhotos, setFilteredPhotos] = useState<EventPhoto[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedPhoto, setSelectedPhoto] = useState<EventPhoto | null>(null)
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [uploadForm, setUploadForm] = useState<UploadForm>({
    image: null,
    latitude: 0,
    longitude: 0,
    description: ''
  })
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [currentLocation, setCurrentLocation] = useState<{lat: number, lng: number} | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'map'>('grid')

  // Load photos on component mount
  useEffect(() => {
    loadPhotos()
    getCurrentLocation()
  }, [])

  // Filter photos based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredPhotos(photos)
    } else {
      const filtered = photos.filter(photo => 
        photo.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        photo.gemini_summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
        photo.user_id.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredPhotos(filtered)
    }
  }, [searchQuery, photos])

  const loadPhotos = async () => {
    try {
      setIsLoading(true)
      const response = await getEventPhotos()
      setPhotos(response)
      setFilteredPhotos(response)
    } catch (error) {
      console.error('Error loading photos:', error)
      toast.error('Failed to load photos')
    } finally {
      setIsLoading(false)
    }
  }

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          })
          setUploadForm(prev => ({
            ...prev,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }))
        },
        (error) => {
          console.error('Error getting location:', error)
          toast.error('Unable to get current location')
        }
      )
    }
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadForm(prev => ({ ...prev, image: file }))
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreviewImage(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmitUpload = async () => {
    if (!uploadForm.image) {
      toast.error('Please select an image')
      return
    }

    if (!uploadForm.latitude || !uploadForm.longitude) {
      toast.error('Please enable location access')
      return
    }

    try {
      setIsLoading(true)
      
      const formData = new FormData()
      formData.append('file', uploadForm.image)
      formData.append('latitude', uploadForm.latitude.toString())
      formData.append('longitude', uploadForm.longitude.toString())
      formData.append('user_id', 'user123') // TODO: Get from auth
      if (uploadForm.description) {
        formData.append('description', uploadForm.description)
      }

      await uploadEventPhoto(formData)
      
      toast.success('Photo uploaded successfully!')
      setIsUploadDialogOpen(false)
      setUploadForm({
        image: null,
        latitude: 0,
        longitude: 0,
        description: ''
      })
      setPreviewImage(null)
      
      // Reload photos
      await loadPhotos()
      
    } catch (error) {
      console.error('Error uploading photo:', error)
      toast.error('Failed to upload photo')
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handlePhotoClick = (photo: EventPhoto) => {
    setSelectedPhoto(photo)
  }

  // Convert photos to map events format
  const mapEvents = filteredPhotos.map(photo => ({
    id: parseInt(photo.id.replace(/-/g, '').slice(0, 8), 16),
    type: 'photo',
    title: photo.description || 'Geotagged Photo',
    location: `${photo.latitude.toFixed(4)}, ${photo.longitude.toFixed(4)}`,
    coordinates: { x: photo.longitude, y: photo.latitude },
    severity: 'info',
    summary: photo.gemini_summary,
    reporter: {
      name: photo.user_id,
      avatar: '/placeholder-user.jpg',
      verified: false,
      followers: 0
    },
    timestamp: new Date(photo.upload_timestamp),
    likes: 0,
    comments: 0,
    shares: 0,
    bookmarks: 0,
    image: photo.file_url,
    tags: ['photo', 'geotagged'],
    customEmoji: '📸'
  }))

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
              Geotagged Photos Dashboard
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              View and manage geotagged photos from around the city
            </p>
          </div>
          
          <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white">
                <Plus className="w-4 h-4 mr-2" />
                Upload Photo
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Upload Geotagged Photo</DialogTitle>
              </DialogHeader>
              
              <div className="space-y-6">
                {/* Image Upload */}
                <div>
                  <label className="block text-sm font-medium mb-2">Photo</label>
                  <div className="flex gap-4">
                    <Button
                      variant="outline"
                      onClick={() => document.getElementById('photo-upload')?.click()}
                      className="flex-1"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Choose File
                    </Button>
                    <Button
                      variant="outline"
                      onClick={getCurrentLocation}
                      className="flex-1"
                    >
                      <MapPin className="w-4 h-4 mr-2" />
                      Get Location
                    </Button>
                  </div>
                  <input
                    id="photo-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                </div>

                {/* Preview */}
                {previewImage && (
                  <div className="relative">
                    <img
                      src={previewImage}
                      alt="Preview"
                      className="w-full h-48 object-cover rounded-lg"
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2 bg-black/50 text-white"
                      onClick={() => {
                        setPreviewImage(null)
                        setUploadForm(prev => ({ ...prev, image: null }))
                      }}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                )}

                {/* Location */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Latitude</label>
                    <Input
                      type="number"
                      step="any"
                      value={uploadForm.latitude}
                      onChange={(e) => setUploadForm(prev => ({ ...prev, latitude: parseFloat(e.target.value) || 0 }))}
                      placeholder="Latitude"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Longitude</label>
                    <Input
                      type="number"
                      step="any"
                      value={uploadForm.longitude}
                      onChange={(e) => setUploadForm(prev => ({ ...prev, longitude: parseFloat(e.target.value) || 0 }))}
                      placeholder="Longitude"
                    />
                  </div>
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium mb-2">Description (Optional)</label>
                  <Textarea
                    value={uploadForm.description}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe what's happening in this photo..."
                    rows={3}
                  />
                </div>

                {/* Submit */}
                <div className="flex gap-4">
                  <Button
                    variant="outline"
                    onClick={() => setIsUploadDialogOpen(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSubmitUpload}
                    disabled={isLoading || !uploadForm.image}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600"
                  >
                    {isLoading ? 'Uploading...' : 'Upload Photo'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <Input
              placeholder="Search photos by description, content, or user..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              onClick={() => setViewMode('grid')}
              size="sm"
            >
              <Grid3X3 className="w-4 h-4 mr-2" />
              Grid
            </Button>
            <Button
              variant={viewMode === 'map' ? 'default' : 'outline'}
              onClick={() => setViewMode('map')}
              size="sm"
            >
              <Map className="w-4 h-4 mr-2" />
              Map
            </Button>
          </div>
        </div>

        {/* Content */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredPhotos.map((photo) => (
              <Card
                key={photo.id}
                className="cursor-pointer hover:shadow-lg transition-all duration-300 hover:scale-105"
                onClick={() => handlePhotoClick(photo)}
              >
                <div className="relative">
                  <img
                    src={photo.file_url}
                    alt={photo.description || 'Geotagged photo'}
                    className="w-full h-48 object-cover rounded-t-lg"
                  />
                  <Badge className="absolute top-2 right-2 bg-black/50 text-white">
                    📸
                  </Badge>
                </div>
                <CardContent className="p-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                      <MapPin className="w-4 h-4" />
                      <span>{photo.latitude.toFixed(4)}, {photo.longitude.toFixed(4)}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDate(photo.upload_timestamp)}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                      <User className="w-4 h-4" />
                      <span>{photo.user_id}</span>
                    </div>
                    {photo.description && (
                      <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-2">
                        {photo.description}
                      </p>
                    )}
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-3">
                      {photo.gemini_summary}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="h-[600px] rounded-lg overflow-hidden">
            <GoogleMap
              events={mapEvents}
              selectedEvent={selectedPhoto ? mapEvents.find(e => e.id === parseInt(selectedPhoto.id.replace(/-/g, '').slice(0, 8), 16)) || null : null}
              onEventSelect={(event) => {
                const photo = photos.find(p => parseInt(p.id.replace(/-/g, '').slice(0, 8), 16) === event.id)
                setSelectedPhoto(photo || null)
              }}
              eventTypes={[{ id: 'photo', label: 'Photos' }]}
              isDarkMode={false}
              zones={[]}
            />
          </div>
        )}

        {/* Photo Detail Dialog */}
        <Dialog open={!!selectedPhoto} onOpenChange={() => setSelectedPhoto(null)}>
          <DialogContent className="max-w-4xl">
            {selectedPhoto && (
              <>
                <DialogHeader>
                  <DialogTitle>Photo Details</DialogTitle>
                </DialogHeader>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <img
                      src={selectedPhoto.file_url}
                      alt={selectedPhoto.description || 'Geotagged photo'}
                      className="w-full h-96 object-cover rounded-lg"
                    />
                  </div>
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold mb-2">Location</h3>
                      <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                        <MapPin className="w-4 h-4" />
                        <span>{selectedPhoto.latitude.toFixed(6)}, {selectedPhoto.longitude.toFixed(6)}</span>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold mb-2">Uploaded</h3>
                      <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(selectedPhoto.upload_timestamp)}</span>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold mb-2">User</h3>
                      <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                        <User className="w-4 h-4" />
                        <span>{selectedPhoto.user_id}</span>
                      </div>
                    </div>
                    
                    {selectedPhoto.description && (
                      <div>
                        <h3 className="font-semibold mb-2">Description</h3>
                        <p className="text-sm text-slate-700 dark:text-slate-300">
                          {selectedPhoto.description}
                        </p>
                      </div>
                    )}
                    
                    <div>
                      <h3 className="font-semibold mb-2">AI Analysis</h3>
                      <p className="text-sm text-slate-700 dark:text-slate-300">
                        {selectedPhoto.gemini_summary}
                      </p>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4 mr-2" />
                        View on Map
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  </div>
                </div>
              </>
            )}
          </DialogContent>
        </Dialog>

        {/* Empty State */}
        {filteredPhotos.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <Camera className="w-16 h-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              No photos found
            </h3>
            <p className="text-slate-600 dark:text-slate-400 mb-4">
              {searchQuery ? 'Try adjusting your search terms' : 'Upload the first geotagged photo!'}
            </p>
            {!searchQuery && (
              <Button onClick={() => setIsUploadDialogOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Upload Photo
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
} 