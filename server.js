const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3000;
const PYTHON_API_URL = 'http://localhost:5000';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Proxy requests to Python API
app.use('/api', async (req, res) => {
  try {
    const response = await axios({
      method: req.method,
      url: `${PYTHON_API_URL}/api${req.path}`,
      data: req.body,
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 10000 // 10 second timeout
    });
    res.json(response.data);
  } catch (error) {
    console.error('API Error:', error.message);
    if (error.code === 'ECONNREFUSED') {
      res.status(503).json({ 
        error: 'Optimization engine is starting up',
        details: 'Please wait a moment and try again'
      });
    } else if (error.response && error.response.status === 404) {
      res.status(404).json({ 
        error: 'API endpoint not found',
        details: `Endpoint ${req.path} not found on optimization engine`
      });
    } else {
      res.status(500).json({ 
        error: 'Failed to connect to optimization engine',
        details: error.message 
      });
    }
  }
});

// Serve the main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    python_api: PYTHON_API_URL
  });
});

app.listen(PORT, () => {
  console.log(`🌐 Frontend server running on http://localhost:${PORT}`);
  console.log(`📡 Proxying to Python API: ${PYTHON_API_URL}`);
});
