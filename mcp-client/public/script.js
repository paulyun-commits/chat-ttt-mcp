const CONFIG = {
    server: {
        mcpServerUrl: 'http://localhost:8000',
        ollamaHost: 'http://localhost:11434',
        ollamaModel: 'llama3.2:latest'
    },
    
    ollama: {
        high_temperature: 0.9,   // Lower for more consistent tool selection and game logic
        med_temperature: 0.5,    // Lower for more consistent tool selection and game logic
        low_temperature: 0.1,    // Lower for more consistent tool selection and game logic
        temperature: 0.2,        // Lower for more consistent tool selection and game logic
        maxTokens: 2048,         // Reduced from 4096 - sufficient for most responses, faster generation
        timeout: 20000,          // Increased from 15000 - allows for complex reasoning
        top_p: 0.9,              // Nucleus sampling for response diversity
        repeat_penalty: 1.15,    // Reduces repetitive phrases in chat
        presence_penalty: 0.6,   // Encourages topic variety
        frequency_penalty: 0.3,  // Mild penalty for overused tokens
        stop: ["Human:", "User:", "Assistant:"], // Stop sequences to prevent role confusion
        num_ctx: 4096,           // Context window size for conversation memory
        num_predict: 512,        // Max tokens to predict per request (overridden by maxTokens)
        seed: -1,                // Random seed for variety (-1 = random)
        mirostat: 0,             // Use standard sampling (0 = off, 1 = Mirostat v1, 2 = Mirostat v2)
        mirostat_tau: 5.0,       // Target entropy for Mirostat (if enabled)
        mirostat_eta: 0.1        // Learning rate for Mirostat (if enabled)
    },
    
    mcp: {
        timeout: 10000,
        statusCheckInterval: 300000, // 5 minutes instead of 30 seconds
        autoRefreshResources: true
    },
    
    chat: {
        maxHistoryMessages: 100
    },
    
    game: {
        aiAutoPlay: true
    },
    
    ui: {
        // TODO: Add UI settings if needed
    }
};

const PLAYERS = {
    HUMAN: 'X',
    AI: 'O'
};

const GAME_MESSAGES = {
    WELCOME: "Welcome to ChatTTT! Click a cell or tell me where to play.",
    GAME_OVER_NEW: "Game over! New game?",
    POSITION_TAKEN: (pos) => `Position ${pos} taken!`,
    INVALID_POSITION: "Pick 1-9.",
    GAME_OVER_START_NEW: "Game over! Play again?",
    NEW_GAME_STARTED: 'New game! Your turn (X)',
    CANT_PROCESS_MESSAGE: "Try asking differently?",
    THINKING: "🤔 Thinking...",
    GETTING_RANDOM_MOVE: 'Finding move...',
    THINKING_BEST_MOVE: 'Analyzing...',
    PLAYING_MOVE: 'Playing move...'
};

let appConfig = {
    mcpServerUrl: CONFIG.server.mcpServerUrl,
    ollamaHost: CONFIG.server.ollamaHost,
    ollamaModel: CONFIG.server.ollamaModel
};

let gameState = {
    board: Array(9).fill(),
    player: PLAYERS.HUMAN,
    gameOver: false,
    winner: null,
    gameId: Date.now()
};

let chatHistory = [];
let gameBoard, gameStatus, mcpStatus, mcpStatusText, ollamaStatus, ollamaStatusText;
let chatMessages, chatInput, sendBtn, toolsList, resourcesList, modelSelect, refreshModelsBtn;
let mcpServerInput, updateMcpBtn, ollamaServerInput, updateOllamaBtn, aiAutoplayToggle;
let servicesHeader, servicesToggle, servicesContent;
let toolsHeader, resourcesHeader;
let availableModels = [];
let isLoadingModels = false;

document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
    loadConfiguration();
    checkMCPStatus(); // This will load both capabilities and resources
    checkOllamaStatus();
    resetGame();
});

// Initialization/Configuration

function initializeElements() {
    gameBoard = document.getElementById('gameBoard');
    gameStatus = document.getElementById('gameStatus');
    mcpStatus = document.getElementById('mcpStatus');
    mcpStatusText = document.getElementById('mcpStatusText');
    ollamaStatus = document.getElementById('ollamaStatus');
    ollamaStatusText = document.getElementById('ollamaStatusText');
    chatMessages = document.getElementById('chatMessages');
    chatInput = document.getElementById('chatInput');
    sendBtn = document.getElementById('sendBtn');
    toolsList = document.getElementById('toolsList');
    resourcesList = document.getElementById('resourcesList');
    modelSelect = document.getElementById('modelSelect');
    refreshModelsBtn = document.getElementById('refreshModelsBtn');
    mcpServerInput = document.getElementById('mcpServerInput');
    updateMcpBtn = document.getElementById('updateMcpBtn');
    ollamaServerInput = document.getElementById('ollamaServerInput');
    updateOllamaBtn = document.getElementById('updateOllamaBtn');
    aiAutoplayToggle = document.getElementById('aiAutoplayToggle');
    servicesHeader = document.getElementById('servicesHeader');
    servicesToggle = document.getElementById('servicesToggle');
    servicesContent = document.getElementById('servicesContent');
    toolsHeader = document.getElementById('toolsHeader');
    resourcesHeader = document.getElementById('resourcesHeader');
}

async function loadConfiguration() {
    console.log('Using default configuration:');
    console.log(appConfig);
    
    aiAutoplayToggle.checked = CONFIG.game.aiAutoPlay;
    ollamaServerInput.value = appConfig.ollamaHost;
    mcpServerInput.value = appConfig.mcpServerUrl;
    await loadAvailableModels();
}

