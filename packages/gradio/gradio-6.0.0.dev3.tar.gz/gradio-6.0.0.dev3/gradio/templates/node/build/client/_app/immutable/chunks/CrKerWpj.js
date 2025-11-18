import "./9B4_veAf.js";
import { p as push, M as user_effect, c as from_html, v as first_child, s as sibling, D as comment, b as append, k as get, A as user_derived, d as child, r as reset, t as template_effect, z as event, F as text, g as set_text, o as pop, W as to_array } from "./DEzry6cj.js";
import { G as Gradio, l as snapshot, B as Block, g as Static, z as BlockTitle, r as remove_input_defaults, t as each, v as index, A as set_checked, a as set_class, s as set_attribute } from "./DXi4jxVF.js";
import { r as rest_props, s as spread_props, i as if_block } from "./DUftb7my.js";
import "./BAp-OWo-.js";
var root_3 = from_html(`<div class="select-all-container svelte-yb2gcx"><label class="select-all-label svelte-yb2gcx"><input class="select-all-checkbox svelte-yb2gcx" type="checkbox" title="Select/Deselect All"/></label> <button type="button" class="label-text svelte-yb2gcx"> </button></div>`);
var root_6 = from_html(`<label><input type="checkbox" class="svelte-yb2gcx"/> <span class="ml-2 svelte-yb2gcx"> </span></label>`);
var root_1 = from_html(`<!> <!> <div class="wrap svelte-yb2gcx" data-testid="checkbox-group"></div>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  let gradio = new Gradio(props);
  function toggle_choice(choice) {
    if (gradio.props.value.includes(choice)) {
      gradio.props.value = gradio.props.value.filter((v) => v !== choice);
    } else {
      gradio.props.value = [...gradio.props.value, choice];
    }
    gradio.dispatch("input");
  }
  function toggle_select_all() {
    const all_values = gradio.props.choices.map(([, internal_value]) => internal_value);
    if (gradio.props.value.length === all_values.length) {
      gradio.props.value = [];
    } else {
      gradio.props.value = all_values.slice();
    }
    gradio.dispatch("input");
  }
  let select_all_state = user_derived(() => {
    const all_values = gradio.props.choices.map(([, internal_value]) => internal_value);
    if (gradio.props.value.length === 0) return "unchecked";
    if (gradio.props.value.length === all_values.length) return "checked";
    return "indeterminate";
  });
  let disabled = user_derived(() => !gradio.shared.interactive);
  user_effect(() => {
    gradio.dispatch("change", snapshot(gradio.props.value));
  });
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
    type: "fieldset",
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
      var node_1 = sibling(node, 2);
      {
        let $0 = user_derived(() => gradio.shared.show_label || gradio.props.show_select_all && gradio.shared.interactive);
        BlockTitle(node_1, {
          get show_label() {
            return get($0);
          },
          get info() {
            return gradio.props.info;
          },
          children: ($$anchor3, $$slotProps2) => {
            var fragment_2 = comment();
            var node_2 = first_child(fragment_2);
            {
              var consequent = ($$anchor4) => {
                var div = root_3();
                var label = child(div);
                var input = child(label);
                remove_input_defaults(input);
                reset(label);
                var button = sibling(label, 2);
                var text2 = child(button, true);
                reset(button);
                reset(div);
                template_effect(() => {
                  set_checked(input, get(select_all_state) === "checked");
                  input.indeterminate = get(select_all_state) === "indeterminate";
                  set_text(text2, gradio.shared.show_label ? gradio.shared.label : "Select All");
                });
                event("change", input, toggle_select_all);
                event("click", button, toggle_select_all);
                append($$anchor4, div);
              };
              var alternate = ($$anchor4) => {
                var fragment_3 = comment();
                var node_3 = first_child(fragment_3);
                {
                  var consequent_1 = ($$anchor5) => {
                    var text_1 = text();
                    template_effect(($02) => set_text(text_1, $02), [
                      () => gradio.shared.label || gradio.i18n("checkbox.checkbox_group")
                    ]);
                    append($$anchor5, text_1);
                  };
                  if_block(
                    node_3,
                    ($$render) => {
                      if (gradio.shared.show_label) $$render(consequent_1);
                    },
                    true
                  );
                }
                append($$anchor4, fragment_3);
              };
              if_block(node_2, ($$render) => {
                if (gradio.props.show_select_all && gradio.shared.interactive) $$render(consequent);
                else $$render(alternate, false);
              });
            }
            append($$anchor3, fragment_2);
          },
          $$slots: { default: true }
        });
      }
      var div_1 = sibling(node_1, 2);
      each(div_1, 21, () => gradio.props.choices, index, ($$anchor3, $$item, i) => {
        var $$array = user_derived(() => to_array(get($$item), 2));
        let display_value = () => get($$array)[0];
        let internal_value = () => get($$array)[1];
        var label_1 = root_6();
        let classes;
        var input_1 = child(label_1);
        remove_input_defaults(input_1);
        var span = sibling(input_1, 2);
        var text_2 = child(span, true);
        reset(span);
        reset(label_1);
        template_effect(
          ($0, $1, $2, $3) => {
            classes = set_class(label_1, 1, "svelte-yb2gcx", null, classes, $0);
            input_1.disabled = get(disabled);
            set_checked(input_1, $1);
            set_attribute(input_1, "name", $2);
            set_attribute(input_1, "title", $3);
            set_text(text_2, display_value());
          },
          [
            () => ({
              disabled: get(disabled),
              selected: gradio.props.value.includes(internal_value())
            }),
            () => gradio.props.value.includes(internal_value()),
            () => internal_value()?.toString(),
            () => internal_value()?.toString()
          ]
        );
        event("change", input_1, () => toggle_choice(internal_value()));
        event("input", input_1, (evt) => gradio.dispatch("select", {
          index: i,
          value: internal_value(),
          selected: evt.currentTarget.checked
        }));
        event("keydown", input_1, (event2) => {
          if (event2.key === "Enter") {
            toggle_choice(internal_value());
            gradio.dispatch("select", {
              index: i,
              value: internal_value(),
              selected: !gradio.props.value.includes(internal_value())
            });
          }
        });
        append($$anchor3, label_1);
      });
      reset(div_1);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=CrKerWpj.js.map
