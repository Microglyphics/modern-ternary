// src/lib/types/survey.ts
export interface Response {
    id: string;
    text: string;
    scores: [number, number, number];
    r_value: number;
}

export interface Question {
    id: string;           // Added this
    text: string;
    responses: Response[];
    required?: boolean;   // Added this
}

export interface Questions {
    questions: {
        [key: string]: Question;
    };
}

export interface SurveyStoreState {
    currentQuestionId: string;
    answers: {
        [questionId: string]: {
            responseId: string;
            scores: [number, number, number];
            timestamp: string;
        }
    };
    sessionId?: string;
}