#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Apply admin user and role binding
kubectl apply -f "$SCRIPT_DIR/dashboard-admin.yaml"

# Apply token configuration
kubectl apply -f "$SCRIPT_DIR/dashboard-token.yaml"

# Apply NodePort service
kubectl apply -f "$SCRIPT_DIR/dashboard-nodeport.yaml"

# Wait for resources to be created
echo "Waiting for resources to be created..."
sleep 5

# Get the token
echo "Your admin token is:"
kubectl -n kubernetes-dashboard describe secret admin-user-token | grep -E '^token' | awk '{print $2}'

echo ""
echo "Access the dashboard at: https://<your-node-ip>:30443"
echo "You can also use port-forwarding: kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443"
echo "Then access: https://localhost:8443" 