function setupEventListeners() {
    window.addEventListener('online', function() {
        updateGameStatus('🟢 Internet connection restored');
        checkMCPStatus();
        checkOllamaStatus();
    });

    window.addEventListener('offline', function() {
        updateGameStatus('🔴 Internet connection lost');
    });

    gameBoard.addEventListener('click', (e) => {
        if (!e.target.classList.contains('cell')) return;
        
        const position = parseInt(e.target.dataset.position);
        if (position >= 1 && position <= 9 && !gameState.gameOver) {
            addUserMessage(position.toString());
            processChatInput(position.toString());
        }
    });

    aiAutoplayToggle.addEventListener('change', () => {
        CONFIG.game.aiAutoPlay = aiAutoplayToggle.checked;
        
        const status = CONFIG.game.aiAutoPlay ? 'enabled' : 'disabled';
        addGameMessage(`🤖 AI Auto-Play ${status}`);
        
        // If we just enabled auto-play and it's AI's turn, make a move
        if (CONFIG.game.aiAutoPlay && gameState.player === PLAYERS.AI && !gameState.gameOver) {
            requestAIMove();
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleChatSubmit();
        }
    });
    sendBtn.addEventListener('click', handleChatSubmit);

    ollamaServerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleOllamaServerUpdate();
        }
    });
    updateOllamaBtn.addEventListener('click', handleOllamaServerUpdate);

    modelSelect.addEventListener('change', () => {
        const selectedModel = modelSelect.value;
        
        if (selectedModel && selectedModel !== appConfig.ollamaModel) {
            appConfig.ollamaModel = selectedModel;
            updateOllamaStatus('connected', { model: selectedModel });
            addGameMessage(`🤖 Switched to model: ${selectedModel}`);
            console.log('Model changed to:', selectedModel);
        }
    });
    refreshModelsBtn.addEventListener('click', async () => {
        addGameMessage('🔄 Refreshing available models...');
        await loadAvailableModels();
        
        if (availableModels.length > 0) {
            addGameMessage(`✅ Found ${availableModels.length} available models`);
        } else {
            addGameMessage('❌ No models found or failed to connect to Ollama');
        }
    });

    mcpServerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleMcpServerUpdate();
        }
    });
    updateMcpBtn.addEventListener('click', handleMcpServerUpdate);

    servicesHeader.addEventListener('click', toggleServicesPanel);
    
    servicesToggle.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent servicesHeader click
        toggleServicesPanel();
    });
    
    // Add escape key listener for fullscreen mode
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const servicesPanel = servicesContent.closest('.services-panel');
            if (servicesPanel.classList.contains('fullscreen')) {
                // Exit fullscreen by going to collapsed state
                servicesPanel.classList.remove('fullscreen');
                servicesPanel.classList.add('collapsed');
                servicesToggle.querySelector('.toggle-icon').textContent = '▼';
                servicesToggle.setAttribute('title', 'Show Services Settings');
            }
        }
    });
    
    window.setInterval(async () => {
        await checkOllamaStatus();
        await checkMCPStatus();
    }, CONFIG.mcp.statusCheckInterval);

    restoreServicesPanelState();
}

// Ollama

