import "./9B4_veAf.js";
import { p as push, M as user_effect, k as get, A as user_derived, z as event, c as from_html, v as first_child, s as sibling, d as child, E as next, F as text, t as template_effect, b as append, r as reset, o as pop, $ as $window, g as set_text } from "./DEzry6cj.js";
import { r as rest_props, s as spread_props, b as bind_this, i as if_block } from "./DUftb7my.js";
import { G as Gradio, B as Block, g as Static, z as BlockTitle, r as remove_input_defaults, q as bind_value, s as set_attribute } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
let _id = 0;
var root_3 = from_html(`<button class="reset-button svelte-8epfm4" aria-label="Reset to default value" data-testid="reset-button">↺</button>`);
var root_1 = from_html(`<!> <div class="wrap svelte-8epfm4"><div class="head svelte-8epfm4"><label class="svelte-8epfm4"><!></label> <div class="tab-like-container svelte-8epfm4"><input data-testid="number-input" type="number" class="svelte-8epfm4"/> <!></div></div> <div class="slider_input_container svelte-8epfm4"><span class="min_value svelte-8epfm4"> </span> <input type="range" name="cowbell" class="svelte-8epfm4"/> <span class="max_value svelte-8epfm4"> </span></div></div>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  let gradio = new Gradio(props);
  const INITIAL_VALUE = gradio.props.value;
  let range_input;
  let number_input;
  const id = `range_id_${_id++}`;
  let minimum_value = user_derived(() => gradio.props.minimum ?? 0);
  let percentage = user_derived(() => {
    const min = gradio.props.minimum;
    const max = gradio.props.maximum;
    const val = gradio.props.value;
    if (val > max) {
      return 100;
    } else if (val < min) {
      return 0;
    }
    return (val - min) / (max - min) * 100;
  });
  user_effect(() => {
    if (!gradio.props.value) return;
    range_input.style.setProperty("--range_progress", `${get(percentage)}%`);
    range_input.value = gradio.props.value.toString();
  });
  function handle_change() {
    gradio.dispatch("change");
    gradio.dispatch("input");
  }
  function handle_release(e) {
    gradio.dispatch("release", gradio.props.value);
  }
  function clamp() {
    gradio.dispatch("release", gradio.props.value);
    gradio.props.value = Math.min(Math.max(gradio.props.value, gradio.props.minimum), gradio.props.maximum);
  }
  let disabled = user_derived(() => !gradio.shared.interactive);
  user_effect(() => {
    gradio.props.value && handle_change();
  });
  function handle_resize() {
  }
  function reset_value() {
    gradio.props.value = INITIAL_VALUE;
    gradio.dispatch("change");
    gradio.dispatch("release", gradio.props.value);
  }
  event("resize", $window, handle_resize);
  Block($$anchor, {
    get visible() {
      return gradio.shared.visible;
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
      var div = sibling(node, 2);
      var div_1 = child(div);
      var label = child(div_1);
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
          var text$1 = text();
          template_effect(() => set_text(text$1, gradio.shared.label || "Slider"));
          append($$anchor3, text$1);
        },
        $$slots: { default: true }
      });
      reset(label);
      var div_2 = sibling(label, 2);
      var input = child(div_2);
      remove_input_defaults(input);
      bind_this(input, ($$value) => number_input = $$value, () => number_input);
      var node_2 = sibling(input, 2);
      {
        var consequent = ($$anchor3) => {
          var button = root_3();
          template_effect(() => button.disabled = get(disabled));
          event("click", button, reset_value);
          append($$anchor3, button);
        };
        if_block(node_2, ($$render) => {
          if (gradio.props.buttons?.includes("reset") ?? true) $$render(consequent);
        });
      }
      reset(div_2);
      reset(div_1);
      var div_3 = sibling(div_1, 2);
      var span = child(div_3);
      var text_1 = child(span, true);
      reset(span);
      var input_1 = sibling(span, 2);
      remove_input_defaults(input_1);
      bind_this(input_1, ($$value) => range_input = $$value, () => range_input);
      var span_1 = sibling(input_1, 2);
      var text_2 = child(span_1, true);
      reset(span_1);
      reset(div_3);
      reset(div);
      template_effect(() => {
        set_attribute(label, "for", id);
        set_attribute(input, "aria-label", `number input for ${gradio.shared.label}`);
        set_attribute(input, "min", gradio.props.minimum);
        set_attribute(input, "max", gradio.props.maximum);
        set_attribute(input, "step", gradio.props.step);
        input.disabled = get(disabled);
        set_text(text_1, get(minimum_value));
        set_attribute(input_1, "id", id);
        set_attribute(input_1, "min", gradio.props.minimum);
        set_attribute(input_1, "max", gradio.props.maximum);
        set_attribute(input_1, "step", gradio.props.step);
        input_1.disabled = get(disabled);
        set_attribute(input_1, "aria-label", `range slider for ${gradio.shared.label}`);
        set_text(text_2, gradio.props.maximum);
      });
      bind_value(input, () => gradio.props.value, ($$value) => gradio.props.value = $$value);
      event("blur", input, clamp);
      event("pointerup", input, handle_release);
      bind_value(input_1, () => gradio.props.value, ($$value) => gradio.props.value = $$value);
      event("pointerup", input_1, handle_release);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=B_JDwqJW.js.map
