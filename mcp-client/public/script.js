// ChatTTT Client Script

// ========================================
// CONFIGURATION SECTION
// ========================================
const CONFIG = {
    // Server Configuration
    server: {
        mcpServerUrl: 'http://127.0.0.1:8000',
        ollamaHost: 'http://omega:11434',
        ollamaModel: 'llama3.2:latest'
    },
    
    // Ollama API Settings
    ollama: {
        temperature: 0.3,
        maxTokens: 4096,
        timeout: 15000
    },
    
    // MCP Tool Settings
    mcp: {
        timeout: 10000,
        statusCheckInterval: 300000, // 5 minutes instead of 30 seconds
        autoRefreshResources: true,
        enablePeriodicStatusCheck: false // Disable automatic polling by default
    },
    
    // Chat Settings
    chat: {
        maxHistoryMessages: 20,
        enableUpArrowRepeat: true,
        showTimestamps: true,
        showSystemMessages: true
    },
    
    // Game Settings
    game: {
        autoSwitchPlayer: true,
        confirmNewGameInProgress: true,
        showMoveNumbers: true,
        enableKeyboardShortcuts: true
    },
    
    // UI Settings
    ui: {
        showResourcesPanel: true,
        showMCPStatus: true,
        enableHoverNumbers: true,
        showToolSelectionReason: true
    }
};

const PLAYERS = {
    HUMAN: 'X',
    AI: 'O'
};

const GAME_MESSAGES = {
    WELCOME: "Welcome to ChatTTT! Click a cell or tell me where you'd like to play. I can also help with strategy or make suggestions.",
    GAME_OVER_NEW: "The game is over! Let me know if you'd like to start a new game.",
    POSITION_TAKEN: (pos) => `Position ${pos} is already taken!`,
    NOT_YOUR_TURN: "It's not your turn right now.",
    INVALID_POSITION: "That's not a valid position. Please choose a spot from 1-9.",
    GAME_OVER_START_NEW: "Game is over! Would you like to start again?",
    NEW_GAME_STARTED: 'New game started! Your turn (X)',
    CANT_PROCESS_MESSAGE: "Sorry, I couldn't understand that. Could you try asking differently?",
    THINKING: "🤔 Thinking...",
    AI_THINKING: 'AI is thinking...',
    GETTING_RANDOM_MOVE: 'Finding a random move...',
    THINKING_BEST_MOVE: 'Analyzing the best move...',
    PLAYING_MOVE: 'Making your move...',
    CONFUSED: 'I do not know what to do.',
    NEW_GAME_CONFIRMATION: "⚠️ You have a game in progress. Are you sure you want to start a new game? The current game will be lost. Please confirm or cancel.",
    INVALID_CONFIRMATION: "Please confirm if you want to start a new game or continue the current one.",
    ACTION_CANCELLED: "Action cancelled. Continuing with the current game."
};

let appConfig = {
    mcpServerUrl: CONFIG.server.mcpServerUrl,
    ollamaHost: CONFIG.server.ollamaHost,
    ollamaModel: CONFIG.server.ollamaModel
};

let gameState = {
    board: Array(9).fill(null),
    player: PLAYERS.HUMAN,
    gameOver: false,
    winner: null,
    gameId: Date.now()
};

// Chat history for up arrow functionality
let lastChatInput = '';

// Chat history for context (stores messages for current game)
let chatHistory = [];

// Pending confirmation state
let pendingConfirmation = null;

// DOM elements
let gameBoard, gameStatus, mcpStatus, mcpStatusText, chatMessages, chatInput, sendBtn, resourcesPanel, resourcesList;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
    loadConfiguration();
    checkMCPStatus();
    loadMCPResources();
    resetGame();
    updateGameStatus();
    // Don't clear chat on initial load - there's no history yet
    addSystemMessage(GAME_MESSAGES.WELCOME);
});

