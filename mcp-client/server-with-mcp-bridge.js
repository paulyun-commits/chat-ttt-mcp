const express = require('express');
const cors = require('cors');
const path = require('path');
const { MCPStdioBridge } = require('./mcp-bridge');

class MCPHttpServer {
    constructor(port = 5000) {
        this.port = port;
        this.app = express();
        this.mcpBridge = new MCPStdioBridge();
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        // CORS middleware
        this.app.use(cors({
            origin: '*',
            credentials: true,
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            allowedHeaders: ['Content-Type', 'Authorization']
        }));

        // JSON parsing middleware
        this.app.use(express.json());
        this.app.use(express.urlencoded({ extended: true }));
        this.app.use(express.static(path.join(__dirname, 'public')));

        // Request logging middleware
        this.app.use((req, res, next) => {
            console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
            next();
        });
    }

    setupRoutes() {
        // Delegate core MCP endpoints (including /info) to the bridge to avoid duplication
        this.mcpBridge.setupRoutes(this.app);

        // 404 handler
        this.app.use('*', (req, res) => {
            res.status(404).json({
                error: 'Not found',
                detail: `Endpoint ${req.method} ${req.originalUrl} not found`
            });
        });

        // Error handler
        this.app.use((error, req, res, next) => {
            console.error('Unhandled error:', error);
            res.status(500).json({
                error: 'Internal server error',
                detail: error.message
            });
        });
    }

    async start() {
        try {
            // Initialize the MCP bridge
            await this.mcpBridge.initialize();

            // Start the HTTP server
            return new Promise((resolve, reject) => {
                const server = this.app.listen(this.port, (error) => {
                    if (error) {
                        reject(error);
                    } else {
                        console.log(`MCP HTTP Server running on http://localhost:${this.port}`);
                        console.log('Available endpoints:');
                        console.log('  GET  /info - Server information');
                        console.log('  GET  /mcp/status - MCP bridge status');
                        console.log('  GET  /mcp/capabilities - Server capabilities');
                        console.log('  GET  /mcp/tools - List available tools');
                        console.log('  POST /mcp/tools/call - Call a tool');
                        console.log('  GET  /mcp/resources - List available resources');
                        console.log('  POST /mcp/resources/content - Read resource content');
                        console.log('  GET  /mcp/prompts - List available prompts');
                        console.log('  POST /mcp/prompts/get - Get a prompt');
                        console.log('  GET  /mcp/ping - Ping test');
                        resolve(server);
                    }
                });

                // Handle graceful shutdown
                const shutdown = async () => {
                    console.log('Shutting down MCP HTTP Server...');
                    this.mcpBridge.stop();
                    server.close(() => {
                        console.log('HTTP Server closed');
                        process.exit(0);
                    });
                };

                process.on('SIGINT', shutdown);
                process.on('SIGTERM', shutdown);
            });
        } catch (error) {
            console.error('Failed to start MCP HTTP Server:', error);
            throw error;
        }
    }
}

// If this file is run directly, start the server
if (require.main === module) {
    const port = process.env.PORT || 8000;
    const server = new MCPHttpServer(port);
    
    server.start().catch(error => {
        console.error('Failed to start server:', error);
        process.exit(1);
    });
}

module.exports = { MCPHttpServer };
