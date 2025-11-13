<script lang="ts">
  import SimpleJsonViewer from './SimpleJsonViewer.svelte';

  type Primitive = string | number | boolean | null | undefined;
  type DiffStatus = "added" | "removed" | "changed" | "unchanged";

  const {
    data,
    baseline,
    dirty = false,
    diffContext = "unchanged",
    depth = 2,
    currentDepth = 0,
    isLast = true,
  } = $props<{
    data?: unknown;
    baseline?: unknown;
    dirty?: boolean;
    diffContext?: DiffStatus;
    depth?: number;
    currentDepth?: number;
    isLast?: boolean;
  }>();

  let items = $state<string[]>([]);
  let isArray = $state(false);
  let brackets = $state<[string, string]>(["{", "}"]);
  let collapsed = $state(false);
  let diffMeta = $state<
    Record<
      string,
      {
        status: DiffStatus;
        hasCurrent: boolean;
        hasPrevious: boolean;
        currentValue: unknown;
        previousValue: unknown;
      }
    >
  >({});

  const getType = (value: unknown): string => {
    if (value === null) return "null";
    return typeof value;
  };

  const isObjectLike = (value: unknown): value is Record<string, unknown> =>
    typeof value === "object" && value !== null;

  const deepEqual = (a: unknown, b: unknown): boolean => {
    if (a === b) return true;

    if (typeof a !== typeof b) return false;

    if (Array.isArray(a) && Array.isArray(b)) {
      if (a.length !== b.length) return false;
      return a.every((item, index) => deepEqual(item, b[index]));
    }

    if (isObjectLike(a) && isObjectLike(b)) {
      const keysA = Object.keys(a);
      const keysB = Object.keys(b);
      if (keysA.length !== keysB.length) return false;
      return keysA.every((key) => deepEqual(a[key], b[key]));
    }

    return false;
  };

  const hasRemainingCurrentValues = (startIndex: number): boolean => {
    for (let i = startIndex + 1; i < items.length; i += 1) {
      if (diffMeta[items[i]]?.hasCurrent) {
        return true;
      }
    }
    return false;
  };

  const stringify = (value: unknown): string => JSON.stringify(value);

  const formatPrimitive = (value: Primitive): string => {
    const type = getType(value);
    if (type === "string") return stringify(value);
    if (type === "number" || type === "bigint") return String(value);
    if (type === "boolean") return value ? "true" : "false";
    if (value === null) return "null";
    if (value === undefined) return "undefined";
    return String(value);
  };

  const toggleCollapsed = () => {
    collapsed = !collapsed;
  };

  const handleKeyPress = (event: KeyboardEvent) => {
    if (["Enter", " "].includes(event.key)) {
      event.preventDefault();
      toggleCollapsed();
    }
  };

  $effect(() => {
    const source = data ?? baseline;
    const type = getType(source);

    if (type === "object") {
      const currentObj = isObjectLike(data) ? data : undefined;
      const baselineObj = isObjectLike(baseline) ? baseline : undefined;

      const currentKeys = currentObj ? Object.keys(currentObj) : [];
      const baselineKeys = baselineObj ? Object.keys(baselineObj) : [];

      const keySet = new Set([
        ...currentKeys,
        ...(dirty && baselineObj ? baselineKeys : []),
      ]);

      const keys = Array.from(keySet);

      const sortKeys = Array.isArray(source)
        ? (keysToSort: string[]) =>
            keysToSort.sort((a, b) => Number(a) - Number(b))
        : (keysToSort: string[]) =>
            keysToSort.sort((a, b) =>
              a.localeCompare(b, undefined, { numeric: true }),
            );

      sortKeys(keys);

      const meta: typeof diffMeta = {};

      for (const key of keys) {
        const hasCurrent = Boolean(currentObj && key in currentObj);
        const hasPrevious = Boolean(baselineObj && key in baselineObj);
        const currentValue = hasCurrent ? currentObj?.[key] : undefined;
        const previousValue = hasPrevious ? baselineObj?.[key] : undefined;

        let status: DiffStatus = "unchanged";

        if (dirty && baselineObj) {
          if (hasCurrent && !hasPrevious) {
            status = "added";
          } else if (!hasCurrent && hasPrevious) {
            status = "removed";
          } else if (!deepEqual(currentValue, previousValue)) {
            status = "changed";
          }
        }

        meta[key] = {
          status,
          hasCurrent,
          hasPrevious,
          currentValue,
          previousValue,
        };
      }

      items = keys;
      diffMeta = meta;
      isArray = Array.isArray(source);
      brackets = isArray ? ["[", "]"] : ["{", "}"];
    } else {
      items = [];
      isArray = false;
      brackets = ["{", "}"];
      diffMeta = {};
    }
  });

  $effect(() => {
    collapsed = depth < currentDepth;
  });
