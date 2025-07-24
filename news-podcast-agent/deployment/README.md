# Deployment Guide

This directory contains the infrastructure and deployment scripts for the news-podcast-agent.

## Prerequisites

Before deploying, ensure you have:

1. **Google Cloud SDK** installed and configured
2. **Terraform** installed
3. **uv** Python package manager installed
4. Appropriate permissions on your Google Cloud project

## Setting Up Development Environment

To set up a development environment:

```bash
make setup-dev-env
```

This will create the necessary Google Cloud resources using Terraform.

## Deploying to Agent Engine

To deploy the agent to Vertex AI Agent Engine:

```bash
make backend
```

This will package and deploy the agent to your Google Cloud project.

## Infrastructure Components

The deployment creates the following resources:

- **Agent Engine**: Hosts the agent on Vertex AI
- **Cloud Storage Buckets**: For agent artifacts and logs
- **BigQuery Dataset**: For analytics and monitoring
- **Cloud Logging**: For observability

## CI/CD Setup

For a streamlined CI/CD pipeline setup, you can use the `agent-starter-pack` CLI command:

```bash
uvx agent-starter-pack setup-cicd
```

This will set up GitHub Actions workflows for continuous integration and deployment.

## Manual Deployment

If you prefer to deploy manually, follow these steps:

1. Set your Google Cloud project:
   ```bash
   gcloud config set project <your-project-id>
   ```

2. Deploy the agent:
   ```bash
   python -m app.agent_engine_app
   ```

3. Check the deployment status:
   ```bash
   gcloud ai agents list
   ```

## Monitoring

After deployment, you can monitor your agent using:

- **Cloud Logging**: For detailed logs
- **Cloud Trace**: For request tracing
- **Looker Studio**: For visualizing analytics

Refer to the main README.md for the Looker Studio dashboard link.