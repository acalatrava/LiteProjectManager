<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/services/api";
    import type { User } from "$lib/types/user";
    import { UserRole } from "$lib/types/user";
    import { _ } from "svelte-i18n";
    import { fade } from "svelte/transition";
    import { Functions } from "$lib/services/functions";

    let users: User[] = [];
    let loading = true;
    let error = "";
    let success = "";

    // Modal states
    let showDeleteModal = false;
    let showEditModal = false;
    let showCreateModal = false;
    let showResetModal = false;
    let selectedUser: User | null = null;

    // Edit form data
    let editForm = {
        name: "",
        role: UserRole.USER,
        is_active: true,
    };

    // Create form data
    let createForm = {
        email: "",
        full_name: "",
        role: "user",
    };

    onMount(async () => {
        await loadUsers();
    });

    async function loadUsers() {
        loading = true;
        error = "";
        try {
            users = await api.getUsers();
        } catch (err) {
            error = $_("admin.errors.loadFailed");
            console.error(err);
        } finally {
            loading = false;
        }
    }

    function openEditModal(user: User) {
        selectedUser = user;
        editForm = {
            name: user.name || "",
            role: user.role,
            is_active: user.is_active,
        };
        showEditModal = true;
    }

    function openDeleteModal(user: User) {
        selectedUser = user;
        showDeleteModal = true;
    }

    function openResetModal(user: User) {
        selectedUser = user;
        showResetModal = true;
    }

    async function handleEditSubmit() {
        if (!selectedUser) return;

        try {
            await api.updateUser(selectedUser.id, editForm);
            await loadUsers();
            showEditModal = false;
            success = $_("admin.userList.success.userUpdated");
        } catch (err: any) {
            error = err.message || $_("admin.errors.updateFailed");
        }
    }

    async function handleDeleteConfirm() {
        if (!selectedUser) return;

        try {
            await api.deleteUser(selectedUser.id);
            await loadUsers();
            showDeleteModal = false;
            success = $_("admin.userList.success.userDeleted");
        } catch (err: any) {
            error = err.message || $_("admin.errors.deleteFailed");
        }
    }

    async function handleCreateSubmit() {
        try {
            await api.createUser(createForm);
            await loadUsers();
            showCreateModal = false;
            success = $_("admin.success.userCreated");
            // Reset form
            createForm = {
                email: "",
                full_name: "",
                role: "user",
            };
        } catch (err: any) {
            error = err.message || $_("admin.errors.createFailed");
        }
    }

    async function handleResetConfirm() {
        if (!selectedUser) return;

        try {
            await api.resetUserPassword(selectedUser.id);
            showResetModal = false;
            success = $_("admin.success.passwordReset");
        } catch (err: any) {
            error = err.message || $_("admin.errors.resetFailed");
        }
    }
</script>

