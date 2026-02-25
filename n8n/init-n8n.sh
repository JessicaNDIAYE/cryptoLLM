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

# ─── Step 1: Create owner account (skip setup wizard) ──────────────
echo ""
echo "👤 Creating owner account..."
OWNER_RESULT=$(wget -qO- \
    --header="Content-Type: application/json" \
    --post-data="{\"email\":\"${N8N_DEFAULT_USER_EMAIL:-crypto.agentbuddy@gmail.com}\",\"firstName\":\"${N8N_DEFAULT_USER_FIRST_NAME:-InvestBuddy}\",\"lastName\":\"${N8N_DEFAULT_USER_LAST_NAME:-Admin}\",\"password\":\"${N8N_DEFAULT_USER_PASSWORD:-InvestBuddy2024!}\"}" \
    http://localhost:5678/rest/owner/setup 2>/dev/null || true)

if echo "$OWNER_RESULT" | grep -q '"isOwner":true'; then
    echo "   ✅ Owner account created successfully!"
    OWNER_COOKIE=$(wget -qO- -S \
        --header="Content-Type: application/json" \
        --post-data="{\"emailOrLdapLoginId\":\"${N8N_DEFAULT_USER_EMAIL:-crypto.agentbuddy@gmail.com}\",\"password\":\"${N8N_DEFAULT_USER_PASSWORD:-InvestBuddy2024!}\"}" \
        http://localhost:5678/rest/login 2>&1 | grep -i "set-cookie" | head -1 | sed 's/.*Set-Cookie: //' | cut -d';' -f1 || true)
elif echo "$OWNER_RESULT" | grep -q "already"; then
    echo "   ℹ️ Owner already exists, logging in..."
    OWNER_COOKIE=$(wget -qO- -S \
        --header="Content-Type: application/json" \
        --post-data="{\"emailOrLdapLoginId\":\"${N8N_DEFAULT_USER_EMAIL:-crypto.agentbuddy@gmail.com}\",\"password\":\"${N8N_DEFAULT_USER_PASSWORD:-InvestBuddy2024!}\"}" \
        http://localhost:5678/rest/login 2>&1 | grep -i "set-cookie" | head -1 | sed 's/.*Set-Cookie: //' | cut -d';' -f1 || true)
else
    echo "   ⚠️ Owner setup response: $OWNER_RESULT"
    # Try to login anyway (owner might already exist)
    OWNER_COOKIE=$(wget -qO- -S \
        --header="Content-Type: application/json" \
        --post-data="{\"emailOrLdapLoginId\":\"${N8N_DEFAULT_USER_EMAIL:-crypto.agentbuddy@gmail.com}\",\"password\":\"${N8N_DEFAULT_USER_PASSWORD:-InvestBuddy2024!}\"}" \
        http://localhost:5678/rest/login 2>&1 | grep -i "set-cookie" | head -1 | sed 's/.*Set-Cookie: //' | cut -d';' -f1 || true)
fi

# Helper function for authenticated API calls
n8n_api() {
    method=$1
    endpoint=$2
    data=$3
    cookie="${OWNER_COOKIE}"

    if [ -n "$data" ]; then
        wget -qO- \
            --header="Content-Type: application/json" \
            --header="Cookie: ${cookie}" \
            --post-data="$data" \
            "http://localhost:5678/api/v1$endpoint" 2>/dev/null || true
    else
        wget -qO- \
            --header="Cookie: ${cookie}" \
            "http://localhost:5678/api/v1$endpoint" 2>/dev/null || true
    fi
}

# ─── Step 2: Create OpenAI credential ──────────────────────────────
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

# ─── Step 3: Create SMTP credential ────────────────────────────────
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

# ─── Step 4: Import workflow ────────────────────────────────────────
echo ""
echo "📥 Importing InvestBuddy workflow..."

if [ -f /home/node/.n8n/workflows/working_workflow.json ]; then
    WORKFLOW=$(cat /home/node/.n8n/workflows/working_workflow.json)

    IMPORT_RESULT=$(echo "$WORKFLOW" | wget -qO- \
        --header="Content-Type: application/json" \
        --header="Cookie: ${OWNER_COOKIE}" \
        --post-data=@- \
        "http://localhost:5678/api/v1/workflows" 2>/dev/null || true)

    WORKFLOW_ID=$(echo "$IMPORT_RESULT" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -n "$WORKFLOW_ID" ]; then
        echo "   ✅ Workflow imported with ID: $WORKFLOW_ID"

        echo ""
        echo "🚀 Activating workflow..."
        wget -qO- \
            --header="Content-Type: application/json" \
            --header="Cookie: ${OWNER_COOKIE}" \
            --post-data='{"active": true}' \
            "http://localhost:5678/api/v1/workflows/$WORKFLOW_ID" 2>/dev/null || true
        echo "   ✅ Workflow activated!"
    else
        echo "   ⚠️ Could not import workflow automatically"
    fi
else
    echo "   ⚠️ Workflow file not found, skipping import"
fi

echo ""
echo "================================================"
echo "  ✅ n8n Configuration Complete!"
echo "================================================"
echo ""
echo "  📌 n8n Dashboard:  http://localhost:5678"
echo "  📌 Login email:    ${N8N_DEFAULT_USER_EMAIL:-crypto.agentbuddy@gmail.com}"
echo "  📌 Webhook URL:    http://localhost:5678/webhook/investbuddy-alert"
echo ""
echo "================================================"
