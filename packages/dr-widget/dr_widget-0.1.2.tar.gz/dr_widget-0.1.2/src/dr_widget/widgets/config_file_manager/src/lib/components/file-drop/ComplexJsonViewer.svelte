<script lang="ts">
  import { createElement } from "react";
  import { onDestroy, onMount } from "svelte";

  const { data } = $props<{ data?: unknown }>();

  let container: HTMLDivElement | null = null;
  let root: import("react-dom/client").Root | null = null;
  let JsonTreeCanvas:
    | (typeof import("$lib/react/JsonTreeCanvas"))["JsonTreeCanvas"]
    | null = null;

  const mountReact = async () => {
    const [{ createRoot }, module] = await Promise.all([
      import("react-dom/client"),
      import("$lib/react/JsonTreeCanvas"),
    ]);

    JsonTreeCanvas = module.JsonTreeCanvas;
    if (container) {
      root = createRoot(container);
      root.render(createElement(JsonTreeCanvas, { data }));
    }
  };

  onMount(() => {
    mountReact();
  });

  $effect(() => {
    if (root && JsonTreeCanvas) {
      root.render(createElement(JsonTreeCanvas, { data }));
    }
  });

  onDestroy(() => {
    root?.unmount();
    root = null;
  });
</script>

<div
  class="flex h-96 w-full items-center justify-center overflow-hidden rounded-md border border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950"
>
  <div
    bind:this={container}
    class="h-full w-full"
    aria-label="Complex JSON graph viewer"
  ></div>
</div>

<style>
  :global(.json-tree-placeholder),
  :global(.json-tree-error) {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
    padding: 1.5rem;
    text-align: center;
    color: var(--viewer-muted, rgba(63, 63, 70, 0.7));
  }

  :global(.json-tree-error) {
    color: #ef4444;
  }

  :global(.json-tree-node) {
    fill: #18181b;
    stroke: rgba(63, 63, 70, 0.25);
    stroke-width: 1;
    rx: 12;
    ry: 12;
  }

  :global(.json-tree-node text) {
    font-size: 12px;
    fill: #f4f4f5;
  }

  :global(.json-tree-node--root) {
    fill: #2563eb;
  }

  :global(.json-tree-node--root text) {
    font-weight: 600;
  }

  :global(.json-tree-edge path) {
    stroke: rgba(37, 99, 235, 0.45);
    stroke-width: 1.5;
  }
</style>
