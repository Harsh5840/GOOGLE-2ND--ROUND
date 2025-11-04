import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getSeverityColor(severity: string) {
  switch (severity) {
    case "critical":
      return "#dc2626"
    case "high":
      return "#ea580c"
    case "medium":
      return "#ca8a04"
    case "low":
      return "#16a34a"
    default:
      return "#6b7280"
  }
}

export function formatTimeAgo(timestamp: Date) {
  const minutes = Math.floor((Date.now() - timestamp.getTime()) / 60000)
  if (minutes < 1) return "now"
  if (minutes < 60) return `${minutes}m`
  return `${Math.floor(minutes / 60)}h`
}
