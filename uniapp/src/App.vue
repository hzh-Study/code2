<script setup>
import { onLaunch } from '@dcloudio/uni-app'
import { loginIfNeeded } from './store/user'

onLaunch(() => {
  // 启动即静默登录（开发模式/微信均兼容）
  loginIfNeeded().catch(() => {})
})
</script>

<style>
page {
  --c-primary: #e85d2c;
  --c-primary-light: #f06f42;
  --c-primary-dark: #bd431c;
  --c-primary-bg: #fff0e9;
  --c-accent: #9a6400;
  --c-accent-bg: #fff7df;
  --c-success: #2f7d4a;
  --c-success-bg: #edf7f0;
  --c-warning: #9a6400;
  --c-warning-bg: #fff7df;
  --c-danger: #b42318;
  --c-danger-bg: #fff0ee;
  --c-info: #3f6475;
  --c-info-bg: #eef4f6;
  --c-text: #2b2b2b;
  --c-text-secondary: #5f5a54;
  --c-text-placeholder: #918a82;
  --c-text-disabled: #9e978f;
  --c-text-inverse: #ffffff;
  --c-bg: #faf7f2;
  --c-bg-card: #ffffff;
  --c-bg-soft: #f7f3ed;
  --c-bg-disabled: #f0ece6;
  --c-border: #d9d2c8;
  --c-border-light: #e9e3da;
  --c-border-strong: #b8aea2;
  --c-focus: #bd431c;
  --c-focus-ring: rgba(232, 93, 44, 0.28);
  --c-shadow: rgba(43, 43, 43, 0.06);
  --c-shadow-md: rgba(43, 43, 43, 0.1);
  --c-bar-bg: var(--c-primary);
  --font-xs: 12px;
  --font-sm: 13px;
  --font-base: 14px;
  --font-md: 16px;
  --font-lg: 18px;
  --font-xl: 22px;
  --font-xxl: 28px;
  --sp-4: 4px;
  --sp-8: 8px;
  --sp-10: 10px;
  --sp-12: 12px;
  --sp-16: 16px;
  --sp-20: 20px;
  --sp-24: 24px;

  --r-sm: 6px;
  --r-md: 8px;
  --r-lg: 12px;
  --r-xl: 16px;
  --r-full: 999px;
  --shadow-sm: 0 2px 8px var(--c-shadow);
  --shadow-md: 0 6px 18px var(--c-shadow-md);
  --shadow-lg: 0 12px 32px var(--c-shadow-md);
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --duration-fast: 120ms;
  --duration-normal: 200ms;
  --duration-slow: 320ms;
  background: var(--c-bg);
  color: var(--c-text);
  font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
  font-size: var(--font-base);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -webkit-tap-highlight-color: transparent;
}

image {
  display: block;
}

button,
input,
textarea {
  font: inherit;
}

button {
  border-radius: var(--r-md);
  transition: color var(--duration-fast) var(--ease), background-color var(--duration-fast) var(--ease), border-color var(--duration-fast) var(--ease), opacity var(--duration-fast) var(--ease), transform var(--duration-fast) var(--ease);
}

button::after {
  border: 0;
}

button:active:not([disabled]),
[role='button']:active:not(.disabled):not(.is-disabled),
.button:active:not(.disabled):not(.is-disabled),
.btn:active:not(.disabled):not(.is-disabled) {
  opacity: 0.86;
  transform: scale(0.98);
}

button[disabled],
.disabled,
.is-disabled {
  color: var(--c-text-disabled);
  background: var(--c-bg-disabled);
  border-color: var(--c-border-light);
  box-shadow: none;
  opacity: 0.62;
}

.is-loading,
button[loading] {
  cursor: progress;
  pointer-events: none;
  opacity: 0.72;
}

.disabled,
.is-disabled,
[aria-disabled='true'] {
  pointer-events: none;
}

.bottom-action-safe {
  position: fixed;
  right: 0;
  bottom: var(--window-bottom, 0px);
  left: 0;
  z-index: 20;
  padding-bottom: env(safe-area-inset-bottom);
  background: var(--c-bg-card);
  border-top: 1px solid var(--c-border-light);
}

.bottom-action-bar {
  min-height: 72px;
  padding: 0 12px;
  display: flex;
  align-items: center;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 9px;
  border: 1px solid currentColor;
  border-radius: var(--r-full);
  font-size: 10px;
  font-weight: 700;
}

.status-badge.status-1 { background: var(--c-warning-bg); color: var(--c-warning); }
.status-badge.status-2 { background: var(--c-primary-bg); color: var(--c-primary-dark); }
.status-badge.status-3 { background: var(--c-success-bg); color: var(--c-success); }
.status-badge.status-4 { background: var(--c-bg-soft); color: var(--c-text-secondary); }

input,
textarea {
  color: var(--c-text);
  background: var(--c-bg-card);
  border-color: var(--c-border);
  transition: border-color var(--duration-fast) var(--ease), box-shadow var(--duration-fast) var(--ease), background-color var(--duration-fast) var(--ease);
}

input:focus,
textarea:focus {
  border-color: var(--c-primary);
}

@media (hover: hover) and (pointer: fine) {
  button:hover:not([disabled]),
  [role='button']:hover:not(.disabled):not(.is-disabled),
  .button:hover:not(.disabled):not(.is-disabled),
  .btn:hover:not(.disabled):not(.is-disabled) {
    filter: brightness(0.96);
  }
}

@media (prefers-reduced-motion: reduce) {
  page {
    --duration-fast: 1ms;
    --duration-normal: 1ms;
    --duration-slow: 1ms;
  }

  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 1ms !important;
    transition-delay: 0ms !important;
  }
}

@media screen and (min-width: 0) {
  button:focus-visible,
  input:focus-visible,
  textarea:focus-visible,
  [tabindex]:focus-visible,
  [role='button']:focus-visible {
    outline: 2px solid var(--c-focus);
    outline-offset: 2px;
    box-shadow: 0 0 0 4px var(--c-focus-ring);
  }
}
</style>
