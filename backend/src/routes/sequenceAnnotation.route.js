/**
 * Sequence Annotation Routes - Express Router
 * 
 * Provides API endpoints for:
 * - Mol* library asset information
 * - PDB ID validation
 * - PDB structure URL generation
 * - Health checks
 */

import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import axios from 'axios';

const router = express.Router();

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * @route   GET /api/sequence-annotation/health
 * @desc    Health check endpoint
 * @access  Public
 */
router.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'Sequence Annotation API'
    });
});

/**
 * @route   GET /api/sequence-annotation/molstar-assets
 * @desc    Get available Mol* assets
 * @access  Public
 */
router.get('/molstar-assets', (req, res) => {
    try {
        // Get the path to molstar build directory
        const molstarPath = path.join(process.cwd(), 'node_modules', 'molstar', 'build');
        
        // Check if directory exists
        if (!fs.existsSync(molstarPath)) {
            return res.status(404).json({
                success: false,
                error: 'Mol* assets not found',
                message: 'molstar package not installed in node_modules'
            });
        }

        const files = fs.readdirSync(molstarPath);
        res.json({
            success: true,
            assets: files,
            baseUrl: '/api/sequence-annotation/molstar',
            assetCount: files.length
        });
    } catch (error) {
        console.error('Error reading Mol* assets:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to read Mol* assets',
            details: error.message
        });
    }
});

/**
 * @route   GET /api/sequence-annotation/validate-pdb/:pdbId
 * @desc    Validate PDB ID format
 * @access  Public
 */
router.get('/validate-pdb/:pdbId', (req, res) => {
    const { pdbId } = req.params;
    
    // PDB ID format: 4 alphanumeric characters starting with a number (1-9)
    const pdbRegex = /^[1-9][A-Za-z0-9]{3}$/;
    const isValid = pdbRegex.test(pdbId);
    
    res.json({
        pdbId: pdbId.toUpperCase(),
        isValid,
        message: isValid 
            ? 'Valid PDB ID format' 
            : 'Invalid PDB ID format. Expected: 4 alphanumeric characters starting with 1-9 (e.g., 4HHB)'
    });
});

/**
 * @route   GET /api/sequence-annotation/pdb-url/:pdbId
 * @desc    Get RCSB PDB download URLs
 * @access  Public
 */
router.get('/pdb-url/:pdbId', (req, res) => {
    const { pdbId } = req.params;
    const upperPdbId = pdbId.toUpperCase();
    
    res.json({
        pdbId: upperPdbId,
        pdbUrl: `https://files.rcsb.org/download/${upperPdbId}.pdb`,
        cifUrl: `https://files.rcsb.org/download/${upperPdbId}.cif`,
        structFactUrl: `https://files.rcsb.org/download/${upperPdbId}-sf.cif`,
        rcsbEntryUrl: `https://www.rcsb.org/structure/${upperPdbId}`,
        rcsbDataApi: `https://data.rcsb.org/rest/v1/core/entry/${upperPdbId}`
    });
});

/**
 * @route   GET /api/sequence-annotation/structure-info/:pdbId
 * @desc    Get structure information from RCSB PDB API
 * @access  Public
 */
router.get('/structure-info/:pdbId', async (req, res) => {
    const { pdbId } = req.params;
    
    try {
        const response = await axios.get(`https://data.rcsb.org/rest/v1/core/entry/${pdbId.toUpperCase()}`);
        
        const data = response.data;
        
        // Extract relevant information
        const entities = data.rcsb_entry_container_identifiers?.polymer_entity_ids || [];
        const asymIds = data.rcsb_entry_container_identifiers?.asym_ids || [];
        const chains = asymIds.map((id, index) => String.fromCharCode(65 + index)).slice(0, asymIds.length);
        
        res.json({
            success: true,
            pdbId: pdbId.toUpperCase(),
            title: data.struct?.title?.[0] || 'Unknown Structure',
            depositionDate: data.rcsb_accession_info?.initial_release_date,
            resolution: data.rcsb_entry_info?.resolution_combined?.[0] || null,
            chains: chains.length > 0 ? chains : ['A'],
            entityCount: entities.length,
            asymIdCount: asymIds.length,
            experimentalMethod: data.exptl?.[0]?.method || 'Unknown'
        });
    } catch (error) {
        console.error('Error fetching structure info:', error);
        if (error.response?.status === 404) {
            return res.status(404).json({
                success: false,
                error: 'Structure not found',
                message: `PDB ID ${pdbId.toUpperCase()} not found in RCSB database`
            });
        }
        res.status(500).json({
            success: false,
            error: 'Failed to fetch structure information',
            details: error.message
        });
    }
});

