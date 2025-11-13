<script lang="ts">
  import type { BoundFile } from "$lib/hooks/use-file-bindings";
  import SelectedFileRow from "./SelectedFileRow.svelte";

  const {
    files = [],
    onLoad,
    onRemove,
    emptyMessage = "No files selected yet. Use the drop zone above to add some.",
  } = $props<{
    files?: BoundFile[];
    onLoad: (index: number) => void;
    onRemove: (index: number) => void;
    emptyMessage?: string;
  }>();
</script>

{#if files.length > 0}
  <div class="space-y-3">
    {#each files as file, index (file.name + file.size + file.type)}
      <SelectedFileRow
        {file}
        onLoad={() => onLoad(index)}
        onRemove={() => onRemove(index)}
      />
    {/each}
  </div>
{:else}
  <p class="text-sm text-zinc-500 dark:text-zinc-400">{emptyMessage}</p>
{/if}
