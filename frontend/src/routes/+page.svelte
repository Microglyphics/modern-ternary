//+page.svelte
<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import type { Questions } from '../lib/types/survey';  // Relative path
    import { surveyStore } from '../lib/stores/surveyStore';  // Relative path

    let questions: Questions | null = null;
    let questionList: Questions['questions'] | null = null;

    onMount(async () => {
        try {
            const response = await fetch('/questions_responses.json');
            if (!response.ok) throw new Error('Failed to load questions');
            questions = await response.json();
            questionList = questions?.questions || null;
            console.log('Loaded questions:', questionList); // Debug log
        } catch (error) {
            console.error('Failed to load questions:', error);
        }
    });

    $: isComplete = $surveyStore.answers && 
        questionList && 
        Object.keys(questionList).every(qId => 
            $surveyStore.answers[qId]?.scores !== undefined
        );

    async function handleSubmit() {
        console.log('HandleSubmit called');
        if (!isComplete || !questions || !questionList) {
            console.log('Form not complete or questions not loaded');
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
            console.log('Submitting survey data:', surveyData);

            const response = await fetch('/api/submit', {
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

            await goto('/results');
        } catch (error) {
            console.error('Submission error:', error);
            error = error instanceof Error ? error.message : 'Failed to submit survey';
        }
    }
</script>

<main class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Modernity Worldview Survey</h1>
    
    {#if !questionList}
        <div class="text-center p-4">Loading survey...</div>
    {:else}
        <form on:submit|preventDefault={handleSubmit}>
            {#each Object.entries(questionList) as [qKey, question]}
                <div class="mb-8 p-6 bg-white rounded-lg shadow">
                    <h2 class="text-xl font-semibold mb-4">{question.text}</h2>
                    
                    <div class="space-y-2">
                        {#each question.responses as response}
                            <label class="flex items-start p-2 hover:bg-gray-50 rounded">
                                <input
                                    type="radio"
                                    name={qKey}
                                    value={response.r_value}
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
                    class="px-8 py-3 bg-blue-600 text-white rounded-lg disabled:bg-gray-400"
                    disabled={!isComplete}
                >
                    Submit Survey
                </button>
            </div>
        </form>
    {/if}
</main>