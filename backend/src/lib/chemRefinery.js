import fetch from "node-fetch";

const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || "http://localhost:8000";

/**
 * Calls the Python Chemical Microservice to analyze a SMILES string.
 * Validates Drug-likeness, Lipinski Rules, and Biochemical Properties.
 */
export const analyzeMolecule = async (smiles) => {
    try {
        const response = await fetch(`${PYTHON_SERVICE_URL}/api/chemistry/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ smiles }),
        });

        if (!response.ok) {
            console.error(`Chemical Service Error: ${response.statusText}`);
            return null;
        }

        const data = await response.json();
        return data; // Returns { valid, properties, lipinski, analysis }
    } catch (error) {
        console.error("Failed to connect to Chemical Microservice:", error.message);
        return null; // Fail gracefully
    }
};

/**
 * Requests an SVG rendering of the molecule.
 */
export const renderMoleculeSVG = async (smiles) => {
    try {
        const response = await fetch(`${PYTHON_SERVICE_URL}/api/chemistry/render?smiles=${encodeURIComponent(smiles)}`);
        if (!response.ok) return null;
        const data = await response.json();
        return data.svg;
    } catch (error) {
        return null;
    }
};

/**
 * Heuristic to calculate a simple "Confidence Score" (0-100)
 * based on the analysis.
 */
export const calculateConfidenceScore = (analysis) => {
    if (!analysis || !analysis.valid) return 0;

    let score = 50; // Base score

    // Reward/Penalize based on QED (Drug-likeness)
    if (analysis.properties.qed > 0.7) score += 30;
    else if (analysis.properties.qed > 0.5) score += 15;
    else score -= 10;

    // Penalize Lipinski Violations
    score -= (analysis.lipinski.violations_count * 15);

    // Cap at 99 (nothing is 100%)
    return Math.max(10, Math.min(99, score));
};
