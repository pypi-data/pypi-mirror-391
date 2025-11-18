import "./9B4_veAf.js";
import { p as push, c as from_html, d as child, s as sibling, r as reset, t as template_effect, b as append, o as pop, k as get, A as user_derived } from "./DEzry6cj.js";
import { r as rest_props, i as if_block, s as spread_props } from "./DUftb7my.js";
import { s as slot } from "./DX-MI-YE.js";
import { G as Gradio, s as set_attribute, a as set_class, p as set_style, g as Static } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
var root = from_html(`<div><!> <!></div>`);
function Index($$anchor, $$props) {
  push($$props, true);
  const get_dimension = (dimension_value) => {
    if (dimension_value === void 0) {
      return void 0;
    }
    if (typeof dimension_value === "number") {
      return dimension_value + "px";
    } else if (typeof dimension_value === "string") {
      return dimension_value;
    }
  };
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  let gradio = new Gradio(props);
  var div = root();
  let classes;
  let styles;
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      {
        let $0 = user_derived(() => gradio.shared.loading_status ? gradio.shared.loading_status.status == "pending" ? "generating" : gradio.shared.loading_status.status : null);
        Static($$anchor2, spread_props(
          {
            get autoscroll() {
              return gradio.shared.autoscroll;
            },
            get i18n() {
              return gradio.i18n;
            }
          },
          () => gradio.shared.loading_status,
          {
            get status() {
              return get($0);
            }
          }
        ));
      }
    };
    if_block(node, ($$render) => {
      if (gradio.shared.loading_status && gradio.shared.loading_status.show_progress && gradio) $$render(consequent);
    });
  }
  var node_1 = sibling(node, 2);
  slot(node_1, $$props, "default", {}, null);
  reset(div);
  template_effect(
    ($0, $1) => {
      set_attribute(div, "id", gradio.shared.elem_id);
      classes = set_class(div, 1, `row ${$0 ?? ""}`, "svelte-7xavid", classes, {
        compact: gradio.props.variant === "compact",
        panel: gradio.props.variant === "panel",
        "unequal-height": gradio.props.equal_height === false,
        stretch: gradio.props.equal_height,
        hide: !gradio.shared.visible,
        "grow-children": gradio.shared.scale && gradio.shared.scale >= 1
      });
      styles = set_style(div, "", styles, $1);
    },
    [
      () => gradio.shared.elem_classes?.join(" "),
      () => ({
        height: get_dimension(gradio.props.height),
        "max-height": get_dimension(gradio.props.max_height),
        "min-height": get_dimension(gradio.props.min_height),
        "flex-grow": gradio.shared.scale
      })
    ]
  );
  append($$anchor, div);
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=DvPZAQsf.js.map