async function aiChooseTool(message) {
    try {
        // Fetch all MCP data in parallel with a single /info call
        const [infoResponse, toolsResponse, resourcesResponse] = await Promise.all([
            fetch(`${appConfig.mcpServerUrl}/info`),
            fetch(`${appConfig.mcpServerUrl}/mcp/tools/list`),
            fetch(`${appConfig.mcpServerUrl}/mcp/resources/list`)
        ]);
        
        if (!infoResponse.ok || !toolsResponse.ok || !resourcesResponse.ok) {
            throw new Error(`HTTP ${infoResponse.status || toolsResponse.status || resourcesResponse.status}`);
        }

        const [infoData, toolsData, resourcesData] = await Promise.all([
            infoResponse.json(),
            toolsResponse.json(),
            resourcesResponse.json()
        ]);

        const mcpTools = {
            status: 'connected',
            serverInfo: infoData,
            tools: toolsData.tools || []
        };

        const mcpResources = {
            status: 'connected',
            serverInfo: infoData,
            resources: resourcesData.resources || []
        };
        
        // Get relevant resource content for tool selection context
        const relevantResources = await getRelevantResourceContent(message, mcpResources.resources);
        
        const prompt = `
- You are a smart assistant for a tic-tac-toe game that can select tools.
- Analyze the user's request and pick the an appropriate tool if there is one.
- Be choosy and only select the tool that's right for the job, otherwise return 'none'.

${relevantResources.length > 0 ? `
RELEVANT CONTEXT FROM RESOURCES:
${relevantResources.map(resource => `
=== ${resource.name} ===
${resource.content.substring(0, 800)} // Shorter for tool selection
=== End of ${resource.name} ===
`).join('\n')}
` : ''}

AVAILABLE TOOLS:
${mcpTools.tools.map(tool => `- ${tool.name}: ${tool.description}`).join('\n')}

AVAILABLE TOOLS - EXAMPLE USAGE:
- best_move: {"board": ["X","O","X","O","O",null,"X","X",null], "player": "O", "game_over": false, "winner": null}
- random_move: {"board": ["X","O","X","O","O",null,"X","X",null], "player": "O", "game_over": false, "winner": null}
- play_move: {"board": ["X","O","X","O","O",null,"X","X",null], "player": "O, "position": 1"}
- new_game: {}

CURRENT BOARD STATE:
- Is Game Over? ${gameState.gameOver}
- Winner: ${gameState.winner || 'none'}
- Current Player: ${gameState.player}
- Board Layout (X & O - played squares, 1-9 - valid moves):
${visualizeBoard(gameState.board)}

CHAT HISTORY:
${formatChatHistoryForPrompt()}

INSTRUCTIONS:
- If the user's request is a single number, you can assume the play_move tool.
- If the is asking a question or asking for a suggestion, then just reply and avoid selecting a tool.
- Analyze the user's request and respond with exactly one of these formats:

1. If a tool should be used:
TOOL: tool_name
ARGS: {"key1": "value1", "key2": "value2"}
REASON: Brief explanation why this tool is appropriate
QUESTION: 'yes' if the user is asking a question, 'no' otherwise

2. If no tool is needed (just conversation):
TOOL: none
ARGS: {}
REASON: Brief explanation why no tool is needed
QUESTION: 'yes' if the user is asking a question, 'no' otherwise
RESPONSE: Your conversational response to the user

This is the user's request: "${message}"
`;
        console.log("CHOOSE TOOL PROMPT:", prompt)
        const ollamaResponse = await fetch(`${appConfig.ollamaHost}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: appConfig.ollamaModel,
                prompt: `${prompt}\n\nAssistant:`,
                stream: false,
                options: {
                    temperature: CONFIG.ollama.low_temperature,
                    max_tokens: CONFIG.ollama.maxTokens
                }
            })
        });
        
        if (!ollamaResponse.ok) {
            console.error('Ollama API error:', ollamaResponse.status, ollamaResponse.statusText);
            return {
                tool: 'none',
                reason: `Ollama API error: ${ollamaResponse.status}`,
                arguments: {},
                response: "Sorry, I couldn't process your message right now. Please try again.",
                availableTools: [],
                availableResources: [],
                analysis: ''
            };
        }

        const data = await ollamaResponse.json();
        const aiResponse = data.response?.trim() || '';
        console.log('OLLAMA RESPONSE:');
        console.log(aiResponse);
        
        const toolMatch = aiResponse.match(/TOOL:\s*(\w+)/);
        const argsMatch = aiResponse.match(/ARGS:\s*(\{.*?\})/s);
        const reasonMatch = aiResponse.match(/REASON:\s*(.+?)(?=\n|$)/s);
        const responseMatch = aiResponse.match(/RESPONSE:\s*(.+)/s);
        
        const tool = toolMatch ? toolMatch[1] : 'none';
        const reason = reasonMatch ? reasonMatch[1].trim() : 'No specific reason provided';
        const response = responseMatch ? responseMatch[1].trim() : null;
        const arguments = argsMatch ? JSON.parse(argsMatch[1]) : {};

        return {
            tool: tool || 'none',
            reason: reason,
            arguments: arguments || {},
            response: response,
            availableTools: mcpTools.tools.map(t => t.name),
            availableResources: mcpResources.resources,
            analysis: aiResponse
        };
    }
    catch (error) {
        console.error('Error determining tool:', error);
        return {
            tool: 'none',
            reason: 'Failed to analyze request: ' + error.message,
            arguments: {},
            response: "Sorry, I couldn't process your message right now. Please try again.",
            availableTools: [],
            availableResources: [],
            analysis: ''
        };
    }
}

// Helper function to determine relevant resources based on user message
async function getRelevantResourceContent(userMessage, availableResources) {
    const relevantResources = [];
    const message = userMessage.toLowerCase();
    
    // Keywords to resource mapping
    const resourceKeywords = {
        'chatttp://game-rules': ['rules', 'how to play', 'how do i', 'play', 'move', 'win', 'board', 'grid', 'position', 'cell', 'click'],
        'chatttp://strategy-guide': ['strategy', 'tactics', 'best move', 'winning', 'block', 'optimal', 'minimax', 'algorithm', 'think', 'plan'],
        'chatttp://ai-algorithms': ['technical', 'implementation', 'ai', 'algorithm', 'minimax', 'mcp', 'server', 'how it works', 'architecture'],
        'chatttp://commands-reference': ['command', 'interface', 'natural language', 'examples', 'phrases', 'interaction', 'chat', 'say']
    };
    
    // Check each resource for relevance
    for (const resource of availableResources) {
        const keywords = resourceKeywords[resource.uri] || [];
        const isRelevant = keywords.some(keyword => message.includes(keyword));
        
        // Also include resources if user asks general questions about the game
        const isGeneralGameQuestion = message.includes('how') || message.includes('what') || message.includes('explain');
        
        if (isRelevant || (isGeneralGameQuestion && resource.uri === 'chatttp://game-rules')) {
            try {
                // Fetch the resource content
                const response = await fetch(`${appConfig.mcpServerUrl}/mcp/resources/read`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        uri: resource.uri
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const content = data.contents?.[0]?.text || '';
                    
                    if (content) {
                        relevantResources.push({
                            uri: resource.uri,
                            name: resource.name,
                            content: content.substring(0, 2000) // Limit content length to avoid huge prompts
                        });
                    }
                }
            } catch (error) {
                console.error(`Error fetching resource ${resource.uri}:`, error);
            }
        }
    }
    
    return relevantResources;
}

async function aiSendMessage(message, args) {
    addBotMessage(GAME_MESSAGES.THINKING, false);
    
    try {
        let responseText = args.response;

        if (!responseText) {
            // Fetch all MCP data in parallel with a single /info call
            const [infoResponse, toolsResponse, resourcesResponse] = await Promise.all([
                fetch(`${appConfig.mcpServerUrl}/info`),
                fetch(`${appConfig.mcpServerUrl}/mcp/tools/list`),
                fetch(`${appConfig.mcpServerUrl}/mcp/resources/list`)
            ]);
            
            if (!infoResponse.ok || !toolsResponse.ok || !resourcesResponse.ok) {
                throw new Error(`HTTP ${infoResponse.status || toolsResponse.status || resourcesResponse.status}`);
            }

            const [infoData, toolsData, resourcesData] = await Promise.all([
                infoResponse.json(),
                toolsResponse.json(),
                resourcesResponse.json()
            ]);

            const mcpTools = {
                status: 'connected',
                serverInfo: infoData,
                tools: toolsData.tools || []
            };

            const mcpResources = {
                status: 'connected',
                serverInfo: infoData,
                resources: resourcesData.resources || []
            };

            // Determine which resources are relevant to include full content
            const relevantResources = await getRelevantResourceContent(message, mcpResources.resources);
            
            const prompt = `
- You are a smart assistant for a tic-tac-toe game that can have conversations.
- Provide helpful information about the game state, strategy tips, or general chat.

AVAILABLE RESOURCES:
${mcpResources.resources.map(resource => `- ${resource.name}: ${resource.description} (${resource.mimeType})`).join('\n')}

${relevantResources.length > 0 ? `
RELEVANT RESOURCE CONTENT:
${relevantResources.map(resource => `
=== ${resource.name} ===
${resource.content}
=== End of ${resource.name} ===
`).join('\n')}
` : ''}

CURRENT BOARD STATE:
- Is Game Over? ${gameState.gameOver}
- Winner: ${gameState.winner || 'none'}
- Current Player: ${gameState.player}
- Board Layout (X & O - played squares, 1-9 - valid moves):
${visualizeBoard(gameState.board)}

CHAT HISTORY:
${formatChatHistoryForPrompt()}

INSTRUCTIONS:
- Analyze the user's request and respond with helpful information.
- Use the relevant resource content above to provide accurate and detailed answers.
- Reference specific information from the resources when appropriate.

This is the user's request: "${message}"
`;
            console.log("SEND MESSAGE PROMPT:", prompt)
            const ollamaResponse = await fetch(`${appConfig.ollamaHost}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: appConfig.ollamaModel,
                    prompt: `${prompt}\n\nAssistant:`,
                    stream: false,
                    options: {
                        temperature: CONFIG.ollama.med_temperature,
                        max_tokens: CONFIG.ollama.maxTokens
                    }
                })
            });

            if (!ollamaResponse.ok) {
                responseText = "I'm at a loss of words.";
            }

            const data = await ollamaResponse.json();
            const aiResponse = data.response?.trim() || '';
            console.log('OLLAMA RESPONSE:');
            console.log(aiResponse);
            removeThinkingMessage();
            addBotMessage(aiResponse);
        }
    }
    catch (error) {
        removeThinkingMessage();
        addBotMessage(GAME_MESSAGES.CANT_PROCESS_MESSAGE);
    }
}

