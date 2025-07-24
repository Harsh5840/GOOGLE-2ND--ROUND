export interface ChatResponse {
  intent: string;
  entities: {
    [key: string]: any;
  };
  reply: string;
}

export interface ChatMessage {
  id: number;
  type: 'user' | 'bot';
  message: string;
  timestamp: Date;
  entities?: {
    [key: string]: any;
  };
}