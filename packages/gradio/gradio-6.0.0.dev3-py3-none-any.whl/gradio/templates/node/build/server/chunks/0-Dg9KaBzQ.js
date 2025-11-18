import { r as redirect } from './index-Djsj11qr.js';
import { d as dev } from './index4-DpKVuxl4.js';
import './browser-fallback-CYSLhaFr.js';

function load({ url }) {
  const { pathname, search } = url;
  if (dev && url.pathname.startsWith("/theme")) {
    redirect(308, `http://127.0.0.1:7860${pathname}${search}`);
  }
}

var _layout_server_ts = /*#__PURE__*/Object.freeze({
  __proto__: null,
  load: load
});

const index = 0;
let component_cache;
const component = async () => component_cache ??= (await import('./_layout.svelte-CV18t7Qq.js')).default;
const server_id = "src/routes/+layout.server.ts";
const imports = ["_app/immutable/nodes/0.ClU7Boea.js","_app/immutable/chunks/9B4_veAf.js","_app/immutable/chunks/DEzry6cj.js","_app/immutable/chunks/BAp-OWo-.js","_app/immutable/chunks/DX-MI-YE.js"];
const stylesheets = ["_app/immutable/assets/0.DbYgK2MM.css"];
const fonts = [];

export { component, fonts, imports, index, _layout_server_ts as server, server_id, stylesheets };
//# sourceMappingURL=0-Dg9KaBzQ.js.map
