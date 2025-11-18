import "./9B4_veAf.js";
import { p as push, J as state, L as proxy, M as user_effect, k as get, j as set, c as from_html, v as first_child, s as sibling, d as child, E as next, t as template_effect, b as append, r as reset, z as event, o as pop, g as set_text, A as user_derived, K as tick } from "./DEzry6cj.js";
import { r as rest_props, s as spread_props, i as if_block } from "./DUftb7my.js";
import { G as Gradio, B as Block, g as Static, z as BlockTitle, r as remove_input_defaults, q as bind_value, a as set_class, s as set_attribute } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
var root_3 = from_html(`<div class="validation-error svelte-16ty2ow"> </div>`);
var root_2 = from_html(` <!>`, 1);
var root_1 = from_html(`<!> <label><!> <input type="number"/></label>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  gradio.props.value ??= 0;
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  async function handle_keypress(e) {
    await tick();
    if (e.key === "Enter") {
      e.preventDefault();
      gradio.dispatch("submit");
    }
  }
  const disabled = user_derived(() => !gradio.shared.interactive);
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
    get padding() {
      return gradio.shared.container;
    },
    allow_overflow: false,
    get scale() {
      return gradio.shared.scale;
    },
    get min_width() {
      return gradio.shared.min_width;
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
          show_validation_error: false,
          $$events: {
            clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
          }
        }
      ));
      var label = sibling(node, 2);
      let classes;
      var node_1 = child(label);
      BlockTitle(node_1, {
        get show_label() {
          return gradio.shared.show_label;
        },
        get info() {
          return gradio.props.info;
        },
        children: ($$anchor3, $$slotProps2) => {
          next();
          var fragment_2 = root_2();
          var text = first_child(fragment_2);
          var node_2 = sibling(text);
          {
            var consequent = ($$anchor4) => {
              var div = root_3();
              var text_1 = child(div, true);
              reset(div);
              template_effect(() => set_text(text_1, gradio.shared.loading_status?.validation_error));
              append($$anchor4, div);
            };
            if_block(node_2, ($$render) => {
              if (gradio.shared.loading_status?.validation_error) $$render(consequent);
            });
          }
          template_effect(() => set_text(text, `${(gradio.shared.label || "Number") ?? ""} `));
          append($$anchor3, fragment_2);
        },
        $$slots: { default: true }
      });
      var input = sibling(node_1, 2);
      remove_input_defaults(input);
      let classes_1;
      reset(label);
      template_effect(() => {
        classes = set_class(label, 1, "block svelte-16ty2ow", null, classes, { container: gradio.shared.container });
        set_attribute(input, "aria-label", gradio.shared.label || "Number");
        set_attribute(input, "min", gradio.props.minimum);
        set_attribute(input, "max", gradio.props.maximum);
        set_attribute(input, "step", gradio.props.step);
        set_attribute(input, "placeholder", gradio.props.placeholder);
        input.disabled = get(disabled);
        classes_1 = set_class(input, 1, "svelte-16ty2ow", null, classes_1, {
          "validation-error": gradio.shared.loading_status?.validation_error
        });
      });
      bind_value(input, () => gradio.props.value, ($$value) => gradio.props.value = $$value);
      event("keypress", input, handle_keypress);
      event("input", input, () => gradio.dispatch("input"));
      event("blur", input, () => gradio.dispatch("blur"));
      event("focus", input, () => gradio.dispatch("focus"));
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=CnweJyx-.js.map
