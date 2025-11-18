import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { c as from_html, d as child, r as reset, t as template_effect, y as untrack, u as deep_read_state, g as set_text, b as append } from "./DEzry6cj.js";
import { a as set_class } from "./DXi4jxVF.js";
import { p as prop } from "./DUftb7my.js";
var root = from_html(`<div><pre> </pre></div>`);
function Example($$anchor, $$props) {
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  var div = root();
  let classes;
  var pre = child(div);
  var text = child(pre, true);
  reset(pre);
  reset(div);
  template_effect(
    ($0) => {
      classes = set_class(div, 1, "svelte-pj4oi8", null, classes, {
        table: type() === "table",
        gallery: type() === "gallery",
        selected: selected()
      });
      set_text(text, $0);
    },
    [
      () => (deep_read_state(value()), untrack(() => JSON.stringify(value(), null, 2)))
    ]
  );
  append($$anchor, div);
}
export {
  Example as default
};
//# sourceMappingURL=BYwHcaCE.js.map
