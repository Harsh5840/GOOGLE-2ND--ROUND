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