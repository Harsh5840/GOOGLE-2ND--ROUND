export interface ChatResponse {
  intent: string;
  entities: {
    [key: string]: any;
  };
  reply: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: Date;
  entities?: {
    [key: string]: any;
  };
}