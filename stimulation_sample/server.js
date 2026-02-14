/**
 * Drug Discovery Mol* Viewer - Express Server
 * 
 * This server provides:
 * - Static file serving from the 'public' directory
 * - Mol* library files from node_modules
 * - API endpoints for structure loading
 * - Main application routing
 */

const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware for parsing JSON bodies
app.use(express.json());

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, 'public')));

// Serve Mol* library files from node_modules
// This makes the Mol* viewer JavaScript and CSS available to the client
app.use('/molstar', express.static(path.join(__dirname, 'node_modules/molstar/build')));

// Serve RCSB Mol* specific files
app.use('/rcsb-molstar', express.static(path.join(__dirname, 'node_modules/@rcsb/rcsb-molstar/build')));

// Serve RCSB Saguaro 3D files
app.use('/rcsb-saguaro-3d', express.static(path.join(__dirname, 'node_modules/@rcsb/rcsb-saguaro-3d/build')));

// API endpoint to get available Mol* assets
app.get('/api/molstar-assets', (req, res) => {
    const molstarPath = path.join(__dirname, 'node_modules/molstar/build');

    try {
        const files = fs.readdirSync(molstarPath);
        res.json({
            success: true,
            assets: files,
            baseUrl: '/molstar'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to read Mol* assets',
            details: error.message
        });
    }
});

// API endpoint to validate PDB ID format
app.get('/api/validate-pdb/:pdbId', (req, res) => {
    const { pdbId } = req.params;

    // PDB ID format: 4 alphanumeric characters
    const pdbRegex = /^[1-9][A-Za-z0-9]{3}$/;
    const isValid = pdbRegex.test(pdbId);

    res.json({
        pdbId: pdbId.toUpperCase(),
        isValid,
        message: isValid ? 'Valid PDB ID format' : 'Invalid PDB ID format. Expected: 4 alphanumeric characters (e.g., 4HHB)'
    });
});

// API endpoint to get RCSB PDB download URL
app.get('/api/pdb-url/:pdbId', (req, res) => {
    const { pdbId } = req.params;
    const upperPdbId = pdbId.toUpperCase();

    res.json({
        pdbId: upperPdbId,
        pdbUrl: `https://files.rcsb.org/download/${upperPdbId}.pdb`,
        cifUrl: `https://files.rcsb.org/download/${upperPdbId}.cif`,
        structFactUrl: `https://files.rcsb.org/download/${upperPdbId}-sf.cif`
    });
});

// Main application route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'Drug Discovery Mol* Viewer'
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        details: err.message
    });
});

// Start the server
app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('Drug Discovery Mol* Viewer Server');
    console.log('='.repeat(60));
    console.log(`Server running at: http://localhost:${PORT}`);
    console.log(`Mol* assets served from: /molstar`);
    console.log(`RCSB Mol* served from: /rcsb-molstar`);
    console.log(`RCSB Saguaro 3D served from: /rcsb-saguaro-3d`);
    console.log('='.repeat(60));
});

module.exports = app;
