<script lang="ts">
    import { goto } from "$app/navigation";
    import { user } from "$lib/stores/auth";
    import { api } from "$lib/services/api";
    import { _ } from "svelte-i18n";

    let username = "";
    let password = "";
    let error = "";
    let loading = false;

    async function handleSubmit() {
        loading = true;
        error = "";
        try {
            const authResponse = await api.login(username, password);
            localStorage.setItem("token", authResponse.access_token);

            const userData = await api.getCurrentUser();
            user.set(userData);
            goto("/projects");
        } catch (err) {
            error = "Invalid credentials";
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
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {$_("auth.loginTitle")}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
            {$_("auth.noAccount")}
            <a
                href="/register"
                class="font-medium text-primary-600 hover:text-primary-500"
            >
                {$_("auth.signUp")}
            </a>
        </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <form on:submit|preventDefault={handleSubmit} class="space-y-6">
                <div>
                    <label
                        for="username"
                        class="block text-sm font-medium text-gray-700"
                    >
                        {$_("auth.email")}
                    </label>
                    <div class="mt-1">
                        <input
                            id="username"
                            type="email"
                            bind:value={username}
                            required
                            class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        />
                    </div>
                </div>

                <div>
                    <label
                        for="password"
                        class="block text-sm font-medium text-gray-700"
                    >
                        {$_("auth.password")}
                    </label>
                    <div class="mt-1">
                        <input
                            id="password"
                            type="password"
                            bind:value={password}
                            required
                            class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
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
                            {$_("auth.signIn")}
                        {/if}
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
