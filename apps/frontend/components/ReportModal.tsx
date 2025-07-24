import React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Camera, Upload, X } from "lucide-react"

interface ReportModalProps {
  isDarkMode: boolean
  show: boolean
  onClose: () => void
  reportForm: any
  setReportForm: (form: any) => void
  handleCameraCapture: () => void
  fileInputRef: React.RefObject<HTMLInputElement>
  handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void
  capturedImage: string | null
  setCapturedImage: (img: string | null) => void
  handleSubmitReport: () => void
  eventTypes: { id: string; label: string }[]
}

const ReportModal: React.FC<ReportModalProps> = ({
  isDarkMode,
  show,
  onClose,
  reportForm,
  setReportForm,
  handleCameraCapture,
  fileInputRef,
  handleFileUpload,
  capturedImage,
  setCapturedImage,
  handleSubmitReport,
  eventTypes,
}) => {
  if (!show) return null
  return (
    <div className="fixed inset-0 z-[10000] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div
        className={`w-full max-w-2xl backdrop-blur-xl rounded-2xl md:rounded-3xl shadow-2xl border transition-all duration-500 animate-slideUp max-h-[90vh] overflow-y-auto ${
          isDarkMode ? "bg-gray-800/90 border-gray-600/30" : "bg-white/90 border-white/30"
        }`}
      >
        <div className={`p-6 md:p-8 border-b ${isDarkMode ? "border-gray-600/30" : "border-white/30"}`}>
          <div className="flex items-center justify-between">
            <h2 className={`text-xl md:text-2xl font-bold ${isDarkMode ? "text-gray-100" : "text-gray-900"}`}>
              Report New Event
            </h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="rounded-2xl transition-all duration-300 hover:scale-110"
            >
              <X className="w-5 h-5 md:w-6 md:h-6" />
            </Button>
          </div>
        </div>

        <div className="p-6 md:p-8 space-y-6 md:space-y-8">
          <div className="group">
            <label className={`block text-sm font-semibold mb-3 ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              Event Title
            </label>
            <Input
              value={reportForm.title}
              onChange={(e) => setReportForm((prev: any) => ({ ...prev, title: e.target.value }))}
              placeholder="What's happening?"
              className={`backdrop-blur-sm border rounded-xl md:rounded-2xl h-12 font-medium shadow-lg transition-all duration-300 hover:shadow-xl focus:shadow-xl focus:scale-[1.02] group-focus-within:border-blue-400 ${
                isDarkMode
                  ? "bg-gray-700/60 border-gray-600/40 text-gray-200 placeholder-gray-400"
                  : "bg-white/60 border-white/40 shadow-blue-500/5"
              }`}
            />
          </div>

          <div className="group">
            <label className={`block text-sm font-semibold mb-3 ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              Description
            </label>
            <Textarea
              value={reportForm.description}
              onChange={(e) => setReportForm((prev: any) => ({ ...prev, description: e.target.value }))}
              placeholder="Describe the event in detail..."
              className={`backdrop-blur-sm border rounded-xl md:rounded-2xl min-h-[120px] font-medium shadow-lg transition-all duration-300 hover:shadow-xl focus:shadow-xl focus:scale-[1.02] group-focus-within:border-blue-400 ${
                isDarkMode
                  ? "bg-gray-700/60 border-gray-600/40 text-gray-200 placeholder-gray-400"
                  : "bg-white/60 border-white/40 shadow-blue-500/5"
              }`}
            />
          </div>

          <div className="group">
            <label className={`block text-sm font-semibold mb-3 ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              Event Type
            </label>
            <select
              value={reportForm.type}
              onChange={(e) => setReportForm((prev: any) => ({ ...prev, type: e.target.value }))}
              className={`w-full p-4 backdrop-blur-sm border rounded-xl md:rounded-2xl focus:border-blue-400 focus:ring-blue-400/20 font-medium shadow-lg transition-all duration-300 hover:shadow-xl focus:shadow-xl focus:scale-[1.02] ${
                isDarkMode
                  ? "bg-gray-700/60 border-gray-600/40 text-gray-200"
                  : "bg-white/60 border-white/40 shadow-blue-500/5"
              }`}
            >
              {eventTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className={`block text-sm font-semibold mb-3 ${isDarkMode ? "text-gray-100" : "text-gray-700"}`}>
              Add Photo
            </label>
            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
              <Button
                type="button"
                onClick={handleCameraCapture}
                className="flex-1 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white rounded-xl md:rounded-2xl h-12 md:h-14 font-semibold shadow-xl shadow-green-500/25 transition-all duration-300 hover:scale-[1.02] group"
              >
                <Camera className="w-5 h-5 md:w-6 md:h-6 mr-2 md:mr-3 group-hover:animate-bounce" />
                Take Photo
              </Button>
              <Button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
                className={`flex-1 rounded-xl md:rounded-2xl h-12 md:h-14 font-semibold shadow-lg transition-all duration-300 hover:scale-[1.02] group ${
                  isDarkMode
                    ? "border-gray-600/40 hover:bg-gray-700/60"
                    : "border-white/40 hover:bg-white/60 shadow-blue-500/5"
                }`}
              >
                <Upload className="w-5 h-5 md:w-6 md:h-6 mr-2 md:mr-3 group-hover:animate-bounce" />
                Upload File
              </Button>
            </div>
            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
          </div>

          {capturedImage && (
            <div className="relative animate-fadeIn">
              <img
                src={capturedImage || "/placeholder.svg"}
                alt="Captured"
                className="w-full h-48 md:h-64 object-cover rounded-xl md:rounded-2xl shadow-lg transition-all duration-300 hover:scale-[1.02]"
              />
              <Button
                onClick={() => {
                  setCapturedImage(null)
                  setReportForm((prev: any) => ({ ...prev, image: null }))
                }}
                variant="ghost"
                size="icon"
                className="absolute top-4 right-4 bg-black/60 hover:bg-black/80 text-white rounded-2xl backdrop-blur-sm transition-all duration-300 hover:scale-110"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
          )}
        </div>

        <div
          className={`p-6 md:p-8 border-t flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 ${isDarkMode ? "border-gray-600/30" : "border-white/30"}`}
        >
          <Button
            variant="outline"
            onClick={onClose}
            className={`flex-1 rounded-xl md:rounded-2xl h-12 md:h-14 font-semibold shadow-lg transition-all duration-300 hover:scale-[1.02] ${
              isDarkMode
                ? "border-gray-600/40 hover:bg-gray-700/60"
                : "border-white/40 hover:bg-white/60 shadow-blue-500/5"
            }`}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmitReport}
            className="flex-1 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 text-white rounded-xl md:rounded-2xl h-12 md:h-14 font-semibold shadow-xl shadow-blue-500/25 transition-all duration-300 hover:scale-[1.02] group"
          >
            Submit Report
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ReportModal 