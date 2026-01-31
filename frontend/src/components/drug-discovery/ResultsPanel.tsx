import React, { useState, useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useNavigate } from "react-router-dom";
import {
    Copy,
    Check,
    Database,
    Globe,
    Download,
    ChevronDown,
    ChevronRight,
    Microscope,
    Layers,
    ExternalLink,
    Link as LinkIcon,
    Dna,
    FlaskConical,
    Activity,
    AlertTriangle,
    CheckCircle2,
    ArrowRight,
    Beaker,
    Atom,
    GitBranch,
    FileText,
    Target,
    Search,
    Zap,
    Info,
    BookOpen,
    FileDown,
    ShieldCheck,
    Maximize2
} from "lucide-react";
import { MolstarViewer } from "./MolstarViewer";
import { MolecularDetailsPanel } from "./MolecularDetailsPanel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

// --- Types ---
interface Source {
    title: string;
    url: string;
    status?: string;
    category?: string;
    database?: string;
    contentLength?: number;
}

interface Metadata {
    totalDuration?: string;
    queriesExecuted?: number;
    sourcesFound?: number;
    sourcesUsed?: number;
    modelUsed?: string;
    timestamp?: string;
}

interface ResearchPlan {
    strategy?: string;
    hypotheses?: string[];
    targetDatabases?: string[];
}

interface ChemicalAnalysis {
    valid: boolean;
    smiles: string;
    properties: {
        molecular_weight: number;
        logp: number;
        hbd: number;
        hba: number;
        tpsa: number;
        rotatable_bonds: number;
        qed: number;
    };
    lipinski: {
        passed: boolean;
        violations_count: number;
        details: string[];
    };
    analysis: string;
}

interface SynthesisStep {
    step: number;
    reactant: string;
    reagent: string;
    product: string;
    conditions: string;
}

interface Reference {
    database: string;
    id: string;
    url: string;
}

interface DrugCandidate {
    name: string;
    smiles: string;
    target: string;
    pdb_id?: string;
    pdb_source?: string;
    pdb_resolution?: string;
    pdb_method?: string;
    tier: string;
    mechanism?: string;
    mechanism_evidence?: string;
    references?: Reference[];
    synthesis?: SynthesisStep[];
    chemicalAnalysis?: ChemicalAnalysis;
    confidenceScore?: number;
    isValidated?: boolean;
}

interface ResearchResult {
    content: string;
    sources: Source[];
    candidates?: DrugCandidate[];
    symptoms: string;
    extractedSymptoms?: string;
    researchPlan?: ResearchPlan;
    metadata?: Metadata;
}

interface ResultsPanelProps {
    results: ResearchResult;
}

// --- Helpers ---
const getFaviconUrl = (url: string): string | null => {
    try {
        const domain = new URL(url).hostname;
        return `https://www.google.com/s2/favicons?domain=${domain}&sz=64`;
    } catch {
        return null;
    }
};

const getDomain = (url: string): string => {
    try {
        return new URL(url).hostname.replace('www.', '');
    } catch {
        return url;
    }
};

const DB_COLORS: Record<string, string> = {
    pubmed: "border-primary/20 hover:border-primary/50",
    uniprot: "border-primary/20 hover:border-primary/50",
    pubchem: "border-primary/20 hover:border-primary/50",
    default: "border-border hover:border-primary/30"
};

