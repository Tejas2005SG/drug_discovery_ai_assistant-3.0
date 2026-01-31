import { GoogleGenAI } from "@google/genai";

const key = process.env.GEMINI_API_KEY;
if (key) {
    console.log(`Gemini API Key loaded: ${key.substring(0, 8)}...`);
} else {
    console.warn("GEMINI_API_KEY is missing in environment variables!");
}

export const ai = new GoogleGenAI({ apiKey: key });

// Using Flash for the Selection Algorithm (speed), Pro for Writing (quality)
const MODEL_NAME = process.env.GEMINI_MODEL || "gemini-1.5-pro-latest";

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function withRetry(fn, maxRetries = 5) {
    let lastError;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            if (error.status === 429 && attempt < maxRetries - 1) {
                await delay(2000 * Math.pow(2, attempt));
                continue;
            }
            throw error;
        }
    }
    throw lastError;
}

// ... (Keep generateResearchPlan as is from your previous code) ...
export const generateResearchPlan = async (symptoms) => {
    // [Use the exact code from your previous message for this function]
    // For brevity, I am assuming the previous implementation remains here.
    try {
        const response = await ai.models.generateContent({
            model: MODEL_NAME,
            contents: [{
                role: 'user',
                parts: [{
                    text: `You are a senior bioinformatics researcher. Analyze these symptoms: "${symptoms}"
Generate a HIGH-VOLUME data mining strategy.
Respond ONLY with a JSON object... (rest of your prompt)`
                }]
            }],
            generationConfig: { responseMimeType: "application/json" }
        });
        let text = response.candidates[0].content.parts[0].text;
        text = text.replace(/```json\n?|```/g, '').trim();
        const parsed = JSON.parse(text);
        const allQueries = [
            ...(parsed.queries?.clinical || []),
            ...(parsed.queries?.protein || []),
            ...(parsed.queries?.compound || []),
            ...(parsed.queries?.pharmacology || []),
            ...(parsed.queries?.pathway || [])
        ];
        return { ...parsed, flatQueries: allQueries };
    } catch (e) {
        return { flatQueries: [`comprehensive molecular analysis ${symptoms}`] }; // Fallback
    }
};

/**
 * ---------------------------------------------------------
 * NEW: THE SELECTION ALGORITHM
 * ---------------------------------------------------------
 * Analyzes sources to scientifically rank targets before writing.
 */
async function runSelectionAlgorithm(symptoms, categorizedSources, onProgress) {
    if (onProgress) onProgress({ stage: "thinking", message: "Running target scoring algorithm...", status: "running" });

    // Summarize sources for the selection brain (to save context)
    const contextSummary = Object.entries(categorizedSources)
        .map(([cat, sources]) => {
            return sources.slice(0, 8).map(s => `[${cat}] ${s.title}: ${s.content.substring(0, 400)}...`).join('\n');
        }).join('\n');

    const selectionPrompt = `
    You are a Bioinformatics Ranking Algorithm. 
    Analyze the provided research snippets for symptoms: "${symptoms}".

    TASK 1: SCORE PROTEIN TARGETS (Select Top 5)
    Score (0-10) based on:
    - Pathogenicity (Is it a driver?)
    - Druggability (Are there ligands?)
    
    TASK 2: RANK THERAPEUTIC LIGANDS (Select Top 5)
    Rank based on:
    - Clinical Status (FDA Approved > Phase III > Pre-clinical)
    - Target Validation (Must hit one of the top targets)
    - Data Quality (SMILES available?)

    Return JSON ONLY:
    {
        "priorityTargets": [
            { "name": "Target Name", "rationale": "Direct genetic driver...", "score": 9 }
        ],
        "priorityLigands": [
            { "name": "Compound Name", "target": "Target Name", "tier": "FDA Approved", "smiles": "Available" }
        ]
    }
    `;

    try {
        const response = await ai.models.generateContent({
            model: MODEL_NAME, // Use same model as main synthesis
            contents: [{
                role: 'user',
                parts: [{ text: selectionPrompt + "\n\nDATA SUMMARY:\n" + contextSummary }]
            }],
            generationConfig: { responseMimeType: "application/json" }
        });

        let text = response.candidates[0].content.parts[0].text;
        text = text.replace(/```json\n?|```/g, '').trim();
        return JSON.parse(text);
    } catch (e) {
        console.error("Selection Algorithm Failed:", e);
        return { priorityTargets: [], priorityLigands: [] }; // Fallback
    }
}

/**
 * Main synthesis function
 */
