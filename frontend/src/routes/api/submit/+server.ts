// src/routes/api/submit/+server.ts
import { json } from '@sveltejs/kit';
import mysql from 'mysql2/promise';
import { env } from '$env/dynamic/private';
import type { RequestEvent } from '@sveltejs/kit';
import type { SurveyDatabaseRecord } from '$lib/data/survey-db';

// Check for production environment
const isProduction = process.env.NODE_ENV === 'production' || process.env.GAE_ENV === 'standard';

const dbConfig = isProduction 
    ? {
        // Production (Cloud) settings
        socketPath: '/cloudsql/modernity-worldview:us-central1:modernity-db',
        user: env.DB_USER || 'app_user',
        database: env.DB_NAME || 'modernity_survey',
        waitForConnections: true,
        connectionLimit: 10,
        connectTimeout: 60000,
        ssl: null  // Not needed when using socket path
    } 
    : {
        // Development settings - proxy connection
        host: 'localhost',
        user: env.DB_USER,
        database: env.DB_NAME,
        port: 3307,
        waitForConnections: true,
        connectionLimit: 10
    };

console.log('Environment:', {
    isProduction,
    NODE_ENV: process.env.NODE_ENV,
    GAE_ENV: process.env.GAE_ENV,
    dbHost: dbConfig.host,
    dbPort: dbConfig.port
});

// Helper function to find response number based on scores
function findResponseNumber(scores: number[]): number {
    // Map known score patterns to response numbers
    const scorePatterns = [
        [100, 0, 0],    // Response 1
        [0, 100, 0],    // Response 2
        [0, 0, 100],    // Response 3
        [50, 50, 0],    // Response 4
        [25, 50, 25]    // Response 5
    ];

    const scoresStr = scores.join(',');
    const index = scorePatterns.findIndex(pattern => pattern.join(',') === scoresStr);
    return index !== -1 ? index + 1 : null;
}

const pool = mysql.createPool({
    ...dbConfig,
    password: env.DB_PASSWORD
});

export async function POST(event: RequestEvent) {
    try {
        const rawData = await event.request.json();
        console.log('Raw survey data received:', rawData);

        // Calculate response numbers and scores
        const responses = {};
        let totalScores = [0, 0, 0];
        let responseCount = 0;

        Object.entries(rawData.answers || {}).forEach(([qKey, answer]: [string, any]) => {
            if (answer.scores) {
                // Find the response number based on the scores pattern
                responses[qKey] = findResponseNumber(answer.scores);
                
                // Add to total scores
                totalScores[0] += answer.scores[0] || 0;
                totalScores[1] += answer.scores[1] || 0;
                totalScores[2] += answer.scores[2] || 0;
                responseCount++;
            }
        });

        console.log('Calculated responses:', responses);

        // Calculate n values and plot coordinates
        const n1 = responseCount > 0 ? Math.round((totalScores[0] / responseCount) * 6) : null;
        const n2 = responseCount > 0 ? Math.round((totalScores[1] / responseCount) * 6) : null;
        const n3 = responseCount > 0 ? Math.round((totalScores[2] / responseCount) * 6) : null;

        const plot_x = n1 !== null && n2 !== null ? parseFloat(((n2 - n1) / 6).toFixed(2)) : null;
        const plot_y = n1 !== null && n2 !== null && n3 !== null ? 
            parseFloat(((n3 - ((n1 + n2) / 2)) / 6).toFixed(2)) : null;

        const surveyData: SurveyDatabaseRecord = {
            q1_response: responses['Q1'] ?? null,
            q2_response: responses['Q2'] ?? null,
            q3_response: responses['Q3'] ?? null,
            q4_response: responses['Q4'] ?? null,
            q5_response: responses['Q5'] ?? null,
            q6_response: responses['Q6'] ?? null,
            n1,
            n2,
            n3,
            plot_x,
            plot_y,
            session_id: rawData.session_id,
            browser: rawData.browser,
            source: rawData.source || 'web'
        };

        console.log('Transformed survey data:', surveyData);

        const connection = await pool.getConnection();
        try {
            const query = `
                INSERT INTO survey_results (
                    q1_response, q2_response, q3_response, 
                    q4_response, q5_response, q6_response,
                    n1, n2, n3, 
                    plot_x, plot_y,
                    session_id, browser, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `;

            const values = [
                surveyData.q1_response,
                surveyData.q2_response,
                surveyData.q3_response,
                surveyData.q4_response,
                surveyData.q5_response,
                surveyData.q6_response,
                surveyData.n1,
                surveyData.n2,
                surveyData.n3,
                surveyData.plot_x,
                surveyData.plot_y,
                surveyData.session_id,
                surveyData.browser,
                surveyData.source
            ];

            console.log('Executing INSERT with values:', values);

            const [result] = await connection.execute(query, values);
            console.log('Survey response saved:', result);
            
            return json({
                success: true,
                message: 'Survey response recorded successfully'
            });
        } finally {
            connection.release();
        }

    } catch (error: any) {
        console.error('Detailed error information:', {
            name: error.name,
            message: error.message,
            code: error.code,
            errno: error.errno,
            sqlState: error.sqlState,
            sqlMessage: error.sqlMessage
        });
        
        return json(
            { 
                error: 'Failed to save survey response', 
                details: error.message 
            },
            { status: 500 }
        );
    }
}