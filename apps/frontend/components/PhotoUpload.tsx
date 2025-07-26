"use client"

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Camera, Upload, MapPin, X, Plus } from 'lucide-react'
import { uploadEventPhoto } from '@/lib/api'
import { toast } from 'sonner'

interface PhotoUploadProps {
  trigger?: React.ReactNode
  onUploadSuccess?: () => void
}

export default function PhotoUpload({ trigger, onUploadSuccess }: PhotoUploadProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [form, setForm] = useState({
    image: null as File | null,
    latitude: 0,
    longitude: 0,
    description: ''
  })
  const [previewImage, setPreviewImage] = useState<string | null>(null)

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setForm(prev => ({
            ...prev,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }))
          toast.success('Location captured!')
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
      setForm(prev => ({ ...prev, image: file }))
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreviewImage(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async () => {
    if (!form.image) {
      toast.error('Please select an image')
      return
    }

    if (!form.latitude || !form.longitude) {
      toast.error('Please enable location access')
      return
    }

    try {
      setIsLoading(true)
      
      const formData = new FormData()
      formData.append('file', form.image)
      formData.append('latitude', form.latitude.toString())
      formData.append('longitude', form.longitude.toString())
      formData.append('user_id', 'user123') // TODO: Get from auth
      if (form.description) {
        formData.append('description', form.description)
      }

      await uploadEventPhoto(formData)
      
      toast.success('Photo uploaded successfully!')
      setIsOpen(false)
      setForm({
        image: null,
        latitude: 0,
        longitude: 0,
        description: ''
      })
      setPreviewImage(null)
      
      onUploadSuccess?.()
      
    } catch (error) {
      console.error('Error uploading photo:', error)
      toast.error('Failed to upload photo')
    } finally {
      setIsLoading(false)
    }
  }

  const resetForm = () => {
    setForm({
      image: null,
      latitude: 0,
      longitude: 0,
      description: ''
    })
    setPreviewImage(null)
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => {
      setIsOpen(open)
      if (!open) resetForm()
    }}>
      <DialogTrigger asChild>
        {trigger || (
          <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white">
            <Plus className="w-4 h-4 mr-2" />
            Upload Photo
          </Button>
        )}
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
                  setForm(prev => ({ ...prev, image: null }))
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
                value={form.latitude}
                onChange={(e) => setForm(prev => ({ ...prev, latitude: parseFloat(e.target.value) || 0 }))}
                placeholder="Latitude"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Longitude</label>
              <Input
                type="number"
                step="any"
                value={form.longitude}
                onChange={(e) => setForm(prev => ({ ...prev, longitude: parseFloat(e.target.value) || 0 }))}
                placeholder="Longitude"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium mb-2">Description (Optional)</label>
            <Textarea
              value={form.description}
              onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe what's happening in this photo..."
              rows={3}
            />
          </div>

          {/* Submit */}
          <div className="flex gap-4">
            <Button
              variant="outline"
              onClick={() => setIsOpen(false)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={isLoading || !form.image}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600"
            >
              {isLoading ? 'Uploading...' : 'Upload Photo'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 