<script lang="ts">
  import { Button } from "$lib/components/ui/button/index.js";
  import { displaySize } from "$lib/components/ui/file-drop-zone";
  import type { BoundFile } from "$lib/hooks/use-file-bindings";
  import { X } from "@lucide/svelte";

  const { file, onLoad, onRemove } = $props<{
    file: BoundFile;
    onLoad: () => void;
    onRemove: () => void;
  }>();
</script>

<div
  class="flex items-center justify-between rounded-lg border border-zinc-200 bg-white p-3 text-sm shadow-sm dark:border-zinc-700 dark:bg-zinc-900"
>
  <div>
    <p class="font-medium text-zinc-800 dark:text-zinc-100">{file.name}</p>
    <p class="text-xs text-zinc-500 dark:text-zinc-400">
      {displaySize(file.size)} · {file.type || "unknown type"}
    </p>
  </div>

  <div class="flex gap-2">
    <Button variant="ghost" class="w-30 bg-slate-50 shadow-sm" onclick={onLoad}>
      Load
    </Button>
    <Button
      variant="ghost"
      size="icon"
      class="bg-red-100 shadow-sm"
      onclick={onRemove}
    >
      <span class="sr-only">Remove</span>
      <X class="size-4" />
    </Button>
  </div>
</div>
