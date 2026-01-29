import { create } from "zustand";
import { toast } from "sonner";
import { axiosInstance } from "@/lib/axios";

const API_URL = "/research-results";

interface Source {
  title: string;
  url: string;
  category?: string;
  database?: string;
  contentLength?: number;
  status?: string;
}

interface ResearchPlan {
  strategy?: string;
  hypotheses?: string[];
  targetDatabases?: string[];
}

interface Metadata {
  totalDuration?: string;
  queriesExecuted?: number;
  sourcesFound?: number;
  sourcesCrawled?: number;
  sourcesUsed?: number;
  sourceBreakdown?: {
    clinical?: number;
    protein?: number;
    compound?: number;
    pathway?: number;
    trials?: number;
    general?: number;
  };
  modelUsed?: string;
  timestamp?: string;
  errors?: string[];
}

export interface ResearchResult {
  _id: string;
  symptoms: string;
  extractedSymptoms?: string;
  mode: string;
  content: string;
  sources: Source[];
  researchPlan?: ResearchPlan;
  metadata?: Metadata;
  tags?: string[];
  notes?: string;
  isStarred?: boolean;
  createdAt: string;
  updatedAt: string;
}

interface Pagination {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

interface ResearchHistoryState {
  // Data
  results: ResearchResult[];
  currentResult: ResearchResult | null;
  stats: {
    overview: {
      totalResearches: number;
      totalSourcesUsed: number;
      avgSourcesPerResearch: number;
      totalQueriesExecuted: number;
      starredCount: number;
    };
    categoryBreakdown: {
      clinical: number;
      protein: number;
      compound: number;
      pathway: number;
      trials: number;
      general: number;
    };
    recentActivity: Array<{
      symptoms: string;
      createdAt: string;
      metadataSourcesUsed: number;
    }>;
  } | null;
  tags: string[];

  // Pagination
  pagination: Pagination;

  // Loading states
  isLoading: boolean;
  isLoadingStats: boolean;
  isLoadingDetail: boolean;
  isDeleting: boolean;
  isUpdating: boolean;

  // Error
  error: string | null;

  // Actions
  fetchHistory: (page?: number, limit?: number, search?: string, tag?: string) => Promise<void>;
  fetchResultById: (id: string) => Promise<void>;
  fetchStats: () => Promise<void>;
  fetchTags: () => Promise<void>;
  updateResult: (id: string, data: { notes?: string; tags?: string[]; isStarred?: boolean }) => Promise<boolean>;
  deleteResult: (id: string) => Promise<boolean>;
  setCurrentResult: (result: ResearchResult | null) => void;
  clearError: () => void;
}

export const useResearchHistoryStore = create<ResearchHistoryState>((set, get) => ({
  // Initial state
  results: [],
  currentResult: null,
  stats: null,
  tags: [],
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0,
  },
  isLoading: false,
  isLoadingStats: false,
  isLoadingDetail: false,
  isDeleting: false,
  isUpdating: false,
  error: null,

  // Fetch research history
  fetchHistory: async (page = 1, limit = 20, search = "", tag = "") => {
    set({ isLoading: true, error: null });

    try {
      const params = new URLSearchParams();
      params.append("page", page.toString());
      params.append("limit", limit.toString());
      if (search) params.append("search", search);
      if (tag) params.append("tag", tag);

      const response = await axiosInstance.get(`${API_URL}?${params.toString()}`);

      if (response.data.success) {
        set({
          results: response.data.data,
          pagination: response.data.pagination,
          isLoading: false,
        });
      } else {
        throw new Error(response.data.message || "Failed to fetch history");
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || "Failed to fetch research history";
      set({ error: errorMessage, isLoading: false });
      toast.error(errorMessage);
    }
  },

  // Fetch single result by ID
  fetchResultById: async (id: string) => {
    set({ isLoadingDetail: true, error: null });

    try {
      const response = await axiosInstance.get(`${API_URL}/${id}`);

      if (response.data.success) {
        set({
          currentResult: response.data.data,
          isLoadingDetail: false,
        });
      } else {
        throw new Error(response.data.message || "Failed to fetch result");
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || "Failed to fetch research result";
      set({ error: errorMessage, isLoadingDetail: false });
      toast.error(errorMessage);
    }
  },

  // Fetch statistics
  fetchStats: async () => {
    set({ isLoadingStats: true });

    try {
      const response = await axiosInstance.get(`${API_URL}/stats`);

      if (response.data.success) {
        set({
          stats: response.data.data,
          isLoadingStats: false,
        });
      }
    } catch (error: any) {
      console.error("Failed to fetch stats:", error);
      set({ isLoadingStats: false });
    }
  },

  // Fetch tags
  fetchTags: async () => {
    try {
      const response = await axiosInstance.get(`${API_URL}/tags`);

      if (response.data.success) {
        set({ tags: response.data.data });
      }
    } catch (error: any) {
      console.error("Failed to fetch tags:", error);
    }
  },

  // Update result
  updateResult: async (id: string, data: { notes?: string; tags?: string[]; isStarred?: boolean }) => {
    set({ isUpdating: true, error: null });

    try {
      const response = await axiosInstance.patch(`${API_URL}/${id}`, data);

      if (response.data.success) {
        // Update local state
        const { results, currentResult } = get();
        
        // Update in results list
        const updatedResults = results.map((r) =>
          r._id === id ? { ...r, ...data } : r
        );

        // Update current result if it's the same
        const updatedCurrent = currentResult?._id === id 
          ? { ...currentResult, ...data } 
          : currentResult;

        set({
          results: updatedResults,
          currentResult: updatedCurrent,
          isUpdating: false,
        });

        toast.success("Research result updated");
        return true;
      } else {
        throw new Error(response.data.message || "Failed to update");
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || "Failed to update result";
      set({ error: errorMessage, isUpdating: false });
      toast.error(errorMessage);
      return false;
    }
  },

  // Delete result
  deleteResult: async (id: string) => {
    set({ isDeleting: true, error: null });

    try {
      const response = await axiosInstance.delete(`${API_URL}/${id}`);

      if (response.data.success) {
        // Remove from local state
        const { results, currentResult, pagination } = get();
        
        const updatedResults = results.filter((r) => r._id !== id);
        const updatedCurrent = currentResult?._id === id ? null : currentResult;

        set({
          results: updatedResults,
          currentResult: updatedCurrent,
          pagination: {
            ...pagination,
            total: Math.max(0, pagination.total - 1),
          },
          isDeleting: false,
        });

        toast.success("Research result deleted");
        return true;
      } else {
        throw new Error(response.data.message || "Failed to delete");
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || "Failed to delete result";
      set({ error: errorMessage, isDeleting: false });
      toast.error(errorMessage);
      return false;
    }
  },

  // Set current result
  setCurrentResult: (result: ResearchResult | null) => {
    set({ currentResult: result });
  },

  // Clear error
  clearError: () => {
    set({ error: null });
  },
}));
