import ResearchResult from "../models/ResearchResult.js";

/**
 * Save a new research result to the database
 * Called after successful drug discovery completion
 */
export const saveResearchResult = async (userId, researchData) => {
    try {
        const {
            content,
            sources,
            symptoms,
            extractedSymptoms,
            mode,
            researchPlan,
            metadata,
        } = researchData;

        // Flatten the nested structures for optimal storage
        const researchResult = new ResearchResult({
            userId,
            symptoms,
            extractedSymptoms,
            mode: mode || "comprehensive-research",
            content,
            sources: sources.map((source) => ({
                title: source.title || "Untitled",
                url: source.url,
                category: source.category || "general",
                database: source.database || "unknown",
                contentLength: source.contentLength || 0,
                status: source.status || "search",
            })),

            // Flatten research plan
            researchPlanStrategy: researchPlan?.strategy || "",
            researchPlanHypotheses: researchPlan?.hypotheses || [],
            researchPlanTargetDatabases: researchPlan?.targetDatabases || [],

            // Flatten metadata
            metadataTotalDuration: metadata?.totalDuration || "",
            metadataQueriesExecuted: metadata?.queriesExecuted || 0,
            metadataSourcesFound: metadata?.sourcesFound || 0,
            metadataSourcesCrawled: metadata?.sourcesCrawled || 0,
            metadataSourcesUsed: metadata?.sourcesUsed || 0,
            metadataSourceBreakdownClinical: metadata?.sourceBreakdown?.clinical || 0,
            metadataSourceBreakdownProtein: metadata?.sourceBreakdown?.protein || 0,
            metadataSourceBreakdownCompound: metadata?.sourceBreakdown?.compound || 0,
            metadataSourceBreakdownPathway: metadata?.sourceBreakdown?.pathway || 0,
            metadataSourceBreakdownTrials: metadata?.sourceBreakdown?.trials || 0,
            metadataSourceBreakdownGeneral: metadata?.sourceBreakdown?.general || 0,
            metadataModelUsed: metadata?.modelUsed || "",
            metadataTimestamp: metadata?.timestamp
                ? new Date(metadata.timestamp)
                : new Date(),
            metadataErrors: metadata?.errors || [],

            // Search stats
            searchStats: {
                queriesExecuted: metadata?.queriesExecuted || 0,
                sourcesFound: metadata?.sourcesFound || 0,
                sourcesCrawled: metadata?.sourcesCrawled || 0,
                sourcesUsed: metadata?.sourcesUsed || 0,
            },
        });

        const savedResult = await researchResult.save();
        return {
            success: true,
            data: savedResult,
            message: "Research result saved successfully",
        };
    } catch (error) {
        console.error("Error saving research result:", error);
        return {
            success: false,
            error: error.message,
            message: "Failed to save research result",
        };
    }
};

/**
 * Get all research results for the authenticated user
 */
