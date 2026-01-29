import { tavily } from "@tavily/core";
import dotenv from "dotenv";

dotenv.config();

const apiKey = process.env.TAVILY_API_KEY;
if (!apiKey) {
    console.warn("TAVILY_API_KEY is missing!");
}

export const tvly = tavily({ apiKey });

/**
 * Database-specific search configurations
 */
const DATABASE_CONFIGS = {
    pubmed: {
        siteSuffix: "site:pubmed.ncbi.nlm.nih.gov OR site:ncbi.nlm.nih.gov OR site:pmc.ncbi.nlm.nih.gov",
        // Added "review" and "list" to force high-density papers
        keywords: ["comprehensive review", "list of targets", "interactome", "pathogenesis"]
    },
    uniprot: {
        siteSuffix: "site:uniprot.org",
        keywords: ["protein", "gene", "interaction", "function"]
    },
    pubchem: {
        siteSuffix: "site:pubchem.ncbi.nlm.nih.gov",
        keywords: ["bioactivity", "target", "compound", "SMILES"]
    },
    drugbank: {
        siteSuffix: "site:drugbank.com OR site:go.drugbank.com",
        keywords: ["targets", "pharmacology", "mechanism"]
    },
    chembl: {
        siteSuffix: "site:ebi.ac.uk/chembl",
        keywords: ["target profile", "bioactivity", "assay"]
    },
    general: {
        siteSuffix: "",
        keywords: ["molecular mechanism", "therapeutic targets", "review"]
    }
};

export const searchMedicalDatabase = async (query, database = "general", maxResults = 5) => {
    try {
        const config = DATABASE_CONFIGS[database] || DATABASE_CONFIGS.general;
        const enhancedQuery = config.siteSuffix
            ? `${query} ${config.siteSuffix}`.substring(0, 400)
            : query.substring(0, 400);

        console.log(`Tavily ${database} search: ${enhancedQuery.substring(0, 80)}...`);

        const result = await tvly.search(enhancedQuery, {
            searchDepth: "advanced",
            maxResults: maxResults, // Allow higher limit passed from caller
            includeAnswer: true,
            includeRawContent: true
        });

        const sources = result.results || [];
        return sources.map(source => ({
            ...source,
            database: database,
            searchQuery: query
        }));
    } catch (error) {
        console.error(`Tavily ${database} search error:`, error.message);
        return [];
    }
};

/**
 * UPDATED: Aggressive search for maximum target yield
 */
export const searchAllMedicalSources = async (symptomQuery, researchPlan = null) => {
    const allResults = [];

    // Use plan queries if available, otherwise generate aggressive default ones
    const queries = researchPlan?.flatQueries || generateHighYieldQueries(symptomQuery);

    console.log(`\nStarting aggressive search with ${queries.length} queries...\n`);

    // 1. Database Specific Searches (Increased Count)
    const databaseSearches = [
        // PubMed: Look for Reviews (best source of lists)
        { db: "pubmed", query: `comprehensive review ${symptomQuery} molecular targets` },
        { db: "pubmed", query: `list of proteins associated with ${symptomQuery}` },

        // UniProt/PubChem
        { db: "uniprot", query: `${symptomQuery} associated proteins` },
        { db: "pubchem", query: `${symptomQuery} bioassay targets` },

        // Drug/Trial Data
        { db: "drugbank", query: `${symptomQuery} drug targets` },
        { db: "chembl", query: `${symptomQuery} target profile` }
    ];

    // Execute targeted searches (Increased maxResults to 6)
    for (const search of databaseSearches) {
        try {
            const results = await searchMedicalDatabase(search.query, search.db, 6);
            allResults.push(...results);
            await delay(400);
        } catch (error) {
            console.warn(`${search.db} search failed:`, error.message);
        }
    }

    // 2. Execute Research Plan Queries (General)
    // Take up to 7 queries from the AI plan
    for (const query of queries.slice(0, 7)) {
        try {
            // "General" search but looking for lists
            const listQuery = query.includes("list") ? query : `${query} list table`;
            const results = await searchMedicalDatabase(listQuery, "general", 5);
            allResults.push(...results);
            await delay(400);
        } catch (error) {
            console.warn(`Query search failed:`, error.message);
        }
    }

    const uniqueResults = deduplicateResults(allResults);
    console.log(`\nTotal unique sources found: ${uniqueResults.length}\n`);

    return uniqueResults;
};

