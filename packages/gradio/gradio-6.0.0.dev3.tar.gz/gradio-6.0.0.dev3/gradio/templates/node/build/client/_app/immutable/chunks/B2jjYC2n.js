import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { c as from_html, d as child, r as reset, t as template_effect, b as append, g as set_text } from "./DEzry6cj.js";
import { a as set_class } from "./DXi4jxVF.js";
import { p as prop } from "./DUftb7my.js";
/* empty css         */
var root = from_html(`<div> </div>`);
function Example($$anchor, $$props) {
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  var div = root();
  let classes;
  var text = child(div, true);
  reset(div);
  template_effect(() => {
    classes = set_class(div, 1, "svelte-9pg6fh", null, classes, {
      table: type() === "table",
      gallery: type() === "gallery",
      selected: selected()
    });
    set_text(text, value() ? value() : "");
  });
  append($$anchor, div);
}
export {
  Example as default
};
//# sourceMappingURL=B2jjYC2n.js.map