export const getUserResearchHistory = async (req, res) => {
    try {
        const userId = req.user._id;
        const { page = 1, limit = 20, search, tag } = req.query;

        const skip = (parseInt(page) - 1) * parseInt(limit);
        const limitNum = parseInt(limit);

        let results;
        let total;

        if (search) {
            // Text search
            results = await ResearchResult.searchUserResearch(userId, search, {
                limit: limitNum,
                skip,
            });
            total = await ResearchResult.countDocuments({
                userId,
                isDeleted: false,
                $text: { $search: search },
            });
        } else if (tag) {
            // Tag filter
            results = await ResearchResult.find({
                userId,
                isDeleted: false,
                tags: tag,
            })
                .sort({ createdAt: -1 })
                .skip(skip)
                .limit(limitNum)
                .lean();
            total = await ResearchResult.countDocuments({
                userId,
                isDeleted: false,
                tags: tag,
            });
        } else {
            // Default: get all
            results = await ResearchResult.getUserHistory(userId, {
                limit: limitNum,
                skip,
            });
            total = await ResearchResult.countDocuments({
                userId,
                isDeleted: false,
            });
        }

        // Transform results to match frontend expectations
        const transformedResults = results.map((result) => ({
            _id: result._id,
            symptoms: result.symptoms,
            extractedSymptoms: result.extractedSymptoms,
            mode: result.mode,
            content: result.content,
            sources: result.sources,
            researchPlan: {
                strategy: result.researchPlanStrategy,
                hypotheses: result.researchPlanHypotheses,
                targetDatabases: result.researchPlanTargetDatabases,
            },
            metadata: {
                totalDuration: result.metadataTotalDuration,
                queriesExecuted: result.metadataQueriesExecuted,
                sourcesFound: result.metadataSourcesFound,
                sourcesCrawled: result.metadataSourcesCrawled,
                sourcesUsed: result.metadataSourcesUsed,
                sourceBreakdown: {
                    clinical: result.metadataSourceBreakdownClinical,
                    protein: result.metadataSourceBreakdownProtein,
                    compound: result.metadataSourceBreakdownCompound,
                    pathway: result.metadataSourceBreakdownPathway,
                    trials: result.metadataSourceBreakdownTrials,
                    general: result.metadataSourceBreakdownGeneral,
                },
                modelUsed: result.metadataModelUsed,
                timestamp: result.metadataTimestamp,
                errors: result.metadataErrors,
            },
            tags: result.tags,
            isStarred: result.isStarred,
            createdAt: result.createdAt,
            updatedAt: result.updatedAt,
        }));

        res.json({
            success: true,
            data: transformedResults,
            pagination: {
                page: parseInt(page),
                limit: limitNum,
                total,
                totalPages: Math.ceil(total / limitNum),
            },
        });
    } catch (error) {
        console.error("Error fetching research history:", error);
        res.status(500).json({
            success: false,
            message: error.message || "Failed to fetch research history",
        });
    }
};

/**
 * Get a single research result by ID
 */
export const getResearchResultById = async (req, res) => {
    try {
        const userId = req.user._id;
        const { id } = req.params;

        const result = await ResearchResult.findOne({
            _id: id,
            userId,
            isDeleted: false,
        }).lean();

        if (!result) {
            return res.status(404).json({
                success: false,
                message: "Research result not found",
            });
        }

        // Transform to match frontend expectations
        const transformedResult = {
            _id: result._id,
            symptoms: result.symptoms,
            extractedSymptoms: result.extractedSymptoms,
            mode: result.mode,
            content: result.content,
            sources: result.sources,
            researchPlan: {
                strategy: result.researchPlanStrategy,
                hypotheses: result.researchPlanHypotheses,
                targetDatabases: result.researchPlanTargetDatabases,
            },
            metadata: {
                totalDuration: result.metadataTotalDuration,
                queriesExecuted: result.metadataQueriesExecuted,
                sourcesFound: result.metadataSourcesFound,
                sourcesCrawled: result.metadataSourcesCrawled,
                sourcesUsed: result.metadataSourcesUsed,
                sourceBreakdown: {
                    clinical: result.metadataSourceBreakdownClinical,
                    protein: result.metadataSourceBreakdownProtein,
                    compound: result.metadataSourceBreakdownCompound,
                    pathway: result.metadataSourceBreakdownPathway,
                    trials: result.metadataSourceBreakdownTrials,
                    general: result.metadataSourceBreakdownGeneral,
                },
                modelUsed: result.metadataModelUsed,
                timestamp: result.metadataTimestamp,
                errors: result.metadataErrors,
            },
            tags: result.tags,
            notes: result.notes,
            isStarred: result.isStarred,
            createdAt: result.createdAt,
            updatedAt: result.updatedAt,
        };

        res.json({
            success: true,
            data: transformedResult,
        });
    } catch (error) {
        console.error("Error fetching research result:", error);
        res.status(500).json({
            success: false,
            message: error.message || "Failed to fetch research result",
        });
    }
};

/**
 * Update a research result (notes, tags, starred status)
 */
