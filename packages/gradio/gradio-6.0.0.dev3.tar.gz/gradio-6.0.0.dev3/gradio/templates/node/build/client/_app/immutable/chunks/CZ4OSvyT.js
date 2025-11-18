import "./9B4_veAf.js";
import { p as push, c as from_html, d as child, s as sibling, r as reset, t as template_effect, z as event, b as append, o as pop, k as get, A as user_derived, g as set_text, j as set, J as state, L as proxy, M as user_effect, v as first_child, E as next, F as text, W as to_array } from "./DEzry6cj.js";
import { r as remove_input_defaults, P as bind_group, s as set_attribute, a as set_class, G as Gradio, B as Block, g as Static, z as BlockTitle, t as each, v as index } from "./DXi4jxVF.js";
import { p as prop, r as rest_props, s as spread_props } from "./DUftb7my.js";
import "./BAp-OWo-.js";
import { default as default2 } from "./CsROyocN.js";
let id = 0;
var root = from_html(`<label><input type="radio" class="svelte-19qdtil"/> <span class="svelte-19qdtil"> </span></label>`);
function Radio($$anchor, $$props) {
  push($$props, true);
  const binding_group = [];
  let selected = prop($$props, "selected", 15);
  let is_selected = user_derived(() => selected() === $$props.internal_value);
  function handle_input(e) {
    set(is_selected, e.currentTarget.checked);
    if (e.currentTarget.checked) {
      $$props.on_input();
    }
  }
  var label = root();
  let classes;
  var input = child(label);
  remove_input_defaults(input);
  var input_value;
  var span = sibling(input, 2);
  var text2 = child(span, true);
  reset(span);
  reset(label);
  template_effect(() => {
    set_attribute(label, "data-testid", `${$$props.display_value ?? ""}-radio-label`);
    classes = set_class(label, 1, "svelte-19qdtil", null, classes, {
      disabled: $$props.disabled,
      selected: get(is_selected),
      rtl: $$props.rtl
    });
    input.disabled = $$props.disabled;
    set_attribute(input, "name", `radio-${++id}`);
    set_attribute(input, "aria-checked", get(is_selected));
    if (input_value !== (input_value = $$props.internal_value)) {
      input.value = (input.__value = $$props.internal_value) ?? "";
    }
    set_text(text2, $$props.display_value);
  });
  bind_group(
    binding_group,
    [],
    input,
    () => {
      $$props.internal_value;
      return selected();
    },
    selected
  );
  event("input", input, handle_input);
  append($$anchor, label);
  pop();
}
var root_1 = from_html(`<!> <!> <div class="wrap svelte-e4x47i"></div>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let disabled = user_derived(() => !gradio.shared.interactive);
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  Block($$anchor, {
    get visible() {
      return gradio.shared.visible;
    },
    type: "fieldset",
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
    get rtl() {
      return gradio.props.rtl;
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
          $$events: {
            clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
          }
        }
      ));
      var node_1 = sibling(node, 2);
      BlockTitle(node_1, {
        get show_label() {
          return gradio.shared.show_label;
        },
        get info() {
          return gradio.props.info;
        },
        children: ($$anchor3, $$slotProps2) => {
          next();
          var text$1 = text();
          template_effect(($0) => set_text(text$1, $0), [() => gradio.shared.label || gradio.i18n("radio.radio")]);
          append($$anchor3, text$1);
        },
        $$slots: { default: true }
      });
      var div = sibling(node_1, 2);
      each(div, 21, () => gradio.props.choices, index, ($$anchor3, $$item, i) => {
        var $$array = user_derived(() => to_array(get($$item), 2));
        let display_value = () => get($$array)[0];
        let internal_value = () => get($$array)[1];
        Radio($$anchor3, {
          get display_value() {
            return display_value();
          },
          get internal_value() {
            return internal_value();
          },
          get disabled() {
            return get(disabled);
          },
          get rtl() {
            return gradio.props.rtl;
          },
          on_input: () => {
            gradio.dispatch("select", { value: internal_value(), index: i });
            gradio.dispatch("input");
          },
          get selected() {
            return gradio.props.value;
          },
          set selected($$value) {
            gradio.props.value = $$value;
          }
        });
      });
      reset(div);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  default2 as BaseExample,
  Radio as BaseRadio,
  Index as default
};
//# sourceMappingURL=CZ4OSvyT.js.map
