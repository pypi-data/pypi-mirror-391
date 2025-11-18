import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, c as from_html, d as child, r as reset, t as template_effect, b as append, o as pop, y as untrack, u as deep_read_state } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { j as Image, a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
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
    var consequent = ($$anchor2) => {
      Image($$anchor2, {
        get src() {
          return deep_read_state(value()), untrack(() => value().url);
        },
        alt: ""
      });
    };
    if_block(node, ($$render) => {
      if (value()) $$render(consequent);
    });
  }
  reset(div);
  template_effect(() => classes = set_class(div, 1, "container svelte-bs74gu", null, classes, {
    table: type() === "table",
    gallery: type() === "gallery",
    selected: selected(),
    border: value()
  }));
  append($$anchor, div);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=MZSzuq-N.js.map