async function aiGetComment(message, player) {
    addBotMessage(GAME_MESSAGES.THINKING, false);
    
    try {
        const prompt = `
- You are a witty expert in the game of tic-tac-toe.
- Direct your comment to the one who made the last move.
- If it's O, then talk about yourself.  If it's X then talk about me.
- The last move was made by: ${player}

CURRENT BOARD STATE:
- Is Game Over? ${gameState.gameOver}
- Winner: ${gameState.winner || 'none'}
- Board Layout (X & O - played squares, 1-9 - valid moves):
${visualizeBoard(gameState.board)}

CHAT HISTORY:
${formatChatHistoryForPrompt()}

INSTRUCTIONS:
- Analyze the user's request and respond with a witty, but short remark.
- No more than one sentence.

This is the user's request: "${message}"
`;
        console.log("COMMENT MESSAGE PROMPT:", prompt)
        const ollamaResponse = await fetch(`${appConfig.ollamaHost}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: appConfig.ollamaModel,
                prompt: `${prompt}\n\nAssistant:`,
                stream: false,
                options: {
                    temperature: CONFIG.ollama.high_temperature,
                    max_tokens: CONFIG.ollama.maxTokens
                }
            })
        });

        if (!ollamaResponse.ok) {
            responseText = "I'm at a loss of words.";
        }

        const data = await ollamaResponse.json();
        const aiResponse = data.response?.trim() || '';
        console.log('OLLAMA RESPONSE:');
        console.log(aiResponse);

        removeThinkingMessage();
        addBotMessage(aiResponse);
    }
    catch (error) {
        removeThinkingMessage();
        addBotMessage(GAME_MESSAGES.CANT_PROCESS_MESSAGE);
    }
}

async function checkOllamaStatus() {
    try {
        const response = await fetch(`${appConfig.ollamaHost}/api/version`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        updateOllamaStatus('connected', { version: data.version });
        
        if (availableModels.length === 0 && !isLoadingModels) {
            await loadAvailableModels();
        }
    }
    catch (error) {
        console.error('Error checking Ollama status:', error);
        updateOllamaStatus('error', { error: error.message });
    }
}

function removeThinkingMessage() {
    const messages = chatMessages.querySelectorAll('.message.bot');
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.textContent.includes(GAME_MESSAGES.THINKING)) {
        lastMessage.remove();
    }
}

// MCP

async function callMCPTool(toolName, args) {
    addGameMessage(`MCP call: ${toolName} with arguments: ${JSON.stringify(args)}`);

    try {
        const response = await fetch(`${appConfig.mcpServerUrl}/mcp/tools/call`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: toolName,
                arguments: args
            })
        });

        const toolResult = await response.json();
        console.log(`MCP TOOL RESPONSE (${toolName}):`);
        console.log(toolResult);
        addGameMessage(`MCP returned: ${JSON.stringify(toolResult)}`);

        if (response.ok) return toolResult;

        throw new Error(`MCP API error: ${response.status}`);
    }
    catch (error) {
        console.error(`MCP tool ${toolName} call failed:`, error.message);
        throw error;
    }
}

async function getMCPCapabilities() {
    try {
        const infoResponse = await fetch(`${appConfig.mcpServerUrl}/info`);
        const toolsResponse = await fetch(`${appConfig.mcpServerUrl}/mcp/tools/list`);
        
        if (!infoResponse.ok || !toolsResponse.ok) {
            throw new Error(`HTTP ${infoResponse.status || toolsResponse.status}`);
        }

        const infoData = await infoResponse.json();
        const toolsData = await toolsResponse.json();

        return {
            status: 'connected',
            serverInfo: infoData,
            tools: toolsData.tools || []
        };
    }
    catch (error) {
        console.error('Error getting MCP capabilities:', error);
        return { 
            tools: [], 
            status: 'error',
            error: error.message
        };
    }
}

async function getMCPResources() {
    try {
        const infoResponse = await fetch(`${appConfig.mcpServerUrl}/info`);
        const resourcesResponse = await fetch(`${appConfig.mcpServerUrl}/mcp/resources/list`);

        if (!infoResponse.ok || !resourcesResponse.ok) {
            throw new Error(`HTTP ${infoResponse.status || resourcesResponse.status}`);
        }

        const infoData = await infoResponse.json();
        const resourcesData = await resourcesResponse.json();

        return {
            status: 'connected',
            serverInfo: infoData,
            resources: resourcesData.resources || []
        };
    }
    catch (error) {
        console.error('Error getting MCP resources:', error);
        return { 
            tools: [], 
            status: 'error',
            error: error.message
        };
    }
}

async function checkMCPStatus() {
    try {
        // Fetch all MCP data in parallel with a single /info call
        const [infoResponse, toolsResponse, resourcesResponse] = await Promise.all([
            fetch(`${appConfig.mcpServerUrl}/info`),
            fetch(`${appConfig.mcpServerUrl}/mcp/tools/list`),
            fetch(`${appConfig.mcpServerUrl}/mcp/resources/list`)
        ]);
        
        if (!infoResponse.ok || !toolsResponse.ok || !resourcesResponse.ok) {
            throw new Error(`HTTP ${infoResponse.status || toolsResponse.status || resourcesResponse.status}`);
        }

        const [infoData, toolsData, resourcesData] = await Promise.all([
            infoResponse.json(),
            toolsResponse.json(),
            resourcesResponse.json()
        ]);

        const capabilities = {
            status: 'connected',
            serverInfo: infoData,
            tools: toolsData.tools || []
        };

        const resources = {
            status: 'connected',
            serverInfo: infoData,
            resources: resourcesData.resources || []
        };

        updateMCPStatus(capabilities.status, { ...capabilities, resources: resources.resources });
        updateToolsPanel(capabilities.tools);
        updateResourcesPanel(resources.resources);
        restoreServicesPanelState();
    }
    catch (error) {
        console.error('Error checking MCP status:', error);
        updateMCPStatus('error', { error: error.message });
        updateToolsPanel([]);
        updateResourcesPanel([]);
        restoreServicesPanelState();
    }
}

// Handlers

function handleChatSubmit() {
    const input = chatInput.value.trim();
    if (!input) return;
    
    chatInput.value = '';
    addUserMessage(input);
    processChatInput(input);
}

async function handleNewGameRequest() {
    const confirmed = confirm("Start new game? Current game will be lost.");
    if (!confirmed) {
        addGameMessage("New game cancelled, please continue.");
        return;
    }

    const mcp_args = {};

    try {
        const toolResult = await callMCPTool('new_game', mcp_args);

        if (toolResult && !toolResult.isError) {
            resetGame();
            addGameMessage(`A new game was started!`);
            return;
        }
        
        addBotMessage(`A problem occured while resetting the game.`);
    }
    catch (error) {
        addBotMessage(`An error occured while resetting the game.`);
    }
}

async function handleBestMoveRequest(args) {
    if (gameState.gameOver) {
        addBotMessage(GAME_MESSAGES.GAME_OVER_NEW);
        return;
    }
    
    updateGameStatus(GAME_MESSAGES.THINKING_BEST_MOVE);

    const mpc_args = {
        board: gameState.board,
        player: gameState.player,
        game_over: gameState.gameOver,
        winner: gameState.winner
    };

    try {
        const toolResult = await callMCPTool('best_move', mpc_args);
   
        if (!toolResult) {
            return addBotMessage(`Error calling MCP random_move for ${mpc_args.player}.`);
        }

        if (toolResult.isError) {
            return addBotMessage(toolResult.content[0]);
        }

        const toolResponse = toolResult.content[0]?.text || '';
        const positionMatch = toolResponse.match(/position (\d+)/);
        
        if (positionMatch) {
            const bestMove = parseInt(positionMatch[1]);
            return handlePlayMoveRequest({ position: bestMove });
        }

        addBotMessage(`A problem occured while making the best move for ${mpc_args.player}.`);
    }
    catch (error) {
        addBotMessage(`An error occured while making the best move for ${mpc_args.player}.`);
    }
}

async function handleRandomMoveRequest(args) {
    if (gameState.gameOver) {
        addBotMessage(GAME_MESSAGES.GAME_OVER_NEW);
        return;
    }
    
    updateGameStatus(GAME_MESSAGES.GETTING_RANDOM_MOVE);

    const mpc_args = {
        board: gameState.board,
        player: gameState.player,
        game_over: gameState.gameOver,
        winner: gameState.winner
    };

    try {
        const toolResult = await callMCPTool('random_move', mpc_args);

        if (!toolResult) {
            return addBotMessage(`Error calling MCP random_move for ${mpc_args.player}.`);
        }

        if (toolResult.isError) {
            return addBotMessage(toolResult.content[0]);
        }

        const toolResponse = toolResult.content[0]?.text || '';
        const positionMatch = toolResponse.match(/position (\d+)/);
        
        if (positionMatch) {
            const randomMove = parseInt(positionMatch[1]);
            return handlePlayMoveRequest({ position: randomMove });
        }

        addBotMessage(`A problem occured while making a random move for ${mpc_args.player}.`);
    }
    catch (error) {
        addBotMessage(`An error occured while making a random move for ${mpc_args.player}.`);
    }
}

async function handlePlayMoveRequest(args) {
    if (gameState.gameOver) {
        addBotMessage(GAME_MESSAGES.GAME_OVER_NEW);
        return;
    }
    
    updateGameStatus(GAME_MESSAGES.PLAYING_MOVE);

    const mpc_args = {
        board: gameState.board,
        player: gameState.player,
        position: parseInt(args.position.toString())
    };

    try {
        const toolResult = await callMCPTool('play_move', mpc_args);

        if (!toolResult) {
            return addBotMessage(`Error calling MCP play_move ${args.position} for ${mpc_args.player}.`);
        }

        if (toolResult.isError) {
            return addBotMessage(toolResult.content[0]?.text);
        }
        
        addGameMessage(`${mpc_args.player} played a move in position ${args.position}!`);
        const success = makeMove(args.position, mpc_args.player); // gameState changes after makeMove()
        if (success) return;
        addBotMessage(`A problem occured while making move ${args.position} for ${mpc_args.player}.`);
    }
    catch (error) {
        addBotMessage(`An error occured while making move ${args.position} for ${mpc_args.player}.`);
    }
}

async function handleOllamaServerUpdate() {
    const newServerUrl = ollamaServerInput.value.trim();
    if (!newServerUrl || newServerUrl === appConfig.ollamaHost) return;

    try {
        new URL(newServerUrl);
    } catch (e) {
        addGameMessage('❌ Invalid URL format. Please enter a valid URL (e.g., http://localhost:11434)');
        return;
    }
    
    appConfig.ollamaHost = newServerUrl;
    addGameMessage(`🌐 Ollama server updated to: ${newServerUrl}`);
    await checkOllamaStatus();
    await loadAvailableModels();
}

async function handleMcpServerUpdate() {
    const newServerUrl = mcpServerInput.value.trim();
    if (!newServerUrl || newServerUrl === appConfig.mcpServerUrl) return;

    try {
        new URL(newServerUrl);
    }
    catch (e) {
        addGameMessage('❌ Invalid URL format. Please enter a valid URL (e.g., http://localhost:8000)');
        return;
    }

    appConfig.mcpServerUrl = newServerUrl;
    addGameMessage(`🔧 MCP server updated to: ${newServerUrl}`);
    await checkMCPStatus();
}

function handleModelChange() {
    const selectedModel = modelSelect.value;
    if (!selectedModel || selectedModel === appConfig.ollamaModel) return;

    appConfig.ollamaModel = selectedModel;
    updateOllamaStatus('connected', { model: selectedModel });
    addGameMessage(`🤖 Switched to model: ${selectedModel}`);
    console.log('Model changed to:', selectedModel);
}

// Game

async function requestAIMove() {
    if (gameState.gameOver) {
        addBotMessage(GAME_MESSAGES.GAME_OVER_NEW);
        return;
    }

    try {
        await handleBestMoveRequest({ player: PLAYERS.AI });
        await aiGetComment("Comment on how good your last move was", PLAYERS.AI);
    }
    catch (error) {
        console.error('Error requesting AI move:', error);
        addGameMessage('❌ Failed to get AI move. You can ask me to make a move manually.');
    }
}

function makeMove(position, player) {
    const index = position - 1;
    
    // Validation checks
    if (gameState.gameOver) {
        updateGameStatus(GAME_MESSAGES.GAME_OVER_START_NEW);
        return false;
    }
    
    if (index < 0 || index > 8) {
        updateGameStatus(GAME_MESSAGES.INVALID_POSITION);
        return false;
    }
    
    if (gameState.board[index] !== null) {
        updateGameStatus(GAME_MESSAGES.POSITION_TAKEN(position));
        return false;
    }
    
    if (gameState.player !== player) {
        updateGameStatus(`It's ${gameState.player}'s turn, not ${player}!`);
        return false;
    }
    
    // Make the move
    gameState.board[index] = player;
    let game_status, game_message;
    
    // Check for game end
    const winner = checkWinner(gameState.board);
    if (winner) {
        gameState.winner = winner;
        gameState.gameOver = true;
        game_status = `🎉 ${winner} wins!`;
        game_message = `🎉 Game Over! ${winner} wins!`;
        updateGameBoard();
    } 
    
    if (gameState.board.every(cell => cell !== null)) {
        gameState.winner = null; // Tie
        gameState.gameOver = true;
        game_status = `🤝 It's a tie!`;
        game_message = `🤝 Game Over! It's a tie!`;
        updateGameBoard();
    } 

    if (game_status && game_message) {
        updateGameStatus(game_status);
        addGameMessage(game_message);
        return true;
    }

    // Switch player and continue game
    gameState.player = gameState.player === PLAYERS.HUMAN ? PLAYERS.AI : PLAYERS.HUMAN;
    updateGameBoard();
    updateGameStatus();
    
    // If auto-play is enabled and it's now AI's turn, make an automatic move
    if (CONFIG.game.aiAutoPlay && gameState.player === PLAYERS.AI && !gameState.gameOver) {
        requestAIMove();
    }
    
    return true;
}

function resetGame() {
    gameState = {
        board: Array(9).fill(null),
        player: PLAYERS.HUMAN,
        gameOver: false,
        winner: null,
        gameId: Date.now()
    };

    clearChat();
    updateGameBoard();
    updateGameStatus(GAME_MESSAGES.NEW_GAME_STARTED);
    addGameMessage(GAME_MESSAGES.WELCOME);
}

function checkWinner(board) {
    const winningCombinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
        [0, 4, 8], [2, 4, 6] // diagonals
    ];

    for (const combination of winningCombinations) {
        const [a, b, c] = combination;
        if (board[a] && board[a] === board[b] && board[a] === board[c]) {
            return board[a];
        }
    }
    return null;
}

