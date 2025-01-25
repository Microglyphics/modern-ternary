// frontend/src/lib/stores/surveyStore.ts
import { writable } from 'svelte/store';
import type { Questions } from '$lib/types/survey';

// src/lib/stores/surveyStore.ts
export interface SurveyAnswer {
    responseId: string;
    scores: [number, number, number];
    timestamp: string;  // Add this back
    response_num?: number;  // Optional
}

export interface SurveyStoreState {
    currentQuestionId: string;
    answers: {
        [questionId: string]: SurveyAnswer;
    };
    sessionId?: string;
}

function createSurveyStore() {
    const initialState: SurveyStoreState = {
        currentQuestionId: '',
        answers: {},
        sessionId: crypto.randomUUID()
    };

    const { subscribe, update } = writable<SurveyStoreState>(initialState);

    return {
        subscribe,
        setResponse: (questionId: string, scores: [number, number, number]) => {
            update(state => ({
                ...state,
                answers: {
                    ...state.answers,
                    [questionId]: {
                        responseId: crypto.randomUUID(),
                        scores,
                        timestamp: new Date().toISOString()
                    }
                }
            }));
        },
        reset: () => {
            update(() => ({
                ...initialState,
                sessionId: crypto.randomUUID()
            }));
        }
    };
}

export const surveyStore = createSurveyStore();