export const synthesizeMolecularDossier = async (symptoms, crawledData, onProgress) => {
    const validData = crawledData.filter(d => d.success && d.content && d.content.length > 50);

    if (validData.length === 0) throw new Error("No valid data available.");

    const categorizedSources = categorizeSources(validData);

    // --- STEP 1: RUN SELECTION ALGORITHM ---
    const selectionResult = await runSelectionAlgorithm(symptoms, categorizedSources, onProgress);

    // --- STEP 2: BUILD CONTENT WITH SELECTIONS ---
    const systemPrompt = buildComprehensiveSystemPrompt(symptoms);
    const userContent = buildUserContentWithSelections(categorizedSources, symptoms, selectionResult);

    try {
        if (onProgress) {
            onProgress({
                stage: "synthesizing",
                message: "Compiling Molecular Dossier based on algorithm selections...",
                status: "running"
            });
        }

        const response = await withRetry(async () => {
            return await ai.models.generateContentStream({
                model: MODEL_NAME,
                contents: [{
                    role: 'user',
                    parts: [{ text: systemPrompt + "\n\n" + userContent }]
                }],
                generationConfig: {
                    temperature: 0.4,
                    topP: 0.95,
                    maxOutputTokens: 65536
                }
            });
        });

        let fullContent = "";
        let currentThought = "";
        let lastProgressUpdate = 0;
        let chunkCount = 0;

        for await (const chunk of response) {
            const parts = chunk.candidates?.[0]?.content?.parts || [];
            for (const part of parts) {
                if (part.thought) {
                    currentThought += part.text || "";
                } else if (part.text) {
                    fullContent += part.text;
                    chunkCount++;
                    if (onProgress && chunkCount % 20 === 0) {
                        onProgress({
                            stage: "writing",
                            message: `Generating dossier... (${fullContent.length} chars)`,
                            status: "running",
                            progress: Math.min(99, 50 + chunkCount)
                        });
                    }
                }
            }
        }

        if (onProgress) onProgress({ stage: "complete", message: "Complete", status: "complete", progress: 100 });

        return {
            content: fullContent,
            sourcesUsed: validData.length,
            sourceBreakdown: {
                clinical: categorizedSources.clinical.length,
                protein: categorizedSources.protein.length,
                compound: categorizedSources.compound.length,
                general: categorizedSources.general.length
            },
            success: true,
            modelUsed: MODEL_NAME,
            timestamp: new Date().toISOString()
        };
    } catch (error) {
        console.error("Gemini synthesis error:", error);
        throw error;
    }
};

function categorizeSources(sources) {
    const categories = { clinical: [], protein: [], compound: [], pathway: [], general: [] };
    for (const source of sources) {
        const url = source.url.toLowerCase();
        const content = (source.content || "").toLowerCase();

        if (url.includes('pubmed') || url.includes('clinical')) categories.clinical.push(source);
        else if (url.includes('uniprot') || content.includes('protein')) categories.protein.push(source);
        else if (url.includes('pubchem') || url.includes('drugbank')) categories.compound.push(source);
        else if (url.includes('kegg') || content.includes('pathway')) categories.pathway.push(source);
        else categories.general.push(source);
    }
    return categories;
}

/**
 * UPDATED SYSTEM PROMPT:
 * Focuses on Detailed Analysis for the *Algorithm Selected* items.
 */
function buildComprehensiveSystemPrompt(symptoms) {
    return `# ROLE: Senior Bioinformatics Research Scientist

You are conducting a comprehensive molecular investigation for: "${symptoms}"

## OBJECTIVE
Create an **EXHAUSTIVE** Molecular Dossier using the provided **Algorithmic Selections**.

## REQUIRED DOSSIER STRUCTURE

### EXECUTIVE SUMMARY
- Brief overview of disease mechanism.
- Summary of targets identified.

### SECTION 1: MASTER LISTS (DATA EXTRACTION)
**INSTRUCTION:** Extract ALL proteins and compounds mentioned in sources. Do not filter here.
#### 1.1 Master Protein Target List
| Target Name | UniProt ID | Type | Relevance | Source |
|-------------|------------|------|-----------|--------|

#### 1.2 Master Ligand & Drug Candidate List
**INSTRUCTION:** Include SMILES for every compound found if available.
| Compound Name | ID | Target | Status | SMILES | Mechanism |
|---------------|----|--------|--------|--------|-----------|

### SECTION 2: DISEASE MECHANISM
(Pathophysiology analysis)

---
### SECTION 3: PRIORITY TARGET DEEP-DIVE
**MANDATORY:** You MUST analyze the **Priority Targets** listed in the "Mandatory Algorithmic Selections" provided below.

For EACH Priority Target:
#### Target: [PROTEIN NAME]
- **Selection Rationale:** (Why was this scored high?)
- **Function & Disease Role:**
- **Structural Data:** (PDB IDs)
- **Druggability:**
- **Key Binding Pockets:**

---
### SECTION 4: PRIORITY PHARMACOLOGY DEEP-DIVE
**MANDATORY:** You MUST analyze the **Priority Ligands** listed in the "Mandatory Algorithmic Selections".
**REQUIREMENT:** Analyze at least 1 compound for EVERY target in Section 3.

For EACH Priority Compound:
#### Compound: [NAME]
- **Primary Target:**
- **Clinical Tier:** (FDA / Clinical / Pre-clinical)
- **Binding Affinity:** (IC50/Ki)
- **Structure:** (SMILES)
- **ADMET Profile:**
- **Mechanism:**

---
### SECTION 5: CLINICAL EVIDENCE
### SECTION 6: REFERENCES
`;
}

/**
 * UPDATED USER CONTENT BUILDER
 * Injects the Algorithm results directly into the prompt to force the writer's hand.
 */
