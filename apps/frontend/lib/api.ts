import axios from 'axios';
import { ChatResponse } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api/v1';

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