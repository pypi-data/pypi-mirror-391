import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, i as legacy_pre_effect, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, v as first_child, k as get, x as derived_safe_equal, s as sibling, b as append, o as pop, y as untrack } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { i as init } from "./DB0xzveP.js";
import { I as IconButtonWrapper, b as IconButton, c as bubble_event, u as uploadToHuggingFace } from "./DXi4jxVF.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { D as DownloadLink } from "./BFO3TfnI.js";
import { E as Empty } from "./B-xg5Dhl.js";
import { S as ShareButton } from "./D6EAw2Po.js";
import { D as Download } from "./rkplYKOt.js";
import { M as Music } from "./Dr2P5Z1a.js";
import { A as AudioPlayer } from "./CxZmGzlA.js";
var root_2 = from_html(`<!> <!>`, 1);
var root_1 = from_html(`<!> <!>`, 1);
var root = from_html(`<!> <!>`, 1);
function StaticAudio($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8, null);
  let subtitles = prop($$props, "subtitles", 8, null);
  let label = prop($$props, "label", 8);
  let show_label = prop($$props, "show_label", 8, true);
  let buttons = prop($$props, "buttons", 8, null);
  let i18n = prop($$props, "i18n", 8);
  let waveform_settings = prop($$props, "waveform_settings", 24, () => ({}));
  let waveform_options = prop($$props, "waveform_options", 24, () => ({ show_recording_waveform: true }));
  let editable = prop($$props, "editable", 8, true);
  let loop = prop($$props, "loop", 8);
  let display_icon_button_wrapper_top_corner = prop($$props, "display_icon_button_wrapper_top_corner", 8, false);
  const dispatch = createEventDispatcher();
  legacy_pre_effect(() => deep_read_state(value()), () => {
    value() && dispatch("change", value());
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => (deep_read_state(label()), deep_read_state(i18n()), untrack(() => label() || i18n()("audio.audio"))));
    BlockLabel(node, {
      get show_label() {
        return show_label();
      },
      get Icon() {
        return Music;
      },
      float: false,
      get label() {
        return get($0);
      }
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent_2 = ($$anchor2) => {
      var fragment_1 = root_1();
      var node_2 = first_child(fragment_1);
      IconButtonWrapper(node_2, {
        get display_top_corner() {
          return display_icon_button_wrapper_top_corner();
        },
        children: ($$anchor3, $$slotProps) => {
          var fragment_2 = root_2();
          var node_3 = first_child(fragment_2);
          {
            var consequent = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value().is_stream ? value().url?.replace("playlist.m3u8", "playlist-file") : value().url)));
                let $1 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value().orig_name || value().path)));
                DownloadLink($$anchor4, {
                  get href() {
                    return get($0);
                  },
                  get download() {
                    return get($1);
                  },
                  children: ($$anchor5, $$slotProps2) => {
                    {
                      let $02 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.download"))));
                      IconButton($$anchor5, {
                        get Icon() {
                          return Download;
                        },
                        get label() {
                          return get($02);
                        }
                      });
                    }
                  },
                  $$slots: { default: true }
                });
              }
            };
            if_block(node_3, ($$render) => {
              if (deep_read_state(buttons()), untrack(() => buttons() === null ? true : buttons().includes("download"))) $$render(consequent);
            });
          }
          var node_4 = sibling(node_3, 2);
          {
            var consequent_1 = ($$anchor4) => {
              ShareButton($$anchor4, {
                get i18n() {
                  return i18n();
                },
                formatter: async (value2) => {
                  if (!value2) return "";
                  let url = await uploadToHuggingFace(value2.url);
                  return `<audio controls src="${url}"></audio>`;
                },
                get value() {
                  return value();
                },
                $$events: {
                  error($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  share($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  }
                }
              });
            };
            if_block(node_4, ($$render) => {
              if (deep_read_state(buttons()), untrack(() => buttons() === null ? true : buttons().includes("share"))) $$render(consequent_1);
            });
          }
          append($$anchor3, fragment_2);
        },
        $$slots: { default: true }
      });
      var node_5 = sibling(node_2, 2);
      {
        let $0 = derived_safe_equal(() => (deep_read_state(subtitles()), untrack(() => Array.isArray(subtitles()) ? subtitles() : subtitles()?.url)));
        AudioPlayer(node_5, {
          get value() {
            return value();
          },
          get subtitles() {
            return get($0);
          },
          get label() {
            return label();
          },
          get i18n() {
            return i18n();
          },
          get waveform_settings() {
            return waveform_settings();
          },
          get waveform_options() {
            return waveform_options();
          },
          get editable() {
            return editable();
          },
          get loop() {
            return loop();
          },
          $$events: {
            pause($$arg) {
              bubble_event.call(this, $$props, $$arg);
            },
            play($$arg) {
              bubble_event.call(this, $$props, $$arg);
            },
            stop($$arg) {
              bubble_event.call(this, $$props, $$arg);
            },
            load($$arg) {
              bubble_event.call(this, $$props, $$arg);
            }
          }
        });
      }
      append($$anchor2, fragment_1);
    };
    var alternate = ($$anchor2) => {
      Empty($$anchor2, {
        size: "small",
        children: ($$anchor3, $$slotProps) => {
          Music($$anchor3);
        },
        $$slots: { default: true }
      });
    };
    if_block(node_1, ($$render) => {
      if (value() !== null) $$render(consequent_2);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  StaticAudio as default
};
//# sourceMappingURL=CgFyFGmP.js.map
