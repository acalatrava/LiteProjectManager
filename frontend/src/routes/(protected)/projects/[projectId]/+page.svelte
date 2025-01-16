<script lang="ts">
    import { page } from "$app/stores";
    import { onMount } from "svelte";
    import { api } from "$lib/services/api";
    import type { GanttTask } from "$lib/types/project";
    import type {
        Project,
        Task,
        ProjectMember,
        User,
    } from "$lib/types/project";
    import { _ } from "svelte-i18n";

    const projectId = $page.params.projectId;
    let project: Project | null = null;
    let tasks: Task[] = [];
    let ganttTasks: GanttTask[] = [];
    let projectMembers: (ProjectMember & { user?: User })[] = [];
    let loading = true;
    let error = "";

    // Task creation form
    let showCreateTaskModal = false;
    let newTask = {
        name: "",
        description: "",
        start_date: new Date().toISOString().split("T")[0],
        deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
            .toISOString()
            .split("T")[0],
        assigned_to_id: "",
    };

    let showAddMemberModal = false;
    let availableUsers: User[] = [];
    let newMember = {
        user_id: "",
        role: "project_member" as "project_manager" | "project_member",
    };

    onMount(async () => {
        await loadProjectData();
    });

    async function loadProjectData() {
        loading = true;
        error = "";
        try {
            const [projectData, tasksData, membersData, usersData, ganttData] =
                await Promise.all([
                    api.getProject(projectId),
                    api.getTasks(projectId),
                    api.getProjectMembers(projectId),
                    api.getUsers(),
                    api.getGanttChart(projectId),
                ]);
            project = projectData;
            tasks = tasksData;
            ganttTasks = ganttData.tasks;

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
            error = "Failed to load project data";
            console.error(err);
        } finally {
            loading = false;
        }
    }

    async function handleCreateTask() {
        error = "";
        try {
            const taskData = {
                ...newTask,
                project_id: projectId,
                start_date: new Date(newTask.start_date).toISOString(),
                deadline: new Date(newTask.deadline).toISOString(),
                assigned_to_id: newTask.assigned_to_id || null, // Ensure null if empty string
            };

            await api.createTask(taskData);
            showCreateTaskModal = false;
            await loadProjectData();
            newTask = {
                name: "",
                description: "",
                start_date: new Date().toISOString().split("T")[0],
                deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                    .toISOString()
                    .split("T")[0],
                assigned_to_id: "",
            };
        } catch (err) {
            error = "Failed to create task";
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

    async function handleReassignTask(
        taskId: string,
        newAssigneeId: string | null,
    ) {
        error = "";
        try {
            await api.updateTask(taskId, {
                assigned_to_id: newAssigneeId,
            });
            await loadProjectData();
        } catch (err) {
            error = "Failed to reassign task";
            console.error(err);
        }
    }

    async function handleDeleteTask(taskId: string) {
        if (!confirm($_("common.confirmDelete"))) return;

        error = "";
        try {
            await api.deleteTask(taskId);
            tasks = tasks.filter((t) => t.id !== taskId);
        } catch (err) {
            error = $_("projects.errors.deleteFailed");
            console.error(err);
        }
    }

    async function handleAddMember() {
        error = "";
        try {
            await api.addProjectMember(
                projectId,
                newMember.user_id,
                newMember.role,
            );
            showAddMemberModal = false;
            await loadProjectData();
            newMember = {
                user_id: "",
                role: "project_member",
            };
        } catch (err) {
            error = "Failed to add member";
            console.error(err);
        }
    }

    async function handleRemoveMember(userId: string) {
        if (!confirm("Are you sure you want to remove this member?")) return;

        error = "";
        try {
            await api.removeProjectMember(projectId, userId);
            await loadProjectData();
        } catch (err) {
            error = "Failed to remove member";
            console.error(err);
        }
    }

    function getTaskOffset(
        start: string,
        projectStart: string | undefined,
    ): number {
        if (!projectStart) return 0;
        const startDate = new Date(start);
        const projectStartDate = new Date(projectStart);
        const diffDays = Math.floor(
            (startDate.getTime() - projectStartDate.getTime()) /
                (1000 * 60 * 60 * 24),
        );
        return (diffDays / 60) * 100; // 60 days view window
    }

    function getTaskWidth(start: string, end: string): number {
        const startDate = new Date(start);
        const endDate = new Date(end);
        const diffDays = Math.floor(
            (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24),
        );
        return (diffDays / 60) * 100; // 60 days view window
    }

    function getTaskColor(progress: number): string {
        if (progress >= 1) {
            return "bg-green-200 border-green-300";
        } else if (progress > 0) {
            return "bg-yellow-200 border-yellow-300";
        }
        return "bg-blue-200 border-blue-300";
    }

    function getProgressColor(progress: number): string {
        if (progress >= 1) {
            return "bg-green-500";
        } else if (progress > 0) {
            return "bg-yellow-500";
        }
        return "bg-blue-500";
    }

    function formatDate(date: Date): string {
        return date.toLocaleDateString(undefined, {
            month: "short",
            day: "numeric",
        });
    }

    function getDatesForTimeline(startDate: Date): Date[] {
        const dates: Date[] = [];
        for (let i = 0; i < 60; i += 5) {
            // Show every 5 days for 60 days
            const date = new Date(startDate);
            date.setDate(date.getDate() + i);
            dates.push(date);
        }
        return dates;
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
{:else if project}
    <div class="mb-6">
        <a href="/projects" class="text-primary-600 hover:text-primary-900"
            >← {$_("common.back")}</a
        >
    </div>
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
            <div class="flex justify-between items-center">
                <div>
                    <h3 class="text-lg leading-6 font-medium text-gray-900">
                        {project.name}
                    </h3>
                    <p class="mt-1 max-w-2xl text-sm text-gray-500">
                        {project.description}
                    </p>
                </div>
                <span
                    class="px-2 inline-flex text-xs leading-5 font-semibold {getStatusColor(
                        project.status,
                    )}"
                >
                    {project.status}
                </span>
            </div>
        </div>

        <!-- Project Details -->
        <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
            <dl class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
                <div class="sm:col-span-1">
                    <dt class="text-sm font-medium text-gray-500">
                        Start Date
                    </dt>
                    <dd class="mt-1 text-sm text-gray-900">
                        {new Date(project.start_date).toLocaleDateString()}
                    </dd>
                </div>
                <div class="sm:col-span-1">
                    <dt class="text-sm font-medium text-gray-500">Deadline</dt>
                    <dd class="mt-1 text-sm text-gray-900">
                        {new Date(project.deadline).toLocaleDateString()}
                    </dd>
                </div>
            </dl>
        </div>

        <!-- Add this before the task list section -->
        <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                {$_("common.timeline")}
            </h3>
            <div class="bg-white shadow overflow-hidden sm:rounded-lg p-4">
                <div class="relative" style="height: 200px;">
                    <!-- Timeline header -->
                    <div
                        class="absolute top-0 left-0 right-0 h-8 flex border-b"
                    >
                        {#each getDatesForTimeline(new Date(project?.start_date || Date.now())) as date}
                            <div class="flex-1 text-xs text-center border-r">
                                {formatDate(date)}
                            </div>
                        {/each}
                    </div>

                    <!-- Gantt bars -->
                    <div
                        class="absolute top-8 left-0 right-0 bottom-0 overflow-y-auto"
                    >
                        {#each ganttTasks as task, i}
                            <div
                                class="relative h-8 border-b flex items-center"
                            >
                                <div
                                    on:click={() => {
                                        window.location.href = `/projects/${projectId}/tasks/${task.id}`;
                                    }}
                                    class="absolute h-6 rounded {getTaskColor(
                                        task.progress,
                                    )} border cursor-pointer hover:opacity-75 transition-opacity"
                                    style="
                                        left: {getTaskOffset(
                                        task.start,
                                        project?.start_date,
                                    )}%;
                                        width: {getTaskWidth(
                                        task.start,
                                        task.end,
                                    )}%;
                                    "
                                >
                                    <div class="px-2 truncate text-xs">
                                        {task.name}
                                    </div>
                                    <div
                                        class="absolute top-0 left-0 bottom-0 {getProgressColor(
                                            task.progress,
                                        )} opacity-25"
                                        style="width: {task.progress * 100}%"
                                    ></div>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>
        </div>

        <!-- Tasks Section -->
        <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                    {$_("common.tasks")}
                </h3>
                <button
                    on:click={() => (showCreateTaskModal = true)}
                    class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                    {$_("common.addTask")}
                </button>
            </div>

            {#if tasks.length === 0}
                <p class="text-sm text-gray-500">{$_("common.noTasks")}</p>
            {:else}
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
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
                                    {$_("common.taskStatus")}
                                </th>
                                <th
                                    scope="col"
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                >
                                    {$_("common.taskDeadline")}
                                </th>
                                <th
                                    scope="col"
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                >
                                    {$_("common.taskAssignTo")}
                                </th>
                                <th scope="col" class="relative px-6 py-3">
                                    <span class="sr-only">Actions</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            {#each tasks as task}
                                <tr>
                                    <td class="px-6 py-4">
                                        <div
                                            class="text-sm font-medium text-gray-900"
                                        >
                                            <a
                                                href="/projects/{projectId}/tasks/{task.id}"
                                                class="text-primary-600 hover:text-primary-900"
                                            >
                                                {task.name}
                                            </a>
                                        </div>
                                        <div class="text-sm text-gray-500">
                                            {task.description}
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span
                                            class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getStatusColor(
                                                task.status,
                                            )}"
                                        >
                                            {task.status}
                                        </span>
                                    </td>
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                                    >
                                        {new Date(
                                            task.deadline,
                                        ).toLocaleDateString()}
                                    </td>
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                                    >
                                        <select
                                            value={task.assigned_to_id || ""}
                                            on:change={(e) =>
                                                handleReassignTask(
                                                    task.id,
                                                    e.currentTarget.value ||
                                                        null,
                                                )}
                                            class="block w-full pl-3 pr-10 py-1 text-sm border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-md"
                                        >
                                            <option value=""
                                                >{$_(
                                                    "common.taskUnassigned",
                                                )}</option
                                            >
                                            {#each projectMembers as member}
                                                <option value={member.user_id}>
                                                    {member.user?.name ||
                                                        member.user?.username ||
                                                        member.user_id}
                                                </option>
                                            {/each}
                                        </select>
                                    </td>
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                                    >
                                        <button
                                            on:click={() =>
                                                handleDeleteTask(task.id)}
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
            {/if}
        </div>

        <!-- Update the project members list -->
        <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                    {$_("common.projectMembers")}
                </h3>
                <button
                    on:click={() => (showAddMemberModal = true)}
                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                    {$_("common.addMember")}
                </button>
            </div>
            <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th
                                scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                                Name
                            </th>
                            <th
                                scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                                Role
                            </th>
                            <th scope="col" class="relative px-6 py-3">
                                <span class="sr-only">Actions</span>
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {#each projectMembers as member}
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div
                                        class="text-sm font-medium text-gray-900"
                                    >
                                        {member.user?.name ||
                                            member.user?.username ||
                                            "Unknown User"}
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span
                                        class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800"
                                    >
                                        {member.role === "project_manager"
                                            ? "Project Manager"
                                            : "Project Member"}
                                    </span>
                                </td>
                                <td
                                    class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                                >
                                    <button
                                        on:click={() =>
                                            handleRemoveMember(member.user_id)}
                                        class="text-red-600 hover:text-red-900"
                                    >
                                        Remove
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
{/if}

<!-- Create Task Modal -->
{#if showCreateTaskModal}
    <div
        class="fixed z-10 inset-0 overflow-y-auto"
        aria-labelledby="modal-title"
        role="dialog"
        aria-modal="true"
    >
        <!-- Modal backdrop -->
        <div
            class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"
        >
            <div
                class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
                aria-hidden="true"
            />
            <span
                class="hidden sm:inline-block sm:align-middle sm:h-screen"
                aria-hidden="true">&#8203;</span
            >
            <div
                class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6"
            >
                <form on:submit|preventDefault={handleCreateTask}>
                    <div>
                        <h3
                            class="text-lg leading-6 font-medium text-gray-900"
                            id="modal-title"
                        >
                            {$_("common.createTask")}
                        </h3>
                        <div class="mt-2">
                            <div class="space-y-6">
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
                                            bind:value={newTask.name}
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
                                            bind:value={newTask.description}
                                            class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                        />
                                    </div>
                                </div>

                                <div
                                    class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2"
                                >
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
                                                bind:value={newTask.start_date}
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
                                                bind:value={newTask.deadline}
                                                class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <label
                                        for="assigned_to"
                                        class="block text-sm font-medium text-gray-700"
                                        >Assign To</label
                                    >
                                    <div class="mt-1">
                                        <select
                                            id="assigned_to"
                                            name="assigned_to"
                                            bind:value={newTask.assigned_to_id}
                                            class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                        >
                                            <option value=""
                                                >{$_(
                                                    "common.taskUnassigned",
                                                )}</option
                                            >
                                            {#each projectMembers as member}
                                                <option value={member.user_id}>
                                                    {member.user?.name ||
                                                        member.user?.username ||
                                                        member.user_id}
                                                </option>
                                            {/each}
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-5 sm:mt-6 grid grid-cols-2 gap-3">
                        <button
                            type="button"
                            on:click={() => (showCreateTaskModal = false)}
                            class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:text-sm"
                        >
                            {$_("common.cancel")}
                        </button>
                        <button
                            type="submit"
                            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:text-sm"
                        >
                            {$_("common.create")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}

<!-- Add Member Modal -->
{#if showAddMemberModal}
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
                class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6"
            >
                <form on:submit|preventDefault={handleAddMember}>
                    <div>
                        <h3
                            class="text-lg leading-6 font-medium text-gray-900"
                            id="modal-title"
                        >
                            {$_("common.addMember")}
                        </h3>
                        <div class="mt-6 grid grid-cols-1 gap-y-6 gap-x-4">
                            <div>
                                <label
                                    for="user_id"
                                    class="block text-sm font-medium text-gray-700"
                                    >User</label
                                >
                                <select
                                    id="user_id"
                                    required
                                    bind:value={newMember.user_id}
                                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-md"
                                >
                                    <option value=""
                                        >{$_("common.selectUser")}</option
                                    >
                                    {#each availableUsers as user}
                                        <option value={user.id}>
                                            {user.name || user.username}
                                        </option>
                                    {/each}
                                </select>
                            </div>

                            <div>
                                <label
                                    for="role"
                                    class="block text-sm font-medium text-gray-700"
                                    >Role</label
                                >
                                <select
                                    id="role"
                                    required
                                    bind:value={newMember.role}
                                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-md"
                                >
                                    <option value="project_member"
                                        >Project Member</option
                                    >
                                    <option value="project_manager"
                                        >Project Manager</option
                                    >
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="mt-5 sm:mt-6 grid grid-cols-2 gap-3">
                        <button
                            type="button"
                            on:click={() => (showAddMemberModal = false)}
                            class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:text-sm"
                        >
                            {$_("common.cancel")}
                        </button>
                        <button
                            type="submit"
                            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:text-sm"
                        >
                            {$_("common.addMember")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
