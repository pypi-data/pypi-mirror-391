<script lang="ts">
  import * as Tabs from "$lib/components/ui/tabs/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import { Badge } from "$lib/components/ui/badge/index.js";

  import BrowseConfigsPanel from "$lib/components/file-drop/BrowseConfigsPanel.svelte";
  import LoadedConfigPreview from "$lib/components/file-drop/LoadedConfigPreview.svelte";
  import SaveConfigPanel from "$lib/components/file-drop/SaveConfigPanel.svelte";
  import {
    createFileBindingHandlers,
    type BoundFile,
    type FileBinding,
  } from "$lib/hooks/use-file-bindings";

const { bindings } = $props<{
  bindings: FileBinding;
}>();

const maxFiles = 1;
let lastWrittenCurrentState = $state<string | undefined | null>(undefined);
let lastWrittenBaselineState = $state<string | undefined | null>(undefined);
let lastWrittenVersion = $state<string | undefined | null>(undefined);
let lastWrittenConfigFile = $state<string | undefined | null>(undefined);

const writeCurrentStateCallback = (contents?: string | null) => {
  lastWrittenCurrentState = contents;
};

const writeBaselineStateCallback = (contents?: string | null) => {
  lastWrittenBaselineState = contents;
};

const writeVersionCallback = (version?: string | null) => {
  lastWrittenVersion = version;
};

const writeConfigFileCallback = (path?: string | null) => {
  lastWrittenConfigFile = path;
};

const bindingHandlers = createFileBindingHandlers({
  bindings,
  maxFiles,
  writeCurrentStateCallback,
  writeBaselineStateCallback,
  writeVersionCallback,
  writeConfigFileCallback,
});

const parseJsonObject = (value?: string | null) => {
  if (!value) return undefined;
  try {
    const parsed = JSON.parse(value);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>;
    }
  } catch {
    return undefined;
  }
  return undefined;
};

const canonicalizeState = (value?: string | null) => {
  const parsed = parseJsonObject(value);
  if (parsed) {
    try {
      return JSON.stringify(parsed);
    } catch {
      return (value ?? "").trim();
    }
  }
  return (value ?? "").trim();
};

type NormalizedConfig = {
  data: Record<string, unknown>;
  version?: string;
  savedAt?: string;
};

const normalizeConfigPayload = (payload: Record<string, unknown>): NormalizedConfig => {
  let data: Record<string, unknown> | undefined;

  const payloadData = payload["data"];
  if (payloadData && typeof payloadData === "object" && !Array.isArray(payloadData)) {
    data = payloadData as Record<string, unknown>;
  } else if (
    payload["selections"] &&
    typeof payload["selections"] === "object" &&
    !Array.isArray(payload["selections"])
  ) {
    data = { selections: payload["selections"] as Record<string, unknown> };
  } else {
    const fallback: Record<string, unknown> = {};
    Object.entries(payload).forEach(([key, value]) => {
      if (key === "version" || key === "saved_at") {
        return;
      }
      fallback[key] = value;
    });
    data = fallback;
  }

  const versionValue = payload["version"];
  let version: string | undefined;
  if (typeof versionValue === "string" && versionValue) {
    version = versionValue;
  } else if (typeof versionValue === "number") {
    version = String(versionValue);
  }

  const savedAtValue = payload["saved_at"];
  let savedAt: string | undefined;
  if (typeof savedAtValue === "string" && savedAtValue) {
    savedAt = savedAtValue;
  }

  return {
    data: data ?? {},
    version,
    savedAt,
  };
};

let lastSavedAt = $state<string | undefined>(undefined);

const parsedFiles = $derived(bindingHandlers.readBoundFiles());
const baselineParsed = $derived.by(() => parseJsonObject(bindings.baseline_state));
const isDirty = $derived.by(
  () => canonicalizeState(bindings.current_state) !== canonicalizeState(bindings.baseline_state),
);
const selectedConfigVersion = $derived.by(() => bindings.version ?? "");
const canEditSelectedConfigVersion = $derived.by(() => Boolean(bindings.current_state && bindings.current_state.trim().length > 0));

  const formatSavedAt = (value: unknown): string | undefined => {
    if (typeof value === "string" && value) {
      const parsed = new Date(value);
      if (!Number.isNaN(parsed.getTime())) {
        return new Intl.DateTimeFormat(undefined, {
          year: "numeric",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }).format(parsed);
      }
      return value;
    }
    return undefined;
  };

