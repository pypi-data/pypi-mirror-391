import "./9B4_veAf.js";
import { p as push, c as from_html, v as first_child, s as sibling, d as child, k as get, A as user_derived, r as reset, t as template_effect, b as append, o as pop } from "./DEzry6cj.js";
import { G as Gradio, B as Block, g as Static, a as set_class } from "./DXi4jxVF.js";
import { r as rest_props, s as spread_props } from "./DUftb7my.js";
import { M as Markdown } from "./BIgjM4qn.js";
import "./BAp-OWo-.js";
import { default as default2 } from "./JuE3hNoR.js";
var root_1 = from_html(`<!> <div><!></div>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  Block($$anchor, {
    get visible() {
      return gradio.shared.visible;
    },
    get elem_id() {
      return gradio.shared.elem_id;
    },
    get elem_classes() {
      return gradio.shared.elem_classes;
    },
    get container() {
      return gradio.shared.container;
    },
    allow_overflow: true,
    overflow_behavior: "auto",
    get height() {
      return gradio.props.height;
    },
    get min_height() {
      return gradio.props.min_height;
    },
    get max_height() {
      return gradio.props.max_height;
    },
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      Static(node, spread_props(
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
          variant: "center",
          $$events: {
            clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
          }
        }
      ));
      var div = sibling(node, 2);
      let classes;
      var node_1 = child(div);
      {
        let $0 = user_derived(() => gradio.props.buttons?.includes("copy"));
        Markdown(node_1, {
          get value() {
            return gradio.props.value;
          },
          get elem_classes() {
            return gradio.shared.elem_classes;
          },
          get visible() {
            return gradio.shared.visible;
          },
          get rtl() {
            return gradio.props.rtl;
          },
          get latex_delimiters() {
            return gradio.props.latex_delimiters;
          },
          get sanitize_html() {
            return gradio.props.sanitize_html;
          },
          get line_breaks() {
            return gradio.props.line_breaks;
          },
          get header_links() {
            return gradio.props.header_links;
          },
          get show_copy_button() {
            return get($0);
          },
          get loading_status() {
            return gradio.shared.loading_status;
          },
          get theme_mode() {
            return gradio.shared.theme_mode;
          },
          $$events: {
            change: () => gradio.dispatch("change"),
            copy: (e) => gradio.dispatch("copy", e.detail)
          }
        });
      }
      reset(div);
      template_effect(() => classes = set_class(div, 1, "svelte-16ln60g", null, classes, {
        padding: gradio.props.padding,
        pending: gradio.shared.loading_status?.status === "pending"
      }));
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  default2 as BaseExample,
  Markdown as BaseMarkdown,
  Index as default
};
//# sourceMappingURL=CtS5Zm7a.js.map
