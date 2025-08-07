const express = require('express');
const cors = require('cors');
const { MCPStdioBridge } = require('./mcp-bridge');

class MCPHttpServer {
    constructor(port = 8000) {
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

        // Request logging middleware
        this.app.use((req, res, next) => {
            console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
            next();
        });
    }

    setupRoutes() {
        // Server info endpoint - for backward compatibility
        this.app.get('/info', (req, res) => {
            res.json({
                name: 'chattt-mcp-client',
                version: '1.0.0',
                description: 'MCP HTTP client bridge for ChatTTT game',
                status: 'healthy',
                mcp_server_available: this.mcpBridge.mcpProcess !== null,
                capabilities: {
                    tools: true,
                    resources: true,
                    prompts: true,
                    logging: true
                },
                protocolVersion: '2024-11-05',
                serverInfo: {
                    name: 'chattt-mcp-client',
                    version: '1.0.0'
                }
            });
        });

        // Standard MCP HTTP Transport Endpoints
        this.app.post('/mcp/initialize', (req, res) => {
            res.json({
                protocolVersion: '2024-11-05',
                capabilities: {
                    tools: true,
                    resources: true,
                    prompts: true,
                    logging: true
                },
                serverInfo: {
                    name: 'chattt-mcp-client',
                    version: '1.0.0'
                }
            });
        });

        // Tools endpoints
        this.app.get('/mcp/tools/list', async (req, res) => {
            try {
                const tools = await this.mcpBridge.listTools();
                res.json({ tools });
            } catch (error) {
                console.error('Error listing MCP tools:', error);
                res.status(500).json({
                    error: 'Internal server error',
                    detail: error.message
                });
            }
        });

        this.app.post('/mcp/tools/call', async (req, res) => {
            try {
                const { name, arguments: args } = req.body;
                
                if (!name) {
                    return res.status(400).json({
                        error: 'Bad request',
                        detail: 'Tool name is required'
                    });
                }

                const result = await this.mcpBridge.callTool(name, args || {});
                
                // Ensure the response format matches Python server
                const formattedResult = {
                    content: result.content || [{ type: 'text', text: String(result) }],
                    isError: result.isError || false
                };

                res.json(formattedResult);
            } catch (error) {
                console.error(`Error calling MCP tool ${req.body.name}:`, error);
                res.json({
                    content: [{ type: 'text', text: `Error: ${error.message}` }],
                    isError: true
                });
            }
        });

        // Resources endpoints
        this.app.get('/mcp/resources/list', async (req, res) => {
            try {
                const resources = await this.mcpBridge.listResources();
                res.json({ resources });
            } catch (error) {
                console.error('Error listing MCP resources:', error);
                res.status(500).json({
                    error: 'Internal server error',
                    detail: error.message
                });
            }
        });

        this.app.post('/mcp/resources/read', async (req, res) => {
            try {
                const { uri } = req.body;
                
                if (!uri) {
                    return res.status(400).json({
                        error: 'Bad request',
                        detail: 'Resource URI is required'
                    });
                }

                const content = await this.mcpBridge.readResource(uri);
                res.json({
                    contents: [
                        {
                            uri: uri,
                            mimeType: 'text/plain',
                            text: content
                        }
                    ]
                });
            } catch (error) {
                console.error(`Error reading MCP resource ${req.body.uri}:`, error);
                res.status(500).json({
                    error: 'Internal server error',
                    detail: error.message
                });
            }
        });

        // Prompts endpoints
        this.app.get('/mcp/prompts/list', async (req, res) => {
            try {
                const prompts = await this.mcpBridge.listPrompts();
                res.json({ prompts });
            } catch (error) {
                console.error('Error listing MCP prompts:', error);
                res.status(500).json({
                    error: 'Internal server error',
                    detail: error.message
                });
            }
        });

        this.app.post('/mcp/prompts/get', async (req, res) => {
            try {
                const { name, arguments: args } = req.body;
                
                if (!name) {
                    return res.status(400).json({
                        error: 'Bad request',
                        detail: 'Prompt name is required'
                    });
                }

                const prompt = await this.mcpBridge.getPrompt(name, args || {});
                res.json(prompt);
            } catch (error) {
                console.error(`Error getting MCP prompt ${req.body.name}:`, error);
                res.status(500).json({
                    error: 'Internal server error',
                    detail: error.message
                });
            }
        });

        // Logging endpoint
        this.app.post('/mcp/logging/setLevel', (req, res) => {
            try {
                const { level } = req.body;
                
                const validLevels = ['debug', 'info', 'warning', 'error', 'critical'];
                
                if (!level || !validLevels.includes(level.toLowerCase())) {
                    return res.status(400).json({
                        error: 'Bad request',
                        detail: `Invalid logging level: ${level}. Valid levels: ${validLevels.join(', ')}`
                    });
                }

                // In a more sophisticated implementation, you might actually change the logging level
                console.log(`Logging level set to ${level}`);
                res.json({ success: true });
            } catch (error) {
                console.error('Error setting logging level:', error);
                res.status(400).json({
                    error: 'Bad request',
                    detail: error.message
                });
            }
        });

        // Notification endpoints (stubs for completeness)
        this.app.post('/mcp/notifications/tools/list_changed', (req, res) => {
            res.json({ message: 'Tools list changed notification received' });
        });

        this.app.post('/mcp/notifications/resources/list_changed', (req, res) => {
            res.json({ message: 'Resources list changed notification received' });
        });

        this.app.post('/mcp/notifications/resources/updated', (req, res) => {
            res.json({ message: 'Resources updated notification received' });
        });

        this.app.post('/mcp/notifications/prompts/list_changed', (req, res) => {
            res.json({ message: 'Prompts list changed notification received' });
        });

        // Additional utility endpoints
        this.app.get('/mcp/ping', (req, res) => {
            res.json({
                pong: true,
                timestamp: Date.now() / 1000
            });
        });

        this.app.post('/mcp/completion', (req, res) => {
            // Stub for completion functionality
            res.json({
                completion: {
                    values: [],
                    total: 0,
                    hasMore: false
                }
            });
        });

        this.app.get('/mcp/roots/list', (req, res) => {
            // Stub for listing file system roots
            res.json({
                roots: [
                    {
                        uri: 'file:///game-data/',
                        name: 'Game Data'
                    }
                ]
            });
        });

        // Bridge-specific endpoints (from the original mcp-bridge.js)
        this.app.get('/mcp/status', (req, res) => {
            res.json({
                status: this.mcpBridge.mcpProcess ? 'connected' : 'disconnected',
                serverInfo: this.mcpBridge.serverInfo,
                capabilities: {
                    tools: this.mcpBridge.tools.length,
                    resources: this.mcpBridge.resources.length,
                    prompts: this.mcpBridge.prompts.length
                }
            });
        });

        this.app.post('/mcp/restart', async (req, res) => {
            try {
                await this.mcpBridge.restartMCP();
                res.json({ status: 'restarted' });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/mcp/all', async (req, res) => {
            try {
                const [tools, resources, prompts] = await Promise.all([
                    this.mcpBridge.listTools(),
                    this.mcpBridge.listResources(),
                    this.mcpBridge.listPrompts()
                ]);
                res.json({ tools, resources, prompts });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/mcp/capabilities', (req, res) => {
            res.json({
                tools: {
                    listTools: true,
                    callTool: true
                },
                resources: {
                    listResources: true,
                    readResource: true
                },
                prompts: {
                    listPrompts: true,
                    getPrompt: true
                }
            });
        });

        // Health check endpoint
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                mcpStatus: this.mcpBridge.mcpProcess ? 'connected' : 'disconnected'
            });
        });

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
            console.log('MCP Bridge initialized successfully');

            // Start the HTTP server
            return new Promise((resolve, reject) => {
                const server = this.app.listen(this.port, (error) => {
                    if (error) {
                        reject(error);
                    } else {
                        console.log(`MCP HTTP Server running on http://localhost:${this.port}`);
                        console.log('Available endpoints:');
                        console.log('  GET  /info - Server information');
                        console.log('  GET  /health - Health check');
                        console.log('  POST /mcp/initialize - MCP initialization');
                        console.log('  GET  /mcp/tools/list - List available tools');
                        console.log('  POST /mcp/tools/call - Call a tool');
                        console.log('  GET  /mcp/resources/list - List available resources');
                        console.log('  POST /mcp/resources/read - Read a resource');
                        console.log('  GET  /mcp/prompts/list - List available prompts');
                        console.log('  POST /mcp/prompts/get - Get a prompt');
                        console.log('  GET  /mcp/status - MCP bridge status');
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
