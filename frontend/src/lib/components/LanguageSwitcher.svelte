<script lang="ts">
    import { locale } from "svelte-i18n";

    function switchLanguage(lang: string) {
        locale.set(lang);
    }
</script>

<div class="flex gap-2">
    <button
        class="px-2 py-1 rounded {$locale === 'en'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200'}"
        on:click={() => switchLanguage("en")}
    >
        EN
    </button>
    <button
        class="px-2 py-1 rounded {$locale === 'es'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200'}"
        on:click={() => switchLanguage("es")}
    >
        ES
    </button>
</div>
