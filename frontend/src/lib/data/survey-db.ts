// frontend/src/lib/data/survey-db.ts
import type { Questions } from '$lib/types/survey';
import type { SurveyStoreState, SurveyAnswer } from '$lib/stores/surveyStore';

interface SurveyDatabaseRecord {
    q1_response: number | null;
    q2_response: number | null;
    q3_response: number | null;
    q4_response: number | null;
    q5_response: number | null;
    q6_response: number | null;
    n1: number | null;
    n2: number | null;
    n3: number | null;
    plot_x: number | null;
    plot_y: number | null;
    session_id: string;
    source: string;
    hash_email_session?: string | null;
    browser?: string | null;
    region?: string | null;
    version?: string | null;
}

type ResponseKey = 'q1_response' | 'q2_response' | 'q3_response' | 
                   'q4_response' | 'q5_response' | 'q6_response';

function prepareSurveyDataForDatabase(
    surveyStore: SurveyStoreState,
    questions: Questions,
    version: string = '2.0.0'
): SurveyDatabaseRecord {
    const record: SurveyDatabaseRecord = {
        q1_response: 0,
        q2_response: 0,
        q3_response: 0,
        q4_response: 0,
        q5_response: 0,
        q6_response: 0,
        n1: 0,
        n2: 0,
        n3: 0,
        plot_x: 0,
        plot_y: 0,
        session_id: surveyStore.sessionId || crypto.randomUUID(),
        source: 'web',
        browser: navigator.userAgent,
        version: version
    };

    Object.entries(surveyStore.answers).forEach(([qId, answer]: [string, SurveyAnswer]) => {
        const questionNum = parseInt(qId.replace('Q', ''));
        const responseNum = questions.questions[qId].responses.findIndex(
            r => r.scores.join(',') === answer.scores.join(',')
        ) + 1;
        const key = `q${questionNum}_response` as ResponseKey;
        if (key in record) {
            record[key] = responseNum;
        }
    });

    let totals: [number, number, number] = [0, 0, 0];
    const answers = Object.values(surveyStore.answers);
    answers.forEach((answer: SurveyAnswer) => {
        totals[0] += answer.scores[0];
        totals[1] += answer.scores[1];
        totals[2] += answer.scores[2];
    });

    const responseCount = answers.length;
    if (responseCount > 0) {
        record.n1 = Math.round((totals[0] / responseCount) * 6);
        record.n2 = Math.round((totals[1] / responseCount) * 6);
        record.n3 = Math.round((totals[2] / responseCount) * 6);
        record.plot_x = parseFloat(((record.n2 - record.n1) / 6).toFixed(2));
        record.plot_y = parseFloat(((record.n3 - ((record.n1 + record.n2) / 2)) / 6).toFixed(2));
    }

    return record;
}

export { prepareSurveyDataForDatabase, type SurveyDatabaseRecord };