function generateHighYieldQueries(symptoms) {
    return [
        `comprehensive list of protein targets ${symptoms}`,
        `review of molecular mechanisms ${symptoms}`,
        `all FDA approved drugs for ${symptoms}`,
        `investigational compounds ${symptoms}`,
        `genomic analysis ${symptoms} targets`,
        `pathway analysis ${symptoms} KEGG`
    ];
}

function deduplicateResults(results) {
    const seen = new Set();
    return results.filter(result => {
        if (seen.has(result.url)) return false;
        seen.add(result.url);
        return true;
    });
}

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const crawlSource = async (source, options = {}) => {
    const { url, title, rawContent, database } = source;
    // Increased max extraction length to capture long tables
    const maxContentLength = options.maxContentLength || 40000;

    // Priority: Raw Content
    if (rawContent && rawContent.length > 800) {
        console.log(`Using raw content for: ${url.substring(0, 60)}...`);
        return {
            url,
            title,
            content: cleanContent(rawContent.substring(0, maxContentLength)),
            success: true,
            source: "rawContent",
            database: database || "unknown",
            contentLength: rawContent.length
        };
    }

    // Skip junk
    const skipPatterns = ['.pdf', '/login', 'javascript:', 'doubleclick'];
    if (skipPatterns.some(pattern => url.toLowerCase().includes(pattern))) {
        return createSnippetFallback(source, "Skipped URL");
    }

    try {
        console.log(`Crawling: ${url.substring(0, 60)}...`);
        const result = await tvly.extract([url]);

        const extractedData = result.results?.[0] || result.data?.[0];
        const crawledContent = extractedData?.rawContent || extractedData?.content || "";

        if (!crawledContent || crawledContent.length < 200) {
            // Fallback to snippet if crawl fails or is too short
            return createSnippetFallback(source, "Content too short");
        }

        const cleanedContent = cleanContent(crawledContent);

        return {
            url,
            title: extractedData?.title || title,
            content: cleanedContent.substring(0, maxContentLength),
            success: true,
            source: "crawl",
            database: database || "unknown",
            contentLength: cleanedContent.length
        };
    } catch (error) {
        return createSnippetFallback(source, error.message);
    }
};

function createSnippetFallback(source, errorMessage) {
    const { url, title, content: searchSnippet, database } = source;
    if (searchSnippet && searchSnippet.length > 50) {
        return {
            url,
            title,
            content: `[Snippet Only]\n${searchSnippet}`,
            success: true,
            source: "snippet",
            database: database || "unknown",
            crawlError: errorMessage,
            contentLength: searchSnippet.length
        };
    }
    return { url, title, content: "", success: false, error: errorMessage, source: "failed", database: database || "unknown" };
}

function cleanContent(content) {
    if (!content) return "";
    return content
        .replace(/\s+/g, ' ')
        .replace(/cookie[s]?\s*policy/gi, '')
        .trim();
}

export const batchCrawl = async (sources, options = {}) => {
    const { concurrency = 4, delayBetweenBatches = 800, onProgress } = options;
    const results = [];
    const batches = chunkArray(sources, concurrency);

    for (let i = 0; i < batches.length; i++) {
        if (onProgress) {
            onProgress({
                stage: "crawling",
                message: `Crawling batch ${i + 1}/${batches.length}`,
                progress: Math.round((i / batches.length) * 100)
            });
        }
        const batchResults = await Promise.all(batches[i].map(s => crawlSource(s, options)));
        results.push(...batchResults);
        if (i < batches.length - 1) await delay(delayBetweenBatches);
    }
    return results;
};

function chunkArray(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) chunks.push(array.slice(i, i + size));
    return chunks;
}

export default { tvly, searchAllMedicalSources, crawlSource, batchCrawl };