import "./9B4_veAf.js";
import { p as push, c as from_html, d as child, r as reset, t as template_effect, k as get, A as user_derived, b as append, o as pop } from "./DEzry6cj.js";
import { s as slot } from "./DX-MI-YE.js";
import { G as Gradio, p as set_style, s as set_attribute, a as set_class } from "./DXi4jxVF.js";
import { r as rest_props } from "./DUftb7my.js";
var root = from_html(`<div><div class="styler svelte-1p9262q"><!></div></div>`);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  new Gradio(props);
  const elem_id = user_derived(() => $$props.elem_id || "");
  const elem_classes = user_derived(() => $$props.elem_classes || []);
  const visible = user_derived(() => $$props.visible === void 0 ? true : $$props.visible);
  var div = root();
  let classes;
  var div_1 = child(div);
  set_style(div_1, "", {}, {
    "--block-radius": "0px",
    "--block-border-width": "0px",
    "--layout-gap": "1px",
    "--form-gap-width": "1px",
    "--button-border-width": "0px",
    "--button-large-radius": "0px",
    "--button-small-radius": "0px"
  });
  var node = child(div_1);
  slot(node, $$props, "default", {}, null);
  reset(div_1);
  reset(div);
  template_effect(
    ($0) => {
      set_attribute(div, "id", get(elem_id));
      classes = set_class(div, 1, `gr-group ${$0 ?? ""}`, "svelte-1p9262q", classes, { hide: !get(visible) });
    },
    [() => get(elem_classes).join(" ")]
  );
  append($$anchor, div);
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=B5dITtNQ.js.map
