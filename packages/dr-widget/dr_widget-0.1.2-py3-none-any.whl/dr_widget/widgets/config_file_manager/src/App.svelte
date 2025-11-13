<script>
  import { Separator } from "./lib/components/ui/separator/";
  import ConfigFileManager from "./ConfigFileManager.svelte";

  // Simulate anywidget bindings for testing
  let bindings = $state({
    files: "",
    file_count: 0,
    error: "",
  });
</script>

<main class="mx-auto max-w-5xl p-8 font-sans">
  <div class="flex flex-col gap-8">
    <div class="space-y-2">
      <h1 class="text-3xl font-semibold text-zinc-900 dark:text-zinc-100">
        Widget
      </h1>
    </div>

    <ConfigFileManager {bindings} />

    <div
      class="mt-4 rounded-lg border border-zinc-200 bg-zinc-50 p-6 dark:border-zinc-700 dark:bg-zinc-900"
    >
      <h2 class="text-lg font-medium text-zinc-800 dark:text-zinc-100">
        Debug Output
      </h2>

      <div
        class="mt-4 rounded-md bg-white p-3 text-sm shadow-sm dark:bg-zinc-800"
      >
        <strong class="font-semibold text-zinc-700 dark:text-zinc-200"
          >File Count:</strong
        >
        <span class="ml-2 text-zinc-600 dark:text-zinc-300"
          >{bindings.file_count}</span
        >
      </div>

      <div
        class="mt-4 rounded-md bg-white p-3 text-sm shadow-sm dark:bg-zinc-800"
      >
        <strong class="font-semibold text-zinc-700 dark:text-zinc-200"
          >Files Data:</strong
        >
        <pre
          class="mt-2 overflow-x-auto rounded-md bg-zinc-900/10 p-2 font-mono text-xs dark:bg-zinc-50/10">
{bindings.files || "(empty)"}</pre>
      </div>

      {#if bindings.error}
        <div
          class="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-600 dark:border-red-500/40 dark:bg-red-950/40 dark:text-red-300"
        >
          <strong class="font-semibold">Error:</strong>
          <span class="ml-2">{bindings.error}</span>
        </div>
      {/if}
    </div>
  </div>
</main>
