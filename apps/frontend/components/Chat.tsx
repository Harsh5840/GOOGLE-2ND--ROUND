import React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Bot, ChevronRight, ChevronUp, ChevronDown, Send } from "lucide-react"

interface ChatProps {
  isDarkMode: boolean
  isMobile: boolean
  rightPanelCollapsed: boolean
  setRightPanelCollapsed: (collapsed: boolean) => void
  chatMessages: any[]
  chatInput: string
  setChatInput: (input: string) => void
  isTyping: boolean
  handleSendMessage: () => void
  chatMessagesRef: React.RefObject<HTMLDivElement>
  mobileChatRef: React.RefObject<HTMLDivElement>
  mobileChatOpen: boolean
  mobileChatExpanded: boolean
  setMobileChatExpanded: (expanded: boolean) => void
}

const Chat: React.FC<ChatProps> = ({
  isDarkMode,
  isMobile,
  rightPanelCollapsed,
  setRightPanelCollapsed,
  chatMessages,
  chatInput,
  setChatInput,
  isTyping,
  handleSendMessage,
  chatMessagesRef,
  mobileChatRef,
  mobileChatOpen,
  mobileChatExpanded,
  setMobileChatExpanded,
}) => {
  return (
    <>
      {/* Desktop Chat Panel */}
      {!isMobile && (
        <div
          className={`$${rightPanelCollapsed ? "w-16" : "w-80 lg:w-96"} backdrop-blur-xl border-l flex flex-col transition-all duration-300 relative shadow-2xl ${
            isDarkMode
              ? "bg-gray-900/90 border-gray-600/30 shadow-blue-900/40"
              : "bg-white/70 border-white/30 shadow-blue-500/5"
          }`}
        >
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setRightPanelCollapsed(!rightPanelCollapsed)}
            className={`absolute -left-4 top-6 z-10 backdrop-blur-sm shadow-xl hover:shadow-2xl rounded-full w-8 h-8 border transition-all duration-300 hover:scale-110 ${
              isDarkMode
                ? "bg-gray-800/90 border-gray-600/30 hover:bg-gray-700/90"
                : "bg-white/90 border-white/40 hover:bg-white"
            }`}
          >
            <ChevronRight
              className={`w-4 h-4 transition-transform duration-300 ${rightPanelCollapsed ? "" : "rotate-180"}`}
            />
          </Button>

          {!rightPanelCollapsed && (
            <>
              {/* Chat Header */}
              <div
                className={`p-6 md:p-8 border-b transition-all duration-500 ${isDarkMode ? "border-gray-600/30" : "border-white/30"}`}
              >
                <div className="flex items-center space-x-4 group">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 via-pink-500 to-indigo-500 rounded-2xl flex items-center justify-center shadow-xl shadow-purple-500/25 group-hover:shadow-2xl group-hover:shadow-purple-500/40 transition-all duration-300 group-hover:scale-110">
                    <Bot className="w-7 h-7 text-white animate-pulse" />
                  </div>
                  <div>
                    <h3 className={`font-bold text-lg ${isDarkMode ? "text-gray-100" : "text-gray-900"}`}>City Assistant</h3>
                    <p className={`text-sm font-medium ${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>Ask anything about your city</p>
                  </div>
                  <div className="ml-auto">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
                  </div>
                </div>
              </div>

              {/* Chat Messages */}
              <div ref={chatMessagesRef} className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
                {chatMessages.map((message, index) => (
                  <div
                    key={message.id}
                    className={`flex animate-fadeInUp ${message.type === "user" ? "justify-end" : "justify-start"}`}
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div
                      className={`max-w-[85%] rounded-3xl px-6 py-4 shadow-lg transition-all duration-300 hover:scale-[1.02] ${
                        message.type === "user"
                          ? "bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white shadow-blue-500/25"
                          : isDarkMode
                            ? "bg-gray-800/80 backdrop-blur-sm text-gray-100 border border-gray-600/30 shadow-blue-900/10"
                            : "bg-white/80 backdrop-blur-sm text-gray-900 border border-white/40 shadow-blue-500/5"
                      }`}
                    >
                      <p className="text-sm leading-relaxed font-medium">{message.message}</p>
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="flex justify-start">
                    <div
                      className={`backdrop-blur-sm rounded-3xl px-6 py-4 border shadow-lg ${
                        isDarkMode
                          ? "bg-gray-800/80 border-gray-600/30 shadow-blue-900/10"
                          : "bg-white/80 border-white/40 shadow-blue-500/5"
                      }`}
                    >
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div className={`p-6 md:p-8 border-t transition-all duration-500 ${isDarkMode ? "border-gray-600/30" : "border-white/30"}`}>
                <div className="flex space-x-4">
                  <Input
                    placeholder="Ask about traffic, events..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                    className={`flex-1 backdrop-blur-sm border focus:border-blue-400 focus:ring-blue-400/20 rounded-2xl h-12 font-medium shadow-lg transition-all duration-300 hover:shadow-xl focus:shadow-xl focus:scale-[1.02] ${
                      isDarkMode
                        ? "bg-gray-800/60 border-gray-600/30 text-gray-200 placeholder-gray-400"
                        : "bg-white/60 border-white/40 shadow-blue-500/5"
                    }`}
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!chatInput.trim() || isTyping}
                    className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 rounded-2xl w-12 h-12 p-0 shadow-xl shadow-blue-500/25 transition-all duration-300 hover:scale-110 group"
                  >
                    <Send className="w-5 h-5 group-hover:animate-pulse" />
                  </Button>
                </div>
              </div>
            </>
          )}

          {rightPanelCollapsed && (
            <div className="p-4 flex flex-col items-center space-y-6 mt-8">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 via-pink-500 to-indigo-500 rounded-2xl flex items-center justify-center shadow-xl shadow-purple-500/25 transition-all duration-300 hover:scale-110">
                <Bot className="w-7 h-7 text-white animate-pulse" />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Mobile Chat Bar */}
      {isMobile && (
        <div
          ref={mobileChatRef}
          className={`fixed bottom-0 left-0 right-0 z-50 transition-all duration-500 ${mobileChatExpanded ? "h-80" : "h-16"}`}
        >
          {/* Chat Bar */}
          <div
            className={`backdrop-blur-xl border-t shadow-2xl transition-all duration-500 ${
              isDarkMode
                ? "bg-gray-900/90 border-gray-600/30 shadow-blue-900/40"
                : "bg-white/90 border-white/30 shadow-blue-500/10"
            } ${mobileChatExpanded ? "h-full" : "h-16"}`}
          >
            {/* Chat Header Bar */}
            <div
              className="h-16 flex items-center justify-between px-4 cursor-pointer"
              onClick={() => setMobileChatExpanded(!mobileChatExpanded)}
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 via-pink-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
                  <Bot className="w-6 h-6 text-white animate-pulse" />
                </div>
                <div>
                  <h3 className={`font-bold text-sm ${isDarkMode ? "text-gray-100" : "text-gray-900"}`}>City Assistant</h3>
                  <p className={`text-xs ${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>{isTyping ? "Typing..." : "Ask me anything"}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <Button variant="ghost" size="icon" className="w-8 h-8 rounded-lg">
                  {mobileChatExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
                </Button>
              </div>
            </div>

            {/* Expanded Chat Content */}
            {mobileChatExpanded && (
              <div className="flex flex-col h-64">
                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {chatMessages.map((message, index) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-lg ${
                          message.type === "user"
                            ? "bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white"
                            : isDarkMode
                              ? "bg-gray-800/80 text-gray-100 border border-gray-600/30"
                              : "bg-white/80 text-gray-900 border border-white/40"
                        }`}
                      >
                        <p className="text-sm leading-relaxed">{message.message}</p>
                      </div>
                    </div>
                  ))}

                  {isTyping && (
                    <div className="flex justify-start">
                      <div
                        className={`rounded-2xl px-4 py-3 border shadow-lg ${
                          isDarkMode ? "bg-gray-800/80 border-gray-600/30" : "bg-white/80 border-white/40"
                        }`}
                      >
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Chat Input */}
                <div className="p-4 border-t border-gray-200/20">
                  <div className="flex space-x-3">
                    <Input
                      placeholder="Ask about traffic, events..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                      className={`flex-1 rounded-xl h-10 text-sm ${
                        isDarkMode
                          ? "bg-gray-800/60 border-gray-600/30 text-gray-200 placeholder-gray-400"
                          : "bg-white/60 border-white/40"
                      }`}
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!chatInput.trim() || isTyping}
                      className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 rounded-xl w-10 h-10 p-0 shadow-lg"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}

export default Chat 