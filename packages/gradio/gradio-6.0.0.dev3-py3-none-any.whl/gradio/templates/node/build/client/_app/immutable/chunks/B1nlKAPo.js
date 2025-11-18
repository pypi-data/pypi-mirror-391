import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, I as onMount, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, k as get, n as legacy_pre_effect_reset, c as from_html, z as event, v as first_child, E as next, F as text, t as template_effect, b as append, s as sibling, o as pop, K as tick, $ as $window, d as child, r as reset, a8 as effect, g as set_text, A as user_derived, y as untrack, W as to_array } from "./DEzry6cj.js";
import { p as prop, i as if_block, b as bind_this, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { z as BlockTitle, r as remove_input_defaults, t as each, v as index, y as action, q as bind_value, a as set_class, c as bubble_event, p as set_style, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { i as init } from "./DB0xzveP.js";
import { t as tinycolor, E as Eyedropper } from "./BuyRlBBC.js";
import { default as default2 } from "./Dx0cSCYr.js";
function click_outside(node, callback) {
  const handle_click = (event2) => {
    if (node && !node.contains(event2.target) && !event2.defaultPrevented) {
      callback(event2);
    }
  };
  document.addEventListener("mousedown", handle_click, true);
  return {
    destroy() {
      document.removeEventListener("mousedown", handle_click, true);
    }
  };
}
function hsva_to_rgba(hsva) {
  const saturation = hsva.s;
  const value = hsva.v;
  let chroma = saturation * value;
  const hue_by_60 = hsva.h / 60;
  let x = chroma * (1 - Math.abs(hue_by_60 % 2 - 1));
  const m = value - chroma;
  chroma = chroma + m;
  x = x + m;
  const index2 = Math.floor(hue_by_60) % 6;
  const red = [chroma, x, m, m, x, chroma][index2];
  const green = [x, chroma, chroma, x, m, m][index2];
  const blue = [m, m, x, chroma, chroma, x][index2];
  return `rgba(${red * 255}, ${green * 255}, ${blue * 255}, ${hsva.a})`;
}
function format_color(color, mode) {
  if (mode === "hex") {
    return tinycolor(color).toHexString();
  } else if (mode === "rgb") {
    return tinycolor(color).toRgbString();
  }
  return tinycolor(color).toHslString();
}
var root_4 = from_html(`<button> </button>`);
var root_2 = from_html(`<div class="color-picker svelte-nbn1m9"><div class="color-gradient svelte-nbn1m9"><div class="marker svelte-nbn1m9"></div></div> <div class="hue-slider svelte-nbn1m9"><div class="marker svelte-nbn1m9"></div></div> <div class="input svelte-nbn1m9"><button class="swatch svelte-nbn1m9"></button> <div><div class="input-wrap svelte-nbn1m9"><input type="text" class="svelte-nbn1m9"/> <button class="eyedropper svelte-nbn1m9"><!></button></div> <div class="buttons svelte-nbn1m9"></div></div></div></div>`);
var root = from_html(`<!> <button class="dialog-button svelte-nbn1m9"></button> <!>`, 1);
function Colorpicker($$anchor, $$props) {
  push($$props, false);
  const color_string = mutable_source();
  let value = prop($$props, "value", 12, "#000000");
  let label = prop($$props, "label", 8);
  let info = prop($$props, "info", 8, void 0);
  let disabled = prop($$props, "disabled", 8, false);
  let show_label = prop($$props, "show_label", 8, true);
  let current_mode = prop($$props, "current_mode", 12, "hex");
  let dialog_open = prop($$props, "dialog_open", 12, false);
  let eyedropper_supported = mutable_source(false);
  let sl_wrap = mutable_source();
  let hue_wrap = mutable_source();
  const dispatch = createEventDispatcher();
  let sl_marker_pos = mutable_source([0, 0]);
  let sl_rect = null;
  let sl_moving = false;
  let sl = [0, 0];
  let hue = mutable_source(0);
  let hue_marker_pos = mutable_source(0);
  let hue_rect = null;
  let hue_moving = false;
  function handle_hue_down(event2) {
    hue_rect = event2.currentTarget.getBoundingClientRect();
    hue_moving = true;
    update_hue_from_mouse(event2.clientX);
  }
  function update_hue_from_mouse(x) {
    if (!hue_rect) return;
    const _x = Math.max(0, Math.min(x - hue_rect.left, hue_rect.width));
    set(hue_marker_pos, _x);
    const _hue = _x / hue_rect.width * 360;
    set(hue, _hue);
    value(hsva_to_rgba({ h: _hue, s: sl[0], v: sl[1], a: 1 }));
    dispatch("input");
  }
  function update_color_from_mouse(x, y) {
    if (!sl_rect) return;
    const _x = Math.max(0, Math.min(x - sl_rect.left, sl_rect.width));
    const _y = Math.max(0, Math.min(y - sl_rect.top, sl_rect.height));
    set(sl_marker_pos, [_x, _y]);
    const _hsva = {
      h: get(hue) * 1,
      s: _x / sl_rect.width,
      v: 1 - _y / sl_rect.height,
      a: 1
    };
    sl = [_hsva.s, _hsva.v];
    value(hsva_to_rgba(_hsva));
    dispatch("input");
  }
  function handle_sl_down(event2) {
    sl_moving = true;
    sl_rect = event2.currentTarget.getBoundingClientRect();
    update_color_from_mouse(event2.clientX, event2.clientY);
  }
  function handle_move(event2) {
    if (sl_moving) update_color_from_mouse(event2.clientX, event2.clientY);
    if (hue_moving) update_hue_from_mouse(event2.clientX);
  }
  function handle_end() {
    sl_moving = false;
    hue_moving = false;
  }
  async function update_mouse_from_color(color) {
    if (sl_moving || hue_moving) return;
    await tick();
    if (!color) return;
    if (!sl_rect && get(sl_wrap)) {
      sl_rect = get(sl_wrap).getBoundingClientRect();
    }
    if (!hue_rect && get(hue_wrap)) {
      hue_rect = get(hue_wrap).getBoundingClientRect();
    }
    if (!sl_rect || !hue_rect) return;
    const hsva = tinycolor(color).toHsv();
    const _x = hsva.s * sl_rect.width;
    const _y = (1 - hsva.v) * sl_rect.height;
    set(sl_marker_pos, [_x, _y]);
    sl = [hsva.s, hsva.v];
    set(hue, hsva.h);
    set(hue_marker_pos, hsva.h / 360 * hue_rect.width);
  }
  function request_eyedropper() {
    const eyeDropper = new EyeDropper();
    eyeDropper.open().then((result) => {
      value(result.sRGBHex);
    });
    dispatch("input");
  }
  const modes = [["Hex", "hex"], ["RGB", "rgb"], ["HSL", "hsl"]];
  onMount(async () => {
    set(eyedropper_supported, window !== void 0 && !!window.EyeDropper);
  });
  function handle_click_outside() {
    dialog_open(false);
  }
  function handle_change() {
    dispatch("change", value());
  }
  function handle_click() {
    dispatch("selected", get(color_string));
    dispatch("close");
  }
  legacy_pre_effect(
    () => (deep_read_state(value()), deep_read_state(current_mode())),
    () => {
      set(color_string, format_color(value(), current_mode()));
    }
  );
  legacy_pre_effect(() => get(color_string), () => {
    get(color_string) && dispatch("selected", get(color_string));
  });
  legacy_pre_effect(() => deep_read_state(value()), () => {
    update_mouse_from_color(value());
  });
  legacy_pre_effect(() => deep_read_state(value()), () => {
    value(), handle_change();
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root();
  event("mousemove", $window, handle_move);
  event("mouseup", $window, handle_end);
  var node = first_child(fragment);
  BlockTitle(node, {
    get show_label() {
      return show_label();
    },
    get info() {
      return info();
    },
    children: ($$anchor2, $$slotProps) => {
      next();
      var text$1 = text();
      template_effect(() => set_text(text$1, label()));
      append($$anchor2, text$1);
    },
    $$slots: { default: true }
  });
  var button = sibling(node, 2);
  let styles;
  var node_1 = sibling(button, 2);
  {
    var consequent_1 = ($$anchor2) => {
      var div = root_2();
      var div_1 = child(div);
      var div_2 = child(div_1);
      let styles_1;
      reset(div_1);
      bind_this(div_1, ($$value) => set(sl_wrap, $$value), () => get(sl_wrap));
      var div_3 = sibling(div_1, 2);
      var div_4 = child(div_3);
      let styles_2;
      reset(div_3);
      bind_this(div_3, ($$value) => set(hue_wrap, $$value), () => get(hue_wrap));
      var div_5 = sibling(div_3, 2);
      var button_1 = child(div_5);
      let styles_3;
      var div_6 = sibling(button_1, 2);
      var div_7 = child(div_6);
      var input = child(div_7);
      remove_input_defaults(input);
      var button_2 = sibling(input, 2);
      var node_2 = child(button_2);
      {
        var consequent = ($$anchor3) => {
          Eyedropper($$anchor3);
        };
        if_block(node_2, ($$render) => {
          if (get(eyedropper_supported)) $$render(consequent);
        });
      }
      reset(button_2);
      reset(div_7);
      var div_8 = sibling(div_7, 2);
      each(div_8, 5, () => modes, index, ($$anchor3, $$item, $$index, $$array) => {
        var $$array_1 = user_derived(() => to_array(get($$item), 2));
        let label2 = () => get($$array_1)[0];
        let value2 = () => get($$array_1)[1];
        var button_3 = root_4();
        let classes;
        var text_1 = child(button_3, true);
        reset(button_3);
        template_effect(() => {
          classes = set_class(button_3, 1, "button svelte-nbn1m9", null, classes, { active: current_mode() === value2() });
          set_text(text_1, label2());
        });
        event("click", button_3, () => current_mode(value2()));
        append($$anchor3, button_3);
      });
      reset(div_8);
      reset(div_6);
      reset(div_5);
      reset(div);
      effect(() => event("focus", div, function($$arg) {
        bubble_event.call(this, $$props, $$arg);
      }));
      effect(() => event("blur", div, function($$arg) {
        bubble_event.call(this, $$props, $$arg);
      }));
      action(div, ($$node, $$action_arg) => click_outside?.($$node, $$action_arg), () => handle_click_outside);
      template_effect(() => {
        set_style(div_1, `--hue:${get(hue) ?? ""}`);
        styles_1 = set_style(div_2, "", styles_1, {
          transform: `translate(${(get(sl_marker_pos), untrack(() => get(sl_marker_pos)[0])) ?? ""}px,${(get(sl_marker_pos), untrack(() => get(sl_marker_pos)[1])) ?? ""}px)`,
          background: value()
        });
        styles_2 = set_style(div_4, "", styles_2, {
          background: "hsl(" + get(hue) + ", 100%, 50%)",
          transform: `translateX(${get(hue_marker_pos) ?? ""}px)`
        });
        styles_3 = set_style(button_1, "", styles_3, { background: value() });
      });
      event("mousedown", div_1, handle_sl_down);
      event("mousedown", div_3, handle_hue_down);
      event("click", button_1, handle_click);
      bind_value(input, () => get(color_string), ($$value) => set(color_string, $$value));
      event("change", input, (e) => {
        value(e.currentTarget.value);
      });
      event("click", button_2, request_eyedropper);
      append($$anchor2, div);
    };
    if_block(node_1, ($$render) => {
      if (dialog_open()) $$render(consequent_1);
    });
  }
  template_effect(() => {
    button.disabled = disabled();
    styles = set_style(button, "", styles, { background: value() });
  });
  event("click", button, () => {
    update_mouse_from_color(value());
    dialog_open(!dialog_open());
  });
  append($$anchor, fragment);
  pop();
}
var root_1 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let label = user_derived(() => gradio.shared.label || gradio.i18n("colorpicker.color_picker"));
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
        let $0 = user_derived(() => !gradio.shared.interactive);
        Colorpicker(node_1, {
          get label() {
            return get(label);
          },
          get info() {
            return gradio.props.info;
          },
          get show_label() {
            return gradio.shared.show_label;
          },
          get disabled() {
            return get($0);
          },
          get value() {
            return gradio.props.value;
          },
          set value($$value) {
            gradio.props.value = $$value;
          },
          $$events: {
            change: () => gradio.dispatch("change"),
            input: () => gradio.dispatch("input"),
            submit: () => gradio.dispatch("submit"),
            blur: () => gradio.dispatch("blur"),
            focus: () => gradio.dispatch("focus")
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
  Colorpicker as BaseColorPicker,
  default2 as BaseExample,
  Index as default
};
//# sourceMappingURL=B1nlKAPo.js.map