let previewFile = $state<BoundFile | undefined>(undefined);
let previewText = $state<string | undefined>(bindings.current_state ?? undefined);
let previewJson = $state<unknown | undefined>(() => {
  if (!bindings.current_state) return undefined;
  try {
    return JSON.parse(bindings.current_state);
  } catch {
    return undefined;
  }
});
const normalizedPreviewData = $derived.by(() => {
  if (!previewJson || typeof previewJson !== "object") return undefined;
  const normalized = normalizeConfigPayload(previewJson as Record<string, unknown>);
  return JSON.stringify(normalized.data, null, 2);
});
  let managerOpen = $state(false);
  let activeTab = $state("find");
  let lastLoadedFileName = $state<string | undefined>(undefined);
  let loadedConfigSummary = $state<
    | {
        name?: string;
        savedAt?: string;
        version?: string;
        rawText?: string;
        parsed?: unknown;
      }
    | undefined
  >(undefined);
  let showLoadedPreview = $state(false);
  let previewFromLoaded = $state(false);
  let loadedConfigPath = $state<string | undefined>(undefined);

  const handleSaveSuccess = ({
    fileName,
    timestamp,
  }: {
    fileName?: string;
    timestamp: string;
  }) => {
    const raw = bindings.current_state;

    if (fileName) {
      bindingHandlers.writeConfigFile(fileName);
      loadedConfigPath = fileName;
      lastLoadedFileName = fileName;
    }

    bindingHandlers.writeBaselineState(raw ?? "");
    lastSavedAt = timestamp;

    const formattedSavedAt = formatSavedAt(timestamp) ?? timestamp;

    let parsed: unknown;
    if (raw) {
      try {
        parsed = JSON.parse(raw);
      } catch {
        parsed = loadedConfigSummary?.parsed;
      }
    }

    loadedConfigSummary = {
      name: fileName ?? loadedConfigSummary?.name ?? "Config saved",
      savedAt: formattedSavedAt,
      version: bindings.version ?? loadedConfigSummary?.version,
      rawText: raw ?? loadedConfigSummary?.rawText,
      parsed: parsed ?? loadedConfigSummary?.parsed,
    };

    previewFromLoaded = false;
    showLoadedPreview = false;
    bindingHandlers.writeError("");
  };


  const handleSaveError = (message: string) => {
    bindingHandlers.writeError(message);
  };

  const computeByteSize = (input: string): number => {
    if (typeof TextEncoder !== "undefined") {
      return new TextEncoder().encode(input).byteLength;
    }
    return input.length;
  };

  const resetPreviewState = () => {
    previewFile = undefined;
    previewText = undefined;
    previewJson = undefined;
  };

  // previewText
  $effect(() => {
    if (!previewText) {
      previewJson = undefined;
      return;
    }

    try {
      previewJson = JSON.parse(previewText);
    } catch {
      previewJson = undefined;
    }
  });

  // parsedFiles, previewFile, previewFromLoaded
  $effect(() => {
    if (parsedFiles.length === 0 && previewFile && !previewFromLoaded) {
      resetPreviewState();
    }
  });

  const previewSavedAt = $derived.by(() => {
    if (!previewJson || typeof previewJson !== "object") return undefined;
    return formatSavedAt((previewJson as Record<string, unknown>)["saved_at"]);
  });

  const previewVersion = $derived.by(() => {
    if (!previewJson || typeof previewJson !== "object") return undefined;
    const value = (previewJson as Record<string, unknown>)["version"];
    if (typeof value === "string" && value) return value;
    if (typeof value === "number") return String(value);
    return undefined;
  });

  const handleSelectedVersionChange = (nextVersion: string) => {
    const trimmed = nextVersion.trim();
    if (!trimmed) {
      bindingHandlers.writeVersion("");
      return;
    }
    bindingHandlers.writeVersion(trimmed);
  };

  // managerOpen, isDirty
  $effect(() => {
    if (!managerOpen) return;
    activeTab = isDirty ? "save" : "find";
  });

  // current_state sync
  $effect(() => {
    if (lastWrittenCurrentState !== bindings.current_state) {
      bindingHandlers.writeCurrentState(bindings.current_state);
    }
  });

  // baseline_state sync
  $effect(() => {
    if (lastWrittenBaselineState !== bindings.baseline_state) {
      bindingHandlers.writeBaselineState(bindings.baseline_state);
    }
  });

  // version sync
  $effect(() => {
    if (lastWrittenVersion !== bindings.version) {
      bindingHandlers.writeVersion(bindings.version);
    }
  });

  // config_file sync
  $effect(() => {
    if (lastWrittenConfigFile !== bindings.config_file) {
      bindingHandlers.writeConfigFile(bindings.config_file);
    }
  });

  // current_state and metadata summary
  $effect(() => {
    const raw = bindings.current_state;
    if (!raw || raw.trim().length === 0) {
      loadedConfigSummary = undefined;
      previewFromLoaded = false;
      showLoadedPreview = false;
      lastLoadedFileName = undefined;
      loadedConfigPath = undefined;
      lastSavedAt = undefined;
      if (!managerOpen) {
        resetPreviewState();
      }
      return;
    }

    let parsed: unknown;
    try {
      parsed = JSON.parse(raw);
    } catch {
      parsed = undefined;
    }

    const savedAtLabel = lastSavedAt ? formatSavedAt(lastSavedAt) : undefined;

    loadedConfigSummary = {
      name: bindings.config_file || lastLoadedFileName || loadedConfigSummary?.name || "Config loaded",
      savedAt: savedAtLabel,
      version: bindings.version ?? undefined,
      rawText: raw,
      parsed,
    };

    if (!previewFromLoaded && !managerOpen) {
      previewText = raw;
      previewJson = parsed;
    }
  });

  const handleUpload = async (files: File[]) => {
    const [file] = files;
    if (!file) return;

    const fileText = await file.text();

    await bindingHandlers.handleUpload([file]);

    previewFile = {
      name: file.name,
      size: file.size,
      type: file.type,
    };
    previewText = fileText;
    bindingHandlers.writeError("");
    previewFromLoaded = false;
  };

  const handleRemove = () => {
    if (previewFromLoaded) {
      bindingHandlers.writeCurrentState("");
      bindingHandlers.writeBaselineState("");
      bindingHandlers.writeVersion("");
      bindingHandlers.writeConfigFile("");
      lastSavedAt = undefined;
      loadedConfigSummary = undefined;
      previewFromLoaded = false;
      showLoadedPreview = false;
      lastLoadedFileName = undefined;
      loadedConfigPath = undefined;
      bindingHandlers.writeError("");
      resetPreviewState();
      return;
    }

    if (parsedFiles.length > 0) {
      bindingHandlers.removeFile(0);
    }
    bindingHandlers.writeError("");
    resetPreviewState();
    loadedConfigPath = undefined;
  };

  const handleLoadConfig = () => {
    if (!previewText) {
      bindingHandlers.writeError("Unable to load config: missing file contents.");
      return;
    }

    lastLoadedFileName = previewFile?.name ?? lastLoadedFileName;
    const summaryName = lastLoadedFileName ?? previewFile?.name ?? "Config loaded";

    let parsedFile: unknown;
    try {
      parsedFile = JSON.parse(previewText);
    } catch {
      bindingHandlers.writeError("Config is not valid JSON.");
      return;
    }

    if (!parsedFile || typeof parsedFile !== "object" || Array.isArray(parsedFile)) {
      bindingHandlers.writeError("Config must be a JSON object.");
      return;
    }

    const normalized = normalizeConfigPayload(parsedFile as Record<string, unknown>);
    const dataJson = JSON.stringify(normalized.data, null, 2);

    bindingHandlers.writeCurrentState(dataJson);
    bindingHandlers.writeBaselineState(dataJson);
    if (normalized.version) {
      bindingHandlers.writeVersion(normalized.version);
    }
    if (summaryName) {
      bindingHandlers.writeConfigFile(summaryName);
    }

    lastSavedAt = normalized.savedAt;

    loadedConfigSummary = {
      name: summaryName,
      savedAt: normalized.savedAt ? formatSavedAt(normalized.savedAt) : undefined,
      version: normalized.version,
      rawText: dataJson,
      parsed: normalized.data,
    };
    loadedConfigPath = summaryName;

    if (parsedFiles.length > 0) {
      bindingHandlers.removeFile(0);
    }

    bindingHandlers.writeError("");
    resetPreviewState();
    managerOpen = false;
    showLoadedPreview = false;
    previewFromLoaded = false;
  };

  // managerOpen
  $effect(() => {
    if (managerOpen) {
      showLoadedPreview = false;

      if (!previewFile && loadedConfigSummary?.rawText) {
        previewFromLoaded = true;
        previewText = loadedConfigSummary.rawText;
        previewFile = {
          name: loadedConfigSummary.name ?? "Loaded config",
          size: computeByteSize(loadedConfigSummary.rawText),
          type: "application/json",
        };
        previewJson = loadedConfigSummary.parsed;
      }
    } else if (previewFromLoaded) {
      resetPreviewState();
      previewFromLoaded = false;
    }
  });

  const isLoadedConfigCurrent = $derived.by(() => {
    if (!loadedConfigSummary?.rawText) return false;
    const candidate = normalizedPreviewData ?? previewText;
    if (!candidate) return false;
    return candidate.trim() === loadedConfigSummary.rawText.trim();
  });
