<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/services/api";
    import { user } from "$lib/stores/auth";
    import { _ } from "svelte-i18n";
    import { fade } from "svelte/transition";

    let loading = false;
    let error = "";
    let success = "";

    let formData = {
        name: $user?.name || "",
        email: $user?.username || "",
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
    };

    async function handleSubmit() {
        loading = true;
        error = "";
        success = "";

        try {
            if (formData.newPassword) {
                if (formData.newPassword !== formData.confirmPassword) {
                    throw new Error($_("profile.errors.passwordMismatch"));
                }
                if (!formData.currentPassword) {
                    throw new Error(
                        $_("profile.errors.currentPasswordRequired"),
                    );
                }
            }

            const updatedUser = await api.updateProfile({
                name: formData.name,
                email: formData.email,
                current_password: formData.currentPassword || undefined,
                new_password: formData.newPassword || undefined,
            });

            user.set(updatedUser);
            success = $_("profile.success.profileUpdated");

            // Reset password fields
            formData.currentPassword = "";
            formData.newPassword = "";
            formData.confirmPassword = "";
        } catch (err) {
            error = err.message || $_("profile.errors.updateFailed");
        } finally {
            loading = false;
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
            <h1 class="text-3xl font-bold text-white">
                {$_("profile.title")}
            </h1>
            <p class="mt-2 text-lg text-primary-100">
                {$_("profile.description")}
            </p>
        </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <!-- Profile Form -->
        <div class="lg:col-span-2">
            <div class="rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5">
                <form
                    on:submit|preventDefault={handleSubmit}
                    class="space-y-6 p-6"
                >
                    {#if error}
                        <div
                            class="rounded-lg bg-red-50 p-4 text-sm text-red-700"
                            transition:fade
                        >
                            {error}
                        </div>
                    {/if}

                    {#if success}
                        <div
                            class="rounded-lg bg-green-50 p-4 text-sm text-green-700"
                            transition:fade
                        >
                            {success}
                        </div>
                    {/if}

                    <!-- Basic Information -->
                    <div>
                        <h2 class="text-lg font-medium text-gray-900">
                            {$_("profile.sections.basicInfo")}
                        </h2>
                        <div class="mt-4 grid grid-cols-1 gap-6">
                            <div>
                                <label
                                    for="name"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("profile.fields.name")}
                                </label>
                                <input
                                    type="text"
                                    id="name"
                                    bind:value={formData.name}
                                    class="mt-1 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                />
                            </div>

                            <div>
                                <label
                                    for="email"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("profile.fields.email")}
                                </label>
                                <input
                                    type="email"
                                    id="email"
                                    value={formData.email}
                                    disabled
                                    class="mt-1 block w-full rounded-md border-0 py-1.5 text-gray-900 bg-gray-50 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>
                    </div>

                    <!-- Password Change -->
                    <div class="pt-6">
                        <h2 class="text-lg font-medium text-gray-900">
                            {$_("profile.sections.changePassword")}
                        </h2>
                        <div class="mt-4 grid grid-cols-1 gap-6">
                            <div>
                                <label
                                    for="currentPassword"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("profile.fields.currentPassword")}
                                </label>
                                <input
                                    type="password"
                                    id="currentPassword"
                                    bind:value={formData.currentPassword}
                                    class="mt-1 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                />
                            </div>

                            <div>
                                <label
                                    for="newPassword"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("profile.fields.newPassword")}
                                </label>
                                <input
                                    type="password"
                                    id="newPassword"
                                    bind:value={formData.newPassword}
                                    class="mt-1 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                />
                            </div>

                            <div>
                                <label
                                    for="confirmPassword"
                                    class="block text-sm font-medium text-gray-700"
                                >
                                    {$_("profile.fields.confirmPassword")}
                                </label>
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    bind:value={formData.confirmPassword}
                                    class="mt-1 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>
                    </div>

                    <div class="flex justify-end pt-6">
                        <button
                            type="submit"
                            disabled={loading}
                            class="inline-flex items-center rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
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
                            {/if}
                            {$_("profile.actions.save")}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Profile Summary -->
        <div class="space-y-6">
            <div class="rounded-xl bg-white shadow-sm ring-1 ring-gray-900/5">
                <div class="p-6">
                    <div class="flex items-center">
                        <div
                            class="h-16 w-16 rounded-full bg-primary-500 flex items-center justify-center text-2xl font-bold text-white"
                        >
                            {$user?.name?.[0]?.toUpperCase() ||
                                $user?.username?.[0]?.toUpperCase() ||
                                "U"}
                        </div>
                        <div class="ml-4">
                            <h2 class="text-lg font-medium text-gray-900">
                                {$user?.name || $user?.username}
                            </h2>
                            <p class="text-sm text-gray-500">
                                {$user?.email}
                            </p>
                            <p class="text-sm text-gray-500">
                                {$user?.role}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
