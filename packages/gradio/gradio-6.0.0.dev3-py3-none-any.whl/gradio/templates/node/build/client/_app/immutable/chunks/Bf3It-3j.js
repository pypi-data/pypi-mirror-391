import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, I as onMount, c as from_html, d as child, r as reset, t as template_effect, y as untrack, u as deep_read_state, g as set_text, b as append, o as pop, k as get, m as mutable_source, j as set } from "./DEzry6cj.js";
import { a as set_class, i as bind_element_size } from "./DXi4jxVF.js";
import { p as prop, b as bind_this } from "./DUftb7my.js";
import { i as init } from "./DB0xzveP.js";
var root = from_html(`<div> </div>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  let size = mutable_source();
  let el = mutable_source();
  function set_styles(element, el_width) {
    element.style.setProperty("--local-text-width", `${el_width && el_width < 150 ? el_width : 200}px`);
    element.style.whiteSpace = "unset";
  }
  function truncate_text(text, max_length = 60) {
    if (!text) return "";
    const str = String(text);
    if (str.length <= max_length) return str;
    return str.slice(0, max_length) + "...";
  }
  onMount(() => {
    set_styles(get(el), get(size));
  });
  init();
  var div = root();
  let classes;
  var text_1 = child(div, true);
  reset(div);
  bind_this(div, ($$value) => set(el, $$value), () => get(el));
  template_effect(
    ($0) => {
      classes = set_class(div, 1, "svelte-xxobeb", null, classes, {
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
  bind_element_size(div, "clientWidth", ($$value) => set(size, $$value));
  append($$anchor, div);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=Bf3It-3j.js.map
