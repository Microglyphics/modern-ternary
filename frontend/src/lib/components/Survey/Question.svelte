<script lang="ts">
  import { surveyStore } from '$lib/stores/surveyStore';
  import type { Question, Response } from '$lib/types/survey';
  
  export let question: Question;
  
  let selected: string | null = null;
  
  surveyStore.subscribe((state) => {
    selected = state.answers[question.id]?.responseId ?? null;
  });
  
  function handleSelect(response: Response) {
    surveyStore.setResponse(
      question.id,
      response.scores
    );
  }
</script>

<div class="question">
  <h2 class="text-xl font-semibold mb-4">{question.text}</h2>
  
  <div class="responses" role="radiogroup" aria-labelledby={`question-${question.id}`}>
    {#each question.responses as response (response.id)}
      <label 
        class="response-option flex items-start p-2 hover:bg-gray-50 rounded"
        class:selected={selected === response.id}
      >
        <input
          type="radio"
          name={`question-${question.id}`}
          value={response.id}
          checked={selected === response.id}
          on:change={() => handleSelect(response)}
          class="mt-1 mr-3"
        />
        <span>{response.text}</span>
      </label>
    {/each}
  </div>
  
  {#if question.required && !selected}
    <p class="text-red-600 text-sm mt-2">This question is required</p>
  {/if}
</div>

<style>
  .question {
    margin-bottom: 2rem;
    padding: 1.5rem;
    border: 1px solid #eee;
    border-radius: 8px;
    background-color: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  h3 {
    margin-bottom: 1.5rem;
    color: #333;
    font-size: 1.1rem;
    font-weight: 500;
  }

  .responses {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .response-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s ease;
  }

  .response-option:hover {
    background-color: #f5f5f5;
  }

  .response-option.selected {
    background-color: #e8f0fe;
  }

  input[type="radio"] {
    margin: 0;
    width: 1.25rem;
    height: 1.25rem;
  }

  .error-message {
    margin-top: 0.5rem;
    color: #dc2626;
    font-size: 0.875rem;
  }
</style>