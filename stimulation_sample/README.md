# Drug Discovery Mol* Viewer

A fully functional Node.js web application that integrates the RCSB Mol* 3D protein structure viewer for drug discovery visualization. This application displays protein structures with sequence annotations, binding sites, and interactive 3D visualization similar to the RCSB PDB viewer interface.

![Mol* Viewer](https://img.shields.io/badge/Mol*-Viewer-blue)
![Node.js](https://img.shields.io/badge/Node.js-18+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

### 3D Structure Visualization
- **Interactive 3D Viewer**: Full-featured Mol* viewer with rotation, zoom, and pan
- **Multiple Representation Modes**: Cartoon, Ball & Stick, and Surface views
- **Chain Coloring**: Different colors for different protein chains
- **Ligand Visualization**: Heme groups and other ligands clearly visible

### Sequence Annotations
- **Secondary Structure**: Helices and sheets displayed in sequence panel
- **Binding Sites**: HEM binding sites and metal coordination sites
- **UniProt Mapping**: Sequence annotations from UniProt
- **Hydropathy Plots**: Hydrophobicity visualization
- **Interactive Selection**: Click on sequence regions to highlight in 3D

### User Interface
- **Modern Dark Theme**: Optimized for scientific visualization
- **Responsive Design**: Works on desktop and tablet devices
- **Loading States**: Visual feedback during structure loading
- **Error Handling**: User-friendly error messages
- **Quick Load**: Pre-configured buttons for common structures

### Additional Features
- **PDB ID Input**: Load any structure from RCSB PDB
- **Screenshot Export**: Capture and download 3D views
- **Structure Information**: Display metadata (method, resolution, chains)
- **REST API**: Backend endpoints for programmatic access

## Installation

### Prerequisites
- Node.js 18 or higher
- npm or yarn package manager

### Setup

1. **Clone or download the project**:
```bash
cd drug-discovery-molstar-viewer
```

2. **Install dependencies**:
```bash
npm install
```

This will install:
- `express` - Web server framework
- `molstar` - Core Mol* 3D visualization library
- `@rcsb/rcsb-molstar` - RCSB-specific Mol* extensions

3. **Start the server**:
```bash
npm start
```

Or for development with auto-reload:
```bash
npm run dev
```

4. **Open in browser**:
Navigate to `http://localhost:3000`

## Project Structure

```
drug-discovery-molstar-viewer/
├── package.json              # Project dependencies and scripts
├── server.js                 # Express.js server configuration
├── README.md                 # This file
└── public/                   # Static files served to client
    ├── index.html            # Main application page
    ├── css/
    │   └── style.css         # Custom application styles
    └── js/
        └── molstar-init.js   # Mol* viewer initialization
```

## Usage

### Loading Structures

1. **Default Structure**: The application loads `4HHB` (Human Deoxyhemoglobin) by default
2. **Custom PDB ID**: Enter any valid PDB ID (e.g., `1UBQ`, `2LZM`) in the input field and click "Load Structure"
3. **Quick Load**: Use the quick load buttons in the left panel for common structures

### Visualization Controls

- **Cartoon**: Standard ribbon representation showing secondary structure
- **Ball & Stick**: Atomic detail with bonds shown as cylinders
- **Surface**: Solvent-accessible surface representation

### Interacting with the 3D View

- **Rotate**: Click and drag with left mouse button
- **Zoom**: Scroll wheel or right-click and drag
- **Pan**: Middle-click and drag
- **Select**: Click on atoms or residues to select them
- **Focus**: Double-click to center view on a specific region

### Sequence Panel

The left panel shows:
- Protein sequence with residue numbers
- Secondary structure elements (helices in pink)
- Binding sites (HEM as purple dots)
- Metal coordination sites
- Click on sequence regions to highlight in 3D

## API Endpoints

The backend provides several REST API endpoints:

### Health Check
```
GET /api/health
```
Returns server status and timestamp.

### Validate PDB ID
```
GET /api/validate-pdb/:pdbId
```
Validates PDB ID format (4 alphanumeric characters).

### Get PDB URLs
```
GET /api/pdb-url/:pdbId
```
Returns download URLs for PDB, mmCIF, and structure factor files.

### List Mol* Assets
```
GET /api/molstar-assets
```
Lists available Mol* library files.

## Configuration

### Mol* Viewer Options

The viewer is configured in `public/js/molstar-init.js`:

```javascript
const viewer = await molstar.Viewer.create(container, {
    layoutIsExpanded: true,        // Show expanded layout
    layoutShowControls: true,      // Show control panel
    layoutShowSequence: true,      // Show sequence panel
    layoutShowLog: false,          // Hide log panel
    layoutShowLeftPanel: true,     // Show left panel
    viewportShowExpand: true,      // Allow viewport expansion
    viewportShowControls: true,    // Show viewport controls
    viewportShowSettings: true,    // Show settings
});
```

### Customizing Colors

Chain colors are defined in `public/css/style.css`:

```css
:root {
    --chain-a: #ff6b35;    /* Orange - Chain A */
    --chain-b: #4ecdc4;    /* Teal - Chain B */
    --chain-c: #9b59b6;    /* Purple - Chain C */
    --chain-d: #e91e63;    /* Magenta - Chain D */
    --chain-hem: #8e44ad;  /* Purple - Heme */
}
```

## Example Structures

| PDB ID | Description | Features |
|--------|-------------|----------|
| 4HHB | Human Deoxyhemoglobin | 4 chains, heme groups, alpha/beta subunits |
| 1UBQ | Ubiquitin | Small protein, single chain |
| 2LZM | Lysozyme | Enzyme structure, binding site |
| 1MBN | Myoglobin | Oxygen storage, heme group |
| 3PQR | Insulin | Hormone, disulfide bonds |
| 7DFL | Spike Protein | Viral protein, large structure |

## Development

### Adding New Features

1. **Custom Annotations**: Extend the sequence panel by modifying the Mol* configuration
2. **New Visualization Modes**: Add buttons and handlers in `molstar-init.js`
3. **API Endpoints**: Add new routes in `server.js`

### Debugging

Enable verbose logging in the browser console:
```javascript
localStorage.setItem('molstar-debug', 'true');
```

### Performance Optimization

For large structures (>50,000 atoms):
- Use `cartoon` representation instead of `ball-stick`
- Disable shadows in viewport settings
- Reduce animation frame rate

## Troubleshooting

### Common Issues

**Viewer not loading**
- Check that `npm install` completed successfully
- Verify Mol* files are in `node_modules/molstar/build/`
- Check browser console for JavaScript errors

**Structure loading fails**
- Verify PDB ID format (4 characters, starts with digit)
- Check internet connection (structures loaded from RCSB)
- Try a different PDB ID to isolate the issue

**Slow performance**
- Switch to `cartoon` representation
- Close browser developer tools
- Use Chrome or Edge for best WebGL performance

### Browser Compatibility

- **Chrome/Edge**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support (macOS 10.15+)
- **Mobile**: Limited support (iPad recommended over phones)

## Architecture

### Frontend
- **Mol* Viewer**: WebGL-based 3D molecular visualization
- **RCSB Integration**: Fetches structures and annotations from RCSB PDB
- **Responsive UI**: CSS Grid and Flexbox layout

### Backend
- **Express.js**: Static file serving and API endpoints
- **Mol* Assets**: Serves library files from node_modules
- **Proxy**: Can be extended to proxy RCSB API requests

## Resources

- [Mol* Documentation](https://molstar.org/docs/)
- [RCSB PDB](https://www.rcsb.org/)
- [PDB File Format](https://www.wwpdb.org/documentation/file-format)
- [Mol* GitHub](https://github.com/molstar/molstar)

## License

MIT License - See LICENSE file for details

## Acknowledgments

- [Mol*](https://molstar.org/) - Developed by the PDBe, RCSB PDB, and Mol* team
- [RCSB PDB](https://www.rcsb.org/) - Protein Data Bank
- [Worldwide Protein Data Bank](https://www.wwpdb.org/) - wwPDB consortium

## Contributing

Contributions are welcome! Please ensure:
1. Code follows existing style conventions
2. Comments explain Mol* API usage
3. Error handling is comprehensive
4. Changes are tested across browsers

## Support

For issues related to:
- **This application**: Open an issue in the repository
- **Mol* viewer**: Visit [Mol* GitHub](https://github.com/molstar/molstar)
- **RCSB PDB data**: Contact [RCSB PDB Help](https://www.rcsb.org/help)

---

**Note**: This application is designed for computational drug discovery research and educational purposes. For production use in clinical or commercial settings, additional validation and compliance measures may be required.
