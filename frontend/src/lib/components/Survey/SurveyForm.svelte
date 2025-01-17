<script lang="ts">
  import { onMount } from 'svelte';
  import { surveyStore } from '$lib/stores/surveyStore';
  import type { Questions } from '$lib/types/survey';
  import { goto } from '$app/navigation';
  
  let questions: Questions | null = null;
  let loading = true;
  let error: string | null = null;
  
  onMount(async () => {
    try {
      const response = await fetch('/questions_responses.json');
      if (!response.ok) throw new Error('Failed to load questions');
      questions = await response.json();
      loading = false;
    } catch (e) {
      error = e instanceof Error ? e.message : 'An error occurred';
      loading = false;
    }
  });

  $: isComplete = questions && $surveyStore.answers && 
    Object.keys(questions.questions).every(qId => 
      $surveyStore.answers[qId]?.scores !== undefined
    );

    async function handleSubmit() {
    console.log('HandleSubmit called');
    if (!isComplete) {
        console.log('Form not complete');
        return;
    }
    
    try {
        const surveyData = {
            session_id: $surveyStore.sessionId,
            answers: $surveyStore.answers,
            source: 'web',
            browser: navigator.userAgent,
            version: '2.0.0'
        };
        console.log('Survey data:', surveyData);

        const response = await fetch('http://localhost:8000/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(surveyData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Submission failed:', errorText);
            throw new Error(`Failed to submit survey: ${errorText}`);
        }

        const result = await response.json();
        console.log('Submission successful:', result);

        // Only navigate after confirmed success
        await goto('/results');
    } catch (error) {
        console.error('Submission error:', error);
        error = error instanceof Error ? error.message : 'Failed to submit survey';
    }
}
</script>

<div class="container mx-auto px-4 py-8">
  {#if loading}
    <div class="text-center p-4">Loading survey...</div>
{:else if error}
    <div class="text-center p-4 text-red-600">{error}</div>
{:else if questions}
    <form 
        on:submit|preventDefault={async (event) => {
            event.preventDefault();
            console.log('Form submitted');
            await handleSubmit();
        }} 
        class="space-y-6"
    >
        {#each Object.entries(questions.questions) as [qKey, question]}
            <div class="mb-8 p-6 bg-white rounded-lg shadow">
                <h2 class="text-xl font-semibold mb-4">{question.text}</h2>
                
                <div class="space-y-2">
                    {#each question.responses as response}
                        <label class="flex items-start p-2 hover:bg-gray-50 rounded">
                            <input
                                type="radio"
                                name={qKey}
                                value={response.r_value}
                                checked={$surveyStore.answers[qKey]?.scores.join(',') === response.scores.join(',')}
                                class="mt-1 mr-3"
                                on:change={() => surveyStore.setResponse(qKey, response.scores)}
                            />
                            <span>{response.text}</span>
                        </label>
                    {/each}
                </div>
            </div>
        {/each}
        
        <div class="mt-8 flex justify-center">
            <button 
                type="submit" 
                disabled={!isComplete}
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
                Submit Survey
            </button>
        </div>
    </form>
{/if}
</div>