function initializeElements() {
    gameBoard = document.getElementById('gameBoard');
    gameStatus = document.getElementById('gameStatus');
    mcpStatus = document.getElementById('mcpStatus');
    mcpStatusText = document.getElementById('mcpStatusText');
    chatMessages = document.getElementById('chatMessages');
    chatInput = document.getElementById('chatInput');
    sendBtn = document.getElementById('sendBtn');
    resourcesPanel = document.getElementById('resourcesPanel');
    resourcesList = document.getElementById('resourcesList');
}

async function loadConfiguration() {
    console.log('Using default configuration:');
    console.log(appConfig);
}

// Game Logic Functions
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
    
    // Check for game end
    const winner = checkWinner(gameState.board);
    if (winner) {
        gameState.winner = winner;
        gameState.gameOver = true;
        updateGameBoard();
        updateGameStatus(`🎉 ${winner} wins!`);
        addSystemMessage(`🎉 Game Over! ${winner} wins!`);
        return true;
    } 
    
    if (gameState.board.every(cell => cell !== null)) {
        gameState.winner = null; // Tie
        gameState.gameOver = true;
        updateGameBoard();
        updateGameStatus(`🤝 It's a tie!`);
        addSystemMessage(`🤝 Game Over! It's a tie!`);
        return true;
    } 
    
    // Switch player and continue game
    gameState.player = gameState.player === PLAYERS.HUMAN ? PLAYERS.AI : PLAYERS.HUMAN;
    updateGameBoard();
    updateGameStatus();
    return true;
}

function startNewGame() {
    resetGame();
    // Clear chat history when starting a new game
    clearChat();
    updateGameStatus(GAME_MESSAGES.NEW_GAME_STARTED);
    addSystemMessage(GAME_MESSAGES.WELCOME);
}

function resetGame() {
    gameState = {
        board: Array(9).fill(null),
        player: PLAYERS.HUMAN,
        gameOver: false,
        winner: null,
        gameId: Date.now()
    };
    
    // Clear any pending confirmations
    pendingConfirmation = null;
    
    // Clear chat history for new game
    chatHistory = [];
    
    updateGameBoard();
    updateGameStatus();
}

async function handleNewGameRequest() {
    // If game is already over, start new game immediately without confirmation
    if (gameState.gameOver) {
        startNewGame();
        addBotMessage("Starting a new game!");
        return;
    }
    
    // If game is in progress, ask for confirmation
    const movesMade = gameState.board.filter(cell => cell !== null).length;
    if (movesMade > 0) {
        pendingConfirmation = {
            action: 'new_game',
            message: GAME_MESSAGES.NEW_GAME_CONFIRMATION
        };
        
        addBotMessage(GAME_MESSAGES.NEW_GAME_CONFIRMATION);
        return;
    }
    
    // If no moves made yet, start new game without confirmation
    startNewGame();
    addBotMessage("Starting a new game!");
}

// Chat Functions
function addMessage(content, type = 'bot', includeTimestamp = CONFIG.chat.showTimestamps) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.textContent = content;
    messageDiv.appendChild(contentDiv);
    
    if (includeTimestamp && type !== 'system' && CONFIG.chat.showTimestamps) {
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'timestamp';
        timestampDiv.textContent = new Date().toLocaleTimeString();
        messageDiv.appendChild(timestampDiv);
    }
    
    // Store in chat history (exclude system messages from history)
    if (type !== 'system') {
        chatHistory.push({
            content: content,
            type: type,
            timestamp: new Date().toISOString()
        });
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addSystemMessage(content) {
    if (CONFIG.chat.showSystemMessages) {
        addMessage(content, 'system', false);
    }
}

function addUserMessage(content) {
    addMessage(content, 'user');
}

function addBotMessage(content) {
    addMessage(content, 'bot');
}

function clearChat() {
    chatMessages.innerHTML = '';
    chatHistory = []; // Clear chat history as well
}

function removeThinkingMessage() {
    const messages = chatMessages.querySelectorAll('.message.bot');
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.textContent.includes(GAME_MESSAGES.THINKING)) {
        lastMessage.remove();
    }
}