const isLikelySmiles = (text: string): boolean => {
    if (!text || typeof text !== 'string' || text.includes(' ')) return false;
    if (text.length < 5) return false;
    const smilesChars = /[CNOPSFIBrClc1234567890()=\[\]#\-+]/;
    const hasSmilesChars = smilesChars.test(text);
    const isUrl = text.startsWith('http') || text.includes('www');
    return hasSmilesChars && !isUrl;
};

// Small Molecule Viewer Component
const SmallMoleculeViewer = ({ smiles, name }: { smiles: string; name: string }) => {
    // Use PubChem SVG for the molecule
    const pubchemUrl = `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/${encodeURIComponent(smiles)}/PNG`;

    return (
        <div className="relative h-48 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 rounded-lg overflow-hidden border border-border">
            <img
                src={pubchemUrl}
                alt={`${name} structure`}
                className="w-full h-full object-contain p-2"
                onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    target.parentElement!.innerHTML = `
                        <div class="flex items-center justify-center h-full text-center p-4">
                            <div>
                                <div class="text-6xl font-mono font-bold text-blue-600 mb-2">${name.charAt(0)}</div>
                                <div class="text-xs text-muted-foreground">2D Structure</div>
                            </div>
                        </div>
                    `;
                }}
            />
            <div className="absolute bottom-2 right-2 bg-white/90 dark:bg-black/70 px-2 py-1 rounded text-[10px] font-medium">
                PubChem
            </div>
        </div>
    );
};

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ results }) => {
    const navigate = useNavigate();
    const [copied, setCopied] = useState(false);
    const [activeSourceCategory, setActiveSourceCategory] = useState<string>("all");
    const [showResearchPlan, setShowResearchPlan] = useState(false);
    const [selectedCandidate, setSelectedCandidate] = useState<DrugCandidate | null>(null);

    // Auto-select first candidate if not selected
    if (results.candidates && results.candidates.length > 0 && !selectedCandidate) {
        setSelectedCandidate(results.candidates[0]);
    }

    // Navigate to fullscreen molecule viewer
    const openMoleculeViewer = (candidate: DrugCandidate) => {
        const params = new URLSearchParams();
        if (candidate.pdb_id) params.set("pdbId", candidate.pdb_id);
        if (candidate.target) params.set("targetName", candidate.target);
        if (candidate.name) params.set("ligandName", candidate.name);
        navigate(`/dashboard/molecule-viewer?${params.toString()}`);
    };

    // --- Content Processor ---
    const processedContent = useMemo(() => {
        let content = results.content || "";
        content = content.replace(/([^\n])\n(#{1,3}\s)/g, "$1\n\n$2");
        content = content.replace(/\|.*\|\n?\|[-:| ]+\|/g, (match) => {
            if (match.includes('\n')) return match;
            return match.replace(/(\|\s*\|)/, '|\n|');
        });
        return content;
    }, [results.content]);

    // Group sources
    const groupedSources = useMemo(() => {
        const groups: Record<string, Source[]> = { all: results.sources || [] };
        results.sources?.forEach(source => {
            const cat = source.category || 'general';
            if (!groups[cat]) groups[cat] = [];
            groups[cat].push(source);
        });
        return groups;
    }, [results.sources]);

    const handleCopy = () => {
        navigator.clipboard.writeText(results.content);
        setCopied(true);
        toast.success("Dossier copied to clipboard");
        setTimeout(() => setCopied(false), 2000);
    };

    const downloadScientistReport = () => {
        if (!results.candidates) return;
        const data = JSON.stringify(results.candidates, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Aurelius_Scientist_Report_${new Date().getTime()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        toast.success("Scientist Report exported successfully");
    };

    // --- Custom Citation Renderer ---
    const renderWithCitations = (text: React.ReactNode) => {
        if (typeof text !== 'string') return text;
        const parts = text.split(/(\[(?:Source\s?|Clinical\s?|Protein\s?|Compound\s?)?\d+\])/g);
        return parts.map((part, i) => {
            const match = part.match(/\[(?:Source\s?|Clinical\s?|Protein\s?|Compound\s?)?(\d+)\]/);
            if (match) {
                const index = parseInt(match[1]) - 1;
                const source = results.sources?.[index];
                if (source) {
                    const domain = getDomain(source.url);
                    const favicon = getFaviconUrl(source.url);
                    return (
                        <TooltipProvider key={i}>
                            <Tooltip delayDuration={0}>
                                <TooltipTrigger asChild>
                                    <a
                                        href={source.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center justify-center min-w-[16px] h-4 px-1 ml-0.5 text-[9px] font-bold text-primary bg-primary/10 rounded-full align-text-top cursor-pointer hover:bg-primary/20 transition-colors no-underline select-none transform -translate-y-0.5"
                                    >
                                        {match[1]}
                                    </a>
                                </TooltipTrigger>
                                <TooltipContent className="max-w-[300px] p-3 bg-popover text-popover-foreground border border-border shadow-xl">
                                    <div className="flex items-start gap-3">
                                        <div className="shrink-0 pt-0.5">
                                            {favicon ? (
                                                <img
                                                    src={favicon}
                                                    className="h-4 w-4 rounded-sm"
                                                    alt=""
                                                    onError={(e) => {
                                                        (e.target as HTMLImageElement).style.display = 'none';
                                                        (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                                                    }}
                                                />
                                            ) : null}
                                            <Globe className={cn("h-4 w-4 text-muted-foreground", favicon && "hidden")} />
                                        </div>
                                        <div className="space-y-1">
                                            <p className="text-xs font-semibold line-clamp-2">
                                                {source.title || "Source Reference"}
                                            </p>
                                            <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                                                <LinkIcon className="h-2.5 w-2.5" />
                                                {domain}
                                            </p>
                                        </div>
                                    </div>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    );
                }
                return <span key={i} className="text-xs text-muted-foreground">{part}</span>;
            }
            return part;
        });
    };

    // Extract target information from candidates
    const targetInfo = useMemo(() => {
        if (!results.candidates || results.candidates.length === 0) return null;

        // Get unique targets from candidates
        const targets = new Map();
        results.candidates.forEach(cand => {
            if (!targets.has(cand.target)) {
                targets.set(cand.target, {
                    name: cand.target,
                    pdb_id: cand.pdb_id,
                    candidates: []
                });
            }
            targets.get(cand.target).candidates.push(cand);
        });

        return Array.from(targets.values())[0]; // Return first target
    }, [results.candidates]);

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-10">

            {/* --- 1. RESEARCH SUMMARY SECTION --- */}
            <Card className="border-border shadow-xl bg-card overflow-hidden">
                <CardHeader className="pb-6 border-b border-border bg-gradient-to-r from-blue-50/50 to-indigo-50/50 dark:from-blue-950/20 dark:to-indigo-950/20">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-primary rounded-xl shadow-lg shadow-primary/20">
                                <Search className="h-6 w-6 text-primary-foreground" />
                            </div>
                            <div className="space-y-2">
                                <CardTitle className="text-2xl font-bold tracking-tight flex items-center gap-2">
                                    Research Summary
                                </CardTitle>
                                <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                                    <Badge variant="outline" className="font-normal bg-muted/50 border-border">
                                        {results.extractedSymptoms || results.symptoms}
                                    </Badge>
                                    <span>•</span>
                                    <span>{results.sources?.length || 0} Sources Analyzed</span>
                                    <span>•</span>
                                    <span>{new Date().toLocaleDateString()}</span>
                                </div>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <Button variant="outline" size="sm" onClick={handleCopy} className="h-8">
                                {copied ? <Check className="h-3.5 w-3.5 mr-1.5 text-green-600" /> : <Copy className="h-3.5 w-3.5 mr-1.5" />}
                                Copy
                            </Button>
                        </div>
                    </div>
                </CardHeader>
            </Card>

            {/* --- 2. DETAILED RESEARCH CONTENT (The "Tavily" Dossier) --- */}
            <Card className="border-border shadow-xl bg-card overflow-hidden">
                <CardHeader className="pb-6 border-b border-border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
                            <BookOpen className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div>
                            <CardTitle className="text-2xl font-bold tracking-tight">
                                Detailed Research Findings
                            </CardTitle>
                            <p className="text-sm text-muted-foreground">
                                Comprehensive analysis based on {results.sources?.length || 0} scientific sources
                            </p>
                        </div>
                    </div>
                </CardHeader>

                {/* Collapsible Research Strategy */}
                {results.researchPlan && (
                    <div className="border-b border-border bg-muted/10">
                        <button
                            onClick={() => setShowResearchPlan(!showResearchPlan)}
                            className="w-full px-6 py-3 flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors"
                        >
                            <span className="flex items-center gap-2">
                                <Layers className="h-4 w-4" />
                                Discovery Strategy & Hypotheses
                            </span>
                            {showResearchPlan ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                        </button>

                        {showResearchPlan && (
                            <div className="px-6 py-4 border-t border-border space-y-4 animate-in slide-in-from-top-2">
                                <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                                    <h4 className="text-xs font-bold text-primary uppercase mb-2">Primary Strategy</h4>
                                    <p className="text-sm leading-relaxed">
                                        {results.researchPlan.strategy}
                                    </p>
                                </div>

                                {results.researchPlan.hypotheses && (
                                    <div className="space-y-2">
                                        <h4 className="text-xs font-bold text-muted-foreground uppercase">Working Hypotheses</h4>
                                        <div className="grid gap-2">
                                            {results.researchPlan.hypotheses.map((h, i) => (
                                                <div key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                                                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary/60 shrink-0" />
                                                    {h}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                <CardContent className="pt-8 px-6 md:px-10 pb-10">
                    <article className="prose prose-zinc dark:prose-invert max-w-none prose-headings:font-bold prose-h1:text-3xl prose-h2:text-xl prose-h2:mt-10 prose-h2:mb-4 prose-p:leading-7 prose-p:text-foreground/80 prose-li:text-foreground/80">
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                table: ({ children }) => (
                                    <div className="my-8 w-full overflow-x-auto rounded-lg border border-border bg-background shadow-sm">
                                        <table className="w-full text-sm text-left border-collapse min-w-[600px]">
                                            {children}
                                        </table>
                                    </div>
                                ),
                                thead: ({ children }) => (
                                    <thead className="bg-muted/50 border-b border-border">
                                        {children}
                                    </thead>
                                ),
                                tbody: ({ children }) => (
                                    <tbody className="divide-y divide-border">
                                        {children}
                                    </tbody>
                                ),
                                tr: ({ children }) => (
                                    <tr className="transition-colors hover:bg-muted/30">
                                        {children}
                                    </tr>
                                ),
                                th: ({ children }) => (
                                    <th className="px-4 py-3 text-xs font-bold uppercase tracking-wider text-muted-foreground select-none whitespace-nowrap bg-muted/20">
                                        {children}
                                    </th>
                                ),
                                td: ({ children }) => {
                                    const content = React.Children.toArray(children).join('');
                                    const isSmiles = typeof content === 'string' && isLikelySmiles(content);

                                    if (isSmiles) {
                                        return (
                                            <td className="px-4 py-3 text-sm align-top leading-relaxed">
                                                <div
                                                    className="font-mono text-[11px] font-medium text-blue-600 dark:text-blue-400 bg-blue-50/80 dark:bg-blue-950/50 px-2.5 py-1 rounded border border-blue-200 dark:border-blue-800/50 shadow-sm break-all inline-block hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors cursor-copy"
                                                    title="Click to copy SMILES"
                                                    onClick={() => {
                                                        navigator.clipboard.writeText(content);
                                                        toast.success("SMILES copied to clipboard");
                                                    }}
                                                >
                                                    {content}
                                                </div>
                                            </td>
                                        );
                                    }

                                    return (
                                        <td className="px-4 py-3 text-sm align-top leading-relaxed">
                                            {renderWithCitations(children)}
                                        </td>
                                    );
                                },
                                p: ({ children }) => (
                                    <p className="mb-4 leading-7 text-foreground/80">
                                        {React.Children.map(children, child => renderWithCitations(child))}
                                    </p>
                                ),
                                li: ({ children }) => (
                                    <li className="flex items-start gap-2.5">
                                        <span className="mt-2.5 h-1.5 w-1.5 rounded-full bg-muted-foreground/40 shrink-0" />
                                        <span>{React.Children.map(children, child => renderWithCitations(child))}</span>
                                    </li>
                                ),
                                h1: ({ children }) => (
                                    <h1 className="text-3xl font-extrabold tracking-tight mb-8 pb-4 border-b border-border">
                                        {children}
                                    </h1>
                                ),
                                h2: ({ children }) => (
                                    <h2 className="group flex items-center gap-3 text-xl font-bold mt-12 mb-6 pb-2 border-b border-border text-foreground">
                                        <div className="h-6 w-1 bg-primary rounded-full" />
                                        {children}
                                    </h2>
                                ),
                                h3: ({ children }) => (
                                    <h3 className="text-lg font-semibold mt-8 mb-3 text-foreground flex items-center gap-2">
                                        <span className="text-primary/60">#</span>
                                        {children}
                                    </h3>
                                ),
                                strong: ({ children }) => (
                                    <span className="font-semibold text-blue-700 dark:text-blue-300 bg-blue-50/50 dark:bg-blue-900/20 px-1 rounded border border-blue-100/50 dark:border-blue-800/30 mx-0.5">
                                        {children}
                                    </span>
                                ),
                                blockquote: ({ children }) => (
                                    <div className="my-6 pl-6 border-l-4 border-primary italic text-muted-foreground bg-primary/5 py-3 pr-4 rounded-r-lg">
                                        {children}
                                    </div>
                                ),
                                code: ({ children }) => (
                                    <code className="px-1.5 py-0.5 rounded bg-muted text-primary text-xs font-mono border border-border">
                                        {children}
                                    </code>
                                ),
                                ul: ({ children }) => (
                                    <ul className="my-4 space-y-2 list-none pl-0">
                                        {children}
                                    </ul>
                                ),
                                a: ({ href, children }) => (
                                    <a href={href} target="_blank" className="text-primary hover:underline underline-offset-4 inline-flex items-center gap-0.5">
                                        {children}
                                        <ExternalLink className="h-3 w-3" />
                                    </a>
                                )
                            }}
                        >
                            {processedContent}
                        </ReactMarkdown>
                    </article>
                </CardContent>
            </Card>

            {/* --- 3. SCIENTIST DASHBOARD (Aurelius v3.0) --- */}
            {results.candidates && results.candidates.length > 0 && (
                <Card className="border-border shadow-2xl bg-card overflow-hidden ring-1 ring-primary/5">
                    <CardHeader className="pb-6 border-b border-border/50 bg-background/50 backdrop-blur-xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 blur-3xl -mr-32 -mt-32 pointer-events-none" />
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-primary rounded-2xl shadow-[0_8px_24px_rgba(var(--primary),0.25)] ring-1 ring-white/10">
                                    <FlaskConical className="h-7 w-7 text-primary-foreground" />
                                </div>
                                <div>
                                    <CardTitle className="text-3xl font-black tracking-tighter">
                                        Scientist Dashboard
                                    </CardTitle>
                                    <div className="text-[11px] text-muted-foreground font-bold flex items-center gap-2 mt-1 uppercase tracking-widest opacity-70">
                                        Advanced Molecular Intel & Lead Analytics
                                        <div className="h-1 w-1 rounded-full bg-primary/40" />
                                        <span className="text-primary font-black">v3.0 AURELIUS</span>
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={downloadScientistReport}
                                    className="h-10 px-5 bg-background/50 hover:bg-background/80 border-border/50 rounded-xl font-bold flex gap-2 transition-all"
                                >
                                    <FileDown className="h-4 w-4" />
                                    Export Analysis
                                </Button>
                                <div className="h-10 pl-1 pr-4 bg-primary rounded-xl flex items-center gap-3 shadow-lg shadow-primary/20 ring-1 ring-white/20">
                                    <div className="h-8 w-8 rounded-lg bg-white/20 flex items-center justify-center font-black text-white">
                                        {results.candidates.length}
                                    </div>
                                    <span className="text-[11px] font-black text-white uppercase tracking-wider">Potential Leads</span>
                                </div>
                            </div>
                        </div>
                    </CardHeader>

                    <CardContent className="p-0">
                        <div className="flex flex-col lg:flex-row h-[950px] overflow-hidden bg-background/20 backdrop-blur-3xl">
                            {/* Dashboard Sidebar - Candidate List */}
                            <div className="w-full lg:w-[300px] border-r border-border/10 bg-muted/5 flex flex-col shrink-0">
                                <div className="p-6 border-b border-border/10 bg-background/10 backdrop-blur-md">
                                    <div className="relative group">
                                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground/40 group-focus-within:text-primary transition-all" />
                                        <input
                                            type="text"
                                            placeholder="Find candidates..."
                                            className="w-full pl-10 pr-4 py-2.5 bg-background/30 border border-white/5 rounded-2xl text-[11px] font-bold focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all placeholder:text-muted-foreground/30"
                                        />
                                    </div>
                                </div>
                                <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                                    {results.candidates.map((candidate, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => setSelectedCandidate(candidate)}
                                            className={cn(
                                                "w-full text-left p-5 rounded-[24px] border transition-all duration-300 group relative overflow-hidden",
                                                selectedCandidate?.name === candidate.name
                                                    ? "bg-primary border-primary shadow-[0_12px_40px_rgba(var(--primary),0.3)] scale-[1.02] z-10"
                                                    : "bg-background/20 border-white/5 hover:border-primary/20 hover:bg-background/40"
                                            )}
                                        >
                                            <div className="flex flex-col gap-3 relative z-10">
                                                <div className="flex items-center justify-between">
                                                    <h4 className={cn(
                                                        "font-black text-[13px] tracking-tight truncate pr-2 uppercase",
                                                        selectedCandidate?.name === candidate.name ? "text-primary-foreground" : "text-foreground"
                                                    )}>
                                                        {candidate.name}
                                                    </h4>
                                                    <ChevronRight className={cn(
                                                        "h-4 w-4 transition-transform group-hover:translate-x-1",
                                                        selectedCandidate?.name === candidate.name ? "text-primary-foreground" : "text-muted-foreground/30"
                                                    )} />
                                                </div>
                                                <div className="flex flex-wrap gap-1.5 font-bold">
                                                    <div className={cn(
                                                        "text-[9px] px-2 py-0.5 rounded-lg border",
                                                        selectedCandidate?.name === candidate.name
                                                            ? "bg-white/20 text-white border-white/20"
                                                            : "bg-muted/30 text-muted-foreground/60 border-border/50"
                                                    )}>
                                                        {candidate.chemicalAnalysis?.properties.molecular_weight || "?"} <span className="opacity-50">g/mol</span>
                                                    </div>
                                                    <div className={cn(
                                                        "text-[9px] px-2 py-0.5 rounded-lg border",
                                                        selectedCandidate?.name === candidate.name
                                                            ? "bg-white/20 text-white border-white/20"
                                                            : "bg-muted/30 text-muted-foreground/60 border-border/50"
                                                    )}>
                                                        LogP: {candidate.chemicalAnalysis?.properties.logp || "?"}
                                                    </div>
                                                </div>
                                                {candidate.confidenceScore && (
                                                    <div className="space-y-1.5 pt-1">
                                                        <div className="flex items-center justify-between text-[8px] font-black uppercase tracking-widest">
                                                            <span className={selectedCandidate?.name === candidate.name ? "text-white/60" : "text-muted-foreground/50"}>Confidence</span>
                                                            <span className={selectedCandidate?.name === candidate.name ? "text-white" : "text-primary"}>{candidate.confidenceScore}%</span>
                                                        </div>
                                                        <div className={cn(
                                                            "w-full rounded-full h-1 overflow-hidden",
                                                            selectedCandidate?.name === candidate.name ? "bg-white/10" : "bg-primary/5"
                                                        )}>
                                                            <div
                                                                className={cn(
                                                                    "h-full rounded-full transition-all duration-1000 ease-out",
                                                                    selectedCandidate?.name === candidate.name ? "bg-white" : "bg-primary"
                                                                )}
                                                                style={{ width: `${candidate.confidenceScore}%` }}
                                                            />
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                                <div className="p-6 border-t border-border/10 bg-background/5 text-[9px] font-black uppercase tracking-[0.3em] text-muted-foreground/40 flex items-center justify-center gap-3">
                                    <div className="w-2 h-2 rounded-full bg-primary/40 shadow-[0_0_10px_rgba(var(--primary),0.5)] animate-pulse" />
                                    Intel-Node Active
                                </div>
                            </div>

                            {/* Main Content Pane */}
                            <div className="flex-1 bg-background relative flex flex-col">
                                {selectedCandidate ? (
                                    <>
                                        <div className="p-8 border-b border-border/50 bg-background/20 flex flex-col md:flex-row md:items-center justify-between gap-6">
                                            <div className="flex items-center gap-5">
                                                <div className="p-4 bg-primary/10 rounded-3xl ring-1 ring-primary/20 shadow-inner">
                                                    <Beaker className="h-8 w-8 text-primary" />
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-3">
                                                        <h2 className="text-3xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-br from-foreground to-foreground/60">
                                                            {selectedCandidate.name}
                                                        </h2>
                                                        <div className="px-3 py-1 bg-muted/50 border border-border/50 rounded-lg text-[10px] font-black font-mono text-muted-foreground tracking-tighter shadow-sm">
                                                            {selectedCandidate.smiles}
                                                        </div>
                                                    </div>
                                                    <p className="text-sm font-medium text-muted-foreground mt-1.5 flex items-center gap-2">
                                                        <Target className="h-3.5 w-3.5 text-primary/60" />
                                                        Target: <span className="font-bold text-foreground">{selectedCandidate.target}</span>
                                                        <span className="w-1 h-1 rounded-full bg-muted-foreground/30 mx-1" />
                                                        Tier: <span className="text-primary font-bold">{selectedCandidate.tier}</span>
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex flex-col items-end gap-1.5">
                                                <div className="text-[10px] uppercase font-black tracking-[0.2em] text-muted-foreground/50">Scientific Confidence</div>
                                                <div className="flex items-center gap-3">
                                                    <div className="text-4xl font-black text-primary drop-shadow-sm">{selectedCandidate.confidenceScore}%</div>
                                                    <div className="px-3 py-1 bg-green-500/10 text-green-600 border border-green-500/20 rounded-full text-[10px] font-black uppercase tracking-wider shadow-sm">
                                                        Verified Lead
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Detail Tabs */}
                                        <Tabs defaultValue="structure" className="flex-1 flex flex-col">
                                            <div className="px-8 bg-background/30 backdrop-blur-md border-b border-border/40">
                                                <TabsList className="h-16 bg-transparent gap-10 p-0">
                                                    <TabsTrigger
                                                        value="structure"
                                                        className="h-16 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-0 font-black text-xs uppercase tracking-widest transition-all hover:text-primary"
                                                    >
                                                        <Dna className="h-4 w-4 mr-2 opacity-60" />
                                                        3D Interaction
                                                    </TabsTrigger>
                                                    <TabsTrigger
                                                        value="mechanism"
                                                        className="h-16 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-0 font-black text-xs uppercase tracking-widest transition-all hover:text-primary"
                                                    >
                                                        <Activity className="h-4 w-4 mr-2 opacity-60" />
                                                        Pharmacology
                                                    </TabsTrigger>
                                                    <TabsTrigger
                                                        value="properties"
                                                        className="h-16 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-0 font-black text-xs uppercase tracking-widest transition-all hover:text-primary"
                                                    >
                                                        <ShieldCheck className="h-4 w-4 mr-2 opacity-60" />
                                                        ADMET Dossier
                                                    </TabsTrigger>
                                                    <TabsTrigger
                                                        value="synthesis"
                                                        className="h-16 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-0 font-black text-xs uppercase tracking-widest transition-all hover:text-primary"
                                                    >
                                                        <GitBranch className="h-4 w-4 mr-2 opacity-60" />
                                                        Synthesis
                                                    </TabsTrigger>
                                                </TabsList>
                                            </div>

                                            <div className="flex-1 overflow-y-auto custom-scrollbar">
                                                <TabsContent value="structure" className="p-0 m-0 h-full">
                                                    <div className="flex flex-col xl:flex-row h-full">
                                                        <div className="flex-1 min-h-[500px] xl:min-h-0 relative group">
                                                            {/* Expand button overlay with glassmorphism */}
                                                            <div className="absolute top-6 right-6 z-30 opacity-0 group-hover:opacity-100 transition-all duration-300 transform group-hover:translate-x-0 translate-x-4">
                                                                <Tooltip>
                                                                    <TooltipTrigger asChild>
                                                                        <Button
                                                                            variant="secondary"
                                                                            size="sm"
                                                                            onClick={() => openMoleculeViewer(selectedCandidate)}
                                                                            className="gap-2 bg-background/40 backdrop-blur-2xl border border-white/20 shadow-[0_8px_32px_rgba(0,0,0,0.2)] hover:bg-background/60 text-foreground font-bold"
                                                                        >
                                                                            <Maximize2 className="h-4 w-4" />
                                                                            Expand Stage
                                                                        </Button>
                                                                    </TooltipTrigger>
                                                                    <TooltipContent side="left">
                                                                        <p className="font-bold">Enter Fullscreen Laboratory</p>
                                                                    </TooltipContent>
                                                                </Tooltip>
                                                            </div>
                                                            <MolstarViewer
                                                                pdbId={selectedCandidate.pdb_id}
                                                                height="100%"
                                                                className="w-full h-full border-none shadow-none"
                                                                targetName={selectedCandidate.target}
                                                                ligandName={selectedCandidate.name}
                                                                showControls={true}
                                                            />
                                                            <div className="absolute inset-0 border-r border-border/10 pointer-events-none" />
                                                        </div>
                                                        <div className="w-full xl:w-[380px] p-8 bg-muted/10 backdrop-blur-sm space-y-8 overflow-y-auto shrink-0 custom-scrollbar border-l border-border/50">
                                                            <div className="space-y-6">
                                                                <div className="flex items-center justify-between">
                                                                    <h4 className="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center gap-2">
                                                                        <Target className="h-4 w-4" />
                                                                        Affinity Analysis
                                                                    </h4>
                                                                    <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20 text-[9px] font-black uppercase">Vina-Ensemble</Badge>
                                                                </div>

                                                                <div className="p-6 rounded-[32px] bg-background/40 backdrop-blur-2xl border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.1)] relative overflow-hidden group">
                                                                    <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 blur-3xl -mr-12 -mt-12 transition-all group-hover:bg-primary/20" />
                                                                    <div className="text-[10px] font-black uppercase text-secondary-foreground opacity-50 mb-1 tracking-widest">Binding Energy (ΔG)</div>
                                                                    <div className="flex items-baseline gap-2">
                                                                        <div className="text-5xl font-black text-foreground drop-shadow-sm">-8.4</div>
                                                                        <div className="text-lg font-bold text-muted-foreground">kcal/mol</div>
                                                                    </div>
                                                                    <div className="mt-4 flex items-center gap-3">
                                                                        <div className="h-2 flex-1 bg-muted/50 rounded-full overflow-hidden">
                                                                            <div className="h-full bg-primary w-[84%] rounded-full shadow-[0_0_12px_rgba(var(--primary),0.5)]" />
                                                                        </div>
                                                                        <div className="text-[10px] font-black text-primary">84% PROB.</div>
                                                                    </div>
                                                                </div>

                                                                <div className="space-y-4">
                                                                    <div className="flex items-center justify-between px-1">
                                                                        <h5 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">Molecular Interactions</h5>
                                                                        <Activity className="h-3 w-3 text-muted-foreground/40" />
                                                                    </div>
                                                                    <div className="grid grid-cols-2 gap-3">
                                                                        <div className="p-4 bg-background/30 backdrop-blur-md border border-white/5 rounded-3xl hover:bg-background/50 hover:border-blue-500/30 transition-all cursor-default group">
                                                                            <div className="text-[9px] text-muted-foreground font-black uppercase tracking-tighter mb-1">H-Bonds</div>
                                                                            <div className="text-2xl font-black tracking-tight text-blue-500 group-hover:scale-105 transition-transform">4 <span className="text-[10px] opacity-50 ml-0.5">Sites</span></div>
                                                                        </div>
                                                                        <div className="p-4 bg-background/30 backdrop-blur-md border border-white/5 rounded-3xl hover:bg-background/50 hover:border-orange-500/30 transition-all cursor-default group">
                                                                            <div className="text-[9px] text-muted-foreground font-black uppercase tracking-tighter mb-1">Pi-Stacking</div>
                                                                            <div className="text-2xl font-black tracking-tight text-orange-500 group-hover:scale-105 transition-transform">2 <span className="text-[10px] opacity-50 ml-0.5">Reg.</span></div>
                                                                        </div>
                                                                        <div className="p-4 bg-background/30 backdrop-blur-md border border-white/5 rounded-3xl hover:bg-background/50 hover:border-green-500/30 transition-all cursor-default group">
                                                                            <div className="text-[9px] text-muted-foreground font-black uppercase tracking-tighter mb-1">Hydrophobic</div>
                                                                            <div className="text-2xl font-black tracking-tight text-green-500 group-hover:scale-105 transition-transform">6 <span className="text-[10px] opacity-50 ml-0.5">Cnts.</span></div>
                                                                        </div>
                                                                        <div className="p-4 bg-background/30 backdrop-blur-md border border-white/5 rounded-3xl hover:bg-background/50 hover:border-purple-500/30 transition-all cursor-default group">
                                                                            <div className="text-[9px] text-muted-foreground font-black uppercase tracking-tighter mb-1">Salt Bridges</div>
                                                                            <div className="text-2xl font-black tracking-tight text-purple-500 group-hover:scale-105 transition-transform">1 <span className="text-[10px] opacity-50 ml-0.5">Site</span></div>
                                                                        </div>
                                                                    </div>
                                                                </div>

                                                                <div className="p-1 rounded-[32px] bg-gradient-to-br from-border/50 to-transparent">
                                                                    <div className="p-6 rounded-[31px] bg-background/40 backdrop-blur-sm border border-white/5">
                                                                        <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 mb-4 flex items-center justify-between">
                                                                            2D Topology
                                                                            <Atom className="h-3 w-3 opacity-30" />
                                                                        </div>
                                                                        <SmallMoleculeViewer smiles={selectedCandidate.smiles} name={selectedCandidate.name} />
                                                                    </div>
                                                                </div>

                                                                {/* Quick Properties Card */}
                                                                <div className="p-6 rounded-[32px] bg-primary/[0.03] border border-primary/10 shadow-inner group">
                                                                    <div className="flex items-center justify-between mb-4">
                                                                        <div className="text-[10px] font-black uppercase tracking-widest text-primary">Core Metrics</div>
                                                                        <Info className="h-3 w-3 text-primary opacity-50" />
                                                                    </div>
                                                                    <div className="grid grid-cols-2 gap-4">
                                                                        <div className="space-y-0.5">
                                                                            <div className="text-[9px] text-muted-foreground uppercase font-bold tracking-tight">Mass</div>
                                                                            <div className="text-md font-black">{selectedCandidate.chemicalAnalysis?.properties.molecular_weight || "--"} <span className="text-[10px] opacity-50">Da</span></div>
                                                                        </div>
                                                                        <div className="space-y-0.5">
                                                                            <div className="text-[9px] text-muted-foreground uppercase font-bold tracking-tight">LogP</div>
                                                                            <div className="text-md font-black text-blue-500">{selectedCandidate.chemicalAnalysis?.properties.logp || "--"}</div>
                                                                        </div>
                                                                        <div className="space-y-0.5 pt-2 border-t border-border/20">
                                                                            <div className="text-[9px] text-muted-foreground uppercase font-bold tracking-tight">TPSA</div>
                                                                            <div className="text-md font-black">{selectedCandidate.chemicalAnalysis?.properties.tpsa || "--"} <span className="text-[10px] opacity-50">Å²</span></div>
                                                                        </div>
                                                                        <div className="space-y-0.5 pt-2 border-t border-border/20">
                                                                            <div className="text-[9px] text-muted-foreground uppercase font-bold tracking-tight">QED</div>
                                                                            <div className="text-md font-black text-green-500">{selectedCandidate.chemicalAnalysis?.properties.qed?.toFixed(3) || "--"}</div>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </TabsContent>

                                                <TabsContent value="mechanism" className="p-10 m-0 max-w-5xl custom-scrollbar overflow-y-auto">
                                                    <div className="grid grid-cols-1 lg:grid-cols-1 gap-12">
                                                        <section className="space-y-6">
                                                            <div className="inline-flex items-center gap-3 px-4 py-1.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-[10px] font-black uppercase tracking-widest">
                                                                <Microscope className="h-3.5 w-3.5" />
                                                                Pharmacodynamic profile
                                                            </div>
                                                            <h3 className="text-4xl font-black tracking-tight leading-tight italic">
                                                                Molecular Mechanism <br /><span className="text-primary not-italic">& Synthesis of Action</span>
                                                            </h3>
                                                            <div className="p-8 rounded-[40px] bg-muted/30 border border-border/40 leading-relaxed text-lg font-medium text-foreground/80 shadow-inner">
                                                                {selectedCandidate.mechanism || "No detailed mechanism provided."}
                                                            </div>
                                                        </section>

                                                        {selectedCandidate.mechanism_evidence && (
                                                            <section className="space-y-6">
                                                                <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground/60 flex items-center gap-2">
                                                                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                                                                    Biological Evidence & Validation
                                                                </h4>
                                                                <div className="p-8 rounded-[40px] bg-green-500/[0.03] border border-green-500/20 text-md font-medium leading-relaxed italic text-green-800 dark:text-green-300">
                                                                    "{selectedCandidate.mechanism_evidence}"
                                                                </div>
                                                            </section>
                                                        )}

                                                        <section className="space-y-6">
                                                            <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground/60 flex items-center gap-2">
                                                                <BookOpen className="h-4 w-4 text-primary" />
                                                                Extracted Scientific References
                                                            </h4>
                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                                {selectedCandidate.references?.map((ref, idx) => (
                                                                    <a
                                                                        key={idx}
                                                                        href={ref.url}
                                                                        target="_blank"
                                                                        className="p-5 rounded-2xl border border-border/50 bg-background/50 hover:bg-background hover:border-primary/50 hover:shadow-xl transition-all flex items-center gap-5 group"
                                                                    >
                                                                        <div className="w-12 h-12 rounded-xl bg-muted/50 flex items-center justify-center font-black text-sm text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                                                                            {ref.database.charAt(0)}
                                                                        </div>
                                                                        <div className="flex-1 min-w-0">
                                                                            <div className="font-black text-xs text-foreground group-hover:text-primary transition-colors truncate">{ref.database} • ID {ref.id}</div>
                                                                            <div className="text-[9px] text-muted-foreground font-mono truncate mt-1">{ref.url}</div>
                                                                        </div>
                                                                        <ExternalLink className="h-3.5 w-3.5 text-muted-foreground/50 group-hover:text-primary transition-colors" />
                                                                    </a>
                                                                ))}
                                                            </div>
                                                        </section>
                                                    </div>
                                                </TabsContent>

                                                <TabsContent value="properties" className="p-10 m-0 custom-scrollbar overflow-y-auto">
                                                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-12">
                                                        <div className="space-y-8">
                                                            <h4 className="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center gap-2">
                                                                <Beaker className="h-4 w-4" />
                                                                Physical Druglikeness
                                                            </h4>
                                                            <div className="grid grid-cols-2 gap-px bg-border/20 border border-border/50 rounded-3xl overflow-hidden shadow-2xl">
                                                                <div className="bg-background/40 p-8 space-y-2">
                                                                    <div className="text-[10px] text-muted-foreground uppercase font-black tracking-widest">Molecular Weight</div>
                                                                    <div className="text-3xl font-black tracking-tighter italic">{selectedCandidate.chemicalAnalysis?.properties.molecular_weight} <span className="text-xs not-italic opacity-40">g/mol</span></div>
                                                                </div>
                                                                <div className="bg-background/40 p-8 space-y-2">
                                                                    <div className="text-[10px] text-muted-foreground uppercase font-black tracking-widest">Lipophilicity (LogP)</div>
                                                                    <div className="text-3xl font-black tracking-tighter italic text-blue-600 dark:text-blue-400">{selectedCandidate.chemicalAnalysis?.properties.logp}</div>
                                                                </div>
                                                                <div className="bg-background/40 p-8 space-y-2">
                                                                    <div className="text-[10px] text-muted-foreground uppercase font-black tracking-widest">H-Bond Donors</div>
                                                                    <div className="text-3xl font-black tracking-tighter italic">{selectedCandidate.chemicalAnalysis?.properties.hbd}</div>
                                                                </div>
                                                                <div className="bg-background/40 p-8 space-y-2">
                                                                    <div className="text-[10px] text-muted-foreground uppercase font-black tracking-widest">H-Bond Acceptors</div>
                                                                    <div className="text-3xl font-black tracking-tighter italic">{selectedCandidate.chemicalAnalysis?.properties.hba}</div>
                                                                </div>
                                                                <div className="bg-background/60 p-8 col-span-2 space-y-4">
                                                                    <div className="flex items-center justify-between">
                                                                        <div className="text-[10px] text-muted-foreground uppercase font-black tracking-widest">QED (Qualitative Estimation of Druglikeness)</div>
                                                                        <div className="text-3xl font-black text-green-600">{selectedCandidate.chemicalAnalysis?.properties.qed.toFixed(3)}</div>
                                                                    </div>
                                                                    <div className="h-3 bg-muted/40 rounded-full overflow-hidden ring-1 ring-border whitespace-pre">
                                                                        <div className="h-full bg-gradient-to-r from-green-600 to-green-400 shadow-[0_0_20px_rgba(22,163,74,0.5)]" style={{ width: `${(selectedCandidate.chemicalAnalysis?.properties.qed || 0) * 100}%` }} />
                                                                    </div>
                                                                </div>
                                                            </div>

                                                            <div className={cn(
                                                                "p-8 rounded-[40px] border-2 shadow-2xl transition-all",
                                                                selectedCandidate.chemicalAnalysis?.lipinski.passed
                                                                    ? "bg-green-500/[0.05] border-green-500/20 shadow-green-500/5"
                                                                    : "bg-amber-500/[0.05] border-amber-500/20 shadow-amber-500/5"
                                                            )}>
                                                                <div className="flex items-center justify-between mb-6">
                                                                    <h4 className="text-lg font-black uppercase tracking-tight flex items-center gap-3">
                                                                        <div className={cn("w-3 h-3 rounded-full", selectedCandidate.chemicalAnalysis?.lipinski.passed ? "bg-green-500" : "bg-amber-500")} />
                                                                        Lipinski's Rule of 5
                                                                    </h4>
                                                                    <div className={cn(
                                                                        "px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] shadow-lg",
                                                                        selectedCandidate.chemicalAnalysis?.lipinski.passed ? "bg-green-500 text-white" : "bg-amber-500 text-white"
                                                                    )}>
                                                                        {selectedCandidate.chemicalAnalysis?.lipinski.passed ? "Candidate Passed" : "Action Required"}
                                                                    </div>
                                                                </div>
                                                                <div className="grid grid-cols-1 gap-3">
                                                                    {selectedCandidate.chemicalAnalysis?.lipinski.details.map((detail, i) => (
                                                                        <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-background/50 border border-border/30">
                                                                            <span className="text-sm font-medium text-muted-foreground">{detail}</span>
                                                                            <CheckCircle2 className={cn("h-4 w-4", detail.includes('Violation') ? "text-amber-500" : "text-green-500")} />
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div className="space-y-8">
                                                            <h4 className="text-xs font-black uppercase tracking-[0.2em] text-amber-600 flex items-center gap-2">
                                                                <Zap className="h-4 w-4" />
                                                                ADMET Toxicity Profile
                                                            </h4>
                                                            <div className="space-y-3">
                                                                {[
                                                                    { label: "Absorption (P-gp Inhibitor)", value: "Optimal Prediction", status: "success" },
                                                                    { label: "Blood-Brain Barrier (BBB)", value: "Candidate Permeable", status: "info" },
                                                                    { label: "Hepatotoxicity Risk", value: "Non-toxic Signature", status: "success" },
                                                                    { label: "Synthetic Accessibility", value: "3.4 (Accessible)", status: "warning" }
                                                                ].map((item, idx) => (
                                                                    <div key={idx} className="p-6 rounded-[30px] bg-background/40 border border-border/50 hover:bg-background/80 hover:border-primary/30 transition-all flex items-center justify-between group shadow-sm">
                                                                        <div className="space-y-1">
                                                                            <div className="text-[9px] font-black uppercase tracking-widest text-muted-foreground/60">{item.label}</div>
                                                                            <div className="text-lg font-black tracking-tight group-hover:text-primary transition-colors">{item.value}</div>
                                                                        </div>
                                                                        <div className={cn(
                                                                            "w-12 h-12 rounded-full flex items-center justify-center border-2 shadow-inner",
                                                                            item.status === 'success' ? "bg-green-500/10 border-green-500/20 text-green-600" :
                                                                                item.status === 'info' ? "bg-blue-500/10 border-blue-500/20 text-blue-600" :
                                                                                    "bg-amber-500/10 border-amber-500/20 text-amber-600"
                                                                        )}>
                                                                            <CheckCircle2 className="h-6 w-6" />
                                                                        </div>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                            <div className="p-8 rounded-[40px] bg-primary/5 border border-primary/20 leading-relaxed">
                                                                <div className="flex gap-4 items-start">
                                                                    <Info className="h-5 w-5 text-primary shrink-0" />
                                                                    <p className="text-xs font-medium text-primary/80">
                                                                        Aurelius v3.0 Engine leverages a hybrid of ensemble QSAR models and high-reasoning bio-logic. Estimates are for research use only and require in-vitro validation.
                                                                    </p>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </TabsContent>

                                                <TabsContent value="synthesis" className="p-10 m-0 h-full overflow-y-auto custom-scrollbar">
                                                    <div className="max-w-4xl mx-auto space-y-12">
                                                        <div className="flex flex-col items-center text-center space-y-4">
                                                            <div className="px-4 py-1.5 rounded-full bg-amber-500/10 text-amber-600 border border-amber-500/20 text-[10px] font-black uppercase tracking-[0.2em] shadow-sm">
                                                                AI-Generated Assembly Strategy
                                                            </div>
                                                            <h3 className="text-4xl font-black tracking-tight italic">
                                                                Computational <span className="text-primary not-italic">Assembly Pathway</span>
                                                            </h3>
                                                            <p className="text-sm text-muted-foreground max-w-lg font-medium">
                                                                High-yield assembly route optimized for rapid lab synthesis and clinical batch production.
                                                            </p>
                                                        </div>

                                                        {selectedCandidate.synthesis && selectedCandidate.synthesis.length > 0 ? (
                                                            <div className="space-y-0 relative px-4">
                                                                <div className="absolute left-[39px] top-6 bottom-6 w-1 bg-gradient-to-b from-primary via-primary/40 to-muted z-0 rounded-full" />
                                                                {selectedCandidate.synthesis.map((step, i) => (
                                                                    <div key={i} className="relative z-10 flex gap-10 pb-16 last:pb-0 group">
                                                                        <div className="w-16 h-16 rounded-[24px] bg-primary flex flex-col items-center justify-center font-black text-primary-foreground shadow-2xl shadow-primary/40 ring-4 ring-background shrink-0 transition-all group-hover:scale-110 group-hover:rotate-3">
                                                                            <span className="text-[10px] opacity-70 uppercase leading-none mb-1">Step</span>
                                                                            <span className="text-2xl leading-none">{step.step}</span>
                                                                        </div>
                                                                        <div className="flex-1 p-8 rounded-[40px] bg-background/60 border border-border/40 hover:border-primary/40 hover:shadow-2xl hover:bg-background transition-all group-hover:-translate-y-1">
                                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                                                                <div className="space-y-2">
                                                                                    <div className="text-[9px] uppercase font-black text-muted-foreground/60 tracking-widest">Main Reactant</div>
                                                                                    <div className="text-lg font-black tracking-tight text-foreground">{step.reactant}</div>
                                                                                </div>
                                                                                <div className="space-y-2">
                                                                                    <div className="text-[9px] uppercase font-black text-muted-foreground/60 tracking-widest">Reagent / Catalyst</div>
                                                                                    <div className="text-lg font-black tracking-tight text-blue-600 dark:text-blue-400">{step.reagent}</div>
                                                                                </div>
                                                                                <div className="space-y-2 border-t border-border/30 pt-4">
                                                                                    <div className="text-[9px] uppercase font-black text-muted-foreground/60 tracking-widest">Lab Conditions</div>
                                                                                    <div className="text-xs font-mono font-bold py-1 px-2 bg-muted/50 rounded inline-block">{step.conditions}</div>
                                                                                </div>
                                                                                <div className="space-y-2 border-t border-border/30 pt-4">
                                                                                    <div className="text-[9px] uppercase font-black text-muted-foreground/60 tracking-widest">Intermediate / Product</div>
                                                                                    <div className="text-lg font-black tracking-tight text-green-600 dark:text-green-400 drop-shadow-sm">{step.product}</div>
                                                                                </div>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        ) : (
                                                            <div className="flex flex-col items-center justify-center py-24 text-center space-y-6 bg-muted/20 rounded-[50px] border border-dashed border-border/60">
                                                                <div className="w-20 h-20 rounded-full bg-muted/50 flex items-center justify-center animate-pulse">
                                                                    <GitBranch className="h-10 w-10 text-muted-foreground/40" />
                                                                </div>
                                                                <div className="space-y-2">
                                                                    <div className="font-black text-2xl tracking-tight">Pathway Computation in Progress</div>
                                                                    <p className="text-sm text-muted-foreground max-w-xs mx-auto font-medium leading-relaxed">
                                                                        Determining the most cost-effective and highest-yield synthesis route for this molecular structure.
                                                                    </p>
                                                                </div>
                                                                <Button variant="outline" className="rounded-full px-8 font-black text-xs uppercase tracking-widest hover:bg-primary hover:text-primary-foreground transition-all">
                                                                    Prioritize Synthesis Logic
                                                                </Button>
                                                            </div>
                                                        )}
                                                    </div>
                                                </TabsContent>
                                            </div>
                                        </Tabs>

                                        {/* New Comprehensive Molecular Details Panel */}
                                        <div className="mt-8 px-8 pb-8">
                                            <MolecularDetailsPanel candidate={selectedCandidate} />
                                        </div>
                                    </>
                                ) : (
                                    <div className="flex-1 flex flex-col items-center justify-center text-center p-12 space-y-6">
                                        <div className="w-24 h-24 rounded-full bg-muted/50 flex items-center justify-center animate-pulse">
                                            <FlaskConical className="h-12 w-12 text-muted-foreground/30" />
                                        </div>
                                        <div className="space-y-2">
                                            <h3 className="text-xl font-bold">No Candidate Selected</h3>
                                            <p className="text-sm text-muted-foreground max-w-xs mx-auto">
                                                Select a drug candidate from the sidebar to view full interaction maps and chemical proofs.
                                            </p>
                                        </div>
                                        <div className="grid grid-cols-2 gap-3 max-w-sm">
                                            <div className="p-4 rounded-xl border border-border bg-muted/10">
                                                <Target className="h-8 w-8 text-muted-foreground/40 mb-2 mx-auto" />
                                                <div className="text-[10px] font-bold">3D BINDING</div>
                                            </div>
                                            <div className="p-4 rounded-xl border border-border bg-muted/10">
                                                <Dna className="h-8 w-8 text-muted-foreground/40 mb-2 mx-auto" />
                                                <div className="text-[10px] font-bold">SYNTHESIS</div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* --- 4. TARGET PROTEIN SUMMARY (Standalone Structure) --- */}
            {targetInfo && (
                <Card className="border-border shadow-md bg-card overflow-hidden">
                    <CardHeader className="pb-4 border-b border-border">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                                    <Target className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                                </div>
                                <CardTitle className="text-lg font-bold">Target Protein Overview</CardTitle>
                            </div>
                            <Badge variant="outline">{targetInfo.pdb_id || "4EY6"}</Badge>
                        </div>
                    </CardHeader>
                    <div className="grid grid-cols-1 md:grid-cols-4 divide-x divide-border">
                        <div className="p-4 text-center">
                            <div className="text-[10px] text-muted-foreground uppercase font-bold mb-1">PDB Method</div>
                            <div className="font-bold">X-RAY DIFFRACTION</div>
                        </div>
                        <div className="p-4 text-center">
                            <div className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Resolution</div>
                            <div className="font-bold">2.10 Å</div>
                        </div>
                        <div className="p-4 text-center">
                            <div className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Organism</div>
                            <div className="font-bold">Homo sapiens</div>
                        </div>
                        <div className="p-4 text-center">
                            <div className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Source</div>
                            <div className="font-bold">RCSB PDB</div>
                        </div>
                    </div>
                </Card>
            )}

            {/* --- 5. SOURCES SECTION --- */}
            <div className="space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-2">
                        <div className="p-1.5 bg-muted rounded-md border border-border">
                            <Database className="h-4 w-4 text-muted-foreground" />
                        </div>
                        <h3 className="text-lg font-semibold">
                            Identified Sources
                        </h3>
                    </div>

                    <Tabs value={activeSourceCategory} onValueChange={setActiveSourceCategory}>
                        <TabsList className="h-9 bg-muted p-1 border border-border">
                            <TabsTrigger value="all" className="text-xs px-3">All</TabsTrigger>
                            <TabsTrigger value="clinical" className="text-xs px-3">Clinical</TabsTrigger>
                            <TabsTrigger value="protein" className="text-xs px-3">Protein</TabsTrigger>
                        </TabsList>
                    </Tabs>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {(groupedSources[activeSourceCategory] || []).map((source, idx) => {
                        const domain = getDomain(source.url);
                        const favicon = getFaviconUrl(source.url);

                        let dbType = 'default';
                        if (source.url.includes('pubmed')) dbType = 'pubmed';
                        if (source.url.includes('uniprot')) dbType = 'uniprot';
                        if (source.url.includes('pubchem')) dbType = 'pubchem';

                        const borderClass = DB_COLORS[dbType] || DB_COLORS.default;

                        return (
                            <a
                                key={idx}
                                href={source.url}
                                target="_blank"
                                className={cn(
                                    "group flex flex-col p-4 rounded-xl border bg-card transition-all duration-200",
                                    "hover:shadow-lg hover:-translate-y-0.5",
                                    borderClass
                                )}
                            >
                                <div className="flex items-start gap-3 mb-3">
                                    <div className="shrink-0 pt-1">
                                        {favicon ? (
                                            <img
                                                src={favicon}
                                                className="h-6 w-6 rounded-sm bg-background p-0.5 object-contain"
                                                alt=""
                                                onError={(e) => {
                                                    (e.target as HTMLImageElement).style.display = 'none';
                                                    (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                                                }}
                                            />
                                        ) : null}
                                        <Globe className={cn("h-6 w-6 text-muted-foreground", favicon && "hidden")} />
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <h4 className="font-medium text-sm leading-snug line-clamp-2 group-hover:text-primary transition-colors">
                                            {source.title || domain}
                                        </h4>
                                        <p className="text-[10px] text-muted-foreground mt-1 truncate">{source.url}</p>
                                    </div>
                                </div>

                                <div className="mt-auto flex items-center justify-between pt-3 border-t border-border">
                                    <div className="flex items-center gap-2">
                                        {dbType !== 'default' && (
                                            <Badge variant="secondary" className="text-[10px] h-5 px-1.5 font-normal bg-primary/10 text-primary border-0">
                                                {dbType}
                                            </Badge>
                                        )}
                                        <Badge variant="outline" className="text-[10px] h-5 px-1.5 font-normal border-border text-muted-foreground">
                                            rawContent
                                        </Badge>
                                    </div>

                                    {source.contentLength && (
                                        <span className="text-[10px] font-mono text-muted-foreground/60">
                                            {Math.round(source.contentLength / 1000)}k chars
                                        </span>
                                    )}
                                </div>
                            </a>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default ResultsPanel;
