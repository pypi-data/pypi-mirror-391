import "./9B4_veAf.js";
import { p as push, I as onMount, M as user_effect, k as get, A as user_derived, c as from_html, t as template_effect, b as append, o as pop } from "./DEzry6cj.js";
import { G as Gradio, n as navbar_config, k as clsx, s as set_attribute, a as set_class } from "./DXi4jxVF.js";
import { r as rest_props } from "./DUftb7my.js";
import { g as get$1 } from "./DdkXqxbl.js";
var root = from_html(`<div style="display: none;"></div>`);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let navbar_props = user_derived(() => {
    return {
      visible: gradio.shared.visible,
      main_page_name: gradio.props.main_page_name || "Home",
      value: gradio.props.value
    };
  });
  onMount(() => {
    const current_store = get$1(navbar_config);
    if (!current_store) {
      navbar_config.set(get(navbar_props));
    }
  });
  user_effect(() => {
    navbar_config.set(get(navbar_props));
  });
  var div = root();
  template_effect(
    ($0) => {
      set_attribute(div, "id", gradio.shared.elem_id);
      set_class(div, 1, $0);
    },
    [() => clsx(gradio.shared.elem_classes.join(" "))]
  );
  append($$anchor, div);
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=C9OBTJCa.js.map
