// src/routes/api/survey/+server.ts
import { json } from '@sveltejs/kit';
import { surveyStore } from '$lib/stores/surveyStore';

export async function POST({ request }) {
   const { questionId, scores } = await request.json();
   
   surveyStore.setResponse(questionId, scores);
   
   try {
       // DB insert logic here
       return json({ success: true });
   } catch (error) {
       return json({ success: false, error: error.message }, { status: 500 });
   }
}

export async function GET() {
   try {
       let state;
       surveyStore.subscribe(value => {
           state = value;
       })();
       return json(state);
   } catch (error) {
       return json({ error: error.message }, { status: 500 });
   }
}