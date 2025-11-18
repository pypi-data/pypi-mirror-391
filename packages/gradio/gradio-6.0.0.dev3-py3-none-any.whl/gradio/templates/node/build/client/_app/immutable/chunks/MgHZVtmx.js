import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { c as from_html, d as child, r as reset, t as template_effect, y as untrack, u as deep_read_state, g as set_text, b as append } from "./DEzry6cj.js";
import { a as set_class } from "./DXi4jxVF.js";
import { p as prop } from "./DUftb7my.js";
/* empty css         */
var root = from_html(`<pre> </pre>`);
function Example($$anchor, $$props) {
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  function truncate_text(text, max_length = 60) {
    if (!text) return "";
    const str = String(text);
    if (str.length <= max_length) return str;
    return str.slice(0, max_length) + "...";
  }
  var pre = root();
  let classes;
  var text_1 = child(pre, true);
  reset(pre);
  template_effect(
    ($0) => {
      classes = set_class(pre, 1, "svelte-1bbj91m", null, classes, {
        table: type() === "table",
        gallery: type() === "gallery",
        selected: selected()
      });
      set_text(text_1, $0);
    },
    [
      () => (deep_read_state(value()), untrack(() => truncate_text(value())))
    ]
  );
  append($$anchor, pre);
}
export {
  Example as default
};
//# sourceMappingURL=MgHZVtmx.js.map
