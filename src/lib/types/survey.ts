// src/lib/types/survey.ts
export interface SurveyResponse {
  sessionId: string;
  questionId: string;
  response: number;
}

// src/lib/db/mysql.ts
import mysql from 'mysql2/promise';

export const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
});

// src/routes/api/test/+server.ts
import { json } from '@sveltejs/kit';
import { pool } from '$lib/db/mysql';

export async function GET() {
  try {
    const [rows] = await pool.query('SELECT 1');
    return json({ success: true, data: rows });
  } catch (error) {
    return json({ success: false, error: error.message });
  }
}