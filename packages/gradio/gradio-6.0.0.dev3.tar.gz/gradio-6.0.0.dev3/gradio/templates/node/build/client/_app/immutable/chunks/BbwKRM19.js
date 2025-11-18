import "./9B4_veAf.js";
import { p as push, J as state, L as proxy, M as user_effect, k as get, j as set, c as from_html, d as child, s as sibling, r as reset, t as template_effect, z as event, b as append, o as pop, g as set_text, A as user_derived } from "./DEzry6cj.js";
import { l as snapshot, r as remove_input_defaults, m as bind_checked } from "./DXi4jxVF.js";
import { i as if_block } from "./DUftb7my.js";
var root_1 = from_html(`<span class="label-text svelte-1q8xtp9"> </span>`);
var root = from_html(`<label class="checkbox-container svelte-1q8xtp9"><input type="checkbox" name="test" data-testid="checkbox" class="svelte-1q8xtp9"/> <!></label>`);
function Checkbox($$anchor, $$props) {
  push($$props, true);
  const gradio = $$props.gradio;
  let disabled = user_derived(() => !gradio.shared.interactive);
  let old_value = state(proxy(gradio.props.value));
  let label = user_derived(() => gradio.shared.label || gradio.i18n("checkbox.checkbox"));
  user_effect(() => {
    if (get(old_value) !== gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change", snapshot(gradio.props.value));
    }
  });
  async function handle_enter(event2) {
    if (event2.key === "Enter") {
      gradio.props.value = !gradio.props.value;
      gradio.dispatch("select", {
        index: 0,
        value: event2.currentTarget.checked,
        selected: event2.currentTarget.checked
      });
    }
  }
  async function handle_input(event2) {
    gradio.props.value = event2.currentTarget.checked;
    gradio.dispatch("select", {
      index: 0,
      value: event2.currentTarget.checked,
      selected: event2.currentTarget.checked
    });
    gradio.dispatch("input");
  }
  var label_1 = root();
  var input = child(label_1);
  remove_input_defaults(input);
  var node = sibling(input, 2);
  {
    var consequent = ($$anchor2) => {
      var span = root_1();
      var text = child(span, true);
      reset(span);
      template_effect(() => set_text(text, get(label)));
      append($$anchor2, span);
    };
    if_block(node, ($$render) => {
      if (gradio.shared.show_label) $$render(consequent);
    });
  }
  reset(label_1);
  template_effect(() => input.disabled = get(disabled));
  bind_checked(input, () => gradio.props.value, ($$value) => gradio.props.value = $$value);
  event("keydown", input, handle_enter);
  event("input", input, handle_input);
  append($$anchor, label_1);
  pop();
}
export {
  Checkbox as C
};
//# sourceMappingURL=BbwKRM19.js.map
