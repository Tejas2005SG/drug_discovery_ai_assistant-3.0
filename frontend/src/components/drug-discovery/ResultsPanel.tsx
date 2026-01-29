import React, { useState, useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
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
    Link as LinkIcon
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
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

interface ResearchResult {
    content: string;
    sources: Source[];
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
    // Basic heuristic for SMILES strings
    // 1. No spaces
    // 2. Contains usually mixed case, numbers, special chars like () = #
    // 3. Reasonable length (e.g. > 5)
    // 4. Not a common word (handled by space check mostly)
    if (!text || typeof text !== 'string' || text.includes(' ')) return false;
    if (text.length < 5) return false;

    // Check for common SMILES characters
    const smilesChars = /[CNOPSFIBrClc1234567890()=\[\]#\-+]/;
    const hasSmilesChars = smilesChars.test(text);

    // Check if it looks like a URL or ID (basic exclusion)
    const isUrl = text.startsWith('http') || text.includes('www');

    return hasSmilesChars && !isUrl;
};

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ results }) => {
    const [copied, setCopied] = useState(false);
    const [activeSourceCategory, setActiveSourceCategory] = useState<string>("all");
    const [showResearchPlan, setShowResearchPlan] = useState(false);

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

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-10">

            {/* --- Main Dossier Card --- */}
            <Card className="border-border shadow-xl bg-card text-card-foreground overflow-hidden">

                {/* Header */}
                <CardHeader className="pb-6 border-b border-border bg-muted/30">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-primary rounded-xl shadow-lg shadow-primary/20">
                                <Microscope className="h-6 w-6 text-primary-foreground" />
                            </div>
                            <div className="space-y-1">
                                <CardTitle className="text-2xl font-bold tracking-tight">
                                    Drug Discovery Dossier
                                </CardTitle>
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Badge variant="outline" className="font-normal bg-muted/50 border-border">
                                        {results.sources?.length || 0} Sources Analyzed
                                    </Badge>
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
                            <Button variant="outline" size="sm" className="h-8">
                                <Download className="h-3.5 w-3.5 mr-1.5" />
                                Export
                            </Button>
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

                {/* Markdown Content Area */}
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
                                strong: ({ children }) => {
                                    return (
                                        <span className="font-semibold text-blue-700 dark:text-blue-300 bg-blue-50/50 dark:bg-blue-900/20 px-1 rounded border border-blue-100/50 dark:border-blue-800/30 mx-0.5">
                                            {children}
                                        </span>
                                    );
                                },
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

            {/* --- Sources Section --- */}
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