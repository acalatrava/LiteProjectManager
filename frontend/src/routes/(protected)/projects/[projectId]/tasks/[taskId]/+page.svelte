<script lang="ts">
    import { page } from "$app/stores";
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
        } catch (err) {
            error = "Failed to load task data";
            console.error(err);
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
        } catch (err) {
            error = "Failed to add comment";
            console.error(err);
        }
    }

    async function handleStatusChange(
        newStatus: "pending" | "in_progress" | "completed",
    ) {
        error = "";
        try {
            await api.updateTask(taskId, { status: newStatus });
            showStatusMenu = false;
            await loadTaskData();
        } catch (err) {
            error = "Failed to update task status";
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
            <a
                href="/projects/{projectId}"
                class="text-primary-600 hover:text-primary-900"
                >← {$_("common.back")}</a
            >
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
    </div>
{/if}
