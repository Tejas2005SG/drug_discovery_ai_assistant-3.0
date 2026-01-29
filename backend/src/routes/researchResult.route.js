import express from "express";
import {
    getUserResearchHistory,
    getResearchResultById,
    updateResearchResult,
    deleteResearchResult,
    getResearchStats,
    getUserTags,
} from "../controller/researchResult.controller.js";
import { protectRoute } from "../middleware/protectRoute.js";

const router = express.Router();

// Get all research results for the authenticated user
router.get("/", protectRoute, getUserResearchHistory);

// Get research statistics
router.get("/stats", protectRoute, getResearchStats);

// Get all unique tags
router.get("/tags", protectRoute, getUserTags);

// Get a single research result by ID
router.get("/:id", protectRoute, getResearchResultById);

// Update a research result
router.patch("/:id", protectRoute, updateResearchResult);

// Delete a research result (soft delete)
router.delete("/:id", protectRoute, deleteResearchResult);

export default router;