async function processChatInput(input) {
    // Handle pending confirmation first
    if (pendingConfirmation) {
        const normalizedInput = input.toLowerCase().trim();
        
        // More flexible confirmation understanding
        const confirmWords = ['yes', 'y', 'ok', 'okay', 'sure', 'confirm', 'proceed', 'go ahead'];
        const cancelWords = ['no', 'n', 'cancel', 'stop', 'nevermind', 'abort'];
        
        const isConfirm = confirmWords.some(word => normalizedInput.includes(word));
        const isCancel = cancelWords.some(word => normalizedInput.includes(word));
        
        if (isConfirm && !isCancel) {
            // User confirmed the action
            const action = pendingConfirmation.action;
            pendingConfirmation = null; // Clear confirmation
            
            if (action === 'new_game') {
                startNewGame();
                addBotMessage("New game started!");
            }
            return;
        } else if (isCancel) {
            // User cancelled the action
            addBotMessage(GAME_MESSAGES.ACTION_CANCELLED);
            pendingConfirmation = null; // Clear confirmation
            return;
        } else {
            // Invalid response to confirmation
            addBotMessage(GAME_MESSAGES.INVALID_CONFIRMATION);
            return;
        }
    }
    
    // Parse the user input to determine which tool to use
    console.log('Processing user prompt:');
    console.log(input);
    const result = await pickToolToUse(input);
    console.log('Tool selection result:');
    console.log(result);
    
    // Show tool identification information
    if (result && CONFIG.ui.showToolSelectionReason) {
        addSystemMessage(result.reason + " [" + result.tool + "]");
    }

    // Execute the appropriate action based on the identified tool
    await executeToolAction(result.tool, result.arguments, input, result.conversationalResponse);
}

async function executeToolAction(toolName, args, originalInput, conversationalResponse = null) {
    switch (toolName) {
        case 'new_game':
            await handleNewGameRequest();
            break;
            
        case 'best_move':
            await requestBestMove(args);
            break;
            
        case 'random_move':
            await requestRandomMove(args);
            break;
            
        case 'play_move':
            await requestPlayMove(args);
            break;
            
        case 'no_move':
            await sendChatMessage(originalInput, conversationalResponse);
            break;
            
        case 'none':
        default:
            // For 'none' or any unrecognized tool, use conversational response if available
            await sendChatMessage(originalInput, conversationalResponse);
            break;
    }
}

async function getMCPCapabilities() {
    try {
        // Try to get server info
        const infoResponse = await fetch(`${appConfig.mcpServerUrl}/info`);
        
        // Try to get available tools
        const toolsResponse = await fetch(`${appConfig.mcpServerUrl}/tools`);
        
        if (infoResponse.ok && toolsResponse.ok) {
            const infoData = await infoResponse.json();
            const toolsData = await toolsResponse.json();
            
            return {
                status: 'connected',
                serverInfo: infoData,
                tools: toolsData.tools || []
            };
        } else {
            throw new Error(`HTTP ${infoResponse.status || toolsResponse.status}`);
        }
    } catch (error) {
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
        const response = await fetch(`${appConfig.mcpServerUrl}/resources`);
        if (response.ok) {
            const data = await response.json();
            return data.resources || [];
        }
        return [];
    } catch (error) {
        console.error('Error getting MCP resources:', error);
        return [];
    }
}

async function loadMCPResources() {
    try {
        const resources = await getMCPResources();
        updateResourcesPanel(resources);
    } catch (error) {
        console.error('Error loading MCP resources:', error);
        updateResourcesPanel([]);
    }
}

