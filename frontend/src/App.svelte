<script>
  import { onMount } from 'svelte';
  let version = '1.0.0'; // We'll fetch this from the API later
</script>

<main>
  <div class="container">
    <h1>Modernity Worldview Survey</h1>
    <!-- Router view will go here later -->
    <slot></slot>
  </div>
</main>

<footer>
  <p>Survey Version: {version}</p>
</footer>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

  h1 {
    color: #333;
    text-align: center;
    margin-bottom: 2rem;
  }

  footer {
    text-align: center;
    padding: 1rem;
    font-size: 0.8rem;
    color: #666;
    position: fixed;
    bottom: 0;
    width: 100%;
    background: white;
    border-top: 1px solid #eee;
  }
</style>