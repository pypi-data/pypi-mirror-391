<script lang="ts">
  import { Button } from "$lib/components/ui/button/index.js";
  import { Badge } from "$lib/components/ui/badge/index.js";
  import ConfigViewerPanel from "$lib/components/file-drop/ConfigViewerPanel.svelte";

  const {
    fileName,
    savedAtLabel,
    versionLabel,
    rawContents,
    parsedContents,
    baselineContents,
    dirty,
    onClose,
    onManage,
  } = $props<{
    fileName?: string;
    savedAtLabel?: string;
    versionLabel?: string;
    rawContents?: string;
    parsedContents?: unknown;
    baselineContents?: unknown;
    dirty?: boolean;
    onClose: () => void;
    onManage?: () => void;
  }>();
</script>

<div class="space-y-3 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
  <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
    <div>
      <p class="text-base font-semibold text-zinc-900 dark:text-zinc-100">
        {fileName ?? "Loaded configuration"}
      </p>
      {#if savedAtLabel || versionLabel}
        <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
          {#if savedAtLabel}
            <span>Saved {savedAtLabel}</span>
          {/if}
          {#if versionLabel}
            <Badge variant="secondary" class="px-2 py-0.5 text-[0.65rem]">
              v{versionLabel}
            </Badge>
          {/if}
          {#if dirty}
            <Badge variant="secondary" class="bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-200">
              Unsaved changes
            </Badge>
          {/if}
        </div>
      {/if}
    </div>

    <div class="flex gap-2">
      {#if onManage}
        <Button variant="outline" onclick={onManage}>Manage Configs</Button>
      {/if}
      <Button variant="outline" onclick={onClose}>Close</Button>
    </div>
  </div>

  <ConfigViewerPanel
    data={parsedContents}
    rawJson={rawContents}
    baselineData={baselineContents}
    {dirty}
  />
</div>
