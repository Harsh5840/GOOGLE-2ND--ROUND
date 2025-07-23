# Variables for the Terraform configuration

variable "project_id" {
  description = "The Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region"
  type        = string
  default     = "us-central1"
}

variable "agent_name" {
  description = "The name of the agent"
  type        = string
  default     = "news-podcast-agent"
}