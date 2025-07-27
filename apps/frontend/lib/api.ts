import axios from 'axios';
import { ChatResponse } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://city-api-gateway-ixlmqkeuva-uc.a.run.app/api/v1';

export async function sendChatMessage(userId: string, message: string): Promise<ChatResponse> {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      user_id: userId,
      message: message,
    });
    return response.data;
  } catch (error: any) {
    console.error('Error sending chat message:', error);
    throw error;
  }
}

// Location Display and Mood Map Functions
export async function displayLocationsOnMap(locations: any[]): Promise<any> {
  try {
    const response = await axios.post(`${API_BASE_URL}/display_locations`, {
      locations: locations
    });
    return response.data;
  } catch (error: any) {
    console.error('Error displaying locations on map:', error);
    throw error;
  }
}

export async function getLocationMoodWithDisplay(location: string, datetimeStr?: string): Promise<any> {
  try {
    const params: any = { location };
    if (datetimeStr) params.datetime_str = datetimeStr;
    const response = await axios.post(`${API_BASE_URL}/location_mood`, null, { params });
    return response.data;
  } catch (error: any) {
    console.error('Error fetching location mood with display:', error);
    throw error;
  }
}

export async function getBestRouteWithMood(origin: string, destination: string, mode: string = "driving"): Promise<any> {
  try {
    const response = await axios.post(`${API_BASE_URL}/best_route`, {
      origin: origin,
      destination: destination,
      mode: mode
    });
    return response.data;
  } catch (error: any) {
    console.error('Error getting best route with mood:', error);
    throw error;
  }
}

export async function getMustVisitPlacesWithMood(location: string, maxResults: number = 3): Promise<any> {
  try {
    const response = await axios.post(`${API_BASE_URL}/must_visit_places`, {
      location: location,
      max_results: maxResults
    });
    return response.data;
  } catch (error: any) {
    console.error('Error getting must-visit places with mood:', error);
    throw error;
  }
}

// New API functions for reports and events
export async function submitReport(reportData: {
  type: string;
  title: string;
  location: string;
  coordinates: { lat: number; lng: number };
  severity: string;
  summary: string;
  image?: string;
  tags: string[];
  customEmoji?: string;
}): Promise<any> {
  try {
    const response = await axios.post(`${API_BASE_URL}/reports`, reportData);
    return response.data;
  } catch (error: any) {
    console.error('Error submitting report:', error);
    throw error;
  }
}

// Gemini Photo Classification API Functions
export async function classifyPhoto(file: File, latitude: number, longitude: number, userId: string): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('latitude', latitude.toString());
    formData.append('longitude', longitude.toString());
    formData.append('user_id', userId);

    const response = await axios.post(`${API_BASE_URL}/classify_photo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error classifying photo:', error);
    throw error;
  }
}

export async function submitClassifiedReport(
  file: File,
  latitude: number,
  longitude: number,
  userId: string,
  title: string,
  description: string,
  category: string,
  severity: string
): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('latitude', latitude.toString());
    formData.append('longitude', longitude.toString());
    formData.append('user_id', userId);
    formData.append('title', title);
    formData.append('description', description);
    formData.append('category', category);
    formData.append('severity', severity);

    const response = await axios.post(`${API_BASE_URL}/submit_classified_report`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error submitting classified report:', error);
    throw error;
  }
}

export async function getAllUserReports(limit: number = 100): Promise<any[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/user_reports?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error getting user reports:', error);
    throw error;
  }
}

export async function getEvents(filters?: {
  type?: string;
  location?: string;
  severity?: string;
  search?: string;
}): Promise<any[]> {
  try {
    const params = filters || {};
    const response = await axios.get(`${API_BASE_URL}/events`, { params });
    return response.data;
  } catch (error: any) {
    console.error('Error fetching events:', error);
    throw error;
  }
}

export async function searchLocation(query: string): Promise<any[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/search/location`, {
      params: { query }
    });
    return response.data;
  } catch (error: any) {
    console.error('Error searching location:', error);
    throw error;
  }
}

