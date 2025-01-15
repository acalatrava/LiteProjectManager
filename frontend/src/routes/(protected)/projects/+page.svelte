<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/services/api";
    import type { Project } from "$lib/types/project";
    import { _ } from "svelte-i18n";

    let projects: Project[] = [];
    let loading = true;
    let error = "";
    let showCreateModal = false;
    let newProject = {
        name: "",
        description: "",
        start_date: new Date().toISOString().split("T")[0],
        deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
            .toISOString()
            .split("T")[0],
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

    async function handleCreateProject() {
        error = "";
        try {
            await api.createProject({
                ...newProject,
                start_date: new Date(newProject.start_date).toISOString(),
                deadline: new Date(newProject.deadline).toISOString(),
            });
            showCreateModal = false;
            await loadProjects();
            newProject = {
                name: "",
                description: "",
                start_date: new Date().toISOString().split("T")[0],
                deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
                    .toISOString()
                    .split("T")[0],
            };
        } catch (err) {
            error = "Failed to create project";
            console.error(err);
        }
    }

    async function handleDeleteProject(id: string) {
        if (!confirm("Are you sure you want to delete this project?")) return;

        error = "";
        try {
            await api.deleteProject(id);
            projects = projects.filter((p) => p.id !== id);
        } catch (err) {
            error = "Failed to delete project";
            console.error(err);
        }
    }

    function getStatusColor(status: string) {
        switch (status) {
            case "pending":
                return "bg-yellow-100 text-yellow-800";
            case "in_progress":
                return "bg-blue-100 text-blue-800";
            case "completed":
                return "bg-green-100 text-green-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    }
</script>

<div class="py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="sm:flex sm:items-center">
            <div class="sm:flex-auto">
                <h1 class="text-2xl font-semibold text-gray-900">Projects</h1>
                <p class="mt-2 text-sm text-gray-700">
                    A list of all projects including their name, status, and
                    other details.
                </p>
            </div>
            <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
                <button
                    on:click={() => (showCreateModal = true)}
                    class="inline-flex items-center justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 sm:w-auto"
                >
                    Create Project
                </button>
            </div>
        </div>

        {#if error}
            <div class="mt-4 rounded-md bg-red-50 p-4">
                <div class="flex">
                    <div class="ml-3">
                        <p class="text-sm font-medium text-red-800">{error}</p>
                    </div>
                </div>
            </div>
        {/if}

        {#if loading}
            <div class="mt-8 flex justify-center">
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
        {:else}
            <div class="mt-8 flex flex-col">
                <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                    <div
                        class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8"
                    >
                        <div
                            class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg"
                        >
                            <table class="min-w-full divide-y divide-gray-300">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th
                                            scope="col"
                                            class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6"
                                        >
                                            Name
                                        </th>
                                        <th
                                            scope="col"
                                            class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                                        >
                                            Description
                                        </th>
                                        <th
                                            scope="col"
                                            class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                                        >
                                            Status
                                        </th>
                                        <th
                                            scope="col"
                                            class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                                        >
                                            Deadline
                                        </th>
                                        <th
                                            scope="col"
                                            class="relative py-3.5 pl-3 pr-4 sm:pr-6"
                                        >
                                            <span class="sr-only">Actions</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody
                                    class="divide-y divide-gray-200 bg-white"
                                >
                                    {#each projects as project}
                                        <tr>
                                            <td
                                                class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6"
                                            >
                                                <a
                                                    href="/projects/{project.id}"
                                                    class="text-primary-600 hover:text-primary-900"
                                                >
                                                    {project.name}
                                                </a>
                                            </td>
                                            <td
                                                class="whitespace-nowrap px-3 py-4 text-sm text-gray-500"
                                            >
                                                {project.description}
                                            </td>
                                            <td
                                                class="whitespace-nowrap px-3 py-4 text-sm"
                                            >
                                                <span
                                                    class="inline-flex rounded-full px-2 text-xs font-semibold leading-5 {getStatusColor(
                                                        project.status,
                                                    )}"
                                                >
                                                    {project.status}
                                                </span>
                                            </td>
                                            <td
                                                class="whitespace-nowrap px-3 py-4 text-sm text-gray-500"
                                            >
                                                {new Date(
                                                    project.deadline,
                                                ).toLocaleDateString()}
                                            </td>
                                            <td
                                                class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6"
                                            >
                                                <button
                                                    on:click={() =>
                                                        handleDeleteProject(
                                                            project.id,
                                                        )}
                                                    class="text-red-600 hover:text-red-900"
                                                >
                                                    Delete
                                                </button>
                                            </td>
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        {/if}
    </div>
</div>

<!-- Create Project Modal -->
{#if showCreateModal}
    <div
        class="fixed z-10 inset-0 overflow-y-auto"
        aria-labelledby="modal-title"
        role="dialog"
        aria-modal="true"
    >
        <div
            class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"
        >
            <div
                class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
                aria-hidden="true"
            ></div>
            <span
                class="hidden sm:inline-block sm:align-middle sm:h-screen"
                aria-hidden="true">&#8203;</span
            >
            <div
                class="relative inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6"
            >
                <form on:submit|preventDefault={handleCreateProject}>
                    <div>
                        <h3
                            class="text-lg leading-6 font-medium text-gray-900"
                            id="modal-title"
                        >
                            Create New Project
                        </h3>
                        <div class="mt-6 grid grid-cols-1 gap-y-6 gap-x-4">
                            <div>
                                <label
                                    for="name"
                                    class="block text-sm font-medium text-gray-700"
                                    >Name</label
                                >
                                <div class="mt-1">
                                    <input
                                        type="text"
                                        name="name"
                                        id="name"
                                        required
                                        bind:value={newProject.name}
                                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    />
                                </div>
                            </div>

                            <div>
                                <label
                                    for="description"
                                    class="block text-sm font-medium text-gray-700"
                                    >Description</label
                                >
                                <div class="mt-1">
                                    <textarea
                                        id="description"
                                        name="description"
                                        rows="3"
                                        required
                                        bind:value={newProject.description}
                                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    ></textarea>
                                </div>
                            </div>

                            <div>
                                <label
                                    for="start_date"
                                    class="block text-sm font-medium text-gray-700"
                                    >Start Date</label
                                >
                                <div class="mt-1">
                                    <input
                                        type="date"
                                        name="start_date"
                                        id="start_date"
                                        required
                                        bind:value={newProject.start_date}
                                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    />
                                </div>
                            </div>

                            <div>
                                <label
                                    for="deadline"
                                    class="block text-sm font-medium text-gray-700"
                                    >Deadline</label
                                >
                                <div class="mt-1">
                                    <input
                                        type="date"
                                        name="deadline"
                                        id="deadline"
                                        required
                                        bind:value={newProject.deadline}
                                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3">
                        <button
                            type="submit"
                            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:col-start-2 sm:text-sm"
                        >
                            Create
                        </button>
                        <button
                            type="button"
                            on:click={() => (showCreateModal = false)}
                            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:col-start-1 sm:text-sm"
                        >
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
