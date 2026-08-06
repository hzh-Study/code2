<template>
  <view class="ui-state" :class="`is-${type}`" role="status" aria-live="polite">
    <view class="ui-state-mark" aria-hidden="true">{{ mark }}</view>
    <view class="ui-state-title">{{ title }}</view>
    <view v-if="description" class="ui-state-copy">{{ description }}</view>
    <view v-if="actionText" class="ui-state-action" role="button" tabindex="0" @click="$emit('action')" @keydown.enter="$emit('action')">{{ actionText }}</view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, default: 'empty' },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  actionText: { type: String, default: '' }
})

defineEmits(['action'])

const mark = computed(() => ({ loading: '···', error: '!', success: '✓', empty: '—' })[props.type] || '—')
</script>

<style scoped>
.ui-state { min-height: 260px; padding: 44px 20px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--c-text-secondary); text-align: center; }
.ui-state-mark { width: 48px; height: 48px; margin-bottom: 18px; display: flex; align-items: center; justify-content: center; border: 2px solid var(--c-border-strong); border-radius: 50%; color: var(--c-text-secondary); font-size: var(--font-lg); font-weight: 800; }
.is-loading .ui-state-mark { border-style: dashed; color: var(--c-primary-dark); }
.is-error .ui-state-mark { border-color: var(--c-danger); color: var(--c-danger); }
.is-success .ui-state-mark { border-color: var(--c-success); color: var(--c-success); }
.ui-state-title { color: var(--c-text); font-size: var(--font-md); font-weight: 800; }
.ui-state-copy { max-width: 280px; margin-top: 6px; color: var(--c-text-secondary); font-size: var(--font-xs); }
.ui-state-action { min-width: 116px; height: 44px; margin-top: 22px; padding: 0 18px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border-radius: var(--r-md); background: var(--c-primary); color: var(--c-text-inverse); font-weight: 700; }
</style>
