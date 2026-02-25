#!/bin/sh
set -e

echo "================================================"
echo "  InvestBuddy n8n Auto-Configuration Script"
echo "================================================"

# Wait for n8n to be ready
echo "⏳ Waiting for n8n to start..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if wget --no-verbose --tries=1 --spider http://localhost:5678/healthz 2>/dev/null; then
        echo "✅ n8n is ready!"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "   Attempt $retry_count/$max_retries..."
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ n8n failed to start within timeout"
    exit 1
fi

# Give n8n a moment to fully initialize
sleep 5

# Function to make API calls to n8n
n8n_api() {
    method=$1
    endpoint=$2
    data=$3
    
    if [ -n "$data" ]; then
        wget --no-check-certificate -qO- \
            --method=$method \
            --header='Content-Type: application/json' \
            --body-data="$data" \
            "http://localhost:5678/api/v1$endpoint" 2>/dev/null || true
    else
        wget --no-check-certificate -qO- \
            --method=$method \
            "http://localhost:5678/api/v1$endpoint" 2>/dev/null || true
    fi
}

# Create OpenAI credential
echo ""
echo "🔑 Creating OpenAI credential..."
OPENAI_CRED=$(cat <<EOF
{
    "name": "OpenAi account",
    "type": "openAiApi",
    "data": {
        "apiKey": "${OPENAI_API_KEY}"
    }
}
EOF
)

n8n_api POST "/credentials" "$OPENAI_CRED"
echo "   ✅ OpenAI credential created"

# Create SMTP credential
echo ""
echo "🔑 Creating SMTP credential..."
SMTP_CRED=$(cat <<EOF
{
    "name": "SMTP account",
    "type": "smtp",
    "data": {
        "host": "${SMTP_HOST}",
        "port": ${SMTP_PORT:-587},
        "user": "${SMTP_USERNAME}",
        "password": "${SMTP_PASSWORD}",
        "secure": true
    }
}
EOF
)

n8n_api POST "/credentials" "$SMTP_CRED"
echo "   ✅ SMTP credential created"

# Import the workflow
echo ""
echo "📥 Importing InvestBuddy workflow..."

# Read and modify workflow to remove hardcoded credential IDs
WORKFLOW=$(cat /home/node/.n8n/workflows/working_workflow.json | \
    sed 's/"id": "IoDyMXP9gjxzNJwL"//g' | \
    sed 's/"id": "w7cTdqwiZVCZeA9S"//g')

# Import workflow
IMPORT_RESULT=$(echo "$WORKFLOW" | wget --no-check-certificate -qO- \
    --method=POST \
    --header='Content-Type: application/json' \
    --body-data=@- \
    "http://localhost:5678/api/v1/workflows" 2>/dev/null || true)

# Extract workflow ID
WORKFLOW_ID=$(echo "$IMPORT_RESULT" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$WORKFLOW_ID" ]; then
    echo "   ✅ Workflow imported with ID: $WORKFLOW_ID"
    
    # Activate the workflow
    echo ""
    echo "🚀 Activating workflow..."
    n8n_api PATCH "/workflows/$WORKFLOW_ID" '{"active": true}'
    echo "   ✅ Workflow activated!"
else
    echo "   ⚠️ Could not import workflow automatically"
    echo "   Please import manually: http://localhost:5678"
fi

echo ""
echo "================================================"
echo "  ✅ n8n Configuration Complete!"
echo "================================================"
echo ""
echo "  📌 n8n Dashboard: http://localhost:5678"
echo "  📌 Webhook URL: http://localhost:5678/webhook/investbuddy-alert"
echo ""
echo "================================================"