import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { c as from_html, d as child, r as reset, t as template_effect, b as append } from "./DEzry6cj.js";
import { D as html, a as set_class } from "./DXi4jxVF.js";
import { p as prop } from "./DUftb7my.js";
var root = from_html(`<div><!></div>`);
function Example($$anchor, $$props) {
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  var div = root();
  let classes;
  var node = child(div);
  html(node, value);
  reset(div);
  template_effect(() => classes = set_class(div, 1, "prose svelte-s7j0w2", null, classes, {
    table: type() === "table",
    gallery: type() === "gallery",
    selected: selected()
  }));
  append($$anchor, div);
}
export {
  Example as default
};
//# sourceMappingURL=398Qv58B.js.map
