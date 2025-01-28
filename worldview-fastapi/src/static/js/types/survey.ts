// src/types/survey.ts
export interface SurveyResponse {
  id: string;
  text: string;
  scores: number[];
}

export interface Question {
  text: string;
  responses: SurveyResponse[];
}

export interface Questions {
  [key: string]: Question;
}