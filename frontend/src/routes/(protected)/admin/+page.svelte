<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/services/api";
    import type { User } from "$lib/types/user";
    import { UserRole } from "$lib/types/user";
    import { _ } from "svelte-i18n";

    let users: User[] = [];
    let loading = true;
    let error = "";
    let selectedUser: User | null = null;
    let showDeleteModal = false;
    let showEditModal = false;
    let showCreateModal = false;
    let newUser = {
        email: "",
        full_name: "",
        role: UserRole.USER,
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
            error = "admin.errors.loadFailed";
            console.error(err);
        } finally {
            loading = false;
        }
    }

    async function handleRoleChange(userId: string, newRole: UserRole) {
        error = "";
        try {
            await api.updateUser(userId, { role: newRole });
            users = await api.getUsers();
        } catch (err) {
            error = "admin.errors.updateRoleFailed";
            console.error(err);
        }
    }

    function openDeleteModal(user: User) {
        selectedUser = user;
        showDeleteModal = true;
    }

    function openEditModal(user: User) {
        selectedUser = user;
        showEditModal = true;
    }

    async function handleDeleteUser() {
        if (!selectedUser) return;

        error = "";
        try {
            await api.deleteUser(selectedUser!.id);
            users = users.filter((u) => u.id !== selectedUser!.id);
            showDeleteModal = false;
            selectedUser = null;
        } catch (err) {
            error = "admin.errors.deleteFailed";
            console.error(err);
        }
    }

    async function handleUpdateUser(event: Event) {
        event.preventDefault();
        if (!selectedUser) return;

        error = "";
        try {
            await api.updateUser(selectedUser.id, {
                name: selectedUser.name,
                is_active: selectedUser.is_active,
            });
            users = await api.getUsers();
            showEditModal = false;
            selectedUser = null;
        } catch (err) {
            error = "admin.errors.updateFailed";
            console.error(err);
        }
    }

    async function handleCreateUser(event: Event) {
        event.preventDefault();
        error = "";

        try {
            await api.createUser(newUser);
            users = await api.getUsers();
            showCreateModal = false;
            newUser = {
                email: "",
                full_name: "",
                role: UserRole.USER,
            };
        } catch (err) {
            error = "admin.errors.createFailed";
            console.error(err);
        }
    }
</script>

