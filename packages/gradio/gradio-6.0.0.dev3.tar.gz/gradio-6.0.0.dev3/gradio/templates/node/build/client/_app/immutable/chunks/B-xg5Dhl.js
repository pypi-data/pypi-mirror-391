import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, i as legacy_pre_effect, j as set, k as get, m as mutable_source, n as legacy_pre_effect_reset, c as from_html, d as child, r as reset, t as template_effect, b as append, o as pop } from "./DEzry6cj.js";
import { s as slot } from "./DX-MI-YE.js";
import { a as set_class } from "./DXi4jxVF.js";
import { p as prop, b as bind_this } from "./DUftb7my.js";
var root = from_html(`<div aria-label="Empty value"><div class="icon svelte-v95lt3"><!></div></div>`);
function Empty($$anchor, $$props) {
  push($$props, false);
  const parent_height = mutable_source();
  let size = prop($$props, "size", 8, "small");
  let unpadded_box = prop($$props, "unpadded_box", 8, false);
  let el = mutable_source();
  function compare_el_to_parent(el2) {
    if (!el2) return false;
    const { height: el_height } = el2.getBoundingClientRect();
    const { height: parent_height2 } = el2.parentElement?.getBoundingClientRect() || { height: el_height };
    return el_height > parent_height2 + 2;
  }
  legacy_pre_effect(() => get(el), () => {
    set(parent_height, compare_el_to_parent(get(el)));
  });
  legacy_pre_effect_reset();
  var div = root();
  let classes;
  var div_1 = child(div);
  var node = child(div_1);
  slot(node, $$props, "default", {}, null);
  reset(div_1);
  reset(div);
  bind_this(div, ($$value) => set(el, $$value), () => get(el));
  template_effect(() => classes = set_class(div, 1, "empty svelte-v95lt3", null, classes, {
    small: size() === "small",
    large: size() === "large",
    unpadded_box: unpadded_box(),
    small_parent: get(parent_height)
  }));
  append($$anchor, div);
  pop();
}
export {
  Empty as E
};
//# sourceMappingURL=B-xg5Dhl.js.map
