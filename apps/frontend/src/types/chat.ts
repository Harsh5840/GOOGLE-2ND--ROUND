export interface ChatResponse {
  intent: string;
  entities: {
    [key: string]: any;
  };
  reply: string;
  location_data?: {
    locations_to_display?: any[];
    mood_data?: any;
    route_details?: any;
    places?: any[];
    summary?: string;
  };
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: Date;
  locationData?: {
    locations_to_display?: any[];
    mood_data?: any;
    route_details?: any;
    places?: any[];
    summary?: string;
  };
}