const express = require('express');
const path = require('path');

// Configuration
const config = {
    port: process.env.PORT || 5000
};

const app = express();

// Middleware
app.use(express.static(path.join(__dirname, 'public')));

const PORT = config.port;
app.listen(PORT, () => {
    console.log(`ChatTTT server running on port ${PORT}`);
    console.log(`Game available at: http://localhost:${PORT}`);
});
