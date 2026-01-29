import dotenv from "dotenv";
dotenv.config();

import express from "express";
import cookieParser from "cookie-parser";
import cors from "cors";

import { connectDB } from "./lib/db.js";

import authRoutes from "./routes/auth.route.js";
import drugDiscoveryRoutes from "./routes/drugDiscovery.route.js";
import researchResultRoutes from "./routes/researchResult.route.js";

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use(cookieParser());
app.use(cors({
    origin: "http://localhost:5173", // Allow frontend
    credentials: true
}));

app.use("/api/auth", authRoutes);
app.use("/api/drug-discovery", drugDiscoveryRoutes);
app.use("/api/research-results", researchResultRoutes);

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
    connectDB();
});
