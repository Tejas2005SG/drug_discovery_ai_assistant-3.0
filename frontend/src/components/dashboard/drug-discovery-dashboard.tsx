import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import {
    ArrowUp,
    Sparkles,
    Layers,
    Search,
    Info
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useDrugDiscoveryStore } from "@/store/useDrugDiscoveryStore";

export function DrugDiscoveryDashboard() {
    const [query, setQuery] = useState("");
    const navigate = useNavigate();
    const { startResearch, isResearching } = useDrugDiscoveryStore();

    const handleSearch = () => {
        if (!query.trim() || isResearching) return;
        startResearch(query);
        navigate("/dashboard/research");
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSearch();
        }
    };



    return (
        <div className="flex flex-col items-center justify-center min-h-[70vh] w-full max-w-3xl mx-auto p-4 space-y-12">

            {/* Hero Section */}
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

            {/* Main Search Interface */}
            <div className="w-full relative group animate-in zoom-in-95 duration-700">
                {/* Visual Glow */}
                <div className="absolute -inset-2 bg-gradient-to-r from-primary/20 to-purple-500/20 rounded-[2rem] blur-2xl opacity-50 group-hover:opacity-100 transition duration-700"></div>

                <div className="relative bg-white/70 dark:bg-black/40 backdrop-blur-2xl border border-white/20 dark:border-white/10 rounded-2xl overflow-hidden shadow-2xl transition-all duration-500 ring-1 ring-black/5 dark:ring-white/5">

                    {/* Header Controls */}
                    <div className="px-4 pt-4 flex items-center justify-between border-b border-white/10 pb-2">
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/30 border border-border/50">
                                <Search className="h-3.5 w-3.5 text-primary" />
                                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">New Discovery Project</span>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <Info className="h-3.5 w-3.5 text-muted-foreground cursor-help" />
                            <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-tighter">
                                Computed Molecular Intelligence
                            </span>
                        </div>
                    </div>

                    {/* Input Area */}
                    <div className="p-6">
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Enter Symptoms..."
                            className="w-full bg-transparent border-none text-xl sm:text-2xl placeholder:text-muted-foreground/30 focus:outline-none resize-none min-h-[100px] scrollbar-hide text-foreground leading-tight"
                        />
                    </div>

                    {/* Bottom Actions */}
                    <div className="px-6 pb-6 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Layers className="h-4 w-4 text-muted-foreground/50" />
                            <span className="text-xs text-muted-foreground/50">Accessing Global Chemical Databases</span>
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



            {/* Footer Disclaimer */}
            <div className="pt-8 border-t border-border/30 w-full max-w-sm mx-auto text-center opacity-40">
                <p className="text-[10px] text-muted-foreground uppercase tracking-widest leading-relaxed">
                    Discover new drugs for disease using AI. <br />

                </p>
            </div>
        </div>
    );
}
