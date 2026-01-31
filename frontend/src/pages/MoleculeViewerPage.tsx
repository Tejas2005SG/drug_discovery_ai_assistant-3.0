import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { MolstarViewer } from "@/components/drug-discovery/MolstarViewer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
    ArrowLeft,
    Dna,
    Atom,
    ExternalLink,
    Share2,
    Target,
    Activity,
    Microscope,
    Info,
    FileText,
    Beaker,
    Layers
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

// --- Types ---
interface MolecularData {
    pdbId: string;
    targetName: string;
    ligandName?: string;
    resolution?: string;
    method?: string;
    organism?: string;
    description?: string;
}

// Mock data for demonstration - in real app, fetch from API
const MOCK_MOLECULAR_DATA: Record<string, MolecularData> = {
    "1eve": {
        pdbId: "1eve",
        targetName: "Acetylcholinesterase",
        ligandName: "Donepezil",
        resolution: "2.1 Å",
        method: "X-RAY DIFFRACTION",
        organism: "Homo sapiens",
        description: "Crystal structure of human acetylcholinesterase in complex with donepezil."
    },
    "1m17": {
        pdbId: "1m17",
        targetName: "EGFR Kinase",
        ligandName: "Erlotinib",
        resolution: "2.6 Å",
        method: "X-RAY DIFFRACTION",
        organism: "Homo sapiens",
        description: "Crystal structure of the EGFR kinase domain in complex with erlotinib."
    },
    "6vxx": {
        pdbId: "6vxx",
        targetName: "SARS-CoV-2 Spike Protein",
        ligandName: "ACE2",
        resolution: "3.5 Å",
        method: "CRYO-EM",
        organism: "Severe acute respiratory syndrome coronavirus 2",
        description: "Structure of the SARS-CoV-2 spike glycoprotein in the prefusion conformation."
    },
    "6v6p": {
        pdbId: "6v6p",
        targetName: "CFTR",
        ligandName: "Ivacaftor",
        resolution: "3.2 Å",
        method: "CRYO-EM",
        organism: "Homo sapiens",
        description: "Structure of the human CFTR in complex with Ivacaftor."
    }
};

