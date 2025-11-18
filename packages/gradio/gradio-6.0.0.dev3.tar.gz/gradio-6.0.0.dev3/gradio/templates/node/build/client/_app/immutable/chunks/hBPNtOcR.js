import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, c as from_html, d as child, r as reset, t as template_effect, b as append, o as pop, v as first_child, y as untrack, u as deep_read_state, s as sibling, g as set_text, k as get } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { t as each, v as index, a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
var root_2 = from_html(`<li><code> </code></li>`);
var root_3 = from_html(`<li class="extra svelte-14aa7hi">...</li>`);
var root_1 = from_html(`<!> <!>`, 1);
var root = from_html(`<ul><!></ul>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  init();
  var ul = root();
  let classes;
  var node = child(ul);
  {
    var consequent_1 = ($$anchor2) => {
      var fragment = root_1();
      var node_1 = first_child(fragment);
      each(
        node_1,
        1,
        () => (deep_read_state(value()), untrack(() => Array.isArray(value()) ? value().slice(0, 3) : [value()])),
        index,
        ($$anchor3, path) => {
          var li = root_2();
          var code = child(li);
          var text = child(code);
          reset(code);
          reset(li);
          template_effect(() => set_text(text, `./${get(path) ?? ""}`));
          append($$anchor3, li);
        }
      );
      var node_2 = sibling(node_1, 2);
      {
        var consequent = ($$anchor3) => {
          var li_1 = root_3();
          append($$anchor3, li_1);
        };
        if_block(node_2, ($$render) => {
          if (deep_read_state(value()), untrack(() => Array.isArray(value()) && value().length > 3)) $$render(consequent);
        });
      }
      append($$anchor2, fragment);
    };
    if_block(node, ($$render) => {
      if (value()) $$render(consequent_1);
    });
  }
  reset(ul);
  template_effect(() => classes = set_class(ul, 1, "svelte-14aa7hi", null, classes, {
    table: type() === "table",
    gallery: type() === "gallery",
    selected: selected()
  }));
  append($$anchor, ul);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=hBPNtOcR.js.map
