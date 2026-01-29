import {
    searchMedicalDatabase,
    searchAllMedicalSources,
    crawlSource,
    batchCrawl
} from "../lib/tavily.js";
import {
    synthesizeMolecularDossier,
    generateResearchPlan
} from "../lib/gemini.js";
import { saveResearchResult } from "./researchResult.controller.js";

/**
 * Send Server-Sent Event
 */
const sendSSE = (res, data) => {
    try {
        res.write(`data: ${JSON.stringify(data)}\n\n`);
    } catch (e) {
        console.error("SSE send error:", e.message);
    }
};

/**
 * Parse symptoms from structured or unstructured input
 */
const parseSymptoms = (input) => {
    // Handle structured format: "given symptoms {symptom1, symptom2}"
    const match = input.match(/given symptoms\s*\{([^}]+)\}/i);
    if (match) {
        return {
            raw: input,
            extracted: match[1].trim(),
            isStructured: true
        };
    }

    // Handle list format: "symptoms: a, b, c"
    const listMatch = input.match(/symptoms?\s*[:=]\s*(.+)/i);
    if (listMatch) {
        return {
            raw: input,
            extracted: listMatch[1].trim(),
            isStructured: true
        };
    }

    return { raw: input, extracted: input.trim(), isStructured: false };
};

/**
 * Detect database sources from URL or query
 */
const detectSources = (urlOrQuery) => {
    const sources = [];
    const text = urlOrQuery.toLowerCase();

    const dbPatterns = {
        'pubmed': ['pubmed', 'ncbi.nlm.nih.gov/pubmed'],
        'pmc': ['pmc', 'ncbi.nlm.nih.gov/pmc'],
        'uniprot': ['uniprot.org'],
        'pubchem': ['pubchem.ncbi.nlm.nih.gov'],
        'drugbank': ['drugbank.com', 'go.drugbank'],
        'chembl': ['ebi.ac.uk/chembl', 'chembl'],
        'kegg': ['kegg.jp', 'genome.jp/kegg'],
        'reactome': ['reactome.org'],
        'omim': ['omim.org'],
        'orphanet': ['orpha.net'],
        'clinicaltrials': ['clinicaltrials.gov'],
        'fda': ['fda.gov'],
        'ema': ['ema.europa.eu'],
        'mesh': ['mesh', 'nlm.nih.gov/mesh']
    };

    for (const [db, patterns] of Object.entries(dbPatterns)) {
        if (patterns.some(p => text.includes(p))) {
            sources.push(db);
        }
    }

    return sources.length > 0 ? sources : ['web'];
};

/**
 * Categorize a source by its URL
 */
const categorizeSource = (url) => {
    const urlLower = url.toLowerCase();

    if (urlLower.includes('pubmed') || urlLower.includes('ncbi')) return 'clinical';
    if (urlLower.includes('uniprot')) return 'protein';
    if (urlLower.includes('pubchem') || urlLower.includes('drugbank') || urlLower.includes('chembl')) return 'compound';
    if (urlLower.includes('kegg') || urlLower.includes('reactome')) return 'pathway';
    if (urlLower.includes('clinicaltrials')) return 'trials';

    return 'general';
};

/**
 * Create progress update object
 */
const createProgress = (id, stage, message, status, extras = {}) => ({
    type: "progress",
    id,
    stage,
    message,
    status,
    timestamp: Date.now(),
    ...extras
});

/**
 * Main drug discovery endpoint with comprehensive research pipeline
 */
