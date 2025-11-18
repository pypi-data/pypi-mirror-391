import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, c as from_html, d as child, r as reset, z as event, b as append, o as pop, y as untrack, k as get, A as user_derived } from "./DEzry6cj.js";
import { s as slot } from "./DX-MI-YE.js";
import { d as attribute_effect, S as STYLE } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { l as legacy_rest_props, p as prop } from "./DUftb7my.js";
var root = from_html(`<a><!></a>`);
function DownloadLink($$anchor, $$props) {
  const $$sanitized_props = legacy_rest_props($$props, ["children", "$$slots", "$$events", "$$legacy"]);
  const $$restProps = legacy_rest_props($$sanitized_props, ["href", "download"]);
  push($$props, false);
  let href = prop($$props, "href", 8, void 0);
  let download = prop($$props, "download", 8);
  const dispatch = createEventDispatcher();
  init();
  var a = root();
  var event_handler = user_derived(() => dispatch.bind(null, "click"));
  attribute_effect(
    a,
    () => ({
      class: "download-link",
      href: href(),
      target: untrack(() => typeof window !== "undefined" && window.__is_colab__ ? "_blank" : null),
      rel: "noopener noreferrer",
      download: download(),
      ...$$restProps,
      [STYLE]: { position: "relative" }
    }),
    void 0,
    void 0,
    void 0,
    "svelte-7nkusa"
  );
  var node = child(a);
  slot(node, $$props, "default", {}, null);
  reset(a);
  event("click", a, function(...$$args) {
    get(event_handler)?.apply(this, $$args);
  });
  append($$anchor, a);
  pop();
}
export {
  DownloadLink as D
};
//# sourceMappingURL=BFO3TfnI.js.map
