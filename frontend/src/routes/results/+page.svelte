<script lang="ts">
    import { surveyStore } from '$lib/stores/surveyStore';
    import type { Questions } from '$lib/types/survey';
    import { onMount } from 'svelte';

    interface ResultItem {
    question: string;
    response: string;
    scores: [number, number, number];
    interpretation?: string;
    }

    interface ResponseTemplate {
        score_pattern: [number, number, number];
        response: string;
    }

    type CategoryType = 'PreModern' | 'Modern' | 'PostModern' | 'PreModern-Modern' | 'Modern-Balanced';

    interface CategoryPattern {
        [key: string]: {
            [K in CategoryType]: ResponseTemplate;
        };
    }

    let results: ResultItem[] = [];
    let questions: Questions | null = null;
    let templates: { categories: CategoryPattern } | null = null;

    // Use type assertion for categoryMap
    const categoryMap: Record<string, string> = {
        'Q1': 'Source of Truth',
        'Q2': 'Understanding the World',
        'Q3': 'Knowledge Acquisition',
        'Q4': 'World View',
        'Q5': 'Societal Values',
        'Q6': 'Identity'
    } as const;

    function findBestMatchPattern(scores: [number, number, number], patterns: Record<CategoryType, ResponseTemplate>): CategoryType {
        const patternEntries: [CategoryType, ResponseTemplate][] = Object.entries(patterns) as [CategoryType, ResponseTemplate][];
        
        let bestMatch: CategoryType = 'Modern-Balanced';
        let smallestDifference = Infinity;

        patternEntries.forEach(([name, template]) => {
            const difference = Math.abs(template.score_pattern[0] - scores[0]) + 
                            Math.abs(template.score_pattern[1] - scores[1]) + 
                            Math.abs(template.score_pattern[2] - scores[2]);
            if (difference < smallestDifference) {
                smallestDifference = difference;
                bestMatch = name;
            }
        });

        return bestMatch;
    }

    onMount(async () => {
        try {
            // Load both data files
            const [questionsResponse, templatesResponse] = await Promise.all([
                fetch('/questions_responses.json'),
                fetch('/response_templates.json')
            ]);

            questions = await questionsResponse.json();
            templates = await templatesResponse.json();
            
            if (questions && templates && $surveyStore.answers) {
                calculateResults();
            }
        } catch (error) {
            console.error('Error loading data:', error);
        }
    });

    function calculateResults() {
        if (!questions || !templates) return;

        results = Object.entries($surveyStore.answers)
            .map(([qId, answer]): ResultItem | null => {  // Explicitly specify return type
                const question = questions?.questions[qId];
                if (!question) return null;

                const categoryName = categoryMap[qId];
                if (!categoryName) return null;

                const categoryTemplates = templates?.categories[categoryName];
                if (!categoryTemplates) return null;

                const patternType = findBestMatchPattern(answer.scores, categoryTemplates);
                const matchedResponse = categoryTemplates[patternType]?.response;
                if (!matchedResponse) return null;

                const responseText = question.responses.find(r => 
                    r.scores.join('.') === answer.scores.join('.')
                )?.text || 'No answer';

                return {
                    question: question.text,
                    response: responseText,
                    scores: answer.scores,
                    interpretation: matchedResponse
                } satisfies ResultItem;  // Use satisfies to verify type conformance
            })
            .filter((result): result is ResultItem => result !== null);  // Type guard for the filter
    }
</script>

<div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Survey Results</h1>

    {#if !results.length}
        <div class="text-center p-4">Loading results...</div>
    {:else}
        <div class="space-y-8">
            {#each results as result}
                <div class="bg-white p-6 rounded-lg shadow">
                    <h2 class="font-semibold text-xl mb-4">{result.question}</h2>
                    <div class="mb-2">
                        <p class="font-medium">Your answer:</p>
                        <p class="text-gray-700">{result.response}</p>
                    </div>
                    <div class="mb-4">
                        <p class="font-medium">Scores:</p>
                        <p class="text-gray-600">
                            Pre-Modern: {result.scores[0]}%, 
                            Modern: {result.scores[1]}%, 
                            Post-Modern: {result.scores[2]}%
                        </p>
                    </div>
                    <div>
                        <p class="font-medium">Interpretation:</p>
                        <p class="text-gray-700">{result.interpretation}</p>
                    </div>
                </div>
            {/each}
        </div>

        <div class="mt-8 flex justify-center">
            <button
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                on:click={() => window.history.back()}
            >
                Back to Survey
            </button>
        </div>
    {/if}
</div>