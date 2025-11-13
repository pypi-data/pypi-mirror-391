<!--
	Installed from @ieedan/shadcn-svelte-extras
-->

<script lang="ts">
	import { useModalSub } from './modal.svelte.js';
	import * as Dialog from '../dialog/index.js';
	import * as Drawer from '../drawer/index.js';
	import type { DialogDescriptionProps } from 'bits-ui';

	const modal = useModalSub();

	let { ref = $bindable(null), ...rest }: DialogDescriptionProps = $props();
</script>

{#if modal.view === 'desktop'}
	<Dialog.Description bind:ref {...rest} />
{:else}
	<Drawer.Description bind:ref {...rest} />
{/if}