function updateResourcesPanel(resources) {
    if (!resourcesPanel || !resourcesList) {
        console.warn('Resources panel elements not found');
        return;
    }
    
    // Clear existing resources
    resourcesList.innerHTML = '';
    
    // Check if resources panel should be shown based on configuration
    if (!CONFIG.ui.showResourcesPanel || resources.length === 0) {
        resourcesPanel.classList.remove('show');
        return;
    }
    
    // Show panel and populate resources
    resourcesPanel.classList.add('show');
    
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

async function showResourceContent(uri, name) {
    try {
        // Create modal if it doesn't exist
        let modal = document.getElementById('resourceModal');
        if (!modal) {
            modal = createResourceModal();
        }
        
        // Show loading state
        const modalContent = modal.querySelector('.resource-modal-content');
        const modalTitle = modal.querySelector('.resource-modal-title');
        const modalBody = modal.querySelector('.resource-modal-body');
        
        modalTitle.textContent = name;
        modalBody.innerHTML = '<div class="loading">Loading resource content...</div>';
        modal.style.display = 'block';
        
        // Fetch resource content
        const response = await fetch(`${appConfig.mcpServerUrl}/resources/${encodeURIComponent(uri)}`);
        
        if (response.ok) {
            const data = await response.json();
            const content = data.content || 'No content available';
            
            // Convert markdown-style content to HTML
            const htmlContent = formatResourceContent(content);
            modalBody.innerHTML = htmlContent;
        } else {
            modalBody.innerHTML = '<div class="error">Failed to load resource content</div>';
        }
    } catch (error) {
        console.error('Error loading resource content:', error);
        const modalBody = document.querySelector('.resource-modal-body');
        if (modalBody) {
            modalBody.innerHTML = '<div class="error">Error loading resource content</div>';
        }
    }
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
    
    // Add event listeners
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

// Helper function to call MCP tools directly
async function callMCPTool(toolName, args) {
    try {
        const response = await fetch(`${appConfig.mcpServerUrl}/call-tool`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: toolName,
                arguments: args
            })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`MCP API error: ${response.status}`);
        }
    } catch (error) {
        console.error(`MCP tool ${toolName} call failed:`, error.message);
        throw error;
    }
}

async function requestBestMove(args) {
    if (gameState.gameOver) {
        addBotMessage(GAME_MESSAGES.GAME_OVER_NEW);
        return;
    }
    
    updateGameStatus(GAME_MESSAGES.THINKING_BEST_MOVE);
    
    try {
        // Always call the MCP server to get the best move
        const toolResult = await callMCPTool('best_move', {
            board: gameState.board,
            player: gameState.player,
            game_over: gameState.gameOver,
            winner: gameState.winner
        });
        
        if (toolResult && !toolResult.isError) {
            const toolResponse = toolResult.content[0]?.text || '';
            const positionMatch = toolResponse.match(/position (\d+)/);
            
            if (positionMatch) {
                const bestMove = parseInt(positionMatch[1]);
                const success = makeMove(bestMove, gameState.player);
                if (success) {
                    addBotMessage(`The best move is position ${bestMove}!`);
                } else {
                    addBotMessage("Sorry, I couldn't make that best move.");
                }
            } else {
                addBotMessage("Sorry, I couldn't determine the best move right now.");
            }
        } else {
            addBotMessage("Sorry, I couldn't get the best move right now.");
        }
    } catch (error) {
        console.error('Error getting best move:', error);
        addBotMessage("Sorry, I couldn't get the best move right now.");
    }
}

async function requestRandomMove(args) {
    if (gameState.gameOver) {
        addBotMessage(GAME_MESSAGES.GAME_OVER_NEW);
        return;
    }
    
    updateGameStatus(GAME_MESSAGES.GETTING_RANDOM_MOVE);
    
    try {
        // Always call the MCP server to get the random move
        const toolResult = await callMCPTool('random_move', {
            board: gameState.board,
            player: gameState.player,
            game_over: gameState.gameOver,
            winner: gameState.winner
        });
        
        if (toolResult && !toolResult.isError) {
            const toolResponse = toolResult.content[0]?.text || '';
            const positionMatch = toolResponse.match(/position (\d+)/);
            
            if (positionMatch) {
                const randomMove = parseInt(positionMatch[1]);
                const success = makeMove(randomMove, gameState.player);
                if (success) {
                    addBotMessage(`Random move: position ${randomMove}!`);
                } else {
                    addBotMessage("Sorry, I couldn't make that random move.");
                }
            } else {
                addBotMessage("Sorry, I couldn't get a random move right now.");
            }
        } else {
            addBotMessage("Sorry, I couldn't get a random move right now.");
        }
    } catch (error) {
        console.error('Error getting random move:', error);
        addBotMessage("Sorry, I couldn't get a random move right now.");
    }
}

