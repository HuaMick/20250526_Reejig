#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Source environment variables
if [ -f "$(dirname "$0")/../env/env.env" ]; then
    source "$(dirname "$0")/../env/env.env"
else
    echo "Error: env/env.env not found."
    exit 1
fi

# Check if GCP_PROJECT is set
if [ -z "$GCP_PROJECT" ]; then
    echo "Error: GCP_PROJECT is not set in env/env.env."
    exit 1
fi

# Check if POSTGRESQL_USER is set
if [ -z "$POSTGRESQL_USER" ]; then
    echo "Error: POSTGRESQL_USER is not set in env/env.env."
    exit 1
fi

# Check if POSTGRESQL_PASSWORD is set
if [ -z "$POSTGRESQL_PASSWORD" ]; then
    echo "Error: POSTGRESQL_PASSWORD is not set in env/env.env."
    exit 1
fi

# Variables (customize as needed)
INSTANCE_NAME="postgres-instance-1"
REGION="us-central1"
DB_VERSION="POSTGRES_15" # Check gcloud sql db versions list for available versions
TIER="db-f1-micro" # Example: db-custom-1-3840 for 1 vCPU, 3.75GB RAM. Choose appropriate tier.
STORAGE_SIZE="10GB"
DATABASE_NAME="postgres-db"
DB_USER_NAME="$POSTGRESQL_USER" # Use the variable from env/env.env
NETWORK_NAME="default" # Using default VPC for the instance location

echo "Starting GCP PostgreSQL Initialization for project: $GCP_PROJECT"

# 0. Set the project
gcloud config set project "$GCP_PROJECT"

# 1. Enable APIs
echo "Enabling necessary GCP APIs..."
gcloud services enable servicenetworking.googleapis.com \
    sqladmin.googleapis.com \
    compute.googleapis.com

# Variables for network configuration (even for public IP, peering is needed for provisioning)
ALLOCATED_IP_RANGE_NAME="google-managed-services-${NETWORK_NAME}"

# 2. Create a global IP address range for service networking
echo "Checking/Creating IP address range for service networking..."
gcloud compute addresses describe "${ALLOCATED_IP_RANGE_NAME}" --global --project="${GCP_PROJECT}" > /dev/null 2>&1 || \
    gcloud compute addresses create "${ALLOCATED_IP_RANGE_NAME}" \
        --global \
        --purpose=VPC_PEERING \
        --prefix-length=16 \
        --network="projects/${GCP_PROJECT}/global/networks/${NETWORK_NAME}" \
        --project="${GCP_PROJECT}"

# 3. Establish VPC peering for service networking
echo "Checking/Creating VPC peering connection..."
# List peerings and grep for the specific one. 
# The output of list can be complex, so we are looking for the exact name.
EXISTING_PEERING=$(gcloud services vpc-peerings list --network="${NETWORK_NAME}" --project="${GCP_PROJECT}" --format="value(peering)" | grep -w "servicenetworking-googleapis-com" || true)

if [ -z "$EXISTING_PEERING" ]; then
    echo "Peering 'servicenetworking-googleapis-com' not found. Creating..."
    gcloud services vpc-peerings connect \
        --service=servicenetworking.googleapis.com \
        --ranges="${ALLOCATED_IP_RANGE_NAME}" \
        --network="${NETWORK_NAME}" \
        --project="${GCP_PROJECT}"
elif [ "$EXISTING_PEERING" == "servicenetworking-googleapis-com" ]; then
    echo "VPC peering 'servicenetworking-googleapis-com' already exists and is correct."
else
    # This case should ideally not be reached if grep works as expected, 
    # but as a fallback if grep somehow returns a partial but not exact match that isn't empty.
    echo "An unexpected peering state detected: '$EXISTING_PEERING'. Manual check might be required."
    echo "Attempting to ensure peering is correctly configured with an update..."
    gcloud services vpc-peerings update \
        --service=servicenetworking.googleapis.com \
        --ranges="${ALLOCATED_IP_RANGE_NAME}" \
        --network="${NETWORK_NAME}" \
        --project="${GCP_PROJECT}" \
        --force
fi

# 4. Create Cloud SQL PostgreSQL instance
echo "Checking/Creating Cloud SQL PostgreSQL instance: ${INSTANCE_NAME}..."
gcloud sql instances describe "${INSTANCE_NAME}" --project="${GCP_PROJECT}" > /dev/null 2>&1 || \
    gcloud sql instances create "${INSTANCE_NAME}" \
        --database-version="${DB_VERSION}" \
        --tier="${TIER}" \
        --region="${REGION}" \
        --storage-size="${STORAGE_SIZE}" \
        --network="projects/${GCP_PROJECT}/global/networks/${NETWORK_NAME}" \
        --assign-ip

echo "Cloud SQL instance ${INSTANCE_NAME} should be provisioning. Waiting for it to be RUNNABLE..."
# Wait for instance to be runnable (optional, can take a while)
# while true; do
#    STATUS=$(gcloud sql instances describe "${INSTANCE_NAME}" --project="${GCP_PROJECT}" --format='value(state)')
#    if [ "$STATUS" = "RUNNABLE" ]; then
#        echo "Instance ${INSTANCE_NAME} is RUNNABLE."
#        break
#    fi
#    echo "Instance status: $STATUS. Waiting..."
#    sleep 30
# done

# 5. Create a database within the instance
echo "Checking/Creating database '${DATABASE_NAME}' in instance '${INSTANCE_NAME}'..."
gcloud sql databases describe "${DATABASE_NAME}" --instance="${INSTANCE_NAME}" --project="${GCP_PROJECT}" > /dev/null 2>&1 || \
    gcloud sql databases create "${DATABASE_NAME}" \
        --instance="${INSTANCE_NAME}" --project="${GCP_PROJECT}"

# 6. Create a user for the database
# Note: This uses environment variables for password.
echo "Checking/Creating user '${DB_USER_NAME}' for instance '${INSTANCE_NAME}'..."
gcloud sql users describe "${DB_USER_NAME}" --instance="${INSTANCE_NAME}" --project="${GCP_PROJECT}" > /dev/null 2>&1 || \
    gcloud sql users create "${DB_USER_NAME}" \
        --instance="${INSTANCE_NAME}" \
        --project="${GCP_PROJECT}" \
        --password="$POSTGRESQL_PASSWORD"

echo "PostgreSQL instance '${INSTANCE_NAME}', database '${DATABASE_NAME}', and user '${DB_USER_NAME}' setup process initiated."
echo "The instance will have a public IP. Please check the GCP console for the status and public IP address."
echo "IMPORTANT: You MUST configure firewall rules for your instance to allow connections."
echo "Example to allow your current IP: gcloud sql instances patch ${INSTANCE_NAME} --authorized-networks=$(curl -s ifconfig.me)/32"
echo "Or for allowing all (NOT RECOMMENDED FOR PRODUCTION): gcloud sql instances patch ${INSTANCE_NAME} --authorized-networks=0.0.0.0/0"
