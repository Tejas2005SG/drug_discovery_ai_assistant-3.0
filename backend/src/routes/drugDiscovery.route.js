import express from "express";
import { startDrugDiscovery, getResearchHistory } from "../controller/drugDiscovery.controller.js";
import { protectRoute } from "../middleware/protectRoute.js";

const router = express.Router();

// Start drug discovery research (SSE endpoint)
router.post("/research", protectRoute, startDrugDiscovery);

// Get research history
router.get("/history", protectRoute, getResearchHistory);

export default router;