async function requestPlayMove(args) {
    if (gameState.gameOver) {
        addBotMessage(GAME_MESSAGES.GAME_OVER_NEW);
        return;
    }
    
    // Extract position from args or parse from user input
    let position = null;
    if (args && args.position !== undefined) {
        // If position is provided in args, use it
        position = Array.isArray(args.position) ? args.position[0] : args.position;
    }
    
    if (position === null || position < 1 || position > 9) {
        addBotMessage("Invalid position specified. Please choose a position between 1-9.");
        return;
    }
    
    updateGameStatus(GAME_MESSAGES.PLAYING_MOVE);
    
    try {
        const success = makeMove(position, gameState.player);
        if (success) {
            addBotMessage(`Played move at position ${position}!`);
        } else {
            addBotMessage(`Sorry, I couldn't make that move at position ${position}.`);
        }
    } catch (error) {
        console.error('Error making play move:', error);
        addBotMessage("Sorry, I couldn't make that move.");
    }
}

async function pickToolToUse(message) {
    try {
        // First get available MCP tools and resources
        const [mcpCapabilities, mcpResources] = await Promise.all([
            getMCPCapabilities(),
            getMCPResources()
        ]);
        const availableTools = mcpCapabilities.tools || [];
        
        const systemPrompt = `
You are a smart assistant for a ChatTTT game that can both select tools and have conversations.
Your job is to analyze the user's request and either recommend a tool or provide a conversational response.

Current game state:
Board: ${JSON.stringify(gameState.board)} (positions 1-9, null = empty, X/O = taken)
Current Player: ${gameState.player}
Game Over: ${gameState.gameOver}
Winner: ${gameState.winner || 'none'}

Board layout:
 1 2 3 
 4 5 6 
 7 8 9 

Current board visualization:
${visualizeBoard(gameState.board)}

Previous conversation in this game:
${formatChatHistoryForPrompt()}

Available Tools:
${availableTools.map(tool => `- ${tool.name}: ${tool.description}`).join('\n')}

Available Resources:
${mcpResources.map(resource => `- ${resource.name}: ${resource.description} (${resource.mimeType})`).join('\n')}

User request: "${message}"

If the user asks about resources, guides, help documentation, or strategy, mention the available resources in your response.

Analyze the user's request and respond with exactly one of these formats:

1. If a tool should be used:
TOOL: tool_name
ARGS: {"key1": "value1", "key2": "value2"}
REASON: Brief explanation why this tool is appropriate

2. If no tool is needed (just conversation):
TOOL: none
ARGS: {}
REASON: Brief explanation why no tool is needed
RESPONSE: Your conversational response to the user

For game tools that need board state, use these argument structures:
- best_move/random_move: {"board": ${JSON.stringify(gameState.board)}, "player": "${gameState.player}", "game_over": ${gameState.gameOver}, "winner": ${gameState.winner ? `"${gameState.winner}"` : 'null'}}
- play_move: {"board": ${JSON.stringify(gameState.board)}, "position": [position_number], "player": "${gameState.player}"}
- new_game: {}
- no_move: {}

For conversational responses, provide helpful information about the game state, strategy tips, or general chat.
If the user asks about help, guides, or strategy, mention the available resources.
Remember the conversation history and respond appropriately to follow-up questions or references to previous messages.
`;
        // Call Ollama API directly
        const ollamaResponse = await fetch(`${appConfig.ollamaHost}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: appConfig.ollamaModel,
                prompt: `${systemPrompt}\n\nAssistant:`,
                stream: false,
                options: {
                    temperature: CONFIG.ollama.temperature,
                    max_tokens: CONFIG.ollama.maxTokens
                }
            })
        });
        
        if (ollamaResponse.ok) {
            const data = await ollamaResponse.json();
            const aiResponse = data.response?.trim() || '';
            console.log('Ollama response:');
            console.log(aiResponse);
            
            // Parse the AI response
            const toolMatch = aiResponse.match(/TOOL:\s*(\w+)/);
            const argsMatch = aiResponse.match(/ARGS:\s*(\{.*?\})/s);
            const reasonMatch = aiResponse.match(/REASON:\s*(.+?)(?=\n|$)/s);
            const responseMatch = aiResponse.match(/RESPONSE:\s*(.+)/s);
            
            const recommendedTool = toolMatch ? toolMatch[1] : 'none';
            const reason = reasonMatch ? reasonMatch[1].trim() : 'No specific reason provided';
            const conversationalResponse = responseMatch ? responseMatch[1].trim() : null;
            
            let arguments = {};
            if (argsMatch) {
                try {
                    arguments = JSON.parse(argsMatch[1]);
                } catch (e) {
                    console.warn('Failed to parse tool arguments:', e.message);
                    arguments = {};
                }
            }
            
            // Validate the recommended tool exists
            const isValidTool = recommendedTool === 'none' || 
                              availableTools.some(tool => tool.name === recommendedTool);
            
            return {
                tool: isValidTool ? recommendedTool : 'none',
                reason: reason,
                arguments: isValidTool ? arguments : {},
                conversationalResponse: conversationalResponse,
                availableTools: availableTools.map(t => t.name),
                availableResources: mcpResources,
                analysis: aiResponse
            };
        } else {
            console.error('Ollama API error:', ollamaResponse.status, ollamaResponse.statusText);
            return {
                tool: 'none',
                reason: `Ollama API error: ${ollamaResponse.status}`,
                arguments: {},
                conversationalResponse: "Sorry, I couldn't process your message right now. Please try again.",
                availableTools: [],
                availableResources: [],
                analysis: ''
            };
        }
    } catch (error) {
        console.error('Error determining tool:', error);
        return {
            tool: 'none',
            reason: 'Failed to analyze request: ' + error.message,
            arguments: {},
            conversationalResponse: "Sorry, I couldn't process your message right now. Please try again.",
            availableTools: [],
            availableResources: [],
            analysis: ''
        };
    }
}

async function sendChatMessage(message, providedResponse = null) {
    addBotMessage(GAME_MESSAGES.THINKING);
    
    try {
        let responseText = providedResponse;
        
        // If no response provided, use a fallback approach
        if (!responseText) {
            responseText = "I'm here to help with your ChatTTT game! You can click on the board, tell me where to play, ask for move suggestions, or start a new game. What would you like to do?";
        }
        
        removeThinkingMessage();
        addBotMessage(responseText);
        
    } catch (error) {
        console.error('Error sending chat message:', error);
        removeThinkingMessage();
        addBotMessage(GAME_MESSAGES.CANT_PROCESS_MESSAGE);
    }
}

// Helper function to visualize the board
function visualizeBoard(board) {
    const display = board.map((cell, index) => {
        if (cell) return cell;
        return index+1;
    });
    
    return `${display[0]} ${display[1]} ${display[2]}
${display[3]} ${display[4]} ${display[5]}
${display[6]} ${display[7]} ${display[8]}`;
}

// Helper function to format chat history for the prompt
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

function setupEventListeners() {
    // Game board cell clicks
    gameBoard.addEventListener('click', handleBoardClick);
    
    // Chat input events
    sendBtn.addEventListener('click', handleChatSubmit);
    chatInput.addEventListener('keypress', handleChatKeyPress);
    chatInput.addEventListener('keydown', handleChatKeyDown);
}

function handleBoardClick(e) {
    if (!e.target.classList.contains('cell')) return;
    
    const position = parseInt(e.target.dataset.position);
    if (position >= 1 && position <= 9 && !gameState.gameOver) {
        addUserMessage(position.toString());
        processChatInput(position.toString());
    }
}

function handleChatKeyPress(e) {
    if (e.key === 'Enter') {
        handleChatSubmit();
    }
}

function handleChatKeyDown(e) {
    // Handle up arrow to repeat last input
    if (e.key === 'ArrowUp' && CONFIG.chat.enableUpArrowRepeat && lastChatInput && chatInput.value === '') {
        e.preventDefault();
        chatInput.value = lastChatInput;
        chatInput.setSelectionRange(chatInput.value.length, chatInput.value.length);
    }
}

function handleChatSubmit() {
    const input = chatInput.value.trim();
    if (!input) return;
    
    // Store the input for up arrow functionality
    lastChatInput = input;
    
    // Add user message to chat
    addUserMessage(input);
    
    // Clear input
    chatInput.value = '';
    
    // Process the input
    processChatInput(input);
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
        gameStatus.textContent = "AI's turn (O) - Ask me to make a move or suggest one";
    }
}

function updateGameBoard() {
    const cells = gameBoard.querySelectorAll('.cell');
    
    cells.forEach((cell, index) => {
        const value = gameState.board[index];
        
        // Clear previous classes
        cell.classList.remove('x', 'o', 'available', 'winning');
        
        if (value === PLAYERS.HUMAN) {
            cell.classList.add('x');
            cell.textContent = 'X';
        } else if (value === PLAYERS.AI) {
            cell.classList.add('o');
            cell.textContent = 'O';
        } else {
            cell.classList.add('available');
            cell.textContent = '';
            
            // Show position number on hover if game is not over and it's player's turn
            if (!gameState.gameOver && gameState.player === PLAYERS.HUMAN && CONFIG.game.enableHoverNumbers) {
                cell.setAttribute('data-hover', index + 1);
            }
        }
        
        // Enable/disable clicks based on game state
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

async function checkMCPStatus() {
    try {
        const [capabilities, resources] = await Promise.all([
            getMCPCapabilities(),
            getMCPResources()
        ]);
        updateMCPStatus(capabilities.status, { ...capabilities, resources });
    } catch (error) {
        console.error('Error checking MCP status:', error);
        updateMCPStatus('error', { error: error.message });
    }
}

function updateMCPStatus(status, data) {
    // Only update status display if enabled in configuration
    if (!CONFIG.ui.showMCPStatus) {
        return;
    }
    
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

// Event Listeners Setup
// Only set up periodic status checking if enabled
if (CONFIG.mcp.enablePeriodicStatusCheck) {
    setInterval(async () => {
        await checkMCPStatus();
        await loadMCPResources(); // Refresh resources as well
    }, CONFIG.mcp.statusCheckInterval); // Check MCP status using configurable interval
}

document.addEventListener('visibilitychange', async function() {
    if (!document.hidden) {
        await checkMCPStatus();
        await loadMCPResources();
    }
});

document.addEventListener('keydown', function(e) {
    // Only handle shortcuts if enabled and chat input is not focused
    if (!CONFIG.game.enableKeyboardShortcuts || document.activeElement === chatInput) return;
    
    // Number keys 1-9 for quick moves (when game allows it)
    if (!gameState.gameOver && gameState.player === PLAYERS.HUMAN) {
        const num = parseInt(e.key);
        if (num >= 1 && num <= 9) {
            addUserMessage(num.toString());
            processChatInput(num.toString());
            e.preventDefault();
        }
    }
    
    // 'n' for new game
    if (e.key.toLowerCase() === 'n') {
        addUserMessage('n');
        processChatInput('new');
        e.preventDefault();
    }
    
    // Focus chat input on '/' key
    if (e.key === '/') {
        chatInput.focus();
        e.preventDefault();
    }
});

// Handle connection status
window.addEventListener('online', function() {
    updateGameStatus('🟢 Internet connection restored');
    checkMCPStatus();
});

window.addEventListener('offline', function() {
    updateGameStatus('🔴 Internet connection lost');
});

// Export functions for debugging (optional)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        makeMove,
        startNewGame,
        updateGameBoard,
        checkMCPStatus,
        resetGame,
        checkWinner,
        clearChat
    };
}
