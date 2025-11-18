import "./9B4_veAf.js";
import { f as from_svg, b as append, K as tick, p as push, m as mutable_source, q as createEventDispatcher, am as beforeUpdate, k as get, I as onMount, a0 as afterUpdate, i as legacy_pre_effect, j as set, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, E as next, F as text, t as template_effect, s as sibling, y as untrack, V as remove_textarea_child, a8 as effect, z as event, r as reset, o as pop, g as set_text, D as comment, v as first_child, J as state, A as user_derived } from "./DEzry6cj.js";
import { p as prop, i as if_block, b as bind_this, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { z as BlockTitle, y as action, q as bind_value, c as bubble_event, t as each, v as index, a as set_class, C as Clear, j as Image, a1 as Square, s as set_attribute, p as set_style, N as preventDefault, B as Block, g as Static, G as Gradio } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { i as init } from "./DB0xzveP.js";
import { A as ArrowUp } from "./D7IeRqAg.js";
import { F as File } from "./bc1v6JFX.js";
import { M as Microphone } from "./jPEKutgU.js";
import { M as Music } from "./Dr2P5Z1a.js";
import { V as Video } from "./B7T4xKTK.js";
import { U as Upload } from "./BcroWaqq.js";
/* empty css         */
import "./CxZmGzlA.js";
import { I as InteractiveAudio } from "./D2gsMg7z.js";
/* empty css         */
import { default as default2 } from "./BJZZzk1u.js";
var root = from_svg(`<svg fill="currentColor" width="100%" height="100%" viewBox="0 0 1920 1920" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M1752.768 221.109C1532.646.986 1174.283.986 954.161 221.109l-838.588 838.588c-154.052 154.165-154.052 404.894 0 558.946 149.534 149.421 409.976 149.308 559.059 0l758.738-758.626c87.982-88.094 87.982-231.417 0-319.51-88.32-88.208-231.642-87.982-319.51 0l-638.796 638.908 79.85 79.849 638.795-638.908c43.934-43.821 115.539-43.934 159.812 0 43.934 44.047 43.934 115.877 0 159.812l-758.739 758.625c-110.23 110.118-289.355 110.005-399.36 0-110.118-110.117-110.005-289.242 0-399.247l838.588-838.588c175.963-175.962 462.382-176.188 638.909 0 176.075 176.188 176.075 462.833 0 638.908l-798.607 798.72 79.849 79.85 798.607-798.72c220.01-220.123 220.01-578.485 0-798.607" fill-rule="evenodd"></path></g></svg>`);
function Paperclip($$anchor) {
  var svg = root();
  append($$anchor, svg);
}
async function resize(target, lines, max_lines) {
  await tick();
  if (lines === max_lines) return;
  const computed_styles = window.getComputedStyle(target);
  const padding_top = parseFloat(computed_styles.paddingTop);
  const padding_bottom = parseFloat(computed_styles.paddingBottom);
  const line_height = parseFloat(computed_styles.lineHeight);
  let max = max_lines === void 0 ? false : padding_top + padding_bottom + line_height * max_lines;
  let min = padding_top + padding_bottom + lines * line_height;
  target.style.height = "1px";
  let scroll_height;
  if (max && target.scrollHeight > max) {
    scroll_height = max;
  } else if (target.scrollHeight < min) {
    scroll_height = min;
  } else {
    scroll_height = target.scrollHeight;
  }
  target.style.height = `${scroll_height}px`;
}
function text_area_resize(_el, _value) {
  if (_value.lines === _value.max_lines) return;
  _el.style.overflowY = "scroll";
  function handle_input(event2) {
    resize(event2.target, _value.lines, _value.max_lines);
  }
  _el.addEventListener("input", handle_input);
  if (!_value.text.trim()) return;
  resize(_el, _value.lines, _value.max_lines);
  return {
    destroy: () => _el.removeEventListener("input", handle_input)
  };
}
var root_6 = from_html(`<button data-testid="upload-button" class="upload-button mobile-thumbnail-add svelte-1qn0337" aria-label="Upload a file"><!></button>`);
var root_7 = from_html(`<span class="thumbnail-wrapper svelte-1qn0337" role="listitem" aria-label="File thumbnail"><div class="thumbnail-item thumbnail-small svelte-1qn0337"><!> <button class="delete-button svelte-1qn0337" aria-label="Remove file"><!></button></div></span>`);
var root_14 = from_html(`<div class="loader svelte-1qn0337" role="status" aria-label="Uploading"></div>`);
var root_5 = from_html(`<div class="thumbnails svelte-1qn0337" aria-label="Uploaded files" data-testid="container_el"><!> <!> <!></div>`);
var root_15 = from_html(`<button data-testid="microphone-button" aria-label="Record audio"><!></button>`);
var root_16 = from_html(`<button aria-label="Submit"><!></button>`);
var root_19 = from_html(`<button aria-label="Stop"><!></button>`);
var root_1$1 = from_html(`<div role="group" aria-label="Multimedia input field"><!> <div class="input-container svelte-1qn0337"><!> <!> <div><!> <div class="input-row svelte-1qn0337"><textarea data-testid="textbox"></textarea> <!> <!> <!></div></div></div></div>`);
function MultimodalTextbox($$anchor, $$props) {
  push($$props, false);
  const sources = mutable_source();
  const file_types = mutable_source();
  const show_upload = mutable_source();
  let value = prop($$props, "value", 28, () => ({ text: "", files: [] }));
  let value_is_output = prop($$props, "value_is_output", 8, false);
  let lines = prop($$props, "lines", 8, 1);
  let i18n = prop($$props, "i18n", 8);
  let placeholder = prop($$props, "placeholder", 8, "Type here...");
  let disabled = prop($$props, "disabled", 8, false);
  let label = prop($$props, "label", 8);
  let info = prop($$props, "info", 8, void 0);
  let show_label = prop($$props, "show_label", 8, true);
  let max_lines = prop($$props, "max_lines", 8);
  let submit_btn = prop($$props, "submit_btn", 8, null);
  let stop_btn = prop($$props, "stop_btn", 8, null);
  let rtl = prop($$props, "rtl", 8, false);
  let autofocus = prop($$props, "autofocus", 8, false);
  let text_align = prop($$props, "text_align", 8, void 0);
  let autoscroll = prop($$props, "autoscroll", 8, true);
  let root2 = prop($$props, "root", 8);
  let file_types_string = prop($$props, "file_types_string", 8, null);
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let upload = prop($$props, "upload", 8);
  let stream_handler = prop($$props, "stream_handler", 8);
  let file_count = prop($$props, "file_count", 8, "multiple");
  let max_plain_text_length = prop($$props, "max_plain_text_length", 8, 1e3);
  let waveform_settings = prop($$props, "waveform_settings", 8);
  let waveform_options = prop($$props, "waveform_options", 24, () => ({ show_recording_waveform: true }));
  let sources_string = prop($$props, "sources_string", 8, "upload");
  let active_source = prop($$props, "active_source", 12, null);
  let html_attributes = prop($$props, "html_attributes", 8, null);
  let upload_promise = prop($$props, "upload_promise", 12, null);
  let upload_component = mutable_source();
  let el = mutable_source();
  let can_scroll;
  let previous_scroll_top = 0;
  let user_has_scrolled_up = false;
  let dragging = prop($$props, "dragging", 12, false);
  let uploading = mutable_source(false);
  let oldValue = mutable_source(value()?.text ?? "");
  let recording = false;
  let mic_audio = mutable_source(null);
  let full_container = mutable_source();
  const dispatch = createEventDispatcher();
  beforeUpdate(() => {
    can_scroll = get(el) && get(el).offsetHeight + get(el).scrollTop > get(el).scrollHeight - 100;
  });
  const scroll = () => {
    if (can_scroll && autoscroll() && !user_has_scrolled_up) {
      get(el).scrollTo(0, get(el).scrollHeight);
    }
  };
  async function handle_change() {
    dispatch("change", value());
    if (!value_is_output()) {
      dispatch("input");
    }
  }
  onMount(() => {
    if (autofocus() && get(el) !== null) {
      get(el).focus();
    }
  });
  const after_update = () => {
    if (can_scroll && autoscroll()) {
      scroll();
    }
    if (autofocus() && get(el)) {
      get(el).focus();
    }
  };
  afterUpdate(after_update);
  function handle_select(event2) {
    const target = event2.target;
    const text2 = target.value;
    const index2 = [target.selectionStart, target.selectionEnd];
    dispatch("select", { value: text2.substring(...index2), index: index2 });
  }
  async function handle_keypress(e) {
    if (e.key === "Enter" && e.shiftKey && lines() > 1) {
      e.preventDefault();
      await tick();
      dispatch("submit");
    } else if (e.key === "Enter" && !e.shiftKey && lines() === 1 && max_lines() >= 1) {
      e.preventDefault();
      await tick();
      dispatch("submit");
      active_source(null);
      add_mic_audio_to_files();
    }
  }
  function handle_scroll(event2) {
    const target = event2.target;
    const current_scroll_top = target.scrollTop;
    if (current_scroll_top < previous_scroll_top) {
      user_has_scrolled_up = true;
    }
    previous_scroll_top = current_scroll_top;
    const max_scroll_top = target.scrollHeight - target.clientHeight;
    const user_has_scrolled_to_bottom = current_scroll_top >= max_scroll_top;
    if (user_has_scrolled_to_bottom) {
      user_has_scrolled_up = false;
    }
  }
  async function handle_upload({ detail }) {
    handle_change();
    if (Array.isArray(detail)) {
      for (let file of detail) {
        value().files.push(file);
      }
      value(value());
    } else {
      value().files.push(detail);
      value(value());
    }
    await tick();
    dispatch("change", value());
    dispatch("upload", detail);
  }
  function remove_thumbnail(event2, index2) {
    handle_change();
    event2.stopPropagation();
    value().files.splice(index2, 1);
    value(value());
  }
  function handle_upload_click() {
    get(upload_component).open_upload();
  }
  function handle_stop() {
    dispatch("stop");
  }
  function add_mic_audio_to_files() {
    if (get(mic_audio)) {
      value().files.push(get(mic_audio));
      value(value());
      set(mic_audio, null);
    }
  }
  function handle_submit() {
    dispatch("submit");
    active_source(null);
    add_mic_audio_to_files();
  }
  async function handle_paste(event2) {
    if (!event2.clipboardData) return;
    const items = event2.clipboardData.items;
    const text2 = event2.clipboardData.getData("text");
    if (text2 && text2.length > max_plain_text_length()) {
      event2.preventDefault();
      const file = new window.File([text2], "pasted_text.txt", { type: "text/plain", lastModified: Date.now() });
      if (get(upload_component)) {
        get(upload_component).load_files([file]);
      }
      return;
    }
    for (let index2 in items) {
      const item = items[index2];
      if (item.kind === "file" && item.type.includes("image")) {
        const blob = item.getAsFile();
        if (blob) get(upload_component).load_files([blob]);
      }
    }
  }
  function handle_dragenter(event2) {
    event2.preventDefault();
    dragging(true);
  }
  function handle_dragleave(event2) {
    event2.preventDefault();
    const rect = get(full_container).getBoundingClientRect();
    const { clientX, clientY } = event2;
    if (clientX <= rect.left || clientX >= rect.right || clientY <= rect.top || clientY >= rect.bottom) {
      dragging(false);
    }
  }
  function handle_drop(event2) {
    event2.preventDefault();
    dragging(false);
    if (event2.dataTransfer && event2.dataTransfer.files) {
      const files = Array.from(event2.dataTransfer.files);
      if (get(file_types)) {
        const valid_files = files.filter((file) => {
          return get(file_types).some((type) => {
            if (type.startsWith(".")) {
              return file.name.toLowerCase().endsWith(type.toLowerCase());
            }
            return file.type.match(new RegExp(type.replace("*", ".*")));
          });
        });
        const invalid_files = files.length - valid_files.length;
        if (invalid_files > 0) {
          dispatch("error", `${invalid_files} file(s) were rejected. Accepted formats: ${get(file_types).join(", ")}`);
        }
        if (valid_files.length > 0) {
          get(upload_component).load_files(valid_files);
        }
      } else {
        get(upload_component).load_files(files);
      }
    }
  }
  legacy_pre_effect(() => deep_read_state(sources_string()), () => {
    set(sources, sources_string().split(",").map((s) => s.trim()).filter((s) => s === "upload" || s === "microphone"));
  });
  legacy_pre_effect(() => deep_read_state(file_types_string()), () => {
    set(file_types, file_types_string() ? file_types_string().split(",").map((s) => s.trim()) : null);
  });
  legacy_pre_effect(() => deep_read_state(dragging()), () => {
    dispatch("drag", dragging());
  });
  legacy_pre_effect(() => deep_read_state(value()), () => {
    if (value() === null) value({ text: "", files: [] });
  });
  legacy_pre_effect(
    () => (get(sources), deep_read_state(file_count()), deep_read_state(value())),
    () => {
      set(show_upload, get(sources) && get(sources).includes("upload") && !(file_count() === "single" && value().files.length > 0));
    }
  );
  legacy_pre_effect(() => (get(oldValue), deep_read_state(value())), () => {
    if (get(oldValue) !== value().text) {
      dispatch("change", value());
      set(oldValue, value().text);
    }
  });
  legacy_pre_effect(
    () => (deep_read_state(value()), get(el), deep_read_state(lines()), deep_read_state(max_lines()), resize),
    () => {
      value(), get(el) && lines() !== max_lines() && resize(get(el), lines(), max_lines());
    }
  );
  legacy_pre_effect_reset();
  init();
  var div = root_1$1();
  let classes;
  var node = child(div);
  BlockTitle(node, {
    get show_label() {
      return show_label();
    },
    get info() {
      return info();
    },
    get rtl() {
      return rtl();
    },
    children: ($$anchor2, $$slotProps) => {
      next();
      var text_1 = text();
      template_effect(() => set_text(text_1, label()));
      append($$anchor2, text_1);
    },
    $$slots: { default: true }
  });
  var div_1 = sibling(node, 2);
  var node_1 = child(div_1);
  {
    var consequent = ($$anchor2) => {
      InteractiveAudio($$anchor2, {
        sources: ["microphone"],
        class_name: "compact-audio",
        recording,
        get waveform_settings() {
          return waveform_settings();
        },
        get waveform_options() {
          return waveform_options();
        },
        get i18n() {
          return i18n();
        },
        get active_source() {
          return active_source();
        },
        get upload() {
          return upload();
        },
        get stream_handler() {
          return stream_handler();
        },
        stream_every: 1,
        editable: true,
        get label() {
          return label();
        },
        get root() {
          return root2();
        },
        loop: false,
        show_label: false,
        buttons: [],
        dragging: false,
        $$events: {
          change: ({ detail }) => {
            if (detail !== null) {
              set(mic_audio, detail);
            }
          },
          clear: () => {
            active_source(null);
          },
          start_recording: () => dispatch("start_recording"),
          pause_recording: () => dispatch("pause_recording"),
          stop_recording: () => dispatch("stop_recording")
        }
      });
    };
    if_block(node_1, ($$render) => {
      if (get(sources), deep_read_state(active_source()), untrack(() => get(sources) && get(sources).includes("microphone") && active_source() === "microphone")) $$render(consequent);
    });
  }
  var node_2 = sibling(node_1, 2);
  {
    var consequent_1 = ($$anchor2) => {
      bind_this(
        Upload($$anchor2, {
          get file_count() {
            return file_count();
          },
          get filetype() {
            return get(file_types);
          },
          get root() {
            return root2();
          },
          get max_file_size() {
            return max_file_size();
          },
          show_progress: false,
          disable_click: true,
          hidden: true,
          get upload() {
            return upload();
          },
          get stream_handler() {
            return stream_handler();
          },
          get upload_promise() {
            return upload_promise();
          },
          set upload_promise($$value) {
            upload_promise($$value);
          },
          get dragging() {
            return dragging();
          },
          set dragging($$value) {
            dragging($$value);
          },
          get uploading() {
            return get(uploading);
          },
          set uploading($$value) {
            set(uploading, $$value);
          },
          $$events: {
            load: handle_upload,
            error($$arg) {
              bubble_event.call(this, $$props, $$arg);
            }
          },
          $$legacy: true
        }),
        ($$value) => set(upload_component, $$value),
        () => get(upload_component)
      );
    };
    if_block(node_2, ($$render) => {
      if (get(show_upload)) $$render(consequent_1);
    });
  }
  var div_2 = sibling(node_2, 2);
  let classes_1;
  var node_3 = child(div_2);
  {
    var consequent_7 = ($$anchor2) => {
      var div_3 = root_5();
      var node_4 = child(div_3);
      {
        var consequent_2 = ($$anchor3) => {
          var button = root_6();
          var node_5 = child(button);
          Paperclip(node_5);
          reset(button);
          template_effect(() => button.disabled = disabled());
          event("click", button, handle_upload_click);
          append($$anchor3, button);
        };
        if_block(node_4, ($$render) => {
          if (get(show_upload)) $$render(consequent_2);
        });
      }
      var node_6 = sibling(node_4, 2);
      each(node_6, 1, () => (deep_read_state(value()), untrack(() => value().files)), index, ($$anchor3, file, index2) => {
        var span = root_7();
        var div_4 = child(span);
        var node_7 = child(div_4);
        {
          var consequent_3 = ($$anchor4) => {
            Image($$anchor4, {
              get src() {
                return get(file), untrack(() => get(file).url);
              },
              restProps: {
                title: null,
                alt: "",
                loading: "lazy",
                class: "thumbnail-image"
              }
            });
          };
          var alternate_2 = ($$anchor4) => {
            var fragment_4 = comment();
            var node_8 = first_child(fragment_4);
            {
              var consequent_4 = ($$anchor5) => {
                Music($$anchor5);
              };
              var alternate_1 = ($$anchor5) => {
                var fragment_6 = comment();
                var node_9 = first_child(fragment_6);
                {
                  var consequent_5 = ($$anchor6) => {
                    Video($$anchor6);
                  };
                  var alternate = ($$anchor6) => {
                    File($$anchor6);
                  };
                  if_block(
                    node_9,
                    ($$render) => {
                      if (get(file), untrack(() => get(file).mime_type && get(file).mime_type.includes("video"))) $$render(consequent_5);
                      else $$render(alternate, false);
                    },
                    true
                  );
                }
                append($$anchor5, fragment_6);
              };
              if_block(
                node_8,
                ($$render) => {
                  if (get(file), untrack(() => get(file).mime_type && get(file).mime_type.includes("audio"))) $$render(consequent_4);
                  else $$render(alternate_1, false);
                },
                true
              );
            }
            append($$anchor4, fragment_4);
          };
          if_block(node_7, ($$render) => {
            if (get(file), untrack(() => get(file).mime_type && get(file).mime_type.includes("image"))) $$render(consequent_3);
            else $$render(alternate_2, false);
          });
        }
        var button_1 = sibling(node_7, 2);
        var node_10 = child(button_1);
        Clear(node_10);
        reset(button_1);
        reset(div_4);
        reset(span);
        event("click", button_1, (event2) => remove_thumbnail(event2, index2));
        append($$anchor3, span);
      });
      var node_11 = sibling(node_6, 2);
      {
        var consequent_6 = ($$anchor3) => {
          var div_5 = root_14();
          append($$anchor3, div_5);
        };
        if_block(node_11, ($$render) => {
          if (get(uploading)) $$render(consequent_6);
        });
      }
      reset(div_3);
      append($$anchor2, div_3);
    };
    if_block(node_3, ($$render) => {
      if (deep_read_state(value()), get(uploading), get(show_upload), untrack(() => value().files.length > 0 || get(uploading) || get(show_upload))) $$render(consequent_7);
    });
  }
  var div_6 = sibling(node_3, 2);
  var textarea = child(div_6);
  remove_textarea_child(textarea);
  let classes_2;
  action(textarea, ($$node, $$action_arg) => text_area_resize?.($$node, $$action_arg), () => ({ text: value().text, lines: lines(), max_lines: max_lines() }));
  effect(() => bind_value(textarea, () => value().text, ($$value) => value(value().text = $$value, true)));
  bind_this(textarea, ($$value) => set(el, $$value), () => get(el));
  effect(() => event("keypress", textarea, handle_keypress));
  effect(() => event("blur", textarea, function($$arg) {
    bubble_event.call(this, $$props, $$arg);
  }));
  effect(() => event("select", textarea, handle_select));
  effect(() => event("focus", textarea, function($$arg) {
    bubble_event.call(this, $$props, $$arg);
  }));
  effect(() => event("scroll", textarea, handle_scroll));
  effect(() => event("paste", textarea, handle_paste));
  var node_12 = sibling(textarea, 2);
  {
    var consequent_8 = ($$anchor2) => {
      var button_2 = root_15();
      set_class(button_2, 1, "microphone-button svelte-1qn0337", null, {}, { recording });
      var node_13 = child(button_2);
      Microphone(node_13);
      reset(button_2);
      template_effect(() => button_2.disabled = disabled());
      event("click", button_2, () => {
        active_source(active_source() !== "microphone" ? "microphone" : null);
      });
      append($$anchor2, button_2);
    };
    if_block(node_12, ($$render) => {
      if (get(sources), untrack(() => get(sources) && get(sources).includes("microphone"))) $$render(consequent_8);
    });
  }
  var node_14 = sibling(node_12, 2);
  {
    var consequent_10 = ($$anchor2) => {
      var button_3 = root_16();
      let classes_3;
      var node_15 = child(button_3);
      {
        var consequent_9 = ($$anchor3) => {
          ArrowUp($$anchor3);
        };
        var alternate_3 = ($$anchor3) => {
          var text_2 = text();
          template_effect(() => set_text(text_2, submit_btn()));
          append($$anchor3, text_2);
        };
        if_block(node_15, ($$render) => {
          if (submit_btn() === true) $$render(consequent_9);
          else $$render(alternate_3, false);
        });
      }
      reset(button_3);
      template_effect(() => {
        classes_3 = set_class(button_3, 1, "submit-button svelte-1qn0337", null, classes_3, { "padded-button": submit_btn() !== true });
        button_3.disabled = disabled();
      });
      event("click", button_3, handle_submit);
      append($$anchor2, button_3);
    };
    if_block(node_14, ($$render) => {
      if (submit_btn()) $$render(consequent_10);
    });
  }
  var node_16 = sibling(node_14, 2);
  {
    var consequent_12 = ($$anchor2) => {
      var button_4 = root_19();
      let classes_4;
      var node_17 = child(button_4);
      {
        var consequent_11 = ($$anchor3) => {
          Square($$anchor3, { fill: "none", stroke_width: 2.5 });
        };
        var alternate_4 = ($$anchor3) => {
          var text_3 = text();
          template_effect(() => set_text(text_3, stop_btn()));
          append($$anchor3, text_3);
        };
        if_block(node_17, ($$render) => {
          if (stop_btn() === true) $$render(consequent_11);
          else $$render(alternate_4, false);
        });
      }
      reset(button_4);
      template_effect(() => classes_4 = set_class(button_4, 1, "stop-button svelte-1qn0337", null, classes_4, { "padded-button": stop_btn() !== true }));
      event("click", button_4, handle_stop);
      append($$anchor2, button_4);
    };
    if_block(node_16, ($$render) => {
      if (stop_btn()) $$render(consequent_12);
    });
  }
  reset(div_6);
  reset(div_2);
  reset(div_1);
  reset(div);
  bind_this(div, ($$value) => set(full_container, $$value), () => get(full_container));
  template_effect(() => {
    classes = set_class(div, 1, "full-container svelte-1qn0337", null, classes, { dragging: dragging() });
    classes_1 = set_class(div_2, 1, "input-wrapper svelte-1qn0337", null, classes_1, { "has-files": value().files.length > 0 || get(uploading) });
    set_attribute(textarea, "dir", rtl() ? "rtl" : "ltr");
    set_attribute(textarea, "placeholder", placeholder());
    set_attribute(textarea, "rows", lines());
    textarea.disabled = disabled();
    set_style(textarea, text_align() ? "text-align: " + text_align() : "");
    set_attribute(textarea, "autocapitalize", (deep_read_state(html_attributes()), untrack(() => html_attributes()?.autocapitalize)));
    set_attribute(textarea, "autocorrect", (deep_read_state(html_attributes()), untrack(() => html_attributes()?.autocorrect)));
    set_attribute(textarea, "spellcheck", (deep_read_state(html_attributes()), untrack(() => html_attributes()?.spellcheck)));
    set_attribute(textarea, "autocomplete", (deep_read_state(html_attributes()), untrack(() => html_attributes()?.autocomplete)));
    set_attribute(textarea, "tabindex", (deep_read_state(html_attributes()), untrack(() => html_attributes()?.tabindex)));
    set_attribute(textarea, "enterkeyhint", (deep_read_state(html_attributes()), untrack(() => html_attributes()?.enterkeyhint)));
    set_attribute(textarea, "lang", (deep_read_state(html_attributes()), untrack(() => html_attributes()?.lang)));
    classes_2 = set_class(textarea, 1, "svelte-1qn0337", null, classes_2, { "no-label": !show_label() });
    textarea.dir = textarea.dir;
  });
  event("dragenter", div, handle_dragenter);
  event("dragleave", div, handle_dragleave);
  event("dragover", div, preventDefault(function($$arg) {
    bubble_event.call(this, $$props, $$arg);
  }));
  event("drop", div, handle_drop);
  append($$anchor, div);
  pop();
}
var root_1 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let upload_promise = state(void 0);
  class MultimodalTextboxGradio extends Gradio {
    async get_data() {
      if (get(upload_promise)) {
        await get(upload_promise);
        await tick();
      }
      const data = await super.get_data();
      return data;
    }
  }
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new MultimodalTextboxGradio(props);
  const value = user_derived(() => gradio.props.value || { text: "", files: [] });
  let dragging;
  let active_source = null;
  let color_accent = "darkorange";
  const waveform_settings = {
    height: 50,
    barWidth: 2,
    barGap: 3,
    cursorWidth: 2,
    cursorColor: "#ddd5e9",
    autoplay: false,
    barRadius: 10,
    dragToSeek: true,
    normalize: true,
    minPxPerSec: 20,
    waveColor: "",
    progressColor: "",
    mediaControls: false,
    sampleRate: 44100
  };
  onMount(() => {
    color_accent = getComputedStyle(document?.documentElement).getPropertyValue("--color-accent");
    set_trim_region_colour();
    waveform_settings.waveColor = gradio.props?.waveform_options?.waveform_color || "#9ca3af";
    waveform_settings.progressColor = gradio.props?.waveform_options?.waveform_progress_color || color_accent;
    waveform_settings.mediaControls = gradio.props?.waveform_options?.show_controls;
    waveform_settings.sampleRate = gradio.props?.waveform_options?.sample_rate || 44100;
  });
  const trim_region_settings = {
    color: gradio.props?.waveform_options?.trim_region_color
  };
  function set_trim_region_colour() {
    document.documentElement.style.setProperty("--trim-region-color", trim_region_settings.color || color_accent);
  }
  const upload_fn = (...args) => gradio.shared.client.upload(...args);
  const i18n = (s) => gradio.i18n(s);
  const stream_handler_fn = (...args) => gradio.shared.client.stream(...args);
  let sources_string = user_derived(() => gradio.props.sources.join(","));
  let file_types_string = user_derived(() => (gradio.props.file_types || []).join(",") || null);
  {
    let $0 = user_derived(() => [...gradio.shared.elem_classes || [], "multimodal-textbox"]);
    let $1 = user_derived(() => dragging ? "focus" : "base");
    Block($$anchor, {
      get visible() {
        return gradio.shared.visible;
      },
      get elem_id() {
        return gradio.shared.elem_id;
      },
      get elem_classes() {
        return get($0);
      },
      get scale() {
        return gradio.shared.scale;
      },
      get min_width() {
        return gradio.shared.min_width;
      },
      allow_overflow: false,
      padding: false,
      get border_mode() {
        return get($1);
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
          let $02 = user_derived(() => gradio.shared.label || "MultimodalTextbox");
          let $12 = user_derived(() => !gradio.props.max_lines ? gradio.props.lines + 1 : gradio.props.max_lines);
          let $2 = user_derived(() => !gradio.shared.interactive);
          MultimodalTextbox(node_1, {
            get value() {
              return get(value);
            },
            value_is_output: true,
            get file_types_string() {
              return get(file_types_string);
            },
            get root() {
              return gradio.shared.root;
            },
            get label() {
              return get($02);
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
            get rtl() {
              return gradio.props.rtl;
            },
            get text_align() {
              return gradio.props.text_align;
            },
            get waveform_settings() {
              return waveform_settings;
            },
            i18n,
            get max_lines() {
              return get($12);
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
            get autofocus() {
              return gradio.props.autofocus;
            },
            get autoscroll() {
              return gradio.shared.autoscroll;
            },
            get file_count() {
              return gradio.props.file_count;
            },
            get sources_string() {
              return get(sources_string);
            },
            get max_file_size() {
              return gradio.shared.max_file_size;
            },
            get disabled() {
              return get($2);
            },
            upload: upload_fn,
            stream_handler: stream_handler_fn,
            get max_plain_text_length() {
              return gradio.props.max_plain_text_length;
            },
            get html_attributes() {
              return gradio.props.html_attributes;
            },
            get upload_promise() {
              return get(upload_promise);
            },
            set upload_promise($$value) {
              set(upload_promise, $$value, true);
            },
            get dragging() {
              return dragging;
            },
            set dragging($$value) {
              dragging = $$value;
            },
            get active_source() {
              return active_source;
            },
            set active_source($$value) {
              active_source = $$value;
            },
            $$events: {
              change: (e) => (gradio.props.value = e.detail, gradio.dispatch("change", gradio.props.value)),
              input: () => gradio.dispatch("input"),
              submit: () => gradio.dispatch("submit"),
              stop: () => gradio.dispatch("stop"),
              blur: () => gradio.dispatch("blur"),
              select: (e) => gradio.dispatch("select", e.detail),
              focus: () => gradio.dispatch("focus"),
              error: ({ detail }) => {
                gradio.dispatch("error", detail);
              },
              start_recording: () => gradio.dispatch("start_recording"),
              pause_recording: () => gradio.dispatch("pause_recording"),
              stop_recording: () => gradio.dispatch("stop_recording"),
              upload: (e) => gradio.dispatch("upload", e.detail),
              clear: () => gradio.dispatch("clear")
            }
          });
        }
        append($$anchor2, fragment_1);
      },
      $$slots: { default: true }
    });
  }
  pop();
}
export {
  default2 as BaseExample,
  MultimodalTextbox as BaseMultimodalTextbox,
  Index as default
};
//# sourceMappingURL=DY9yRh0K.js.map
