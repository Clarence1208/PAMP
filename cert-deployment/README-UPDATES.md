# PAMP Certificate Deployment - Updates

## Changes Made to Avoid Resource Conflicts

The certificate deployment has been modified to work with existing deployments without causing conflicts. The following changes were made:

1. **Disabled ingress patching**: 
   - We've emptied the `ingressPatches` list in `values.yaml` to prevent the chart from trying to modify existing Ingress resources.

2. **Created a consolidated template**:
   - Added `certificate-only.yaml` to handle all certificate-related resources in one place.
   - This template includes the Certificate Issuer, Certificates, and a specific IngressRoute for ACME challenges.

3. **ACME challenge handling**:
   - Created a dedicated service and IngressRoute specifically for handling ACME HTTP-01 challenges.
   - This ensures Let's Encrypt can validate domain ownership without modifying existing Ingress resources.

## How to Use with Existing Deployments

After deploying this chart, the TLS certificates will be generated but not automatically applied to existing services. To use the certificates:

1. **Update your frontend deployment**:
   ```yaml
   # In front-deployment/values.yaml
   ingress:
     tls:
       - secretName: edulor-tls-cert
         hosts:
           - edulor.fr
           - www.edulor.fr
   ```

2. **Update your auth service deployment**:
   ```yaml
   # In auth-deployment/values.yaml 
   ingress:
     tls:
       - secretName: edulor-tls-cert
         hosts:
           - edulor.fr
           - www.edulor.fr
   ```

3. **Apply the updates**:
   ```bash
   helm upgrade pamp-frontend ./front-deployment
   helm upgrade pamp-auth ./auth-deployment
   ```

## Advantages of This Approach

- **Clean separation of concerns**: Certificate management is handled separately from application deployment.
- **No ownership conflicts**: Avoids Helm ownership conflicts with existing resources.
- **Reusable certificates**: The same certificate can be used by multiple services.
- **Centralized certificate management**: All certificate configuration is in one place. 