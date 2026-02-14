/**
 * Drug Discovery Store - Zustand without immer
 * Manages drug discovery state and API calls
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { axiosInstance } from '@/lib/axios';

interface ThinkingStep {
    step: number;
    title: string;
    description: string;
    status: 'pending' | 'in_progress' | 'completed';
    timestamp: string;
}

interface ADMET {
    bioavailability: number;
    toxicity_risk: string;
    half_life: number;
}

interface Lipinski {
    violations: number;
    passes: boolean;
}

interface Candidate {
    id: string;
    smiles: string;
    molecular_formula: string;
    molecular_weight: number;
    qed: number;
    logp: number;
    tpsa: number;
    confidence: number;
    target_proteins: string[];
    generation_method: string;
    admet: ADMET;
    lipinski: Lipinski;
}

interface Metadata {
    totalDuration: string;
    queriesExecuted: number;
    sourcesFound: number;
    sourcesUsed: number;
    modelUsed: string;
    timestamp: string;
    totalCandidates: number;
}

interface ResearchResult {
    content: string;
    sources: Array<{
        title: string;
        url: string;
        category?: string;
        database?: string;
    }>;
    symptoms: string;
    extractedSymptoms: string;
    candidates: Candidate[];
    metadata: Metadata;
}

interface DrugDiscoveryState {
    isResearching: boolean;
    results: ResearchResult | null;
    thinkingSteps: ThinkingStep[];
    error: string | null;
    currentQuery: string;
    
    startResearch: (query: string) => Promise<void>;
    reset: () => void;
    setError: (error: string | null) => void;
}

export const useDrugDiscoveryStore = create<DrugDiscoveryState>()(
    devtools((set, get) => ({
        isResearching: false,
        results: null,
        thinkingSteps: [],
        error: null,
        currentQuery: '',
        
        startResearch: async (query: string) => {
            set({
                isResearching: true,
                currentQuery: query,
                results: null,
                error: null,
                thinkingSteps: []
            });
            
            try {
                const symptoms = query.split(/[,\n]+/).map(s => s.trim()).filter(s => s.length > 0);
                
                if (symptoms.length === 0) {
                    throw new Error('No valid symptoms provided');
                }
                
                console.log('[Store] Starting drug discovery for:', symptoms);
                
                const response = await axiosInstance.post('/drug-discovery/discover', {
                    symptoms,
                    n_candidates: 5
                });
                
                if (response.data.success) {
                    // Transform backend response to frontend format
                    const transformedResults = {
                        content: `# Drug Discovery Results\n\n## Input Symptoms\n${response.data.symptoms?.join(', ') || ''}\n\n## Generated Candidates (${response.data.candidates?.length || 0})`,
                        sources: [],
                        symptoms: response.data.symptoms?.join(', ') || '',
                        extractedSymptoms: response.data.symptoms?.join(', ') || '',
                        candidates: response.data.candidates || [],
                        metadata: {
                            totalDuration: `${(response.data.candidates?.length || 0) * 2}s`,
                            queriesExecuted: response.data.symptoms?.length || 0,
                            sourcesFound: 0,
                            sourcesUsed: 0,
                            modelUsed: 'NOVO-1 v3.0',
                            timestamp: response.data.timestamp,
                            totalCandidates: response.data.candidates?.length || 0
                        }
                    };
                    
                    set({
                        results: transformedResults,
                        thinkingSteps: response.data.thinking_steps || [],
                        isResearching: false,
                        error: null
                    });
                    console.log('[Store] Drug discovery completed successfully');
                } else {
                    throw new Error(response.data.error || 'Drug discovery failed');
                }
                
            } catch (error: any) {
                console.error('[Store] Drug discovery error:', error);
                set({
                    isResearching: false,
                    error: error.response?.data?.error || error.message || 'An error occurred during drug discovery',
                    results: null
                });
            }
        },
        
        reset: () => {
            set({
                isResearching: false,
                results: null,
                thinkingSteps: [],
                error: null,
                currentQuery: ''
            });
        },
        
        setError: (error: string | null) => {
            set({ error });
        }
    }), { name: 'drug-discovery-store' })
);
