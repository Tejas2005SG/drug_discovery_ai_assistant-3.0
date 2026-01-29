import React, { useState, useEffect, useMemo } from "react";
import {
    ChevronDown,
    ChevronRight,
    Loader2,
    CheckCircle2,
    Circle,
    Database,
    Globe,
    Zap,
    Link as LinkIcon,
    Terminal,
    Activity,
    Clock,
    Server,
    Cpu,
    Search,
    FileCode,
    Layers,
    AlertCircle,
    Radio
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { motion, AnimatePresence } from "framer-motion";

// --- Configuration & Helpers ---

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

// Source config with logo support
const SOURCE_CONFIG: Record<string, {
    icon: React.ReactNode;
    label: string;
    domain: string;
    logo: string;
}> = {
    pubmed: { icon: <Database className="h-3.5 w-3.5" />, label: "PUBMED", domain: "ncbi.nlm.nih.gov", logo: "/source-logos/pubmed.svg" },
    uniprot: { icon: <Database className="h-3.5 w-3.5" />, label: "UNIPROT", domain: "uniprot.org", logo: "/source-logos/uniprot.svg" },
    pubchem: { icon: <Database className="h-3.5 w-3.5" />, label: "PUBCHEM", domain: "pubchem.ncbi.nlm.nih.gov", logo: "/source-logos/pubchem.svg" },
    drugbank: { icon: <Database className="h-3.5 w-3.5" />, label: "DRUGBANK", domain: "go.drugbank.com", logo: "/source-logos/drugbank.svg" },
    clinicaltrials: { icon: <Database className="h-3.5 w-3.5" />, label: "CLINICAL", domain: "clinicaltrials.gov", logo: "/source-logos/clinicaltrials.svg" },
    kegg: { icon: <Database className="h-3.5 w-3.5" />, label: "KEGG", domain: "kegg.jp", logo: "/source-logos/kegg.svg" },
    general: { icon: <Globe className="h-3.5 w-3.5" />, label: "GENERAL", domain: "", logo: "/source-logos/general.svg" },
    default: { icon: <Globe className="h-3.5 w-3.5" />, label: "SOURCE", domain: "", logo: "/source-logos/general.svg" }
};

// Stage configuration with monochromatic professional styling
const STAGE_CONFIG: Record<string, {
    icon: React.ReactNode;
    label: string;
    code: string;
}> = {
    planning: { icon: <Layers className="h-4 w-4" />, label: "PLANNING", code: "PLAN" },
    searching: { icon: <Search className="h-4 w-4" />, label: "SEARCHING", code: "SRCH" },
    crawling: { icon: <Server className="h-4 w-4" />, label: "EXTRACTION", code: "EXTR" },
    thinking: { icon: <Cpu className="h-4 w-4" />, label: "ANALYSIS", code: "ANLZ" },
    generating: { icon: <FileCode className="h-4 w-4" />, label: "GENERATING", code: "GEN" },
    complete: { icon: <CheckCircle2 className="h-4 w-4" />, label: "COMPLETE", code: "DONE" },
    error: { icon: <AlertCircle className="h-4 w-4" />, label: "ERROR", code: "ERR" }
};

// --- Types ---
interface QueryInfo {
    query: string;
    sources: string[];
    resultCount?: number;
}

interface StepData {
    breakdown?: Record<string, number>;
    hypotheses?: string[];
}

export interface ThinkingStep {
    id: string;
    stage: "planning" | "searching" | "crawling" | "thinking" | "generating" | "complete" | "error";
    message: string;
    status: "running" | "completed" | "failed" | "pending" | "warning";
    timestamp: number;
    duration?: string;
    queries?: QueryInfo[];
    data?: StepData;
    sourceName?: string;
}

interface ThinkingPanelProps {
    steps: ThinkingStep[];
    isActive: boolean;
}

// --- Components ---

export const ThinkingPanel: React.FC<ThinkingPanelProps> = ({ steps, isActive }) => {
    const [isExpanded, setIsExpanded] = useState(true);
    const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
    const [elapsed, setElapsed] = useState(0);

    // Aggregate unique sources from all steps
    const liveSources = useMemo(() => {
        const sources = new Set<string>();
        steps.forEach(step => {
            step.queries?.forEach(q => {
                q.sources.forEach(s => sources.add(s));
            });
        });
        return Array.from(sources);
    }, [steps]);

    // Auto-expand running step
    useEffect(() => {
        const running = steps.find(s => s.status === "running");
        if (running) {
            setExpandedSteps(prev => new Set([...prev, running.id]));
        }
    }, [steps]);

    // Timer
    useEffect(() => {
        if (!isActive) return;
        const interval = setInterval(() => setElapsed(t => t + 0.1), 100);
        return () => clearInterval(interval);
    }, [isActive]);

    const toggleStep = (id: string) => {
        setExpandedSteps(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    const getSourceType = (url: string): string => {
        const lower = url.toLowerCase();
        if (lower.includes('pubmed')) return 'pubmed';
        if (lower.includes('uniprot')) return 'uniprot';
        if (lower.includes('pubchem')) return 'pubchem';
        if (lower.includes('drugbank')) return 'drugbank';
        if (lower.includes('clinicaltrials')) return 'clinicaltrials';
        if (lower.includes('kegg')) return 'kegg';
        if (lower.includes('general')) return 'general';
        return 'default';
    };

    // Source Logo Component
    const SourceLogo: React.FC<{ type: string; className?: string }> = ({ type, className = "h-4 w-4" }) => {
        const config = SOURCE_CONFIG[type] || SOURCE_CONFIG.default;
        return (
            <img
                src={config.logo}
                alt={config.label}
                className={cn("object-contain rounded", className)}
                onError={(e) => {
                    // Fallback to icon if image fails to load
                    e.currentTarget.style.display = 'none';
                    e.currentTarget.nextElementSibling?.classList.remove('hidden');
                }}
            />
        );
    };

    if (steps.length === 0) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full bg-background border border-border rounded-lg overflow-hidden flex flex-col font-mono text-sm"
        >
            {/* --- Header --- */}
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between px-4 py-3 bg-muted/30 hover:bg-muted/50 transition-colors border-b border-border"
            >
                <div className="flex items-center gap-3">
                    <Terminal className="h-4 w-4 text-muted-foreground" />
                    <span className="text-foreground font-semibold tracking-wider">REASONING_TRACE</span>
                    <span className="text-xs text-muted-foreground">[{elapsed.toFixed(1)}s]</span>
                </div>
                <div className="flex items-center gap-3">
                    {isActive && (
                        <div className="flex items-center gap-2">
                            <Radio className="h-3 w-3 text-primary animate-pulse" />
                            <span className="text-xs text-primary">ACTIVE</span>
                        </div>
                    )}
                    <motion.div
                        animate={{ rotate: isExpanded ? 180 : 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                    </motion.div>
                </div>
            </button>

            {/* --- Body --- */}
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.25, ease: "easeInOut" }}
                        className="flex flex-col overflow-hidden"
                    >
                        {/* --- Sources Section --- */}
                        {liveSources.length > 0 && (
                            <div className="p-4 border-b border-border bg-muted/10">
                                <div className="flex items-center gap-2 mb-3">
                                    <Server className="h-3.5 w-3.5 text-muted-foreground" />
                                    <span className="text-xs text-muted-foreground uppercase tracking-widest">
                                        Data Sources
                                    </span>
                                    <span className="text-xs text-muted-foreground">({liveSources.length})</span>
                                </div>

                                <div className="flex flex-wrap gap-2">
                                    {liveSources.slice(0, 8).map((sourceUrl, idx) => {
                                        const type = getSourceType(sourceUrl);
                                        const config = SOURCE_CONFIG[type] || SOURCE_CONFIG.default;
                                        const domain = getDomain(sourceUrl);

                                        return (
                                            <motion.div
                                                key={idx}
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                transition={{ delay: idx * 0.03 }}
                                                className="flex items-center gap-2 px-3 py-2 rounded bg-muted/30 border border-border hover:border-primary/30 hover:bg-muted/50 transition-all"
                                            >
                                                <SourceLogo type={type} className="h-4 w-4" />
                                                <span className="hidden">{config.icon}</span>
                                                <span className="text-xs text-foreground truncate">
                                                    {config.label}
                                                </span>
                                            </motion.div>
                                        )
                                    })}
                                </div>
                            </div>
                        )}

                        {/* --- Execution Log --- */}
                        <div className="p-4 relative">
                            {/* Vertical line */}
                            <div className="absolute left-[22px] top-4 bottom-4 w-px bg-border" />

                            <div className="space-y-1">
                                {steps.map((step, stepIndex) => {
                                    const isStepExpanded = expandedSteps.has(step.id);
                                    const hasDetails = (step.queries?.length ?? 0) > 0 || (step.data?.hypotheses);
                                    const stageConfig = STAGE_CONFIG[step.stage] || STAGE_CONFIG.searching;

                                    const isRunning = step.status === "running";
                                    const isCompleted = step.status === "completed";
                                    const isFailed = step.status === "failed";

                                    return (
                                        <motion.div
                                            key={step.id}
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: stepIndex * 0.03 }}
                                            className="relative pl-8"
                                        >
                                            {/* Node indicator */}
                                            <div className={cn(
                                                "absolute left-0 top-1.5 h-4 w-4 rounded-full border flex items-center justify-center z-10 bg-background",
                                                isRunning && "border-primary",
                                                isCompleted && "border-muted-foreground/50",
                                                isFailed && "border-destructive"
                                            )}>
                                                {isRunning && (
                                                    <Loader2 className="h-2.5 w-2.5 text-primary animate-spin" />
                                                )}
                                                {isCompleted && (
                                                    <div className="h-1.5 w-1.5 rounded-full bg-muted-foreground/50" />
                                                )}
                                                {isFailed && (
                                                    <div className="h-1.5 w-1.5 rounded-full bg-destructive" />
                                                )}
                                            </div>

                                            {/* Content */}
                                            <div
                                                className={cn(
                                                    "py-2 px-3 rounded hover:bg-muted/30 transition-colors",
                                                    isRunning && "bg-primary/5"
                                                )}
                                            >
                                                {/* Header Row */}
                                                <div className="flex items-center gap-3">
                                                    <span className={cn(
                                                        "text-xs font-bold tracking-wider min-w-[70px]",
                                                        isRunning ? "text-primary" : "text-muted-foreground"
                                                    )}>
                                                        {stageConfig.code}
                                                    </span>

                                                    {/* Source Logo for search steps */}
                                                    {step.sourceName && (
                                                        <SourceLogo
                                                            type={getSourceType(step.sourceName)}
                                                            className="h-4 w-4"
                                                        />
                                                    )}

                                                    <span className="text-foreground">
                                                        {step.message}
                                                    </span>

                                                    {step.duration && (
                                                        <span className="text-xs text-muted-foreground ml-auto">
                                                            {step.duration}s
                                                        </span>
                                                    )}

                                                    {hasDetails && (
                                                        <button
                                                            onClick={() => toggleStep(step.id)}
                                                            className="ml-2 text-muted-foreground hover:text-foreground transition-colors"
                                                        >
                                                            <motion.div
                                                                animate={{ rotate: isStepExpanded ? 90 : 0 }}
                                                                transition={{ duration: 0.15 }}
                                                            >
                                                                <ChevronRight className="h-3.5 w-3.5" />
                                                            </motion.div>
                                                        </button>
                                                    )}
                                                </div>

                                                {/* Details */}
                                                <AnimatePresence>
                                                    {isStepExpanded && hasDetails && (
                                                        <motion.div
                                                            initial={{ height: 0, opacity: 0 }}
                                                            animate={{ height: "auto", opacity: 1 }}
                                                            exit={{ height: 0, opacity: 0 }}
                                                            transition={{ duration: 0.15 }}
                                                            className="mt-2 ml-[70px] space-y-2 overflow-hidden"
                                                        >
                                                            {step.queries?.map((q, i) => (
                                                                <div
                                                                    key={i}
                                                                    className="pl-3 border-l-2 border-border space-y-1"
                                                                >
                                                                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                                        <Zap className="h-3 w-3" />
                                                                        <span className="font-mono">{'>'} {q.query}</span>
                                                                    </div>
                                                                    <div className="flex flex-wrap gap-1 pl-5">
                                                                        {q.sources.map((src, sIdx) => {
                                                                            const srcType = getSourceType(src);
                                                                            const srcConfig = SOURCE_CONFIG[srcType] || SOURCE_CONFIG.default;
                                                                            return (
                                                                                <span
                                                                                    key={sIdx}
                                                                                    className="flex items-center gap-1 text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded"
                                                                                >
                                                                                    <SourceLogo type={srcType} className="h-3 w-3" />
                                                                                    {srcConfig.label}
                                                                                </span>
                                                                            );
                                                                        })}
                                                                    </div>
                                                                </div>
                                                            ))}

                                                            {step.data?.hypotheses && (
                                                                <div className="pl-3 border-l-2 border-border space-y-1">
                                                                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider">
                                                                        Hypotheses
                                                                    </span>
                                                                    {step.data.hypotheses.map((h, hi) => (
                                                                        <div
                                                                            key={hi}
                                                                            className="text-xs text-muted-foreground pl-2"
                                                                        >
                                                                            • {h}
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            )}
                                                        </motion.div>
                                                    )}
                                                </AnimatePresence>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default ThinkingPanel;
