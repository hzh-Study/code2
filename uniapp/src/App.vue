<script setup>
import { onLaunch } from '@dcloudio/uni-app'
import { loginIfNeeded } from './store/user'

onLaunch(() => {
  // 启动即静默登录（开发模式/微信均兼容）
  loginIfNeeded().catch(() => {})
})
</script>

<style>
/* ========== 设计变量 ========== */
page {
  /* 色板 */
  --c-primary: #e85d2c;
  --c-primary-light: #ff7a45;
  --c-primary-bg: #fff3ed;
  --c-accent: #f5a623;
  --c-accent-bg: #fef7e8;
  --c-success: #4caf50;
  --c-warning: #e8a33c;
  --c-danger: #e53935;
  --c-text: #3d2b1f;
  --c-text-secondary: #666666;
  --c-text-placeholder: #aaaaaa;
  --c-text-inverse: #ffffff;
  --c-bg: #f5f2ed;
  --c-bg-card: #ffffff;
  --c-bg-soft: #f7f3ee;
  --c-border: #ebe6df;
  --c-border-light: #f0ebe5;
  --c-shadow: rgba(61, 43, 31, 0.08);
  --c-shadow-md: rgba(61, 43, 31, 0.12);
  --c-bar-bg: linear-gradient(135deg, #c94a1e, #e85d2c);

  /* 字体 */
  --font-xs: 11px;
  --font-sm: 13px;
  --font-base: 15px;
  --font-md: 16px;
  --font-lg: 18px;
  --font-xl: 22px;
  --font-xxl: 26px;

  /* 间距 */
  --sp-4: 4px;
  --sp-8: 8px;
  --sp-10: 10px;
  --sp-12: 12px;
  --sp-16: 16px;
  --sp-20: 20px;
  --sp-24: 24px;

  /* 圆角 */
  --r-sm: 8px;
  --r-md: 12px;
  --r-lg: 16px;
  --r-xl: 20px;
  --r-full: 999px;

  /* 阴影 */
  --shadow-sm: 0 2px 8px var(--c-shadow);
  --shadow-md: 0 4px 16px var(--c-shadow-md);
  --shadow-lg: 0 8px 30px var(--c-shadow-md);

  /* 过渡 */
  --ease: cubic-bezier(0.4, 0, 0.2, 1);

  /* 排版 */
  background: var(--c-bg);
  color: var(--c-text);
  font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
  font-size: var(--font-base);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -webkit-tap-highlight-color: transparent;
}

/* 全局图片默认行为 */
image { display: block; }
</style>
