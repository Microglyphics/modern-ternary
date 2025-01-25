// src/lib/utils/validation.ts
export function validateResponse(questionNum: number, response: number): boolean {
  return response >= 1 && response <= 6;
}

export function validateScores(n1: number, n2: number, n3: number): boolean {
  return [n1, n2, n3].every(n => n >= 0 && n <= 600);
}