export const updateResearchResult = async (req, res) => {
    try {
        const userId = req.user._id;
        const { id } = req.params;
        const { notes, tags, isStarred } = req.body;

        const updateData = {};
        if (notes !== undefined) updateData.notes = notes;
        if (tags !== undefined) updateData.tags = tags;
        if (isStarred !== undefined) updateData.isStarred = isStarred;

        const result = await ResearchResult.findOneAndUpdate(
            { _id: id, userId, isDeleted: false },
            updateData,
            { new: true }
        );

        if (!result) {
            return res.status(404).json({
                success: false,
                message: "Research result not found",
            });
        }

        res.json({
            success: true,
            data: result,
            message: "Research result updated successfully",
        });
    } catch (error) {
        console.error("Error updating research result:", error);
        res.status(500).json({
            success: false,
            message: error.message || "Failed to update research result",
        });
    }
};

/**
 * Soft delete a research result
 */
export const deleteResearchResult = async (req, res) => {
    try {
        const userId = req.user._id;
        const { id } = req.params;

        const result = await ResearchResult.findOneAndUpdate(
            { _id: id, userId, isDeleted: false },
            { isDeleted: true },
            { new: true }
        );

        if (!result) {
            return res.status(404).json({
                success: false,
                message: "Research result not found",
            });
        }

        res.json({
            success: true,
            message: "Research result deleted successfully",
        });
    } catch (error) {
        console.error("Error deleting research result:", error);
        res.status(500).json({
            success: false,
            message: error.message || "Failed to delete research result",
        });
    }
};

/**
 * Get research statistics for the user
 */
export const getResearchStats = async (req, res) => {
    try {
        const userId = req.user._id;

        const stats = await ResearchResult.aggregate([
            { $match: { userId: userId.toString(), isDeleted: false } },
            {
                $group: {
                    _id: null,
                    totalResearches: { $sum: 1 },
                    totalSourcesUsed: { $sum: "$metadataSourcesUsed" },
                    avgSourcesPerResearch: { $avg: "$metadataSourcesUsed" },
                    totalQueriesExecuted: { $sum: "$metadataQueriesExecuted" },
                    starredCount: {
                        $sum: { $cond: [{ $eq: ["$isStarred", true] }, 1, 0] },
                    },
                },
            },
        ]);

        const categoryBreakdown = await ResearchResult.aggregate([
            { $match: { userId: userId.toString(), isDeleted: false } },
            {
                $group: {
                    _id: null,
                    clinical: { $sum: "$metadataSourceBreakdownClinical" },
                    protein: { $sum: "$metadataSourceBreakdownProtein" },
                    compound: { $sum: "$metadataSourceBreakdownCompound" },
                    pathway: { $sum: "$metadataSourceBreakdownPathway" },
                    trials: { $sum: "$metadataSourceBreakdownTrials" },
                    general: { $sum: "$metadataSourceBreakdownGeneral" },
                },
            },
        ]);

        const recentActivity = await ResearchResult.find({
            userId,
            isDeleted: false,
        })
            .sort({ createdAt: -1 })
            .limit(5)
            .select("symptoms createdAt metadataSourcesUsed")
            .lean();

        res.json({
            success: true,
            data: {
                overview: stats[0] || {
                    totalResearches: 0,
                    totalSourcesUsed: 0,
                    avgSourcesPerResearch: 0,
                    totalQueriesExecuted: 0,
                    starredCount: 0,
                },
                categoryBreakdown: categoryBreakdown[0] || {
                    clinical: 0,
                    protein: 0,
                    compound: 0,
                    pathway: 0,
                    trials: 0,
                    general: 0,
                },
                recentActivity,
            },
        });
    } catch (error) {
        console.error("Error fetching research stats:", error);
        res.status(500).json({
            success: false,
            message: error.message || "Failed to fetch research statistics",
        });
    }
};

/**
 * Get all unique tags for the user
 */
export const getUserTags = async (req, res) => {
    try {
        const userId = req.user._id;

        const tags = await ResearchResult.distinct("tags", {
            userId,
            isDeleted: false,
        });

        res.json({
            success: true,
            data: tags,
        });
    } catch (error) {
        console.error("Error fetching user tags:", error);
        res.status(500).json({
            success: false,
            message: error.message || "Failed to fetch tags",
        });
    }
};

export default {
    saveResearchResult,
    getUserResearchHistory,
    getResearchResultById,
    updateResearchResult,
    deleteResearchResult,
    getResearchStats,
    getUserTags,
};
