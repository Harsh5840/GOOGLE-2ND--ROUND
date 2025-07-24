# Terraform configuration for news-podcast-agent

provider "google" {
  project = var.project_id
  region  = var.region
}

# Create a GCS bucket for agent artifacts
resource "google_storage_bucket" "agent_artifacts" {
  name     = "${var.project_id}-news-podcast-agent-artifacts"
  location = var.region
  force_destroy = true
  uniform_bucket_level_access = true
}

# Create a GCS bucket for agent logs
resource "google_storage_bucket" "agent_logs" {
  name     = "${var.project_id}-news-podcast-agent-logs"
  location = var.region
  force_destroy = true
  uniform_bucket_level_access = true
}

# Create a BigQuery dataset for analytics
resource "google_bigquery_dataset" "agent_analytics" {
  dataset_id                  = "news_podcast_agent_analytics"
  friendly_name               = "News Podcast Agent Analytics"
  description                 = "Dataset for news podcast agent analytics"
  location                    = var.region
  delete_contents_on_destroy  = true
}

# Create a BigQuery table for feedback
resource "google_bigquery_table" "feedback" {
  dataset_id = google_bigquery_dataset.agent_analytics.dataset_id
  table_id   = "feedback"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "score",
    "type": "FLOAT",
    "mode": "REQUIRED",
    "description": "Feedback score"
  },
  {
    "name": "text",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Feedback text"
  },
  {
    "name": "invocation_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Invocation ID"
  },
  {
    "name": "log_type",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Log type"
  },
  {
    "name": "service_name",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Service name"
  },
  {
    "name": "user_id",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "User ID"
  },
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "Timestamp"
  }
]
EOF
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "aiplatform.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "logging.googleapis.com",
    "texttospeech.googleapis.com"
  ])
  
  project = var.project_id
  service = each.key
  disable_on_destroy = false
}

# Output the bucket names
output "artifacts_bucket" {
  value = google_storage_bucket.agent_artifacts.name
}

output "logs_bucket" {
  value = google_storage_bucket.agent_logs.name
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.agent_analytics.dataset_id
}