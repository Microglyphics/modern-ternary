// src/lib/types/survey.ts

// Base types
export interface Response {
    id: string;
    text: string;
    scores: [number, number, number];
}

export interface Question {
    text: string;
    responses: Response[];
}

export interface Questions {
    questions: Record<string, Question>;  // This fixes the indexing issue
}

// Survey store types
export interface SurveyAnswer {
    responseId: string;
    scores: [number, number, number];
    timestamp: string;
}

export interface SurveyStoreState {
    currentQuestionId: string;
    answers: Record<string, SurveyAnswer>;  // This fixes the indexing issue
    sessionId?: string;
}

// API types
export interface SurveySubmission {
    session_id: string;
    answers: Record<string, {
        responseId: string;
        scores: number[];
        timestamp: string;
    }>;
    source: string;
    browser: string;
    version: string;
}

export interface ApiErrorDetail {
    type: string;
    loc: string[];
    msg: string;
    input: any;
}

export interface ApiResponse {
    success: boolean;
    message?: string;
    error?: {
        detail: ApiErrorDetail[];
    };
}

// Database record type
export interface DatabaseRecord {
    session_id: string;
    source: string;
    browser: string;
    q1_response: number | null;
    q2_response: number | null;
    q3_response: number | null;
    q4_response: number | null;
    q5_response: number | null;
    q6_response: number | null;
    n1: number;
    n2: number;
    n3: number;
    plot_x: number;
    plot_y: number;
}