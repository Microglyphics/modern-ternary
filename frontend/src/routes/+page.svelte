<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import type { Questions } from '$lib/types/survey';
    import { surveyStore } from '$lib/stores/surveyStore';

    interface ResponseNumbers {
        q1_response: number;
        q2_response: number;
        q3_response: number;
        q4_response: number;
        q5_response: number;
        q6_response: number;
    }

    interface SubmissionData {
        session_id: string;
        source: 'web';
        browser: string;
        q1_response: number;
        q2_response: number;
        q3_response: number;
        q4_response: number;
        q5_response: number;
        q6_response: number;
        n1: number;
        n2: number;
        n3: number;
        plot_x: number;
        plot_y: number;
    }

    let questions: Questions | null = null;
    let questionList: Questions['questions'] | null = null;
    let submissionData: SubmissionData | null = null;

    onMount(async () => {
        try {
            const response = await fetch('/questions_responses.json');
            if (!response.ok) throw new Error('Failed to load questions');
            questions = await response.json();
            questionList = questions?.questions || null;
            console.log('Loaded questions:', questionList);
        } catch (error) {
            console.error('Failed to load questions:', error);
        }
    });

    $: isComplete = $surveyStore.answers && 
        questionList && 
        Object.keys(questionList).every(qId => 
            $surveyStore.answers[qId]?.scores !== undefined
        );

    // Calculate submission data whenever answers change
    $: if (isComplete && questionList && $surveyStore.sessionId) {
        const totals = Object.values($surveyStore.answers).reduce(
            (acc: number[], answer) => {
                answer.scores.forEach((score, idx) => {
                    acc[idx] += Number(score);
                });
                return acc;
            },
            [0, 0, 0]
        );
        
        const total = totals[0] + totals[1] + totals[2];

        // Initialize with correct types
        const responseNumbers: ResponseNumbers = {
            q1_response: 1,
            q2_response: 1,
            q3_response: 1,
            q4_response: 1,
            q5_response: 1,
            q6_response: 1
        };

        // Safe access to questionList since we checked it's not null
        Object.entries($surveyStore.answers).forEach(([qId, answer]) => {
            const responses = questionList[qId].responses;
            const index = responses.findIndex(
                r => r.scores.join(',') === answer.scores.join(',')
            );
            const key = `${qId.toLowerCase()}_response` as keyof ResponseNumbers;
            responseNumbers[key] = index + 1;
        });

        submissionData = {
            session_id: $surveyStore.sessionId,
            source: 'web',
            browser: navigator.userAgent,
            ...responseNumbers,
            n1: totals[0],
            n2: totals[1],
            n3: totals[2],
            plot_x: parseFloat(((totals[1] / total) * 100).toFixed(2)),
            plot_y: parseFloat(((totals[2] / total) * 100).toFixed(2))
        };
    }

    async function handleSubmit() {
    console.log('HandleSubmit called');
    if (!isComplete || !questions || !questionList || !submissionData) {
        console.error('Validation failed:', { 
            isComplete, 
            hasQuestions: !!questions, 
            hasQuestionList: !!questionList, 
            hasSubmissionData: !!submissionData 
        });
        return;
    }

    try {
        console.log('Attempting submission with data:', submissionData);

        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(submissionData)
        });

        console.log('Raw Response:', response);
        console.log('Response Status:', response.status);
        console.log('Response Headers:', Object.fromEntries(response.headers.entries()));

        const responseText = await response.text();
        console.log('Response Text:', responseText);

        if (!response.ok) {
            console.error('Submission failed:', {
                status: response.status,
                statusText: response.statusText,
                body: responseText
            });
            throw new Error(`Failed to submit survey: ${responseText}`);
        }

        let result;
        try {
            result = JSON.parse(responseText);
            console.log('Parsed Response:', result);
        } catch (parseError) {
            console.error('Error parsing response:', parseError);
            console.log('Raw response text:', responseText);
            throw new Error('Invalid response format from server');
        }

        try {
            console.log('Attempting navigation to /results');
            await goto('/results');
        } catch (navError) {
            console.error('Navigation failed:', navError);
            console.log('Trying fallback navigation');
            window.location.href = '/results';
        }
    } catch (error) {
        console.error('Submission error:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
        throw error;
    }
}
</script>

<main class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Modernity Worldview Survey</h1>
    
    <!-- Debug Status Box - Always visible -->
    <div class="mb-8 p-4 bg-gray-100 rounded border-2 border-dashed border-gray-300">
        <h3 class="text-lg font-bold mb-2">Page Status</h3>
        <div class="bg-white p-4 rounded-lg">
            <p><strong>Questions Loaded:</strong> {questionList ? 'Yes' : 'No'}</p>
            <p><strong>Form Complete:</strong> {isComplete ? 'Yes' : 'No'}</p>
            <p><strong>Session ID:</strong> {$surveyStore.sessionId || 'Not generated'}</p>
        </div>
    </div>

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
                                    value={response.id}
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

            <!-- Survey Data Debug Box -->
            <div class="mt-8 p-4 bg-gray-100 rounded border-2 border-dashed border-gray-300">
                <h3 class="text-lg font-bold mb-2">Current Survey Data</h3>
                <div class="bg-white p-4 rounded-lg">
                    <div class="mb-4">
                        <h4 class="font-semibold mb-2">Raw Answers:</h4>
                        <pre class="bg-gray-50 p-2 rounded overflow-auto text-sm">
                            {JSON.stringify($surveyStore.answers, null, 2)}
                        </pre>
                    </div>
                    {#if submissionData}
                        <div>
                            <h4 class="font-semibold mb-2">Data to Submit:</h4>
                            <pre class="bg-gray-50 p-2 rounded overflow-auto text-sm">
                                {JSON.stringify(submissionData, null, 2)}
                            </pre>
                        </div>
                    {/if}
                </div>
            </div>
        </form>
    {/if}
</main>