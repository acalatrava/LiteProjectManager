<script lang="ts">
    import { goto } from "$app/navigation";
    import { user, passwordResetRequired } from "$lib/stores/auth";
    import { api } from "$lib/services/api";
    import { _ } from "svelte-i18n";

    let newPassword = "";
    let confirmPassword = "";
    let error = "";
    let loading = false;

    async function handleSubmit() {
        error = "";

        if (newPassword.length < 8) {
            error = $_("changePassword.errors.tooShort");
            return;
        }

        if (newPassword !== confirmPassword) {
            error = $_("changePassword.errors.mismatch");
            return;
        }

        loading = true;
        try {
            await api.updateProfile({ new_password: newPassword } as any);

            // Password change invalidates all tokens, so re-login to get a fresh one
            const username = $user?.username;
            if (username) {
                const authResponse = await api.login(username, newPassword);
                localStorage.setItem("token", authResponse.access_token);

                const userData = await api.getCurrentUser();
                user.set(userData);
            }

            passwordResetRequired.set(false);
            goto("/projects");
        } catch (err: any) {
            error = err.message || $_("changePassword.errors.failed");
            console.error(err);
        } finally {
            loading = false;
        }
    }
</script>

<div
    class="min-h-[80vh] flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-gray-50"
>
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
            <svg
                class="h-6 w-6 text-yellow-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
            </svg>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {$_("changePassword.title")}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
            {$_("changePassword.description")}
        </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <form on:submit|preventDefault={handleSubmit} class="space-y-6">
                <div>
                    <label
                        for="new-password"
                        class="block text-sm font-medium text-gray-700"
                    >
                        {$_("changePassword.newPassword")}
                    </label>
                    <div class="mt-1">
                        <input
                            id="new-password"
                            type="password"
                            bind:value={newPassword}
                            required
                            minlength="8"
                            class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                            placeholder="••••••••"
                        />
                    </div>
                    <p class="mt-1 text-sm text-gray-500">
                        {$_("changePassword.hint")}
                    </p>
                </div>

                <div>
                    <label
                        for="confirm-password"
                        class="block text-sm font-medium text-gray-700"
                    >
                        {$_("changePassword.confirmPassword")}
                    </label>
                    <div class="mt-1">
                        <input
                            id="confirm-password"
                            type="password"
                            bind:value={confirmPassword}
                            required
                            minlength="8"
                            class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                            placeholder="••••••••"
                        />
                    </div>
                </div>

                {#if error}
                    <div class="rounded-md bg-red-50 p-4">
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

                <div>
                    <button
                        type="submit"
                        disabled={loading}
                        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {#if loading}
                            <svg
                                class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
                            {$_("common.loading")}
                        {:else}
                            {$_("changePassword.submit")}
                        {/if}
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