function updateGameBoard() {
    const cells = gameBoard.querySelectorAll('.cell');
    
    cells.forEach((cell, index) => {
        const value = gameState.board[index];
        
        cell.classList.remove('x', 'o', 'available', 'winning');
        
        if (value === PLAYERS.HUMAN) {
            cell.classList.add('x');
            cell.textContent = 'X';
        }
        else if (value === PLAYERS.AI) {
            cell.classList.add('o');
            cell.textContent = 'O';
        }
        else {
            cell.classList.add('available');
            cell.textContent = '';
            
            // Show position number on hover if game is not over and it's player's turn
            if (!gameState.gameOver && gameState.player === PLAYERS.HUMAN && CONFIG.game.enableHoverNumbers) {
                cell.setAttribute('data-hover', index + 1);
            }
        }
        
        const isClickable = !gameState.gameOver && value === null;
        cell.style.pointerEvents = isClickable ? 'auto' : 'none';
        cell.style.cursor = isClickable ? 'pointer' : 'default';
    });
    
    // Update game board classes for styling
    gameBoard.classList.toggle('game-over', gameState.gameOver);
    gameBoard.classList.toggle('x-turn', gameState.player === PLAYERS.HUMAN && !gameState.gameOver);
    gameBoard.classList.toggle('o-turn', gameState.player === PLAYERS.AI && !gameState.gameOver);
    
    updateGameStatus();
}

