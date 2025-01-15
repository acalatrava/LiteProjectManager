<script lang="ts">
    import { user } from "$lib/stores/auth";
    import { api } from "$lib/services/api";
    import { onMount } from "svelte";
    import { _ } from "svelte-i18n";

    let loading = false;
    let error = "";
    let success = "";
    let editMode = false;
    let editedUser = {
        name: $user?.name || "",
        current_password: "",
        new_password: "",
        confirm_password: "",
    };

    let showPasswordFields = false;

    async function handleUpdateProfile(event: Event) {
        event.preventDefault();
        loading = true;
        error = "";
        success = "";

        try {
            const updateData: any = { name: editedUser.name };

            // Only include password update if the user is changing it
            if (showPasswordFields) {
                if (!editedUser.current_password) {
                    throw new Error($_("profile.currentPasswordRequired"));
                }
                if (editedUser.new_password !== editedUser.confirm_password) {
                    throw new Error($_("profile.passwordsDoNotMatch"));
                }
                if (editedUser.new_password.length < 8) {
                    throw new Error($_("profile.passwordTooShort"));
                }
                updateData.current_password = editedUser.current_password;
                updateData.new_password = editedUser.new_password;
            }

            await api.updateCurrentUser(updateData);
            const updatedUser = await api.getCurrentUser();
            user.set(updatedUser);
            editMode = false;
            showPasswordFields = false;
            success = $_("profile.updateSuccess");

            // Clear password fields
            editedUser.current_password = "";
            editedUser.new_password = "";
            editedUser.confirm_password = "";
        } catch (err: any) {
            error = err.message || $_("profile.updateError");
            console.error(err);
        } finally {
            loading = false;
        }
    }
</script>