</script>

{#if data === undefined && (!dirty || baseline === undefined)}
  <div
    class="flex h-80 w-full items-center justify-center rounded-md border border-dashed border-zinc-200 bg-zinc-50 text-sm text-zinc-500 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400"
  >
    <p>No JSON selected.</p>
  </div>
{:else}
  {#if !items.length}
    <span class="_jsonBkt empty" class:isArray={isArray}>
      {brackets[0]}{brackets[1]}
    </span>
    {#if !isLast}
      <span class="_jsonSep">,</span>
    {/if}
  {:else if collapsed}
    <span
      class="_jsonBkt"
      class:isArray={isArray}
      role="button"
      tabindex="0"
      onclick={toggleCollapsed}
      onkeydown={handleKeyPress}
    >{brackets[0]}...{brackets[1]}</span>
    {#if !isLast && collapsed}
      <span class="_jsonSep">,</span>
    {/if}
  {:else}
    <span
      class="_jsonBkt"
      class:isArray={isArray}
      class:diff-block-added={diffContext === "added"}
      class:diff-block-removed={diffContext === "removed"}
      role="button"
      tabindex="0"
      onclick={toggleCollapsed}
      onkeydown={handleKeyPress}
    >{brackets[0]}</span>
    <ul class="_jsonList">
      {#each items as key, idx}
        {@const meta = diffMeta[key]}
        {#if meta}
          {@const currentValue = meta.currentValue}
          {@const previousValue = meta.previousValue}
          {@const valueType = getType(
            meta.hasCurrent ? currentValue : previousValue,
          )}

          <li class:diff-removed-row={meta.status === "removed"}>
            {#if !isArray}
              <span
                class="_jsonKey"
                class:diff-removed-text={meta.status === "removed"}
              >
                {stringify(key)}
              </span>
              <span class="_jsonSep">:</span>
            {/if}

            {#if (meta.hasCurrent ? getType(currentValue) : getType(previousValue)) ===
            "object"}
              <SimpleJsonViewer
                data={meta.hasCurrent ? currentValue : undefined}
                baseline={meta.hasPrevious ? previousValue : undefined}
                {depth}
                dirty={dirty}
                diffContext={meta.status}
                currentDepth={currentDepth + 1}
                isLast={!hasRemainingCurrentValues(idx)}
              />
              {#if meta.hasCurrent && hasRemainingCurrentValues(idx)}
                <span class="_jsonSep">,</span>
              {/if}
            {:else if meta.hasCurrent}
              <span
                class="_jsonVal {getType(currentValue)}"
                class:diff-added={meta.status === "added" || meta.status === "changed"}
              >
                {formatPrimitive(currentValue as Primitive)}
              </span>
              {#if meta.status === "changed" && meta.hasPrevious}
                <span class="diff-previous-label">Updated from</span>
                <span class="_jsonVal {getType(previousValue)} diff-removed">
                  {formatPrimitive(previousValue as Primitive)}
                </span>
              {/if}
              {#if meta.hasCurrent && hasRemainingCurrentValues(idx)}
                <span class="_jsonSep">,</span>
              {/if}
            {:else if meta.hasPrevious}
              <span class="_jsonVal {valueType} diff-removed">
                {formatPrimitive(previousValue as Primitive)}
              </span>
              <span class="diff-previous-label">Removed</span>
            {/if}
          </li>
        {/if}
      {/each}
    </ul>
    <span
      class="_jsonBkt"
      class:isArray={isArray}
      class:diff-block-added={diffContext === "added"}
      class:diff-block-removed={diffContext === "removed"}
      role="button"
      tabindex="0"
      onclick={toggleCollapsed}
      onkeydown={handleKeyPress}
    >{brackets[1]}</span>
    {#if !isLast && diffContext !== "removed"}
      <span class="_jsonSep">,</span>
    {/if}
  {/if}
{/if}

<style>
  :global(.dark) {
    --jsonBracketHoverBackground: rgba(63, 63, 70, 0.4);
    --jsonBorderLeft: 1px dashed rgba(63, 63, 70, 0.6);
    --jsonValColor: rgba(228, 228, 231, 0.8);
  }

  :where(._jsonList) {
    list-style: none;
    margin: 0;
    padding: 0;
    padding-left: var(--jsonPaddingLeft, 1rem);
    border-left: var(--jsonBorderLeft, 1px dotted);
  }

  :where(._jsonBkt) {
    color: var(--jsonBracketColor, currentcolor);
    border-radius: 0.25rem;
    padding: 0.1rem 0.25rem;
  }

  :where(._jsonBkt):not(.empty):hover,
  :where(._jsonBkt):focus-visible {
    cursor: pointer;
    outline: none;
    background: var(--jsonBracketHoverBackground, #e5e7eb);
  }

  :where(._jsonSep) {
    color: var(--jsonSeparatorColor, currentcolor);
  }

  :where(._jsonKey) {
    color: var(--jsonKeyColor, currentcolor);
    margin-right: 0.35rem;
  }

  :where(._jsonVal) {
    color: var(--jsonValColor, #9ca3af);
  }

  :where(._jsonVal).string {
    color: var(--jsonValStringColor, #059669);
  }

  :where(._jsonVal).number {
    color: var(--jsonValNumberColor, #d97706);
  }

  :where(._jsonVal).boolean {
    color: var(--jsonValBooleanColor, #2563eb);
  }

  :where(.diff-added) {
    background: var(--jsonDiffAddedBg, rgba(34, 197, 94, 0.14));
    color: var(--jsonDiffAddedColor, #166534);
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
  }

  :where(.diff-removed) {
    background: var(--jsonDiffRemovedBg, rgba(239, 68, 68, 0.16));
    color: var(--jsonDiffRemovedColor, #b91c1c);
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    text-decoration: line-through;
  }

  .diff-removed-text {
    color: var(--jsonDiffRemovedColor, #b91c1c);
  }

  .diff-removed-row {
    display: flex;
    align-items: baseline;
    gap: 0.35rem;
  }

  .diff-previous-label {
    margin-left: 0.35rem;
    margin-right: 0.25rem;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--jsonDiffLabelColor, #52525b);
  }

  .diff-block-added {
    background: var(--jsonDiffAddedBg, rgba(34, 197, 94, 0.08));
  }

  .diff-block-removed {
    background: var(--jsonDiffRemovedBg, rgba(239, 68, 68, 0.08));
  }

  :global(.dark) :where(.diff-added) {
    background: rgba(34, 197, 94, 0.24);
    color: #bbf7d0;
  }

  :global(.dark) :where(.diff-removed) {
    background: rgba(239, 68, 68, 0.22);
    color: #fecaca;
  }

  :global(.dark) .diff-previous-label {
    color: #a1a1aa;
  }

  :global(.dark) .diff-block-added {
    background: rgba(34, 197, 94, 0.18);
  }

  :global(.dark) .diff-block-removed {
    background: rgba(239, 68, 68, 0.18);
  }
</style>