export default function MoleculeViewerPage() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(true);
    const [molecularData, setMolecularData] = useState<MolecularData | null>(null);

    // Get query parameters
    const pdbId = searchParams.get("pdbId") || "";
    const targetName = searchParams.get("targetName") || "";
    const ligandName = searchParams.get("ligandName") || "";

    // Fetch molecular data
    useEffect(() => {
        setIsLoading(true);

        // Simulate API call
        const timer = setTimeout(() => {
            const cleanId = pdbId.toLowerCase();
            const data = MOCK_MOLECULAR_DATA[cleanId] || {
                pdbId: cleanId || "1eve",
                targetName: targetName || "Unknown Target",
                ligandName: ligandName || undefined,
                resolution: "2.1 Å",
                method: "X-RAY DIFFRACTION",
                organism: "Homo sapiens",
                description: `Molecular structure of ${targetName || "the target protein"}.`
            };
            setMolecularData(data);
            setIsLoading(false);
        }, 500);

        return () => clearTimeout(timer);
    }, [pdbId, targetName, ligandName]);

    const handleBack = () => {
        navigate(-1); // Go back to previous page
    };

    const handleShare = () => {
        const url = window.location.href;
        navigator.clipboard.writeText(url);
        toast.success("Link copied to clipboard");
    };

    const rcsbUrl = `https://www.rcsb.org/structure/${molecularData?.pdbId || pdbId}`;
    const pdbeUrl = `https://www.ebi.ac.uk/pdbe/entry/pdb/${(molecularData?.pdbId || pdbId).toLowerCase()}`;

    if (isLoading) {
        return (
            <div className="h-screen w-full flex items-center justify-center bg-[#050505]">
                <div className="flex flex-col items-center gap-6">
                    <div className="relative">
                        <div className="h-20 w-20 rounded-full border-t-2 border-primary animate-spin" />
                        <div className="absolute inset-0 flex items-center justify-center">
                            <Atom className="h-8 w-8 text-primary/50 animate-pulse" />
                        </div>
                    </div>
                    <div className="text-center">
                        <p className="text-xs font-black uppercase tracking-[0.3em] text-white/80">Synchronizing Crystal Data</p>
                        <p className="text-[10px] text-muted-foreground mt-2 font-mono">NODE_PDB: {pdbId || "AUTH"}</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="h-screen w-full flex flex-col bg-black overflow-hidden font-sans selection:bg-primary/30">
            {/* Header */}
            <header className="h-20 border-b border-white/5 bg-black/60 backdrop-blur-2xl flex items-center justify-between px-6 lg:px-8 shrink-0 z-50 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-transparent pointer-events-none" />
                <div className="flex items-center gap-6 relative z-10">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={handleBack}
                                    className="h-12 w-12 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/5 transition-all text-white/60 hover:text-white"
                                >
                                    <ArrowLeft className="h-5 w-5" />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent className="bg-black/90 backdrop-blur-xl border-white/10">
                                <p className="font-bold">RETURN TO DASHBOARD</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>

                    <div className="h-10 w-px bg-white/10 hidden sm:block" />

                    <div className="flex items-center gap-4">
                        <div className="h-12 w-12 bg-primary/20 rounded-2xl flex items-center justify-center border border-primary/20 shadow-lg shadow-primary/10">
                            <Dna className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <div className="flex items-center gap-3">
                                <h1 className="text-xl font-black tracking-tighter text-white">
                                    {molecularData?.targetName || targetName || "Molecular Viewer"}
                                </h1>
                                <Badge className="bg-primary/10 text-primary border-primary/20 text-[10px] font-black uppercase tracking-widest px-2.5 h-6">
                                    {molecularData?.pdbId || pdbId || "1EVE"}
                                </Badge>
                            </div>
                            {molecularData?.ligandName && (
                                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-amber-500/60 flex items-center gap-2 mt-1">
                                    <Atom className="h-3 w-3" />
                                    Complexed Ligand: {molecularData.ligandName}
                                </p>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3 relative z-10">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={handleShare}
                                    className="h-10 px-5 rounded-xl bg-white/5 hover:bg-white/10 border-white/10 gap-2 font-black uppercase text-[10px] tracking-widest text-white/70 hover:text-white transition-all"
                                >
                                    <Share2 className="h-4 w-4" />
                                    Share
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent className="bg-black/90 backdrop-blur-xl border-white/10">
                                <p className="font-bold">COPY CRYSTAL LINK</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>

                    <div className="h-6 w-px bg-white/10" />

                    <a
                        href={rcsbUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        <Button
                            variant="default"
                            size="sm"
                            className="h-10 px-5 rounded-xl font-black uppercase text-[10px] tracking-widest shadow-lg shadow-primary/20"
                        >
                            <ExternalLink className="h-4 w-4 mr-2" />
                            RCSB PDB
                        </Button>
                    </a>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* 3D Viewer - Takes most of the space */}
                <div className="flex-1 relative bg-[#0a0a0f]">
                    <MolstarViewer
                        pdbId={molecularData?.pdbId || pdbId}
                        height="100%"
                        className="w-full h-full"
                        targetName={molecularData?.targetName || targetName}
                        ligandName={molecularData?.ligandName || ligandName}
                        showControls={true}
                    />
                </div>

                {/* Side Panel */}
                <div className="w-[400px] border-l border-white/5 bg-black/40 backdrop-blur-3xl flex flex-col overflow-hidden shrink-0">
                    <Tabs defaultValue="details" className="flex-1 flex flex-col">
                        <TabsList className="w-full rounded-none border-b border-white/5 bg-white/5 p-0 h-14">
                            <TabsTrigger
                                value="details"
                                className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-white/5 h-14 font-black uppercase text-[10px] tracking-widest text-white/40 data-[state=active]:text-white transition-all"
                            >
                                <Info className="h-4 w-4 mr-2" />
                                Dossier
                            </TabsTrigger>
                            <TabsTrigger
                                value="interactions"
                                className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-white/5 h-14 font-black uppercase text-[10px] tracking-widest text-white/40 data-[state=active]:text-white transition-all"
                            >
                                <Activity className="h-4 w-4 mr-2" />
                                Binding
                            </TabsTrigger>
                            <TabsTrigger
                                value="annotations"
                                className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-white/5 h-14 font-black uppercase text-[10px] tracking-widest text-white/40 data-[state=active]:text-white transition-all"
                            >
                                <FileText className="h-4 w-4 mr-2" />
                                Archive
                            </TabsTrigger>
                        </TabsList>

                        <div className="flex-1 overflow-y-auto custom-scrollbar">
                            <TabsContent value="details" className="m-0 p-6 space-y-6">
                                {/* Structure Overview */}
                                <div className="bg-white/5 border border-white/10 rounded-[32px] overflow-hidden backdrop-blur-xl">
                                    <div className="p-5 border-b border-white/10 bg-white/5">
                                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-primary flex items-center gap-2">
                                            <Beaker className="h-4 w-4" />
                                            Structure Metrics
                                        </h3>
                                    </div>
                                    <div className="p-6 space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="p-4 bg-white/5 rounded-[20px] border border-white/5 group hover:bg-white/10 transition-all">
                                                <div className="text-[9px] uppercase text-white/40 font-black tracking-widest mb-1.5">PDB ID</div>
                                                <div className="text-sm font-mono font-black text-white">{molecularData?.pdbId || pdbId}</div>
                                            </div>
                                            <div className="p-4 bg-white/5 rounded-[20px] border border-white/5 group hover:bg-white/10 transition-all">
                                                <div className="text-[9px] uppercase text-white/40 font-black tracking-widest mb-1.5">Resolution</div>
                                                <div className="text-sm font-black text-white">{molecularData?.resolution || "2.1 Å"}</div>
                                            </div>
                                            <div className="p-4 bg-white/5 rounded-[20px] border border-white/5 group hover:bg-white/10 transition-all">
                                                <div className="text-[9px] uppercase text-white/40 font-black tracking-widest mb-1.5">Method</div>
                                                <div className="text-sm font-black text-white">{molecularData?.method || "X-RAY"}</div>
                                            </div>
                                            <div className="p-4 bg-white/5 rounded-[20px] border border-white/5 group hover:bg-white/10 transition-all">
                                                <div className="text-[9px] uppercase text-white/40 font-black tracking-widest mb-1.5">Organism</div>
                                                <div className="text-sm font-black text-white truncate">{molecularData?.organism || "Human"}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Description */}
                                <div className="bg-white/5 border border-white/10 rounded-[32px] overflow-hidden backdrop-blur-xl">
                                    <div className="p-5 border-b border-white/10 bg-white/5">
                                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-primary flex items-center gap-2">
                                            <FileText className="h-4 w-4" />
                                            Target Profile
                                        </h3>
                                    </div>
                                    <div className="p-6">
                                        <p className="text-sm text-white/70 leading-relaxed font-medium">
                                            {molecularData?.description || `Molecular structure of ${targetName || "the target protein"}.`}
                                        </p>
                                    </div>
                                </div>

                                {/* External Links */}
                                <div className="bg-white/5 border border-white/10 rounded-[32px] overflow-hidden backdrop-blur-xl">
                                    <div className="p-5 border-b border-white/10 bg-white/5">
                                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-primary flex items-center gap-2">
                                            <ExternalLink className="h-4 w-4" />
                                            External Resources
                                        </h3>
                                    </div>
                                    <div className="p-6 space-y-3">
                                        <a
                                            href={rcsbUrl}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 hover:bg-white/10 transition-all group"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
                                                    <span className="text-[10px] font-black text-blue-400">RCSB</span>
                                                </div>
                                                <div>
                                                    <div className="text-sm font-black text-white">RCSB PDB</div>
                                                    <div className="text-[10px] text-white/30 font-bold uppercase tracking-widest">Structural Repository</div>
                                                </div>
                                            </div>
                                            <ExternalLink className="h-4 w-4 text-white/20 group-hover:text-primary transition-colors" />
                                        </a>
                                        <a
                                            href={pdbeUrl}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 hover:bg-white/10 transition-all group"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
                                                    <span className="text-[10px] font-black text-green-400">PDBe</span>
                                                </div>
                                                <div>
                                                    <div className="text-sm font-black text-white">PDBe-EBI</div>
                                                    <div className="text-[10px] text-white/30 font-bold uppercase tracking-widest">Bioinformatics Node</div>
                                                </div>
                                            </div>
                                            <ExternalLink className="h-4 w-4 text-white/20 group-hover:text-primary transition-colors" />
                                        </a>
                                    </div>
                                </div>
                            </TabsContent>

                            <TabsContent value="interactions" className="m-0 p-6 space-y-6">
                                {/* Binding Data */}
                                <div className="bg-white/5 border border-white/10 rounded-[32px] overflow-hidden backdrop-blur-xl">
                                    <div className="p-5 border-b border-white/10 bg-white/5">
                                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-primary flex items-center gap-2">
                                            <Target className="h-4 w-4" />
                                            Affinity & Interaction
                                        </h3>
                                    </div>
                                    <div className="p-6 space-y-6">
                                        <div className="p-5 rounded-2xl bg-primary/10 border border-primary/20 shadow-lg shadow-primary/5">
                                            <div className="text-[9px] uppercase text-primary font-black tracking-widest mb-1.5">ΔG (Binding Energy)</div>
                                            <div className="text-3xl font-black text-primary">-8.4 <span className="text-sm font-medium opacity-60">kcal/mol</span></div>
                                            <div className="flex items-center gap-2 mt-3">
                                                <Badge className="bg-primary/20 text-primary border-primary/20 text-[9px] font-black">HIGH_CONFIDENCE</Badge>
                                                <span className="text-[9px] font-black uppercase tracking-widest text-white/30">Node: AutoDock Vina</span>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-3">
                                            {[
                                                { label: "H-Bonds", val: "4 Sites", color: "text-blue-400", bg: "bg-blue-400/10", border: "border-blue-400/20" },
                                                { label: "Pi-Stacking", val: "2 Contacts", color: "text-orange-400", bg: "bg-orange-400/10", border: "border-orange-400/20" },
                                                { label: "Hydrophobic", val: "6 Contacts", color: "text-green-400", bg: "bg-green-400/10", border: "border-green-400/20" },
                                                { label: "Salt Bridge", val: "1 Site", color: "text-purple-400", bg: "bg-purple-400/10", border: "border-purple-400/20" }
                                            ].map((item, idx) => (
                                                <div key={idx} className={cn("p-4 rounded-2xl border transition-all hover:scale-[1.02]", item.bg, item.border)}>
                                                    <div className={cn("text-[9px] font-black uppercase tracking-widest opacity-60 mb-1", item.color)}>{item.label}</div>
                                                    <div className={cn("text-base font-black truncate", item.color)}>{item.val}</div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-white/5 border border-white/10 rounded-[32px] overflow-hidden backdrop-blur-xl">
                                    <div className="p-5 border-b border-white/10 bg-white/5">
                                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-primary flex items-center gap-2">
                                            <Layers className="h-4 w-4" />
                                            Active Site Residues
                                        </h3>
                                    </div>
                                    <div className="p-6 flex flex-wrap gap-2">
                                        {["TRP84", "TYR121", "SER122", "GLY123", "PHE330", "TYR334", "HIS440", "GLU199"].map((residue) => (
                                            <Badge
                                                key={residue}
                                                className="bg-white/5 hover:bg-white/10 text-white/60 hover:text-white border-white/10 font-mono text-[10px] px-3 py-1.5 transition-all cursor-default"
                                            >
                                                {residue}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            </TabsContent>

                            <TabsContent value="annotations" className="m-0 p-6 space-y-6">
                                <div className="bg-white/5 border border-white/10 rounded-[32px] overflow-hidden backdrop-blur-xl">
                                    <div className="p-5 border-b border-white/10 bg-white/5">
                                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-primary flex items-center gap-2">
                                            <Microscope className="h-4 w-4" />
                                            Structural Anatomy
                                        </h3>
                                    </div>
                                    <div className="p-6 space-y-3">
                                        {[
                                            { label: "Alpha Helices", val: "12" },
                                            { label: "Beta Sheets", val: "8" },
                                            { label: "Binding Pockets", val: "3" },
                                            { label: "Disulfide Bonds", val: "2" }
                                        ].map((item, idx) => (
                                            <div key={idx} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 group hover:bg-white/10 transition-all">
                                                <span className="text-sm font-bold text-white/60 group-hover:text-white transition-colors">{item.label}</span>
                                                <Badge className="bg-primary/10 text-primary border-primary/20 font-black">{item.val}</Badge>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </TabsContent>
                        </div>
                    </Tabs>
                </div>
            </div>
        </div>
    );
}
