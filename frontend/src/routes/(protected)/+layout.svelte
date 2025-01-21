<script lang="ts">
    import { page } from "$app/stores";
    import { user } from "$lib/stores/auth";
    import { goto } from "$app/navigation";
    import { _ } from "svelte-i18n";
    import { fly } from "svelte/transition";

    let isSidebarOpen = false;

    const navigation = [
        {
            name: "Projects",
            href: "/projects",
            icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
        },
        {
            name: "Profile",
            href: "/profile",
            icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
        },
    ];

    if ($user?.role === "admin") {
        navigation.push({
            name: "Admin",
            href: "/admin",
            icon: "M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4",
        });
    }

    $: currentPath = $page.url.pathname;

    function logout() {
        localStorage.removeItem("token");
        user.set(null);
        isSidebarOpen = false;
        goto("/login");
    }
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <!-- Mobile sidebar backdrop -->
    {#if isSidebarOpen}
        <div
            class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-40 lg:hidden"
            on:click={() => (isSidebarOpen = false)}
            transition:fly={{ duration: 200, x: -100 }}
        ></div>
    {/if}

    <!-- Sidebar -->
    <div
        class={`fixed top-0 left-0 bottom-0 w-64 bg-white transform lg:translate-x-0 transition-transform duration-200 ease-in-out z-50 ${
            isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
    >
        <div class="h-full flex flex-col">
            <!-- Logo -->
            <div class="flex-shrink-0 px-4 py-6 flex items-center">
                <span class="ml-3 text-xl font-bold text-gray-900"
                    >Dashboard</span
                >
            </div>

            <!-- Navigation -->
            <nav class="flex-1 px-2 py-4 space-y-1">
                {#each navigation as item}
                    <a
                        href={item.href}
                        on:click={() => {
                            if (window.innerWidth < 1024) {
                                isSidebarOpen = false;
                            }
                        }}
                        class={`group flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 ${
                            currentPath.startsWith(item.href)
                                ? "bg-primary-50 text-primary-700 "
                                : "text-gray-700 hover:bg-gray-50 "
                        }`}
                    >
                        <svg
                            class={`mr-3 h-5 w-5 transition-colors duration-200 ${
                                currentPath.startsWith(item.href)
                                    ? "text-primary-500 "
                                    : "text-gray-400 group-hover:text-gray-500 "
                            }`}
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d={item.icon}
                            ></path>
                        </svg>
                        {item.name}
                    </a>
                {/each}
            </nav>

            <!-- User profile -->
            <div class="flex-shrink-0 p-4 border-t border-gray-200">
                <div class="flex items-center">
                    <div
                        class="h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold"
                    >
                        {$user?.name?.[0]?.toUpperCase() ||
                            $user?.username?.[0]?.toUpperCase() ||
                            "U"}
                    </div>
                    <div class="ml-3 flex-1">
                        <p class="text-sm font-medium text-gray-900">
                            {$user?.name || $user?.username}
                        </p>
                        <p class="text-xs text-gray-500">
                            {$user?.role}
                        </p>
                    </div>
                    <button
                        on:click={logout}
                        class="p-2 text-gray-500 hover:text-gray-700"
                        title={$_("common.logout")}
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
                                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                            />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Main content -->
    <div class="lg:pl-64">
        <!-- Top bar -->
        <div class="sticky top-0 z-10 flex h-16 bg-white/80">
            <button
                type="button"
                class="lg:hidden px-4 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
                on:click={() => (isSidebarOpen = true)}
            >
                <span class="sr-only">Open sidebar</span>
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

        <!-- Page content -->
        <main class="py-6">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <slot />
            </div>
        </main>
    </div>
</div>

<style>
    :global(body) {
        @apply antialiased;
    }
</style>
