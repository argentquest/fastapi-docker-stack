# MCP Inspector Container
# Browser-based tool for testing MCP (Model Context Protocol) servers

FROM node:20-alpine

# Install system dependencies
RUN apk add --no-cache \
    git \
    curl \
    bash

WORKDIR /app

# Clone MCP Inspector repository
RUN git clone https://github.com/modelcontextprotocol/inspector.git . && \
    npm ci && \
    npm run build

# Update Vite config to allow external hosts
RUN sed -i '/server: {/,/},/c\
  server: {\
    host: true,\
    allowedHosts: ["mcp.pocmaster.argentquest.com", "localhost", "127.0.0.1", "mcp.mystack.local"],\
  },' /app/client/vite.config.ts

# Create startup script
RUN cat > /app/start.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting MCP Inspector..."
echo "Environment: ${NODE_ENV:-development}"
echo "Port: 5173"
echo "Host: 0.0.0.0"

# Change to client directory and start the development server
cd /app/client
exec npx vite --host 0.0.0.0 --port 5173
EOF

RUN chmod +x /app/start.sh

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5173 || exit 1

# Start the application
CMD ["/app/start.sh"]