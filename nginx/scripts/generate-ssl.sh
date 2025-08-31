#!/bin/bash
# SSL Certificate Generation Script for dev.local
# Generates self-signed certificates on container startup

set -e

CERT_DIR="/etc/nginx/certs"
DOMAIN="dev.local"

echo "Generating SSL certificates for $DOMAIN..."

# Create certificate directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Check if certificates already exist
if [ -f "$CERT_DIR/$DOMAIN.crt" ] && [ -f "$CERT_DIR/$DOMAIN.key" ]; then
    echo "SSL certificates already exist for $DOMAIN"
    exit 0
fi

# Generate private key
echo "Generating private key..."
openssl genrsa -out "$CERT_DIR/$DOMAIN.key" 2048

# Generate certificate signing request
echo "Generating certificate signing request..."
openssl req -new -key "$CERT_DIR/$DOMAIN.key" -out "$CERT_DIR/$DOMAIN.csr" -subj "/C=US/ST=Development/L=Docker/O=V2POC/OU=Development/CN=$DOMAIN/emailAddress=admin@$DOMAIN"

# Generate self-signed certificate with SAN extension
echo "Generating self-signed certificate..."
cat > "$CERT_DIR/$DOMAIN.conf" << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = Development
L = Docker
O = V2POC
OU = Development
CN = $DOMAIN
emailAddress = admin@$DOMAIN

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = localhost
DNS.3 = *.dev.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# Generate the certificate
openssl x509 -req -in "$CERT_DIR/$DOMAIN.csr" \
    -signkey "$CERT_DIR/$DOMAIN.key" \
    -out "$CERT_DIR/$DOMAIN.crt" \
    -days 365 \
    -extensions v3_req \
    -extfile "$CERT_DIR/$DOMAIN.conf"

# Set proper permissions
chmod 600 "$CERT_DIR/$DOMAIN.key"
chmod 644 "$CERT_DIR/$DOMAIN.crt"

# Clean up temporary files
rm -f "$CERT_DIR/$DOMAIN.csr" "$CERT_DIR/$DOMAIN.conf"

echo "SSL certificates generated successfully!"
echo "Certificate: $CERT_DIR/$DOMAIN.crt"
echo "Private Key: $CERT_DIR/$DOMAIN.key"
echo "Valid for: 365 days"
echo "Domains: $DOMAIN, localhost, *.dev.local"