function visualizeBoard(board) {
    const a = board.map((cell, index) => {
        if (cell) return cell;
        return index+1;
    });
    return `${a[0]} ${a[1]} ${a[2]}\n${a[3]} ${a[4]} ${a[5]}\n${a[6]} ${a[7]} ${a[8]}`;
}

function updateGameStatus(message) {
    if (message) {
        gameStatus.textContent = message;
        return;
    }
    
    // Auto-generate status based on game state
    if (gameState.gameOver) {
        gameStatus.textContent = gameState.winner ? `🎉 ${gameState.winner} wins!` : "🤝 It's a tie!";
    } else if (gameState.player === PLAYERS.HUMAN) {
        gameStatus.textContent = "Your turn (X) - Click a cell or tell me your move";
    } else {
        // AI's turn - show different message based on auto-play setting
        if (CONFIG.game.aiAutoPlay) {
            gameStatus.textContent = "AI's turn (O) - Auto-playing...";
        } else {
            gameStatus.textContent = "AI's turn (O) - Ask me to make a move or suggest one";
        }
    }
}

// Chat

async function processChatInput(input) {
    // Parse the user input to determine which tool to use
    console.log('Processing user prompt:');
    console.log(input);
    const result = await aiChooseTool(input);
    
    if (result) {
        addGameMessage(result.reason + " [" + result.tool + "]");
    }

    crrentPlayer = gameState.player

    switch (result.tool) {
        case 'new_game':
            await handleNewGameRequest(result.arguments);
            break;
            
        case 'best_move':
            await handleBestMoveRequest(result.arguments);
            await aiGetComment(input, crrentPlayer);
            break;
            
        case 'random_move':
            await handleRandomMoveRequest(result.arguments);
            await aiGetComment(input, crrentPlayer);
            break;
            
        case 'play_move':
            await handlePlayMoveRequest(result.arguments);
            await aiGetComment(input, crrentPlayer);
            break;
            
        case 'none':
        default:
            await aiSendMessage(input, result.arguments);
            break;
    }
}

function formatChatHistoryForPrompt() {
    if (chatHistory.length === 0) {
        return "No previous conversation in this game.";
    }
    
    // Limit messages based on configuration to avoid token limits
    const recentHistory = chatHistory.slice(-CONFIG.chat.maxHistoryMessages);
    
    return recentHistory.map(msg => {
        const role = msg.type === 'user' ? 'User' : 'Assistant';
        return `${role}: ${msg.content}`;
    }).join('\n');
}

