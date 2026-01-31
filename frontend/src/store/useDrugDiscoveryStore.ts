import { create } from "zustand";
import { toast } from "sonner";

const API_URL = "http://localhost:5000/api/drug-discovery";

interface ThinkingStep {
  id: string;
  stage: "planning" | "searching" | "thinking" | "generating" | "complete" | "error" | "crawling";
  message: string;
  status: "running" | "completed" | "failed" | "warning";
  timestamp: number;
  duration?: string;
  progress?: number;
  queries?: any[];
  data?: any;
}

interface Source {
  title: string;
  url: string;
  status?: string;
  category?: string;
  contentLength?: number;
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
  candidates?: DrugCandidate[]; // NEW: Hybrid Lead Gen Candidates
  symptoms: string;
  mode: string;
  timestamp: string;
}

interface DrugDiscoveryState {
  isResearching: boolean;
  results: ResearchResult | null;
  thinkingSteps: ThinkingStep[];
  sources: Source[];
  candidates: DrugCandidate[]; // Store candidates separately for easy access
  error: string | null;

  startResearch: (symptoms: string) => Promise<void>;
  reset: () => void;
}

export const useDrugDiscoveryStore = create<DrugDiscoveryState>((set) => ({
  isResearching: false,
  results: null,
  thinkingSteps: [],
  sources: [],
  candidates: [],
  error: null,

  reset: () => set({ results: null, thinkingSteps: [], sources: [], candidates: [], error: null, isResearching: false }),

  startResearch: async (symptoms: string) => {
    set({ isResearching: true, error: null, thinkingSteps: [], results: null, sources: [], candidates: [] });

    try {
      const response = await fetch(`${API_URL}/research`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ symptoms }),
      });

      if (!response.ok) {
        throw new Error("Failed to start research");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No reader available");

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.substring(6));

              if (data.type === "progress") {
                set((state) => {
                  const newSteps = [...state.thinkingSteps];
                  const existingStepIndex = newSteps.findIndex(s => s.id === data.id);

                  if (existingStepIndex !== -1) {
                    // Update existing step only if it's not already completed
                    if (newSteps[existingStepIndex].status !== 'completed' || data.status === 'completed') {
                      newSteps[existingStepIndex] = {
                        ...newSteps[existingStepIndex],
                        ...data,
                        // Ensure optional fields are handled
                        queries: data.queries || newSteps[existingStepIndex].queries,
                        data: data.data || newSteps[existingStepIndex].data,
                      };
                    }
                  } else {
                    // Add new step
                    newSteps.push({
                      id: data.id || Math.random().toString(36).substring(2, 9),
                      stage: data.stage,
                      message: data.message,
                      status: data.status,
                      timestamp: data.timestamp || Date.now(),
                      duration: data.duration,
                      progress: data.progress,
                      queries: data.queries,
                      data: data.data,
                    });
                  }

                  return { thinkingSteps: newSteps };
                });
              } else if (data.type === "complete") {
                set((state) => ({
                  results: data.data,
                  isResearching: false,
                  sources: data.data.sources || [],
                  candidates: data.data.candidates || [],
                  // Force mark all previous steps as completed when the whole process finishes
                  thinkingSteps: state.thinkingSteps.map(step => ({
                    ...step,
                    status: "completed"
                  }))
                }));
              } else if (data.type === "error") {
                set({ error: data.message || "An error occurred during research", isResearching: false });
                toast.error(data.message || "An error occurred");
              }
            } catch (err) {
              console.error("Error parsing SSE data", err);
            }
          }
        }
      }
    } catch (error: any) {
      set({ error: error.message, isResearching: false });
      toast.error(error.message || "Failed to connect to research server");
    }
  },
}));
