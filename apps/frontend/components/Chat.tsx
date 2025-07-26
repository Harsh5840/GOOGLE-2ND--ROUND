import React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Bot, Send } from "lucide-react"

interface ChatProps {
  isDarkMode: boolean
  chatMessages: any[]
  chatInput: string
  setChatInput: (input: string) => void
  isTyping: boolean
  handleSendMessage: () => void
  chatMessagesRef: React.RefObject<HTMLDivElement>
}

const Chat: React.FC<ChatProps> = ({
  isDarkMode,
  chatMessages = [],
  chatInput = "",
  setChatInput,
  isTyping,
  handleSendMessage,
  chatMessagesRef,
}) => {
  return (
    <div className={`h-full flex flex-col ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
      {/* Chat Header */}
      <div className={`p-4 border-b ${isDarkMode ? "border-gray-600" : "border-gray-200"}`}>
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 via-pink-500 to-indigo-500 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className={`font-semibold text-sm ${isDarkMode ? "text-gray-100" : "text-gray-900"}`}>City Assistant</h3>
            <p className={`text-xs ${isDarkMode ? "text-gray-400" : "text-gray-500"}`}>Ask anything about your city</p>
          </div>
          <div className="ml-auto">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div 
        ref={chatMessagesRef} 
        className="flex-1 overflow-y-auto p-4 space-y-3"
      >
        {chatMessages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Start a conversation about your city</p>
          </div>
        ) : (
          chatMessages.map((message, index) => (
            <div
              key={message.id}
              className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
                  message.sender === "user"
                    ? "bg-blue-600 text-white"
                    : isDarkMode
                      ? "bg-gray-700 text-gray-100"
                      : "bg-gray-100 text-gray-900"
                }`}
              >
                {message.text}
              </div>
            </div>
          ))
        )}
        {isTyping && (
          <div className="flex justify-start">
            <div className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
              isDarkMode ? "bg-gray-700 text-gray-100" : "bg-gray-100 text-gray-900"
            }`}>
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Chat Input */}
      <div className={`p-4 border-t ${isDarkMode ? "border-gray-600" : "border-gray-200"}`}>
        <div className="flex space-x-2">
          <Input
            placeholder="Type your message..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!chatInput.trim() || isTyping}
            size="sm"
            className="px-3"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

export default Chat 