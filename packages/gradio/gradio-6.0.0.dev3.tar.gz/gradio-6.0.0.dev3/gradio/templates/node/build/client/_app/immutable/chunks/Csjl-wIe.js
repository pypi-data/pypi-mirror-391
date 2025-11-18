import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, c as from_html, d as child, k as get, x as derived_safe_equal, r as reset, t as template_effect, b as append, o as pop, y as untrack, u as deep_read_state } from "./DEzry6cj.js";
import { j as Image, a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { p as prop } from "./DUftb7my.js";
/* empty css         */
/* empty css         */
/* empty css         */
var root = from_html(`<div><!></div>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  init();
  var div = root();
  let classes;
  var node = child(div);
  {
    let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value().composite?.url || value().background?.url)));
    Image(node, {
      get src() {
        return get($0);
      },
      alt: ""
    });
  }
  reset(div);
  template_effect(() => classes = set_class(div, 1, "container svelte-ous74z", null, classes, {
    table: type() === "table",
    gallery: type() === "gallery",
    selected: selected()
  }));
  append($$anchor, div);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=Csjl-wIe.js.map