<div class="py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="sm:flex sm:items-center">
            <div class="sm:flex-auto">
                <h1 class="text-2xl font-semibold text-gray-900">
                    {$_("admin.userList.title")}
                </h1>
                <p class="mt-2 text-sm text-gray-700">
                    {$_("admin.userList.description")}
                </p>
            </div>
            <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
                <button
                    type="button"
                    on:click={() => (showCreateModal = true)}
                    class="inline-flex items-center justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 sm:w-auto"
                >
                    {$_("admin.userList.actions.create")}
                </button>
            </div>
        </div>

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
                            {$_(error)}
                        </p>
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
                        class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8 px-4"
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
                                            >{$_(
                                                "admin.userList.columns.name",
                                            )}</th
                                        >
                                        <th
                                            scope="col"
                                            class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                                            >{$_(
                                                "admin.userList.columns.email",
                                            )}</th
                                        >
                                        <th
                                            scope="col"
                                            class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                                            >{$_(
                                                "admin.userList.columns.role",
                                            )}</th
                                        >
                                        <th
                                            scope="col"
                                            class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                                            >{$_(
                                                "admin.userList.columns.status",
                                            )}</th
                                        >
                                        <th
                                            scope="col"
                                            class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                                            >{$_(
                                                "admin.userList.columns.created",
                                            )}</th
                                        >
                                        <th
                                            scope="col"
                                            class="relative py-3.5 pl-3 pr-4 sm:pr-6"
                                        >
                                            <span class="sr-only"
                                                >{$_(
                                                    "admin.userList.columns.actions",
                                                )}</span
                                            >
                                        </th>
                                    </tr>
                                </thead>
                                <tbody
                                    class="divide-y divide-gray-200 bg-white"
                                >
                                    {#each users as user (user.id)}
                                        <tr>
                                            <td
                                                class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6"
                                            >
                                                {user.name || "-"}
                                            </td>
                                            <td
                                                class="whitespace-nowrap px-3 py-4 text-sm text-gray-500"
                                                >{user.username}</td
                                            >
                                            <td
                                                class="whitespace-nowrap px-3 py-4 text-sm text-gray-500"
                                            >
                                                <select
                                                    value={user.role}
                                                    on:change={(e) =>
                                                        handleRoleChange(
                                                            user.id,
                                                            e.currentTarget
                                                                .value as UserRole,
                                                        )}
                                                    class="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm"
                                                >
                                                    <option
                                                        value={UserRole.USER}
                                                        >{$_(
                                                            "admin.userList.roles.user",
                                                        )}</option
                                                    >
                                                    <option
                                                        value={UserRole.ADMIN}
                                                        >{$_(
                                                            "admin.userList.roles.admin",
                                                        )}</option
                                                    >
                                                </select>
                                            </td>
                                            <td
                                                class="whitespace-nowrap px-3 py-4 text-sm text-gray-500"
                                            >
                                                <span
                                                    class={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${user.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                                                >
                                                    {user.is_active
                                                        ? $_(
                                                              "admin.userList.status.active",
                                                          )
                                                        : $_(
                                                              "admin.userList.status.inactive",
                                                          )}
                                                </span>
                                            </td>
                                            <td
                                                class="whitespace-nowrap px-3 py-4 text-sm text-gray-500"
                                            >
                                                {new Date(
                                                    user.created_at,
                                                ).toLocaleDateString()}
                                            </td>
                                            <td
                                                class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6"
                                            >
                                                <button
                                                    on:click={() =>
                                                        openEditModal(user)}
                                                    class="text-primary-600 hover:text-primary-900 mr-4"
                                                >
                                                    {$_(
                                                        "admin.userList.actions.edit",
                                                    )}
                                                </button>
                                                <button
                                                    on:click={() =>
                                                        openDeleteModal(user)}
                                                    class="text-red-600 hover:text-red-900"
                                                >
                                                    {$_(
                                                        "admin.userList.actions.delete",
                                                    )}
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

<!-- Delete Modal -->
{#if showDeleteModal}
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
                <div class="sm:flex sm:items-start">
                    <div
                        class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"
                    >
                        <svg
                            class="h-6 w-6 text-red-600"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                            />
                        </svg>
                    </div>
                    <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                        <h3
                            class="text-lg leading-6 font-medium text-gray-900"
                            id="modal-title"
                        >
                            {$_("admin.deleteModal.title")}
                        </h3>
                        <div class="mt-2">
                            <p class="text-sm text-gray-500">
                                {$_("admin.deleteModal.message")}
                            </p>
                        </div>
                    </div>
                </div>
                <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                    <button
                        type="button"
                        on:click={handleDeleteUser}
                        class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
                    >
                        {$_("admin.deleteModal.confirm")}
                    </button>
                    <button
                        type="button"
                        on:click={() => {
                            showDeleteModal = false;
                            selectedUser = null;
                        }}
                        class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:w-auto sm:text-sm"
                    >
                        {$_("admin.deleteModal.cancel")}
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- Edit Modal -->
{#if showEditModal && selectedUser}
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
                <form on:submit={handleUpdateUser}>
                    <div>
                        <h3
                            class="text-lg leading-6 font-medium text-gray-900"
                            id="modal-title"
                        >
                            {$_("admin.editModal.title")}
                        </h3>
                        <div
                            class="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6"
                        >
                            <div class="sm:col-span-4">
                                <label
                                    for="name"
                                    class="block text-sm font-medium text-gray-700"
                                    >{$_("admin.editModal.fields.name")}</label
                                >
                                <div class="mt-1">
                                    <input
                                        type="text"
                                        name="name"
                                        id="name"
                                        bind:value={selectedUser.name}
                                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    />
                                </div>
                            </div>

                            <div class="sm:col-span-4">
                                <label
                                    for="status"
                                    class="block text-sm font-medium text-gray-700"
                                    >{$_(
                                        "admin.editModal.fields.status",
                                    )}</label
                                >
                                <div class="mt-1">
                                    <select
                                        id="status"
                                        name="status"
                                        bind:value={selectedUser.is_active}
                                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    >
                                        <option value={true}>Active</option>
                                        <option value={false}>Inactive</option>
                                    </select>
                                </div>
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
                            {$_("admin.editModal.save")}
                        </button>
                        <button
                            type="button"
                            on:click={() => {
                                showEditModal = false;
                                selectedUser = null;
                            }}
                            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:col-start-1 sm:text-sm"
                        >
                            {$_("admin.editModal.cancel")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}

<!-- Create User Modal -->
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
                <form on:submit={handleCreateUser}>
                    <div>
                        <h3
                            class="text-lg leading-6 font-medium text-gray-900"
                            id="modal-title"
                        >
                            {$_("admin.createModal.title")}
                        </h3>
                        <div
                            class="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6"
                        >
                            <div class="sm:col-span-4">
                                <label
                                    for="email"
                                    class="block text-sm font-medium text-gray-700"
                                    >{$_(
                                        "admin.createModal.fields.email",
                                    )}</label
                                >
                                <div class="mt-1">
                                    <input
                                        type="email"
                                        name="email"
                                        id="email"
                                        required
                                        bind:value={newUser.email}
                                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    />
                                </div>
                            </div>

                            <div class="sm:col-span-4">
                                <label
                                    for="full_name"
                                    class="block text-sm font-medium text-gray-700"
                                    >{$_(
                                        "admin.createModal.fields.fullName",
                                    )}</label
                                >
                                <div class="mt-1">
                                    <input
                                        type="text"
                                        name="full_name"
                                        id="full_name"
                                        required
                                        bind:value={newUser.full_name}
                                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    />
                                </div>
                            </div>

                            <div class="sm:col-span-4">
                                <label
                                    for="role"
                                    class="block text-sm font-medium text-gray-700"
                                    >{$_(
                                        "admin.createModal.fields.role",
                                    )}</label
                                >
                                <div class="mt-1">
                                    <select
                                        id="role"
                                        name="role"
                                        bind:value={newUser.role}
                                        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                    >
                                        <option value={UserRole.USER}
                                            >{$_(
                                                "admin.userList.roles.user",
                                            )}</option
                                        >
                                        <option value={UserRole.ADMIN}
                                            >{$_(
                                                "admin.userList.roles.admin",
                                            )}</option
                                        >
                                    </select>
                                </div>
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
                            {$_("admin.createModal.create")}
                        </button>
                        <button
                            type="button"
                            on:click={() => {
                                showCreateModal = false;
                                newUser = {
                                    email: "",
                                    full_name: "",
                                    role: UserRole.USER,
                                };
                            }}
                            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:col-start-1 sm:text-sm"
                        >
                            {$_("admin.createModal.cancel")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