/**
 * @route   GET /api/sequence-annotation/uniprot/:uniprotId
 * @desc    Get PDB structures mapped to UniProt ID
 * @access  Public
 */
router.get('/uniprot/:uniprotId', async (req, res) => {
    const { uniprotId } = req.params;
    const cleanId = uniprotId.trim().toUpperCase();
    
    try {
        // Call UniProt API using axios
        const response = await axios.get(`https://rest.uniprot.org/uniprotkb/${cleanId}.json`);
        
        const data = response.data;
        
        // Extract PDB cross-references
        const pdbReferences = [];
        if (data.uniProtKBCrossReferences) {
            data.uniProtKBCrossReferences.forEach(ref => {
                if (ref.database === 'PDB') {
                    pdbReferences.push({
                        id: ref.id,
                        method: ref.properties?.find(p => p.key === 'method')?.value || 'Unknown',
                        resolution: ref.properties?.find(p => p.key === 'resolution')?.value || null,
                        chains: ref.properties?.find(p => p.key === 'chains')?.value || null
                    });
                }
            });
        }
        
        // Sort by resolution (prefer higher resolution = lower number)
        pdbReferences.sort((a, b) => {
            const resA = parseFloat(a.resolution) || 999;
            const resB = parseFloat(b.resolution) || 999;
            return resA - resB;
        });
        
        // Extract protein info
        const proteinInfo = {
            proteinName: data.proteinDescription?.recommendedName?.fullName?.value || 'Unknown Protein',
            organism: data.organism?.scientificName || 'Unknown Organism',
            sequenceLength: data.sequence?.length || 0,
            function: data.comments?.find(c => c.commentType === 'FUNCTION')?.texts?.[0]?.value || null,
            gene: data.genes?.[0]?.geneName?.value || null
        };
        
        res.json({
            success: true,
            uniprotId: cleanId,
            proteinInfo,
            pdbStructures: pdbReferences,
            bestStructure: pdbReferences[0] || null,
            totalStructures: pdbReferences.length
        });
    } catch (error) {
        console.error('Error fetching UniProt data:', error);
        if (error.response?.status === 404) {
            return res.status(404).json({
                success: false,
                error: 'UniProt ID not found',
                message: `UniProt ID ${cleanId} not found`
            });
        }
        res.status(500).json({
            success: false,
            error: 'Failed to fetch UniProt data',
            details: error.message
        });
    }
});

/**
 * @route   GET /api/sequence-annotation/polymer-entity/:pdbId/:entityId
 * @desc    Get polymer entity details (sequence length, etc.)
 * @access  Public
 */
router.get('/polymer-entity/:pdbId/:entityId', async (req, res) => {
    const { pdbId, entityId } = req.params;
    
    try {
        const response = await axios.get(`https://data.rcsb.org/rest/v1/core/polymer_entity/${pdbId.toUpperCase()}/${entityId}`);
        
        const data = response.data;
        
        res.json({
            success: true,
            pdbId: pdbId.toUpperCase(),
            entityId,
            sequenceLength: data.entity_poly?.rcsb_sample_sequence_length || 
                           data.entity_poly?.sequence_length || 0,
            sequence: data.entity_poly?.sequence?.trim() || null,
            type: data.entity_poly?.type || 'Unknown'
        });
    } catch (error) {
        console.error('Error fetching polymer entity:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch polymer entity',
            details: error.message
        });
    }
});

export default router;
