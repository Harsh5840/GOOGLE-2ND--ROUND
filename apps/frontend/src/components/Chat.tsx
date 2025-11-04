import React, { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Bot, Send, GripVertical, Minimize2, Maximize2, X } from "lucide-react"

interface ChatProps {
  isDarkMode: boolean
  chatMessages: any[]
  chatInput: string
  setChatInput: (input: string) => void
  isTyping: boolean
  handleSendMessage: () => void
  chatMessagesRef: React.RefObject<HTMLDivElement>
  rightPanelCollapsed?: boolean
  setRightPanelCollapsed?: (collapsed: boolean) => void
  isDraggable?: boolean // Optional draggable mode
  isMobile?: boolean
}

const Chat: React.FC<ChatProps> = ({
  isDarkMode,
  chatMessages = [],
  chatInput = "",
  setChatInput,
  isTyping,
  handleSendMessage,
  chatMessagesRef,
  rightPanelCollapsed = false,
  setRightPanelCollapsed,
  isDraggable = false,
  isMobile = false,
}) => {
  const [position, setPosition] = useState({ x: 20, y: 20 })
  const [isDragging, setIsDragging] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const chatRef = useRef<HTMLDivElement>(null)
  const dragRef = useRef<HTMLDivElement>(null)

  // Handle dragging
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!chatRef.current) return
    
    const rect = chatRef.current.getBoundingClientRect()
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
    setIsDragging(true)
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return
    
    const newX = e.clientX - dragOffset.x
    const newY = e.clientY - dragOffset.y
    
    // Keep within viewport bounds
    const maxX = window.innerWidth - 400 // Chat width
    const maxY = window.innerHeight - (isMinimized ? 60 : 500) // Chat height
    
    setPosition({
      x: Math.max(0, Math.min(newX, maxX)),
      y: Math.max(0, Math.min(newY, maxY))
    })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, dragOffset])

  // If draggable mode is enabled, use the floating draggable chat
  if (isDraggable) {
    return (
      <div
        ref={chatRef}
        className={`fixed z-40 w-96 shadow-2xl rounded-lg border transition-all duration-200 ${
          isDarkMode ? "bg-gray-800 border-gray-600" : "bg-white border-gray-200"
        } ${isDragging ? "cursor-grabbing" : ""}`}
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
          height: isMinimized ? 'auto' : '500px'
        }}
      >
        {/* Draggable Header */}
        <div
          ref={dragRef}
          className={`p-3 border-b cursor-grab active:cursor-grabbing select-none ${
            isDarkMode ? "border-gray-600" : "border-gray-200"
          }`}
          onMouseDown={handleMouseDown}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <GripVertical className={`w-4 h-4 ${isDarkMode ? "text-gray-400" : "text-gray-500"}`} />
              <div className="w-6 h-6 bg-gradient-to-br from-purple-500 via-pink-500 to-indigo-500 rounded-md flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className={`font-semibold text-xs ${isDarkMode ? "text-gray-100" : "text-gray-900"}`}>City Assistant</h3>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMinimized(!isMinimized)}
                className={`w-6 h-6 p-0 ${isDarkMode ? "text-gray-400 hover:text-gray-200" : "text-gray-500 hover:text-gray-700"}`}
              >
                {isMinimized ? <Maximize2 className="w-3 h-3" /> : <Minimize2 className="w-3 h-3" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Chat Content - Hidden when minimized */}
        {!isMinimized && (
          <>
            {/* Messages */}
            <div ref={chatMessagesRef} className="h-80 overflow-y-auto p-3 space-y-2">
              {chatMessages.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <Bot className="w-6 h-6 mx-auto mb-2 opacity-50" />
                  <p className="text-xs">Start a conversation</p>
                </div>
              ) : (
                chatMessages.map((message, index) => (
                  <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[80%] rounded-lg px-2 py-1 text-xs ${
                      message.sender === "user" ? "bg-blue-600 text-white" : isDarkMode ? "bg-gray-700 text-gray-100" : "bg-gray-100 text-gray-900"
                    }`}>
                      {message.text}
                    </div>
                  </div>
                ))
              )}
              {isTyping && (
                <div className="flex justify-start">
                  <div className={`max-w-[80%] rounded-lg px-2 py-1 text-xs ${isDarkMode ? "bg-gray-700 text-gray-100" : "bg-gray-100 text-gray-900"}`}>
                    <div className="flex space-x-1">
                      <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className={`p-3 border-t ${isDarkMode ? "border-gray-600" : "border-gray-200"}`}>
              <div className="flex space-x-2">
                <Input
                  placeholder="Type message..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1 text-xs h-8"
                />
                <Button onClick={handleSendMessage} disabled={!chatInput.trim() || isTyping} size="sm" className="px-2 h-8">
                  <Send className="w-3 h-3" />
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    )
  }

  // Default: Original right-side panel layout
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