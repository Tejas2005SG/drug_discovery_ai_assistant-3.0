/**
 * Drug Discovery Routes - NOVO-1 Integration
 * 
 * Provides API endpoints for:
 * - Drug discovery using NOVO-1 model
 * - Health checks
 * - Test endpoint
 * 
 * This route calls the Python Flask API that wraps the NOVO-1 model
 */

import express from 'express';
import axios from 'axios';

const router = express.Router();

// Python API configuration - now using python-backend on port 8000
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://127.0.0.1:8000';

/**
 * @route   GET /api/drug-discovery/health
 * @desc    Health check for both Node and Python APIs
 * @access  Public
 */
router.get('/health', async (req, res) => {
    try {
        // Check Python API health
        const pythonHealth = await axios.get(`${PYTHON_API_URL}/api/health`, {
            timeout: 5000
        });

        res.json({
            success: true,
            node_status: 'healthy',
            python_status: pythonHealth.data.status || 'unknown',
            system_initialized: pythonHealth.data.system_initialized || false,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(503).json({
            success: false,
            node_status: 'healthy',
            python_status: 'unreachable',
            error: 'Python API is not running',
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * @route   GET /api/drug-discovery/test
 * @desc    Test endpoint to verify integration
 * @access  Public
 */
router.get('/test', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API_URL}/api/test`, {
            timeout: 5000
        });

        res.json({
            success: true,
            message: 'NOVO-1 integration is working',
            python_response: response.data,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to connect to NOVO-1 API',
            details: error.message
        });
    }
});

/**
 * @route   POST /api/drug-discovery/discover
 * @desc    Main drug discovery endpoint - calls NOVO-1 model
 * @access  Public
 * 
 * Request body:
 * {
 *   "symptoms": ["fever", "cough", "fatigue"],
 *   "n_candidates": 5
 * }
 */
router.post('/discover', async (req, res) => {
    try {
        const { symptoms, n_candidates = 5 } = req.body;

        // Validate input
        if (!symptoms || !Array.isArray(symptoms) || symptoms.length === 0) {
            return res.status(400).json({
                success: false,
                error: 'Missing or invalid symptoms. Please provide an array of symptoms.'
            });
        }

        console.log(`[INFO] Drug discovery request: ${symptoms.join(', ')}`);

        // Call Python API
        const response = await axios.post(`${PYTHON_API_URL}/api/discover`, {
            symptoms,
            n_candidates
        }, {
            timeout: 120000, // 2 minute timeout for drug generation
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Return results
        res.json(response.data);

    } catch (error) {
        console.error('[ERROR] Drug discovery failed:', error.message);

        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                success: false,
                error: 'NOVO-1 API is not running. Please start the Python server.',
                details: 'Run: python api/novo1_api.py'
            });
        }

        if (error.response) {
            // Python API returned an error
            return res.status(error.response.status).json({
                success: false,
                error: error.response.data.error || 'Drug discovery failed',
                details: error.response.data
            });
        }

        res.status(500).json({
            success: false,
            error: 'Internal server error',
            details: error.message
        });
    }
});

export default router;
