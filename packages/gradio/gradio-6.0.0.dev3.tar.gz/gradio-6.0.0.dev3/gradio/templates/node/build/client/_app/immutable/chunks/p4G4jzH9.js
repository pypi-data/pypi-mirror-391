import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, i as legacy_pre_effect, k as get, m as mutable_source, n as legacy_pre_effect_reset, c as from_html, v as first_child, x as derived_safe_equal, s as sibling, d as child, u as deep_read_state, y as untrack, r as reset, b as append, o as pop, D as comment, j as set, t as template_effect, g as set_text, J as state, L as proxy, M as user_effect, K as tick, A as user_derived } from "./DEzry6cj.js";
import { p as prop, i as if_block, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { k as key } from "./DssvUQ9s.js";
import { s as slot } from "./DX-MI-YE.js";
import { i as init } from "./DB0xzveP.js";
import { c as bubble_event, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import { U as Upload } from "./BcroWaqq.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { V as Video } from "./B7T4xKTK.js";
import { S as SelectSource } from "./jPEKutgU.js";
/* empty css         */
import { W as Webcam } from "./BTuysa41.js";
/* empty css         */
/* empty css         */
import { a as prettyBytes } from "./Br4zzvQm.js";
import { l, p } from "./Br4zzvQm.js";
import { P as Player, V as VideoPreview } from "./B1zO1a6i.js";
import { default as default2 } from "./C6ivXr8W.js";
import { U as UploadText } from "./B8mIV0gF.js";
var root_2$1 = from_html(`<div class="upload-container svelte-ey25pz"><!></div>`);
var root_11 = from_html(`<div class="file-name svelte-ey25pz"> </div> <div class="file-size svelte-ey25pz"> </div>`, 1);
var root_1 = from_html(`<!> <div data-testid="video" class="video-container svelte-ey25pz"><!> <!></div>`, 1);
function InteractiveVideo($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 12, null);
  let subtitle = prop($$props, "subtitle", 8, null);
  let sources = prop($$props, "sources", 24, () => ["webcam", "upload"]);
  let label = prop($$props, "label", 8, void 0);
  let show_download_button = prop($$props, "show_download_button", 8, false);
  let show_label = prop($$props, "show_label", 8, true);
  let webcam_options = prop($$props, "webcam_options", 8);
  let include_audio = prop($$props, "include_audio", 8);
  let autoplay = prop($$props, "autoplay", 8);
  let root = prop($$props, "root", 8);
  let i18n = prop($$props, "i18n", 8);
  let active_source = prop($$props, "active_source", 12, "webcam");
  let handle_reset_value = prop($$props, "handle_reset_value", 8, () => {
  });
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let upload = prop($$props, "upload", 8);
  let stream_handler = prop($$props, "stream_handler", 8);
  let loop = prop($$props, "loop", 8);
  let uploading = prop($$props, "uploading", 12, false);
  let upload_promise = prop($$props, "upload_promise", 12, null);
  let has_change_history = mutable_source(false);
  const dispatch = createEventDispatcher();
  function handle_load({ detail }) {
    value(detail);
    dispatch("change", detail);
    dispatch("upload", detail);
  }
  function handle_clear() {
    value(null);
    dispatch("change", null);
    dispatch("clear");
  }
  function handle_change(video) {
    set(has_change_history, true);
    dispatch("change", video);
  }
  function handle_capture({ detail }) {
    dispatch("change", detail);
  }
  let dragging = mutable_source(false);
  legacy_pre_effect(() => get(dragging), () => {
    dispatch("drag", get(dragging));
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root_1();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => label() || "Video");
    BlockLabel(node, {
      get show_label() {
        return show_label();
      },
      get Icon() {
        return Video;
      },
      get label() {
        return get($0);
      }
    });
  }
  var div = sibling(node, 2);
  var node_1 = child(div);
  {
    var consequent_2 = ($$anchor2) => {
      var div_1 = root_2$1();
      var node_2 = child(div_1);
      {
        var consequent = ($$anchor3) => {
          {
            let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("video.drop_to_upload"))));
            Upload($$anchor3, {
              filetype: "video/x-m4v,video/*",
              get max_file_size() {
                return max_file_size();
              },
              get root() {
                return root();
              },
              get upload() {
                return upload();
              },
              get stream_handler() {
                return stream_handler();
              },
              get aria_label() {
                return get($0);
              },
              get upload_promise() {
                return upload_promise();
              },
              set upload_promise($$value) {
                upload_promise($$value);
              },
              get dragging() {
                return get(dragging);
              },
              set dragging($$value) {
                set(dragging, $$value);
              },
              get uploading() {
                return uploading();
              },
              set uploading($$value) {
                uploading($$value);
              },
              $$events: {
                load: handle_load,
                error: ({ detail }) => dispatch("error", detail)
              },
              children: ($$anchor4, $$slotProps) => {
                var fragment_2 = comment();
                var node_3 = first_child(fragment_2);
                slot(node_3, $$props, "default", {}, null);
                append($$anchor4, fragment_2);
              },
              $$slots: { default: true },
              $$legacy: true
            });
          }
        };
        var alternate = ($$anchor3) => {
          var fragment_3 = comment();
          var node_4 = first_child(fragment_3);
          {
            var consequent_1 = ($$anchor4) => {
              Webcam($$anchor4, {
                get root() {
                  return root();
                },
                get mirror_webcam() {
                  return deep_read_state(webcam_options()), untrack(() => webcam_options().mirror);
                },
                get webcam_constraints() {
                  return deep_read_state(webcam_options()), untrack(() => webcam_options().constraints);
                },
                get include_audio() {
                  return include_audio();
                },
                mode: "video",
                get i18n() {
                  return i18n();
                },
                get upload() {
                  return upload();
                },
                stream_every: 1,
                $$events: {
                  error($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  capture: handle_capture,
                  start_recording($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  stop_recording($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  }
                }
              });
            };
            if_block(
              node_4,
              ($$render) => {
                if (active_source() === "webcam") $$render(consequent_1);
              },
              true
            );
          }
          append($$anchor3, fragment_3);
        };
        if_block(node_2, ($$render) => {
          if (active_source() === "upload") $$render(consequent);
          else $$render(alternate, false);
        });
      }
      reset(div_1);
      append($$anchor2, div_1);
    };
    var alternate_2 = ($$anchor2) => {
      var fragment_5 = comment();
      var node_5 = first_child(fragment_5);
      {
        var consequent_3 = ($$anchor3) => {
          var fragment_6 = comment();
          var node_6 = first_child(fragment_6);
          key(node_6, () => (deep_read_state(value()), untrack(() => value()?.url)), ($$anchor4) => {
            {
              let $0 = derived_safe_equal(() => (deep_read_state(subtitle()), untrack(() => subtitle()?.url)));
              let $1 = derived_safe_equal(() => (deep_read_state(webcam_options()), deep_read_state(active_source()), untrack(() => webcam_options().mirror && active_source() === "webcam")));
              Player($$anchor4, {
                get upload() {
                  return upload();
                },
                get root() {
                  return root();
                },
                interactive: true,
                get autoplay() {
                  return autoplay();
                },
                get src() {
                  return deep_read_state(value()), untrack(() => value().url);
                },
                get subtitle() {
                  return get($0);
                },
                is_stream: false,
                get mirror() {
                  return get($1);
                },
                get label() {
                  return label();
                },
                handle_change,
                get handle_reset_value() {
                  return handle_reset_value();
                },
                get loop() {
                  return loop();
                },
                get value() {
                  return value();
                },
                get i18n() {
                  return i18n();
                },
                get show_download_button() {
                  return show_download_button();
                },
                handle_clear,
                get has_change_history() {
                  return get(has_change_history);
                },
                $$events: {
                  play($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  pause($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  stop($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  end($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  error($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  }
                }
              });
            }
          });
          append($$anchor3, fragment_6);
        };
        var alternate_1 = ($$anchor3) => {
          var fragment_8 = comment();
          var node_7 = first_child(fragment_8);
          {
            var consequent_4 = ($$anchor4) => {
              var fragment_9 = root_11();
              var div_2 = first_child(fragment_9);
              var text = child(div_2, true);
              reset(div_2);
              var div_3 = sibling(div_2, 2);
              var text_1 = child(div_3, true);
              reset(div_3);
              template_effect(
                ($0) => {
                  set_text(text, (deep_read_state(value()), untrack(() => value().orig_name || value().url)));
                  set_text(text_1, $0);
                },
                [
                  () => (deep_read_state(prettyBytes), deep_read_state(value()), untrack(() => prettyBytes(value().size)))
                ]
              );
              append($$anchor4, fragment_9);
            };
            if_block(
              node_7,
              ($$render) => {
                if (deep_read_state(value()), untrack(() => value().size)) $$render(consequent_4);
              },
              true
            );
          }
          append($$anchor3, fragment_8);
        };
        if_block(
          node_5,
          ($$render) => {
            if (deep_read_state(value()), untrack(() => value()?.url)) $$render(consequent_3);
            else $$render(alternate_1, false);
          },
          true
        );
      }
      append($$anchor2, fragment_5);
    };
    if_block(node_1, ($$render) => {
      if (deep_read_state(value()), untrack(() => value() === null || value()?.url === void 0)) $$render(consequent_2);
      else $$render(alternate_2, false);
    });
  }
  var node_8 = sibling(node_1, 2);
  SelectSource(node_8, {
    get sources() {
      return sources();
    },
    handle_clear,
    get active_source() {
      return active_source();
    },
    set active_source($$value) {
      active_source($$value);
    },
    $$legacy: true
  });
  reset(div);
  append($$anchor, fragment);
  pop();
}
var root_2 = from_html(`<!> <!>`, 1);
var root_4 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  let upload_promise = state(void 0);
  class VideoGradio extends Gradio {
    async get_data() {
      if (get(upload_promise)) {
        await get(upload_promise);
        await tick();
      }
      const data = await super.get_data();
      return data;
    }
  }
  const gradio = new VideoGradio(props);
  let old_value = state(proxy(gradio.props.value));
  let uploading = state(false);
  let dragging = state(false);
  let active_source = user_derived(() => gradio.props.sources ? gradio.props.sources[0] : void 0);
  let initial_value = gradio.props.value;
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  const handle_reset_value = () => {
    if (initial_value === null || gradio.props.value === initial_value) {
      return;
    }
    gradio.props.value = initial_value;
  };
  function handle_change({ detail }) {
    if (detail != null) {
      gradio.props.value = detail;
    } else {
      gradio.props.value = null;
    }
  }
  function handle_error({ detail }) {
    const [level, status] = detail.includes("Invalid file type") ? ["warning", "complete"] : ["error", "error"];
    gradio.shared.loading_status.status = status;
    gradio.shared.loading_status.message = detail;
    gradio.dispatch(level, detail);
  }
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      {
        let $0 = user_derived(() => gradio.props.value === null && get(active_source) === "upload" ? "dashed" : "solid");
        let $1 = user_derived(() => get(dragging) ? "focus" : "base");
        let $2 = user_derived(() => gradio.props.height || void 0);
        Block($$anchor2, {
          get visible() {
            return gradio.shared.visible;
          },
          get variant() {
            return get($0);
          },
          get border_mode() {
            return get($1);
          },
          padding: false,
          get elem_id() {
            return gradio.shared.elem_id;
          },
          get elem_classes() {
            return gradio.shared.elem_classes;
          },
          get height() {
            return get($2);
          },
          get width() {
            return gradio.props.width;
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
          allow_overflow: false,
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
              let $02 = user_derived(() => (gradio.props.buttons || []).includes("share"));
              let $12 = user_derived(() => (gradio.props.buttons || ["download"]).includes("download"));
              VideoPreview(node_2, {
                get value() {
                  return gradio.props.value;
                },
                get subtitle() {
                  return gradio.props.subtitles;
                },
                get label() {
                  return gradio.shared.label;
                },
                get show_label() {
                  return gradio.shared.show_label;
                },
                get autoplay() {
                  return gradio.props.autoplay;
                },
                get loop() {
                  return gradio.props.loop;
                },
                get show_share_button() {
                  return get($02);
                },
                get show_download_button() {
                  return get($12);
                },
                get i18n() {
                  return gradio.i18n;
                },
                upload: (...args) => gradio.shared.client.upload(...args),
                $$events: {
                  play: () => gradio.dispatch("play"),
                  pause: () => gradio.dispatch("pause"),
                  stop: () => gradio.dispatch("stop"),
                  end: () => gradio.dispatch("end"),
                  share: ({ detail }) => gradio.dispatch("share", detail),
                  error: ({ detail }) => gradio.dispatch("error", detail)
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
        let $1 = user_derived(() => get(dragging) ? "focus" : "base");
        let $2 = user_derived(() => gradio.props.height || void 0);
        Block($$anchor2, {
          get visible() {
            return gradio.shared.visible;
          },
          get variant() {
            return get($0);
          },
          get border_mode() {
            return get($1);
          },
          padding: false,
          get elem_id() {
            return gradio.shared.elem_id;
          },
          get elem_classes() {
            return gradio.shared.elem_classes;
          },
          get height() {
            return get($2);
          },
          get width() {
            return gradio.props.width;
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
          allow_overflow: false,
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
              let $02 = user_derived(() => (gradio.props.buttons || []).includes("download"));
              InteractiveVideo(node_4, {
                get value() {
                  return gradio.props.value;
                },
                get subtitle() {
                  return gradio.props.subtitles;
                },
                get label() {
                  return gradio.shared.label;
                },
                get show_label() {
                  return gradio.shared.show_label;
                },
                get show_download_button() {
                  return get($02);
                },
                get sources() {
                  return gradio.props.sources;
                },
                get active_source() {
                  return get(active_source);
                },
                get webcam_options() {
                  return gradio.props.webcam_options;
                },
                get include_audio() {
                  return gradio.props.include_audio;
                },
                get autoplay() {
                  return gradio.props.autoplay;
                },
                get root() {
                  return gradio.shared.root;
                },
                get loop() {
                  return gradio.props.loop;
                },
                handle_reset_value,
                get i18n() {
                  return gradio.i18n;
                },
                get max_file_size() {
                  return gradio.shared.max_file_size;
                },
                upload: (...args) => gradio.shared.client.upload(...args),
                stream_handler: (...args) => gradio.shared.client.stream(...args),
                get upload_promise() {
                  return get(upload_promise);
                },
                set upload_promise($$value) {
                  set(upload_promise, $$value, true);
                },
                get uploading() {
                  return get(uploading);
                },
                set uploading($$value) {
                  set(uploading, $$value, true);
                },
                $$events: {
                  change: handle_change,
                  drag: ({ detail }) => set(dragging, detail, true),
                  error: handle_error,
                  clear: () => {
                    gradio.props.value = null;
                    gradio.dispatch("clear");
                  },
                  play: () => gradio.dispatch("play"),
                  pause: () => gradio.dispatch("pause"),
                  upload: () => gradio.dispatch("upload"),
                  stop: () => gradio.dispatch("stop"),
                  end: () => gradio.dispatch("end"),
                  start_recording: () => gradio.dispatch("start_recording"),
                  stop_recording: () => gradio.dispatch("stop_recording")
                },
                children: ($$anchor4, $$slotProps2) => {
                  UploadText($$anchor4, {
                    get i18n() {
                      return gradio.i18n;
                    },
                    type: "video"
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
  InteractiveVideo as BaseInteractiveVideo,
  Player as BasePlayer,
  VideoPreview as BaseStaticVideo,
  Index as default,
  l as loaded,
  p as playable,
  prettyBytes
};
//# sourceMappingURL=p4G4jzH9.js.map
