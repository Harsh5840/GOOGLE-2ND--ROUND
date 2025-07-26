"use client"

import React, { useState, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { 
  Camera, 
  Upload, 
  X, 
  MapPin, 
  AlertTriangle, 
  Calendar, 
  Users,
  Car,
  Building,
  Send,
  Loader2
} from 'lucide-react';

interface ImageUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (eventData: EventData) => void;
  userLocation?: { lat: number; lng: number };
}

interface EventData {
  type: 'accident' | 'event' | 'traffic' | 'construction' | 'other';
  title: string;
  description: string;
  location: string;
  coordinates: { lat: number; lng: number };
  severity: 'low' | 'medium' | 'high';
  imageUrl: string;
  timestamp: Date;
}

const eventTypes = [
  { id: 'accident', label: 'Accident', icon: AlertTriangle, color: 'bg-red-500' },
  { id: 'event', label: 'Event', icon: Calendar, color: 'bg-blue-500' },
  { id: 'traffic', label: 'Traffic', icon: Car, color: 'bg-yellow-500' },
  { id: 'construction', label: 'Construction', icon: Building, color: 'bg-orange-500' },
  { id: 'other', label: 'Other', icon: Users, color: 'bg-gray-500' }
];

export default function ImageUploadModal({ isOpen, onClose, onSubmit, userLocation }: ImageUploadModalProps) {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [eventData, setEventData] = useState<Partial<EventData>>({
    type: 'other',
    title: '',
    description: '',
    location: '',
    severity: 'medium',
    coordinates: userLocation || { lat: 0, lng: 0 }
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageSelect = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleImageSelect(file);
    }
  };

  const handleCameraCapture = () => {
    fileInputRef.current?.click();
  };

  const analyzeImageWithGemini = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);
    try {
      // Convert image to base64
      const base64Image = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onload = () => {
          const result = reader.result as string;
          resolve(result.split(',')[1]); // Remove data:image/...;base64, prefix
        };
        reader.readAsDataURL(selectedImage);
      });

      // Send to backend for Gemini Vision analysis
      const response = await fetch('/api/analyze-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: base64Image,
          mimeType: selectedImage.type
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result.analysis);
        
        // Auto-populate fields based on analysis
        if (result.suggestedType) {
          setEventData(prev => ({ ...prev, type: result.suggestedType }));
        }
        if (result.suggestedTitle) {
          setEventData(prev => ({ ...prev, title: result.suggestedTitle }));
        }
        if (result.suggestedDescription) {
          setEventData(prev => ({ ...prev, description: result.suggestedDescription }));
        }
      }
    } catch (error) {
      console.error('Error analyzing image:', error);
      setAnalysisResult('Failed to analyze image. Please fill in the details manually.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = () => {
    if (!selectedImage || !eventData.title || !eventData.description || !eventData.location) {
      return;
    }

    const completeEventData: EventData = {
      ...eventData as EventData,
      imageUrl: imagePreview,
      timestamp: new Date()
    };

    onSubmit(completeEventData);
    onClose();
    resetForm();
  };

  const resetForm = () => {
    setSelectedImage(null);
    setImagePreview('');
    setEventData({
      type: 'other',
      title: '',
      description: '',
      location: '',
      severity: 'medium',
      coordinates: userLocation || { lat: 0, lng: 0 }
    });
    setAnalysisResult('');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Camera className="w-5 h-5" />
              <span>Report Event</span>
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <CardDescription>
            Upload an image and describe what you're seeing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Image Upload Section */}
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Button onClick={handleCameraCapture} variant="outline">
                <Camera className="w-4 h-4 mr-2" />
                Take Photo
              </Button>
              <Button onClick={() => fileInputRef.current?.click()} variant="outline">
                <Upload className="w-4 h-4 mr-2" />
                Upload Image
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>

            {imagePreview && (
              <div className="relative">
                <img 
                  src={imagePreview} 
                  alt="Preview" 
                  className="w-full h-48 object-cover rounded-lg"
                />
                <Button
                  variant="destructive"
                  size="sm"
                  className="absolute top-2 right-2"
                  onClick={() => {
                    setSelectedImage(null);
                    setImagePreview('');
                  }}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            )}

            {selectedImage && (
              <Button 
                onClick={analyzeImageWithGemini} 
                disabled={isAnalyzing}
                className="w-full"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing Image...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Analyze with AI
                  </>
                )}
              </Button>
            )}
          </div>

          {/* Analysis Result */}
          {analysisResult && (
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-4">
                <h4 className="font-medium text-blue-900 mb-2">AI Analysis:</h4>
                <p className="text-blue-800 text-sm">{analysisResult}</p>
              </CardContent>
            </Card>
          )}

          {/* Event Details Form */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Event Type</label>
              <div className="flex flex-wrap gap-2">
                {eventTypes.map((type) => (
                  <Badge
                    key={type.id}
                    variant={eventData.type === type.id ? "default" : "outline"}
                    className={`cursor-pointer ${eventData.type === type.id ? type.color : ''}`}
                    onClick={() => setEventData(prev => ({ ...prev, type: type.id as EventData['type'] }))}
                  >
                    <type.icon className="w-3 h-3 mr-1" />
                    {type.label}
                  </Badge>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Title</label>
              <Input
                value={eventData.title}
                onChange={(e) => setEventData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Brief description of what happened"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <Textarea
                value={eventData.description}
                onChange={(e) => setEventData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Provide more details about the event..."
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Location</label>
              <Input
                value={eventData.location}
                onChange={(e) => setEventData(prev => ({ ...prev, location: e.target.value }))}
                placeholder="Street address or landmark"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Severity</label>
              <div className="flex space-x-2">
                {['low', 'medium', 'high'].map((severity) => (
                  <Badge
                    key={severity}
                    variant={eventData.severity === severity ? "default" : "outline"}
                    className={`cursor-pointer ${
                      severity === 'high' ? 'bg-red-500' : 
                      severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    onClick={() => setEventData(prev => ({ ...prev, severity: severity as EventData['severity'] }))}
                  >
                    {severity.charAt(0).toUpperCase() + severity.slice(1)}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              onClick={handleSubmit}
              disabled={!selectedImage || !eventData.title || !eventData.description || !eventData.location}
            >
              Submit Report
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 