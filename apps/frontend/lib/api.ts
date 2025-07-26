import axios from 'axios';
import { ChatResponse } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function sendChatMessage(userId: string, message: string): Promise<ChatResponse> {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      user_id: userId,
      message,
    });
    return response.data;
  } catch (error: any) {
    console.error('Error sending chat message:', error);
    throw error;
  }
}

export async function getLocationMood(location: string, datetimeStr?: string): Promise<any> {
  try {
    const params: any = { location };
    if (datetimeStr) params.datetime_str = datetimeStr;
    const response = await axios.post(`${API_BASE_URL}/location_mood`, null, { params });
    return response.data;
  } catch (error: any) {
    console.error('Error fetching location mood:', error);
    throw error;
  }
}

function joinUrl(base: string, path: string) {
  if (base.endsWith("/")) base = base.slice(0, -1);
  if (path.startsWith("/")) path = path.slice(1);
  return `${base}/${path}`;
}

export async function generatePodcast(city: string, duration: number, voice = "en-US-Studio-Q", speakingRate = 1.0) {
  const response = await axios.post(joinUrl(API_BASE_URL, "/podcast/generate"), {
    city,
    duration_minutes: duration,
    voice,
    speaking_rate: speakingRate,
  });
  return response.data; // { job_id, ... }
}

export async function pollPodcastJob(jobId: string) {
  // Poll until status is completed
  while (true) {
    const res = await axios.get(joinUrl(API_BASE_URL, `/jobs/${jobId}`));
    if (res.data.status === "completed") return res.data;
    if (res.data.status === "failed") throw new Error(res.data.message || "Podcast generation failed");
    await new Promise(r => setTimeout(r, 2000));
  }
}

export function getPodcastAudioUrl(filename: string) {
  return joinUrl(API_BASE_URL, `/files/${filename}`);
}

// Event Photos API
export async function uploadEventPhoto(formData: FormData): Promise<any> {
  try {
    const response = await axios.post(`${API_BASE_URL}/upload_event_photo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error: any) {
    console.error('Error uploading event photo:', error);
    throw error;
  }
}

export async function getEventPhotos(): Promise<any[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/event_photos`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching event photos:', error);
    throw error;
  }
}

export async function getEventPhotoById(photoId: string): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/event_photos/${photoId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching event photo:', error);
    throw error;
  }
}

// User Profile Management
export async function createOrUpdateUserProfile(userId: string, profileData: any): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('profile_data', JSON.stringify(profileData));
    
    const response = await axios.post(`${API_BASE_URL}/user/profile`, formData);
    return response.data;
  } catch (error: any) {
    console.error('Error creating/updating user profile:', error);
    throw error;
  }
}

export async function getUserProfile(userId: string): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/profile/${userId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
}

export async function getUserDefaultLocation(userId: string): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/${userId}/default-location`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching user default location:', error);
    throw error;
  }
}

// Location Management
export async function storeUserLocation(
  userId: string, 
  latitude: number, 
  longitude: number, 
  locationName?: string, 
  activityType?: string
): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('latitude', latitude.toString());
    formData.append('longitude', longitude.toString());
    if (locationName) formData.append('location_name', locationName);
    if (activityType) formData.append('activity_type', activityType);
    
    const response = await axios.post(`${API_BASE_URL}/user/location`, formData);
    return response.data;
  } catch (error: any) {
    console.error('Error storing user location:', error);
    throw error;
  }
}

export async function getUserLocationHistory(userId: string, days: number = 7): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/${userId}/location-history?days=${days}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching user location history:', error);
    throw error;
  }
}

export async function getFavoriteLocations(userId: string): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/${userId}/favorite-locations`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching favorite locations:', error);
    throw error;
  }
}

export async function addFavoriteLocation(
  userId: string, 
  latitude: number, 
  longitude: number, 
  locationName: string
): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('latitude', latitude.toString());
    formData.append('longitude', longitude.toString());
    formData.append('location_name', locationName);
    
    const response = await axios.post(`${API_BASE_URL}/user/favorite-location`, formData);
    return response.data;
  } catch (error: any) {
    console.error('Error adding favorite location:', error);
    throw error;
  }
}

// Unified Data Management
export async function storeUnifiedData(
  location: string, 
  dataType: string, 
  data: any, 
  userId?: string
): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('location', location);
    formData.append('data_type', dataType);
    formData.append('data', JSON.stringify(data));
    if (userId) formData.append('user_id', userId);
    
    const response = await axios.post(`${API_BASE_URL}/unified-data`, formData);
    return response.data;
  } catch (error: any) {
    console.error('Error storing unified data:', error);
    throw error;
  }
}

export async function getUnifiedData(
  location: string, 
  dataType?: string, 
  hours: number = 24
): Promise<any> {
  try {
    const params: any = { hours };
    if (dataType) params.data_type = dataType;
    
    const response = await axios.get(`${API_BASE_URL}/unified-data/${location}`, { params });
    return response.data;
  } catch (error: any) {
    console.error('Error fetching unified data:', error);
    throw error;
  }
}

export async function getAggregatedData(location: string, hours: number = 24): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/unified-data/${location}/aggregated?hours=${hours}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching aggregated data:', error);
    throw error;
  }
}

// Enhanced Event Photos
export async function getUserEventPhotos(userId: string, limit: number = 50): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/${userId}/event-photos?limit=${limit}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching user event photos:', error);
    throw error;
  }
}

export async function getLocationEventPhotos(
  latitude: number, 
  longitude: number, 
  radiusKm: number = 5.0, 
  limit: number = 50
): Promise<any> {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/location/${latitude}/${longitude}/event-photos?radius_km=${radiusKm}&limit=${limit}`
    );
    return response.data;
  } catch (error: any) {
    console.error('Error fetching location event photos:', error);
    throw error;
  }
}