export const startDrugDiscovery = async (req, res) => {
    const { symptoms: inputQuery, options = {} } = req.body;

    // Validation
    if (!inputQuery || inputQuery.trim() === "") {
        return res.status(400).json({
            success: false,
            message: "Research query is required"
        });
    }

    // Setup SSE headers
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.setHeader("X-Accel-Buffering", "no"); // Disable nginx buffering

    const startTime = Date.now();
    const { extracted: symptoms, isStructured } = parseSymptoms(inputQuery);

    // Research state
    const state = {
        searchResults: [],
        crawledData: [],
        seenUrls: new Set(),
        errors: [],
        stats: {
            queriesExecuted: 0,
            sourcesFound: 0,
            sourcesCrawled: 0,
            sourcesUsed: 0
        }
    };

    try {
        // ═══════════════════════════════════════════════════════════════
        // PHASE 1: RESEARCH PLANNING
        // ═══════════════════════════════════════════════════════════════

        sendSSE(res, createProgress(
            "phase-planning",
            "planning",
            "Analyzing symptoms and generating research strategy...",
            "running"
        ));

        const researchPlan = await generateResearchPlan(symptoms);

        // Extract queries (handle both old and new format)
        const queries = researchPlan.flatQueries ||
            researchPlan.queries ||
            generateFallbackQueries(symptoms);

        const steps = researchPlan.steps || [];

        sendSSE(res, createProgress(
            "phase-planning",
            "planning",
            `${researchPlan.plan || 'Research plan generated'}`,
            "completed",
            {
                duration: ((Date.now() - startTime) / 1000).toFixed(1),
                data: {
                    hypotheses: researchPlan.hypotheses,
                    queryCount: queries.length,
                    targetDatabases: researchPlan.targetDatabases
                }
            }
        ));

        // Send individual step previews
        if (steps.length > 0) {
            sendSSE(res, {
                type: "plan",
                steps: steps.map((s, i) => ({
                    id: `planned-step-${i}`,
                    stage: s.stage,
                    message: s.message,
                    status: "pending"
                })),
                timestamp: Date.now()
            });
        }

        await delay(300);

        // ═══════════════════════════════════════════════════════════════
        // PHASE 2: MULTI-DATABASE SEARCH
        // ═══════════════════════════════════════════════════════════════

        const searchPhaseStart = Date.now();

        sendSSE(res, createProgress(
            "phase-search",
            "searching",
            "Initiating comprehensive database search...",
            "running"
        ));

        // Execute targeted database searches
        const databaseSearches = [
            { db: "pubmed", query: `${symptoms} pathophysiology mechanism treatment`, priority: 1 },
            { db: "pubmed", query: `${symptoms} molecular target drug`, priority: 1 },
            { db: "uniprot", query: `${symptoms} protein human`, priority: 2 },
            { db: "pubchem", query: `${symptoms} compound drug`, priority: 2 },
            { db: "drugbank", query: `${symptoms} approved medication`, priority: 2 },
            { db: "clinicaltrials", query: `${symptoms} clinical trial`, priority: 3 },
            { db: "kegg", query: `${symptoms} pathway`, priority: 3 }
        ];

        // Add research plan queries
        for (const query of queries.slice(0, 5)) {
            databaseSearches.push({ db: "general", query, priority: 2 });
        }

        // Sort by priority and execute
        databaseSearches.sort((a, b) => a.priority - b.priority);

        for (let i = 0; i < databaseSearches.length; i++) {
            const { db, query } = databaseSearches[i];

            sendSSE(res, createProgress(
                `search-${i}`,
                "searching",
                `${query.substring(0, 60)}...`,
                "running",
                { sourceName: db.toUpperCase(), progress: Math.round((i / databaseSearches.length) * 100) }
            ));

            try {
                const results = await searchMedicalDatabase(query, db, 3);

                let newCount = 0;
                for (const result of results) {
                    if (!state.seenUrls.has(result.url)) {
                        state.seenUrls.add(result.url);
                        state.searchResults.push({
                            ...result,
                            category: categorizeSource(result.url),
                            searchQuery: query,
                            database: db
                        });
                        newCount++;
                    }
                }

                state.stats.queriesExecuted++;

                sendSSE(res, createProgress(
                    `search-${i}`,
                    "searching",
                    `Found ${results.length} results (${newCount} new)`,
                    "completed",
                    {
                        sourceName: db.toUpperCase(),
                        queries: [{
                            query: query,
                            sources: [db],
                            resultCount: results.length,
                            newResults: newCount
                        }]
                    }
                ));

            } catch (error) {
                console.error(`Search error for ${db}:`, error.message);
                state.errors.push({ phase: "search", db, query, error: error.message });

                sendSSE(res, createProgress(
                    `search-${i}`,
                    "searching",
                    `Search failed: ${error.message.substring(0, 50)}`,
                    "warning",
                    { sourceName: db.toUpperCase() }
                ));
            }

            // Rate limiting
            await delay(400);
        }

        state.stats.sourcesFound = state.searchResults.length;

        sendSSE(res, createProgress(
            "phase-search",
            "searching",
            `Search complete: ${state.searchResults.length} unique sources from ${state.stats.queriesExecuted} queries`,
            "completed",
            {
                duration: ((Date.now() - searchPhaseStart) / 1000).toFixed(1),
                data: {
                    totalSources: state.searchResults.length,
                    byCategory: countByCategory(state.searchResults)
                }
            }
        ));

        // Check if we have sources
        if (state.searchResults.length === 0) {
            throw new Error("No sources found. Please try different symptoms or broader terms.");
        }

        await delay(300);

        // ═══════════════════════════════════════════════════════════════
        // PHASE 3: CONTENT EXTRACTION (CRAWLING)
        // ═══════════════════════════════════════════════════════════════

        const crawlPhaseStart = Date.now();

        sendSSE(res, createProgress(
            "phase-crawl",
            "crawling",
            "Extracting detailed content from sources...",
            "running"
        ));

        // Prioritize sources by category
        const prioritizedSources = prioritizeSources(state.searchResults);
        const sourcesToCrawl = prioritizedSources.slice(0, 12); // Limit to top 12

        sendSSE(res, createProgress(
            "phase-crawl",
            "crawling",
            `Processing ${sourcesToCrawl.length} priority sources...`,
            "running"
        ));

        // Batch crawl with progress updates
        const crawlResults = await batchCrawl(sourcesToCrawl, {
            concurrency: 3,
            delayBetweenBatches: 800,
            maxContentLength: 10000,
            onProgress: (update) => {
                sendSSE(res, createProgress(
                    "crawl-progress",
                    "crawling",
                    update.message,
                    "running",
                    { progress: update.progress }
                ));
            }
        });

        // Process crawl results
        for (const result of crawlResults) {
            if (result.success && result.content && result.content.length > 50) {
                state.crawledData.push(result);
            }
        }

        state.stats.sourcesCrawled = state.crawledData.length;

        // Category breakdown
        const crawlBreakdown = {
            clinical: state.crawledData.filter(d => d.database === 'pubmed' || categorizeSource(d.url) === 'clinical').length,
            protein: state.crawledData.filter(d => d.database === 'uniprot' || categorizeSource(d.url) === 'protein').length,
            compound: state.crawledData.filter(d => ['pubchem', 'drugbank', 'chembl'].includes(d.database) || categorizeSource(d.url) === 'compound').length,
            pathway: state.crawledData.filter(d => d.database === 'kegg' || categorizeSource(d.url) === 'pathway').length,
            general: state.crawledData.filter(d => categorizeSource(d.url) === 'general').length
        };

        // Mark the individual crawl progress as complete too
        sendSSE(res, createProgress(
            "crawl-progress",
            "crawling",
            "Extraction sequence finished",
            "completed",
            { progress: 100 }
        ));

        sendSSE(res, createProgress(
            "phase-crawl",
            "crawling",
            `Content extracted: ${state.crawledData.length}/${sourcesToCrawl.length} sources successful`,
            "completed",
            {
                duration: ((Date.now() - crawlPhaseStart) / 1000).toFixed(1),
                data: {
                    successful: state.crawledData.length,
                    failed: sourcesToCrawl.length - state.crawledData.length,
                    breakdown: crawlBreakdown
                }
            }
        ));

        await delay(300);

        // ═══════════════════════════════════════════════════════════════
        // PHASE 4: FALLBACK DATA PREPARATION
        // ═══════════════════════════════════════════════════════════════

        // Prepare data for LLM synthesis
        let dataForSynthesis = [...state.crawledData];

        // If crawling didn't get enough data, use search snippets as fallback
        if (dataForSynthesis.length < 3) {
            sendSSE(res, createProgress(
                "fallback",
                "thinking",
                "Augmenting with search snippets for comprehensive analysis...",
                "running"
            ));

            const snippetSources = state.searchResults
                .filter(r => r.content || r.snippet)
                .filter(r => !state.crawledData.some(c => c.url === r.url))
                .slice(0, 10 - dataForSynthesis.length);

            for (const source of snippetSources) {
                dataForSynthesis.push({
                    url: source.url,
                    title: source.title,
                    content: `[Search Result]\n${source.content || source.snippet}`,
                    success: true,
                    source: "snippet",
                    database: source.database || "search",
                    category: source.category
                });
            }

            sendSSE(res, createProgress(
                "fallback",
                "thinking",
                `Added ${snippetSources.length} search snippets`,
                "completed"
            ));
        }

        // Final validation
        if (dataForSynthesis.length === 0) {
            throw new Error("Unable to extract content from any sources. Please try different symptoms.");
        }

        state.stats.sourcesUsed = dataForSynthesis.length;

        await delay(300);

        // ═══════════════════════════════════════════════════════════════
        // PHASE 5: AI SYNTHESIS
        // ═══════════════════════════════════════════════════════════════

        const synthesisStart = Date.now();

        sendSSE(res, createProgress(
            "phase-synthesis",
            "generating",
            "Initiating AI synthesis of Molecular Dossier...",
            "running",
            {
                data: {
                    sourcesBeingAnalyzed: dataForSynthesis.length,
                    estimatedTime: "2-4 minutes"
                }
            }
        ));

        let lastThoughtUpdate = Date.now();
        let thoughtCount = 0;

        const synthesisResult = await synthesizeMolecularDossier(
            symptoms,
            dataForSynthesis,
            (update) => {
                // Throttle thought updates to prevent overwhelming the client
                const now = Date.now();
                if (update.stage === "thinking" && now - lastThoughtUpdate > 500) {
                    lastThoughtUpdate = now;
                    thoughtCount++;

                    sendSSE(res, createProgress(
                        `thought-${thoughtCount}`,
                        "thinking",
                        `${update.message}`,
                        "running",
                        { progress: update.progress }
                    ));
                } else if (update.stage === "writing") {
                    sendSSE(res, createProgress(
                        "writing-progress",
                        "generating",
                        `${update.message}`,
                        "running",
                        { progress: update.progress }
                    ));
                }
            }
        );

        const synthesisDuration = ((Date.now() - synthesisStart) / 1000).toFixed(1);

        // Mark the writing progress as complete too
        sendSSE(res, createProgress(
            "writing-progress",
            "generating",
            "Dossier generation finalized",
            "completed",
            { progress: 100 }
        ));

        sendSSE(res, createProgress(
            "phase-synthesis",
            "generating",
            `Molecular Dossier synthesis complete (${synthesisDuration}s)`,
            "completed",
            {
                duration: synthesisDuration,
                data: {
                    contentLength: synthesisResult.content?.length || 0,
                    sourcesAnalyzed: synthesisResult.sourcesUsed
                }
            }
        ));

        await delay(200);

        // ═══════════════════════════════════════════════════════════════
        // PHASE 6: COMPLETION
        // ═══════════════════════════════════════════════════════════════

        const totalDuration = ((Date.now() - startTime) / 1000).toFixed(1);

        // Prepare the complete result data
        const completeResultData = {
            content: synthesisResult.content,
            sources: dataForSynthesis.map(d => ({
                title: d.title || "Untitled",
                url: d.url,
                category: d.category || categorizeSource(d.url),
                database: d.database || "unknown",
                contentLength: d.content?.length || 0,
                status: d.source || "crawl"
            })),
            symptoms: inputQuery,
            extractedSymptoms: symptoms,
            mode: "comprehensive-research",
            researchPlan: {
                strategy: researchPlan.plan,
                hypotheses: researchPlan.hypotheses,
                targetDatabases: researchPlan.targetDatabases
            },
            metadata: {
                totalDuration: `${totalDuration}s`,
                queriesExecuted: state.stats.queriesExecuted,
                sourcesFound: state.stats.sourcesFound,
                sourcesCrawled: state.stats.sourcesCrawled,
                sourcesUsed: state.stats.sourcesUsed,
                sourceBreakdown: synthesisResult.sourceBreakdown,
                modelUsed: synthesisResult.modelUsed,
                timestamp: new Date().toISOString(),
                errors: state.errors.length > 0 ? state.errors.map(e => e.message || e.toString()) : undefined
            }
        };

        // Save to database (async, don't block response)
        const userId = req.user._id;
        saveResearchResult(userId, completeResultData).then(saveResult => {
            if (saveResult.success) {
                console.log(`✅ Research result saved to database: ${saveResult.data._id}`);
            } else {
                console.error("❌ Failed to save research result:", saveResult.error);
            }
        }).catch(err => {
            console.error("❌ Error in saveResearchResult:", err);
        });

        // Send completion event
        sendSSE(res, {
            type: "complete",
            data: completeResultData,
            timestamp: Date.now()
        });

        res.end();

    } catch (error) {
        console.error("Pipeline Error:", error);

        sendSSE(res, {
            type: "error",
            error: {
                message: error.message || "Research pipeline failed",
                phase: error.phase || "unknown",
                recoverable: error.recoverable || false
            },
            partialData: state.searchResults.length > 0 ? {
                sourcesFound: state.searchResults.length,
                sourcesCrawled: state.crawledData.length
            } : null,
            timestamp: Date.now()
        });

        res.end();
    }
};

