<script lang="ts">
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import { api } from "$lib/services/api";
    import type { Task, Comment, User } from "$lib/types/project";
    import { _ } from "svelte-i18n";

    const projectId = $page.params.projectId;
    const taskId = $page.params.taskId;

    let task: Task | null = null;
    let comments: (Comment & { user?: User })[] = [];
    let users: User[] = [];
    let loading = true;
    let error = "";
    let newComment = "";
    let showStatusMenu = false;
    let showCreateSubtaskModal = false;
    let newSubtask = {
        name: "",
        description: "",
        start_date: new Date().toISOString().split("T")[0],
        deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
            .toISOString()
            .split("T")[0],
        assigned_to_id: "",
    };

    onMount(async () => {
        await loadTaskData();
    });

    async function loadTaskData() {
        loading = true;
        error = "";
        try {
            const [taskData, commentsData, usersData] = await Promise.all([
                api.getTask(taskId),
                api.getTaskComments(taskId),
                api.getUsers(),
            ]);
            task = taskData;
            comments = commentsData.map((comment) => ({
                ...comment,
                user: usersData.find((u) => u.id === comment.user_id),
            }));
            users = usersData;
        } catch (err: any) {
            const errorMessage = err.message || "Failed to load task data";
            console.error(err);
            alert(errorMessage);
        } finally {
            loading = false;
        }
    }

    async function handleAddComment() {
        if (!newComment.trim()) return;

        error = "";
        try {
            await api.createComment({
                task_id: taskId,
                content: newComment.trim(),
            });
            newComment = "";
            await loadTaskData();
        } catch (err: any) {
            const errorMessage = err.message || "Failed to add comment";
            console.error(err);
            alert(errorMessage);
        }
    }

    async function handleStatusChange(
        newStatus: "pending" | "in_progress" | "completed",
    ) {
        try {
            await api.updateTask(taskId, { status: newStatus });
            showStatusMenu = false;
            await loadTaskData();
        } catch (err: any) {
            let errorMessage = "Failed to update task status";
            // dump err keys
            if (err) {
                errorMessage = err;
            }
            console.error(err);
            alert(errorMessage);
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

    function getTaskRowClass(task: Task) {
        if (task.status === "completed") return "bg-green-100";

        const deadline = new Date(task.deadline);
        const now = new Date();
        const oneWeek = 7 * 24 * 60 * 60 * 1000;

        if (deadline < now) {
            return "bg-red-200";
        } else if (deadline.getTime() - now.getTime() < oneWeek) {
            return "bg-orange-100";
        }

        return "bg-blue-100";
    }

    async function handleDeleteTask(taskId: string) {
        if (!confirm($_("common.confirmDelete"))) return;

        try {
            await api.deleteTask(taskId);
            await loadTaskData();
        } catch (err: any) {
            let errorMessage = $_("projects.errors.deleteFailed");
            if (err.response?.data) {
                const serverError =
                    typeof err.response.data === "string"
                        ? err.response.data
                        : err.response.data.detail;
                errorMessage = `${errorMessage}: ${serverError}`;
            }
            console.error(err);
            alert(errorMessage);
        }
    }

    async function handleCreateSubtask() {
        if (!task) return;

        try {
            const taskData = {
                ...newSubtask,
                project_id: projectId,
            };

            await api.createSubtask(taskId, taskData);
            showCreateSubtaskModal = false;
            await loadTaskData();

            // Reset form
            newSubtask = {
                name: "",
                description: "",
                start_date: new Date().toISOString().split("T")[0],
                deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                    .toISOString()
                    .split("T")[0],
                assigned_to_id: "",
            };
        } catch (err: any) {
            let errorMessage = $_("projects.errors.createFailed");
            if (err.response?.data) {
                const serverError =
                    typeof err.response.data === "string"
                        ? err.response.data
                        : err.response.data.detail;
                errorMessage = `${errorMessage}: ${serverError}`;
            }
            console.error(err);
            alert(errorMessage);
        }
    }
</script>

{#if loading}
    <div class="flex justify-center items-center h-64">
        <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"
        />
    </div>
{:else if error}
    <div class="bg-red-50 p-4 rounded-md">
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
                <h3 class="text-sm font-medium text-red-800">{error}</h3>
            </div>
        </div>
    </div>
{:else if task}
    <div class="max-w-4xl mx-auto py-6">
        <div class="mb-6">
            <button
                on:click={() => {
                    window.location.href = task.parent_task_id
                        ? `/projects/${projectId}/tasks/${task.parent_task_id}`
                        : `/projects/${projectId}`;
                }}
                class="text-primary-600 hover:text-primary-900 text-left"
            >
                ← {$_("common.back")}
            </button>
        </div>

        <div class="bg-white shadow overflow-hidden sm:rounded-lg">
            <div class="px-4 py-5 sm:px-6">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-lg leading-6 font-medium text-gray-900">
                            {task.name}
                        </h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">
                            {task.description}
                        </p>
                    </div>
                    <div class="relative">
                        <button
                            on:click={() => (showStatusMenu = !showStatusMenu)}
                            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        >
                            <span
                                class={`mr-2 inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${getStatusColor(task.status)}`}
                            >
                                {task.status}
                            </span>
                            <svg
                                class="h-5 w-5 text-gray-400"
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                        </button>
                        {#if showStatusMenu}
                            <div
                                class="origin-top-right absolute right-0 mt-2 w-40 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5"
                            >
                                <div class="py-1" role="menu">
                                    <button
                                        on:click={() =>
                                            handleStatusChange("pending")}
                                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    >
                                        Pending
                                    </button>
                                    <button
                                        on:click={() =>
                                            handleStatusChange("in_progress")}
                                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    >
                                        In Progress
                                    </button>
                                    <button
                                        on:click={() =>
                                            handleStatusChange("completed")}
                                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    >
                                        Completed
                                    </button>
                                </div>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>

            <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
                <div class="space-y-8">
                    <!-- Comments List -->
                    <div class="space-y-4">
                        {#each comments as comment}
                            <div class="bg-gray-50 rounded-lg p-4">
                                <div class="flex space-x-3">
                                    <div class="flex-shrink-0">
                                        <div
                                            class="h-10 w-10 rounded-full bg-primary-600 flex items-center justify-center text-white"
                                        >
                                            {comment.user?.name?.[0]?.toUpperCase() ||
                                                comment.user?.username?.[0]?.toUpperCase() ||
                                                "U"}
                                        </div>
                                    </div>
                                    <div class="flex-1 space-y-1">
                                        <div
                                            class="flex items-center justify-between"
                                        >
                                            <h3
                                                class="text-sm font-medium text-gray-900"
                                            >
                                                {comment.user?.name ||
                                                    comment.user?.username ||
                                                    "Unknown User"}
                                            </h3>
                                            <p class="text-sm text-gray-500">
                                                {new Date(
                                                    comment.created_at,
                                                ).toLocaleString()}
                                            </p>
                                        </div>
                                        <p class="text-sm text-gray-500">
                                            {comment.content}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>

                    <!-- Add Comment Form -->
                    <div class="mt-6">
                        <form on:submit|preventDefault={handleAddComment}>
                            <div>
                                <label for="comment" class="sr-only"
                                    >Add your comment</label
                                >
                                <textarea
                                    id="comment"
                                    name="comment"
                                    rows="3"
                                    bind:value={newComment}
                                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    placeholder="Add a comment..."
                                ></textarea>
                            </div>
                            <div class="mt-3 flex justify-end">
                                <button
                                    type="submit"
                                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                                >
                                    Comment
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Subtasks Section -->
        <div class="mt-8">
            <div class="sm:flex sm:items-center">
                <div class="sm:flex-auto">
                    <h2 class="text-xl font-semibold text-gray-900">
                        {$_("common.subtasks")}
                    </h2>
                </div>
                <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
                    <button
                        type="button"
                        class="block rounded-md bg-primary-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
                        on:click={() => (showCreateSubtaskModal = true)}
                    >
                        {$_("common.addSubtask")}
                    </button>
                </div>
            </div>

            {#if task.subtasks?.length}
                <div class="mt-4">
                    <div
                        class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg"
                    >
                        <table class="min-w-full divide-y divide-gray-300">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th
                                        scope="col"
                                        class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >
                                        {$_("common.taskName")}
                                    </th>
                                    <th
                                        scope="col"
                                        class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >
                                        {$_("projects.fields.status")}
                                    </th>
                                    <th
                                        scope="col"
                                        class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >
                                        {$_("projects.fields.deadline")}
                                    </th>
                                    <th scope="col" class="relative px-6 py-3">
                                        <span class="sr-only"
                                            >{$_("common.actions")}</span
                                        >
                                    </th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 bg-white">
                                {#each task.subtasks as subtask}
                                    <tr class={getTaskRowClass(subtask)}>
                                        <td
                                            class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >
                                            <button
                                                on:click={async () => {
                                                    window.location.href = `/projects/${projectId}/tasks/${subtask.id}`;
                                                }}
                                                class="text-primary-600 hover:text-primary-900 text-left"
                                            >
                                                {subtask.name}
                                            </button>
                                        </td>
                                        <td
                                            class="px-6 py-4 whitespace-nowrap text-sm"
                                        >
                                            <span
                                                class="inline-flex rounded-full px-2 text-xs font-semibold leading-5 {getStatusColor(
                                                    subtask.status,
                                                )}"
                                            >
                                                {subtask.status}
                                            </span>
                                        </td>
                                        <td
                                            class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                                        >
                                            {new Date(
                                                subtask.deadline,
                                            ).toLocaleDateString()}
                                        </td>
                                        <td
                                            class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                                        >
                                            <button
                                                on:click={() =>
                                                    handleDeleteTask(
                                                        subtask.id,
                                                    )}
                                                class="text-red-600 hover:text-red-900"
                                            >
                                                {$_("common.remove")}
                                            </button>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                </div>
            {:else}
                <p class="mt-4 text-gray-500">{$_("common.noSubtasks")}</p>
            {/if}
        </div>
    </div>
{/if}

<!-- Create Subtask Modal -->
{#if showCreateSubtaskModal}
    <div
        class="fixed z-10 inset-0 overflow-y-auto"
        aria-labelledby="modal-title"
        role="dialog"
        aria-modal="true"
    >
        <div
            class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"
        >
            <!-- Background overlay -->
            <div
                class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
                aria-hidden="true"
                on:click={() => (showCreateSubtaskModal = false)}
            />

            <!-- Modal panel -->
            <div
                class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6"
            >
                <form on:submit|preventDefault={handleCreateSubtask}>
                    <div>
                        <h3
                            class="text-lg leading-6 font-medium text-gray-900"
                            id="modal-title"
                        >
                            {$_("common.addSubtask")}
                        </h3>

                        <div class="mt-6 grid grid-cols-1 gap-y-6 gap-x-4">
                            <div>
                                <label
                                    for="name"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("common.taskName")}
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    id="name"
                                    required
                                    bind:value={newSubtask.name}
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                />
                            </div>

                            <div>
                                <label
                                    for="description"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("common.taskDescription")}
                                </label>
                                <textarea
                                    id="description"
                                    name="description"
                                    rows="3"
                                    bind:value={newSubtask.description}
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                />
                            </div>

                            <div
                                class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2"
                            >
                                <div>
                                    <label
                                        for="start_date"
                                        class="block text-sm font-medium text-gray-700"
                                    >
                                        {$_("common.taskStartDate")}
                                    </label>
                                    <input
                                        type="date"
                                        name="start_date"
                                        id="start_date"
                                        required
                                        bind:value={newSubtask.start_date}
                                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                    />
                                </div>

                                <div>
                                    <label
                                        for="deadline"
                                        class="block text-sm font-medium text-gray-700"
                                    >
                                        {$_("common.taskDeadline")}
                                    </label>
                                    <input
                                        type="date"
                                        name="deadline"
                                        id="deadline"
                                        required
                                        bind:value={newSubtask.deadline}
                                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                    />
                                </div>
                            </div>

                            <div>
                                <label
                                    for="assigned_to"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("common.taskAssignTo")}
                                </label>
                                <select
                                    id="assigned_to"
                                    name="assigned_to"
                                    bind:value={newSubtask.assigned_to_id}
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                >
                                    <option value="">
                                        {$_("common.taskUnassigned")}
                                    </option>
                                    {#each users as user}
                                        <option value={user.id}>
                                            {user.name || user.username}
                                        </option>
                                    {/each}
                                </select>
                            </div>
                        </div>
                    </div>

                    <div
                        class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense"
                    >
                        <button
                            type="submit"
                            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:col-start-2 sm:text-sm"
                        >
                            {$_("common.create")}
                        </button>
                        <button
                            type="button"
                            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:col-start-1 sm:text-sm"
                            on:click={() => (showCreateSubtaskModal = false)}
                        >
                            {$_("common.cancel")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