export async function geocodeLocation(address: string): Promise<{ lat: number; lng: number }> {
  try {
    const response = await axios.get(`${API_BASE_URL}/geocode`, {
      params: { address }
    });
    return response.data;
  } catch (error: any) {
    console.error('Error geocoding location:', error);
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

// User Data Retention API
export async function exportUserData(userId: string): Promise<any> {
  const formData = new FormData();
  formData.append('user_id', userId);
  
  const response = await fetch(`${API_BASE_URL}/user/export`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to export user data: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getUserDataExports(userId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/user/${userId}/exports`);
  
  if (!response.ok) {
    throw new Error(`Failed to get user data exports: ${response.statusText}`);
  }
  
  return response.json();
}

export async function restoreUserData(userId: string, backupData: any): Promise<any> {
  const formData = new FormData();
  formData.append('backup_data', JSON.stringify(backupData));
  
  const response = await fetch(`${API_BASE_URL}/user/${userId}/restore`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to restore user data: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getUserRetentionAnalytics(userId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/user/${userId}/retention-analytics`);
  
  if (!response.ok) {
    throw new Error(`Failed to get retention analytics: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getUserQueryHistory(userId: string, limit: number = 20): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/user/${userId}/query-history?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get query history: ${response.statusText}`);
  }
  
  return response.json();
}

// Enhanced Unified Data Management API
export async function loadUnifiedDataToFirestore(location: string, dataSources: string[] = ['reddit', 'twitter', 'news', 'maps', 'rag']): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('data_sources', dataSources.join(','));
    
    const response = await axios.post(`${API_BASE_URL}/unified-data/${location}/load`, formData);
    return response.data;
  } catch (error: any) {
    console.error('Error loading unified data to Firestore:', error);
    throw error;
  }
}

export async function getUnifiedDataSources(location: string): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/unified-data/${location}/sources`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching unified data sources:', error);
    throw error;
  }
}

export async function refreshUnifiedData(location: string, dataSources: string[] = ['reddit', 'twitter', 'news', 'maps', 'rag']): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('data_sources', dataSources.join(','));
    
    const response = await axios.post(`${API_BASE_URL}/unified-data/${location}/refresh`, formData);
    return response.data;
  } catch (error: any) {
    console.error('Error refreshing unified data:', error);
    throw error;
  }
}

export async function getUnifiedDataFromFirestore(
  location: string, 
  dataType?: string, 
  hours: number = 24, 
  forceRefresh: boolean = false
): Promise<any> {
  try {
    const params: any = { hours, force_refresh: forceRefresh };
    if (dataType) params.data_type = dataType;
    
    const response = await axios.get(`${API_BASE_URL}/unified-data/${location}/firestore`, { params });
    return response.data;
  } catch (error: any) {
    console.error('Error fetching unified data from Firestore:', error);
    throw error;
  }
}

export async function getAggregatedDataFromFirestore(location: string, hours: number = 24): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/unified-data/${location}/aggregated/firestore?hours=${hours}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching aggregated data from Firestore:', error);
    throw error;
  }
}

// Enhanced wrapper functions that use Firestore as primary source
export async function getUnifiedDataWithFirestore(
  location: string, 
  dataType?: string, 
  hours: number = 24,
  autoLoad: boolean = true
): Promise<any> {
  try {
    // First try to get data from Firestore
    let data = await getUnifiedDataFromFirestore(location, dataType, hours, false);
    
    // If no data and autoLoad is enabled, load fresh data
    if (data.count === 0 && autoLoad) {
      console.log(`No data found for ${location}, loading fresh data...`);
      await loadUnifiedDataToFirestore(location);
      data = await getUnifiedDataFromFirestore(location, dataType, hours, false);
    }
    
    return data;
  } catch (error: any) {
    console.error('Error getting unified data with Firestore:', error);
    throw error;
  }
}

export async function getAggregatedDataWithFirestore(
  location: string, 
  hours: number = 24,
  autoLoad: boolean = true
): Promise<any> {
  try {
    // First try to get aggregated data from Firestore
    let aggregated = await getAggregatedDataFromFirestore(location, hours);
    
    // If no data and autoLoad is enabled, load fresh data
    if (!aggregated.success && autoLoad) {
      console.log(`No aggregated data found for ${location}, loading fresh data...`);
      await loadUnifiedDataToFirestore(location);
      aggregated = await getAggregatedDataFromFirestore(location, hours);
    }
    
    return aggregated;
  } catch (error: any) {
    console.error('Error getting aggregated data with Firestore:', error);
    throw error;
  }
}
