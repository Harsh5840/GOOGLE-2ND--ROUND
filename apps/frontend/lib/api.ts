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

export async function generatePodcast(city: string, duration: number, voice: string = "en-US-Studio-Q", speakingRate: number = 1.0) {
  try {
    const response = await axios.post(`${API_BASE_URL}/podcast/generate`, {
      city,
      duration_minutes: duration,
      voice,
      speaking_rate: speakingRate
    });
    return response.data;
  } catch (error: any) {
    console.error('Error generating podcast:', error);
    throw error;
  }
}

export async function getPodcastJobStatus(jobId: string) {
  try {
    const response = await axios.get(`${API_BASE_URL}/jobs/${jobId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching podcast job status:', error);
    throw error;
  }
}

export function getPodcastAudioUrl(filename: string) {
  return `${API_BASE_URL}/files/${filename}`;
}