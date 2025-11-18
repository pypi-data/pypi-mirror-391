import "./9B4_veAf.js";
import { p as push, J as state, L as proxy, M as user_effect, k as get, j as set, c as from_html, v as first_child, s as sibling, A as user_derived, b as append, o as pop } from "./DEzry6cj.js";
import { G as Gradio, l as snapshot, B as Block, T as Textbox, g as Static } from "./DXi4jxVF.js";
import { r as rest_props, i as if_block, s as spread_props } from "./DUftb7my.js";
import "./BAp-OWo-.js";
import { default as default2 } from "./Bf3It-3j.js";
var root_1 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let _props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(_props);
  let label = user_derived(() => gradio.shared.label || "Textbox");
  gradio.props.value = gradio.props.value ?? "";
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) !== gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change", snapshot(gradio.props.value));
    }
  });
  function handle_change(value) {
    if (!gradio.shared || !gradio.props) return;
    gradio.set_data({ validation_error: null });
    gradio.set_data({ value });
  }
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
    get scale() {
      return gradio.shared.scale;
    },
    get min_width() {
      return gradio.shared.min_width;
    },
    allow_overflow: false,
    get padding() {
      return gradio.shared.container;
    },
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          Static($$anchor3, spread_props(
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
              show_validation_error: false,
              $$events: {
                clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
              }
            }
          ));
        };
        if_block(node, ($$render) => {
          if (gradio.shared.loading_status) $$render(consequent);
        });
      }
      var node_1 = sibling(node, 2);
      {
        let $0 = user_derived(() => gradio.shared?.loading_status?.validation_error || gradio.shared?.validation_error);
        let $1 = user_derived(() => !gradio.shared.interactive);
        Textbox(node_1, {
          get value() {
            return gradio.props.value;
          },
          get label() {
            return get(label);
          },
          get info() {
            return gradio.props.info;
          },
          get show_label() {
            return gradio.shared.show_label;
          },
          get lines() {
            return gradio.props.lines;
          },
          get type() {
            return gradio.props.type;
          },
          get rtl() {
            return gradio.props.rtl;
          },
          get text_align() {
            return gradio.props.text_align;
          },
          get max_lines() {
            return gradio.props.max_lines;
          },
          get placeholder() {
            return gradio.props.placeholder;
          },
          get submit_btn() {
            return gradio.props.submit_btn;
          },
          get stop_btn() {
            return gradio.props.stop_btn;
          },
          get show_copy_button() {
            return gradio.props.show_copy_button;
          },
          get autofocus() {
            return gradio.props.autofocus;
          },
          get container() {
            return gradio.shared.container;
          },
          get autoscroll() {
            return gradio.shared.autoscroll;
          },
          get max_length() {
            return gradio.props.max_length;
          },
          get html_attributes() {
            return gradio.props.html_attributes;
          },
          get validation_error() {
            return get($0);
          },
          get disabled() {
            return get($1);
          },
          $$events: {
            change: (e) => handle_change(e.detail),
            input: () => gradio.dispatch("input"),
            submit: () => {
              gradio.shared.validation_error = null;
              gradio.dispatch("submit");
            },
            blur: () => gradio.dispatch("blur"),
            select: (e) => gradio.dispatch("select", e.detail),
            focus: () => gradio.dispatch("focus"),
            stop: () => gradio.dispatch("stop"),
            copy: (e) => gradio.dispatch("copy", e.detail)
          }
        });
      }
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  default2 as BaseExample,
  Textbox as BaseTextbox,
  Index as default
};
//# sourceMappingURL=MZsx2wGi.js.map
