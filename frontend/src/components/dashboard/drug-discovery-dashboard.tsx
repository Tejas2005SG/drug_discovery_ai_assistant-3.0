import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import {
    ArrowUp,
    Sparkles,
    Layers,
    Search,
    Info,
    FlaskConical,
    RotateCcw
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useDrugDiscoveryStore } from "@/store/useDrugDiscoveryStore";
import { ResultsPanel } from "@/components/drug-discovery/ResultsPanel";

export function DrugDiscoveryDashboard() {
    const [query, setQuery] = useState("");
    const { 
        startResearch, 
        isResearching, 
        results: storeResults, 
        thinkingSteps, 
        error, 
        reset 
    } = useDrugDiscoveryStore();

    const hasContent = isResearching || storeResults || error;

    const handleSearch = () => {
        if (!query.trim() || isResearching) return;
        startResearch(query);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSearch();
        }
    };

    const handleReset = () => {
        reset();
        setQuery("");
    };

    return (
        <div className="flex flex-col items-center justify-start min-h-[70vh] w-full max-w-5xl mx-auto p-4 space-y-8">
            
            {/* Hero Section - Hide when showing results */}
            {!hasContent && (
                <div className="text-center space-y-4 animate-in fade-in slide-in-from-top-4 duration-1000">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold mb-2">
                        <Sparkles className="h-3 w-3" />
                        <span>AI-Powered Drug Discovery</span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-br from-foreground to-foreground/60 bg-clip-text text-transparent">
                        Accelerate Your Drug Discovery
                    </h1>
                    <p className="text-muted-foreground text-sm max-w-lg mx-auto leading-relaxed">
                        Identify targets, generate candidates, and analyze molecular properties with our advanced AI agents.
                    </p>
                </div>
            )}

            {/* Main Search Interface */}
            <div className={cn(
                "w-full relative group animate-in zoom-in-95 duration-700",
                hasContent && "sticky top-4 z-50"
            )}>
                {/* Visual Glow */}
                <div className="absolute -inset-2 bg-gradient-to-r from-primary/20 to-purple-500/20 rounded-[2rem] blur-2xl opacity-50 group-hover:opacity-100 transition duration-700"></div>

                <div className="relative bg-white/70 dark:bg-black/40 backdrop-blur-2xl border border-white/20 dark:border-white/10 rounded-2xl overflow-hidden shadow-2xl transition-all duration-500 ring-1 ring-black/5 dark:ring-white/5">

                    {/* Header Controls */}
                    <div className="px-4 pt-4 flex items-center justify-between border-b border-white/10 pb-2">
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/30 border border-border/50">
                                <Search className="h-3.5 w-3.5 text-primary" />
                                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                                    {hasContent ? 'Discovery in Progress' : 'New Discovery Project'}
                                </span>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            {storeResults && (
                                <Button 
                                    variant="ghost" 
                                    size="sm" 
                                    onClick={handleReset}
                                    className="h-8 gap-2 text-xs"
                                >
                                    <RotateCcw className="h-3.5 w-3.5" />
                                    New Discovery
                                </Button>
                            )}
                            <Info className="h-3.5 w-3.5 text-muted-foreground cursor-help" />
                        </div>
                    </div>

                    {/* Input Area */}
                    <div className="p-6">
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Enter symptoms (e.g., fever, cough, fatigue)..."
                            disabled={isResearching}
                            className="w-full bg-transparent border-none text-xl sm:text-2xl placeholder:text-muted-foreground/30 focus:outline-none resize-none min-h-[100px] scrollbar-hide text-foreground leading-tight disabled:opacity-50"
                        />
                    </div>

                    {/* Bottom Actions */}
                    <div className="px-6 pb-6 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Layers className="h-4 w-4 text-muted-foreground/50" />
                            <span className="text-xs text-muted-foreground/50">
                                {isResearching ? 'Processing with NOVO-1 AI...' : 'Accessing Global Chemical Databases'}
                            </span>
                        </div>

                        <Button
                            onClick={handleSearch}
                            disabled={!query.trim() || isResearching}
                            className={cn(
                                "rounded-xl h-12 w-12 transition-all duration-500",
                                query.trim()
                                    ? "bg-primary text-primary-foreground shadow-[0_0_20px_rgba(var(--primary),0.3)] scale-100 hover:scale-110 active:scale-95"
                                    : "bg-muted text-muted-foreground/30 shadow-none scale-100 opacity-50 cursor-not-allowed"
                            )}
                        >
                            <ArrowUp className="h-6 w-6" />
                        </Button>
                    </div>
                </div>
            </div>

            {/* Thinking Steps Panel - Show during research AND after completion */}
            {(isResearching || (storeResults && thinkingSteps.length > 0)) && (
                <div className="w-full animate-in fade-in slide-in-from-top-4 duration-700">
                    <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-primary/10 rounded-lg">
                                <Layers className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <h3 className="font-semibold">AI Thinking Process</h3>
                                <p className="text-xs text-muted-foreground">
                                    {isResearching ? 'Analyzing in real-time...' : 'Analysis complete'}
                                </p>
                            </div>
                        </div>
                        
                        <div className="space-y-3">
                            {thinkingSteps.map((step, idx) => (
                                <div 
                                    key={idx} 
                                    className={`flex items-start gap-3 p-3 rounded-lg border transition-all duration-300 ${
                                        step.status === 'completed' 
                                            ? 'bg-primary/5 border-primary/20' 
                                            : step.status === 'in_progress'
                                            ? 'bg-amber-500/5 border-amber-500/20'
                                            : 'bg-muted/30 border-border'
                                    }`}
                                >
                                    <div className={`mt-0.5 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                                        step.status === 'completed' 
                                            ? 'bg-primary text-primary-foreground' 
                                            : step.status === 'in_progress'
                                            ? 'bg-amber-500 text-white animate-pulse'
                                            : 'bg-muted text-muted-foreground'
                                    }`}>
                                        {step.status === 'completed' ? '✓' : step.status === 'in_progress' ? '◐' : idx + 1}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between">
                                            <h4 className="font-medium text-sm">{step.title || `Step ${idx + 1}`}</h4>
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                                                step.status === 'completed' 
                                                    ? 'bg-primary/10 text-primary' 
                                                    : step.status === 'in_progress'
                                                    ? 'bg-amber-500/10 text-amber-600'
                                                    : 'bg-muted text-muted-foreground'
                                            }`}>
                                                {step.status === 'completed' ? 'Done' : step.status === 'in_progress' ? 'Working...' : 'Pending'}
                                            </span>
                                        </div>
                                        <p className="text-sm text-muted-foreground mt-1">{step.description}</p>
                                        
                                        {/* Show details if available */}
                                        {step.details && (
                                            <div className="mt-2 p-2 bg-background/50 rounded text-xs text-muted-foreground border border-border/50">
                                                {Object.entries(step.details).map(([key, value]) => {
                                                    // Handle different value types
                                                    let displayValue;
                                                    if (Array.isArray(value)) {
                                                        displayValue = value.join(', ');
                                                    } else if (typeof value === 'object' && value !== null) {
                                                        // For nested objects, show as formatted JSON
                                                        displayValue = JSON.stringify(value).slice(0, 100) + (JSON.stringify(value).length > 100 ? '...' : '');
                                                    } else {
                                                        displayValue = String(value);
                                                    }
                                                    
                                                    return (
                                                        <div key={key} className="flex justify-between py-0.5">
                                                            <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                                                            <span className="font-mono truncate max-w-[200px]" title={displayValue}>{displayValue}</span>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Results Panel */}
            {storeResults && (
                <div className="w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-primary/10 rounded-xl">
                            <FlaskConical className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold tracking-tight">Discovery Results</h2>
                            <p className="text-xs text-muted-foreground font-medium uppercase tracking-widest">
                                NOVO-1 AI System v3.0
                            </p>
                        </div>
                    </div>
                    <ResultsPanel results={storeResults} />
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="w-full p-12 rounded-2xl bg-red-500/5 border border-red-500/20 text-center space-y-4 animate-in fade-in duration-500">
                    <div className="mx-auto w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
                        <span className="text-2xl">⚠</span>
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

            {/* Footer Disclaimer - Hide when showing results */}
            {!hasContent && (
                <div className="pt-8 border-t border-border/30 w-full max-w-sm mx-auto text-center opacity-40">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest leading-relaxed">
                        Discover new drugs for disease using AI. <br />
                    </p>
                </div>
            )}
        </div>
    );
}