function buildUserContentWithSelections(categorizedSources, symptoms, selectionResult) {
    let content = `# RESEARCH QUERY: "${symptoms}"\n\n`;

    // --- INJECT ALGORITHM RESULTS ---
    content += `## ⚠️ MANDATORY ALGORITHMIC SELECTIONS\n`;
    content += `The Ranking Algorithm has analyzed the data and selected the following candidates.\n`;
    content += `**You MUST use these specific candidates for Section 3 and Section 4.**\n\n`;

    content += `### PRIORITY TARGETS (Section 3):\n`;
    selectionResult.priorityTargets?.forEach(t => {
        content += `- **${t.name}** (Score: ${t.score}/10). Rationale: ${t.rationale}\n`;
    });

    content += `\n### PRIORITY LIGANDS (Section 4):\n`;
    selectionResult.priorityLigands?.forEach(l => {
        content += `- **${l.name}** (Tier: ${l.tier}). Target: ${l.target}\n`;
    });

    content += `\n---\n\n`;
    content += `## EXTRACTED SOURCE DATA\n\n`;

    // Increased Context Limit
    const CHAR_LIMIT = 30000;

    const addSources = (category, title, sources) => {
        if (sources.length === 0) return "";
        let section = `### ${title} (${sources.length} sources)\n\n`;
        sources.forEach((source, i) => {
            section += `---\n`;
            section += `**[${category.toUpperCase()}-${i + 1}] ${source.title || 'Untitled'}**\n`;
            section += `- URL: ${source.url}\n`;
            section += `\n**Full Content:**\n${source.content.substring(0, CHAR_LIMIT)}\n\n`;
        });
        return section;
    };

    content += addSources("clinical", "Clinical & Medical Literature", categorizedSources.clinical);
    content += addSources("protein", "Protein & Gene Data", categorizedSources.protein);
    content += addSources("compound", "Compound & Drug Data", categorizedSources.compound);
    content += addSources("pathway", "Pathway Data", categorizedSources.pathway);
    content += addSources("general", "General Sources", categorizedSources.general);

    return content;
}

/**
 * Extract structured candidates from the generated dossier using Flash (Component 2 of Hybrid Phase)
 */
export const extractCandidatesFromDossier = async (dossierContent) => {
    try {
        const response = await ai.models.generateContent({
            model: "gemini-3-flash-preview", // Fast extraction
            contents: [{
                role: 'user',
                parts: [{
                    text: `Extract all chemical compounds, drugs, and ligands mentioned as PRIORITY candidates from the provided text.
                    Focus on "Priority Pharmacology" section.
                    
                    Tasks:
                    1. Extract Name (Prioritize Small Molecules over Antibodies if possible).
                    2. Extract SMILES string (Required for chemical analysis).
                    3. Extract Primary Target (protein name).
                    4. Find the BEST matching PDB ID for the target from RCSB PDB database (e.g., "4EY6", "1ATP", "2XZD"). Use common/validated structures.
                    5. Extract Mechanism of Action (2-3 scientific sentences explaining HOW it binds/works).
                    6. Generate a Plausible 3-Step Synthesis Pathway (theoretical or known).
                    7. Include scientific references and source validation.
                    
                    Return JSON Array:
                    [
                        { 
                            "name": "Compound X", 
                            "smiles": "C1=CC...", 
                            "target": "Protein Y", 
                            "pdb_id": "4EY6",
                            "pdb_source": "RCSB Protein Data Bank",
                            "pdb_resolution": "2.1 Å",
                            "pdb_method": "X-ray diffraction",
                            "tier": "Novel/FDA/Clinical/Preclinical",
                            "mechanism": "Competitive inhibitor that forms H-bonds with...",
                            "mechanism_evidence": "Based on molecular docking studies and published literature",
                            "references": [
                                { "database": "PubMed", "id": "PMID:12345678", "url": "https://pubmed.ncbi.nlm.nih.gov/12345678" },
                                { "database": "PubChem", "id": "CID:12345", "url": "https://pubchem.ncbi.nlm.nih.gov/compound/12345" },
                                { "database": "RCSB PDB", "id": "4EY6", "url": "https://www.rcsb.org/structure/4EY6" }
                            ],
                            "synthesis": [
                                { "step": 1, "reactant": "Start Material A", "reagent": "Reagent B", "product": "Intermediate C", "conditions": "RT, 2h" },
                                { "step": 2, "reactant": "Intermediate C", "reagent": "Reagent D", "product": "Compound X", "conditions": "Reflux, 4h" }
                            ]
                        }
                    ]
                    
                    TEXT TO ANALYZE:
                    ${dossierContent.substring(0, 30000)}`
                }]
            }],
            generationConfig: { responseMimeType: "application/json" }
        });

        let text = response.candidates[0].content.parts[0].text;
        // Clean markdown code blocks if present
        text = text.replace(/```json\n?|```/g, '').trim();
        return JSON.parse(text);
    } catch (e) {
        console.error("Candidate extraction failed:", e);
        return [];
    }
};

export default {
    ai,
    generateResearchPlan,
    synthesizeMolecularDossier,
    extractCandidatesFromDossier
};