<div class="py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="md:grid md:grid-cols-3 md:gap-6">
            <div class="md:col-span-1">
                <div class="px-4 sm:px-0">
                    <h3 class="text-lg font-medium leading-6 text-gray-900">
                        {$_("profile.title")}
                    </h3>
                    <p class="mt-1 text-sm text-gray-600">
                        {$_("profile.personalInfo")}
                    </p>
                </div>
            </div>

            <div class="mt-5 md:mt-0 md:col-span-2">
                <div class="shadow sm:rounded-md sm:overflow-hidden">
                    <div class="px-4 py-5 bg-white space-y-6 sm:p-6">
                        <!-- Avatar Section -->
                        <div>
                            <div class="flex items-center">
                                <div
                                    class="h-20 w-20 rounded-full bg-primary-600 flex items-center justify-center text-2xl font-bold text-white"
                                >
                                    {$user?.name?.[0]?.toUpperCase() ||
                                        $user?.username?.[0]?.toUpperCase() ||
                                        "U"}
                                </div>
                                <div class="ml-6">
                                    <h2 class="text-xl font-bold text-gray-900">
                                        {$user?.name || "No name set"}
                                    </h2>
                                    <p class="text-sm text-gray-500">
                                        {$user?.username}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <!-- Account Info -->
                        <div class="border-t border-gray-200 pt-6">
                            <dl class="divide-y divide-gray-200">
                                <div
                                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4"
                                >
                                    <dt
                                        class="text-sm font-medium text-gray-500"
                                    >
                                        {$_("auth.email")}
                                    </dt>
                                    <dd
                                        class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
                                    >
                                        {$user?.username}
                                    </dd>
                                </div>

                                <div
                                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4"
                                >
                                    <dt
                                        class="text-sm font-medium text-gray-500"
                                    >
                                        {$_("profile.role")}
                                    </dt>
                                    <dd
                                        class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
                                    >
                                        <span
                                            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize
                                            {$user?.role === 'admin'
                                                ? 'bg-purple-100 text-purple-800'
                                                : 'bg-green-100 text-green-800'}"
                                        >
                                            {$user?.role}
                                        </span>
                                    </dd>
                                </div>

                                <div
                                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4"
                                >
                                    <dt
                                        class="text-sm font-medium text-gray-500"
                                    >
                                        {$_("profile.accountStatus")}
                                    </dt>
                                    <dd
                                        class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
                                    >
                                        <span
                                            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                            {$user?.is_active
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-red-100 text-red-800'}"
                                        >
                                            {$user?.is_active
                                                ? $_("profile.statusActive")
                                                : $_("profile.statusInactive")}
                                        </span>
                                    </dd>
                                </div>

                                <div
                                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4"
                                >
                                    <dt
                                        class="text-sm font-medium text-gray-500"
                                    >
                                        {$_("profile.memberSince")}
                                    </dt>
                                    <dd
                                        class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
                                    >
                                        {new Date(
                                            $user?.created_at || "",
                                        ).toLocaleDateString()}
                                    </dd>
                                </div>

                                {#if editMode}
                                    <div class="py-4">
                                        <form
                                            on:submit={handleUpdateProfile}
                                            class="space-y-4"
                                        >
                                            <div>
                                                <label
                                                    for="name"
                                                    class="block text-sm font-medium text-gray-700"
                                                >
                                                    {$_("profile.name")}
                                                </label>
                                                <input
                                                    type="text"
                                                    id="name"
                                                    bind:value={editedUser.name}
                                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                                />
                                            </div>

                                            <div class="flex items-center">
                                                <button
                                                    type="button"
                                                    on:click={() =>
                                                        (showPasswordFields =
                                                            !showPasswordFields)}
                                                    class="text-primary-600 hover:text-primary-500 text-sm font-medium"
                                                >
                                                    {showPasswordFields
                                                        ? $_(
                                                              "profile.cancelPasswordChange",
                                                          )
                                                        : $_(
                                                              "profile.changePassword",
                                                          )}
                                                </button>
                                            </div>

                                            {#if showPasswordFields}
                                                <div class="space-y-4">
                                                    <div>
                                                        <label
                                                            for="current_password"
                                                            class="block text-sm font-medium text-gray-700"
                                                        >
                                                            {$_(
                                                                "profile.currentPassword",
                                                            )}
                                                        </label>
                                                        <input
                                                            type="password"
                                                            id="current_password"
                                                            bind:value={editedUser.current_password}
                                                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                                        />
                                                    </div>

                                                    <div>
                                                        <label
                                                            for="new_password"
                                                            class="block text-sm font-medium text-gray-700"
                                                        >
                                                            {$_(
                                                                "profile.newPassword",
                                                            )}
                                                        </label>
                                                        <input
                                                            type="password"
                                                            id="new_password"
                                                            bind:value={editedUser.new_password}
                                                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                                        />
                                                    </div>

                                                    <div>
                                                        <label
                                                            for="confirm_password"
                                                            class="block text-sm font-medium text-gray-700"
                                                        >
                                                            {$_(
                                                                "profile.confirmPassword",
                                                            )}
                                                        </label>
                                                        <input
                                                            type="password"
                                                            id="confirm_password"
                                                            bind:value={editedUser.confirm_password}
                                                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                                        />
                                                    </div>
                                                </div>
                                            {/if}

                                            <div
                                                class="flex justify-end space-x-3"
                                            >
                                                <button
                                                    type="button"
                                                    on:click={() =>
                                                        (editMode = false)}
                                                    class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                                                >
                                                    {$_("common.cancel")}
                                                </button>
                                                <button
                                                    type="submit"
                                                    disabled={loading}
                                                    class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                                                >
                                                    {#if loading}
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
                                                        {$_("common.saving")}
                                                    {:else}
                                                        {$_(
                                                            "common.saveChanges",
                                                        )}
                                                    {/if}
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                {:else}
                                    <div class="py-4">
                                        <button
                                            on:click={() => {
                                                editedUser.name =
                                                    $user?.name || "";
                                                editMode = true;
                                            }}
                                            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                                        >
                                            {$_("profile.editProfile")}
                                        </button>
                                    </div>
                                {/if}
                            </dl>
                        </div>
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
                                    {error}
                                </p>
                            </div>
                        </div>
                    </div>
                {/if}

                {#if success}
                    <div class="mt-4 rounded-md bg-green-50 p-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <svg
                                    class="h-5 w-5 text-green-400"
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                >
                                    <path
                                        fill-rule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                        clip-rule="evenodd"
                                    />
                                </svg>
                            </div>
                            <div class="ml-3">
                                <p class="text-sm font-medium text-green-800">
                                    {success}
                                </p>
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    </div>
</div>
