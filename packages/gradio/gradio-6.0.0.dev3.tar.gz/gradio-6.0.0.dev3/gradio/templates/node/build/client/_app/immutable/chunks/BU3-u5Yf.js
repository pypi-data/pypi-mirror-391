import "./9B4_veAf.js";
import { f as from_svg, b as append, p as push, q as createEventDispatcher, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, s as sibling, r as reset, t as template_effect, z as event, o as pop, k as get, g as set_text, y as untrack, J as state, L as proxy, M as user_effect, N as onDestroy, v as first_child, E as next, F as text, A as user_derived } from "./DEzry6cj.js";
import { p as prop, i as if_block, u as update_prop, r as rest_props, b as bind_this } from "./DUftb7my.js";
import { t as each, v as index, r as remove_input_defaults, q as bind_value, a as set_class, p as set_style, G as Gradio, B as Block, z as BlockTitle, s as set_attribute } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { i as init } from "./DB0xzveP.js";
import { default as default2 } from "./BBBBNd64.js";
var root$1 = from_svg(`<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"></rect><line x1="2" y1="9" x2="22" y2="9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"></line><line x1="7" y1="2" x2="7" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"></line><line x1="17" y1="2" x2="17" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"></line></svg>`);
function Calendar($$anchor) {
  var svg = root$1();
  append($$anchor, svg);
}
const format_date = (date, include_time) => {
  if (date.toJSON() === null) return "";
  const pad = (num) => num.toString().padStart(2, "0");
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const seconds = pad(date.getSeconds());
  const date_str = `${year}-${month}-${day}`;
  const time_str = `${hours}:${minutes}:${seconds}`;
  if (include_time) {
    return `${date_str} ${time_str}`;
  }
  return date_str;
};
const date_is_valid_format = (date, include_time) => {
  if (date == null || date === "") return true;
  const valid_regex = include_time ? /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/ : /^\d{4}-\d{2}-\d{2}$/;
  const is_valid_date = date.match(valid_regex) !== null;
  const is_valid_now = date.match(/^(?:\s*now\s*(?:-\s*\d+\s*[dmhs])?)?\s*$/) !== null;
  return is_valid_date || is_valid_now;
};
const get_days_in_month = (year, month) => {
  return new Date(year, month + 1, 0).getDate();
};
const get_first_day_of_month = (year, month) => {
  return new Date(year, month, 1).getDay();
};
const parse_date_value = (entered_value, include_time) => {
  if (!entered_value || entered_value === "") {
    const now2 = /* @__PURE__ */ new Date();
    return {
      selected_date: now2,
      current_year: now2.getFullYear(),
      current_month: now2.getMonth(),
      selected_hour: now2.getHours(),
      selected_minute: now2.getMinutes(),
      selected_second: now2.getSeconds(),
      is_pm: now2.getHours() >= 12
    };
  }
  try {
    let date_to_parse = entered_value;
    if (!include_time && entered_value.match(/^\d{4}-\d{2}-\d{2}$/)) {
      date_to_parse += " 00:00:00";
    }
    const parsed = new Date(date_to_parse.replace(" ", "T"));
    if (!isNaN(parsed.getTime())) {
      return {
        selected_date: parsed,
        current_year: parsed.getFullYear(),
        current_month: parsed.getMonth(),
        selected_hour: parsed.getHours(),
        selected_minute: parsed.getMinutes(),
        selected_second: parsed.getSeconds(),
        is_pm: parsed.getHours() >= 12
      };
    }
  } catch (e) {
  }
  const now = /* @__PURE__ */ new Date();
  return {
    selected_date: now,
    current_year: now.getFullYear(),
    current_month: now.getMonth(),
    selected_hour: now.getHours(),
    selected_minute: now.getMinutes(),
    selected_second: now.getSeconds(),
    is_pm: now.getHours() >= 12
  };
};
const generate_calendar_days = (current_year, current_month) => {
  const days_in_month = get_days_in_month(current_year, current_month);
  const first_day = get_first_day_of_month(current_year, current_month);
  const days = [];
  const prev_month = current_month === 0 ? 11 : current_month - 1;
  const prev_year = current_month === 0 ? current_year - 1 : current_year;
  const days_in_prev_month = get_days_in_month(prev_year, prev_month);
  for (let i = first_day - 1; i >= 0; i--) {
    days.push({
      day: days_in_prev_month - i,
      is_current_month: false,
      is_next_month: false
    });
  }
  for (let day = 1; day <= days_in_month; day++) {
    days.push({
      day,
      is_current_month: true,
      is_next_month: false
    });
  }
  const remaining_slots = 42 - days.length;
  for (let day = 1; day <= remaining_slots; day++) {
    days.push({
      day,
      is_current_month: false,
      is_next_month: true
    });
  }
  return days;
};
const calculate_display_hour = (selected_hour, is_pm) => {
  return is_pm ? selected_hour === 0 ? 12 : selected_hour > 12 ? selected_hour - 12 : selected_hour : selected_hour === 0 ? 12 : selected_hour;
};
const convert_display_hour_to_24h = (display_hour, is_pm) => {
  if (is_pm) {
    return display_hour === 12 ? 12 : display_hour + 12;
  }
  return display_hour === 12 ? 0 : display_hour;
};
const month_names = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December"
];
var root_1$1 = from_html(`<button type="button"> </button>`);
var root_2 = from_html(`<div class="time-picker svelte-s8mqj7"><div class="time-inputs svelte-s8mqj7"><div class="time-input-group svelte-s8mqj7"><label for="hour" class="svelte-s8mqj7">Hour</label> <input id="hour" type="number" min="1" max="12" class="svelte-s8mqj7"/></div> <div class="time-input-group svelte-s8mqj7"><label for="minute" class="svelte-s8mqj7">Min</label> <input id="minute" type="number" min="0" max="59" class="svelte-s8mqj7"/></div> <div class="time-input-group svelte-s8mqj7"><label for="second" class="svelte-s8mqj7">Sec</label> <input id="second" type="number" min="0" max="59" class="svelte-s8mqj7"/></div> <div class="time-input-group svelte-s8mqj7"><span class="am-pm-label svelte-s8mqj7">Period</span> <button type="button" class="am-pm-toggle svelte-s8mqj7" aria-label="Toggle AM/PM"> </button></div></div></div>`);
var root = from_html(`<div class="picker-container svelte-s8mqj7"><div class="picker svelte-s8mqj7"><div class="picker-header svelte-s8mqj7"><button type="button" class="nav-button svelte-s8mqj7">‹</button> <div class="month-year svelte-s8mqj7"> </div> <button type="button" class="nav-button svelte-s8mqj7">›</button></div> <div class="calendar-grid svelte-s8mqj7"><div class="weekdays svelte-s8mqj7"><div class="weekday svelte-s8mqj7">Su</div> <div class="weekday svelte-s8mqj7">Mo</div> <div class="weekday svelte-s8mqj7">Tu</div> <div class="weekday svelte-s8mqj7">We</div> <div class="weekday svelte-s8mqj7">Th</div> <div class="weekday svelte-s8mqj7">Fr</div> <div class="weekday svelte-s8mqj7">Sa</div></div> <div class="days svelte-s8mqj7"></div></div> <!> <div class="picker-actions svelte-s8mqj7"><button type="button" class="action-button svelte-s8mqj7">Clear</button> <div class="picker-actions-right svelte-s8mqj7"><button type="button" class="action-button svelte-s8mqj7">Now</button> <button type="button" class="action-button svelte-s8mqj7">Done</button></div></div></div></div>`);
function DateTimePicker($$anchor, $$props) {
  push($$props, false);
  const display_hour = mutable_source();
  const calendar_days = mutable_source();
  let selected_date = prop($$props, "selected_date", 12);
  let current_year = prop($$props, "current_year", 12);
  let current_month = prop($$props, "current_month", 12);
  let selected_hour = prop($$props, "selected_hour", 12);
  let selected_minute = prop($$props, "selected_minute", 12);
  let selected_second = prop($$props, "selected_second", 12);
  let is_pm = prop($$props, "is_pm", 12);
  let include_time = prop($$props, "include_time", 8);
  let position = prop($$props, "position", 8);
  const dispatch = createEventDispatcher();
  const select_date = (day) => {
    selected_date(new Date(current_year(), current_month(), day, selected_hour(), selected_minute(), selected_second()));
    update_value();
  };
  const update_value = () => {
    const formatted = format_date(selected_date(), include_time());
    dispatch("update", { date: selected_date(), formatted });
  };
  const update_time = () => {
    selected_date(new Date(current_year(), current_month(), selected_date().getDate(), selected_hour(), selected_minute(), selected_second()));
    update_value();
  };
  const previous_month = () => {
    if (current_month() === 0) {
      current_month(11);
      update_prop(current_year, -1);
    } else {
      update_prop(current_month, -1);
    }
  };
  const next_month = () => {
    if (current_month() === 11) {
      current_month(0);
      update_prop(current_year);
    } else {
      update_prop(current_month);
    }
  };
  const toggle_am_pm = () => {
    is_pm(!is_pm());
    if (is_pm() && selected_hour() < 12) {
      selected_hour(selected_hour() + 12);
    } else if (!is_pm() && selected_hour() >= 12) {
      selected_hour(selected_hour() - 12);
    }
    update_time();
  };
  const update_display_hour = (new_hour) => {
    selected_hour(convert_display_hour_to_24h(new_hour, is_pm()));
    update_time();
  };
  const handle_now = () => {
    const now = /* @__PURE__ */ new Date();
    selected_date(now);
    current_year(now.getFullYear());
    current_month(now.getMonth());
    selected_hour(now.getHours());
    selected_minute(now.getMinutes());
    selected_second(now.getSeconds());
    is_pm(selected_hour() >= 12);
    update_value();
  };
  legacy_pre_effect(
    () => (deep_read_state(selected_hour()), deep_read_state(is_pm())),
    () => {
      set(display_hour, calculate_display_hour(selected_hour(), is_pm()));
    }
  );
  legacy_pre_effect(
    () => (deep_read_state(current_year()), deep_read_state(current_month())),
    () => {
      set(calendar_days, generate_calendar_days(current_year(), current_month()));
    }
  );
  legacy_pre_effect_reset();
  init();
  var div = root();
  var div_1 = child(div);
  var div_2 = child(div_1);
  var button = child(div_2);
  var div_3 = sibling(button, 2);
  var text2 = child(div_3);
  reset(div_3);
  var button_1 = sibling(div_3, 2);
  reset(div_2);
  var div_4 = sibling(div_2, 2);
  var div_5 = sibling(child(div_4), 2);
  each(div_5, 5, () => get(calendar_days), index, ($$anchor2, $$item) => {
    let day = () => get($$item).day;
    let is_current_month = () => get($$item).is_current_month;
    let is_next_month = () => get($$item).is_next_month;
    var button_2 = root_1$1();
    let classes;
    var text_1 = child(button_2, true);
    reset(button_2);
    template_effect(
      ($0) => {
        classes = set_class(button_2, 1, "day svelte-s8mqj7", null, classes, $0);
        set_text(text_1, day());
      },
      [
        () => ({
          "other-month": !is_current_month(),
          selected: is_current_month() && day() === selected_date().getDate() && current_month() === selected_date().getMonth() && current_year() === selected_date().getFullYear()
        })
      ]
    );
    event("click", button_2, () => {
      if (is_current_month()) {
        select_date(day());
      } else if (is_next_month()) {
        next_month();
        select_date(day());
      } else {
        previous_month();
        select_date(day());
      }
    });
    append($$anchor2, button_2);
  });
  reset(div_5);
  reset(div_4);
  var node = sibling(div_4, 2);
  {
    var consequent = ($$anchor2) => {
      var div_6 = root_2();
      var div_7 = child(div_6);
      var div_8 = child(div_7);
      var input = sibling(child(div_8), 2);
      remove_input_defaults(input);
      reset(div_8);
      var div_9 = sibling(div_8, 2);
      var input_1 = sibling(child(div_9), 2);
      remove_input_defaults(input_1);
      reset(div_9);
      var div_10 = sibling(div_9, 2);
      var input_2 = sibling(child(div_10), 2);
      remove_input_defaults(input_2);
      reset(div_10);
      var div_11 = sibling(div_10, 2);
      var button_3 = sibling(child(div_11), 2);
      var text_2 = child(button_3, true);
      reset(button_3);
      reset(div_11);
      reset(div_7);
      reset(div_6);
      template_effect(() => set_text(text_2, is_pm() ? "PM" : "AM"));
      bind_value(input, () => get(display_hour), ($$value) => set(display_hour, $$value));
      event("input", input, () => update_display_hour(get(display_hour)));
      bind_value(input_1, selected_minute);
      event("input", input_1, update_time);
      bind_value(input_2, selected_second);
      event("input", input_2, update_time);
      event("click", button_3, toggle_am_pm);
      append($$anchor2, div_6);
    };
    if_block(node, ($$render) => {
      if (include_time()) $$render(consequent);
    });
  }
  var div_12 = sibling(node, 2);
  var button_4 = child(div_12);
  var div_13 = sibling(button_4, 2);
  var button_5 = child(div_13);
  var button_6 = sibling(button_5, 2);
  reset(div_13);
  reset(div_12);
  reset(div_1);
  reset(div);
  template_effect(() => {
    set_style(div, `top: ${(deep_read_state(position()), untrack(() => position().top)) ?? ""}px; left: ${(deep_read_state(position()), untrack(() => position().left)) ?? ""}px;`);
    set_text(text2, `${(deep_read_state(month_names), deep_read_state(current_month()), untrack(() => month_names[current_month()])) ?? ""}
				${current_year() ?? ""}`);
  });
  event("click", button, previous_month);
  event("click", button_1, next_month);
  event("click", button_4, () => dispatch("clear"));
  event("click", button_5, handle_now);
  event("click", button_6, () => dispatch("close"));
  append($$anchor, div);
  pop();
}
var root_3 = from_html(`<button class="calendar svelte-16sct4k"><!></button>`);
var root_4 = from_html(`<div class="svelte-16sct4k"><!></div>`);
var root_1 = from_html(`<div class="label-content svelte-16sct4k"><!></div> <div class="timebox svelte-16sct4k"><input/> <!></div> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let old_value = state(proxy(gradio.props.value));
  let show_picker = state(false);
  let entered_value = state(proxy(gradio.props.value));
  let picker_ref;
  let input_ref;
  let calendar_button_ref;
  let picker_position = state(proxy({ top: 0, left: 0 }));
  let current_year = state(proxy((/* @__PURE__ */ new Date()).getFullYear()));
  let current_month = state(proxy((/* @__PURE__ */ new Date()).getMonth()));
  let selected_date = state(proxy(/* @__PURE__ */ new Date()));
  let selected_hour = state(proxy((/* @__PURE__ */ new Date()).getHours()));
  let selected_minute = state(proxy((/* @__PURE__ */ new Date()).getMinutes()));
  let selected_second = state(proxy((/* @__PURE__ */ new Date()).getSeconds()));
  let is_pm = state(get(selected_hour) >= 12);
  let valid = user_derived(() => date_is_valid_format(get(entered_value), gradio.props.include_time));
  let disabled = user_derived(() => !gradio.shared.interactive);
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      set(entered_value, gradio.props.value, true);
      update_picker_from_value();
      gradio.dispatch("change");
    }
  });
  const update_picker_from_value = () => {
    const parsed = parse_date_value(get(entered_value), gradio.props.include_time);
    set(selected_date, parsed.selected_date, true);
    set(current_year, parsed.current_year, true);
    set(current_month, parsed.current_month, true);
    set(selected_hour, parsed.selected_hour, true);
    set(selected_minute, parsed.selected_minute, true);
    set(selected_second, parsed.selected_second, true);
    set(is_pm, parsed.is_pm, true);
  };
  const submit_values = () => {
    if (get(entered_value) === gradio.props.value) return;
    if (!date_is_valid_format(get(entered_value), gradio.props.include_time)) return;
    set(old_value, gradio.props.value = get(entered_value), true);
    gradio.dispatch("change");
  };
  const calculate_picker_position = () => {
    if (calendar_button_ref) {
      const rect = calendar_button_ref.getBoundingClientRect();
      set(picker_position, { top: rect.bottom + 4, left: rect.right - 280 }, true);
    }
  };
  const toggle_picker = (event2) => {
    if (!get(disabled)) {
      event2.stopPropagation();
      set(show_picker, !get(show_picker));
      if (get(show_picker)) {
        update_picker_from_value();
        calculate_picker_position();
        setTimeout(
          () => {
            if (typeof window !== "undefined") {
              window.addEventListener("click", handle_click_outside);
              window.addEventListener("scroll", handle_scroll, true);
            }
          },
          10
        );
      } else if (typeof window !== "undefined") {
        window.removeEventListener("click", handle_click_outside);
        window.removeEventListener("scroll", handle_scroll, true);
      }
    }
  };
  const close_picker = () => {
    set(show_picker, false);
    if (typeof window !== "undefined") {
      window.removeEventListener("click", handle_click_outside);
      window.removeEventListener("scroll", handle_scroll, true);
    }
  };
  const handle_click_outside = (event2) => {
    if (get(show_picker) && picker_ref && !picker_ref.contains(event2.target) && calendar_button_ref && !calendar_button_ref.contains(event2.target)) {
      close_picker();
    }
  };
  const handle_scroll = () => {
    if (get(show_picker)) {
      calculate_picker_position();
    }
  };
  const handle_picker_update = (event2) => {
    set(entered_value, event2.detail.formatted, true);
    submit_values();
  };
  const handle_picker_clear = () => {
    set(entered_value, "");
    gradio.props.value = "";
    close_picker();
    gradio.dispatch("change");
  };
  onDestroy(() => {
    if (typeof window !== "undefined") {
      window.removeEventListener("click", handle_click_outside);
      window.removeEventListener("scroll", handle_scroll, true);
    }
  });
  update_picker_from_value();
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
    padding: true,
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var div = first_child(fragment_1);
      var node = child(div);
      BlockTitle(node, {
        get show_label() {
          return gradio.shared.show_label;
        },
        get info() {
          return gradio.props.info;
        },
        children: ($$anchor3, $$slotProps2) => {
          next();
          var text$1 = text();
          template_effect(() => set_text(text$1, gradio.shared.label || "Date"));
          append($$anchor3, text$1);
        },
        $$slots: { default: true }
      });
      reset(div);
      var div_1 = sibling(div, 2);
      var input = child(div_1);
      remove_input_defaults(input);
      let classes;
      bind_this(input, ($$value) => input_ref = $$value, () => input_ref);
      var node_1 = sibling(input, 2);
      {
        var consequent = ($$anchor3) => {
          var button = root_3();
          var node_2 = child(button);
          Calendar(node_2);
          reset(button);
          bind_this(button, ($$value) => calendar_button_ref = $$value, () => calendar_button_ref);
          template_effect(() => button.disabled = get(disabled));
          event("click", button, toggle_picker);
          append($$anchor3, button);
        };
        if_block(node_1, ($$render) => {
          if (gradio.shared.interactive) $$render(consequent);
        });
      }
      reset(div_1);
      var node_3 = sibling(div_1, 2);
      {
        var consequent_1 = ($$anchor3) => {
          var div_2 = root_4();
          var node_4 = child(div_2);
          DateTimePicker(node_4, {
            get include_time() {
              return gradio.props.include_time;
            },
            get position() {
              return get(picker_position);
            },
            get selected_date() {
              return get(selected_date);
            },
            set selected_date($$value) {
              set(selected_date, $$value, true);
            },
            get current_year() {
              return get(current_year);
            },
            set current_year($$value) {
              set(current_year, $$value, true);
            },
            get current_month() {
              return get(current_month);
            },
            set current_month($$value) {
              set(current_month, $$value, true);
            },
            get selected_hour() {
              return get(selected_hour);
            },
            set selected_hour($$value) {
              set(selected_hour, $$value, true);
            },
            get selected_minute() {
              return get(selected_minute);
            },
            set selected_minute($$value) {
              set(selected_minute, $$value, true);
            },
            get selected_second() {
              return get(selected_second);
            },
            set selected_second($$value) {
              set(selected_second, $$value, true);
            },
            get is_pm() {
              return get(is_pm);
            },
            set is_pm($$value) {
              set(is_pm, $$value, true);
            },
            $$events: {
              update: handle_picker_update,
              clear: handle_picker_clear,
              close: close_picker
            }
          });
          reset(div_2);
          bind_this(div_2, ($$value) => picker_ref = $$value, () => picker_ref);
          append($$anchor3, div_2);
        };
        if_block(node_3, ($$render) => {
          if (get(show_picker)) $$render(consequent_1);
        });
      }
      template_effect(() => {
        classes = set_class(input, 1, "time svelte-16sct4k", null, classes, { invalid: !get(valid) });
        input.disabled = get(disabled);
        set_attribute(input, "placeholder", gradio.props.include_time ? "YYYY-MM-DD HH:MM:SS" : "YYYY-MM-DD");
      });
      bind_value(input, () => get(entered_value), ($$value) => set(entered_value, $$value));
      event("keydown", input, (evt) => {
        if (evt.key === "Enter") {
          submit_values();
          gradio.dispatch("submit");
        }
      });
      event("blur", input, submit_values);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  default2 as BaseExample,
  Index as default
};
//# sourceMappingURL=BU3-u5Yf.js.map
