/**
 * Drug Discovery Mol* Viewer - Main Application
 * 
 * This module initializes and manages the RCSB Mol* 3D protein structure viewer
 * using the RCSB PDB implementation for advanced features.
 */

// ============================================
// Global State Management
// ============================================

const AppState = {
    currentPdbId: '4HHB',
    viewer: null,
    isLoading: false,
    currentRepresentation: 'cartoon',
    structureInfo: null,
    viewerReady: false
};

// ============================================
// DOM Element References
// ============================================

const DOM = {
    pdbInput: document.getElementById('pdb-input'),
    loadPdbBtn: document.getElementById('load-pdb-btn'),
    molstarContainer: document.getElementById('molstar-container'),
    loadingOverlay: document.getElementById('loading-overlay'),
    loadingPdbId: document.getElementById('loading-pdb-id'),
    errorContainer: document.getElementById('error-container'),
    errorText: document.getElementById('error-text'),
    errorClose: document.getElementById('error-close'),
    statusMessage: document.getElementById('status-message'),
    viewCartoon: document.getElementById('view-cartoon'),
    viewBallStick: document.getElementById('view-ball-stick'),
    viewSurface: document.getElementById('view-surface'),
    exportBtn: document.getElementById('export-btn'),
    infoPdbId: document.getElementById('info-pdb-id'),
    infoTitle: document.getElementById('info-title'),
    infoMethod: document.getElementById('info-method'),
    infoResolution: document.getElementById('info-resolution'),
    infoChains: document.getElementById('info-chains'),
    quickLoadButtons: document.querySelectorAll('.quick-load button')
};

// ============================================
// Utility Functions
// ============================================

function isValidPdbId(pdbId) {
    const pdbRegex = /^[1-9][A-Za-z0-9]{3}$/;
    return pdbRegex.test(pdbId);
}

function showLoading(pdbId) {
    AppState.isLoading = true;
    DOM.loadingPdbId.textContent = pdbId.toUpperCase();
    DOM.loadingOverlay.classList.remove('hidden');
    DOM.statusMessage.textContent = `Loading ${pdbId.toUpperCase()}...`;
}

function hideLoading() {
    AppState.isLoading = false;
    DOM.loadingOverlay.classList.add('hidden');
    DOM.statusMessage.textContent = 'Ready';
}

function showError(message) {
    DOM.errorText.textContent = message;
    DOM.errorContainer.classList.remove('hidden');
    DOM.statusMessage.textContent = 'Error';
    setTimeout(() => hideError(), 5000);
}

function hideError() {
    DOM.errorContainer.classList.add('hidden');
}

function ensureProperDisplay() {
    // Force viewer container to have dark background
    const container = document.getElementById('molstar-container');
    if (container) {
        container.style.background = '#0f172a';
    }

    // Try to set viewer background color programmatically
    if (AppState.viewer) {
        try {
            const plugin = AppState.viewer.getPlugin();
            if (plugin) {
                // Set canvas background using Mol* API if available
                if (plugin.canvas3d) {
                    plugin.canvas3d.setProps({
                        renderer: {
                            backgroundColor: 0x0F172A // Match --bg-primary (#0f172a)
                        }
                    });
                }

                // Force canvas elements to have the right background CSS as well
                const canvasElements = container.querySelectorAll('canvas');
                canvasElements.forEach(canvas => {
                    canvas.style.background = '#0f172a';
                });
            }
        } catch (e) {
            console.warn('Could not set display properties:', e);
        }
    }
}

function updateStructureInfo(info) {
    DOM.infoPdbId.textContent = info.pdbId || AppState.currentPdbId;
    DOM.infoTitle.textContent = info.title || 'Unknown';
    DOM.infoMethod.textContent = info.method || '-';
    DOM.infoResolution.textContent = info.resolution || '-';
    DOM.infoChains.textContent = info.chains || '-';
}

// ============================================
// Mol* Viewer Initialization
// ============================================

async function waitForRcsbMolstar(timeoutMs = 15000) {
    const checkInterval = 100;
    const maxAttempts = Math.floor(timeoutMs / checkInterval);

    console.log('Waiting for rcsbMolstar library to load...');

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        // Check both direct and window scope
        if (typeof rcsbMolstar !== 'undefined' || window.rcsbMolstar !== undefined) {
            const lib = rcsbMolstar || window.rcsbMolstar;
            if (lib && lib.Viewer) {
                console.log('rcsbMolstar found after', attempt * checkInterval, 'ms');
                return lib;
            }
        }

        await new Promise(resolve => setTimeout(resolve, checkInterval));
    }

    console.error('Timeout waiting for rcsbMolstar library');
    return null;
}

