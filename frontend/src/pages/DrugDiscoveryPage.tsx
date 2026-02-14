import { useDrugDiscoveryStore } from "@/store/useDrugDiscoveryStore";
import { ThinkingPanel } from "@/components/drug-discovery/ThinkingPanel";
import { ResultsPanel } from "@/components/drug-discovery/ResultsPanel";
import { FlaskConical, ArrowLeft, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function DrugDiscoveryPage() {
    const { isResearching, results: storeResults, thinkingSteps, error, reset } = useDrugDiscoveryStore();
    const navigate = useNavigate();

    const handleBack = () => {
        navigate("/dashboard");
    };

    const handleReset = () => {
        reset();
        navigate("/dashboard");
    };

    if (!isResearching && !storeResults && !error) {
        return null;
    }

    return (
        <div className="w-full mx-auto space-y-8 pb-12 px-4 md:px-6 lg:px-8">
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
                            <h1 className="text-2xl font-bold tracking-tight">Drug Discovery</h1>
                            <p className="text-xs text-muted-foreground font-medium uppercase tracking-widest">
                                NOVO-1 AI System v3.0
                            </p>
                        </div>
                    </div>
                </div>

                {storeResults && (
                    <Button variant="outline" size="sm" onClick={handleReset} className="gap-2 rounded-lg border-border/50">
                        <RotateCcw className="h-4 w-4" />
                        New Discovery
                    </Button>
                )}
            </div>

            <div className="space-y-8">
                {isResearching && thinkingSteps.length > 0 && (
                    <div className="animate-in fade-in slide-in-from-top-4 duration-700">
                        <ThinkingPanel steps={thinkingSteps} isActive={isResearching} />
                    </div>
                )}

                {storeResults && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                        <ResultsPanel results={storeResults} />
                    </div>
                )}

                {error && (
                    <div className="p-12 rounded-2xl bg-red-500/5 border border-red-500/20 text-center space-y-4">
                        <div className="mx-auto w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
                            <span className="text-2xl">X</span>
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
