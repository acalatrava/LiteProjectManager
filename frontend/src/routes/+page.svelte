<script lang="ts">
    import { isAuthenticated } from "$lib/stores/auth";
    import { _ } from "svelte-i18n";
</script>

<div class="relative overflow-hidden">
    <!-- Hero section -->
    <div class="relative pt-6 pb-16 sm:pb-24">
        <main class="mt-16 mx-auto max-w-7xl px-4 sm:mt-24">
            <div class="text-center">
                <h1
                    class="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl"
                >
                    <span class="block">{$_("landing.hero.title1")}</span>
                    <span class="block text-primary-600"
                        >{$_("landing.hero.title2")}</span
                    >
                </h1>
                <p
                    class="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl"
                >
                    {$_("landing.hero.description")}
                </p>
                <div
                    class="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8"
                >
                    {#if !isAuthenticated()}
                        <div class="rounded-md shadow">
                            <a
                                href="/register"
                                class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-lg md:px-10"
                            >
                                {$_("landing.hero.getStarted")}
                            </a>
                        </div>
                        <div class="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                            <a
                                href="/login"
                                class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-primary-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
                            >
                                {$_("common.login")}
                            </a>
                        </div>
                    {:else}
                        <div class="rounded-md shadow">
                            <a
                                href="/projects"
                                class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-lg md:px-10"
                            >
                                {$_("landing.hero.dashboard")}
                            </a>
                        </div>
                    {/if}
                </div>
            </div>
        </main>
    </div>

    <!-- Features section -->
    <div class="py-16 bg-gray-50 overflow-hidden lg:py-24">
        <div
            class="relative max-w-xl mx-auto px-4 sm:px-6 lg:px-8 lg:max-w-7xl"
        >
            <div class="relative">
                <h2
                    class="text-center text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl"
                >
                    {$_("landing.features.title")}
                </h2>
                <p
                    class="mt-4 max-w-3xl mx-auto text-center text-xl text-gray-500"
                >
                    {$_("landing.features.description")}
                </p>
            </div>

            <div
                class="relative mt-12 lg:mt-24 lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center"
            >
                <div class="relative">
                    <h3
                        class="text-2xl font-extrabold text-gray-900 tracking-tight sm:text-3xl"
                    >
                        {$_("landing.features.powerfulFeatures.title")}
                    </h3>
                    <p class="mt-3 text-lg text-gray-500">
                        {$_("landing.features.powerfulFeatures.description")}
                    </p>

                    <dl class="mt-10 space-y-10">
                        <div class="relative">
                            <dt>
                                <div
                                    class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white"
                                >
                                    <!-- Heroicon name: outline/clipboard-list -->
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
                                            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                                        />
                                    </svg>
                                </div>
                                <p
                                    class="ml-16 text-lg leading-6 font-medium text-gray-900"
                                >
                                    {$_("landing.features.tasks.title")}
                                </p>
                            </dt>
                            <dd class="mt-2 ml-16 text-base text-gray-500">
                                {$_("landing.features.tasks.description")}
                            </dd>
                        </div>

                        <div class="relative">
                            <dt>
                                <div
                                    class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white"
                                >
                                    <!-- Heroicon name: outline/users -->
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
                                            d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                                        />
                                    </svg>
                                </div>
                                <p
                                    class="ml-16 text-lg leading-6 font-medium text-gray-900"
                                >
                                    {$_("landing.features.teams.title")}
                                </p>
                            </dt>
                            <dd class="mt-2 ml-16 text-base text-gray-500">
                                {$_("landing.features.teams.description")}
                            </dd>
                        </div>

                        <div class="relative">
                            <dt>
                                <div
                                    class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white"
                                >
                                    <!-- Heroicon name: outline/calendar -->
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
                                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                                        />
                                    </svg>
                                </div>
                                <p
                                    class="ml-16 text-lg leading-6 font-medium text-gray-900"
                                >
                                    {$_("landing.features.timeline.title")}
                                </p>
                            </dt>
                            <dd class="mt-2 ml-16 text-base text-gray-500">
                                {$_("landing.features.timeline.description")}
                            </dd>
                        </div>
                    </dl>
                </div>

                <div class="mt-10 -mx-4 relative lg:mt-0">
                    <div class="relative space-y-4">
                        <div
                            class="flex items-end justify-center lg:justify-start space-x-4"
                        >
                            <div class="flex-shrink-0 w-32 lg:w-64">
                                <div
                                    class="h-32 bg-primary-100 rounded-lg shadow-lg"
                                ></div>
                            </div>
                            <div class="flex-shrink-0 w-48 lg:w-96">
                                <div
                                    class="h-48 bg-primary-200 rounded-lg shadow-lg"
                                ></div>
                            </div>
                        </div>
                        <div
                            class="flex items-start justify-center lg:justify-start space-x-4 ml-12"
                        >
                            <div class="flex-shrink-0 w-48 lg:w-96">
                                <div
                                    class="h-48 bg-primary-300 rounded-lg shadow-lg"
                                ></div>
                            </div>
                            <div class="flex-shrink-0 w-32 lg:w-64">
                                <div
                                    class="h-32 bg-primary-100 rounded-lg shadow-lg"
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- CTA section -->
    <div class="bg-primary-700">
        <div
            class="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8"
        >
            <h2 class="text-3xl font-extrabold text-white sm:text-4xl">
                <span class="block">{$_("landing.cta.title1")}</span>
                <span class="block">{$_("landing.cta.title2")}</span>
            </h2>
            <p class="mt-4 text-lg leading-6 text-primary-200">
                {$_("landing.cta.description")}
            </p>
            <a
                href="/register"
                class="mt-8 w-full inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-primary-600 bg-white hover:bg-primary-50 sm:w-auto"
            >
                {$_("landing.cta.button")}
            </a>
        </div>
    </div>
</div>

<style>
    .home {
        max-width: 800px;
        margin: 0 auto;
        text-align: center;
        padding: 2rem;
    }

    h1 {
        margin-bottom: 1rem;
    }
</style>