function formatMessageContent(content) {
    // Basic sanitization - escape HTML tags but preserve our formatting
    const sanitized = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    
    // Apply basic markdown-like formatting
    return sanitized
        // Bold text: **text** or __text__
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        // Italic text: *text* or _text_
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        // Code: `code`
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Line breaks
        .replace(/\n/g, '<br>');
}

function addMessage(type, content, preserveInHistory = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.innerHTML = formatMessageContent(content);
    messageDiv.appendChild(contentDiv);
    
    if (type !== 'system') {
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'timestamp';
        timestampDiv.textContent = new Date().toLocaleTimeString();
        messageDiv.appendChild(timestampDiv);

        if (preserveInHistory) {
            chatHistory.push({
                content: content,
                type: type,
                timestamp: new Date().toISOString()
            });
        }
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addGameMessage(content, preserveInHistory = true) {
    addMessage('system', content, preserveInHistory);
}

function addUserMessage(content, preserveInHistory = true) {
    addMessage('user', content, preserveInHistory);
}

function addBotMessage(content, preserveInHistory = true) {
    addMessage('bot', content, preserveInHistory);
}

function clearChat() {
    chatMessages.innerHTML = '';
    chatHistory = []; // Clear chat history as well
}

// Panel

function toggleServicesPanel() {
    const servicesPanel = servicesContent.closest('.services-panel');
    
    // Define the two states: collapsed ↔ fullscreen
    const isCollapsed = servicesPanel.classList.contains('collapsed');
    const isFullscreen = servicesPanel.classList.contains('fullscreen');
    
    if (isCollapsed || (!isFullscreen)) {
        // State 1: Collapsed → Fullscreen
        servicesPanel.classList.remove('collapsed', 'expanded');
        servicesPanel.classList.add('fullscreen');
        servicesToggle.querySelector('.toggle-icon').textContent = '⛷';
        servicesToggle.setAttribute('title', 'Minimize Panel');
        
    } else if (isFullscreen) {
        // State 2: Fullscreen → Collapsed
        servicesPanel.classList.remove('expanded', 'fullscreen');
        servicesPanel.classList.add('collapsed');
        servicesToggle.querySelector('.toggle-icon').textContent = '▼';
        servicesToggle.setAttribute('title', 'Show Services Settings');
    }
}

function toggleFullscreenPanel() {
    const servicesPanel = servicesContent.closest('.services-panel');
    
    const isFullscreen = servicesPanel.classList.contains('fullscreen');
    
    if (isFullscreen) {
        // Exit fullscreen
        servicesPanel.classList.remove('fullscreen');
        fullscreenToggle.textContent = '⛶';
        fullscreenToggle.setAttribute('title', 'Enter Fullscreen');
        
        // Restore the expanded state if it was expanded before
        if (!servicesPanel.classList.contains('collapsed')) {
            servicesPanel.classList.add('expanded');
        }
    } else {
        // Enter fullscreen
        servicesPanel.classList.add('fullscreen');
        servicesPanel.classList.remove('collapsed');
        servicesPanel.classList.add('expanded');
        fullscreenToggle.textContent = '⛷';
        fullscreenToggle.setAttribute('title', 'Exit Fullscreen');
    }
}

function restoreServicesPanelState() {
    const servicesPanel = servicesContent.closest('.services-panel');
    
    // Start in collapsed state by default
    servicesPanel.classList.remove('expanded', 'fullscreen');
    servicesPanel.classList.add('collapsed');
    servicesToggle.querySelector('.toggle-icon').textContent = '▼';
    servicesToggle.setAttribute('title', 'Show Services Settings');
}

function updateResourcesPanel(resources) {
    // Update the resources header with count
    resourcesHeader.textContent = `📚 Available Resources (${resources.length})`;
    
    resourcesList.innerHTML = '';
    
    if (resources.length === 0) {
        const noResourcesMsg = document.createElement('div');
        noResourcesMsg.className = 'no-resources-message';
        noResourcesMsg.textContent = 'No resources available';
        resourcesList.appendChild(noResourcesMsg);
        return;
    }
    
    resources.forEach(resource => {
        const resourceItem = document.createElement('div');
        resourceItem.className = 'resource-item';
        
        const resourceHeader = document.createElement('div');
        resourceHeader.className = 'resource-header';
        
        const resourceName = document.createElement('h4');
        resourceName.textContent = resource.name;
        resourceName.className = 'resource-name';
        
        const resourceType = document.createElement('span');
        resourceType.textContent = resource.mimeType;
        resourceType.className = 'resource-type';
        
        const resourceDescription = document.createElement('p');
        resourceDescription.textContent = resource.description;
        resourceDescription.className = 'resource-description';
        
        const resourceUri = document.createElement('a');
        resourceUri.href = '#';
        resourceUri.setAttribute('data-uri', resource.uri);
        resourceUri.textContent = 'View Content';
        resourceUri.className = 'resource-link';
        resourceUri.addEventListener('click', (e) => {
            e.preventDefault();
            showResourceContent(resource.uri, resource.name);
        });
        
        resourceHeader.appendChild(resourceName);
        resourceHeader.appendChild(resourceType);
        
        resourceItem.appendChild(resourceHeader);
        resourceItem.appendChild(resourceDescription);
        resourceItem.appendChild(resourceUri);
        
        resourcesList.appendChild(resourceItem);
    });
}

function updateToolsPanel(tools) {
    // Update the tools header with count
    toolsHeader.textContent = `🔧 Available Tools (${tools.length})`;
    
    toolsList.innerHTML = '';
    
    if (tools.length === 0) {
        const noToolsMsg = document.createElement('div');
        noToolsMsg.className = 'no-tools-message';
        noToolsMsg.textContent = 'No tools available';
        toolsList.appendChild(noToolsMsg);
        return;
    }
    
    tools.forEach(tool => {
        const toolItem = document.createElement('div');
        toolItem.className = 'tool-item';
        
        const toolHeader = document.createElement('div');
        toolHeader.className = 'tool-header';
        
        const toolName = document.createElement('h4');
        toolName.textContent = tool.name;
        toolName.className = 'tool-name';
        
        const toolDescription = document.createElement('p');
        toolDescription.textContent = tool.description;
        toolDescription.className = 'tool-description';
        
        // Show input schema if available
        if (tool.inputSchema && tool.inputSchema.properties) {
            const toolParams = document.createElement('div');
            toolParams.className = 'tool-params';
            
            const paramsTitle = document.createElement('strong');
            paramsTitle.textContent = 'Parameters: ';
            toolParams.appendChild(paramsTitle);
            
            const paramsList = Object.keys(tool.inputSchema.properties).join(', ');
            const paramsText = document.createElement('span');
            paramsText.textContent = paramsList;
            paramsText.className = 'params-list';
            toolParams.appendChild(paramsText);
            
            toolItem.appendChild(toolHeader);
            toolItem.appendChild(toolDescription);
            toolItem.appendChild(toolParams);
        } else {
            toolHeader.appendChild(toolName);
            toolItem.appendChild(toolHeader);
            toolItem.appendChild(toolDescription);
        }
        
        toolHeader.appendChild(toolName);
        
        toolsList.appendChild(toolItem);
    });
}

function createResourceModal() {
    const modal = document.createElement('div');
    modal.id = 'resourceModal';
    modal.className = 'resource-modal';
    
    modal.innerHTML = `
        <div class="resource-modal-content">
            <div class="resource-modal-header">
                <h2 class="resource-modal-title">Resource</h2>
                <span class="resource-modal-close">&times;</span>
            </div>
            <div class="resource-modal-body">
                Loading...
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const closeBtn = modal.querySelector('.resource-modal-close');
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    return modal;
}

function formatResourceContent(content) {
    // Simple markdown-like formatting
    let formatted = content
        // Headers
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Code blocks
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        // Inline code
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Line breaks
        .replace(/\n\n/g, '</p><p>')
        // Lists
        .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
        .replace(/^- (.*$)/gm, '<li>$1</li>');
    
    // Wrap in paragraphs
    if (!formatted.includes('<h1>') && !formatted.includes('<h2>')) {
        formatted = '<p>' + formatted + '</p>';
    }
    
    // Fix list formatting
    formatted = formatted.replace(/(<li>.*<\/li>)/g, (match) => {
        return '<ul>' + match + '</ul>';
    });
    
    return formatted;
}

async function showResourceContent(uri, name) {
    try {
        // Create modal if it doesn't exist
        let modal = document.getElementById('resourceModal');
        modal = modal || createResourceModal();
        
        // Show loading state
        const modalContent = modal.querySelector('.resource-modal-content');
        const modalTitle = modal.querySelector('.resource-modal-title');
        const modalBody = modal.querySelector('.resource-modal-body');
        
        modalTitle.textContent = name;
        modalBody.innerHTML = '<div class="loading">Loading resource content...</div>';
        modal.style.display = 'block';
        
        // Fetch resource content using standard MCP endpoint
        const response = await fetch(`${appConfig.mcpServerUrl}/mcp/resources/read`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                uri: uri
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            const content = data.contents?.[0]?.text || 'No content available';
            
            // Convert markdown-style content to HTML
            const htmlContent = formatResourceContent(content);
            modalBody.innerHTML = htmlContent;
        } else {
            modalBody.innerHTML = '<div class="error">Failed to load resource content</div>';
        }
    } catch (error) {
        console.error('Error loading resource content:', error);
        const modalBody = document.querySelector('.resource-modal-body');
        modalBody.innerHTML = '<div class="error">Error loading resource content</div>';
    }
}

async function loadAvailableModels() {
    if (isLoadingModels) return;
    
    isLoadingModels = true;
    
    try {
        // Update UI to show loading state
        modelSelect.disabled = true;
        modelSelect.innerHTML = '<option value="">Loading models...</option>';
        refreshModelsBtn.disabled = true;
        
        const response = await fetch(`${appConfig.ollamaHost}/api/tags`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            availableModels = data.models?.map(model => model.name) || [];
            
            // Update model selector
            updateModelSelector();
            
            console.log('Available models loaded:', availableModels);
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading available models:', error);
        availableModels = [];
        
        modelSelect.innerHTML = '<option value="">Failed to load models</option>';
        
        // Add system message about model loading failure
        addGameMessage('⚠️ Could not load available models. Using default model.');
    } finally {
        isLoadingModels = false;
        
        refreshModelsBtn.disabled = false;
    }
}

function updateOllamaStatus(status, data) {
    const statusIndicator = ollamaStatus.querySelector('.dot');
    
    const statusConfig = {
        connected: {
            class: 'connected',
            text: `Connected (${data?.model || appConfig.ollamaModel})`,
            color: '#4CAF50'
        },
        disconnected: {
            class: 'disconnected',
            text: 'Disconnected',
            color: '#f44336'
        },
        error: {
            class: 'error',
            text: 'Error',
            color: '#ff9800'
        }
    };
    
    ollamaStatus.classList.remove('connected', 'disconnected', 'error');
    
    const config = statusConfig[status] || statusConfig.error;
    ollamaStatus.classList.add(config.class);
    ollamaStatusText.textContent = config.text;
    statusIndicator.style.backgroundColor = config.color;
}

function updateMCPStatus(status, data) {
    const statusIndicator = mcpStatus.querySelector('.dot');
    const toolsCount = data.tools?.length || 0;
    const resourcesCount = data.resources?.length || 0;
    
    const statusConfig = {
        connected: {
            class: 'connected',
            text: `Connected (${toolsCount} tools, ${resourcesCount} resources)`,
            color: '#4CAF50'
        },
        disconnected: {
            class: 'disconnected',
            text: 'Disconnected',
            color: '#f44336'
        },
        error: {
            class: 'error',
            text: 'Error',
            color: '#ff9800'
        }
    };
    
    mcpStatus.classList.remove('connected', 'disconnected', 'error');
    
    const config = statusConfig[status] || statusConfig.error;
    mcpStatus.classList.add(config.class);
    mcpStatusText.textContent = config.text;
    statusIndicator.style.backgroundColor = config.color;
}

function updateModelSelector() {
    modelSelect.innerHTML = '';
    
    if (availableModels.length === 0) {
        modelSelect.innerHTML = '<option value="">No models available</option>';
        modelSelect.disabled = true;
        return;
    }
    
    // Add default/placeholder option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select a model...';
    modelSelect.appendChild(defaultOption);
    
    // Add available models
    availableModels.forEach(modelName => {
        const option = document.createElement('option');
        option.value = modelName;
        option.textContent = modelName;
        
        // Mark as selected if it matches current model
        if (modelName === appConfig.ollamaModel) {
            option.selected = true;
        }
        
        modelSelect.appendChild(option);
    });
    
    modelSelect.disabled = false;
}
