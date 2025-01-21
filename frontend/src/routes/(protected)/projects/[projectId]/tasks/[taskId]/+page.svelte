<script lang="ts">
    import { page } from "$app/stores";
    import { onMount, afterUpdate } from "svelte";
    import { api } from "$lib/services/api";
    import type { Task, Comment, User, Project } from "$lib/types/project";
    import { _ } from "svelte-i18n";
    import { fade, fly } from "svelte/transition";
    import { Functions } from "$lib/services/functions";

    const projectId = $page.params.projectId;
    let taskId = $page.params.taskId;

    let projectMembers: (ProjectMember & { user?: User })[] = [];

    let task: Task | null = null;
    let parentTask: Task | null = null;
    let comments: (Comment & { user?: User })[] = [];
    let users: User[] = [];
    let loading = true;
    let error = "";
    let newComment = "";
    let showCreateTaskModal = false;
    let newTask = {
        name: "",
        description: "",
        parent_task_id: taskId,
        start_date: new Date().toISOString().split("T")[0] + "T08:00:00Z",
        deadline:
            new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                .toISOString()
                .split("T")[0] + "T12:00:00Z",
        assigned_to_id: "",
        project_id: projectId,
    };
    let availableUsers: User[] = [];

    let isEditingDescription = false;
    let editedDescription = "";
    let isEditingDeadline = false;
    let editedDeadline = "";

    let project: Project | null = null;

    // Watch for route parameter changes
    $: if ($page.params.taskId !== taskId) {
        taskId = $page.params.taskId;
        loadTaskData(); // Reload data when taskId changes
    }

    onMount(async () => {
        await loadTaskData();
    });

    async function loadTaskData() {
        loading = true;
        error = "";
        try {
            const [
                taskData,
                commentsData,
                usersData,
                membersData,
                projectData,
            ] = await Promise.all([
                api.getTask(taskId),
                api.getTaskComments(taskId),
                api.getUsers(),
                api.getProjectMembers(projectId),
                api.getProject(projectId),
            ]);

            task = taskData;
            project = projectData;

            if (task.parent_task_id) {
                parentTask = await api.getTask(task.parent_task_id);
            } else {
                parentTask = null; // Reset parent task if this is a parent task
            }

            comments = commentsData;
            users = usersData;

            // Combine member data with user data
            projectMembers = membersData.map((member) => ({
                ...member,
                user: usersData.find((u) => u.id === member.user_id),
            }));

            // Filter out users that are already members
            availableUsers = usersData.filter(
                (user) =>
                    !projectMembers.some(
                        (member) => member.user_id === user.id,
                    ),
            );
        } catch (err) {
            error = "Failed to load task data";
            console.error(err);
        } finally {
            loading = false;
        }
    }

    async function handleStatusChange(newStatus: string) {
        if (!task) return;

        try {
            await api.updateTaskStatus(taskId, newStatus);
            task.status = newStatus;
        } catch (err) {
            error = "Failed to update task status";
            console.error(err);
        }
    }

    async function handleAddComment() {
        if (!newComment.trim()) return;

        try {
            const comment = await api.createComment({
                task_id: taskId,
                content: newComment.trim(),
            });
            comments = [...comments, comment];
            newComment = "";
        } catch (err) {
            error = "Failed to add comment";
            console.error(err);
        }
    }

    async function handleCreateSubtask() {
        try {
            await api.createSubtask(taskId, {
                ...newSubtask,
                project_id: projectId,
                start_date: new Date(newSubtask.start_date).toISOString(),
                deadline: new Date(newSubtask.deadline).toISOString(),
            });
            showCreateTaskModal = false;
            await loadTaskData();
        } catch (err) {
            error = "Failed to create subtask";
            console.error(err);
        }
    }

    function getBackUrl() {
        if (task?.parent_task_id) {
            return `/projects/${projectId}/tasks/${task.parent_task_id}`;
        }
        return `/projects/${projectId}`;
    }

    async function updateTaskDescription() {
        if (!task) return;
        try {
            await api.updateTask(task.id, {
                description: editedDescription,
            });
            task.description = editedDescription;
            isEditingDescription = false;
        } catch (err) {
            console.error(err);
            error = "Failed to update task description";
        }
    }

    async function updateTaskDeadline() {
        if (!task) return;
        try {
            // Normalize dates to UTC for comparison
            const taskDeadline = new Date(editedDeadline + "T12:00:00Z");
            const projectDeadline = new Date(
                project?.deadline.split("T")[0] + "T12:00:00Z",
            );

            if (taskDeadline > projectDeadline) {
                throw new Error($_("tasks.errors.deadlineAfterProject"));
            }

            await api.updateTask(task.id, {
                deadline: editedDeadline + "T12:00:00Z",
            });
            task.deadline = editedDeadline + "T12:00:00Z";
            isEditingDeadline = false;
        } catch (err) {
            console.error(err);
            error =
                err instanceof Error
                    ? err.message
                    : "Failed to update task deadline";
            alert(error);
        }
    }
