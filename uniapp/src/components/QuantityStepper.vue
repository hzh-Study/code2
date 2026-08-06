<template>
  <view class="quantity-stepper" :class="[size, { disabled }]" :aria-label="`${name}当前数量${modelValue}`">
    <view class="quantity-step" role="button" tabindex="0" :aria-label="`减少${name}`" :aria-disabled="disabled" @click="change(-1)" @keydown.enter="change(-1)">−</view>
    <text class="quantity-value" aria-live="polite">{{ modelValue }}</text>
    <view class="quantity-step primary" role="button" tabindex="0" :aria-label="`增加${name}`" :aria-disabled="disabled" @click="change(1)" @keydown.enter="change(1)">+</view>
  </view>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Number, default: 0 },
  name: { type: String, default: '菜品' },
  disabled: { type: Boolean, default: false },
  size: { type: String, default: 'default' }
})

const emit = defineEmits(['change'])

function change(delta) {
  if (!props.disabled) emit('change', delta)
}
</script>

<style scoped>
.quantity-stepper { height: 44px; display: flex; align-items: center; flex-shrink: 0; }
.quantity-step { width: 44px; height: 44px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 1px solid var(--c-border); border-radius: 50%; color: var(--c-primary-dark); font-size: 21px; }
.quantity-step.primary { border-color: var(--c-primary); background: var(--c-primary); color: var(--c-text-inverse); }
.quantity-value { width: 32px; text-align: center; font-weight: 700; }

.quantity-stepper.small { height: 32px; }
.quantity-stepper.small .quantity-step { width: 32px; height: 32px; font-size: 17px; }
.quantity-stepper.small .quantity-value { width: 24px; font-size: 14px; }
</style>
