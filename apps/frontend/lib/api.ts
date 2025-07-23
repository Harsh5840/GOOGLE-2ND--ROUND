import { ChatResponse } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function sendChatMessage(userId: string, message: string): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        message,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
}

export async function getLocationMood(location: string, datetimeStr?: string): Promise<any> {
  const params = new URLSearchParams({ location });
  if (datetimeStr) params.append('datetime_str', datetimeStr);
  const response = await fetch(`${API_BASE_URL}/api/v1/location_mood?${params.toString()}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}