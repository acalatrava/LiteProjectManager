<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/services/api";
    import type { Sample } from "$lib/types/sample";
    import type { SearchResult } from "$lib/types/sample";
    import { _ } from "svelte-i18n";

    let samples: Sample[] = [];
    let newSampleInfo = "";
    let searchTerm = "";
    let searchResults: SearchResult[] = [];
    let error = "";
    let loading = false;
    let searchLoading = false;
    let addLoading = false;

    onMount(async () => {
        await loadSamples();
    });

    async function loadSamples() {
        loading = true;
        error = "";
        try {
            samples = await api.getSamples();
        } catch (err) {
            error = "Failed to load samples";
            console.error(err);
        } finally {
            loading = false;
        }
    }

    async function handleSearch() {
        if (!searchTerm.trim()) return;

        searchLoading = true;
        error = "";
        try {
            searchResults = await api.search(searchTerm);
        } catch (err) {
            error = "Search failed";
            console.error(err);
        } finally {
            searchLoading = false;
        }
    }

    async function handleAddSample() {
        if (!newSampleInfo.trim()) return;

        addLoading = true;
        error = "";
        try {
            await api.addSample(newSampleInfo);
            newSampleInfo = "";
            await loadSamples();
        } catch (err) {
            error = "Failed to add sample";
            console.error(err);
        } finally {
            addLoading = false;
        }
    }

    async function handleDeleteSample(id: string) {
        if (!confirm($_("dashboard.samples.deleteConfirm"))) return;

        error = "";
        try {
            await api.deleteSample(id);
            samples = samples.filter((s) => s.id !== id);
        } catch (err) {
            error = $_("dashboard.errors.deleteFailed");
            console.error(err);
        }
    }
</script>

<div class="py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 class="text-2xl font-semibold text-gray-900">
            {$_("common.dashboard")}
        </h1>

        <div class="mt-6 grid gap-6 lg:grid-cols-2">
            <!-- Add Sample Section -->
            <div class="bg-white shadow rounded-lg p-6">
                <h2 class="text-lg font-medium text-gray-900">
                    {$_("dashboard.addSample.title")}
                </h2>
                <form on:submit|preventDefault={handleAddSample} class="mt-4">
                    <div>
                        <label for="sampleInfo" class="sr-only"
                            >{$_("dashboard.addSample.title")}</label
                        >
                        <textarea
                            id="sampleInfo"
                            bind:value={newSampleInfo}
                            rows="3"
                            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                            placeholder={$_("dashboard.addSample.placeholder")}
                        ></textarea>
                    </div>
                    <div class="mt-4">
                        <button
                            type="submit"
                            disabled={addLoading}
                            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {#if addLoading}
                                <svg
                                    class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                >
                                    <circle
                                        class="opacity-25"
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        stroke-width="4"
                                    ></circle>
                                    <path
                                        class="opacity-75"
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                    ></path>
                                </svg>
                                {$_("dashboard.addSample.adding")}
                            {:else}
                                {$_("dashboard.addSample.button")}
                            {/if}
                        </button>
                    </div>
                </form>
            </div>

            <!-- Search Section -->
            <div class="bg-white shadow rounded-lg p-6">
                <h2 class="text-lg font-medium text-gray-900">
                    {$_("dashboard.search.title")}
                </h2>
                <div class="mt-4">
                    <div class="flex gap-4">
                        <input
                            type="text"
                            bind:value={searchTerm}
                            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                            placeholder={$_("dashboard.search.placeholder")}
                        />
                        <button
                            on:click={handleSearch}
                            disabled={searchLoading}
                            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {#if searchLoading}
                                <svg
                                    class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                >
                                    <circle
                                        class="opacity-25"
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        stroke-width="4"
                                    ></circle>
                                    <path
                                        class="opacity-75"
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                    ></path>
                                </svg>
                            {:else}
                                {$_("dashboard.search.button")}
                            {/if}
                        </button>
                    </div>

                    {#if searchResults.length > 0}
                        <div class="mt-4">
                            <h3 class="text-sm font-medium text-gray-500">
                                {$_("dashboard.search.results")}
                            </h3>
                            <ul class="mt-2 divide-y divide-gray-200">
                                {#each searchResults as result}
                                    <li class="py-3">
                                        <p class="text-sm text-gray-900">
                                            {result.content}
                                        </p>
                                    </li>
                                {/each}
                            </ul>
                        </div>
                    {/if}
                </div>
            </div>
        </div>

        <!-- Samples List -->
        <div class="mt-6">
            <h2 class="text-lg font-medium text-gray-900">
                {$_("dashboard.samples.title")}
            </h2>

            {#if error}
                <div class="mt-4 rounded-md bg-red-50 p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg
                                class="h-5 w-5 text-red-400"
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm font-medium text-red-800">
                                {error}
                            </p>
                        </div>
                    </div>
                </div>
            {/if}

            {#if loading}
                <div class="mt-4 flex justify-center">
                    <svg
                        class="animate-spin h-8 w-8 text-primary-600"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <circle
                            class="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            stroke-width="4"
                        ></circle>
                        <path
                            class="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                    </svg>
                </div>
            {:else if samples.length === 0}
                <p class="mt-4 text-sm text-gray-500">
                    {$_("dashboard.samples.empty")}
                </p>
            {:else}
                <div class="mt-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {#each samples as sample (sample.id)}
                        <div class="bg-white overflow-hidden shadow rounded-lg">
                            <div class="p-5">
                                <p class="text-sm text-gray-900">
                                    {sample.info}
                                </p>
                                <div
                                    class="mt-4 flex items-center justify-between text-sm"
                                >
                                    <span class="text-gray-500"
                                        >{new Date(
                                            sample.date,
                                        ).toLocaleDateString()}</span
                                    >
                                    <button
                                        on:click={() =>
                                            handleDeleteSample(sample.id)}
                                        class="text-red-600 hover:text-red-900"
                                    >
                                        {$_("dashboard.samples.deleteButton")}
                                    </button>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>
