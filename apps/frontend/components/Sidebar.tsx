import React from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { TrendingUp, Filter, Search, Podcast } from "lucide-react"
import EventFeed from "./EventFeed"
import Link from "next/link"
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Slider } from "@/components/ui/slider"
import { generatePodcast, getPodcastJobStatus, getPodcastAudioUrl } from "@/lib/api";

interface SidebarProps {
  isMobile: boolean
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  isDarkMode: boolean
  searchQuery: string
  setSearchQuery: (query: string) => void
  activeFilters: string[]
  toggleFilter: (filterId: string) => void
  filteredEvents: any[]
  handleEventSelect: (event: any) => void
  mobileChatExpanded: boolean
}

const Sidebar: React.FC<SidebarProps> = ({
  isMobile,
  sidebarOpen,
  setSidebarOpen,
  isDarkMode,
  searchQuery,
  setSearchQuery,
  activeFilters,
  toggleFilter,
  filteredEvents,
  handleEventSelect,
  mobileChatExpanded,
}) => {
  const [podcastLength, setPodcastLength] = React.useState(2);
  const [podcastCity, setPodcastCity] = React.useState("Bengaluru");
  const [isPodcastLoading, setIsPodcastLoading] = React.useState(false);
  const [jobId, setJobId] = React.useState<string | null>(null);
  const [jobStatus, setJobStatus] = React.useState<string>("");
  const [audioUrl, setAudioUrl] = React.useState<string | null>(null);

  const pollJobStatus = async (jobId: string) => {
    try {
      const status = await getPodcastJobStatus(jobId);
      setJobStatus(status.status);
      if (status.status === "completed" && status.audio_file) {
        setAudioUrl(getPodcastAudioUrl(status.audio_file));
      } else if (status.status !== "completed") {
        setTimeout(() => pollJobStatus(jobId), 2000);
      }
    } catch (err) {
      setJobStatus("error");
    }
  };

  const handleGeneratePodcast = async () => {
    setIsPodcastLoading(true);
    setJobStatus("");
    setAudioUrl(null);
    try {
      const result = await generatePodcast(podcastCity, podcastLength);
      setJobId(result.job_id);
      setJobStatus("pending");
      pollJobStatus(result.job_id);
    } catch (err) {
      setJobStatus("error");
      alert("Failed to generate podcast. Please try again.");
    } finally {
      setIsPodcastLoading(false);
    }
  };

  return (
    <>
      {/* Mobile Sidebar Overlay */}
      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Enhanced Left Sidebar with Social Feed */}
      <aside
        className={`$${
          isMobile
            ? `fixed left-0 top-16 w-80 z-50 transform transition-transform duration-300 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} ${mobileChatExpanded ? "bottom-80" : "bottom-16"}`
            : "w-80 lg:w-96"
        } backdrop-blur-xl border-r flex flex-col shadow-2xl transition-all duration-500 ${
          isDarkMode
            ? "bg-gray-900/90 border-gray-600/30 shadow-blue-900/40"
            : "bg-white/70 border-white/30 shadow-blue-500/5"
        }`}
      >
        <div className="flex-1 overflow-y-auto">
          <div className={`p-4 md:p-6 lg:p-8 ${isMobile ? "pb-8" : ""}`}>
            {/* Podcast Button */}
            <div className="mb-6 flex justify-start">
              <Dialog>
                <DialogTrigger asChild>
                  <Button
                    className={`gap-2 px-4 py-2 rounded-xl font-bold text-base shadow-lg transition-all duration-300 hover:scale-105 ${
                      isDarkMode
                        ? "bg-blue-700/90 text-white hover:bg-blue-800/90"
                        : "bg-blue-600/90 text-white hover:bg-blue-700/90"
                    }`}
                  >
                    <span className="flex items-center">
                      <Podcast className="w-5 h-5 mr-2" />
                      Podcasts
                    </span>
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Generate Podcast</DialogTitle>
                    <DialogDescription>
                      Enter the city and select the length (in minutes) for your podcast. Default is 2 minutes.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="flex flex-col items-center gap-4 mt-4">
                    <Input
                      placeholder="Enter city (e.g., New York)"
                      value={podcastCity}
                      onChange={e => setPodcastCity(e.target.value)}
                      className="mb-2"
                    />
                    <span className="font-medium">Length: <span id="podcast-length-value">{podcastLength}</span> min</span>
                    <Slider
                      min={1}
                      max={10}
                      step={1}
                      defaultValue={[2]}
                      value={[podcastLength]}
                      onValueChange={val => {
                        if (val && val[0]) setPodcastLength(val[0]);
                      }}
                      className="w-3/4"
                    />
                    {jobStatus && (
                      <div className="mt-2 text-sm font-medium">
                        Status: {jobStatus}
                      </div>
                    )}
                    {audioUrl && (
                      <div className="mt-4 flex flex-col items-center gap-2">
                        <audio controls src={audioUrl}></audio>
                        <a href={audioUrl} download>
                          <Button>Download Podcast</Button>
                        </a>
                      </div>
                    )}
                  </div>
                  <DialogFooter>
                    <Button type="button" onClick={handleGeneratePodcast} disabled={isPodcastLoading}>
                      {isPodcastLoading ? "Generating..." : "Confirm"}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
            {/* Enhanced Search */}
            <div className="relative mb-6 md:mb-8 group">
              <Search className="absolute left-4 md:left-5 top-1/2 transform -translate-y-1/2 w-4 h-4 md:w-5 md:h-5 text-gray-400 group-focus-within:text-blue-500 transition-colors duration-300" />
              <Input
                placeholder="Search locations, events..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={`pl-12 md:pl-14 pr-4 md:pr-6 py-3 md:py-4 backdrop-blur-sm border focus:border-blue-400 focus:ring-blue-400/20 rounded-xl md:rounded-2xl h-12 md:h-14 text-sm md:text-base font-medium shadow-lg transition-all duration-300 hover:shadow-xl focus:shadow-xl focus:scale-[1.02] ${
                  isDarkMode
                    ? "bg-gray-800/60 border-gray-600/30 text-gray-200 placeholder-gray-400"
                    : "bg-white/60 border-white/40 shadow-blue-500/5"
                }`}
              />
              <div className="absolute inset-0 rounded-xl md:rounded-2xl bg-gradient-to-r from-blue-500/20 to-purple-500/20 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            </div>

            {/* Social Event Feed */}
            <div className="mb-6 md:mb-8">
              <div className="flex items-center justify-between mb-4 md:mb-6">
                <h3
                  className={`text-base md:text-lg font-bold flex items-center ${isDarkMode ? "text-gray-100" : "text-gray-900"}`}
                >
                  <TrendingUp className="w-4 h-4 md:w-5 md:h-5 mr-2 md:mr-3 text-blue-500 animate-pulse" />
                  Live Feed
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  className={`text-xs px-2 py-1 rounded-lg ${isDarkMode ? "text-gray-300 hover:text-gray-100" : "text-gray-600 hover:text-gray-800"}`}
                >
                  <Filter className="w-3 h-3 mr-1" />
                  Filter
                </Button>
              </div>
              {/* Event List */}
              <EventFeed
                events={filteredEvents}
                isDarkMode={isDarkMode}
                onLike={() => {}}
                onBookmark={() => {}}
                onSelect={handleEventSelect}
                likedEvents={new Set()}
                bookmarkedEvents={new Set()}
              />
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

export default Sidebar 