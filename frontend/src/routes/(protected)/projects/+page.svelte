<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/services/api";
    import type { Project } from "$lib/types/project";
    import { _ } from "svelte-i18n";
    import { fade, fly } from "svelte/transition";
    import { Functions } from "$lib/services/functions";
    import { user } from "$lib/stores/auth";

    let projects: Project[] = [];
    let loading = true;
    let error = "";
    let showCreateModal = false;
    let newProject = {
        name: "",
        description: "",
        start_date: new Date().toISOString().split("T")[0] + "T08:00:00Z",
        deadline:
            new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
                .toISOString()
                .split("T")[0] + "T12:00:00Z",
    };

    onMount(async () => {
        await loadProjects();
    });

    async function loadProjects() {
        loading = true;
        error = "";
        try {
            projects = await api.getProjects();
        } catch (err) {
            error = "Failed to load projects";
            console.error(err);
        } finally {
            loading = false;
        }
    }

    function getProgressColor(project: Project) {
        const progress = getProgress(project);

        if (progress >= 100) return "bg-emerald-500";
        if (progress >= 70) return "bg-lime-500";
        if (progress >= 30) return "bg-amber-500";
        return "bg-rose-500";
    }

    function getProgress(project: Project) {
        if (!project?.tasks?.length) return 0;

        const completedTasks = project.tasks.filter(
            (task) => task.status === "completed",
        ).length;

        return Math.round((completedTasks / project.tasks.length) * 100);
    }

    async function handleDeleteProject(id: string) {
        if (!confirm($_("projects.confirmDeleteProject"))) return;

        error = "";
        try {
            await api.deleteProject(id);
            projects = projects.filter((p) => p.id !== id);
        } catch (err) {
            error = $_("projects.errors.deleteFailed");
            console.error(err);
        }
    }

    async function handleCreateProject(event: Event) {
        event.preventDefault();
        error = "";

        try {
            await api.createProject({
                ...newProject,
                start_date: new Date(newProject.start_date).toISOString(),
                deadline: new Date(newProject.deadline).toISOString(),
            });
            showCreateModal = false;
            await loadProjects();

            // Reset form
            newProject = {
                name: "",
                description: "",
                start_date:
                    new Date().toISOString().split("T")[0] + "T08:00:00Z",
                deadline:
                    new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
                        .toISOString()
                        .split("T")[0] + "T12:00:00Z",
            };
        } catch (err) {
            error = $_("projects.errors.createFailed");
            console.error(err);
        }
    }
</script>

