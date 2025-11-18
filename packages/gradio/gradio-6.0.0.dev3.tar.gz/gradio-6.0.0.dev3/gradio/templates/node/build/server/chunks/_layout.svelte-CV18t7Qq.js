import { a0 as run, w as setContext, a1 as noop, a2 as hasContext, a3 as getContext, a4 as getAllContexts, a5 as createContext, a6 as ssr_context } from './async-lbsxUSUV.js';
import { g as getAbortSignal, l as lifecycle_function_unavailable, s as slot } from './index5-fDzIzGoO.js';
import './browser-fallback-CYSLhaFr.js';

function createRawSnippet(fn) {
  return (renderer, ...args) => {
    var getters = (
      /** @type {Getters<Params>} */
      args.map((value) => () => value)
    );
    renderer.push(
      fn(...getters).render().trim()
    );
  };
}
function onDestroy(fn) {
  /** @type {SSRContext} */
  ssr_context.r.on_destroy(fn);
}
function createEventDispatcher() {
  return noop;
}
function mount() {
  lifecycle_function_unavailable("mount");
}
function hydrate() {
  lifecycle_function_unavailable("hydrate");
}
function unmount() {
  lifecycle_function_unavailable("unmount");
}
function fork() {
  lifecycle_function_unavailable("fork");
}
async function tick() {
}
async function settled() {
}
const svelte = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  afterUpdate: noop,
  beforeUpdate: noop,
  createContext,
  createEventDispatcher,
  createRawSnippet,
  flushSync: noop,
  fork,
  getAbortSignal,
  getAllContexts,
  getContext,
  hasContext,
  hydrate,
  mount,
  onDestroy,
  onMount: noop,
  setContext,
  settled,
  tick,
  unmount,
  untrack: run
}, Symbol.toStringTag, { value: "Module" }));

const is_browser = typeof window !== "undefined";
if (is_browser) {
  const o = {
    SvelteComponent: void 0
  };
  for (const key in svelte) {
    if (key === "SvelteComponent") continue;
    if (key === "SvelteComponentDev") {
      o[key] = o["SvelteComponent"];
    } else {
      o[key] = svelte[key];
    }
  }
  window.__gradio__svelte__internal = o;
  window.__gradio__svelte__internal["globals"] = {};
  window.globals = window;
}
function _layout($$renderer, $$props) {
  $$renderer.push(`<!--[-->`);
  slot($$renderer, $$props, "default", {});
  $$renderer.push(`<!--]-->`);
}

export { _layout as default };
//# sourceMappingURL=_layout.svelte-CV18t7Qq.js.map
