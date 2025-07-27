"use client"

import React, { useState, useEffect } from 'react';
import { auth, db } from '../lib/firebase';
import { GoogleAuthProvider, signInWithPopup, onAuthStateChanged, User } from 'firebase/auth';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { Textarea } from './ui/textarea';
import { 
  MapPin, 
  Car, 
  Building, 
  Calendar, 
  Users, 
  Camera, 
  AlertTriangle, 
  Heart,
  Coffee,
  Music,
  ShoppingBag,
  Gamepad2,
  BookOpen,
  Utensils,
  Plane,
  Train,
  Bus,
  Bike,
  // Walking, // Not available in lucide-react
  Home,
  Briefcase,
  GraduationCap,
  Palette,
  Dumbbell,
  TreePine,
  Globe,
  Zap,
  Star,
  Plus,
  ArrowRight,
  Check,
  X
} from 'lucide-react';

interface UserPreferences {
  interests: string[];
  customInterests: string[];
  location: string;
  radius: number;
  notificationTypes: string[];
}

const interestCategories = [
  {
    id: 'transportation',
    label: 'Transportation',
    icon: Car,
    interests: ['Traffic', 'Public Transit', 'Bike Lanes', 'Parking', 'Road Construction']
  },
  {
    id: 'events',
    label: 'Events & Entertainment',
    icon: Calendar,
    interests: ['Concerts', 'Festivals', 'Sports', 'Theater', 'Exhibitions', 'Food Festivals']
  },
  {
    id: 'safety',
    label: 'Safety & Security',
    icon: AlertTriangle,
    interests: ['Accidents', 'Crime Reports', 'Emergency Services', 'Weather Alerts']
  },
  {
    id: 'lifestyle',
    label: 'Lifestyle',
    icon: Heart,
    interests: ['Restaurants', 'Cafes', 'Shopping', 'Fitness', 'Parks', 'Cultural Sites']
  },
  {
    id: 'business',
    label: 'Business & Work',
    icon: Briefcase,
    interests: ['Office Spaces', 'Coworking', 'Business Events', 'Networking']
  },
  {
    id: 'education',
    label: 'Education',
    icon: GraduationCap,
    interests: ['Universities', 'Libraries', 'Workshops', 'Educational Events']
  }
];

interface OnboardingFlowProps {
  onComplete: (user: User, preferences: UserPreferences) => void;
}

export default function OnboardingFlow({ onComplete }: OnboardingFlowProps) {
  const [user, setUser] = useState<User | null>(null);
  const [step, setStep] = useState<'login' | 'interests' | 'location' | 'complete'>('login');
  const [preferences, setPreferences] = useState<UserPreferences>({
    interests: [],
    customInterests: [],
    location: '',
    radius: 5,
    notificationTypes: ['events', 'safety', 'traffic']
  });
  const [customInterest, setCustomInterest] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser);
        // Check if user has completed onboarding
        const userDoc = await getDoc(doc(db, 'users', firebaseUser.uid));
        if (userDoc.exists() && userDoc.data()?.onboardingComplete) {
          onComplete(firebaseUser, userDoc.data()?.preferences || preferences);
        } else {
          setStep('interests');
        }
      } else {
        setUser(null);
        setStep('login');
      }
    });

    return () => unsubscribe();
  }, [onComplete]);

  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      const provider = new GoogleAuthProvider();
      provider.addScope('profile');
      provider.addScope('email');
      
      const result = await signInWithPopup(auth, provider);
      console.log('Google login successful:', result.user);
    } catch (error: any) {
      console.error('Google login error:', error);
      // Handle specific error cases
      if (error?.code === 'auth/popup-closed-by-user') {
        console.log('Login popup was closed by user');
      } else if (error?.code === 'auth/popup-blocked') {
        console.log('Login popup was blocked by browser');
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleInterest = (interest: string) => {
    setPreferences(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const addCustomInterest = () => {
    if (customInterest.trim() && !preferences.customInterests.includes(customInterest.trim())) {
      setPreferences(prev => ({
        ...prev,
        customInterests: [...prev.customInterests, customInterest.trim()]
      }));
      setCustomInterest('');
    }
  };

  const removeCustomInterest = (interest: string) => {
    setPreferences(prev => ({
      ...prev,
      customInterests: prev.customInterests.filter(i => i !== interest)
    }));
  };

  const handleNext = async () => {
    if (step === 'interests') {
      setStep('location');
    } else if (step === 'location') {
      setStep('complete');
      // Save user preferences to Firestore
      if (user) {
        await setDoc(doc(db, 'users', user.uid), {
          email: user.email,
          displayName: user.displayName,
          photoURL: user.photoURL,
          preferences,
          onboardingComplete: true,
          createdAt: new Date(),
          updatedAt: new Date()
        });
        onComplete(user, preferences);
      }
    }
  };

  const canProceed = () => {
    if (step === 'interests') {
      return preferences.interests.length > 0 || preferences.customInterests.length > 0;
    }
    if (step === 'location') {
      return preferences.location.trim().length > 0;
    }
    return true;
  };

  if (step === 'login') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <Card className="w-full max-w-md mx-4">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-4">
              <MapPin className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold">Welcome to CityScape</CardTitle>
            <CardDescription>
              Your smart city companion. Get personalized updates about your city.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={handleGoogleLogin} 
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {loading ? 'Signing in...' : 'Continue with Google'}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (step === 'interests') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">What interests you?</h1>
            <p className="text-gray-600">Select topics you'd like to stay updated on</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {interestCategories.map((category) => (
              <Card key={category.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center space-x-2">
                    <category.icon className="w-5 h-5 text-blue-600" />
                    <CardTitle className="text-lg">{category.label}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {category.interests.map((interest) => (
                      <div key={interest} className="flex items-center space-x-2">
                        <Checkbox
                          id={interest}
                          checked={preferences.interests.includes(interest)}
                          onCheckedChange={() => toggleInterest(interest)}
                        />
                        <label htmlFor={interest} className="text-sm cursor-pointer">
                          {interest}
                        </label>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Plus className="w-5 h-5" />
                <span>Add Custom Interests</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2 mb-4">
                <Input
                  value={customInterest}
                  onChange={(e) => setCustomInterest(e.target.value)}
                  placeholder="Enter custom interest..."
                  onKeyPress={(e) => e.key === 'Enter' && addCustomInterest()}
                />
                <Button onClick={addCustomInterest} disabled={!customInterest.trim()}>
                  Add
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {preferences.customInterests.map((interest) => (
                  <Badge key={interest} variant="secondary" className="flex items-center space-x-1">
                    <span>{interest}</span>
                    <button
                      onClick={() => removeCustomInterest(interest)}
                      className="ml-1 hover:text-red-500"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end">
            <Button 
              onClick={handleNext} 
              disabled={!canProceed()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Next <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'location') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Where are you located?</h1>
            <p className="text-gray-600">Help us show you relevant local updates</p>
          </div>

          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Location
                  </label>
                  <Input
                    value={preferences.location}
                    onChange={(e) => setPreferences(prev => ({ ...prev, location: e.target.value }))}
                    placeholder="Enter your city or neighborhood..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Update Radius (km)
                  </label>
                  <Input
                    type="number"
                    min="1"
                    max="50"
                    value={preferences.radius}
                    onChange={(e) => setPreferences(prev => ({ ...prev, radius: parseInt(e.target.value) }))}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-between mt-8">
            <Button 
              variant="outline" 
              onClick={() => setStep('interests')}
            >
              Back
            </Button>
            <Button 
              onClick={handleNext} 
              disabled={!canProceed()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Complete Setup <Check className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return null;
} 