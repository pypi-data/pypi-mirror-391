import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { c as from_html, d as child, r as reset, t as template_effect, b as append } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { a as set_class } from "./DXi4jxVF.js";
import { J as JSON_1 } from "./N0-8scS7.js";
var root = from_html(`<div><!></div>`);
function Example($$anchor, $$props) {
  let value = prop($$props, "value", 8);
  let theme_mode = prop($$props, "theme_mode", 8, "system");
  let show_indices = false;
  let label_height = 0;
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  var div = root();
  let classes;
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      JSON_1($$anchor2, {
        get value() {
          return value();
        },
        open: true,
        get theme_mode() {
          return theme_mode();
        },
        show_indices,
        label_height,
        interactive: false,
        show_copy_button: false
      });
    };
    if_block(node, ($$render) => {
      if (value()) $$render(consequent);
    });
  }
  reset(div);
  template_effect(() => classes = set_class(div, 1, "container svelte-19cq9h3", null, classes, {
    table: type() === "table",
    gallery: type() === "gallery",
    selected: selected(),
    border: value()
  }));
  append($$anchor, div);
}
export {
  Example as default
};
//# sourceMappingURL=6FIc1HU1.js.map