async function loadLibraryWithRetry(maxRetries = 3) {
    let lastError = null;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        console.log(`Attempt ${attempt}/${maxRetries} to load rcsb-molstar...`);

        // Check if already loaded
        if (typeof rcsbMolstar !== 'undefined' && rcsbMolstar.Viewer) {
            console.log('Library already loaded');
            return rcsbMolstar;
        }

        // Try to load from CDN if local fails
        if (attempt > 1) {
            try {
                await new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = `https://cdn.jsdelivr.net/npm/@rcsb/rcsb-molstar@2.14.2/build/dist/viewer/rcsb-molstar.js`;
                    script.onload = () => {
                        console.log('CDN load successful');
                        setTimeout(resolve, 1000);
                    };
                    script.onerror = () => {
                        console.error('CDN load failed');
                        resolve(); // Resolve anyway
                    };
                    document.head.appendChild(script);
                });
            } catch (e) {
                lastError = e;
            }
        }

        // Wait and check again
        await new Promise(resolve => setTimeout(resolve, 1000));

        if (typeof rcsbMolstar !== 'undefined' && rcsbMolstar.Viewer) {
            console.log(`Attempt ${attempt} successful`);
            return rcsbMolstar;
        }
    }

    throw new Error(`Failed to load rcsb-molstar after ${maxRetries} attempts. Last error: ${lastError?.message || 'Unknown'}`);
}

async function initializeMolstarViewer() {
    try {
        console.log('Initializing RCSB Mol* viewer...');

        // Wait for library to load with retry logic
        const library = await loadLibraryWithRetry(3);

        if (!library || !library.Viewer) {
            throw new Error('rcsbMolstar or Viewer not available after all attempts');
        }

        console.log('rcsbMolstar library loaded successfully');
        console.log('Viewer constructor:', typeof library.Viewer);

        const container = document.getElementById('molstar-container');
        if (!container) {
            throw new Error('Element #molstar-container not found in DOM.');
        }

        // Initialize using the RCSB Molstar wrapper
        const viewer = new library.Viewer('molstar-container', {
            showImportControls: false,
            showSessionControls: false,
            layoutShowLog: false,
            layoutShowControls: false, // Hide Mol* controls for cleaner UI
            showMembraneOrientationPreset: false,
            detachedFromSierra: true,
            manualReset: false
        });

        AppState.viewer = viewer;
        AppState.viewerReady = true;
        console.log('RCSB Mol* viewer initialized successfully');

        // Ensure proper display settings
        ensureProperDisplay();

        // Load default structure
        try {
            await loadPdbStructure(AppState.currentPdbId);
        } catch (e) {
            console.warn("Initial structure load failed", e);
        }

        return true;

    } catch (error) {
        console.error('Failed to initialize Mol* viewer:', error);
        showError(`Init Error: ${error.message}`);
        return false;
    }
}

// ============================================
// Structure Loading Functions
// ============================================

async function loadPdbStructure(pdbId) {
    if (AppState.isLoading) return;

    const upperPdbId = pdbId.toUpperCase();
    if (!isValidPdbId(upperPdbId)) {
        showError(`Invalid PDB ID format: ${upperPdbId}`);
        return;
    }

    if (!AppState.viewer) {
        console.warn('Viewer not initialized, attempting re-initialization...');
        const success = await initializeMolstarViewer();
        if (!success || !AppState.viewer) {
            console.error("Initialization returned failure");
            return;
        }
    }

    showLoading(upperPdbId);

    try {
        console.log(`Loading PDB structure: ${upperPdbId}`);

        // Try standard RCSB load first with explicit representation
        try {
            if (typeof AppState.viewer.loadPdbId === 'function') {
                await AppState.viewer.loadPdbId(upperPdbId, {
                    // Apply cartoon representation with proper coloring
                    representation: 'cartoon',
                    coloring: {
                        scheme: 'chain-id'  // Color by chain
                    }
                });

                // Ensure viewer has proper background color
                ensureProperDisplay();
            } else {
                throw new Error('loadPdbId method not available');
            }
        } catch (loadError) {
            console.warn('Standard loadPdbId failed, trying direct URL load...', loadError);

            // Fallback: Load directly from RCSB files with explicit styling
            const fileUrl = `https://files.rcsb.org/download/${upperPdbId}.cif`;

            if (AppState.viewer && typeof AppState.viewer.loadStructureFromUrl === 'function') {
                await AppState.viewer.loadStructureFromUrl(fileUrl, 'mmcif', false, {
                    representation: 'cartoon',
                    coloring: {
                        scheme: 'chain-id'
                    }
                });

                ensureProperDisplay();
            } else {
                throw new Error("Viewer methods not available after load failure");
            }
        }

        AppState.currentPdbId = upperPdbId;
        DOM.pdbInput.value = upperPdbId;

        // Reset camera to focus on the newly loaded structure
        try {
            const plugin = AppState.viewer.getPlugin();
            if (plugin) {
                // Small delay to ensure structure is fully processed before centering
                setTimeout(() => {
                    plugin.managers.camera.reset();
                    // Double check background
                    ensureProperDisplay();

                    // Try to also focus on the structure manager selection
                    try {
                        const data = plugin.managers.structure.hierarchy.current.structures[0];
                        if (data) {
                            plugin.managers.camera.focusRenderObjects(data.representations.map(r => r.representation.renderObjects).reduce((a, b) => a.concat(b), []));
                        }
                    } catch (e) { }
                }, 800);
            }
        } catch (cameraError) {
            console.warn('Could not reset camera:', cameraError);
        }

        await fetchStructureInfo(upperPdbId);

        console.log(`Successfully loaded ${upperPdbId}`);
        DOM.statusMessage.textContent = `Loaded ${upperPdbId}`;

    } catch (error) {
        console.error(`Failed to load ${upperPdbId}:`, error);
        showError(`Failed to load ${upperPdbId}: ${error.message || 'Network issue or structure not found'}`);
    } finally {
        hideLoading();
    }
}

