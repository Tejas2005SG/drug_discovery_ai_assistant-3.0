import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
    Clock,
    Search,
    Star,
    Trash2,
    ExternalLink,
    ChevronLeft,
    ChevronRight,
    Microscope,
    Database,
    FileText,
    Tag,
    MoreVertical,
    X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { useResearchHistoryStore, type ResearchResult } from "@/store/useResearchHistoryStore";
import { cn } from "@/lib/utils";

const ITEMS_PER_PAGE = 10;

const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
        clinical: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
        protein: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
        compound: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
        pathway: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
        trials: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
        general: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
    };
    return colors[category] || colors.general;
};

const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
        clinical: "🧬",
        protein: "🧪",
        compound: "💊",
        pathway: "🔄",
        trials: "📋",
        general: "📄",
    };
    return icons[category] || icons.general;
};

export const ResearchHistory: React.FC = () => {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedResult, setSelectedResult] = useState<ResearchResult | null>(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [resultToDelete, setResultToDelete] = useState<string | null>(null);

    const {
        results,
        pagination,
        isLoading,
        fetchHistory,
        deleteResult,
        updateResult,
        setCurrentResult,
    } = useResearchHistoryStore();

    useEffect(() => {
        fetchHistory(1, ITEMS_PER_PAGE);
    }, []);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            fetchHistory(1, ITEMS_PER_PAGE, searchQuery);
        }, 300);
        return () => clearTimeout(timeoutId);
    }, [searchQuery]);

    const handlePageChange = (page: number) => {
        fetchHistory(page, ITEMS_PER_PAGE, searchQuery);
    };

    const handleViewResult = (result: ResearchResult) => {
        setCurrentResult(result);
        setSelectedResult(result);
    };

    const handleDeleteClick = (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setResultToDelete(id);
        setDeleteDialogOpen(true);
    };

    const handleConfirmDelete = async () => {
        if (resultToDelete) {
            await deleteResult(resultToDelete);
            setDeleteDialogOpen(false);
            setResultToDelete(null);
        }
    };

    const handleToggleStar = async (id: string, isStarred: boolean, e: React.MouseEvent) => {
        e.stopPropagation();
        await updateResult(id, { isStarred: !isStarred });
    };

    const handleCloseDetail = () => {
        setSelectedResult(null);
        setCurrentResult(null);
    };

    // Calculate source breakdown for display
    const getSourceBreakdown = (result: ResearchResult) => {
        const breakdown = result.metadata?.sourceBreakdown;
        if (!breakdown) return [];

        return Object.entries(breakdown)
            .filter(([_, count]) => count > 0)
            .map(([category, count]) => ({ category, count }));
    };

    return (
        <div className="w-full p-6 md:p-8 space-y-8 animate-in fade-in duration-700">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Drug Discovery History</h1>
                    <p className="text-muted-foreground mt-1 text-sm">
                        View and manage your drug discovery results
                    </p>
                </div>
                <Button onClick={() => navigate("/dashboard")} className="gap-2 shadow-sm">
                    <Microscope className="h-4 w-4" />
                    New Discovery
                </Button>
            </div>

            {/* Search */}
            <div className="relative group">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <Input
                    placeholder="Search your drug discovery history..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 h-11 bg-background/50 backdrop-blur-sm border-muted-foreground/20 focus:border-primary/50 transition-all"
                />
            </div>

            {/* Results List */}
            <div className="space-y-4">
                {isLoading ? (
                    <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                ) : results.length === 0 ? (
                    <Card className="border-dashed">
                        <CardContent className="flex flex-col items-center justify-center py-12">
                            <Database className="h-12 w-12 text-muted-foreground/30 mb-4" />
                            <h3 className="text-lg font-medium">No drug discovery history yet</h3>
                            <p className="text-muted-foreground text-center max-w-sm mt-2 text-sm">
                                Start your first drug discovery process to see results here
                            </p>
                            <Button
                                className="mt-6"
                                onClick={() => navigate("/dashboard")}
                            >
                                Start Drug Discovery
                            </Button>
                        </CardContent>
                    </Card>
                ) : (
                    results.map((result) => (
                        <Card
                            key={result._id}
                            className="cursor-pointer hover:border-primary/50 transition-colors"
                            onClick={() => handleViewResult(result)}
                        >
                            <CardContent className="p-4">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-2">
                                            <h3 className="font-semibold truncate">
                                                {result.extractedSymptoms || result.symptoms}
                                            </h3>
                                            {result.isStarred && (
                                                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                                            )}
                                        </div>

                                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                            <span className="flex items-center gap-1">
                                                <Clock className="h-3.5 w-3.5" />
                                                {new Date(result.createdAt).toLocaleDateString("en-US", {
                                                    month: "short",
                                                    day: "numeric",
                                                    year: "numeric",
                                                })}
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Database className="h-3.5 w-3.5" />
                                                {result.metadata?.sourcesUsed || result.sources?.length || 0} sources
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <FileText className="h-3.5 w-3.5" />
                                                {result.metadata?.queriesExecuted || 0} queries
                                            </span>
                                        </div>

                                        {/* Source Breakdown */}
                                        {getSourceBreakdown(result).length > 0 && (
                                            <div className="flex flex-wrap gap-1 mt-3">
                                                {getSourceBreakdown(result).map(({ category, count }) => (
                                                    <Badge
                                                        key={category}
                                                        variant="secondary"
                                                        className={cn("text-xs", getCategoryColor(category))}
                                                    >
                                                        {getCategoryIcon(category)} {category}: {count}
                                                    </Badge>
                                                ))}
                                            </div>
                                        )}

                                        {/* Tags */}
                                        {result.tags && result.tags.length > 0 && (
                                            <div className="flex flex-wrap gap-1 mt-2">
                                                {result.tags.map((tag) => (
                                                    <Badge key={tag} variant="outline" className="text-xs">
                                                        <Tag className="h-3 w-3 mr-1" />
                                                        {tag}
                                                    </Badge>
                                                ))}
                                            </div>
                                        )}
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8"
                                            onClick={(e) => handleToggleStar(result._id, !!result.isStarred, e)}
                                        >
                                            <Star
                                                className={cn(
                                                    "h-4 w-4",
                                                    result.isStarred
                                                        ? "fill-yellow-400 text-yellow-400"
                                                        : "text-muted-foreground"
                                                )}
                                            />
                                        </Button>
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-8 w-8"
                                                    onClick={(e) => e.stopPropagation()}
                                                >
                                                    <MoreVertical className="h-4 w-4" />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem onClick={() => handleViewResult(result)}>
                                                    <ExternalLink className="h-4 w-4 mr-2" />
                                                    View Details
                                                </DropdownMenuItem>
                                                <DropdownMenuItem
                                                    className="text-destructive"
                                                    onClick={(e: React.MouseEvent) => handleDeleteClick(result._id, e)}
                                                >
                                                    <Trash2 className="h-4 w-4 mr-2" />
                                                    Delete
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>

            {/* Pagination */}
            {!isLoading && pagination.totalPages > 1 && (
                <div className="flex items-center justify-between">
                    <p className="text-sm text-muted-foreground">
                        Showing {(pagination.page - 1) * pagination.limit + 1} -{" "}
                        {Math.min(pagination.page * pagination.limit, pagination.total)} of{" "}
                        {pagination.total} results
                    </p>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handlePageChange(pagination.page - 1)}
                            disabled={pagination.page === 1}
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </Button>
                        <span className="text-sm">
                            Page {pagination.page} of {pagination.totalPages}
                        </span>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handlePageChange(pagination.page + 1)}
                            disabled={pagination.page === pagination.totalPages}
                        >
                            <ChevronRight className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            )}

            {/* Detail Dialog */}
            <Dialog open={!!selectedResult} onOpenChange={handleCloseDetail}>
                <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto overflow-x-hidden">
                    {selectedResult && (
                        <>
                            <DialogHeader className="flex flex-row items-start justify-between">
                                <div>
                                    <DialogTitle className="flex items-center gap-2 text-xl">
                                        <Microscope className="h-5 w-5 text-primary" />
                                        Drug Discovery Result
                                    </DialogTitle>
                                    <DialogDescription>
                                        {selectedResult.extractedSymptoms || selectedResult.symptoms}
                                    </DialogDescription>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Button
                                        size="sm"
                                        onClick={() => navigate(`/dashboard/research/${selectedResult._id}`)}
                                    >
                                        <Microscope className="h-4 w-4 mr-2" />
                                        View Complete Analysis
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-8 w-8"
                                        onClick={handleCloseDetail}
                                    >
                                        <X className="h-4 w-4" />
                                    </Button>
                                </div>
                            </DialogHeader>

                            <div className="space-y-6 py-4">
                                {/* Metadata */}
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                                    <Card>
                                        <CardContent className="p-3">
                                            <p className="text-xs text-muted-foreground">Date</p>
                                            <p className="font-medium">
                                                {new Date(selectedResult.createdAt).toLocaleDateString("en-US", {
                                                    month: "short",
                                                    day: "numeric",
                                                    year: "numeric",
                                                })}
                                            </p>
                                        </CardContent>
                                    </Card>
                                    <Card>
                                        <CardContent className="p-3">
                                            <p className="text-xs text-muted-foreground">Duration</p>
                                            <p className="font-medium">
                                                {selectedResult.metadata?.totalDuration || "N/A"}
                                            </p>
                                        </CardContent>
                                    </Card>
                                    <Card>
                                        <CardContent className="p-3">
                                            <p className="text-xs text-muted-foreground">Sources</p>
                                            <p className="font-medium">
                                                {selectedResult.metadata?.sourcesUsed || selectedResult.sources?.length || 0}
                                            </p>
                                        </CardContent>
                                    </Card>
                                    <Card>
                                        <CardContent className="p-3">
                                            <p className="text-xs text-muted-foreground">Model</p>
                                            <p className="font-medium">
                                                {selectedResult.metadata?.modelUsed || "N/A"}
                                            </p>
                                        </CardContent>
                                    </Card>
                                </div>

                                {/* Content Preview */}
                                <div>
                                    <h4 className="text-sm font-semibold mb-2">Content Preview</h4>
                                    <Card>
                                        <CardContent className="p-4">
                                            <div className="prose prose-sm dark:prose-invert max-w-none max-h-64 overflow-y-auto overflow-x-hidden">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                    {selectedResult.content.substring(0, 2000) + (selectedResult.content.length > 2000 ? "..." : "")}
                                                </ReactMarkdown>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </div>

                                {/* Sources */}
                                {selectedResult.sources && selectedResult.sources.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-semibold mb-2">
                                            Sources ({selectedResult.sources.length})
                                        </h4>
                                        <div className="space-y-2 max-h-64 overflow-y-auto">
                                            {selectedResult.sources.map((source, index) => (
                                                <Card key={index} className="bg-muted/30">
                                                    <CardContent className="p-3">
                                                        <div className="flex items-start justify-between gap-2">
                                                            <div className="flex-1 min-w-0">
                                                                <p className="text-sm font-medium truncate">
                                                                    {source.title}
                                                                </p>
                                                                <p className="text-xs text-muted-foreground truncate">
                                                                    {source.url}
                                                                </p>
                                                            </div>
                                                            <div className="flex items-center gap-2">
                                                                <Badge
                                                                    variant="secondary"
                                                                    className={cn("text-xs", getCategoryColor(source.category || "general"))}
                                                                >
                                                                    {source.category || "general"}
                                                                </Badge>
                                                                <a
                                                                    href={source.url}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-primary hover:underline"
                                                                >
                                                                    <ExternalLink className="h-4 w-4" />
                                                                </a>
                                                            </div>
                                                        </div>
                                                    </CardContent>
                                                </Card>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </DialogContent>
            </Dialog>

            {/* Delete Confirmation Dialog */}
            <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Delete Drug Discovery Result</DialogTitle>
                        <DialogDescription>
                            Are you sure you want to delete this drug discovery result? This action cannot be undone.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
                            Cancel
                        </Button>
                        <Button variant="destructive" onClick={handleConfirmDelete}>
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default ResearchHistory;

