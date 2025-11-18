import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, i as legacy_pre_effect, k as get, m as mutable_source, j as set, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, z as event, v as first_child, s as sibling, b as append, o as pop, $ as $window, r as reset, t as template_effect, d as child, y as untrack, g as set_text, J as state, L as proxy, A as user_derived, M as user_effect, E as next, F as text, W as to_array } from "./DEzry6cj.js";
import { p as prop, b as bind_this, i as if_block } from "./DUftb7my.js";
import { t as each, v as index, Y as transition, a as set_class, s as set_attribute, p as set_style, a2 as fly, N as preventDefault, z as BlockTitle, r as remove_input_defaults, q as bind_value } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { b as bind_window_size } from "./Braj6aVO.js";
import { i as init } from "./DB0xzveP.js";
import { D as DropdownArrow } from "./wPgCyhEZ.js";
var root_2$1 = from_html(`<li data-testid="dropdown-option" role="option"><span>✓</span> </li>`);
var root_1 = from_html(`<ul class="options svelte-1ou0lab" role="listbox"></ul>`);
var root$1 = from_html(`<div class="reference"></div> <!>`, 1);
function DropdownOptions($$anchor, $$props) {
  push($$props, false);
  let choices = prop($$props, "choices", 8);
  let filtered_indices = prop($$props, "filtered_indices", 8);
  let show_options = prop($$props, "show_options", 8, false);
  let disabled = prop($$props, "disabled", 8, false);
  let selected_indices = prop($$props, "selected_indices", 24, () => []);
  let active_index = prop($$props, "active_index", 8, null);
  let remember_scroll = prop($$props, "remember_scroll", 8, false);
  let offset_from_top = prop($$props, "offset_from_top", 8, 0);
  let from_top = prop($$props, "from_top", 8, false);
  let distance_from_top = mutable_source();
  let distance_from_bottom = mutable_source();
  let input_height = mutable_source();
  let input_width = mutable_source();
  let refElement = mutable_source();
  let listElement = mutable_source();
  let top = mutable_source(), bottom = mutable_source(), max_height = mutable_source();
  let innerHeight = mutable_source();
  let list_scroll_y = mutable_source(0);
  function calculate_window_distance() {
    const { top: ref_top, bottom: ref_bottom } = get(refElement).getBoundingClientRect();
    if (from_top()) {
      set(distance_from_top, offset_from_top());
    } else {
      set(distance_from_top, ref_top);
    }
    set(distance_from_bottom, get(innerHeight) - ref_bottom);
  }
  let scroll_timeout = null;
  function scroll_listener() {
    if (!show_options()) return;
    if (scroll_timeout !== null) {
      clearTimeout(scroll_timeout);
    }
    scroll_timeout = setTimeout(
      () => {
        calculate_window_distance();
        scroll_timeout = null;
      },
      10
    );
  }
  function restore_last_scroll() {
    get(listElement)?.scrollTo?.(0, get(list_scroll_y));
  }
  const dispatch = createEventDispatcher();
  legacy_pre_effect(
    () => (deep_read_state(show_options()), get(refElement), deep_read_state(remember_scroll()), get(listElement), deep_read_state(selected_indices()), get(input_height), get(distance_from_bottom), get(distance_from_top), deep_read_state(from_top())),
    () => {
      if (show_options() && get(refElement)) {
        if (remember_scroll()) {
          restore_last_scroll();
        } else {
          if (get(listElement) && selected_indices().length > 0) {
            let elements = get(listElement).querySelectorAll("li");
            for (const element of Array.from(elements)) {
              if (element.getAttribute("data-index") === selected_indices()[0].toString()) {
                get(listElement)?.scrollTo?.(0, element.offsetTop);
                break;
              }
            }
          }
        }
        calculate_window_distance();
        const rect = get(refElement).parentElement?.getBoundingClientRect();
        set(input_height, rect?.height || 0);
        set(input_width, rect?.width || 0);
      }
      if (get(distance_from_bottom) > get(distance_from_top) || from_top()) {
        set(top, `${get(distance_from_top)}px`);
        set(max_height, get(distance_from_bottom));
        set(bottom, null);
      } else {
        set(bottom, `${get(distance_from_bottom) + get(input_height)}px`);
        set(max_height, get(distance_from_top) - get(input_height));
        set(top, null);
      }
    }
  );
  legacy_pre_effect_reset();
  init();
  var fragment = root$1();
  event("scroll", $window, scroll_listener);
  var div = first_child(fragment);
  bind_this(div, ($$value) => set(refElement, $$value), () => get(refElement));
  var node = sibling(div, 2);
  {
    var consequent = ($$anchor2) => {
      var ul = root_1();
      let styles;
      each(ul, 5, filtered_indices, index, ($$anchor3, index2) => {
        var li = root_2$1();
        let classes;
        let styles_1;
        var span = child(li);
        let classes_1;
        var text2 = sibling(span);
        reset(li);
        template_effect(
          ($0, $1, $2) => {
            classes = set_class(li, 1, "item svelte-1ou0lab", null, classes, $0);
            set_attribute(li, "data-index", get(index2));
            set_attribute(li, "aria-label", (deep_read_state(choices()), get(index2), untrack(() => choices()[get(index2)][0])));
            set_attribute(li, "aria-selected", $1);
            styles_1 = set_style(li, "", styles_1, { width: get(input_width) + "px" });
            classes_1 = set_class(span, 1, "inner-item svelte-1ou0lab", null, classes_1, $2);
            set_text(text2, ` ${(deep_read_state(choices()), get(index2), untrack(() => choices()[get(index2)][0])) ?? ""}`);
          },
          [
            () => ({
              selected: selected_indices().includes(get(index2)),
              active: get(index2) === active_index(),
              "bg-gray-100": get(index2) === active_index(),
              "dark:bg-gray-600": get(index2) === active_index()
            }),
            () => (deep_read_state(selected_indices()), get(index2), untrack(() => selected_indices().includes(get(index2)))),
            () => ({ hide: !selected_indices().includes(get(index2)) })
          ]
        );
        append($$anchor3, li);
      });
      reset(ul);
      bind_this(ul, ($$value) => set(listElement, $$value), () => get(listElement));
      template_effect(() => styles = set_style(ul, "", styles, {
        top: get(top),
        bottom: get(bottom),
        "max-height": `calc(${get(max_height)}px - var(--window-padding))`,
        width: get(input_width) + "px"
      }));
      transition(3, ul, () => fly, () => ({ duration: 200, y: 5 }));
      event("mousedown", ul, preventDefault((e) => dispatch("change", e)));
      event("scroll", ul, (e) => set(list_scroll_y, e.currentTarget.scrollTop));
      append($$anchor2, ul);
    };
    if_block(node, ($$render) => {
      if (show_options() && !disabled()) $$render(consequent);
    });
  }
  bind_window_size("innerHeight", ($$value) => set(innerHeight, $$value));
  append($$anchor, fragment);
  pop();
}
function positive_mod(n, m) {
  return (n % m + m) % m;
}
function handle_filter(choices, input_text) {
  return choices.reduce((filtered_indices, o, index2) => {
    if (input_text ? o[0].toLowerCase().includes(input_text.toLowerCase()) : true) {
      filtered_indices.push(index2);
    }
    return filtered_indices;
  }, []);
}
function handle_shared_keys(e, active_index, filtered_indices) {
  if (e.key === "Escape") {
    return [false, active_index];
  }
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    if (filtered_indices.length > 0) {
      if (active_index === null) {
        active_index = e.key === "ArrowDown" ? filtered_indices[0] : filtered_indices[filtered_indices.length - 1];
      } else {
        const index_in_filtered = filtered_indices.indexOf(active_index);
        const increment = e.key === "ArrowUp" ? -1 : 1;
        active_index = filtered_indices[positive_mod(index_in_filtered + increment, filtered_indices.length)];
      }
    }
  }
  return [true, active_index];
}
var root_2 = from_html(`<div class="icon-wrap svelte-1xfsv4t"><!></div>`);
var root = from_html(`<div><!> <div class="wrap svelte-1xfsv4t"><div><div class="secondary-wrap svelte-1xfsv4t"><input role="listbox" aria-controls="dropdown-options" autocomplete="off"/> <!></div></div> <!></div></div>`);
function Dropdown($$anchor, $$props) {
  push($$props, true);
  const is_browser = typeof window !== "undefined";
  const gradio = $$props.gradio;
  let label = user_derived(() => gradio.shared.label || "Dropdown");
  let filter_input;
  let show_options = user_derived(() => {
    return is_browser && filter_input === document.activeElement;
  });
  let choices_names = user_derived(() => {
    return gradio.props.choices.map((c) => c[0]);
  });
  let choices_values = user_derived(() => {
    return gradio.props.choices.map((c) => c[1]);
  });
  let $$d = user_derived(() => {
    if (gradio.props.value === void 0 || Array.isArray(gradio.props.value) && gradio.props.value.length === 0) {
      return ["", null];
    } else if (get(choices_values).includes(gradio.props.value)) {
      return [
        get(choices_names)[get(choices_values).indexOf(gradio.props.value)],
        get(choices_values).indexOf(gradio.props.value)
      ];
    } else if (gradio.props.allow_custom_value) {
      return [gradio.props.value, null];
    } else {
      return ["", null];
    }
  }), $$array = user_derived(() => to_array(get($$d), 2)), input_text = user_derived(() => get($$array)[0]), selected_index = user_derived(() => get($$array)[1]);
  let initialized = state(false);
  let disabled = user_derived(() => !gradio.shared.interactive);
  let filtered_indices = state(proxy(gradio.props.choices.map((_, i) => i)));
  let active_index = state(null);
  if (gradio.props.value) {
    set(selected_index, gradio.props.choices.map((c) => c[1]).indexOf(gradio.props.value));
    if (get(selected_index) === -1) {
      set(selected_index, null);
    } else {
      set(input_text, gradio.props.choices[get(selected_index)][0]);
    }
  }
  function handle_option_selected(e) {
    set(selected_index, parseInt(e.detail.target.dataset.index));
    if (isNaN(get(selected_index))) {
      set(selected_index, null);
      return;
    }
    let [_input_text, _value] = gradio.props.choices[get(selected_index)];
    set(input_text, _input_text);
    gradio.props.value = _value;
    gradio.dispatch("select", {
      index: get(selected_index),
      value: get(choices_values)[get(selected_index)],
      selected: true
    });
    set(show_options, false);
    set(active_index, null);
    filter_input.blur();
  }
  function handle_focus(e) {
    set(filtered_indices, gradio.props.choices.map((_, i) => i), true);
    set(show_options, true);
    gradio.dispatch("focus");
  }
  function handle_blur() {
    if (!gradio.props.allow_custom_value) {
      set(input_text, get(choices_names)[get(choices_values).indexOf(gradio.props.value)]);
    } else {
      gradio.props.value = get(input_text);
    }
    set(show_options, false);
    set(active_index, null);
    set(filtered_indices, gradio.props.choices.map((_, i) => i), true);
    gradio.dispatch("blur");
    gradio.dispatch("input");
  }
  function handle_key_down(e) {
    set(filtered_indices, handle_filter(gradio.props.choices, get(input_text)), true);
    set(active_index, get(filtered_indices).length > 0 ? get(filtered_indices)[0] : null, true);
    (($$value) => {
      var $$array_1 = to_array($$value, 2);
      set(show_options, $$array_1[0]);
      set(active_index, $$array_1[1], true);
    })(handle_shared_keys(e, get(active_index), get(filtered_indices)));
    if (e.key === "Enter") {
      if (get(active_index) !== null) {
        set(selected_index, get(active_index));
        gradio.props.value = get(choices_values)[get(active_index)];
        set(show_options, false);
        filter_input.blur();
        set(active_index, null);
      } else if (get(choices_names).includes(get(input_text))) {
        set(selected_index, get(choices_names).indexOf(get(input_text)));
        gradio.props.value = get(choices_values)[get(selected_index)];
        set(show_options, false);
        set(active_index, null);
        filter_input.blur();
      } else if (gradio.props.allow_custom_value) {
        gradio.props.value = get(input_text);
        set(selected_index, null);
        set(show_options, false);
        set(active_index, null);
        filter_input.blur();
      }
    }
  }
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) !== gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  var div = root();
  let classes;
  var node = child(div);
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
  var div_1 = sibling(node, 2);
  var div_2 = child(div_1);
  let classes_1;
  var div_3 = child(div_2);
  var input = child(div_3);
  remove_input_defaults(input);
  let classes_2;
  bind_this(input, ($$value) => filter_input = $$value, () => filter_input);
  var node_1 = sibling(input, 2);
  {
    var consequent = ($$anchor2) => {
      var div_4 = root_2();
      var node_2 = child(div_4);
      DropdownArrow(node_2);
      reset(div_4);
      append($$anchor2, div_4);
    };
    if_block(node_1, ($$render) => {
      if (!get(disabled)) $$render(consequent);
    });
  }
  reset(div_3);
  reset(div_2);
  var node_3 = sibling(div_2, 2);
  {
    let $0 = user_derived(() => get(selected_index) === null ? [] : [get(selected_index)]);
    DropdownOptions(node_3, {
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
        return get($0);
      },
      get active_index() {
        return get(active_index);
      },
      $$events: {
        change: handle_option_selected,
        load: () => set(initialized, true)
      }
    });
  }
  reset(div_1);
  reset(div);
  template_effect(
    ($0) => {
      classes = set_class(div, 1, "svelte-1xfsv4t", null, classes, { container: gradio.shared.container });
      classes_1 = set_class(div_2, 1, "wrap-inner svelte-1xfsv4t", null, classes_1, { show_options: get(show_options) });
      set_attribute(input, "aria-expanded", get(show_options));
      set_attribute(input, "aria-label", get(label));
      classes_2 = set_class(input, 1, "border-none svelte-1xfsv4t", null, classes_2, $0);
      input.disabled = get(disabled);
      input.readOnly = !gradio.props.filterable;
    },
    [
      () => ({
        subdued: !get(choices_names).includes(get(input_text)) && !gradio.props.allow_custom_value
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
  append($$anchor, div);
  pop();
}
export {
  DropdownOptions as D,
  handle_shared_keys as a,
  Dropdown as b,
  handle_filter as h
};
//# sourceMappingURL=CxkJXoI9.js.map
