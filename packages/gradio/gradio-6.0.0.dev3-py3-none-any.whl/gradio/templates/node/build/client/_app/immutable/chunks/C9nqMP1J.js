import "./9B4_veAf.js";
import { f as from_svg, b as append, p as push, J as state, L as proxy, M as user_effect, k as get, j as set, c as from_html, d as child, E as next, F as text, t as template_effect, s as sibling, A as user_derived, r as reset, z as event, o as pop, v as first_child, W as to_array, g as set_text } from "./DEzry6cj.js";
import { b as bind_this, i as if_block, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { z as BlockTitle, t as each, r as remove_input_defaults, a as set_class, q as bind_value, v as index, s as set_attribute, N as preventDefault, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { D as DropdownArrow } from "./wPgCyhEZ.js";
import { D as DropdownOptions, h as handle_filter, a as handle_shared_keys, b as Dropdown } from "./CxkJXoI9.js";
import { default as default2 } from "./BHSbRAhm.js";
var root$1 = from_svg(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="100%" height="100%"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"></path></svg>`);
function Remove($$anchor) {
  var svg = root$1();
  append($$anchor, svg);
}
var root_5 = from_html(`<div class="token-remove svelte-1dv2vbb" role="button" tabindex="0"><!></div>`);
var root_2 = from_html(`<div class="token svelte-1dv2vbb"><span class="svelte-1dv2vbb"><!></span> <!></div>`);
var root_7 = from_html(`<div role="button" tabindex="0" class="token-remove remove-all svelte-1dv2vbb"><!></div>`);
var root_6 = from_html(`<!> <span class="icon-wrap svelte-1dv2vbb"><!></span>`, 1);
var root = from_html(`<label><!> <div class="wrap svelte-1dv2vbb"><div><!> <div class="secondary-wrap svelte-1dv2vbb"><input autocomplete="off"/> <!></div></div> <!></div></label>`);
function Multiselect($$anchor, $$props) {
  push($$props, true);
  const gradio = $$props.gradio;
  let filter_input;
  let input_text = state("");
  let label = user_derived(() => gradio.shared.label || "Multiselect");
  let choices_names = user_derived(() => {
    return gradio.props.choices.map((c) => c[0]);
  });
  let choices_values = user_derived(() => {
    return gradio.props.choices.map((c) => c[1]);
  });
  let disabled = user_derived(() => !gradio.shared.interactive);
  let show_options = state(false);
  let $$d = user_derived(() => {
    const filtered = handle_filter(gradio.props.choices, get(input_text));
    return [
      filtered,
      filtered.length > 0 && !gradio.props.allow_custom_value ? filtered[0] : null
    ];
  }), $$array = user_derived(() => to_array(get($$d), 2)), filtered_indices = user_derived(() => get($$array)[0]), active_index = user_derived(() => get($$array)[1]);
  function set_selected_indices() {
    if (gradio.props.value === void 0) {
      return [];
    } else if (Array.isArray(gradio.props.value)) {
      return gradio.props.value.map((v) => {
        const index2 = get(choices_values).indexOf(v);
        if (index2 !== -1) {
          return index2;
        }
        if (gradio.props.allow_custom_value) {
          return v;
        }
        return void 0;
      }).filter((val) => val !== void 0);
    }
    return [];
  }
  let selected_indices = user_derived(set_selected_indices);
  function handle_blur() {
    if (!gradio.props.allow_custom_value) {
      set(input_text, "");
    }
    if (gradio.props.allow_custom_value && get(input_text) !== "") {
      add_selected_choice(get(input_text));
      set(input_text, "");
    }
    gradio.dispatch("blur");
    set(show_options, false);
    set(active_index, null);
  }
  function remove_selected_choice(option_index) {
    set(selected_indices, get(selected_indices).filter((v) => v !== option_index));
    gradio.props.value = get(selected_indices).map((index2) => typeof index2 === "number" ? get(choices_values)[index2] : index2);
    gradio.dispatch("input");
    gradio.dispatch("select", {
      index: typeof option_index === "number" ? option_index : -1,
      value: typeof option_index === "number" ? get(choices_values)[option_index] : option_index,
      selected: false
    });
  }
  function add_selected_choice(option_index) {
    if (gradio.props.max_choices == null || get(selected_indices).length < gradio.props.max_choices) {
      get(selected_indices).push(option_index);
      gradio.dispatch("select", {
        index: typeof option_index === "number" ? option_index : -1,
        value: typeof option_index === "number" ? get(choices_values)[option_index] : option_index,
        selected: true
      });
    }
    if (get(selected_indices).length === gradio.props.max_choices) {
      set(show_options, false);
      set(active_index, null);
      filter_input.blur();
    }
    gradio.props.value = get(selected_indices).map((index2) => typeof index2 === "number" ? get(choices_values)[index2] : index2);
  }
  function handle_option_selected(e) {
    const option_index = parseInt(e.detail.target.dataset.index);
    add_or_remove_index(option_index);
  }
  function add_or_remove_index(option_index) {
    if (get(selected_indices).includes(option_index)) {
      remove_selected_choice(option_index);
    } else {
      add_selected_choice(option_index);
    }
    set(input_text, "");
    set(active_index, null);
    gradio.dispatch("input");
  }
  function remove_all(e) {
    set(selected_indices, []);
    set(input_text, "");
    gradio.props.value = [];
    e.preventDefault();
  }
  function handle_focus(e) {
    set(filtered_indices, gradio.props.choices.map((_, i) => i));
    if (gradio.props.max_choices === null || get(selected_indices).length < gradio.props.max_choices) {
      set(show_options, true);
    }
    gradio.dispatch("focus");
    set(show_options, true);
  }
  function handle_key_down(e) {
    (($$value) => {
      var $$array_1 = to_array($$value, 2);
      set(show_options, $$array_1[0], true);
      set(active_index, $$array_1[1]);
    })(handle_shared_keys(e, get(active_index), get(filtered_indices)));
    if (e.key === "Enter") {
      if (get(active_index) !== null) {
        add_or_remove_index(get(active_index));
      } else {
        if (gradio.props.allow_custom_value) {
          add_selected_choice(get(input_text));
          set(input_text, "");
        }
      }
    }
    if (e.key === "Backspace" && get(input_text) === "") {
      set(selected_indices, [...get(selected_indices).slice(0, -1)]);
    }
    if (get(selected_indices).length === gradio.props.max_choices) {
      set(show_options, false);
      set(active_index, null);
    }
  }
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) !== gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  var label_1 = root();
  let classes;
  var node = child(label_1);
  BlockTitle(node, {
    get show_label() {
      return gradio.shared.show_label;
    },
    get info() {
      return gradio.props.info;
    },
    children: ($$anchor2, $$slotProps) => {
      next();
      var text$1 = text();
      template_effect(() => set_text(text$1, get(label)));
      append($$anchor2, text$1);
    },
    $$slots: { default: true }
  });
  var div = sibling(node, 2);
  var div_1 = child(div);
  let classes_1;
  var node_1 = child(div_1);
  each(node_1, 17, () => get(selected_indices), index, ($$anchor2, s) => {
    var div_2 = root_2();
    var span = child(div_2);
    var node_2 = child(span);
    {
      var consequent = ($$anchor3) => {
        var text_1 = text();
        template_effect(() => set_text(text_1, get(choices_names)[get(s)]));
        append($$anchor3, text_1);
      };
      var alternate = ($$anchor3) => {
        var text_2 = text();
        template_effect(() => set_text(text_2, get(s)));
        append($$anchor3, text_2);
      };
      if_block(node_2, ($$render) => {
        if (typeof get(s) === "number") $$render(consequent);
        else $$render(alternate, false);
      });
    }
    reset(span);
    var node_3 = sibling(span, 2);
    {
      var consequent_1 = ($$anchor3) => {
        var div_3 = root_5();
        var node_4 = child(div_3);
        Remove(node_4);
        reset(div_3);
        template_effect(($0) => set_attribute(div_3, "title", $0), [() => gradio.i18n("common.remove") + " " + get(s)]);
        event("click", div_3, preventDefault(() => remove_selected_choice(get(s))));
        event("keydown", div_3, (event2) => {
          if (event2.key === "Enter") {
            remove_selected_choice(get(s));
          }
        });
        append($$anchor3, div_3);
      };
      if_block(node_3, ($$render) => {
        if (!get(disabled)) $$render(consequent_1);
      });
    }
    reset(div_2);
    append($$anchor2, div_2);
  });
  var div_4 = sibling(node_1, 2);
  var input = child(div_4);
  remove_input_defaults(input);
  let classes_2;
  bind_this(input, ($$value) => filter_input = $$value, () => filter_input);
  var node_5 = sibling(input, 2);
  {
    var consequent_3 = ($$anchor2) => {
      var fragment_3 = root_6();
      var node_6 = first_child(fragment_3);
      {
        var consequent_2 = ($$anchor3) => {
          var div_5 = root_7();
          var node_7 = child(div_5);
          Remove(node_7);
          reset(div_5);
          template_effect(($0) => set_attribute(div_5, "title", $0), [() => gradio.i18n("common.clear")]);
          event("click", div_5, remove_all);
          event("keydown", div_5, (event2) => {
            if (event2.key === "Enter") {
              remove_all(event2);
            }
          });
          append($$anchor3, div_5);
        };
        if_block(node_6, ($$render) => {
          if (get(selected_indices).length > 0) $$render(consequent_2);
        });
      }
      var span_1 = sibling(node_6, 2);
      var node_8 = child(span_1);
      DropdownArrow(node_8);
      reset(span_1);
      append($$anchor2, fragment_3);
    };
    if_block(node_5, ($$render) => {
      if (!get(disabled)) $$render(consequent_3);
    });
  }
  reset(div_4);
  reset(div_1);
  var node_9 = sibling(div_1, 2);
  DropdownOptions(node_9, {
    get show_options() {
      return get(show_options);
    },
    get choices() {
      return gradio.props.choices;
    },
    get filtered_indices() {
      return get(filtered_indices);
    },
    get disabled() {
      return get(disabled);
    },
    get selected_indices() {
      return get(selected_indices);
    },
    get active_index() {
      return get(active_index);
    },
    remember_scroll: true,
    $$events: { change: handle_option_selected }
  });
  reset(div);
  reset(label_1);
  template_effect(
    ($0) => {
      classes = set_class(label_1, 1, "svelte-1dv2vbb", null, classes, { container: gradio.shared.container });
      classes_1 = set_class(div_1, 1, "wrap-inner svelte-1dv2vbb", null, classes_1, { show_options: get(show_options) });
      classes_2 = set_class(input, 1, "border-none svelte-1dv2vbb", null, classes_2, $0);
      input.disabled = get(disabled);
      input.readOnly = !gradio.props.filterable;
    },
    [
      () => ({
        subdued: !get(choices_names).includes(get(input_text)) && !gradio.props.allow_custom_value || get(selected_indices).length === gradio.props.max_choices
      })
    ]
  );
  bind_value(input, () => get(input_text), ($$value) => set(input_text, $$value));
  event("keydown", input, handle_key_down);
  event("keyup", input, (e) => {
    gradio.dispatch("key_up", { key: e.key, input_value: get(input_text) });
  });
  event("blur", input, handle_blur);
  event("focus", input, handle_focus);
  append($$anchor, label_1);
  pop();
}
var root_1 = from_html(`<!> <!>`, 1);
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
          $$events: {
            clear_status: () => gradio.dispatch("clear_status", loading_status)
          }
        }
      ));
      var node_1 = sibling(node, 2);
      {
        var consequent = ($$anchor3) => {
          Multiselect($$anchor3, {
            get gradio() {
              return gradio;
            }
          });
        };
        var alternate = ($$anchor3) => {
          Dropdown($$anchor3, {
            get gradio() {
              return gradio;
            }
          });
        };
        if_block(node_1, ($$render) => {
          if (gradio.props.multiselect) $$render(consequent);
          else $$render(alternate, false);
        });
      }
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Dropdown as BaseDropdown,
  DropdownOptions as BaseDropdownOptions,
  default2 as BaseExample,
  Multiselect as BaseMultiselect,
  Index as default
};
//# sourceMappingURL=C9nqMP1J.js.map