</script>

<div class="space-y-6">
  {#if managerOpen}
    <div class="space-y-4 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p class="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
            Manage Configs
          </p>
          <p class="text-sm text-zinc-500 dark:text-zinc-400">
            Load a JSON config or prepare a notebook save.
          </p>
        </div>
        <Button variant="outline" onclick={() => (managerOpen = false)}>
          Close
        </Button>
      </div>

      <Tabs.Root bind:value={activeTab}>
        <Tabs.List>
          <Tabs.Trigger value="find">Browse Configs</Tabs.Trigger>
          <Tabs.Trigger value="save">Save Config</Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="find">
          <BrowseConfigsPanel
            file={previewFile}
            rawContents={previewText}
            parsedContents={previewJson}
            baselineContents={baselineParsed}
            savedAtLabel={previewSavedAt}
            versionLabel={previewVersion}
            dirty={isDirty}
            error={bindings.error}
            maxFiles={maxFiles}
            onUpload={handleUpload}
            onFileRejected={bindingHandlers.handleFileRejected}
            onRemove={handleRemove}
            onLoad={handleLoadConfig}
            disableLoad={isLoadedConfigCurrent}
          />
        </Tabs.Content>

        <Tabs.Content value="save">
          <SaveConfigPanel
            rawConfig={bindings.current_state}
            baselineConfig={baselineParsed}
            defaultFileName={
              bindings.config_file || loadedConfigPath || lastLoadedFileName || "config.json"
            }
            dirty={isDirty}
            currentVersion={selectedConfigVersion}
            canEditVersion={canEditSelectedConfigVersion}
            onSaveSuccess={handleSaveSuccess}
            onSaveError={handleSaveError}
            onVersionChange={handleSelectedVersionChange}
          />
        </Tabs.Content>
      </Tabs.Root>
    </div>
  {:else if showLoadedPreview && loadedConfigSummary?.rawText}
    <LoadedConfigPreview
      fileName={loadedConfigSummary.name}
      savedAtLabel={loadedConfigSummary.savedAt}
      versionLabel={loadedConfigSummary.version}
      rawContents={loadedConfigSummary.rawText}
      parsedContents={loadedConfigSummary.parsed}
      baselineContents={baselineParsed}
      dirty={isDirty}
      onClose={() => (showLoadedPreview = false)}
      onManage={() => {
        showLoadedPreview = false;
        managerOpen = true;
      }}
    />
  {:else}
    <div
      class="flex flex-col gap-3 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
    >
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div class="space-y-1">
          <p class="text-sm font-medium text-zinc-500 dark:text-zinc-400">
            Configuration
          </p>
          {#if loadedConfigSummary}
            <p class="text-base font-semibold text-zinc-900 dark:text-zinc-100">
              {bindings.config_file || loadedConfigSummary.name}
            </p>
            {#if loadedConfigSummary.savedAt || bindings.version}
              <div class="flex flex-wrap items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
                {#if loadedConfigSummary.savedAt}
                  <span>Saved {loadedConfigSummary.savedAt}</span>
                {/if}
                {#if bindings.version}
                  <Badge variant="secondary" class="px-2 py-0.5 text-[0.65rem]">
                    v{bindings.version}
                  </Badge>
                {/if}
                {#if isDirty}
                  <Badge variant="secondary" class="bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-200">
                    Unsaved changes
                  </Badge>
                {/if}
              </div>
            {/if}
          {:else}
            <p class="text-base text-zinc-600 dark:text-zinc-300">
              No config loaded.
            </p>
          {/if}
        </div>

        <div class="flex gap-2">
          <Button variant="outline" onclick={() => (managerOpen = true)}>
            Manage Configs
          </Button>
          {#if loadedConfigSummary?.rawText}
            <Button
              variant="outline"
              disabled={!loadedConfigSummary?.rawText}
              onclick={() => (showLoadedPreview = true)}
            >
              View Config
            </Button>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>
