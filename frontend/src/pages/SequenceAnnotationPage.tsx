import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { toast } from 'sonner';
import { Dna, Loader2, ZoomIn, ZoomOut, Palette, Box, X, HelpCircle, Info, Search, Database, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

// Track Definitions
interface Track {
  id: string;
  label: string;
  type: string;
}

interface StructureInfo {
  pdbId: string;
  title: string;
  sequenceLength: number;
  chains: string[];
  resolution: number | null;
  organism?: string;
}

interface AppState {
  currentPdbId: string;
  currentUniprotId: string;
  currentChain: string;
  viewer: any;
  viewerReady: boolean;
  sequenceLength: number;
  selectedPosition: number | null;
  hoverPosition: number | null;
  isLoading: boolean;
  structureInfo: StructureInfo | null;
}

interface OutlierData {
  hasOutlier: boolean;
  height: number;
  isHigh: boolean;
}

interface HydropathyData {
  value: number;
  isPositive: boolean;
  height: number;
}

const tracks: Track[] = [
  { id: 'chain', label: 'CHAIN', type: 'chain' },
  { id: 'uniprot', label: 'UNIPROT', type: 'uniprot' },
  { id: 'secondary', label: 'SECONDARY STRUCTURE', type: 'secondary' },
  { id: 'plane', label: 'PLANE OUTLIERS', type: 'outliers' },
  { id: 'chiral', label: 'CHIRAL OUTLIERS', type: 'chiral' },
  { id: 'atomic', label: 'ATOMIC CLASHES', type: 'atomic' },
  { id: 'symm', label: 'SYMM CLASHES', type: 'symm' },
  { id: 'angle', label: 'ANGLE OUTLIERS', type: 'angle' },
  { id: 'bond', label: 'BOND OUTLIERS', type: 'bond' },
  { id: 'binding-hem', label: 'BINDING SITE HEM', type: 'binding' },
  { id: 'metal-hem', label: 'METAL COORDINATION HEM', type: 'metal' },
  { id: 'binding-a', label: 'BINDING CHAIN A', type: 'binding-chain' },
  { id: 'binding-b', label: 'BINDING CHAIN B', type: 'binding-chain' },
  { id: 'binding-d', label: 'BINDING CHAIN D', type: 'binding-chain' },
  { id: 'buried', label: 'BURIED RESIDUES', type: 'buried' },
  { id: 'hydropathy', label: 'HYDROPATHY', type: 'hydropathy' },
  { id: 'disorder', label: 'DISORDER', type: 'disorder' },
  { id: 'disordered-binding', label: 'DISORDERED BINDING', type: 'disordered-binding' },
  { id: 'pfam', label: 'PFAM', type: 'domain' },
  { id: 'cath', label: 'CATH', type: 'domain' },
  { id: 'scop', label: 'SCOP', type: 'domain' },
  { id: 'ecod', label: 'ECOD', type: 'domain' },
  { id: 'molecule-processing', label: 'MOLECULE PROCESSING', type: 'processing' }
];

// Generate stable outlier data (not using Math.random on every render)
const generateOutlierData = (length: number): OutlierData[] => {
  return Array.from({ length }, (_, i) => {
    const pos = i + 1;
    // Use a pseudo-random but deterministic approach based on position
    const pseudoRandom1 = Math.sin(pos * 12.9898) * 43758.5453 - Math.floor(Math.sin(pos * 12.9898) * 43758.5453);
    const pseudoRandom2 = Math.cos(pos * 78.233) * 43758.5453 - Math.floor(Math.cos(pos * 78.233) * 43758.5453);
    
    const hasOutlier = pseudoRandom1 < 0.15 || (pos > 40 && pos < 50) || (pos > 80 && pos < 85);
    const height = hasOutlier ? pseudoRandom2 * 80 + 20 : pseudoRandom1 * 10 + 2;
    const isHigh = height > 60;
    
    return { hasOutlier, height, isHigh };
  });
};

const generateAtomicClashData = (length: number): OutlierData[] => {
  return Array.from({ length }, (_, i) => {
    const pos = i + 1;
    const pseudoRandom1 = Math.sin(pos * 45.1234) * 43758.5453 - Math.floor(Math.sin(pos * 45.1234) * 43758.5453);
    const pseudoRandom2 = Math.cos(pos * 23.5678) * 43758.5453 - Math.floor(Math.cos(pos * 23.5678) * 43758.5453);
    
    const hasClash = pseudoRandom1 < 0.08;
    const height = hasClash ? pseudoRandom2 * 60 + 20 : pseudoRandom1 * 8 + 2;
    
    return { hasOutlier: hasClash, height, isHigh: false };
  });
};

const generateBondOutlierData = (length: number): OutlierData[] => {
  return Array.from({ length }, (_, i) => {
    const pos = i + 1;
    const pseudoRandom1 = Math.sin(pos * 67.8901) * 43758.5453 - Math.floor(Math.sin(pos * 67.8901) * 43758.5453);
    const pseudoRandom2 = Math.cos(pos * 34.5678) * 43758.5453 - Math.floor(Math.cos(pos * 34.5678) * 43758.5453);
    
    const hasOutlier = pseudoRandom1 < 0.12;
    const height = hasOutlier ? pseudoRandom2 * 50 + 10 : pseudoRandom1 * 5 + 1;
    
    return { hasOutlier, height, isHigh: false };
  });
};

const generateHydropathyData = (length: number): HydropathyData[] => {
  return Array.from({ length }, (_, i) => {
    const pos = i + 1;
    // Use deterministic pseudo-random
    const pseudoRandom = Math.sin(pos * 89.0123) * 43758.5453 - Math.floor(Math.sin(pos * 89.0123) * 43758.5453);
    const value = Math.sin(pos * 0.2) * 0.5 + pseudoRandom * 0.3;
    const height = Math.abs(value) * 40;
    const isPositive = value > 0;
    
    return { value, isPositive, height };
  });
};

// Sample Structure Data for Landing Page
const SAMPLE_STRUCTURES = [
  { uniprotId: 'P69905', pdbId: '4HHB', name: 'Hemoglobin subunit alpha', organism: 'Human' },
  { uniprotId: 'P68871', pdbId: '4HHB', name: 'Hemoglobin subunit beta', organism: 'Human' },
  { uniprotId: 'P00519', pdbId: '1A5U', name: 'ABL1 Tyrosine Kinase', organism: 'Human' },
  { uniprotId: 'P04637', pdbId: '2OCJ', name: 'p53 Tumor Suppressor', organism: 'Human' },
];

export function SequenceAnnotationPage() {
  const [showLanding, setShowLanding] = useState(true);
  const [uniprotInput, setUniprotInput] = useState('');
  const [isLoadingStructure, setIsLoadingStructure] = useState(false);
  
  const [appState, setAppState] = useState<AppState>({
    currentPdbId: '4HHB',
    currentUniprotId: '',
    currentChain: 'A',
    viewer: null,
    viewerReady: false,
    sequenceLength: 141,
    selectedPosition: null,
    hoverPosition: null,
    isLoading: false,
    structureInfo: null
  });

  const [tooltip, setTooltip] = useState({ show: false, x: 0, y: 0, content: '' });
  const [indicatorPosition, setIndicatorPosition] = useState<number | null>(null);
  const [currentColorTheme, setCurrentColorTheme] = useState('chain-id');
  const [measurementMode, setMeasurementMode] = useState(false);

  const viewerContainerRef = useRef<HTMLDivElement>(null);
  const tracksContainerRef = useRef<HTMLDivElement>(null);
  const rcsbViewerRef = useRef<any>(null);
  const highlightComponentRef = useRef<any>(null);

  // Memoize generated track data so it doesn't change on re-renders
  const outlierData = useMemo(() => generateOutlierData(appState.sequenceLength), [appState.sequenceLength]);
  const atomicClashData = useMemo(() => generateAtomicClashData(appState.sequenceLength), [appState.sequenceLength]);
  const bondOutlierData = useMemo(() => generateBondOutlierData(appState.sequenceLength), [appState.sequenceLength]);
  const hydropathyData = useMemo(() => generateHydropathyData(appState.sequenceLength), [appState.sequenceLength]);

  // Helper: Generate Ruler
  const generateRuler = useCallback(() => {
    const length = appState.sequenceLength;
    const step = 20;
    const items = [];
    
    for (let i = 0; i <= length; i += step) {
      const left = (i / length) * 100;
      items.push(
        <div key={i} className="absolute" style={{ left: `${left}%` }}>
          <span className="text-[11px] text-gray-600">{i}</span>
          <div className="absolute bottom-0 w-px h-1.5 bg-gray-400" />
        </div>
      );
    }
    return items;
  }, [appState.sequenceLength]);

  // Helper: Generate Track Content
  const generateTrackContent = (track: Track) => {
    const length = appState.sequenceLength;

    switch (track.type) {
      case 'chain':
        return (
          <div className="h-5 bg-purple-300 rounded flex items-center px-2 text-xs font-medium text-gray-800">
            CHAIN {appState.currentChain}
          </div>
        );

      case 'uniprot':
        return (
          <div className="h-5 bg-indigo-300 rounded flex items-center px-2 text-xs font-medium text-gray-800">
            {appState.currentUniprotId}
          </div>
        );

      case 'secondary':
        return generateSecondaryStructure(length);

      case 'outliers':
        return generateOutliers(length, outlierData);

      case 'chiral':
        return generateChiralOutliers(length);

      case 'atomic':
        return generateAtomicClashes(length, atomicClashData);

      case 'symm':
        return generateSymmClashes(length);

      case 'angle':
        return generateOutliers(length, outlierData);

      case 'bond':
        return generateBondOutliers(length, bondOutlierData);

      case 'binding':
        return generateBindingSites(length, 'hem');

      case 'metal':
        return generateMetalCoordination(length);

      case 'binding-chain':
        return generateChainBinding(length, track.id);

      case 'buried':
        return generateBuriedResidues(length);

      case 'hydropathy':
        return generateHydropathy(length, hydropathyData);

      case 'disorder':
        return (
          <div className="h-7 rounded opacity-60" style={{ width: '60%', background: 'linear-gradient(to right, #a5b4fc 0%, #a5b4fc 60%, transparent 100%)' }} />
        );

      case 'disordered-binding':
        return (
          <div className="h-7 rounded opacity-60" style={{ width: '80%', background: 'linear-gradient(to right, #a5b4fc 0%, transparent 100%)' }} />
        );

      case 'domain':
        return generateDomains(length, track.id);

      case 'processing':
        return (
          <div className="h-5 bg-red-200 rounded flex items-center px-2 text-[10px] font-medium text-gray-800" style={{ width: '100%' }}>
            Processed
          </div>
        );

      default:
        return null;
    }
  };

  const generateSecondaryStructure = (length: number) => {
    const helices = [
      [3, 18], [20, 35], [52, 57], [58, 77], [80, 89], [96, 112], [119, 136]
    ];

    return (
      <div className="flex items-center h-6 relative">
        {helices.map(([start, end], idx) => {
          const left = ((start - 1) / length) * 100;
          const width = ((end - start + 1) / length) * 100;
          return (
            <div
              key={idx}
              className="absolute h-4.5 bg-pink-300 rounded cursor-pointer hover:opacity-80 transition-opacity"
              style={{ left: `${left}%`, width: `${width}%` }}
              data-start={start}
              data-end={end}
              title={`Helix ${start}-${end}`}
              onClick={(e) => {
                e.stopPropagation();
                highlightResidue(start);
              }}
            />
          );
        })}
      </div>
    );
  };

  const generateOutliers = (length: number, data: OutlierData[]) => {
    return (
      <div className="flex items-end h-6 gap-px">
        {data.map((item, i) => {
          const pos = i + 1;
          return (
            <div
              key={i}
              className={`flex-1 cursor-pointer transition-colors hover:bg-red-500 ${item.isHigh ? 'bg-red-500' : 'bg-red-300'}`}
              style={{ height: `${item.height}%` }}
              data-pos={pos}
              title={`Position ${pos}: ${item.height.toFixed(1)}%`}
              onClick={(e) => {
                e.stopPropagation();
                highlightResidue(pos);
              }}
            />
          );
        })}
      </div>
    );
  };

  const generateChiralOutliers = (length: number) => {
    return (
      <div className="flex items-end h-6 gap-px">
        {Array.from({ length }, (_, i) => {
          const pos = i + 1;
          const hasOutlier = pos === 62 || pos === 98;
          const height = hasOutlier ? 100 : 2;
          return (
            <div
              key={i}
              className={`flex-1 ${hasOutlier ? 'bg-red-500' : 'bg-red-200'}`}
              style={{ height: `${height}%` }}
              data-pos={pos}
              onClick={(e) => {
                e.stopPropagation();
                if (hasOutlier) highlightResidue(pos);
              }}
            />
          );
        })}
      </div>
    );
  };

  const generateAtomicClashes = (length: number, data: OutlierData[]) => {
    return (
      <div className="flex items-end h-6 gap-px">
        {data.map((item, i) => {
          const pos = i + 1;
          return (
            <div
              key={i}
              className="flex-1 bg-purple-300"
              style={{ height: `${item.height}%` }}
              data-pos={pos}
            />
          );
        })}
      </div>
    );
  };

  const generateSymmClashes = (length: number) => {
    return (
      <div className="flex items-end h-6 gap-px">
        {Array.from({ length }, (_, i) => {
          const pos = i + 1;
          const hasClash = pos === 76;
          const height = hasClash ? 100 : 2;
          return (
            <div
              key={i}
              className="flex-1 bg-teal-300"
              style={{ height: `${height}%` }}
              data-pos={pos}
            />
          );
        })}
      </div>
    );
  };

  const generateBondOutliers = (length: number, data: OutlierData[]) => {
    return (
      <div className="flex items-end h-6 gap-px">
        {data.map((item, i) => {
          const pos = i + 1;
          return (
            <div
              key={i}
              className="flex-1 bg-green-300"
              style={{ height: `${item.height}%` }}
              data-pos={pos}
            />
          );
        })}
      </div>
    );
  };

  const generateBindingSites = (length: number, type: string) => {
    const sites = [
      [26, 28], [42, 44], [58, 62], [65, 69], [98, 102], [132, 134]
    ];

    return (
      <div className="flex items-center h-6 gap-1">
        {sites.map(([start, end], idx) => (
          <div key={idx} className="flex gap-0.5">
            {Array.from({ length: end - start + 1 }, (_, i) => {
              const pos = start + i;
              return (
                <div
                  key={i}
                  className="w-2.5 h-2.5 bg-violet-500 rounded-full cursor-pointer hover:scale-125 transition-transform"
                  data-pos={pos}
                  title={`HEM binding site: ${pos}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    highlightResidue(pos);
                  }}
                />
              );
            })}
          </div>
        ))}
      </div>
    );
  };

  const generateMetalCoordination = (length: number) => {
    const sites = [63, 87];
    return (
      <div className="flex items-center h-6 gap-2">
        {sites.map((pos, idx) => (
          <div
            key={idx}
            className="w-2.5 h-2.5 bg-purple-300 rounded-full cursor-pointer hover:scale-125 transition-transform"
            data-pos={pos}
            title={`Metal coordination: ${pos}`}
            onClick={(e) => {
              e.stopPropagation();
              highlightResidue(pos);
            }}
          />
        ))}
      </div>
    );
  };

  const generateChainBinding = (length: number, id: string) => {
    const chain = id.split('-')[1];
    const sites = chain === 'a' ? [[30, 35], [95, 100]] :
                  chain === 'b' ? [[18, 23], [110, 115]] :
                  [[45, 50], [125, 130]];

    return (
      <div className="flex items-center h-6 gap-2">
        {sites.map(([start, end], idx) => (
          <div key={idx} className="flex gap-0.5">
            {Array.from({ length: end - start + 1 }, (_, i) => {
              const pos = start + i;
              return (
                <div
                  key={i}
                  className="w-2.5 h-2.5 bg-indigo-300 rounded-full cursor-pointer hover:scale-125 transition-transform"
                  data-pos={pos}
                  title={`Chain ${chain?.toUpperCase()} binding: ${pos}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    highlightResidue(pos);
                  }}
                />
              );
            })}
          </div>
        ))}
      </div>
    );
  };

  const generateBuriedResidues = (length: number) => {
    const buried = [5, 12, 18, 25, 32, 38, 45, 52, 58, 65, 72, 78, 85, 92, 98, 105, 112, 118, 125];
    return (
      <div className="flex items-center h-6 relative">
        {buried.map((pos, idx) => {
          const left = ((pos - 1) / length) * 100;
          return (
            <div
              key={idx}
              className="absolute w-1.5 h-4 bg-green-500 rounded cursor-pointer hover:bg-green-600"
              style={{ left: `${left}%` }}
              data-pos={pos}
              title={`Buried residue: ${pos}`}
              onClick={(e) => {
                e.stopPropagation();
                highlightResidue(pos);
              }}
            />
          );
        })}
      </div>
    );
  };

  const generateHydropathy = (length: number, data: HydropathyData[]) => {
    return (
      <div className="flex items-center h-7 relative">
        {data.map((item, i) => {
          const pos = i + 1;
          const left = ((pos - 1) / length) * 100;
          return (
            <div
              key={i}
              className={`absolute w-0.5 ${item.isPositive ? 'bg-red-400 rounded-t' : 'bg-blue-400 rounded-b'}`}
              style={{ 
                left: `${left}%`, 
                height: `${item.height}%`,
                ...(item.isPositive ? {} : { top: '50%' })
              }}
              data-pos={pos}
              data-value={item.value.toFixed(2)}
              title={`Position ${pos}: ${item.value.toFixed(2)}`}
            />
          );
        })}
      </div>
    );
  };

  const generateDomains = (length: number, type: string) => {
    const domains: Record<string, [string, number, number][]> = {
      'pfam': [['Globin', 3, 140]],
      'cath': [['3.10.320.10', 3, 140]],
      'scop': [['a.1.1.1', 3, 140]],
      'ecod': [['2013.001.0', 3, 140]]
    };

    const domainList = domains[type] || [];
    const colors: Record<string, string> = {
      'pfam': 'bg-red-200',
      'cath': 'bg-yellow-200',
      'scop': 'bg-gray-300',
      'ecod': 'bg-green-200'
    };

    return (
      <div className="flex items-center h-6 relative">
        {domainList.map(([name, start, end], idx) => {
          const left = ((start - 1) / length) * 100;
          const width = ((end - start + 1) / length) * 100;
          return (
            <div
              key={idx}
              className={`absolute h-4.5 ${colors[type]} rounded flex items-center px-1.5 text-[10px] font-medium text-gray-800`}
              style={{ left: `${left}%`, width: `${width}%` }}
              data-start={start}
              data-end={end}
            >
              {name}
            </div>
          );
        })}
      </div>
    );
  };

  // Viewer Functions
  const initializeViewer = async () => {
    try {
      if (!viewerContainerRef.current || typeof window === 'undefined') {
        return false;
      }

      // Check if rcsbMolstar is available
      const rcsbMolstar = (window as any).rcsbMolstar;
      if (!rcsbMolstar) {
        console.warn('Mol* library not available');
        toast.error('3D viewer library not loaded. Please refresh the page.');
        return false;
      }

      // Clear existing viewer
      if (rcsbViewerRef.current) {
        try {
          rcsbViewerRef.current.clear();
        } catch (e) {
          console.warn('Could not clear existing viewer:', e);
        }
      }

      // Create new viewer
      rcsbViewerRef.current = new rcsbMolstar.Viewer(viewerContainerRef.current.id, {
        showImportControls: false,
        showSessionControls: false,
        layoutShowLog: false,
        layoutShowControls: false,
        showMembraneOrientationPreset: false,
        detachedFromSierra: true,
        manualReset: false
      });

      await new Promise(resolve => setTimeout(resolve, 500));

      setAppState(prev => ({ ...prev, viewerReady: true }));

      // Load default structure
      await loadStructure(appState.currentPdbId);

      toast.success('3D viewer initialized successfully');
      return true;
    } catch (error) {
      console.error('Failed to initialize viewer:', error);
      toast.error('Failed to initialize 3D viewer');
      return false;
    }
  };

  const loadStructure = async (pdbId: string) => {
    try {
      if (!rcsbViewerRef.current) {
        throw new Error('Viewer not initialized');
      }

      setIsLoadingStructure(true);

      // Clear previous structure
      try {
        rcsbViewerRef.current.clear();
      } catch (e) {
        console.warn('Could not clear viewer:', e);
      }

      await new Promise(resolve => setTimeout(resolve, 300));

      // Load new structure
      await rcsbViewerRef.current.loadPdbId(pdbId, {
        representation: 'cartoon',
        coloring: { scheme: currentColorTheme }
      });

      setAppState(prev => ({ 
        ...prev, 
        currentPdbId: pdbId,
        isLoading: false 
      }));

      toast.success(`Structure ${pdbId} loaded successfully`);
    } catch (error) {
      console.error(`Failed to load structure ${pdbId}:`, error);
      toast.error(`Failed to load structure ${pdbId}`);
    } finally {
      setIsLoadingStructure(false);
    }
  };

  const highlightResidue = async (position: number) => {
    if (!rcsbViewerRef.current || appState.isLoading) return;

    try {
      setAppState(prev => ({ ...prev, isLoading: true }));

      // Use the RCSB API to focus on the residue - this automatically zooms
      await rcsbViewerRef.current.loadPdbId(appState.currentPdbId, {
        representation: 'cartoon',
        coloring: { scheme: currentColorTheme },
        props: {
          kind: 'feature',
          target: {
            labelAsymId: appState.currentChain,
            labelSeqId: position,
            authSeqId: position
          }
        }
      });

      setAppState(prev => ({ ...prev, selectedPosition: position, isLoading: false }));
      console.log('Successfully focused on residue', position);
    } catch (error) {
      console.warn('Failed to highlight residue:', error);
      setAppState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const clearHighlights = async () => {
    if (!rcsbViewerRef.current || appState.isLoading) return;

    try {
      setAppState(prev => ({ ...prev, isLoading: true }));

      // Reload structure without target to clear focus and show full structure
      await rcsbViewerRef.current.loadPdbId(appState.currentPdbId, {
        representation: 'cartoon',
        coloring: { scheme: currentColorTheme },
        props: {
          kind: 'standard'
        }
      });

      setAppState(prev => ({ ...prev, selectedPosition: null, isLoading: false }));
      console.log('Cleared highlights - showing full structure');
    } catch (error) {
      console.warn('Failed to clear highlights:', error);
      setAppState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const applyRepresentation = async (type: string) => {
    if (!rcsbViewerRef.current) return;

    try {
      const plugin = rcsbViewerRef.current.getPlugin();
      if (!plugin) return;

      const structure = plugin.managers.structure.hierarchy.current.structures[0];
      if (!structure) return;

      switch (type) {
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
    } catch (e) {
      console.warn('Failed to apply representation:', e);
    }
  };

  const toggleColorTheme = async () => {
    if (!rcsbViewerRef.current) return;

    const themes = ['chain-id', 'element-symbol', 'secondary-structure', 'molecule-type', 'residue-name'];
    const currentIndex = themes.indexOf(currentColorTheme);
    const newTheme = themes[(currentIndex + 1) % themes.length];

    try {
      await rcsbViewerRef.current.loadPdbId(appState.currentPdbId, {
        representation: 'cartoon',
        coloring: { scheme: newTheme }
      });
      setCurrentColorTheme(newTheme);
      toast.success(`Color theme: ${newTheme}`);
    } catch (e) {
      console.warn('Failed to change color theme:', e);
    }
  };

  const zoomCamera = (factor: number) => {
    if (!rcsbViewerRef.current) return;

    try {
      const plugin = rcsbViewerRef.current.getPlugin();
      if (plugin && plugin.canvas3d) {
        const camera = plugin.canvas3d.camera;
        const radius = camera.getRadius();
        camera.setRadius(radius * factor);
        console.log('Zoomed camera by factor:', factor);
      }
    } catch (e) {
      console.warn('Failed to zoom camera:', e);
    }
  };

  // Load from UniProt
  const loadFromUniprot = async () => {
    if (!uniprotInput.trim()) {
      toast.error('Please enter a UniProt ID');
      return;
    }

    setIsLoadingStructure(true);

    try {
      const response = await fetch(`/api/sequence-annotation/uniprot/${uniprotInput.trim()}`);
      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch UniProt data');
      }

      if (data.bestStructure) {
        const pdbId = data.bestStructure.id;
        
        setAppState(prev => ({
          ...prev,
          currentPdbId: pdbId,
          currentUniprotId: uniprotInput.toUpperCase(),
          structureInfo: {
            pdbId,
            title: data.proteinInfo?.proteinName || 'Unknown Structure',
            sequenceLength: data.proteinInfo?.sequenceLength || 141,
            chains: ['A', 'B', 'C', 'D'],
            resolution: data.bestStructure.resolution ? parseFloat(data.bestStructure.resolution) : null
          }
        }));

        // Hide landing page and show annotation view
        // The useEffect will automatically initialize the viewer when showLanding becomes false
        setShowLanding(false);
        
        toast.success(`Loaded structure ${pdbId} from UniProt ${uniprotInput.toUpperCase()}`);
      } else {
        throw new Error('No PDB structures found for this UniProt ID');
      }
    } catch (error) {
      console.error('Failed to load from UniProt:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to load from UniProt');
    } finally {
      setIsLoadingStructure(false);
    }
  };

  // Quick load sample structure
  const loadSampleStructure = (sample: typeof SAMPLE_STRUCTURES[0]) => {
    setUniprotInput(sample.uniprotId);
    
    setAppState(prev => ({
      ...prev,
      currentPdbId: sample.pdbId,
      currentUniprotId: sample.uniprotId,
      structureInfo: {
        pdbId: sample.pdbId,
        title: sample.name,
        sequenceLength: 141,
        chains: ['A', 'B', 'C', 'D'],
        resolution: null
      }
    }));

    // Hide landing page and show annotation view
    // The useEffect will automatically initialize the viewer when showLanding becomes false
    setShowLanding(false);
    
    toast.success(`Loaded sample: ${sample.name}`);
  };

  // Track Interactions
  const handleTrackMouseMove = (e: React.MouseEvent) => {
    if (!tracksContainerRef.current) return;

    const rect = tracksContainerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - 140; // Account for label width
    const contentWidth = rect.width - 140;

    if (x >= 0 && x <= contentWidth) {
      const position = Math.round((x / contentWidth) * appState.sequenceLength) + 1;
      
      if (position >= 1 && position <= appState.sequenceLength) {
        setIndicatorPosition(140 + (position - 1) / appState.sequenceLength * contentWidth);
        setTooltip({
          show: true,
          x: e.clientX,
          y: e.clientY,
          content: `Residue ${position}`
        });
        setAppState(prev => ({ ...prev, hoverPosition: position }));
      }
    }
  };

  const handleTrackMouseLeave = () => {
    setIndicatorPosition(null);
    setTooltip(prev => ({ ...prev, show: false }));
    setAppState(prev => ({ ...prev, hoverPosition: null }));
  };

  const handleTrackClick = (e: React.MouseEvent) => {
    if (!tracksContainerRef.current) return;

    const rect = tracksContainerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - 140;
    const contentWidth = rect.width - 140;
    const position = Math.round((x / contentWidth) * appState.sequenceLength) + 1;

    if (position >= 1 && position <= appState.sequenceLength) {
      highlightResidue(position);
    }
  };

  // Initialize viewer when showing annotation view (not landing page)
  useEffect(() => {
    if (!showLanding) {
      // Check if Mol* script is already loaded
      const rcsbMolstar = (window as any).rcsbMolstar;
      
      if (rcsbMolstar) {
        // Script already loaded, just initialize viewer
        setTimeout(() => {
          initializeViewer();
        }, 100);
      } else {
        // Load Mol* script dynamically
        const existingScript = document.getElementById('rcsb-molstar-script');
        if (!existingScript) {
          const script = document.createElement('script');
          script.id = 'rcsb-molstar-script';
          script.src = 'https://cdn.jsdelivr.net/npm/@rcsb/rcsb-molstar@2.14.2/build/dist/viewer/rcsb-molstar.js';
          script.async = true;
          script.onload = () => {
            setTimeout(() => {
              initializeViewer();
            }, 500);
          };
          script.onerror = () => {
            toast.error('Failed to load 3D viewer library');
          };
          document.body.appendChild(script);
        }
      }
    }
  }, [showLanding]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (rcsbViewerRef.current) {
        try {
          rcsbViewerRef.current.clear();
        } catch (e) {
          console.warn('Could not clear viewer on unmount:', e);
        }
      }
    };
  }, []);

  // Landing Page View
  if (showLanding) {
    return (
      <TooltipProvider>
        <div className="flex flex-col h-full min-h-[calc(100vh-64px)] bg-background">
          {/* Main Content - Landing Page */}
          <div className="flex-1 flex flex-col items-center justify-center p-8">
            <div className="w-full max-w-4xl space-y-6">
              {/* Title Section with Enhanced Styling */}
              <div className="text-center space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                  <Dna className="h-3 w-3" />
                  <span>Protein Structure Visualization</span>
                </div>
                <h2 className="text-3xl font-bold text-foreground tracking-tight">
                  Detailed Sequence Annotations
                </h2>
                <p className="text-muted-foreground max-w-lg mx-auto">
                  Explore protein structures with interactive sequence annotations and 3D molecular visualization
                </p>
              </div>

              {/* Search Box with Sample Card - Enhanced */}
              <Card className="p-5 shadow-lg border-2 border-primary/20">
                <div className="flex items-center gap-3">
                  <div className="flex-1 relative">
                    <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">
                      <Search className="h-5 w-5" />
                    </div>
                    <Input
                      type="text"
                      placeholder="Enter UniProt ID (e.g., P69905)"
                      value={uniprotInput}
                      onChange={(e) => setUniprotInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && loadFromUniprot()}
                      className="h-12 pl-10 text-base"
                    />
                  </div>
                  <Button 
                    size="lg"
                    onClick={loadFromUniprot}
                    disabled={isLoadingStructure}
                    className="h-12 px-8 bg-primary hover:bg-primary/90"
                  >
                    {isLoadingStructure ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <>
                        <Search className="h-5 w-5 mr-2" />
                        Load
                      </>
                    )}
                  </Button>
                  
                  {/* Sample Structure Card */}
                  <div 
                    className="h-12 flex items-center gap-2 px-3 bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5 hover:from-primary/10 hover:via-primary/15 hover:to-primary/10 rounded-lg cursor-pointer transition-all duration-300 border border-primary/20 hover:border-primary/40 hover:shadow-md hover:shadow-primary/5 group"
                    onClick={() => loadSampleStructure({ uniprotId: 'P69905', pdbId: '4HHB', name: 'Hemoglobin subunit alpha', organism: 'Human' })}
                  >
                    <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform duration-300 shadow-sm">
                      <Database className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex flex-col justify-center flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm font-medium text-foreground leading-tight truncate">
                          Hemoglobin subunit alpha
                        </span>
                        <Badge variant="default" className="text-[10px] px-1.5 py-0 h-4 bg-gradient-to-r from-primary/20 to-primary/30 text-primary border-primary/30 font-semibold">
                          Example
                        </Badge>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Badge variant="secondary" className="text-[10px] px-1 py-0 h-4 bg-secondary/80">
                          P69905
                        </Badge>
                        <Badge variant="outline" className="text-[10px] px-1 py-0 h-4 border-primary/20 text-primary/70">
                          4HHB
                        </Badge>
                        <span className="text-[10px] text-muted-foreground">
                          Human
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center justify-center h-6 w-6 rounded-full bg-primary/10 text-primary opacity-0 group-hover:opacity-100 transition-all duration-300 transform group-hover:translate-x-0 -translate-x-2 flex-shrink-0">
                      <ArrowRight className="h-3 w-3" />
                    </div>
                  </div>
                </div>
              </Card>

              {/* How It Works Section */}
              <div className="space-y-4">
                {/* Section Title */}
                <div className="flex items-center gap-2">
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-border to-transparent" />
                  <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                    How it works
                  </span>
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-border to-transparent" />
                </div>
                
                {/* Feature Cards */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-muted/30 rounded-lg border border-border/50">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center mb-2">
                      <span className="text-sm font-bold text-primary">1</span>
                    </div>
                    <h4 className="text-sm font-semibold text-foreground mb-1">Enter UniProt ID</h4>
                    <p className="text-xs text-muted-foreground">Search by UniProt ID or click the example to explore</p>
                  </div>
                  <div className="p-4 bg-muted/30 rounded-lg border border-border/50">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center mb-2">
                      <span className="text-sm font-bold text-primary">2</span>
                    </div>
                    <h4 className="text-sm font-semibold text-foreground mb-1">Explore Tracks</h4>
                    <p className="text-xs text-muted-foreground">View sequence annotations: structure, binding sites, outliers</p>
                  </div>
                  <div className="p-4 bg-muted/30 rounded-lg border border-border/50">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center mb-2">
                      <span className="text-sm font-bold text-primary">3</span>
                    </div>
                    <h4 className="text-sm font-semibold text-foreground mb-1">Interactive 3D</h4>
                    <p className="text-xs text-muted-foreground">Click on any position to zoom to residue in 3D structure</p>
                  </div>
                </div>
                
                {/* Preview Image with Label */}
                <div className="relative group pt-8">
                  <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-primary text-primary-foreground text-xs font-medium px-3 py-1 rounded-full shadow-md z-10">
                    Preview of Annotation Interface
                  </div>
                  <div className="overflow-hidden rounded-xl border-2 border-border shadow-lg">
                    <img 
                      src="/annotations.png" 
                      alt="Sequence Annotation Example" 
                      className="w-full transition-transform duration-500 group-hover:scale-[1.02]" 
                    />
                  </div>
                  {/* Feature Callouts */}
                  <div className="absolute bottom-4 left-4 right-4 flex justify-between text-xs">
                    <div className="bg-background/90 backdrop-blur-sm px-3 py-1.5 rounded-lg shadow-md border">
                      <span className="font-medium text-foreground">← Sequence Tracks</span>
                    </div>
                    <div className="bg-background/90 backdrop-blur-sm px-3 py-1.5 rounded-lg shadow-md border">
                      <span className="font-medium text-foreground">3D Structure Viewer →</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </TooltipProvider>
    );
  }

  // Main Annotation View
  return (
    <TooltipProvider>
      <div className="flex flex-col h-full min-h-[calc(100vh-64px)] bg-background">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-3 bg-card border-b">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Dna className="h-5 w-5 text-primary" />
              <h1 className="text-lg font-semibold">
                Sequence Annotations in 3D: <span className="text-primary">{appState.currentPdbId}</span>
              </h1>
            </div>
            
            {/* Chain Selector */}
            <div className="flex items-center gap-2 ml-4">
              <label className="text-sm text-muted-foreground font-medium">Chain</label>
              <select
                value={appState.currentChain}
                onChange={(e) => {
                  setAppState(prev => ({ ...prev, currentChain: e.target.value }));
                  setTimeout(() => highlightResidue(1), 100);
                }}
                className="px-2 py-1 text-sm border rounded-md bg-background"
              >
                {(appState.structureInfo?.chains || ['A', 'B', 'C', 'D']).map(chain => (
                  <option key={chain} value={chain}>{chain}</option>
                ))}
              </select>
            </div>

            {/* Back Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowLanding(true)}
              className="ml-4"
            >
              Back to Search
            </Button>
          </div>

          {/* Structure Info Badge */}
          {appState.structureInfo && (
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {appState.structureInfo.title?.substring(0, 50)}...
              </Badge>
              {appState.structureInfo.resolution && (
                <Badge variant="secondary" className="text-xs">
                  {appState.structureInfo.resolution} Å
                </Badge>
              )}
            </div>
          )}
        </div>

        {/* Subtitle */}
        <div className="px-6 py-2 bg-muted/30 border-b text-sm text-muted-foreground">
          {appState.structureInfo?.title || 'THE CRYSTAL STRUCTURE OF HUMAN DEOXYHAEMOGLOBIN AT 1.74 ANGSTROMS RESOLUTION'}
        </div>

        {/* Main Content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Left Panel: Sequence Annotations */}
          <div className="w-[45%] min-w-[500px] bg-card border-r flex flex-col">
            {/* Tracks Container */}
            <div 
              ref={tracksContainerRef}
              className="flex-1 overflow-auto relative p-2"
              onMouseMove={handleTrackMouseMove}
              onMouseLeave={handleTrackMouseLeave}
              onClick={handleTrackClick}
            >
              {/* Ruler */}
              <div className="h-8 border-b ml-[140px] relative">
                <div className="relative h-full text-[11px] text-muted-foreground">
                  {generateRuler()}
                </div>
              </div>

              {/* Tracks */}
              <div className="min-h-full">
                {tracks.map(track => (
                  <div 
                    key={track.id} 
                    className="flex items-center min-h-7 border-b hover:bg-muted/50 transition-colors cursor-crosshair"
                  >
                    <div className="w-[140px] px-3 text-[11px] font-semibold text-right uppercase tracking-wider text-foreground flex-shrink-0">
                      {track.type === 'chain' ? `CHAIN ${appState.currentChain}` : 
                       track.type === 'uniprot' ? `UNIPROT ${appState.currentUniprotId}` : track.label}
                    </div>
                    <div className="flex-1 h-full min-h-6 relative px-2 py-0.5 overflow-hidden">
                      {generateTrackContent(track)}
                    </div>
                  </div>
                ))}
              </div>

              {/* Position Indicator */}
              {indicatorPosition !== null && (
                <div 
                  className="absolute top-0 bottom-0 w-0.5 bg-yellow-400 pointer-events-none z-50"
                  style={{ left: `${indicatorPosition}px` }}
                />
              )}
            </div>
          </div>

          {/* Right Panel: 3D Viewer */}
          <div className="flex-1 bg-white dark:bg-slate-900 flex flex-col">
            {/* Toolbar */}
            <div className="h-10 bg-muted border-b flex items-center px-3 gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="h-7 text-xs"
                onClick={() => applyRepresentation('cartoon')}
              >
                Cartoon
              </Button>
              <div className="w-px h-5 bg-border" />
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => applyRepresentation('ball-stick')}
                  >
                    <Box className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Ball & Stick</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => applyRepresentation('surface')}
                  >
                    <div className="h-3 w-3 border border-current rounded-sm" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Surface</TooltipContent>
              </Tooltip>
              <div className="w-px h-5 bg-border" />
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={toggleColorTheme}
                  >
                    <Palette className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Color Theme: {currentColorTheme}</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className={`h-7 w-7 ${measurementMode ? 'bg-primary text-primary-foreground' : ''}`}
                    onClick={() => setMeasurementMode(!measurementMode)}
                  >
                    <Box className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Measurement Mode</TooltipContent>
              </Tooltip>
              <div className="w-px h-5 bg-border" />
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => zoomCamera(0.8)}
                  >
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Zoom Out</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => zoomCamera(1.2)}
                  >
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Zoom In</TooltipContent>
              </Tooltip>
              <div className="flex-1" />
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => toast.info('Click on sequence tracks to select residues. The 3D viewer will automatically zoom to the selected position.')}
                  >
                    <HelpCircle className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Help</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={clearHighlights}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Clear Selection</TooltipContent>
              </Tooltip>
            </div>

            {/* Viewer Container */}
            <div className="flex-1 relative bg-white dark:bg-slate-900">
              <div 
                id="molstar-container" 
                ref={viewerContainerRef}
                className="w-full h-full"
              />
              
              {isLoadingStructure && (
                <div className="absolute inset-0 bg-white/95 dark:bg-slate-900/95 flex flex-col items-center justify-center z-50">
                  <Loader2 className="h-8 w-8 animate-spin text-primary mb-2" />
                  <p className="text-sm text-foreground dark:text-white">Loading structure...</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tooltip */}
        {tooltip.show && (
          <div 
            className="fixed bg-black/90 text-white px-3 py-2 rounded-md text-sm pointer-events-none z-[10000] whitespace-nowrap shadow-lg"
            style={{ left: tooltip.x + 10, top: tooltip.y - 30 }}
          >
            {tooltip.content}
          </div>
        )}

        {/* Info Panel */}
        <Card className="m-4">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Info className="h-4 w-4" />
              Feature Information
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-sm space-y-1">
              {appState.hoverPosition ? (
                <>
                  <p className="font-medium">Position: {appState.hoverPosition}</p>
                  <p className="text-muted-foreground text-xs">
                    Chain {appState.currentChain} | PDB: {appState.currentPdbId}.{appState.currentChain}.{appState.hoverPosition}
                  </p>
                </>
              ) : appState.selectedPosition ? (
                <>
                  <p className="font-medium">Selected: Position {appState.selectedPosition}</p>
                  <p className="text-muted-foreground text-xs">
                    Chain {appState.currentChain} | PDB: {appState.currentPdbId}.{appState.currentChain}.{appState.selectedPosition}
              </p>
                </>
              ) : (
                <p className="text-muted-foreground text-xs">
                  Hover over tracks to see feature details. Click to zoom to residue.
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </TooltipProvider>
  );
}

export default SequenceAnnotationPage;