/**
 * Generate fallback queries if AI fails
 */
function generateFallbackQueries(symptoms) {
    const base = symptoms.toLowerCase().trim();
    return [
        `${base} pathophysiology molecular mechanism`,
        `${base} drug target protein receptor`,
        `${base} treatment therapy medication`,
        `${base} biomarker diagnosis`,
        `${base} clinical trial results`,
        `${base} FDA approved drugs`
    ];
}

/**
 * Count sources by category
 */
function countByCategory(sources) {
    const counts = {};
    for (const source of sources) {
        const cat = source.category || 'general';
        counts[cat] = (counts[cat] || 0) + 1;
    }
    return counts;
}

/**
 * Prioritize sources for crawling
 */
function prioritizeSources(sources) {
    const priority = {
        clinical: 1,
        protein: 2,
        compound: 3,
        pathway: 4,
        trials: 5,
        general: 6
    };

    return [...sources].sort((a, b) => {
        const catA = a.category || 'general';
        const catB = b.category || 'general';
        return (priority[catA] || 10) - (priority[catB] || 10);
    });
}

/**
 * Delay helper
 */
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Get research history (placeholder for future implementation)
 */
export const getResearchHistory = async (req, res) => {
    try {
        // TODO: Implement with database
        res.json({
            success: true,
            history: [],
            message: "History feature coming soon"
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
};

/**
 * Health check endpoint
 */
export const healthCheck = async (req, res) => {
    res.json({
        status: "healthy",
        service: "drug-discovery",
        timestamp: new Date().toISOString(),
        version: "2.0.0"
    });
};

export default {
    startDrugDiscovery,
    getResearchHistory,
    healthCheck
};