async function fetchStructureInfo(pdbId) {
    try {
        const response = await fetch(`https://data.rcsb.org/rest/v1/core/entry/${pdbId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        const info = {
            pdbId: pdbId,
            title: data.struct?.title?.[0] || 'Unknown',
            method: data.exptl?.[0]?.method || 'Unknown',
            resolution: data.rcsb_entry_info?.resolution_combined?.[0]
                ? `${data.rcsb_entry_info.resolution_combined[0]} Å`
                : 'N/A',
            chains: data.rcsb_entry_info?.polymer_entity_count_protein
                ? `${data.rcsb_entry_info.polymer_entity_count_protein} protein chains`
                : 'Unknown'
        };

        AppState.structureInfo = info;
        updateStructureInfo(info);
    } catch (error) {
        console.warn('Failed to fetch structure info:', error);
    }
}

// ============================================
// Visualization Presets
// ============================================

async function applyRepresentation(representation) {
    if (!AppState.viewer) return;

    updateViewButtons(representation);
    AppState.currentRepresentation = representation;

    try {
        const plugin = AppState.viewer.getPlugin();
        if (!plugin) return;

        const structure = plugin.managers.structure.hierarchy.current.structures[0];
        if (!structure) return;

        switch (representation) {
            case 'cartoon':
                await plugin.managers.structure.component.applyPreset(structure, 'polymer-cartoon');
                break;
            case 'ball-stick':
                await plugin.managers.structure.component.applyPreset(structure, 'ball-and-stick');
                break;
            case 'surface':
                await plugin.managers.structure.component.applyPreset(structure, 'molecular-surface');
                break;
        }

        // Ensure background stays dark after representation change
        ensureProperDisplay();

        // Refocus camera on the new representation
        setTimeout(() => {
            plugin.managers.camera.reset();
        }, 300);
    } catch (error) {
        console.warn('Failed to apply representation:', error);
    }
}

function updateViewButtons(activeRepresentation) {
    DOM.viewCartoon.classList.toggle('active', activeRepresentation === 'cartoon');
    DOM.viewBallStick.classList.toggle('active', activeRepresentation === 'ball-stick');
    DOM.viewSurface.classList.toggle('active', activeRepresentation === 'surface');
}

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    DOM.loadPdbBtn.addEventListener('click', () => loadPdbStructure(DOM.pdbInput.value.trim()));
    DOM.pdbInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loadPdbStructure(DOM.pdbInput.value.trim());
    });

    DOM.viewCartoon.addEventListener('click', () => applyRepresentation('cartoon'));
    DOM.viewBallStick.addEventListener('click', () => applyRepresentation('ball-stick'));
    DOM.viewSurface.addEventListener('click', () => applyRepresentation('surface'));

    DOM.exportBtn.addEventListener('click', async () => {
        try {
            const plugin = AppState.viewer?.getPlugin();
            if (plugin?.helpers?.viewportScreenshot?.download) {
                plugin.helpers.viewportScreenshot.download();
            }
        } catch (error) {
            console.warn('Export failed:', error);
        }
    });

    DOM.errorClose.addEventListener('click', hideError);
    DOM.quickLoadButtons.forEach(button => {
        button.addEventListener('click', (e) => loadPdbStructure(e.target.dataset.pdb));
    });
}

// ============================================
// Initialization
// ============================================

async function initializeApp() {
    setupEventListeners();

    // Wait for DOM and library to be ready
    await new Promise(resolve => setTimeout(resolve, 500));

    await initializeMolstarViewer();
}

// Start application
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    // DOM already loaded
    initializeApp();
}

window.MolstarApp = {
    loadStructure: loadPdbStructure,
    applyRepresentation: applyRepresentation,
    getState: () => ({ ...AppState }),
    reinitialize: initializeMolstarViewer,
    waitForRcsbMolstar: waitForRcsbMolstar
};
