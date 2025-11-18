import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, c as from_html, d as child, r as reset, t as template_effect, b as append, o as pop, g as set_text } from "./DEzry6cj.js";
import { a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { p as prop } from "./DUftb7my.js";
var root = from_html(`<div> </div>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  let choices = prop($$props, "choices", 8);
  let names = value().map((val) => choices().find((pair) => pair[1] === val)?.[0]).filter((name) => name !== void 0);
  let names_string = names.join(", ");
  init();
  var div = root();
  let classes;
  var text = child(div, true);
  reset(div);
  template_effect(() => {
    classes = set_class(div, 1, "svelte-25nhtv", null, classes, {
      table: type() === "table",
      gallery: type() === "gallery",
      selected: selected()
    });
    set_text(text, names_string);
  });
  append($$anchor, div);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=BU4G92CT.js.map
