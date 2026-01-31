import { useEffect, useRef, useState, useCallback } from "react";
import {
    AlertCircle,
    ExternalLink,
    RotateCcw,
    Maximize2,
    Minimize2,
    Download,
    Layers,
    Atom,
    Dna,
    Focus,
    Palette
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

// --- Types for PDBe Molstar Plugin ---
interface PDBeMolstarPlugin {
    render: (container: HTMLElement, options: MolstarOptions) => void;
    events: {
        loadComplete: {
            subscribe: (callback: () => void) => void;
        };
    };
    instance?: {
        viewer?: {
            resetCamera: () => void;
            screenshot: () => Promise<Blob>;
        };
    };
}

interface MolstarOptions {
    moleculeId?: string;
    customData?: {
        url: string;
        format: string;
        binary?: boolean;
    };
    pdbeUrl?: string;
    loadEmptyCanvas?: boolean;
    hideCanvasControls?: string[];
    hideControls?: boolean;
    landscape?: boolean;
    subscribeEvents?: boolean;
    bgColor?: { r: number; g: number; b: number };
    selectInteraction?: boolean;
    sequencePanel?: boolean;
    structurePanel?: boolean;
    viewport?: {
        camera?: string;
    };
}

interface MolstarViewerProps {
    pdbId?: string;
    url?: string;
    height?: string;
    className?: string;
    targetName?: string;
    ligandName?: string;
    showControls?: boolean;
    onLoad?: () => void;
    onError?: (error: string) => void;
}

// Common PDB IDs for drug discovery targets as fallbacks (LOWERCASE required for PDBe CDN)
const COMMON_PDB_IDS: Record<string, string> = {
    'ACE2': '1r42',
    'BACE1': '1sgz',
    'CDK2': '1hcl',
    'COX1': '1eqg',
    'COX2': '1cx2',
    'DPP4': '1nu8',
    'EGFR': '1m17',
    'HIV-1 protease': '1hxb',
    'JAK2': '2b7a',
    'MEK': '3eqd',
    'PDE5': '1udt',
    'PI3K': '2rd0',
    'SARS-CoV-2': '6vxx',
    'Spike protein': '6vxx',
    'VEGFR2': '2xir',
    'kinase': '1atp',
    'protease': '1hxb',
    'receptor': '1m17',
    'AChE': '1eve',
    'insulin': '1trz',
    'hemoglobin': '1hho',
    'myoglobin': '1mbo',
    'lysozyme': '1aki',
    'CFTR': '6v6p',
    'donepezil': '1eve',
    'ivacaftor': '6v6p',
    'lumacaftor': '5u71',
    'tezacaftor': '6o1v',
};

// Global script loading state
let scriptLoadPromise: Promise<void> | null = null;

// Load PDBe Molstar script dynamically using unpkg (more reliable)
const loadMolstarScript = (): Promise<void> => {
    // Return existing promise if already loading
    if (scriptLoadPromise) {
        return scriptLoadPromise;
    }

    scriptLoadPromise = new Promise((resolve, reject) => {
        // Check if already loaded
        if ((window as any).PDBeMolstarPlugin) {
            resolve();
            return;
        }

        // Check if script is already being loaded
        const existingScript = document.querySelector('script[src*="pdbe-molstar"]');
        if (existingScript) {
            existingScript.addEventListener('load', () => resolve());
            existingScript.addEventListener('error', () => {
                scriptLoadPromise = null;
                reject(new Error('Failed to load Molstar script'));
            });
            return;
        }

        // Load CSS first
        const existingLink = document.querySelector('link[href*="pdbe-molstar"]');
        if (!existingLink) {
            const link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = "https://unpkg.com/pdbe-molstar@3.2.0/build/pdbe-molstar-light.css";
            document.head.appendChild(link);
        }

        // Load JS from unpkg (more reliable than jsdelivr)
        const script = document.createElement("script");
        script.src = "https://unpkg.com/pdbe-molstar@3.2.0/build/pdbe-molstar-plugin.js";
        script.async = true;

        script.onload = () => {
            // Give the script a moment to initialize
            setTimeout(() => {
                if ((window as any).PDBeMolstarPlugin) {
                    resolve();
                } else {
                    scriptLoadPromise = null;
                    reject(new Error('Molstar script loaded but PDBeMolstarPlugin not found'));
                }
            }, 100);
        };

        script.onerror = () => {
            scriptLoadPromise = null;
            reject(new Error('Failed to load Molstar script from CDN'));
        };

        document.body.appendChild(script);
    });

    return scriptLoadPromise;
};

export const MolstarViewer = ({
    pdbId,
    url,
    height = "500px",
    className,
    targetName,
    ligandName,
    showControls = true,
    onLoad,
    onError
}: MolstarViewerProps) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const pluginRef = useRef<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPdbId, setCurrentPdbId] = useState<string>("");
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [showSequence, setShowSequence] = useState(false);
    const [showStructure, setShowStructure] = useState(false);
    const [retryCount, setRetryCount] = useState(0);

    // Get fallback PDB ID based on target name
    const getFallbackPdbId = useCallback((target?: string): string => {
        if (!target) return "1EVE";
        const targetLower = target.toLowerCase();
        for (const [key, value] of Object.entries(COMMON_PDB_IDS)) {
            if (targetLower.includes(key.toLowerCase())) return value;
        }
        return "1EVE";
    }, []);

    // Validate and get effective PDB ID
    const getEffectivePdbId = useCallback((id?: string, target?: string): string => {
        // IMPORTANT: PDBe CDN requires lowercase IDs for download endpoints
        if (id && /^[A-Za-z0-9]{4}$/.test(id)) return id.toLowerCase();
        return getFallbackPdbId(target).toLowerCase();
    }, [getFallbackPdbId]);

    // Initialize Molstar viewer
    useEffect(() => {
        const effectiveId = getEffectivePdbId(pdbId, targetName);
        setCurrentPdbId(effectiveId);
        setIsLoading(true);
        setError(null);

        const initViewer = async () => {
            try {
                await loadMolstarScript();

                const PDBeMolstarPlugin = (window as any).PDBeMolstarPlugin;
                if (!PDBeMolstarPlugin) {
                    throw new Error('PDBeMolstarPlugin not available after script load');
                }

                if (containerRef.current) {
                    // Clear existing content
                    containerRef.current.innerHTML = '';

                    // Create new plugin instance
                    const viewerInstance = new PDBeMolstarPlugin();
                    pluginRef.current = viewerInstance;

                    const options: MolstarOptions = {
                        moleculeId: effectiveId,
                        pdbeUrl: 'https://www.ebi.ac.uk/pdbe', // No trailing slash for reliability
                        loadEmptyCanvas: false,
                        hideCanvasControls: showControls ? [] : ['selection', 'animation', 'control-toggle', 'control-info', 'control-fullscreen'],
                        hideControls: !showControls,
                        landscape: true,
                        subscribeEvents: true,
                        bgColor: { r: 10, g: 10, b: 15 }, // Darker background for premium feel
                        selectInteraction: true,
                        sequencePanel: showSequence,
                        structurePanel: showStructure,
                    };

                    // If URL is provided, use custom data instead of PDB ID
                    if (url) {
                        delete options.moleculeId;
                        options.customData = {
                            url: url,
                            format: 'pdb',
                            binary: false
                        };
                    }

                    viewerInstance.render(containerRef.current, options);

                    // Subscribe to load complete event
                    if (viewerInstance.events?.loadComplete) {
                        viewerInstance.events.loadComplete.subscribe(() => {
                            setIsLoading(false);
                            onLoad?.();
                        });
                    } else {
                        // Fallback if events not available
                        setTimeout(() => {
                            setIsLoading(false);
                            onLoad?.();
                        }, 4000);
                    }
                }
            } catch (err) {
                console.error("Molstar initialization error:", err);
                const errorMsg = err instanceof Error ? err.message : 'Failed to initialize 3D viewer';
                setError(errorMsg);
                setIsLoading(false);
                onError?.(errorMsg);

                // If it fails, try one more time
                if (retryCount < 1) {
                    setTimeout(() => setRetryCount(prev => prev + 1), 1000);
                }
            }
        };

        const timer = setTimeout(initViewer, 100);
        return () => clearTimeout(timer);
    }, [pdbId, url, targetName, showControls, showSequence, showStructure, onLoad, onError, getEffectivePdbId, retryCount]);

    // Handle retry
    const handleRetry = () => {
        scriptLoadPromise = null;
        setRetryCount(prev => prev + 1);
    };

    // Handle fullscreen toggle
    const toggleFullscreen = () => {
        if (!containerRef.current) return;

        if (!document.fullscreenElement) {
            containerRef.current.requestFullscreen?.().then(() => {
                setIsFullscreen(true);
            }).catch(() => {
                toast.error('Fullscreen not supported');
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen().then(() => {
                    setIsFullscreen(false);
                });
            }
        }
    };

    // Handle screenshot
    const takeScreenshot = async () => {
        try {
            const canvas = containerRef.current?.querySelector('canvas');
            if (canvas) {
                const link = document.createElement('a');
                link.download = `aurelius-mol-${currentPdbId}-${Date.now()}.png`;
                link.href = canvas.toDataURL('image/png');
                link.click();
                toast.success('High-res structural slide captured');
            }
        } catch (err) {
            toast.error('Failed to capture screenshot');
        }
    };

    // Reset camera
    const resetCamera = () => {
        if (pluginRef.current?.instance?.viewer?.resetCamera) {
            pluginRef.current.instance.viewer.resetCamera();
            toast.info('Camera perspective reset');
        } else {
            // Fallback
            const canvas = containerRef.current?.querySelector('canvas');
            if (canvas) {
                canvas.dispatchEvent(new KeyboardEvent('keydown', { key: 'r' }));
                toast.info('Camera reset (event)');
            }
        }
    };

    // Get effective PDB ID for display
    const effectiveId = currentPdbId || getEffectivePdbId(pdbId, targetName);

    // External links
    const rcsbUrl = `https://www.rcsb.org/structure/${effectiveId}`;
    const pdbeUrl = `https://www.ebi.ac.uk/pdbe/entry/pdb/${effectiveId.toLowerCase()}`;

    return (
        <TooltipProvider>
            <div
                className={`relative overflow-hidden rounded-3xl border border-white/5 bg-black ${className} ${isFullscreen ? 'fixed inset-0 z-50 rounded-none' : ''}`}
                style={{ height: isFullscreen ? '100vh' : height }}
            >
                {/* Loading Overlay */}
                {isLoading && (
                    <div className="absolute inset-0 bg-[#050505]/95 backdrop-blur-xl z-40 flex flex-col items-center justify-center">
                        <div className="relative">
                            <div className="h-20 w-20 rounded-full border-t-2 border-primary animate-spin" />
                            <div className="absolute inset-0 flex items-center justify-center">
                                <Atom className="h-8 w-8 text-primary/50 animate-pulse" />
                            </div>
                        </div>
                        <p className="text-xs font-black uppercase tracking-[0.3em] text-white/80 mt-8">Initializing Model</p>
                        <p className="text-[10px] text-muted-foreground mt-2 font-mono bg-white/5 px-2 py-1 rounded">SEQUENCE_REF: {effectiveId}</p>
                    </div>
                )}

                {/* Error Overlay */}
                {error && (
                    <div className="absolute inset-0 bg-red-950/20 backdrop-blur-xl z-40 flex flex-col items-center justify-center p-8 text-center border border-red-500/10">
                        <div className="w-20 h-20 rounded-full bg-red-500/10 flex items-center justify-center mb-6 ring-1 ring-red-500/20">
                            <AlertCircle className="h-10 w-10 text-red-500" />
                        </div>
                        <h3 className="text-white font-black text-xl tracking-tight mb-2">Structure Stream Interrupted</h3>
                        <p className="text-sm text-muted-foreground/80 mt-2 max-w-sm font-medium leading-relaxed">
                            The PDB repository is unable to serve the request for <span className="text-white font-bold">{effectiveId}</span>. This may be due to a malformed ID or network latency.
                        </p>
                        <div className="flex gap-4 mt-8">
                            <Button
                                variant="secondary"
                                onClick={handleRetry}
                                className="gap-2 bg-white/10 hover:bg-white/20 border-white/10 text-white font-bold"
                            >
                                <RotateCcw className="h-4 w-4" /> RECONNECT
                            </Button>
                            <a
                                href={rcsbUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Button variant="default" className="font-bold">
                                    <ExternalLink className="h-4 w-4 mr-2" /> PDB SOURCE
                                </Button>
                            </a>
                        </div>
                    </div>
                )}

                {/* Main Viewer Container */}
                <div ref={containerRef} className="w-full h-full" />

                {/* Top Info Bar */}
                <div className="absolute top-0 left-0 right-0 p-6 flex items-start justify-between pointer-events-none z-20">
                    <div className="pointer-events-auto flex flex-col gap-3">
                        <div className="bg-black/40 backdrop-blur-2xl border border-white/10 p-4 rounded-[28px] shadow-2xl ring-1 ring-white/5">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/20">
                                    <Dna className="h-6 w-6 text-primary" />
                                </div>
                                <div>
                                    <div className="text-[10px] font-black uppercase tracking-widest text-primary mb-0.5">Primary Target</div>
                                    <div className="font-black text-lg text-white flex items-center gap-3">
                                        {targetName || "Structure"}
                                        <div className="px-2 py-0.5 bg-white/10 rounded-md text-[10px] font-mono font-bold text-white/60">
                                            {effectiveId}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {ligandName && (
                                <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <Atom className="h-4 w-4 text-amber-500" />
                                        <span className="text-xs font-bold text-white/90">{ligandName}</span>
                                    </div>
                                    <div className="text-[9px] font-black uppercase text-amber-500/60 tracking-wider">LIGAND ACTIVE</div>
                                </div>
                            )}
                        </div>

                        <div className="flex gap-2">
                            <div className="bg-black/40 backdrop-blur-xl border border-white/5 px-3 py-1.5 rounded-full flex items-center gap-2">
                                <div className="w-1 h-1 rounded-full bg-blue-400" />
                                <span className="text-[9px] font-black text-white/40 uppercase tracking-widest">RES:</span>
                                <span className="text-[10px] font-bold text-white/90">2.1 Å</span>
                            </div>
                            <div className="bg-black/40 backdrop-blur-xl border border-white/5 px-3 py-1.5 rounded-full flex items-center gap-2">
                                <div className="w-1 h-1 rounded-full bg-purple-400" />
                                <span className="text-[9px] font-black text-white/40 uppercase tracking-widest">TYPE:</span>
                                <span className="text-[10px] font-bold text-white/90">X-RAY</span>
                            </div>
                        </div>
                    </div>

                    <div className="pointer-events-auto flex flex-col gap-3">
                        <div className="bg-black/40 backdrop-blur-2xl border border-white/10 p-1.5 rounded-2xl shadow-2xl flex flex-col gap-1.5 ring-1 ring-white/5">
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-9 w-9 text-white/60 hover:text-white hover:bg-white/10 rounded-xl"
                                        onClick={toggleFullscreen}
                                    >
                                        {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent side="left">
                                    <p className="font-bold">{isFullscreen ? 'Exit Stage' : 'Full Stage View'}</p>
                                </TooltipContent>
                            </Tooltip>

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-9 w-9 text-white/60 hover:text-white hover:bg-white/10 rounded-xl"
                                        onClick={takeScreenshot}
                                    >
                                        <Download className="h-4 w-4" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent side="left">
                                    <p className="font-bold">Capture Slide</p>
                                </TooltipContent>
                            </Tooltip>
                        </div>
                    </div>
                </div>

                {/* Bottom HUD Bar */}
                <div className="absolute bottom-0 left-0 right-0 p-6 flex items-end justify-between pointer-events-none z-20">
                    <div className="pointer-events-auto flex flex-col gap-4">
                        <div className="bg-black/60 backdrop-blur-2xl border border-white/10 p-5 rounded-[32px] shadow-2xl ring-1 ring-white/5">
                            <div className="text-[9px] font-black uppercase tracking-[0.2em] text-white/30 mb-4 flex items-center justify-between">
                                Structural Legend
                                <Palette className="h-3 w-3" />
                            </div>
                            <div className="flex flex-col gap-3">
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_12px_rgba(59,130,246,0.6)]" />
                                    <span className="text-[11px] font-black text-white/80 uppercase">Hydrogen Bonds</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 rounded-full bg-orange-500 shadow-[0_0_12px_rgba(249,115,22,0.6)]" />
                                    <span className="text-[11px] font-black text-white/80 uppercase">Pi-Stacking</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 rounded-full bg-green-500 shadow-[0_0_12px_rgba(34,197,94,0.6)]" />
                                    <span className="text-[11px] font-black text-white/80 uppercase">Hydrophobic</span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-2 bg-black/40 backdrop-blur-xl border border-white/5 p-1.5 rounded-2xl">
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-9 w-9 text-white/40 hover:text-white rounded-xl"
                                        onClick={resetCamera}
                                    >
                                        <Focus className="h-4 w-4" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p className="font-bold">Reset Focus</p>
                                </TooltipContent>
                            </Tooltip>

                            <div className="w-px h-4 bg-white/10" />

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className={cn("h-9 w-9 rounded-xl transition-all", showSequence ? 'bg-primary/20 text-primary' : 'text-white/40 hover:text-white')}
                                        onClick={() => setShowSequence(!showSequence)}
                                    >
                                        <Dna className="h-4 w-4" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p className="font-bold">Show Residue Stream</p>
                                </TooltipContent>
                            </Tooltip>

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className={cn("h-9 w-9 rounded-xl transition-all", showStructure ? 'bg-primary/20 text-primary' : 'text-white/40 hover:text-white')}
                                        onClick={() => setShowStructure(!showStructure)}
                                    >
                                        <Layers className="h-4 w-4" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p className="font-bold">Anatomy Inspector</p>
                                </TooltipContent>
                            </Tooltip>
                        </div>
                    </div>

                    <div className="pointer-events-auto flex flex-col items-end gap-3">
                        <div className="flex items-center gap-3 bg-white/5 backdrop-blur-xl border border-white/10 px-5 py-2.5 rounded-[20px] group hover:bg-white/10 transition-all cursor-default shadow-lg">
                            <div className="flex flex-col items-end">
                                <span className="text-[10px] font-black text-white tracking-widest uppercase opacity-40">System Node</span>
                                <span className="text-[11px] font-black text-primary uppercase italic tracking-tighter">AURELIUS V3.0-VIS</span>
                            </div>
                            <div className="w-px h-6 bg-white/10" />
                            <div className="p-1.5 bg-primary/20 rounded-lg group-hover:scale-110 transition-transform">
                                <Atom className="h-4 w-4 text-primary" />
                            </div>
                        </div>

                        <div className="flex gap-3 px-2">
                            <a
                                href={pdbeUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-[10px] font-black uppercase tracking-widest text-white/30 hover:text-primary transition-all underline underline-offset-4 decoration-white/10"
                            >
                                PDBe-API
                            </a>
                            <a
                                href={rcsbUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-[10px] font-black uppercase tracking-widest text-white/30 hover:text-primary transition-all underline underline-offset-4 decoration-white/10"
                            >
                                RCSB-IO
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </TooltipProvider>
    );
};

export default MolstarViewer;
