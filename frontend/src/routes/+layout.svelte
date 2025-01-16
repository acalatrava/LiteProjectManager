<script lang="ts">
    import "../app.css";
    import { page } from "$app/stores";
    import { user, isAuthenticated } from "$lib/stores/auth";
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { api } from "$lib/services/api";
    import "$lib/i18n"; // Import i18n configuration
    import { _, isLoading } from "svelte-i18n"; // Import isLoading store

    let isMenuOpen = false;
    let userMenuButton: HTMLButtonElement;

    // Click outside handler
    function handleClickOutside(event: MouseEvent) {
        if (
            isMenuOpen &&
            userMenuButton &&
            !userMenuButton.contains(event.target as Node)
        ) {
            isMenuOpen = false;
        }
    }

    // Separate async function for checking auth
    async function checkAuth() {
        const token = localStorage.getItem("token");
        if (token) {
            try {
                const userData = await api.getCurrentUser();
                user.set(userData);
            } catch (error) {
                console.error("Error fetching user info:", error);
                localStorage.removeItem("token");
            }
        }
    }

    onMount(() => {
        // Add click outside listener
        document.addEventListener("click", handleClickOutside);

        // Check auth token
        checkAuth();

        // Cleanup listener on component destroy
        return () => {
            document.removeEventListener("click", handleClickOutside);
        };
    });

    function logout() {
        localStorage.removeItem("token");
        user.set(null);
        isMenuOpen = false;
        goto("/login");
    }

    function toggleMenu(event: MouseEvent) {
        event.stopPropagation();
        isMenuOpen = !isMenuOpen;
    }

    // Handle navigation and close menu
    function handleNavigation() {
        isMenuOpen = false;
    }
</script>

{#if $isLoading}
    <div class="min-h-screen flex items-center justify-center">
        <p>Loading...</p>
    </div>
{:else}
    <div class="min-h-screen flex flex-col">
        <nav class="bg-white shadow-lg">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex">
                        <div class="flex-shrink-0 flex items-center">
                            <a
                                href="/"
                                class="text-xl font-bold text-primary-600"
                            >
                                {$_("common.appName")}
                            </a>
                        </div>
                    </div>

                    <!-- Desktop menu -->
                    <div class="hidden sm:flex sm:items-center sm:space-x-4">
                        {#if $user}
                            {#if $user?.role === "admin"}
                                <a
                                    href="/admin"
                                    class="px-3 py-2 rounded-md text-sm font-medium {$page
                                        .url.pathname === '/admin'
                                        ? 'bg-primary-100 text-primary-700'
                                        : 'text-gray-700 hover:bg-gray-100'}"
                                >
                                    {$_("common.admin")}
                                </a>
                            {/if}
                            <a
                                href="/projects"
                                class="px-3 py-2 rounded-md text-sm font-medium {$page
                                    .url.pathname === '/projects'
                                    ? 'bg-primary-100 text-primary-700'
                                    : 'text-gray-700 hover:bg-gray-100'}"
                            >
                                {$_("common.projects")}
                            </a>
                            <div class="relative ml-3">
                                <button
                                    type="button"
                                    bind:this={userMenuButton}
                                    class="flex items-center max-w-xs rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                                    on:click={toggleMenu}
                                >
                                    <span class="sr-only">Open user menu</span>
                                    <div
                                        class="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white"
                                    >
                                        {$user?.name?.[0]?.toUpperCase() ||
                                            $user?.username?.[0]?.toUpperCase() ||
                                            "U"}
                                    </div>
                                </button>
                                {#if isMenuOpen}
                                    <div
                                        class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none"
                                        role="menu"
                                    >
                                        <div class="py-1" role="none">
                                            <a
                                                href="/profile"
                                                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                role="menuitem"
                                                on:click={handleNavigation}
                                            >
                                                {$_("common.profile")}
                                            </a>
                                            <button
                                                on:click={logout}
                                                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                role="menuitem"
                                            >
                                                {$_("common.logout")}
                                            </button>
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        {:else}
                            <a
                                href="/login"
                                class="px-4 py-2 text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
                            >
                                {$_("auth.signIn")}
                            </a>
                            <a
                                href="/register"
                                class="px-4 py-2 text-sm font-medium rounded-md text-primary-600 bg-white border border-primary-600 hover:bg-primary-50"
                            >
                                {$_("auth.signUp")}
                            </a>
                        {/if}
                    </div>

                    <!-- Mobile menu button -->
                    <div class="flex items-center sm:hidden">
                        <button
                            type="button"
                            class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
                            on:click={toggleMenu}
                        >
                            <span class="sr-only">Open main menu</span>
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
                                    d="M4 6h16M4 12h16M4 18h16"
                                />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Mobile menu -->
            {#if isMenuOpen}
                <div class="sm:hidden">
                    <div class="pt-2 pb-3 space-y-1">
                        {#if isAuthenticated()}
                            {#if $user?.role === "admin"}
                                <a
                                    href="/admin"
                                    class="block px-3 py-2 rounded-md text-base font-medium {$page
                                        .url.pathname === '/admin'
                                        ? 'bg-primary-100 text-primary-700'
                                        : 'text-gray-700 hover:bg-gray-100'}"
                                >
                                    {$_("common.admin")}
                                </a>
                            {/if}
                            <a
                                href="/projects"
                                class="block px-3 py-2 rounded-md text-base font-medium {$page
                                    .url.pathname === '/projects'
                                    ? 'bg-primary-100 text-primary-700'
                                    : 'text-gray-700 hover:bg-gray-100'}"
                            >
                                {$_("common.dashboard")}
                            </a>
                            <a
                                href="/profile"
                                class="block px-3 py-2 rounded-md text-base font-medium {$page
                                    .url.pathname === '/profile'
                                    ? 'bg-primary-100 text-primary-700'
                                    : 'text-gray-700 hover:bg-gray-100'}"
                            >
                                {$_("common.profile")}
                            </a>
                            <button
                                on:click={logout}
                                class="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
                            >
                                {$_("common.logout")}
                            </button>
                        {:else}
                            <a
                                href="/login"
                                class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
                            >
                                {$_("auth.signIn")}
                            </a>
                            <a
                                href="/register"
                                class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
                            >
                                {$_("auth.signUp")}
                            </a>
                        {/if}
                    </div>
                </div>
            {/if}
        </nav>

        <main class="flex-1 max-w-7xl w-full mx-auto py-6 sm:px-6 lg:px-8">
            <slot />
        </main>

        <footer class="bg-white mt-auto border-t border-gray-200">
            <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
                <div class="md:flex md:items-center md:justify-between">
                    <div class="flex space-x-6 md:order-2">
                        <a
                            href="https://github.com/acalatrava/LiteProjectManager"
                            class="text-gray-400 hover:text-gray-500"
                        >
                            <span class="sr-only">GitHub</span>
                            <svg
                                class="h-6 w-6"
                                fill="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                        </a>
                    </div>
                    <p class="mt-8 text-base text-gray-400 md:mt-0 md:order-1">
                        &copy; 2025 Antonio Calatrava - Iberovalia Invex SL -
                        MIT Licensed
                    </p>
                </div>
            </div>
        </footer>
    </div>
{/if}
