const { spawn } = require('child_process');
const path = require('path');

class MCPStdioBridge {
    constructor() {
        this.mcpProcess = null;
        this.requestId = 1;
        this.pendingRequests = new Map();
        this.serverInfo = null;
        this.tools = [];
        this.resources = [];
        this.prompts = [];
    }

    setupRoutes(app) {
        // Server info endpoint - for backward compatibility and health checks
        app.get('/info', (req, res) => {
            res.json({
                name: 'chattt-mcp-client',
                version: '1.0.0',
                description: 'MCP HTTP client bridge for ChatTTT game',
                status: 'healthy',
                mcp_server_available: this.mcpProcess !== null,
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

        // Restart MCP connection
        app.post('/mcp/restart', async (req, res) => {
            try {
                await this.restartMCP();
                res.json({ status: 'restarted' });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // List tools
        app.get('/mcp/tools/list', async (req, res) => {
            try {
                const tools = await this.listTools();
                res.json({ tools });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Call tool
        app.post('/mcp/tools/call', async (req, res) => {
            try {
                const { name, arguments: args } = req.body;
                
                if (!name) {
                    return res.status(400).json({ error: 'Tool name is required' });
                }
                
                const result = await this.callTool(name, args || {});
                res.json(result);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // List resources
        app.get('/mcp/resources/list', async (req, res) => {
            try {
                const resources = await this.listResources();
                res.json({ resources });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Get resource content
        app.post('/mcp/resources/read', async (req, res) => {
            try {
                const { uri } = req.body;
                
                if (!uri) {
                    return res.status(400).json({ error: 'Resource URI is required' });
                }
                
                const content = await this.readResource(uri);
                res.json({ content });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // List prompts
        app.get('/mcp/prompts/list', async (req, res) => {
            try {
                const prompts = await this.listPrompts();
                res.json({ prompts });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Get prompt content
        app.post('/mcp/prompts/get', async (req, res) => {
            try {
                const { name, arguments: args } = req.body;
                
                if (!name) {
                    return res.status(400).json({ error: 'Prompt name is required' });
                }
                
                const prompt = await this.getPrompt(name, args || {});
                res.json(prompt);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Get server capabilities
        app.get('/mcp/capabilities', (req, res) => {
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
    }

    async startMCP() {
        if (this.mcpProcess) {
            console.log('MCP process already running');
            return;
        }

        return new Promise((resolve, reject) => {
            console.log('Starting MCP server process...');
            
            const serverPath = path.join(__dirname, '..', 'mcp-server', 'server.py');
            const pythonPath = path.join(__dirname, '..', 'mcp-server', 'venv', 'bin', 'python');
            
            // Use virtual environment python
            const pythonCmd = require('fs').existsSync(pythonPath) ? pythonPath : 'python3';
            
            this.mcpProcess = spawn(pythonCmd, [serverPath], {
                stdio: ['pipe', 'pipe', 'pipe'],
                cwd: path.join(__dirname, '..', 'mcp-server')
            });

            let initBuffer = '';
            let initialized = false;

            this.mcpProcess.stdout.on('data', (data) => {
                const chunk = data.toString();
                if (!initialized) {
                    initBuffer += chunk;
                    // Look for the server info log message OR a JSON-RPC response
                    if (initBuffer.includes('Starting chattt-ai') || chunk.includes('{"jsonrpc"')) {
                        initialized = true;
                        console.log('MCP server initialized');
                        // Use async/await to ensure errors propagate
                        (async () => {
                            try {
                                await this.initializeMCP();
                                resolve();
                            }
                            catch (err) {
                                reject(err);
                            }
                        })();
                    }
                }
                else {
                    this.handleMCPMessage(chunk);
                }
            });

            this.mcpProcess.stderr.on('data', (data) => {
                const errorOutput = data.toString();
                console.error('MCP stderr:', errorOutput);
                
                // Check if this is the startup message (not an error)
                if (!initialized && errorOutput.includes('Starting chattt-ai')) {
                    console.log('MCP server startup detected from stderr');
                    initialized = true;
                    // Use async/await to ensure errors propagate
                    (async () => {
                        try {
                            await this.initializeMCP();
                            resolve();
                        }
                        catch (err) {
                            reject(err);
                        }
                    })();
                }
            });

            this.mcpProcess.on('close', (code) => {
                console.log(`MCP process exited with code ${code}`);
                this.mcpProcess = null;
                this.pendingRequests.clear();
                this.tools = [];
                this.resources = [];
                this.prompts = [];
            });

            this.mcpProcess.on('error', (error) => {
                console.error('MCP process error:', error);
                this.mcpProcess = null;
                reject(error);
            });

            // Timeout for initialization
            setTimeout(() => {
                if (!initialized) {
                    reject(new Error('MCP server initialization timeout'));
                }
            }, 30000);
        });
    }

    async initializeMCP() {
        try {
            // Wait a bit for the server to be ready
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Initialize the MCP session
            const initResult = await this.sendMCPRequest('initialize', {
                protocolVersion: '2024-11-05',
                capabilities: {
                    tools: {},
                    resources: {},
                    prompts: {}
                },
                clientInfo: {
                    name: 'ChatTTT-Bridge',
                    version: '1.0.0'
                }
            });
            this.serverInfo = initResult;

            // Send initialized notification (no response expected)
            await this.sendMCPNotification('notifications/initialized', {});

            // Wait longer after initialization to ensure server is ready
            await new Promise(resolve => setTimeout(resolve, 3000));

            // Get server capabilities
            await this.listTools();
            await this.listResources();
            await this.listPrompts();
            
            console.log(`MCP session initialized successfully with ${this.tools.length} tools, ${this.resources.length} resources, and ${this.prompts.length} prompts`);
        } catch (error) {
            console.error('Failed to initialize MCP session:', error);
            throw error;
        }
    }

    handleMCPMessage(data) {
        const lines = data.split('\n').filter(line => line.trim());
        
        for (const line of lines) {
            try {
                const message = JSON.parse(line);
                
                // Handle responses to requests
                if (message.id !== undefined && this.pendingRequests.has(message.id)) {
                    const { resolve, reject } = this.pendingRequests.get(message.id);
                    this.pendingRequests.delete(message.id);
                    
                    if (message.error) {
                        reject(new Error(message.error.message || JSON.stringify(message.error)));
                    } else {
                        resolve(message.result);
                    }
                }
                // Handle notifications or other messages (like progress updates)
                else if (message.method) {
                    console.log('Received MCP notification:', message.method, message.params);
                }
                // Handle other messages without ID (e.g., server-initiated messages)
                else {
                    console.log('Received MCP message without ID:', message);
                }
            } catch (error) {
                console.error('Failed to parse MCP message:', error, 'Data:', line);
            }
        }
    }

    sendMCPRequest(method, params) {
        return new Promise((resolve, reject) => {
            if (!this.mcpProcess) {
                reject(new Error('MCP process not running'));
                return;
            }

            const id = this.requestId++;
            const request = { jsonrpc: '2.0', id, method, params };
                
            const message = JSON.stringify(request) + '\n';
            this.mcpProcess.stdin.write(message);

            // Store the pending request for response handling
            this.pendingRequests.set(id, { resolve, reject });

            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id);
                    reject(new Error(`Request timeout: ${method}`));
                }
            }, 5000);
        });
    }

    sendMCPNotification(method, params) {
        if (!this.mcpProcess) {
            throw new Error('MCP process not running');
        }

        const notification = { jsonrpc: '2.0', method, params };
        const message = JSON.stringify(notification) + '\n';
        this.mcpProcess.stdin.write(message);
    }

    async listTools() {
        try {
            const result = await this.sendMCPRequest('tools/list', {});
            this.tools = result.tools || [];
            return this.tools;
        }
        catch (error) {
            console.error('Failed to list tools:', error);
            return [];
        }
    }

    async callTool(name, args) {
        try {
            const result = await this.sendMCPRequest('tools/call', {
                name,
                arguments: args
            });
            return result;
        }
        catch (error) {
            console.error(`Failed to call tool ${name}:`, error);
            throw error;
        }
    }

    async listResources() {
        try {
            const result = await this.sendMCPRequest('resources/list', {});
            this.resources = result.resources || [];
            return this.resources;
        } catch (error) {
            console.error('Failed to list resources:', error);
            return [];
        }
    }

    async readResource(uri) {
        try {
            const result = await this.sendMCPRequest('resources/read', { uri });
            if (result.contents && result.contents.length > 0) {
                return result.contents[0].text;
            }
            return '';
        } catch (error) {
            console.error(`Failed to read resource ${uri}:`, error);
            throw error;
        }
    }

    async listPrompts() {
        try {
            const result = await this.sendMCPRequest('prompts/list', {});
            this.prompts = result.prompts || [];
            return this.prompts;
        } catch (error) {
            console.error('Failed to list prompts:', error);
            return [];
        }
    }

    async getPrompt(name, args = {}) {
        try {
            const result = await this.sendMCPRequest('prompts/get', {
                name,
                arguments: args
            });
            return result;
        } catch (error) {
            console.error(`Failed to get prompt ${name}:`, error);
            throw error;
        }
    }

    async restartMCP() {
        console.log('Restarting MCP connection...');
        
        if (this.mcpProcess) {
            this.mcpProcess.kill();
            this.mcpProcess = null;
        }

        this.pendingRequests.clear();
        this.tools = [];
        this.resources = [];
        this.prompts = [];
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait a bit
        await this.startMCP();
    }

    async initialize() {
        try {
            await this.startMCP();
            console.log('MCP Bridge initialized successfully');
        }
        catch (error) {
            console.error('Failed to initialize MCP bridge:', error);
            throw error;
        }
    }

    stop() {
        if (this.mcpProcess) {
            this.mcpProcess.kill();
            this.mcpProcess = null;
        }
    }
}

// Factory function to create and setup MCP routes
function setupMCPRoutes(app) {
    const bridge = new MCPStdioBridge();
    bridge.setupRoutes(app);
    
    // Initialize the MCP connection with retry logic
    const initializeWithRetry = async (retries = 3) => {
        for (let i = 0; i < retries; i++) {
            try {
                await bridge.initialize();
                return;
            } catch (error) {
                console.error(`Failed to initialize MCP bridge (attempt ${i + 1}/${retries}):`, error.message);
                if (i < retries - 1) {
                    console.log('Retrying in 2 seconds...');
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
        }
        console.error('Failed to initialize MCP bridge after all retries');
    };

    initializeWithRetry();

    // Handle graceful shutdown
    const shutdown = () => {
        console.log('Shutting down MCP bridge...');
        bridge.stop();
    };

    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);

    return bridge;
}

module.exports = { MCPStdioBridge, setupMCPRoutes };
