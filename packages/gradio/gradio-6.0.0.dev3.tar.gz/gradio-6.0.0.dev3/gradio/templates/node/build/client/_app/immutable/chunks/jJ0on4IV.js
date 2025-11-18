import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, c as from_html, d as child, s as sibling, E as next, r as reset, t as template_effect, b as append, o as pop, y as untrack, u as deep_read_state } from "./DEzry6cj.js";
import { a as set_class, s as set_attribute } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { p as prop } from "./DUftb7my.js";
var root = from_html(`<div><img class="svelte-ulqlw7"/> <img class="svelte-ulqlw7"/> <span class="svelte-ulqlw7"></span></div>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let samples_dir = prop($$props, "samples_dir", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  init();
  var div = root();
  let classes;
  var img = child(div);
  var img_1 = sibling(img, 2);
  next(2);
  reset(div);
  template_effect(() => {
    classes = set_class(div, 1, "wrap svelte-ulqlw7", null, classes, {
      table: type() === "table",
      gallery: type() === "gallery",
      selected: selected()
    });
    set_attribute(img, "src", (deep_read_state(samples_dir()), deep_read_state(value()), untrack(() => samples_dir() + value()[0])));
    set_attribute(img_1, "src", (deep_read_state(samples_dir()), deep_read_state(value()), untrack(() => samples_dir() + value()[1])));
  });
  append($$anchor, div);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=jJ0on4IV.js.map
