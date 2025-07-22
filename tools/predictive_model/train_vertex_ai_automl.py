import os
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aiplatform_gapic

# === CONFIGURATION ===
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_REGION", "us-central1")
BUCKET_NAME = os.getenv("VERTEX_AI_BUCKET")  # GCS bucket for data
CSV_FILE = "travel_features.csv"  # Local CSV file
GCS_PATH = f"gs://{BUCKET_NAME}/vertex-ai/travel_features.csv"
DATASET_DISPLAY_NAME = "travel_time_dataset"
MODEL_DISPLAY_NAME = "travel_time_predictor"
TARGET_COLUMN = "travel_time_minutes"

# === UPLOAD CSV TO GCS ===
from google.cloud import storage
storage_client = storage.Client()
blob = storage_client.bucket(BUCKET_NAME).blob("vertex-ai/travel_features.csv")
blob.upload_from_filename(CSV_FILE)
print(f"Uploaded {CSV_FILE} to {GCS_PATH}")

# === CREATE DATASET ===
aiplatform.init(project=PROJECT_ID, location=LOCATION, staging_bucket=BUCKET_NAME)
dataset = aiplatform.TabularDataset.create(display_name=DATASET_DISPLAY_NAME, gcs_source=GCS_PATH)
dataset.wait()
print(f"Created dataset: {dataset.resource_name}")

# === TRAIN MODEL ===
model = aiplatform.AutoMLTabularTrainingJob(
    display_name=MODEL_DISPLAY_NAME,
    optimization_prediction_type="regression",
    optimization_objective="minimize-rmse",
)

model_run = model.run(
    dataset=dataset,
    target_column=TARGET_COLUMN,
    input_data_config={"input_data_schema": None},
    model_display_name=MODEL_DISPLAY_NAME,
    budget_milli_node_hours=1000,
    disable_early_stopping=False,
)
print(f"Training job started. Model: {model_run.resource_name}") 