import "./9B4_veAf.js";
import { p as push, J as state, L as proxy, M as user_effect, k as get, j as set, I as onMount, D as comment, v as first_child, b as append, o as pop, K as tick, c as from_html, s as sibling, A as user_derived } from "./DEzry6cj.js";
import { r as rest_props, i as if_block, s as spread_props } from "./DUftb7my.js";
import { G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import StaticAudio from "./CgFyFGmP.js";
import { I as InteractiveAudio } from "./D2gsMg7z.js";
import { U as UploadText } from "./B8mIV0gF.js";
import { A } from "./CxZmGzlA.js";
import { default as default2 } from "./B2jjYC2n.js";
var root_2 = from_html(`<!> <!>`, 1);
var root_4 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  let upload_promise = state(void 0);
  $$props.props.stream_every = 0.1;
  class AudioGradio extends Gradio {
    async get_data() {
      if (get(upload_promise)) {
        await get(upload_promise);
        await tick();
      }
      const data = await super.get_data();
      return data;
    }
  }
  const gradio = new AudioGradio(props);
  let label = user_derived(() => gradio.shared.label || gradio.i18n("audio.audio"));
  let active_source = user_derived(() => gradio.props.sources ? gradio.props.sources[0] : null);
  let initial_value = gradio.props.value;
  const handle_reset_value = () => {
    if (initial_value === null || gradio.props.value === initial_value) {
      return;
    }
    gradio.props.value = initial_value;
  };
  let dragging;
  let color_accent = "darkorange";
  let waveform_settings = user_derived(() => ({
    height: 50,
    barWidth: 2,
    barGap: 3,
    cursorWidth: 2,
    cursorColor: "#ddd5e9",
    autoplay: gradio.props.autoplay,
    barRadius: 10,
    dragToSeek: true,
    normalize: true,
    minPxPerSec: 20
  }));
  const trim_region_settings = {
    color: gradio.props.waveform_options.trim_region_color,
    drag: true,
    resize: true
  };
  function set_trim_region_colour() {
    document.documentElement.style.setProperty("--trim-region-color", trim_region_settings.color || color_accent);
  }
  function handle_error({ detail }) {
    const [level, status] = detail.includes("Invalid file type") ? ["warning", "complete"] : ["error", "error"];
    if (gradio.shared.loading_status) {
      gradio.shared.loading_status.status = status;
      gradio.shared.loading_status.message = detail;
    }
    gradio.dispatch(level, detail);
  }
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  onMount(() => {
    color_accent = getComputedStyle(document?.documentElement).getPropertyValue("--color-accent");
    set_trim_region_colour();
    get(waveform_settings).waveColor = gradio.props.waveform_options.waveform_color || "#9ca3af";
    get(waveform_settings).progressColor = gradio.props.waveform_options.waveform_progress_color || color_accent;
    get(waveform_settings).mediaControls = gradio.props.waveform_options.show_controls;
    get(waveform_settings).sampleRate = gradio.props.waveform_options.sample_rate || 44100;
  });
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      {
        let $0 = user_derived(() => dragging ? "focus" : "base");
        Block($$anchor2, {
          variant: "solid",
          get border_mode() {
            return get($0);
          },
          padding: false,
          allow_overflow: false,
          get elem_id() {
            return gradio.shared.elem_id;
          },
          get elem_classes() {
            return gradio.shared.elem_classes;
          },
          get visible() {
            return gradio.shared.visible;
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
          children: ($$anchor3, $$slotProps) => {
            var fragment_2 = root_2();
            var node_1 = first_child(fragment_2);
            Static(node_1, spread_props(
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
            var node_2 = sibling(node_1, 2);
            {
              let $02 = user_derived(() => gradio.props.buttons ?? ["download", "share"]);
              StaticAudio(node_2, {
                get i18n() {
                  return gradio.i18n;
                },
                get show_label() {
                  return gradio.shared.show_label;
                },
                get buttons() {
                  return get($02);
                },
                get value() {
                  return gradio.props.value;
                },
                get subtitles() {
                  return gradio.props.subtitles;
                },
                get label() {
                  return get(label);
                },
                get loop() {
                  return gradio.props.loop;
                },
                get waveform_settings() {
                  return get(waveform_settings);
                },
                get waveform_options() {
                  return gradio.props.waveform_options;
                },
                get editable() {
                  return gradio.props.editable;
                },
                $$events: {
                  share: (e) => gradio.dispatch("share", e.detail),
                  error: (e) => gradio.dispatch("error", e.detail),
                  play: () => gradio.dispatch("play"),
                  pause: () => gradio.dispatch("pause"),
                  stop: () => gradio.dispatch("stop")
                }
              });
            }
            append($$anchor3, fragment_2);
          },
          $$slots: { default: true }
        });
      }
    };
    var alternate = ($$anchor2) => {
      {
        let $0 = user_derived(() => gradio.props.value === null && get(active_source) === "upload" ? "dashed" : "solid");
        let $1 = user_derived(() => dragging ? "focus" : "base");
        Block($$anchor2, {
          get variant() {
            return get($0);
          },
          get border_mode() {
            return get($1);
          },
          padding: false,
          allow_overflow: false,
          get elem_id() {
            return gradio.shared.elem_id;
          },
          get elem_classes() {
            return gradio.shared.elem_classes;
          },
          get visible() {
            return gradio.shared.visible;
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
          children: ($$anchor3, $$slotProps) => {
            var fragment_4 = root_4();
            var node_3 = first_child(fragment_4);
            Static(node_3, spread_props(
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
            var node_4 = sibling(node_3, 2);
            {
              let $02 = user_derived(() => gradio.props.buttons ?? []);
              InteractiveAudio(node_4, {
                get label() {
                  return get(label);
                },
                get show_label() {
                  return gradio.shared.show_label;
                },
                get buttons() {
                  return get($02);
                },
                get value() {
                  return gradio.props.value;
                },
                get subtitles() {
                  return gradio.props.subtitles;
                },
                get root() {
                  return gradio.shared.root;
                },
                get sources() {
                  return gradio.props.sources;
                },
                get active_source() {
                  return get(active_source);
                },
                get pending() {
                  return gradio.shared.loading_status.pending;
                },
                get streaming() {
                  return gradio.props.streaming;
                },
                get loop() {
                  return gradio.props.loop;
                },
                get max_file_size() {
                  return gradio.shared.max_file_size;
                },
                handle_reset_value,
                get editable() {
                  return gradio.props.editable;
                },
                get i18n() {
                  return gradio.i18n;
                },
                get waveform_settings() {
                  return get(waveform_settings);
                },
                get waveform_options() {
                  return gradio.props.waveform_options;
                },
                get trim_region_settings() {
                  return trim_region_settings;
                },
                get stream_every() {
                  return gradio.props.stream_every;
                },
                get stream_state() {
                  return gradio.shared.loading_status.stream_state;
                },
                upload: (...args) => gradio.shared.client.upload(...args),
                stream_handler: (...args) => gradio.shared.client.stream(...args),
                get time_limit() {
                  return gradio.shared.loading_status.time_limit;
                },
                get upload_promise() {
                  return get(upload_promise);
                },
                set upload_promise($$value) {
                  set(upload_promise, $$value, true);
                },
                get initial_value() {
                  return initial_value;
                },
                set initial_value($$value) {
                  initial_value = $$value;
                },
                get recording() {
                  return gradio.props.recording;
                },
                set recording($$value) {
                  gradio.props.recording = $$value;
                },
                get dragging() {
                  return dragging;
                },
                set dragging($$value) {
                  dragging = $$value;
                },
                $$events: {
                  change: ({ detail }) => gradio.props.value = detail,
                  stream: ({ detail }) => {
                    gradio.props.value = detail;
                    gradio.dispatch("stream", gradio.props.value);
                  },
                  drag: ({ detail }) => dragging = detail,
                  edit: () => gradio.dispatch("edit"),
                  play: () => gradio.dispatch("play"),
                  pause: () => gradio.dispatch("pause"),
                  stop: () => gradio.dispatch("stop"),
                  start_recording: () => gradio.dispatch("start_recording"),
                  pause_recording: () => gradio.dispatch("pause_recording"),
                  stop_recording: (e) => {
                    gradio.dispatch("stop_recording");
                    gradio.dispatch("input");
                  },
                  upload: () => {
                    gradio.dispatch("upload");
                    gradio.dispatch("input");
                  },
                  clear: () => {
                    gradio.dispatch("clear");
                    gradio.dispatch("input");
                  },
                  error: handle_error,
                  close_stream: () => gradio.dispatch("close_stream", "stream")
                },
                children: ($$anchor4, $$slotProps2) => {
                  UploadText($$anchor4, {
                    get i18n() {
                      return gradio.i18n;
                    },
                    type: "audio"
                  });
                },
                $$slots: { default: true }
              });
            }
            append($$anchor3, fragment_4);
          },
          $$slots: { default: true }
        });
      }
    };
    if_block(node, ($$render) => {
      if (!gradio.shared.interactive) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  default2 as BaseExample,
  InteractiveAudio as BaseInteractiveAudio,
  A as BasePlayer,
  StaticAudio as BaseStaticAudio,
  Index as default
};
//# sourceMappingURL=Bsw8xLNO.js.map
