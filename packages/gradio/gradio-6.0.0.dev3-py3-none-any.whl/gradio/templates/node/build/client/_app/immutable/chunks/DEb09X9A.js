import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { c as from_html, d as child, r as reset, s as sibling, t as template_effect, b as append, g as set_text } from "./DEzry6cj.js";
import { s as set_attribute, a as set_class } from "./DXi4jxVF.js";
import { p as prop } from "./DUftb7my.js";
var root = from_html(`<label for="" data-testid="block-label"><span class="svelte-19djge9"><!></span> </label>`);
function BlockLabel($$anchor, $$props) {
  let label = prop($$props, "label", 8, null);
  let Icon = prop($$props, "Icon", 8);
  let show_label = prop($$props, "show_label", 8, true);
  let disable = prop($$props, "disable", 8, false);
  let float = prop($$props, "float", 8, true);
  let rtl = prop($$props, "rtl", 8, false);
  var label_1 = root();
  let classes;
  var span = child(label_1);
  var node = child(span);
  Icon()(node, {});
  reset(span);
  var text = sibling(span);
  reset(label_1);
  template_effect(() => {
    set_attribute(label_1, "dir", rtl() ? "rtl" : "ltr");
    classes = set_class(label_1, 1, "svelte-19djge9", null, classes, {
      hide: !show_label(),
      "sr-only": !show_label(),
      float: float(),
      "hide-label": disable()
    });
    set_text(text, ` ${label() ?? ""}`);
    label_1.dir = label_1.dir;
  });
  append($$anchor, label_1);
}
export {
  BlockLabel as B
};
//# sourceMappingURL=DEb09X9A.js.map