</script>

<div class="space-y-8">
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
    {:else if task}
        <!-- Task Header -->
        <div
            class="relative overflow-hidden rounded-xl bg-gradient-to-r from-primary-600 to-primary-800 p-8 shadow-lg"
        >
            <div class="absolute inset-0 bg-grid-white/10"></div>
            <div class="relative">
                <div class="flex items-center justify-between">
                    <div>
                        <div class="flex items-center space-x-4">
                            <a
                                href={getBackUrl()}
                                class="text-primary-100 hover:text-white transition-colors"
                            >
                                <svg
                                    class="h-6 w-6"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M10 19l-7-7m0 0l7-7m-7 7h18"
                                    />
                                </svg>
                            </a>
                            <div>
                                {#if task?.parent_task_id}
                                    <div class="text-primary-100 text-sm mb-1">
                                        {parentTask?.name || $_("common.tasks")}
                                    </div>
                                {/if}
                                <h1 class="text-3xl font-bold text-white">
                                    {task?.name}
                                </h1>
                            </div>
                        </div>
                        <p class="mt-2 text-lg text-primary-100 max-w-xl">
                            {#if isEditingDescription}
                                <form
                                    class="flex gap-2"
                                    on:submit|preventDefault={updateTaskDescription}
                                >
                                    <input
                                        type="text"
                                        bind:value={editedDescription}
                                        class="flex-1 rounded-lg bg-white/10 backdrop-blur-sm px-3 py-1.5 text-white placeholder:text-primary-100"
                                        placeholder={$_(
                                            "tasks.fields.description",
                                        )}
                                    />
                                    <button
                                        type="submit"
                                        class="rounded-lg bg-white/10 backdrop-blur-sm px-3 py-1.5 text-white hover:bg-white/20"
                                    >
                                        {$_("common.save")}
                                    </button>
                                    <button
                                        type="button"
                                        on:click={() =>
                                            (isEditingDescription = false)}
                                        class="rounded-lg bg-white/10 backdrop-blur-sm px-3 py-1.5 text-white hover:bg-white/20"
                                    >
                                        {$_("common.cancel")}
                                    </button>
                                </form>
                            {:else}
                                <span
                                    class="cursor-pointer hover:underline"
                                    on:click={() => {
                                        editedDescription =
                                            task?.description || "";
                                        isEditingDescription = true;
                                    }}
                                >
                                    {task?.description}
                                </span>
                            {/if}
                        </p>
                    </div>
                    <div class="flex items-center space-x-4">
                        <select
                            bind:value={task.status}
                            on:change={(e) =>
                                handleStatusChange(e.target.value)}
                            class="rounded-lg bg-white/10 backdrop-blur-sm px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-600"
                        >
                            <option value="pending"
                                >{$_("common.taskStatus.pending")}</option
                            >
                            <option value="in_progress"
                                >{$_("common.taskStatus.inProgress")}</option
                            >
                            <option value="completed"
                                >{$_("common.taskStatus.completed")}</option
                            >
                        </select>
                        <button
                            on:click={() => (showCreateTaskModal = true)}
                            class="inline-flex items-center rounded-lg bg-white px-4 py-2 text-sm font-semibold text-primary-600 shadow-sm hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200"
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
                            {$_("common.addSubtask")}
                        </button>
                    </div>
                </div>

                <!-- Task Metadata -->
                <div
                    class="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4"
                >
                    <div class="rounded-lg bg-white/10 backdrop-blur-sm p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg
                                    class="h-6 w-6 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                                    />
                                </svg>
                            </div>
                            <div class="ml-4">
                                <h3 class="text-sm font-medium text-white">
                                    {$_("common.taskStartDate")}
                                </h3>
                                <p
                                    class="mt-1 text-lg font-semibold text-white"
                                >
                                    {new Date(
                                        task.start_date,
                                    ).toLocaleDateString()}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="rounded-lg bg-white/10 backdrop-blur-sm p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg
                                    class="h-6 w-6 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                                    />
                                </svg>
                            </div>
                            <div class="ml-4">
                                <h3 class="text-sm font-medium text-white">
                                    {$_("common.taskDeadline")}
                                </h3>
                                <p
                                    class="mt-1 text-lg font-semibold text-white"
                                >
                                    {#if isEditingDeadline}
                                        <form
                                            class="flex flex-col gap-2"
                                            on:submit|preventDefault={updateTaskDeadline}
                                        >
                                            <input
                                                type="date"
                                                bind:value={editedDeadline}
                                                class="w-full rounded-lg bg-white/10 backdrop-blur-sm px-3 py-1.5 text-white"
                                            />
                                            <div class="flex gap-2">
                                                <button
                                                    type="submit"
                                                    class="flex-1 rounded-lg bg-white/10 backdrop-blur-sm px-3 py-1.5 text-white hover:bg-white/20"
                                                >
                                                    {$_("common.save")}
                                                </button>
                                            </div>
                                            <div class="flex gap-2">
                                                <button
                                                    type="button"
                                                    on:click={() =>
                                                        (isEditingDeadline = false)}
                                                    class="flex-1 rounded-lg bg-white/10 backdrop-blur-sm px-3 py-1.5 text-white hover:bg-white/20"
                                                >
                                                    {$_("common.cancel")}
                                                </button>
                                            </div>
                                        </form>
                                    {:else}
                                        <span
                                            class="cursor-pointer hover:underline"
                                            on:click={() => {
                                                editedDeadline = new Date(
                                                    task?.deadline || "",
                                                )
                                                    .toISOString()
                                                    .split("T")[0];
                                                isEditingDeadline = true;
                                            }}
                                        >
                                            {new Date(
                                                task?.deadline || "",
                                            ).toLocaleDateString()}
                                        </span>
                                    {/if}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="rounded-lg bg-white/10 backdrop-blur-sm p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg
                                    class="h-6 w-6 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                                    />
                                </svg>
                            </div>
                            <div class="ml-4">
                                <h3 class="text-sm font-medium text-white">
                                    {$_("common.taskAssignTo")}
                                </h3>
                                <div class="mt-1">
                                    <select
                                        bind:value={task.assigned_to_id}
                                        on:change={async (e) => {
                                            try {
                                                await api.updateTask(task.id, {
                                                    assigned_to_id:
                                                        e.target.value || null,
                                                });
                                                await loadTaskData();
                                            } catch (err) {
                                                console.error(err);
                                            }
                                        }}
                                        class="w-full rounded-md bg-white/10 backdrop-blur-sm px-3 py-1.5 text-base font-semibold text-white shadow-sm hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-600"
                                    >
                                        <option value=""
                                            >{$_(
                                                "common.taskUnassigned",
                                            )}</option
                                        >
                                        {#each projectMembers as member}
                                            <option
                                                value={member.user_id}
                                                selected={member.user_id ===
                                                    task.assigned_to_id}
                                            >
                                                {member.user?.name ||
                                                    member.user?.username ||
                                                    $_("common.unknownUser")}
                                            </option>
                                        {/each}
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="rounded-lg bg-white/10 backdrop-blur-sm p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg
                                    class="h-6 w-6 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                                    />
                                </svg>
                            </div>
                            <div class="ml-4">
                                <h3 class="text-sm font-medium text-white">
                                    Comments
                                </h3>
                                <p
                                    class="mt-1 text-lg font-semibold text-white"
                                >
                                    {comments.length}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
            <!-- Subtasks List -->
            <div class="lg:col-span-2 space-y-6">
                <div
                    class="rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5"
                >
                    <div class="p-6">
                        <h2
                            class="text-base font-semibold leading-7 text-gray-900"
                        >
                            {$_("common.subtasks")}
                        </h2>
                        {#if task.subtasks?.length}
                            <div class="mt-6 flow-root">
                                <ul class="divide-y divide-gray-100">
                                    {#each task.subtasks as task (task.id)}
                                        <li
                                            class="relative py-5 hover:bg-gray-50"
                                        >
                                            <div class="px-4 sm:px-6">
                                                <div
                                                    class="flex items-center justify-between"
                                                >
                                                    <a
                                                        href="/projects/{projectId}/tasks/{task.id}"
                                                        class="text-sm font-medium text-gray-900 hover:text-primary-600"
                                                    >
                                                        {task.name}
                                                    </a>
                                                    <div
                                                        class="flex items-center space-x-4"
                                                    >
                                                        <!-- Assigned User Avatar -->
                                                        {#if task.assigned_to_id}
                                                            <div
                                                                class="flex items-center"
                                                            >
                                                                <div
                                                                    class="h-6 w-6 rounded-full bg-primary-500 flex items-center justify-center"
                                                                >
                                                                    <span
                                                                        class="text-xs font-medium text-white"
                                                                    >
                                                                        {users
                                                                            .find(
                                                                                (
                                                                                    u,
                                                                                ) =>
                                                                                    u.id ===
                                                                                    task.assigned_to_id,
                                                                            )
                                                                            ?.name?.[0]?.toUpperCase() ||
                                                                            "U"}
                                                                    </span>
                                                                </div>
                                                                <span
                                                                    class="ml-2 text-sm text-gray-500"
                                                                >
                                                                    {users.find(
                                                                        (u) =>
                                                                            u.id ===
                                                                            task.assigned_to_id,
                                                                    )?.name ||
                                                                        "Unknown"}
                                                                </span>
                                                            </div>
                                                        {/if}
                                                        <!-- Task status badge -->
                                                        <span
                                                            class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset {Functions.getStatusColor(
                                                                task.status,
                                                            )}"
                                                        >
                                                            {task.status}
                                                        </span>
                                                        <!-- Delete button -->
                                                        <button
                                                            on:click|preventDefault={async () => {
                                                                if (
                                                                    confirm(
                                                                        "Are you sure you want to delete this task?",
                                                                    )
                                                                ) {
                                                                    try {
                                                                        await api.deleteTask(
                                                                            task.id,
                                                                        );
                                                                        await loadProjectData();
                                                                    } catch (err) {
                                                                        console.error(
                                                                            err,
                                                                        );
                                                                    }
                                                                }
                                                            }}
                                                            class="text-gray-400 hover:text-red-600"
                                                        >
                                                            <svg
                                                                xmlns="http://www.w3.org/2000/svg"
                                                                class="h-5 w-5"
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
                                                        </button>
                                                    </div>
                                                </div>
                                                <div class="mt-2">
                                                    <p
                                                        class="text-sm text-gray-600 line-clamp-2"
                                                    >
                                                        {task.description}
                                                    </p>
                                                </div>
                                            </div>
                                        </li>
                                    {/each}
                                </ul>
                            </div>
                        {:else}
                            <p class="mt-4 text-sm text-gray-500">
                                {$_("common.noSubtasks")}
                            </p>
                        {/if}
                    </div>
                </div>
            </div>

            <!-- Comments Section -->
            <div class="space-y-6">
                <div
                    class="rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5"
                >
                    <div class="p-6">
                        <h2
                            class="text-base font-semibold leading-7 text-gray-900"
                        >
                            Comments
                        </h2>
                        <div class="mt-6">
                            <!-- Comment Input -->
                            <div class="mb-6">
                                <textarea
                                    bind:value={newComment}
                                    placeholder="Add a comment..."
                                    rows="3"
                                    class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                ></textarea>
                                <div class="mt-2 flex justify-end">
                                    <button
                                        on:click={handleAddComment}
                                        class="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
                                    >
                                        Add Comment
                                    </button>
                                </div>
                            </div>

                            <!-- Comments List -->
                            <ul class="space-y-6">
                                {#each comments as comment (comment.id)}
                                    <li class="relative">
                                        <div class="flex gap-4">
                                            <div class="flex-shrink-0">
                                                <div
                                                    class="h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center"
                                                >
                                                    <span
                                                        class="text-sm font-medium text-white"
                                                    >
                                                        {comment.user?.name?.[0]?.toUpperCase() ||
                                                            "U"}
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="flex-grow">
                                                <div
                                                    class="flex items-center justify-between"
                                                >
                                                    <p
                                                        class="text-sm font-medium text-gray-900"
                                                    >
                                                        {comment.user?.name ||
                                                            comment.user
                                                                ?.username ||
                                                            "Unknown User"}
                                                    </p>
                                                    <p
                                                        class="text-xs text-gray-500"
                                                    >
                                                        {new Date(
                                                            comment.created_at,
                                                        ).toLocaleString()}
                                                    </p>
                                                </div>
                                                <p
                                                    class="mt-1 text-sm text-gray-600"
                                                >
                                                    {comment.content}
                                                </p>
                                            </div>
                                        </div>
                                    </li>
                                {/each}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>

<!-- Create Subtask Modal -->
{#if showCreateTaskModal}
    <div
        class="fixed inset-0 z-50 overflow-y-auto backdrop-blur-sm bg-gray-500/30"
        transition:fade
        on:click|self={() => (showCreateTaskModal = false)}
    >
        <div class="flex min-h-screen items-center justify-center p-4">
            <div
                class="relative w-full max-w-2xl rounded-xl bg-white p-6 shadow-lg"
                transition:fly={{ y: 20 }}
            >
                <h3 class="text-lg font-semibold text-gray-900">
                    {$_("common.addSubtask")}
                </h3>
                <form
                    class="mt-4 space-y-4"
                    on:submit|preventDefault={async () => {
                        try {
                            // Normalize dates to UTC for comparison
                            const subtaskDeadline = new Date(
                                newTask.deadline + "T12:00:00Z",
                            );
                            const taskDeadline = new Date(
                                task?.deadline.split("T")[0] + "T12:00:00Z",
                            );
                            const projectDeadline = new Date(
                                project?.deadline.split("T")[0] + "T12:00:00Z",
                            );

                            // Check against both task and project deadlines
                            if (subtaskDeadline > taskDeadline) {
                                throw new Error(
                                    $_("tasks.errors.deadlineAfterParentTask"),
                                );
                            }
                            if (subtaskDeadline > projectDeadline) {
                                throw new Error(
                                    $_("tasks.errors.deadlineAfterProject"),
                                );
                            }

                            await api.createTask(newTask);
                            showCreateTaskModal = false;
                            await loadTaskData();
                        } catch (err) {
                            error =
                                err instanceof Error
                                    ? err.message
                                    : $_("tasks.errors.createFailed");
                            console.error(err);
                            alert(error);
                        }
                    }}
                >
                    <div>
                        <label
                            for="task-name"
                            class="block text-sm font-medium text-gray-700"
                            >{$_("common.taskName")}</label
                        >
                        <input
                            type="text"
                            id="task-name"
                            bind:value={newTask.name}
                            required
                            class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500"
                        />
                    </div>
                    <div>
                        <label
                            for="task-description"
                            class="block text-sm font-medium text-gray-700"
                            >{$_("common.taskDescription")}</label
                        >
                        <textarea
                            id="task-description"
                            bind:value={newTask.description}
                            rows="3"
                            class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500"
                        />
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label
                                for="start-date"
                                class="block text-sm font-medium text-gray-700"
                                >{$_("common.taskStartDate")}</label
                            >
                            <input
                                type="date"
                                id="start-date"
                                bind:value={newTask.start_date}
                                required
                                max={task?.deadline.split("T")[0]}
                                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500"
                            />
                        </div>
                        <div>
                            <label
                                for="deadline"
                                class="block text-sm font-medium text-gray-700"
                                >{$_("common.taskDeadline")}</label
                            >
                            <input
                                type="date"
                                id="deadline"
                                bind:value={newTask.deadline}
                                required
                                max={task?.deadline.split("T")[0]}
                                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500"
                            />
                        </div>
                    </div>
                    <div>
                        <label
                            for="assigned-to"
                            class="block text-sm font-medium text-gray-700"
                            >Assign To</label
                        >
                        <select
                            id="assigned-to"
                            bind:value={newTask.assigned_to_id}
                            class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500"
                        >
                            <option value="">Select team member</option>
                            {#each projectMembers as member}
                                <option value={member.user_id}>
                                    {member.user?.name || member.user?.username}
                                </option>
                            {/each}
                        </select>
                    </div>
                    <div class="mt-6 flex justify-end space-x-3">
                        <button
                            type="button"
                            on:click={() => (showCreateTaskModal = false)}
                            class="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                            >{$_("common.cancel")}</button
                        >
                        <button
                            type="submit"
                            class="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
                            >{$_("common.create")}</button
                        >
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
