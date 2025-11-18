import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, c as from_html, d as child, r as reset, t as template_effect, b as append, o as pop, g as set_text, y as untrack, u as deep_read_state } from "./DEzry6cj.js";
import { i as init } from "./DB0xzveP.js";
import { p as prop } from "./DUftb7my.js";
var root = from_html(`<div style="display: none;"> </div>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 24, () => ({ visible: true, home_page_title: "Home" }));
  init();
  var div = root();
  var text = child(div);
  reset(div);
  template_effect(() => set_text(text, `Navbar config: visible=${(deep_read_state(value()), untrack(() => value().visible)) ?? ""}, home_page_title="${(deep_read_state(value()), untrack(() => value().home_page_title)) ?? ""}"`));
  append($$anchor, div);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=DxrbhsWV.js.map
