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
    import { fade, fly } from "svelte/transition";
    import { Functions } from "$lib/services/functions";

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
        role: "project_member",
    };

    let users: User[] = [];

    let timelineDays = 30;
    let timelineDates: Date[] = [];

    onMount(async () => {
        await loadProjectData();

        // Get dates array for timeline
        timelineDays = getTimelineDays();
        timelineDates = Array(timelineDays)
            .fill(0)
            .map(
                (_, i) =>
                    new Date(
                        new Date(project?.start_date || Date.now()).getTime() +
                            i * 24 * 60 * 60 * 1000,
                    ),
            );
    });

    async function loadProjectData() {
        loading = true;
        error = "";
        try {
            const [projectData, membersData, tasksData, usersData, ganttData] =
                await Promise.all([
                    api.getProject(projectId),
                    api.getProjectMembers(projectId),
                    api.getTasks(projectId),
                    api.getUsers(),
                    api.getGanttChart(projectId),
                ]);

            project = projectData;
            tasks = tasksData;
            users = usersData;

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

    function getTaskColor(progress: number): string {
        if (progress >= 1) return "bg-green-100 border-green-200";
        if (progress > 0) return "bg-blue-100 border-blue-200";
        return "bg-gray-100 border-gray-200";
    }

    function getProgressColor(progress: number): string {
        if (progress >= 1) return "bg-green-500";
        return "bg-blue-500";
    }

    function getTaskOffset(start: string, projectStart: string): number {
        const taskStart = new Date(start);
        const projStart = new Date(projectStart || start);
        const diff = taskStart.getTime() - projStart.getTime();
        const days = diff / (1000 * 60 * 60 * 24);
        return days * 3; // 3% per day
    }

    function getTaskWidth(start: string, end: string): number {
        const taskStart = new Date(start);
        const taskEnd = new Date(end);
        const diff = taskEnd.getTime() - taskStart.getTime();
        const days = diff / (1000 * 60 * 60 * 24);
        return Math.max(days * 3, 3); // 3% per day, minimum 3%
    }

    // Calculate total days needed for the timeline
    function getTimelineDays(): number {
        console.log("getTimelineDays");
        if (!project || !ganttTasks.length) {
            console.log("No project or tasks");
            console.log(project);
            console.log(ganttTasks);
            return 7; // Show a week if no tasks
        }

        const projectStart = new Date(project.start_date);
        const lastTaskEnd = new Date(
            Math.max(...ganttTasks.map((t) => new Date(t.end).getTime())),
        );
        console.log("Last task end:", lastTaskEnd);
        const diffDays = Math.ceil(
            (lastTaskEnd.getTime() - projectStart.getTime()) /
                (1000 * 60 * 60 * 24),
        );
        console.log("Diff days:", diffDays);
        return diffDays + 2; // Add 2 days padding for better visualization
    }
</script>

<!-- Project Header -->
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
    {:else if project}
        <!-- Project Header -->
        <div
            class="relative overflow-hidden rounded-xl bg-gradient-to-r from-primary-600 to-primary-800 p-8 shadow-lg"
        >
            <div class="absolute inset-0 bg-grid-white/10"></div>
            <div class="relative">
                <div class="flex items-center justify-between">
                    <div>
                        <div class="flex items-center space-x-4">
                            <a
                                href={"/projects"}
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
                            <h1 class="text-3xl font-bold text-white">
                                {project.name}
                            </h1>
                        </div>
                        <p class="mt-2 text-lg text-primary-100">
                            {project.description}
                        </p>
                    </div>
                    <div class="flex items-center space-x-4">
                        <button
                            on:click={() => (showAddMemberModal = true)}
                            class="inline-flex items-center rounded-lg bg-white/10 backdrop-blur-sm px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200"
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
                                    d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
                                />
                            </svg>
                            {$_("common.addMember")}
                        </button>
                        <button
                            on:click={() => (showCreateTaskModal = true)}
                            class="inline-flex items-center rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-primary-600 shadow-sm hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200"
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
                            {$_("common.addTask")}
                        </button>
                    </div>
                </div>

                <!-- Project Stats -->
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
                                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                                    />
                                </svg>
                            </div>
                            <div class="ml-4">
                                <h3 class="text-sm font-medium text-white">
                                    {$_("common.tasks")}
                                </h3>
                                <p
                                    class="mt-1 text-2xl font-semibold text-white"
                                >
                                    {tasks.length}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Deadline -->
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
                                    {$_("projects.fields.deadline")}
                                </h3>
                                <p
                                    class="mt-1 text-2xl font-semibold text-white"
                                >
                                    {new Date(
                                        project.deadline,
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
                                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                    />
                                </svg>
                            </div>
                            <div class="ml-4">
                                <h3 class="text-sm font-medium text-white">
                                    Completed
                                </h3>
                                <p
                                    class="mt-1 text-2xl font-semibold text-white"
                                >
                                    {tasks.filter(
                                        (t) => t.status === "completed",
                                    ).length}
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
                                    In Progress
                                </h3>
                                <p
                                    class="mt-1 text-2xl font-semibold text-white"
                                >
                                    {tasks.filter(
                                        (t) => t.status === "in_progress",
                                    ).length}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gantt Chart -->
        {#if !loading && project && ganttTasks.length > 0}
            <div class="rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5">
                <div class="p-6">
                    <h2 class="text-base font-semibold leading-7 text-gray-900">
                        {$_("common.timeline")}
                    </h2>
                    <div class="mt-6">
                        <!-- Fixed height container with both scrollbars -->
                        <div class="h-[400px] overflow-hidden">
                            <!-- Scrollable container -->
                            <div
                                class="h-full overflow-x-auto overflow-y-auto custom-scrollbar"
                            >
                                <!-- Content container with dynamic width -->
                                <div
                                    class="relative min-w-full"
                                    style="width: {timelineDays * 3}%"
                                >
                                    <!-- Timeline header with sticky positioning -->
                                    <div class="sticky top-0 z-10 bg-white">
                                        <div
                                            class="flex border-b border-gray-200"
                                        >
                                            {#each timelineDates as date, i}
                                                <div class="flex-none w-[3%]">
                                                    <div
                                                        class="px-1 py-2 text-xs font-medium text-gray-500"
                                                    >
                                                        {date.toLocaleDateString(
                                                            undefined,
                                                            {
                                                                month: "short",
                                                                day: "numeric",
                                                            },
                                                        )}
                                                    </div>
                                                </div>
                                            {/each}
                                        </div>
                                    </div>

                                    <!-- Content area with grid lines -->
                                    <div class="relative">
                                        <!-- Background grid -->
                                        <div class="absolute inset-0 flex">
                                            {#each timelineDates as _, i}
                                                <div
                                                    class="flex-none w-[3%] border-l border-gray-100"
                                                ></div>
                                            {/each}
                                        </div>

                                        <!-- Tasks -->
                                        <div class="relative">
                                            {#each ganttTasks as task, i}
                                                <div
                                                    class="h-12 flex items-center group hover:bg-gray-50/50"
                                                >
                                                    <div
                                                        on:click={() => {
                                                            window.location.href = `/projects/${projectId}/tasks/${task.id}`;
                                                        }}
                                                        class="absolute h-8 rounded-lg shadow-sm {getTaskColor(
                                                            task.progress,
                                                        )} border-2 cursor-pointer transform transition-all duration-200 hover:scale-y-110 hover:shadow-md"
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
                                                        <div
                                                            class="px-3 py-1 truncate text-sm font-medium"
                                                        >
                                                            {task.name}
                                                        </div>
                                                        <div
                                                            class="absolute top-0 left-0 bottom-0 {getProgressColor(
                                                                task.progress,
                                                            )} opacity-25 rounded-l-lg transition-all duration-300"
                                                            style="width: {task.progress *
                                                                100}%"
                                                        ></div>
                                                    </div>
                                                </div>
                                            {/each}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {/if}

        <!-- Main Content -->
        <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
            <!-- Tasks List -->
            <div class="lg:col-span-2 space-y-6">
                <div
                    class="rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5"
                >
                    <div class="p-6">
                        <h2
                            class="text-base font-semibold leading-7 text-gray-900"
                        >
                            {$_("common.tasks")}
                        </h2>
                        {#if tasks.length == 0}
                            <div class="mt-6 flow-root">
                                <p class="text-sm text-gray-500">
                                    {$_("common.noTasks")}
                                </p>
                            </div>
                        {:else}
                            <div class="mt-6 flow-root">
                                <ul class="divide-y divide-gray-100">
                                    {#each tasks.filter((t) => !t.parent_task_id) as task (task.id)}
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
                        {/if}
                    </div>
                </div>
            </div>

            <!-- Team Members -->
            <div class="space-y-6">
                <div
                    class="rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5"
                >
                    <div class="p-6">
                        <h2
                            class="text-base font-semibold leading-7 text-gray-900"
                        >
                            {$_("common.projectMembers")}
                        </h2>
                        <div class="mt-6 flow-root">
                            <ul class="divide-y divide-gray-100">
                                {#each projectMembers as member (member.id)}
                                    <li class="py-5">
                                        <div
                                            class="flex items-center space-x-4"
                                        >
                                            <div class="flex-shrink-0">
                                                <div
                                                    class="h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center"
                                                >
                                                    <span
                                                        class="text-sm font-medium text-white"
                                                    >
                                                        {member.user?.name?.[0]?.toUpperCase() ||
                                                            "U"}
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="min-w-0 flex-1">
                                                <p
                                                    class="text-sm font-medium text-gray-900"
                                                >
                                                    {member.user?.name ||
                                                        member.user?.username ||
                                                        "Unknown User"}
                                                </p>
                                                <p
                                                    class="text-sm text-gray-500"
                                                >
                                                    {member.role ===
                                                    "project_manager"
                                                        ? "Project Manager"
                                                        : "Project Member"}
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

<!-- Modals -->
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
                    {$_("common.createTask")}
                </h3>
                <form
                    class="mt-4 space-y-4"
                    on:submit|preventDefault={async () => {
                        try {
                            await api.createTask(projectId, newTask);
                            showCreateTaskModal = false;
                            await loadProjectData();
                        } catch (err) {
                            console.error(err);
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
                                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500"
                            />
                        </div>
                    </div>
                    <div>
                        <label
                            for="assigned-to"
                            class="block text-sm font-medium text-gray-700"
                            >{$_("common.taskAssignTo")}</label
                        >
                        <select
                            id="assigned-to"
                            bind:value={newTask.assigned_to_id}
                            class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500"
                        >
                            <option value=""
                                >{$_("common.taskUnassigned")}</option
                            >
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

{#if showAddMemberModal}
    <div
        class="fixed inset-0 z-50 overflow-y-auto backdrop-blur-sm bg-gray-500/30"
        transition:fade
        on:click|self={() => (showAddMemberModal = false)}
    >
        <div class="flex min-h-screen items-center justify-center p-4">
            <div
                class="relative w-full max-w-2xl rounded-xl bg-white p-6 shadow-lg"
                transition:fly={{ y: 20 }}
            >
                <h3 class="text-lg font-semibold text-gray-900">
                    {$_("common.addMember")}
                </h3>
                <form
                    class="mt-4 space-y-4"
                    on:submit|preventDefault={async () => {
                        try {
                            await api.addProjectMember(projectId, newMember);
                            showAddMemberModal = false;
                            await loadProjectData();
                        } catch (err) {
                            console.error(err);
                        }
                    }}
                >
                    <div>
                        <label
                            for="user"
                            class="block text-sm font-medium text-gray-700"
                            >{$_("common.selectUser")}</label
                        >
                        <select
                            id="user"
                            bind:value={newMember.user_id}
                            required
                            class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500"
                        >
                            <option value="">{$_("common.selectUser")}</option>
                            {#each availableUsers as user}
                                <option value={user.id}>
                                    {user.name ||
                                        user.username ||
                                        $_("common.unknownUser")}
                                </option>
                            {/each}
                        </select>
                    </div>
                    <div>
                        <label
                            for="role"
                            class="block text-sm font-medium text-gray-700"
                            >{$_("common.role")}</label
                        >
                        <select
                            id="role"
                            bind:value={newMember.role}
                            required
                            class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500"
                        >
                            <option value="project_member"
                                >{$_("common.projectMember")}</option
                            >
                            <option value="project_manager"
                                >{$_("common.projectManager")}</option
                            >
                        </select>
                    </div>
                    <div class="mt-6 flex justify-end space-x-3">
                        <button
                            type="button"
                            on:click={() => (showAddMemberModal = false)}
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

<style>
    :global(.gantt-container) {
        height: 400px;
        width: 100%;
    }

    .custom-scrollbar {
        scrollbar-width: thin;
        scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
    }

    .custom-scrollbar::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb {
        background-color: rgba(156, 163, 175, 0.5);
        border-radius: 3px;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background-color: rgba(156, 163, 175, 0.7);
    }
</style>
