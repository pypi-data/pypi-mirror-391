import "../chunks/9B4_veAf.js";
import "../chunks/BAp-OWo-.js";
import { aP as svelte, D as comment, v as first_child, b as append } from "../chunks/DEzry6cj.js";
import { s as slot } from "../chunks/DX-MI-YE.js";
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
function _layout($$anchor, $$props) {
  var fragment = comment();
  var node = first_child(fragment);
  slot(node, $$props, "default", {}, null);
  append($$anchor, fragment);
}
export {
  _layout as component
};
//# sourceMappingURL=0.ClU7Boea.js.map