<div class="space-y-8">
    <!-- Header -->
    <div
        class="relative overflow-hidden rounded-xl bg-gradient-to-r from-primary-600 to-primary-800 p-8 shadow-lg"
    >
        <div class="absolute inset-0 bg-grid-white/10"></div>
        <div class="relative">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-white">
                        {$_("admin.userList.title")}
                    </h1>
                    <p class="mt-2 text-lg text-primary-100 max-w-xl">
                        {$_("admin.userList.description")}
                    </p>
                </div>
                <button
                    on:click={() => (showCreateModal = true)}
                    class="inline-flex items-center rounded-md bg-white/10 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-white/20"
                >
                    {$_("admin.userList.actions.create")}
                </button>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5">
        {#if error}
            <div
                class="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg"
                transition:fade
            >
                {error}
            </div>
        {/if}

        {#if success}
            <div
                class="p-4 mb-4 text-sm text-green-700 bg-green-100 rounded-lg"
                transition:fade
            >
                {success}
            </div>
        {/if}

        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th
                            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                            {$_("admin.userList.columns.name")}
                        </th>
                        <th
                            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                            {$_("admin.userList.columns.email")}
                        </th>
                        <th
                            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                            {$_("admin.userList.columns.role")}
                        </th>
                        <th
                            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                            {$_("admin.userList.columns.status")}
                        </th>
                        <th
                            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                            {$_("admin.userList.columns.created")}
                        </th>
                        <th
                            class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                            {$_("admin.userList.columns.actions")}
                        </th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                    {#each users as user (user.id)}
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="h-10 w-10 flex-shrink-0">
                                        <div
                                            class="h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center"
                                        >
                                            <span
                                                class="text-sm font-medium text-white"
                                            >
                                                {user.name?.[0]?.toUpperCase() ||
                                                    user.username?.[0]?.toUpperCase() ||
                                                    "U"}
                                            </span>
                                        </div>
                                    </div>
                                    <div class="ml-4">
                                        <div
                                            class="text-sm font-medium text-gray-900"
                                        >
                                            {user.name || user.username}
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm text-gray-900">
                                    {user.username}
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span
                                    class="inline-flex rounded-full bg-primary-100 px-2 text-xs font-semibold leading-5 text-primary-800"
                                >
                                    {user.role}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span
                                    class={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                                        user.is_active
                                            ? "bg-green-100 text-green-800 "
                                            : "bg-red-100 text-red-800 "
                                    }`}
                                >
                                    {user.is_active
                                        ? $_("admin.userList.status.active")
                                        : $_("admin.userList.status.inactive")}
                                </span>
                            </td>
                            <td
                                class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                            >
                                {new Date(user.created_at).toLocaleDateString()}
                            </td>
                            <td
                                class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                            >
                                <div class="flex justify-end space-x-4">
                                    <button
                                        on:click={() => openEditModal(user)}
                                        class="text-primary-600 hover:text-primary-900"
                                    >
                                        {$_("admin.userList.actions.edit")}
                                    </button>
                                    <button
                                        on:click={() => openResetModal(user)}
                                        class="text-yellow-600 hover:text-yellow-900"
                                    >
                                        {$_("admin.userList.actions.reset")}
                                    </button>
                                    <button
                                        on:click={() => openDeleteModal(user)}
                                        class="text-red-600 hover:text-red-900"
                                    >
                                        {$_("admin.userList.actions.delete")}
                                    </button>
                                </div>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Delete Modal -->
{#if showDeleteModal}
    <div class="fixed inset-0 z-50 overflow-y-auto" transition:fade>
        <div class="flex min-h-screen items-center justify-center p-4">
            <div
                class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
            ></div>
            <div class="relative rounded-lg bg-white p-8 shadow-xl">
                <h3 class="text-lg font-medium text-gray-900">
                    {$_("admin.deleteModal.title")}
                </h3>
                <p class="text-sm text-gray-500">
                    {$_("admin.deleteModal.message")}
                </p>
                <div class="mt-6 flex justify-end space-x-4">
                    <button
                        on:click={() => (showDeleteModal = false)}
                        class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                        {$_("admin.deleteModal.cancel")}
                    </button>
                    <button
                        on:click={handleDeleteConfirm}
                        class="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
                    >
                        {$_("admin.deleteModal.confirm")}
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- Edit Modal -->
{#if showEditModal}
    <div class="fixed inset-0 z-50 overflow-y-auto" transition:fade>
        <div class="flex min-h-screen items-center justify-center p-4">
            <div
                class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
            ></div>
            <div
                class="relative w-full max-w-md rounded-lg bg-white p-8 shadow-xl"
            >
                <h3 class="text-lg font-medium text-gray-900">
                    {$_("admin.editModal.title")}
                </h3>
                <form
                    on:submit|preventDefault={handleEditSubmit}
                    class="space-y-4"
                >
                    <div>
                        <label
                            for="name"
                            class="block text-sm font-medium text-gray-700"
                        >
                            {$_("admin.editModal.fields.name")}
                        </label>
                        <input
                            type="text"
                            id="name"
                            bind:value={editForm.name}
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                        />
                    </div>
                    <div>
                        <label
                            for="role"
                            class="block text-sm font-medium text-gray-700"
                        >
                            {$_("admin.editModal.fields.role")}
                        </label>
                        <select
                            id="role"
                            bind:value={editForm.role}
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                        >
                            <option value="user"
                                >{$_("admin.userList.roles.user")}</option
                            >
                            <option value="admin"
                                >{$_("admin.userList.roles.admin")}</option
                            >
                        </select>
                    </div>
                    <div>
                        <label class="flex items-center">
                            <input
                                type="checkbox"
                                bind:checked={editForm.is_active}
                                class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                            />
                            <span class="ml-2 text-sm text-gray-700">
                                {$_("admin.userList.status.active")}
                            </span>
                        </label>
                    </div>
                    <div class="mt-6 flex justify-end space-x-4">
                        <button
                            type="button"
                            on:click={() => (showEditModal = false)}
                            class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                        >
                            {$_("admin.editModal.cancel")}
                        </button>
                        <button
                            type="submit"
                            class="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
                        >
                            {$_("admin.editModal.save")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}

<!-- Create Modal -->
{#if showCreateModal}
    <div class="fixed inset-0 z-50 overflow-y-auto" transition:fade>
        <div class="flex min-h-screen items-center justify-center p-4">
            <div
                class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
            ></div>
            <div
                class="relative w-full max-w-md rounded-lg bg-white p-8 shadow-xl"
            >
                <h3 class="text-lg font-medium text-gray-900">
                    {$_("admin.createModal.title")}
                </h3>
                <form
                    on:submit|preventDefault={handleCreateSubmit}
                    class="space-y-4"
                >
                    <div>
                        <label
                            for="create-email"
                            class="block text-sm font-medium text-gray-700"
                        >
                            {$_("admin.createModal.fields.email")}
                        </label>
                        <input
                            type="email"
                            id="create-email"
                            bind:value={createForm.email}
                            required
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                        />
                    </div>
                    <div>
                        <label
                            for="create-name"
                            class="block text-sm font-medium text-gray-700"
                        >
                            {$_("admin.createModal.fields.fullName")}
                        </label>
                        <input
                            type="text"
                            id="create-name"
                            bind:value={createForm.full_name}
                            required
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                        />
                    </div>
                    <div>
                        <label
                            for="create-role"
                            class="block text-sm font-medium text-gray-700"
                        >
                            {$_("admin.createModal.fields.role")}
                        </label>
                        <select
                            id="create-role"
                            bind:value={createForm.role}
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                        >
                            <option value="user"
                                >{$_("admin.userList.roles.user")}</option
                            >
                            <option value="admin"
                                >{$_("admin.userList.roles.admin")}</option
                            >
                        </select>
                    </div>
                    <div class="mt-6 flex justify-end space-x-4">
                        <button
                            type="button"
                            on:click={() => (showCreateModal = false)}
                            class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                        >
                            {$_("admin.createModal.cancel")}
                        </button>
                        <button
                            type="submit"
                            class="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
                        >
                            {$_("admin.createModal.create")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}

<!-- Reset Password Modal -->
{#if showResetModal}
    <div class="fixed inset-0 z-50 overflow-y-auto" transition:fade>
        <div class="flex min-h-screen items-center justify-center p-4">
            <div
                class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
            ></div>
            <div class="relative rounded-lg bg-white p-8 shadow-xl">
                <h3 class="text-lg font-medium text-gray-900">
                    {$_("admin.resetModal.title")}
                </h3>
                <p class="text-sm text-gray-500">
                    {$_("admin.resetModal.message")}
                </p>
                <div class="mt-6 flex justify-end space-x-4">
                    <button
                        on:click={() => (showResetModal = false)}
                        class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                        {$_("admin.resetModal.cancel")}
                    </button>
                    <button
                        on:click={handleResetConfirm}
                        class="rounded-md bg-yellow-600 px-4 py-2 text-sm font-medium text-white hover:bg-yellow-700"
                    >
                        {$_("admin.resetModal.confirm")}
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}
