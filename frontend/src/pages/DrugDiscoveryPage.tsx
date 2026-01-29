import { useDrugDiscoveryStore } from "@/store/useDrugDiscoveryStore";
import { useResearchHistoryStore } from "@/store/useResearchHistoryStore";
import { ThinkingPanel } from "@/components/drug-discovery/ThinkingPanel";
import { ResultsPanel } from "@/components/drug-discovery/ResultsPanel";
import { FlaskConical, ArrowLeft, RotateCcw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate, useParams } from "react-router-dom";
import { useEffect } from "react";

export default function DrugDiscoveryPage() {
    const { isResearching, results: storeResults, thinkingSteps, error, reset } = useDrugDiscoveryStore();
    const { currentResult, isLoadingDetail, fetchResultById } = useResearchHistoryStore();
    const navigate = useNavigate();
    const { id } = useParams<{ id: string }>();

    // Determine if viewing historical result (has ID in URL)
    const isHistoricalView = !!id;

    // Fetch historical result when ID is present
    useEffect(() => {
        if (id) {
            fetchResultById(id);
        }
    }, [id, fetchResultById]);

    // Redirect to dashboard if no active research and not viewing historical
    useEffect(() => {
        if (!isHistoricalView && !isResearching && !storeResults && !error) {
            navigate("/dashboard");
        }
    }, [isHistoricalView, isResearching, storeResults, error, navigate]);

    const handleBack = () => {
        if (isHistoricalView) {
            navigate("/dashboard/history");
        } else {
            navigate("/dashboard");
        }
    };

    const handleReset = () => {
        reset();
        navigate("/dashboard");
    };

    // Determine which results to display
    const displayResults = isHistoricalView ? currentResult : storeResults;
    const showThinkingPanel = !isHistoricalView && (isResearching || thinkingSteps.length > 0);

    // Show loading state for historical view
    if (isHistoricalView && isLoadingDetail) {
        return (
            <div className="w-full mx-auto space-y-8 pb-12 px-4 md:px-6 lg:px-8">
                <div className="flex items-center justify-center py-24">
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        <p className="text-sm text-muted-foreground">Loading research result...</p>
                    </div>
                </div>
            </div>
        );
    }

    // Don't render if no data to show
    if (!isHistoricalView && !isResearching && !storeResults && !error) {
        return null;
    }

    // Show error if historical result not found
    if (isHistoricalView && !currentResult && !isLoadingDetail) {
        return (
            <div className="w-full mx-auto space-y-8 pb-12 px-4 md:px-6 lg:px-8">
                <div className="flex items-center gap-4 py-6">
                    <Button variant="ghost" size="icon" onClick={handleBack} className="rounded-full">
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <h1 className="text-2xl font-bold tracking-tight">Research Not Found</h1>
                </div>
                <div className="p-12 rounded-2xl bg-red-500/5 border border-red-500/20 text-center space-y-4">
                    <div className="mx-auto w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
                        <span className="text-2xl">🔍</span>
                    </div>
                    <div className="space-y-1">
                        <h3 className="text-lg font-bold text-red-500">Result Not Found</h3>
                        <p className="text-sm text-muted-foreground">
                            This research result may have been deleted or doesn't exist.
                        </p>
                    </div>
                    <Button variant="outline" onClick={() => navigate("/dashboard/history")} className="mt-4">
                        Back to History
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full mx-auto space-y-8 pb-12 px-4 md:px-6 lg:px-8">
            {/* Header */}
            <div className="flex items-center justify-between animate-in fade-in slide-in-from-top-4 duration-500 py-6">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={handleBack} className="rounded-full">
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/10 rounded-xl">
                            <FlaskConical className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight">
                                {isHistoricalView ? "Drug Discovery Result" : "Drug Discovery"}
                            </h1>
                            <p className="text-xs text-muted-foreground font-medium uppercase tracking-widest">
                                {isHistoricalView ? "Historical Analysis" : "Deep Research Engine v2.0"}
                            </p>
                        </div>
                    </div>
                </div>

                {displayResults && (
                    <Button variant="outline" size="sm" onClick={handleReset} className="gap-2 rounded-lg border-border/50">
                        <RotateCcw className="h-4 w-4" />
                        New Discovery
                    </Button>
                )}
            </div>

            {/* Main Content */}
            <div className="space-y-8">
                {/* Thinking panel visible during research and even after results */}
                {showThinkingPanel && (
                    <div className="animate-in fade-in slide-in-from-top-4 duration-700">
                        <ThinkingPanel steps={thinkingSteps} isActive={isResearching} />
                    </div>
                )}

                {/* Results Display */}
                {displayResults && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                        <ResultsPanel results={displayResults} />
                    </div>
                )}

                {/* Error State */}
                {!isHistoricalView && error && (
                    <div className="p-12 rounded-2xl bg-red-500/5 border border-red-500/20 text-center space-y-4">
                        <div className="mx-auto w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
                            <span className="text-2xl">⚠️</span>
                        </div>
                        <div className="space-y-1">
                            <h3 className="text-lg font-bold text-red-500">Discovery Failed</h3>
                            <p className="text-sm text-muted-foreground">{error}</p>
                        </div>
                        <Button variant="outline" onClick={handleReset} className="mt-4 border-red-500/20 text-red-500 hover:bg-red-500/10">
                            Try Again
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
