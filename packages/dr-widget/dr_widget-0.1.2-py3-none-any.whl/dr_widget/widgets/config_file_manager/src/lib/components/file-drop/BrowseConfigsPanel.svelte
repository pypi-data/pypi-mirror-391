<script lang="ts">
  import * as Card from "$lib/components/ui/card/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import { FileDropZone, displaySize } from "$lib/components/ui/file-drop-zone";
  import { Badge } from "$lib/components/ui/badge/index.js";
  import ConfigViewerPanel from "$lib/components/file-drop/ConfigViewerPanel.svelte";
  import type { FileDropZoneProps } from "$lib/components/ui/file-drop-zone";
  import type { BoundFile } from "$lib/hooks/use-file-bindings";
  import { X } from "@lucide/svelte";

  const {
    file,
    rawContents,
    parsedContents,
    baselineContents,
    savedAtLabel,
    versionLabel,
    dirty,
    error,
    maxFiles,
    onUpload,
    onFileRejected,
    onRemove,
    onLoad,
    disableLoad,
  } = $props<{
    file?: BoundFile;
    rawContents?: string;
    parsedContents?: unknown;
    baselineContents?: unknown;
    savedAtLabel?: string;
    versionLabel?: string;
    dirty?: boolean;
    error?: string;
    maxFiles: number;
    onUpload: FileDropZoneProps["onUpload"];
    onFileRejected?: FileDropZoneProps["onFileRejected"];
    onRemove: () => void;
    onLoad: () => void;
    disableLoad?: boolean;
  }>();
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>Browse Configs</Card.Title>
    <Card.Description>
      Select a config file to view before loading.
    </Card.Description>
  </Card.Header>
  <Card.Content>
    <div class="space-y-4">
      {#if !file}
        <FileDropZone
          {maxFiles}
          fileCount={file ? 1 : 0}
          onUpload={onUpload}
          onFileRejected={onFileRejected}
        />
      {:else}
        <div class="space-y-3">
          <div
            class="flex items-center justify-between rounded-lg border border-zinc-200 bg-white p-3 text-sm shadow-sm dark:border-zinc-700 dark:bg-zinc-900"
          >
            <div>
              <p class="font-medium text-zinc-800 dark:text-zinc-100">{file.name}</p>
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
                  <span>{displaySize(file.size)}</span>
                </div>
              {:else}
                <p class="text-xs text-zinc-500 dark:text-zinc-400">
                  {displaySize(file.size)} · {file.type || "unknown type"}
                </p>
              {/if}
            </div>

            <div class="flex gap-2">
              <Button
                variant="ghost"
                class="w-30 bg-slate-50 shadow-sm"
                onclick={onLoad}
                disabled={!rawContents || disableLoad}
              >
                {disableLoad ? "Loaded" : "Load"}
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

          <ConfigViewerPanel
            data={parsedContents}
            rawJson={rawContents}
            baselineData={baselineContents}
            {dirty}
          />
        </div>
      {/if}

      {#if error}
        <div
          class="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-600 dark:border-red-500/40 dark:bg-red-950/40 dark:text-red-200"
        >
          <strong class="font-semibold">Upload error:</strong>
          <span class="ml-2">{error}</span>
        </div>
      {/if}
    </div>
  </Card.Content>
</Card.Root>
