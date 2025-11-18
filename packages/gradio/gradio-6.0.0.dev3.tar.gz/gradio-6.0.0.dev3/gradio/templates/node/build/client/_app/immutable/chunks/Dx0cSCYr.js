import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { c as from_html, t as template_effect, b as append } from "./DEzry6cj.js";
import { p as set_style, a as set_class } from "./DXi4jxVF.js";
import { p as prop } from "./DUftb7my.js";
var root = from_html(`<div></div>`);
function Example($$anchor, $$props) {
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  var div = root();
  let classes;
  template_effect(() => {
    set_style(div, `background-color: ${(value() ? value() : "black") ?? ""}`);
    classes = set_class(div, 1, "svelte-1k1s8qu", null, classes, {
      table: type() === "table",
      gallery: type() === "gallery",
      selected: selected()
    });
  });
  append($$anchor, div);
}
export {
  Example as default
};
//# sourceMappingURL=Dx0cSCYr.js.map
