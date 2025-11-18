import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, c as from_html, d as child, r as reset, t as template_effect, y as untrack, u as deep_read_state, g as set_text, b as append, o as pop } from "./DEzry6cj.js";
import { a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { p as prop } from "./DUftb7my.js";
var root = from_html(`<div> </div>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  init();
  var div = root();
  let classes;
  var text = child(div, true);
  reset(div);
  template_effect(
    ($0) => {
      classes = set_class(div, 1, "svelte-164n2qi", null, classes, {
        table: type() === "table",
        gallery: type() === "gallery",
        selected: selected()
      });
      set_text(text, $0);
    },
    [
      () => (deep_read_state(value()), untrack(() => value() !== null ? value().toLocaleString() : ""))
    ]
  );
  append($$anchor, div);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=DzRmuYTl.js.map
