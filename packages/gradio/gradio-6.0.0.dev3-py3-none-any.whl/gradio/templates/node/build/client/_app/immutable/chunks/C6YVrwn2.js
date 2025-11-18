import "./9B4_veAf.js";
import { p as push, J as state, L as proxy, M as user_effect, k as get, j as set, c as from_html, v as first_child, d as child, r as reset, s as sibling, A as user_derived, b as append, o as pop } from "./DEzry6cj.js";
import { r as rest_props, i as if_block, s as spread_props } from "./DUftb7my.js";
import { G as Gradio, B as Block, g as Static, i as bind_element_size } from "./DXi4jxVF.js";
import { J as JSON_1, a as JSON } from "./N0-8scS7.js";
import "./BAp-OWo-.js";
import { B as BlockLabel } from "./DEb09X9A.js";
var root_1 = from_html(`<div><!></div> <!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) !== gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  let label_height = state(0);
  Block($$anchor, {
    get visible() {
      return gradio.shared.visible;
    },
    test_id: "json",
    get elem_id() {
      return gradio.shared.elem_id;
    },
    get elem_classes() {
      return gradio.shared.elem_classes;
    },
    get container() {
      return gradio.shared.container;
    },
    get scale() {
      return gradio.shared.scale;
    },
    get min_width() {
      return gradio.shared.min_width;
    },
    padding: false,
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
      var div = first_child(fragment_1);
      var node = child(div);
      {
        var consequent = ($$anchor3) => {
          {
            let $0 = user_derived(() => gradio.shared.container === false);
            BlockLabel($$anchor3, {
              get Icon() {
                return JSON;
              },
              get show_label() {
                return gradio.shared.show_label;
              },
              get label() {
                return gradio.shared.label;
              },
              float: false,
              get disable() {
                return get($0);
              }
            });
          }
        };
        if_block(node, ($$render) => {
          if (gradio.shared.label) $$render(consequent);
        });
      }
      reset(div);
      var node_1 = sibling(div, 2);
      Static(node_1, spread_props(
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
          $$events: {
            clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
          }
        }
      ));
      var node_2 = sibling(node_1, 2);
      {
        let $0 = user_derived(() => gradio.props.buttons == null ? true : gradio.props.buttons.includes("copy"));
        JSON_1(node_2, {
          get value() {
            return gradio.props.value;
          },
          get open() {
            return gradio.props.open;
          },
          get theme_mode() {
            return gradio.props.theme_mode;
          },
          get show_indices() {
            return gradio.props.show_indices;
          },
          get show_copy_button() {
            return get($0);
          },
          get label_height() {
            return get(label_height);
          }
        });
      }
      bind_element_size(div, "clientHeight", ($$value) => set(label_height, $$value));
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  JSON_1 as BaseJSON,
  Index as default
};
//# sourceMappingURL=C6YVrwn2.js.map
