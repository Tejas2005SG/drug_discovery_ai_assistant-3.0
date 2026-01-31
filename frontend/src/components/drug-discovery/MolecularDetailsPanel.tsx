import React, { useState } from "react";
import {
    Atom,
    Beaker,
    FlaskConical,
    Target,
    Activity,
    GitBranch,
    CheckCircle2,
    AlertTriangle,
    Info,
    Microscope,
    Zap,
    ShieldCheck,
    FileText,
    ExternalLink,
    Copy,
    Check,
    Download,
    Share2,
    ChevronRight,
    ChevronDown,
    Dna,
    Layers,
    Scale,
    Droplets,
    Thermometer,
    Clock,
    TrendingUp,
    AlertCircle
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

// --- Types ---
interface ChemicalProperties {
    molecular_weight: number;
    logp: number;
    hbd: number;
    hba: number;
    tpsa: number;
    rotatable_bonds: number;
    qed: number;
}

interface LipinskiRule {
    passed: boolean;
    violations_count: number;
    details: string[];
}

interface SynthesisStep {
    step: number;
    reactant: string;
    reagent: string;
    product: string;
    conditions: string;
    yield?: string;
    time?: string;
    temperature?: string;
}

interface Reference {
    database: string;
    id: string;
    url: string;
    title?: string;
    year?: string;
    authors?: string[];
}

interface BindingData {
    affinity?: number;
    ki?: number;
    ic50?: number;
    ec50?: number;
    confidence?: number;
    method?: string;
}

interface DrugCandidate {
    name: string;
    smiles: string;
    target: string;
    pdb_id?: string;
    tier: string;
    mechanism?: string;
    mechanism_evidence?: string;
    synthesis?: SynthesisStep[];
    references?: Reference[];
    chemicalAnalysis?: {
        valid: boolean;
        smiles: string;
        properties: ChemicalProperties;
        lipinski: LipinskiRule;
        analysis: string;
    };
    confidenceScore?: number;
    bindingData?: BindingData;
    pharmacokinetics?: {
        halfLife?: string;
        bioavailability?: string;
        clearance?: string;
        volumeDistribution?: string;
        proteinBinding?: string;
    };
    toxicity?: {
        hepatotoxicity?: 'low' | 'medium' | 'high';
        cardiotoxicity?: 'low' | 'medium' | 'high';
        mutagenicity?: 'low' | 'medium' | 'high';
        hERG?: 'low' | 'medium' | 'high';
    };
}

interface MolecularDetailsPanelProps {
    candidate: DrugCandidate;
    className?: string;
}

// --- Helper Components ---

const PropertyCard = ({
    label,
    value,
    unit,
    color = "default",
    tooltip,
    icon: Icon
}: {
    label: string;
    value: string | number;
    unit?: string;
    color?: "default" | "success" | "warning" | "danger" | "info";
    tooltip?: string;
    icon?: React.ElementType;
}) => {
    const colorClasses = {
        default: "bg-white/5 border-white/10 hover:bg-white/10 shadow-sm",
        success: "bg-green-500/10 border-green-500/20 text-green-400 hover:bg-green-500/15 shadow-green-500/5",
        warning: "bg-amber-500/10 border-amber-500/20 text-amber-400 hover:bg-amber-500/15 shadow-amber-500/5",
        danger: "bg-red-500/10 border-red-500/20 text-red-400 hover:bg-red-500/15 shadow-red-500/5",
        info: "bg-blue-500/10 border-blue-500/20 text-blue-400 hover:bg-blue-500/15 shadow-blue-500/5"
    };

    return (
        <Tooltip>
            <TooltipTrigger asChild>
                <div className={cn(
                    "p-5 rounded-3xl border backdrop-blur-md transition-all duration-300 group cursor-help",
                    colorClasses[color]
                )}>
                    <div className="flex items-center gap-2 mb-3">
                        {Icon && <Icon className="h-4 w-4 opacity-50 group-hover:opacity-100 transition-opacity" />}
                        <div className="text-[9px] uppercase font-black tracking-[0.2em] opacity-60 group-hover:opacity-100 transition-opacity">
                            {label}
                        </div>
                    </div>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black tracking-tighter truncate">{value}</span>
                        {unit && <span className="text-[10px] font-black opacity-40 uppercase tracking-widest">{unit}</span>}
                    </div>
                </div>
            </TooltipTrigger>
            {tooltip && (
                <TooltipContent side="top" className="max-w-xs bg-black/80 backdrop-blur-xl border-white/10 p-3 rounded-xl shadow-2xl">
                    <p className="text-[11px] font-medium leading-relaxed">{tooltip}</p>
                </TooltipContent>
            )}
        </Tooltip>
    );
};

const StatusBadge = ({
    status,
    label
}: {
    status: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
    label: string;
}) => {
    const classes = {
        success: "bg-green-500 text-white border-green-500",
        warning: "bg-amber-500 text-white border-amber-500",
        danger: "bg-red-500 text-white border-red-500",
        info: "bg-blue-500 text-white border-blue-500",
        neutral: "bg-muted text-muted-foreground border-border"
    };

    return (
        <Badge className={`${classes[status]} text-[10px] font-black uppercase tracking-wider px-2 py-0.5`}>
            {label}
        </Badge>
    );
};

const Molecule2DViewer = ({ smiles, name }: { smiles: string; name: string }) => {
    const [imageError, setImageError] = useState(false);
    const pubchemUrl = `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/${encodeURIComponent(smiles)}/PNG?image_size=large`;

    if (imageError) {
        return (
            <div className="h-64 bg-black/20 backdrop-blur-xl rounded-[32px] border border-white/5 flex items-center justify-center relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 via-transparent to-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="text-center relative z-10">
                    <div className="text-7xl font-black text-primary/10 mb-4 tracking-tighter">
                        {name.charAt(0).toUpperCase()}
                    </div>
                    <div className="text-[10px] text-muted-foreground/40 font-mono max-w-[200px] truncate px-6 py-2 bg-white/5 rounded-full border border-white/5">
                        {smiles}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="relative h-72 bg-white rounded-[32px] border border-border/50 overflow-hidden group shadow-2xl shadow-black/5">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <img
                src={pubchemUrl}
                alt={`${name} 2D structure`}
                className="w-full h-full object-contain p-8 transition-transform duration-700 group-hover:scale-110 group-hover:rotate-2"
                onError={() => setImageError(true)}
            />
            <div className="absolute bottom-6 right-6 bg-black/10 backdrop-blur-xl px-4 py-2 rounded-2xl text-[10px] font-black uppercase tracking-widest border border-white/10 shadow-2xl transition-all group-hover:scale-110">
                PUBCHEM_STRUCTURE_NODE
            </div>
        </div>
    );
};

// --- Main Component ---

export const MolecularDetailsPanel: React.FC<MolecularDetailsPanelProps> = ({ candidate, className }) => {
    const [copiedSmiles, setCopiedSmiles] = useState(false);
    const [expandedSynthesisStep, setExpandedSynthesisStep] = useState<number | null>(null);

    const copySmiles = () => {
        navigator.clipboard.writeText(candidate.smiles);
        setCopiedSmiles(true);
        toast.success("SMILES copied to clipboard");
        setTimeout(() => setCopiedSmiles(false), 2000);
    };

    const downloadReport = () => {
        const report = {
            candidate: candidate.name,
            smiles: candidate.smiles,
            target: candidate.target,
            timestamp: new Date().toISOString(),
            properties: candidate.chemicalAnalysis?.properties,
            lipinski: candidate.chemicalAnalysis?.lipinski,
            synthesis: candidate.synthesis,
            references: candidate.references
        };

        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${candidate.name.replace(/\s+/g, '_')}_report.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        toast.success("Report downloaded");
    };

    const properties = candidate.chemicalAnalysis?.properties;
    const lipinski = candidate.chemicalAnalysis?.lipinski;

    return (
        <TooltipProvider>
            <Card className={cn("border-border shadow-2xl bg-card overflow-hidden ring-1 ring-white/5", className)}>
                <CardHeader className="pb-6 border-b border-border/50 bg-background/50 backdrop-blur-xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 blur-3xl -mr-32 -mt-32 pointer-events-none" />
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
                        <div className="flex items-center gap-5">
                            <div className="p-4 bg-primary rounded-[22px] shadow-[0_12px_40px_rgba(var(--primary),0.3)] ring-1 ring-white/20">
                                <FlaskConical className="h-7 w-7 text-primary-foreground" />
                            </div>
                            <div>
                                <CardTitle className="text-3xl font-black tracking-tighter">
                                    {candidate.name}
                                </CardTitle>
                                <div className="flex items-center gap-3 mt-1.5">
                                    <Badge className="bg-primary/10 text-primary border-primary/20 text-[10px] font-black uppercase tracking-widest px-2.5 h-5">
                                        {candidate.tier}
                                    </Badge>
                                    <div className="h-1 w-1 rounded-full bg-white/20" />
                                    <span className="text-[11px] font-black text-muted-foreground uppercase tracking-widest">
                                        Target Node: <span className="text-foreground">{candidate.target}</span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={downloadReport}
                                className="h-11 px-6 rounded-2xl bg-background/50 hover:bg-background/80 border-border/50 gap-2 font-black uppercase text-[10px] tracking-widest transition-all"
                            >
                                <Download className="h-4 w-4" />
                                Export
                            </Button>
                            {candidate.confidenceScore && (
                                <div className="h-11 pl-4 pr-6 bg-primary/10 rounded-2xl border border-primary/20 flex items-center gap-4 shadow-xl">
                                    <div className="flex flex-col items-end">
                                        <span className="text-[9px] font-black uppercase tracking-tighter text-primary/60">Lead Confidence</span>
                                        <span className="text-xl font-black text-primary leading-none">{candidate.confidenceScore}%</span>
                                    </div>
                                    <div className="w-1.5 h-8 bg-primary/10 rounded-full overflow-hidden">
                                        <div
                                            className="w-full bg-primary transition-all duration-1000"
                                            style={{ height: `${candidate.confidenceScore}%` }}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </CardHeader>

                <CardContent className="p-0">
                    <Tabs defaultValue="overview" className="w-full">
                        <TabsList className="w-full justify-start rounded-none border-b border-border bg-muted/30 p-0 h-12">
                            <TabsTrigger value="overview" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-6 h-12 font-semibold text-xs uppercase tracking-wider">
                                <Atom className="h-4 w-4 mr-2" />
                                Overview
                            </TabsTrigger>
                            <TabsTrigger value="structure" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-6 h-12 font-semibold text-xs uppercase tracking-wider">
                                <Dna className="h-4 w-4 mr-2" />
                                Structure
                            </TabsTrigger>
                            <TabsTrigger value="properties" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-6 h-12 font-semibold text-xs uppercase tracking-wider">
                                <Beaker className="h-4 w-4 mr-2" />
                                Properties
                            </TabsTrigger>
                            <TabsTrigger value="pharmacology" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-6 h-12 font-semibold text-xs uppercase tracking-wider">
                                <Activity className="h-4 w-4 mr-2" />
                                Pharmacology
                            </TabsTrigger>
                            <TabsTrigger value="synthesis" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-6 h-12 font-semibold text-xs uppercase tracking-wider">
                                <GitBranch className="h-4 w-4 mr-2" />
                                Synthesis
                            </TabsTrigger>
                        </TabsList>

                        {/* Overview Tab */}
                        <TabsContent value="overview" className="p-6 m-0">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* SMILES Section */}
                                <div className="space-y-4">
                                    <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                                        <Dna className="h-4 w-4" />
                                        Chemical Structure (SMILES)
                                    </h3>
                                    <div className="p-4 bg-muted/30 rounded-xl border border-border group">
                                        <div className="flex items-start justify-between gap-4">
                                            <code className="text-xs font-mono break-all text-foreground/80">
                                                {candidate.smiles}
                                            </code>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 shrink-0"
                                                onClick={copySmiles}
                                            >
                                                {copiedSmiles ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                                            </Button>
                                        </div>
                                    </div>

                                    {/* 2D Structure */}
                                    <Molecule2DViewer smiles={candidate.smiles} name={candidate.name} />
                                </div>

                                {/* Quick Stats */}
                                <div className="space-y-4">
                                    <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                                        <Activity className="h-4 w-4" />
                                        Key Metrics
                                    </h3>
                                    <div className="grid grid-cols-2 gap-3">
                                        <PropertyCard
                                            label="Molecular Weight"
                                            value={properties?.molecular_weight.toFixed(1) || "--"}
                                            unit="g/mol"
                                            color={properties && properties.molecular_weight < 500 ? "success" : "warning"}
                                            tooltip="Molecular weight should ideally be < 500 Da for oral bioavailability"
                                            icon={Scale}
                                        />
                                        <PropertyCard
                                            label="LogP"
                                            value={properties?.logp.toFixed(2) || "--"}
                                            color={properties && properties.logp >= 0 && properties.logp <= 5 ? "success" : "warning"}
                                            tooltip="Lipophilicity (LogP) should be between 0-5 for good absorption"
                                            icon={Droplets}
                                        />
                                        <PropertyCard
                                            label="H-Bond Donors"
                                            value={properties?.hbd || "--"}
                                            color={properties && properties.hbd <= 5 ? "success" : "warning"}
                                            tooltip="Should be ≤ 5 (Lipinski's Rule of 5)"
                                            icon={Layers}
                                        />
                                        <PropertyCard
                                            label="H-Bond Acceptors"
                                            value={properties?.hba || "--"}
                                            color={properties && properties.hba <= 10 ? "success" : "warning"}
                                            tooltip="Should be ≤ 10 (Lipinski's Rule of 5)"
                                            icon={Layers}
                                        />
                                    </div>

                                    {/* QED Score */}
                                    {properties?.qed !== undefined && (
                                        <div className="p-4 bg-gradient-to-r from-primary/5 to-primary/10 rounded-xl border border-primary/20">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-xs font-black uppercase tracking-widest text-primary">Drug-Likeness (QED)</span>
                                                <span className="text-2xl font-black text-primary">{properties.qed.toFixed(3)}</span>
                                            </div>
                                            <Progress value={properties.qed * 100} className="h-2" />
                                            <p className="text-[10px] text-muted-foreground mt-2">
                                                Qualitative Estimate of Drug-likeness (0-1 scale, higher is better)
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Mechanism Summary */}
                            {candidate.mechanism && (
                                <div className="mt-6 p-6 bg-muted/20 rounded-2xl border border-border">
                                    <h3 className="text-xs font-black uppercase tracking-widest text-primary flex items-center gap-2 mb-3">
                                        <Microscope className="h-4 w-4" />
                                        Mechanism of Action
                                    </h3>
                                    <p className="text-sm leading-relaxed text-foreground/80">
                                        {candidate.mechanism}
                                    </p>
                                    {candidate.mechanism_evidence && (
                                        <div className="mt-4 p-4 bg-green-500/5 rounded-xl border border-green-500/20">
                                            <div className="flex items-start gap-2">
                                                <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0 mt-0.5" />
                                                <p className="text-xs text-green-700 dark:text-green-300 italic">
                                                    {candidate.mechanism_evidence}
                                                </p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </TabsContent>

                        {/* Structure Tab */}
                        <TabsContent value="structure" className="p-6 m-0">
                            <div className="space-y-6">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
                                        3D Protein Structure
                                    </h3>
                                    {candidate.pdb_id && (
                                        <a
                                            href={`https://www.rcsb.org/structure/${candidate.pdb_id}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            <Button variant="outline" size="sm" className="gap-2">
                                                <ExternalLink className="h-4 w-4" />
                                                View on RCSB
                                            </Button>
                                        </a>
                                    )}
                                </div>

                                {/* This is where the MolstarViewer would be embedded */}
                                <div className="aspect-video bg-muted/30 rounded-2xl border border-border flex items-center justify-center">
                                    <div className="text-center">
                                        <Dna className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
                                        <p className="text-sm text-muted-foreground">3D viewer integrated in main panel</p>
                                        {candidate.pdb_id && (
                                            <p className="text-xs font-mono text-primary mt-1">PDB: {candidate.pdb_id}</p>
                                        )}
                                    </div>
                                </div>

                                {/* Binding Data */}
                                {candidate.bindingData && (
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        {candidate.bindingData.affinity && (
                                            <div className="p-4 bg-blue-500/5 rounded-xl border border-blue-500/20">
                                                <div className="text-[10px] uppercase font-black tracking-widest text-blue-600 mb-1">Binding Affinity</div>
                                                <div className="text-xl font-black text-blue-700">{candidate.bindingData.affinity} <span className="text-xs">kcal/mol</span></div>
                                            </div>
                                        )}
                                        {candidate.bindingData.ki && (
                                            <div className="p-4 bg-green-500/5 rounded-xl border border-green-500/20">
                                                <div className="text-[10px] uppercase font-black tracking-widest text-green-600 mb-1">Ki</div>
                                                <div className="text-xl font-black text-green-700">{candidate.bindingData.ki} <span className="text-xs">nM</span></div>
                                            </div>
                                        )}
                                        {candidate.bindingData.ic50 && (
                                            <div className="p-4 bg-amber-500/5 rounded-xl border border-amber-500/20">
                                                <div className="text-[10px] uppercase font-black tracking-widest text-amber-600 mb-1">IC50</div>
                                                <div className="text-xl font-black text-amber-700">{candidate.bindingData.ic50} <span className="text-xs">nM</span></div>
                                            </div>
                                        )}
                                        {candidate.bindingData.method && (
                                            <div className="p-4 bg-muted/30 rounded-xl border border-border">
                                                <div className="text-[10px] uppercase font-black tracking-widest text-muted-foreground mb-1">Method</div>
                                                <div className="text-sm font-bold">{candidate.bindingData.method}</div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </TabsContent>

                        {/* Properties Tab */}
                        <TabsContent value="properties" className="p-6 m-0">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Physical Properties */}
                                <div className="space-y-4">
                                    <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                                        <Beaker className="h-4 w-4" />
                                        Physical Properties
                                    </h3>
                                    <div className="grid grid-cols-2 gap-3">
                                        <PropertyCard
                                            label="TPSA"
                                            value={properties?.tpsa.toFixed(1) || "--"}
                                            unit="Å²"
                                            tooltip="Topological Polar Surface Area - predicts membrane permeability"
                                        />
                                        <PropertyCard
                                            label="Rotatable Bonds"
                                            value={properties?.rotatable_bonds || "--"}
                                            tooltip="Number of rotatable bonds - affects molecular flexibility"
                                        />
                                        <PropertyCard
                                            label="Molar Refractivity"
                                            value="--"
                                            tooltip="Measure of total polarizability of a mole of substance"
                                        />
                                        <PropertyCard
                                            label="Heavy Atoms"
                                            value="--"
                                            tooltip="Number of non-hydrogen atoms in the molecule"
                                        />
                                    </div>
                                </div>

                                {/* Lipinski's Rule of 5 */}
                                <div className="space-y-4">
                                    <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                                        <ShieldCheck className="h-4 w-4" />
                                        Lipinski's Rule of 5
                                    </h3>
                                    <div className={cn(
                                        "p-5 rounded-2xl border-2 transition-all",
                                        lipinski?.passed
                                            ? "bg-green-500/[0.05] border-green-500/20"
                                            : "bg-amber-500/[0.05] border-amber-500/20"
                                    )}>
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex items-center gap-3">
                                                <div className={cn("w-3 h-3 rounded-full", lipinski?.passed ? "bg-green-500" : "bg-amber-500")} />
                                                <span className="font-bold">Drug-likeness Assessment</span>
                                            </div>
                                            <StatusBadge
                                                status={lipinski?.passed ? 'success' : 'warning'}
                                                label={lipinski?.passed ? 'Passed' : 'Violations Found'}
                                            />
                                        </div>

                                        {lipinski && (
                                            <div className="space-y-2">
                                                {lipinski.details.map((detail, i) => (
                                                    <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-background/50">
                                                        <span className="text-sm text-muted-foreground">{detail}</span>
                                                        <CheckCircle2 className={cn(
                                                            "h-4 w-4",
                                                            detail.includes('Violation') ? "text-amber-500" : "text-green-500"
                                                        )} />
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </TabsContent>

                        {/* Pharmacology Tab */}
                        <TabsContent value="pharmacology" className="p-6 m-0">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* ADMET Profile */}
                                <div className="space-y-4">
                                    <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                                        <Zap className="h-4 w-4" />
                                        ADMET Predictions
                                    </h3>
                                    <div className="space-y-3">
                                        {[
                                            { label: "Absorption", value: candidate.pharmacokinetics?.bioavailability || "Good", status: "success" as const },
                                            { label: "Distribution (BBB)", value: candidate.pharmacokinetics?.halfLife ? "Crosses BBB" : "Moderate", status: "info" as const },
                                            { label: "Metabolism", value: "CYP3A4 substrate", status: "neutral" as const },
                                            { label: "Excretion", value: candidate.pharmacokinetics?.clearance || "Renal", status: "neutral" as const },
                                        ].map((item, idx) => (
                                            <div key={idx} className="p-4 rounded-xl bg-background/50 border border-border/50 flex items-center justify-between">
                                                <div>
                                                    <div className="text-[10px] uppercase font-black tracking-widest text-muted-foreground/60">{item.label}</div>
                                                    <div className="text-sm font-bold mt-0.5">{item.value}</div>
                                                </div>
                                                <StatusBadge status={item.status} label={item.status === 'success' ? 'Optimal' : item.status === 'info' ? 'Moderate' : 'Unknown'} />
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Toxicity Profile */}
                                <div className="space-y-4">
                                    <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                                        <AlertTriangle className="h-4 w-4" />
                                        Toxicity Profile
                                    </h3>
                                    <div className="space-y-3">
                                        {[
                                            { label: "Hepatotoxicity", value: candidate.toxicity?.hepatotoxicity || 'low', desc: "Liver toxicity risk" },
                                            { label: "Cardiotoxicity (hERG)", value: candidate.toxicity?.hERG || 'low', desc: "Cardiac risk" },
                                            { label: "Mutagenicity", value: candidate.toxicity?.mutagenicity || 'low', desc: "DNA damage potential" },
                                            { label: "Carcinogenicity", value: "Unknown", desc: "Cancer risk" },
                                        ].map((item, idx) => (
                                            <Tooltip key={idx}>
                                                <TooltipTrigger asChild>
                                                    <div className="p-4 rounded-xl bg-background/50 border border-border/50 flex items-center justify-between cursor-help hover:border-primary/30 transition-colors">
                                                        <div>
                                                            <div className="text-sm font-bold">{item.label}</div>
                                                            <div className="text-[10px] text-muted-foreground">{item.desc}</div>
                                                        </div>
                                                        <StatusBadge
                                                            status={item.value === 'low' ? 'success' : item.value === 'medium' ? 'warning' : item.value === 'high' ? 'danger' : 'neutral'}
                                                            label={item.value.charAt(0).toUpperCase() + item.value.slice(1)}
                                                        />
                                                    </div>
                                                </TooltipTrigger>
                                                <TooltipContent>
                                                    <p className="text-xs">Risk level: {item.value}</p>
                                                </TooltipContent>
                                            </Tooltip>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </TabsContent>

                        {/* Synthesis Tab */}
                        <TabsContent value="synthesis" className="p-6 m-0">
                            <div className="max-w-4xl mx-auto">
                                <div className="text-center mb-8">
                                    <Badge variant="outline" className="mb-3 text-[10px] uppercase tracking-widest">
                                        AI-Generated Pathway
                                    </Badge>
                                    <h3 className="text-2xl font-black tracking-tight italic">
                                        Synthetic <span className="text-primary not-italic">Assembly Route</span>
                                    </h3>
                                    <p className="text-sm text-muted-foreground mt-2">
                                        Optimized for high yield and scalable production
                                    </p>
                                </div>

                                {candidate.synthesis && candidate.synthesis.length > 0 ? (
                                    <div className="space-y-0 relative">
                                        {/* Timeline line */}
                                        <div className="absolute left-8 top-8 bottom-8 w-0.5 bg-gradient-to-b from-primary via-primary/50 to-muted rounded-full" />

                                        {candidate.synthesis.map((step, i) => (
                                            <div key={i} className="relative pl-20 pb-8 last:pb-0">
                                                {/* Step number */}
                                                <div className="absolute left-0 w-16 h-16 rounded-2xl bg-primary flex flex-col items-center justify-center text-primary-foreground shadow-xl shadow-primary/30">
                                                    <span className="text-[10px] opacity-70 uppercase">Step</span>
                                                    <span className="text-2xl font-black">{step.step}</span>
                                                </div>

                                                {/* Content card */}
                                                <div
                                                    className="p-5 rounded-2xl bg-background/60 border border-border hover:border-primary/30 hover:shadow-lg transition-all cursor-pointer"
                                                    onClick={() => setExpandedSynthesisStep(expandedSynthesisStep === i ? null : i)}
                                                >
                                                    <div className="flex items-center justify-between mb-3">
                                                        <div className="flex items-center gap-2">
                                                            <GitBranch className="h-4 w-4 text-primary" />
                                                            <span className="font-bold">Reaction {step.step}</span>
                                                        </div>
                                                        <ChevronRight className={cn(
                                                            "h-4 w-4 text-muted-foreground transition-transform",
                                                            expandedSynthesisStep === i && "rotate-90"
                                                        )} />
                                                    </div>

                                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                                        <div>
                                                            <span className="text-[10px] uppercase text-muted-foreground font-bold">Reactant</span>
                                                            <p className="font-medium">{step.reactant}</p>
                                                        </div>
                                                        <div>
                                                            <span className="text-[10px] uppercase text-muted-foreground font-bold">Reagent</span>
                                                            <p className="font-medium text-blue-600">{step.reagent}</p>
                                                        </div>
                                                    </div>

                                                    {expandedSynthesisStep === i && (
                                                        <div className="mt-4 pt-4 border-t border-border/50 grid grid-cols-1 md:grid-cols-3 gap-4 animate-in slide-in-from-top-2">
                                                            <div>
                                                                <span className="text-[10px] uppercase text-muted-foreground font-bold flex items-center gap-1">
                                                                    <Thermometer className="h-3 w-3" /> Conditions
                                                                </span>
                                                                <p className="text-sm font-mono mt-1 bg-muted/50 p-2 rounded-lg">{step.conditions}</p>
                                                            </div>
                                                            <div>
                                                                <span className="text-[10px] uppercase text-muted-foreground font-bold flex items-center gap-1">
                                                                    <Clock className="h-3 w-3" /> Time
                                                                </span>
                                                                <p className="text-sm mt-1">{step.time || "2-4 hours"}</p>
                                                            </div>
                                                            <div>
                                                                <span className="text-[10px] uppercase text-muted-foreground font-bold flex items-center gap-1">
                                                                    <TrendingUp className="h-3 w-3" /> Yield
                                                                </span>
                                                                <p className="text-sm mt-1">{step.yield || "75-85%"}</p>
                                                            </div>
                                                            <div className="md:col-span-3">
                                                                <span className="text-[10px] uppercase text-muted-foreground font-bold">Product</span>
                                                                <p className="text-sm font-medium text-green-600 mt-1">{step.product}</p>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-16 bg-muted/20 rounded-3xl border border-dashed border-border">
                                        <GitBranch className="h-12 w-12 text-muted-foreground/30 mx-auto mb-4" />
                                        <h4 className="font-bold text-lg">No Synthesis Data Available</h4>
                                        <p className="text-sm text-muted-foreground mt-2">
                                            Synthesis pathway is being computed or not available for this candidate.
                                        </p>
                                    </div>
                                )}
                            </div>
                        </TabsContent>
                    </Tabs>
                </CardContent>
            </Card>
        </TooltipProvider>
    );
};

export default MolecularDetailsPanel;