<div class="space-y-8">
    <!-- Header with modern design -->
    <div
        class="relative overflow-hidden rounded-xl bg-gradient-to-r from-primary-600 to-primary-800 p-8 shadow-lg"
    >
        <div class="absolute inset-0 bg-grid-white/10"></div>
        <div class="relative">
            <div class="sm:flex sm:items-center sm:justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-white">
                        {$_("common.projects")}
                    </h1>
                    <p class="mt-2 text-lg text-primary-100 max-w-xl">
                        {$_("projects.description")}
                    </p>
                </div>
                <button
                    on:click={() => (showCreateModal = true)}
                    class="mt-4 sm:mt-0 inline-flex items-center rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-primary-600 shadow-sm hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200"
                >
                    <svg
                        class="mr-2 -ml-1 h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M12 4v16m8-8H4"
                        />
                    </svg>
                    {$_("projects.createProject")}
                </button>
            </div>
        </div>
    </div>

    {#if error}
        <div
            class="rounded-lg bg-red-50 p-4 animate-in slide-in-from-top-4"
            transition:fade
        >
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
                    <p class="text-sm font-medium text-red-800">{error}</p>
                </div>
            </div>
        </div>
    {/if}

    {#if loading}
        <div class="flex justify-center py-12" transition:fade>
            <div class="relative">
                <div
                    class="h-12 w-12 rounded-full border-4 border-primary-200 border-t-primary-600 animate-spin"
                ></div>
                <div class="absolute inset-0 flex items-center justify-center">
                    <div class="h-6 w-6 rounded-full bg-primary-100"></div>
                </div>
            </div>
        </div>
    {:else}
        <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3" transition:fade>
            {#each projects as project (project.id)}
                <div
                    class="group relative overflow-hidden rounded-xl bg-white shadow-md ring-1 ring-black/5 hover:shadow-lg transition-all duration-300"
                    transition:fly={{ y: 20, duration: 300 }}
                >
                    <!-- Project card content -->
                    <div class="p-6">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-semibold text-gray-900">
                                {project.name}
                            </h3>
                            <span
                                class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset {Functions.getStatusColor(
                                    project.status,
                                )}"
                            >
                                {project.status}
                            </span>
                        </div>

                        <p class="mt-2 text-sm text-gray-600 line-clamp-2">
                            {project.description}
                        </p>

                        <!-- Progress section -->
                        <div class="mt-4">
                            <div
                                class="flex items-center justify-between text-xs"
                            >
                                <span class="text-gray-600">
                                    {#if project.tasks?.length}
                                        {project.tasks.filter(
                                            (t) => t.status === "completed",
                                        ).length} of {project.tasks.length}
                                        {$_("common.tasks")}
                                    {:else}
                                        {$_("common.noTasks")}
                                    {/if}
                                </span>
                                <span class="font-medium text-gray-900">
                                    {getProgress(project)}%
                                </span>
                            </div>
                            <div
                                class="mt-1 h-2 w-full rounded-full bg-gray-200"
                            >
                                <div
                                    class="h-2 rounded-full transition-all duration-500 {getProgressColor(
                                        project,
                                    )}"
                                    style="width: {getProgress(project)}%"
                                ></div>
                            </div>
                        </div>

                        <!-- Project metadata -->
                        <div
                            class="mt-4 flex items-center justify-between text-sm"
                        >
                            <div class="text-gray-600">
                                <span
                                    >{new Date(
                                        project.start_date,
                                    ).toLocaleDateString()}</span
                                >
                                <span class="mx-1">→</span>
                                <span
                                    >{new Date(
                                        project.deadline,
                                    ).toLocaleDateString()}</span
                                >
                            </div>
                            <!-- Team members -->
                            <div class="flex -space-x-2">
                                {#each (project.members || []).slice(0, 3) as member}
                                    <div
                                        class="inline-flex h-6 w-6 items-center justify-center rounded-full bg-primary-500 text-xs font-medium text-white ring-2 ring-white"
                                    >
                                        {member.name?.[0]?.toUpperCase() ||
                                            $_("common.unknownUser")}
                                    </div>
                                {/each}
                                {#if (project.members || []).length > 3}
                                    <div
                                        class="inline-flex h-6 w-6 items-center justify-center rounded-full bg-gray-500 text-xs font-medium text-white ring-2 ring-white"
                                    >
                                        +{project.members.length - 3}
                                    </div>
                                {/if}
                            </div>
                        </div>
                    </div>

                    <!-- Quick actions -->
                    <div
                        class="absolute inset-x-0 bottom-0 translate-y-full bg-gray-50/90 backdrop-blur-sm p-4 transition-transform duration-300 group-hover:translate-y-0"
                    >
                        <div class="flex justify-end space-x-3">
                            {#if $user?.role === "admin"}
                                <button
                                    class="inline-flex items-center rounded-md bg-white/50 backdrop-blur-sm px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                                    on:click={() =>
                                        handleDeleteProject(project.id)}
                                >
                                    <svg
                                        class="mr-2 -ml-0.5 h-4 w-4"
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                    >
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                        />
                                    </svg>
                                    {$_("common.remove")}
                                </button>
                            {/if}
                            <a
                                href="/projects/{project.id}"
                                class="inline-flex items-center rounded-md bg-primary-600/90 backdrop-blur-sm px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
                            >
                                {$_("common.viewDetails")}
                                <svg
                                    class="ml-2 -mr-0.5 h-4 w-4"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M9 5l7 7-7 7"
                                    />
                                </svg>
                            </a>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<!-- Create Project Modal with modern styling -->
{#if showCreateModal}
    <div class="fixed inset-0 z-50 overflow-y-auto" transition:fade>
        <!-- Modal backdrop -->
        <div
            class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm"
            on:click={() => (showCreateModal = false)}
        ></div>

        <!-- Modal panel -->
        <div
            class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"
        >
            <div
                class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6"
                transition:fly={{ y: 20, duration: 300 }}
            >
                <form on:submit|preventDefault={handleCreateProject}>
                    <div>
                        <h3
                            class="text-lg font-semibold leading-6 text-gray-900"
                        >
                            {$_("projects.createProject")}
                        </h3>
                        <div class="mt-6 space-y-6">
                            <div>
                                <label
                                    for="name"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("projects.fields.name")}
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    id="name"
                                    required
                                    bind:value={newProject.name}
                                    class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                />
                            </div>

                            <div>
                                <label
                                    for="description"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("projects.fields.description")}
                                </label>
                                <textarea
                                    id="description"
                                    name="description"
                                    rows="3"
                                    required
                                    bind:value={newProject.description}
                                    class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                ></textarea>
                            </div>

                            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                                <div>
                                    <label
                                        for="start_date"
                                        class="block text-sm font-medium text-gray-700"
                                    >
                                        {$_("projects.fields.startDate")}
                                    </label>
                                    <input
                                        type="date"
                                        name="start_date"
                                        id="start_date"
                                        required
                                        bind:value={newProject.start_date}
                                        class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                    />
                                </div>

                                <div>
                                    <label
                                        for="deadline"
                                        class="block text-sm font-medium text-gray-700"
                                    >
                                        {$_("projects.fields.deadline")}
                                    </label>
                                    <input
                                        type="date"
                                        name="deadline"
                                        id="deadline"
                                        required
                                        bind:value={newProject.deadline}
                                        class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-6 flex items-center justify-end gap-x-3">
                        <button
                            type="button"
                            on:click={() => (showCreateModal = false)}
                            class="rounded-md px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                        >
                            {$_("common.cancel")}
                        </button>
                        <button
                            type="submit"
                            class="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
                        >
                            {$_("common.create")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
