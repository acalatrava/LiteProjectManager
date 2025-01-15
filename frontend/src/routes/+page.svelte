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
                                href="/dashboard"
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
                                    <!-- Heroicon name: outline/search -->
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
                                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                                        />
                                    </svg>
                                </div>
                                <p
                                    class="ml-16 text-lg leading-6 font-medium text-gray-900"
                                >
                                    {$_("landing.features.search.title")}
                                </p>
                            </dt>
                            <dd class="mt-2 ml-16 text-base text-gray-500">
                                {$_("landing.features.search.description")}
                            </dd>
                        </div>

                        <div class="relative">
                            <dt>
                                <div
                                    class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white"
                                >
                                    <!-- Heroicon name: outline/shield-check -->
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
                                            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                                        />
                                    </svg>
                                </div>
                                <p
                                    class="ml-16 text-lg leading-6 font-medium text-gray-900"
                                >
                                    {$_("landing.features.security.title")}
                                </p>
                            </dt>
                            <dd class="mt-2 ml-16 text-base text-gray-500">
                                {$_("landing.features.security.description")}
                            </dd>
                        </div>

                        <div class="relative">
                            <dt>
                                <div
                                    class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white"
                                >
                                    <!-- Heroicon name: outline/chart-bar -->
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
                                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                                        />
                                    </svg>
                                </div>
                                <p
                                    class="ml-16 text-lg leading-6 font-medium text-gray-900"
                                >
                                    {$_("landing.features.analytics.title")}
                                </p>
                            </dt>
                            <dd class="mt-2 ml-16 text-base text-gray-500">
                                {$_("landing.features.analytics.description")}
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
