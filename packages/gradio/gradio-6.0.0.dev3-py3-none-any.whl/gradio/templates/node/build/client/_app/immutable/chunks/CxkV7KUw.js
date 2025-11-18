import "./9B4_veAf.js";
import { p as push, N as onDestroy, k as get, x as derived_safe_equal, o as pop, m as mutable_source, j as set, i as legacy_pre_effect, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, v as first_child, s as sibling, b as append, J as state, L as proxy, M as user_effect, A as user_derived } from "./DEzry6cj.js";
import { p as prop, r as rest_props, s as spread_props, i as if_block } from "./DUftb7my.js";
import { b as IconButton, H as Check, J as Copy, I as IconButtonWrapper, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { C as Code } from "./DDjZdhlS.js";
import { C as Code$1 } from "./cOBxa0vB.js";
import { i as init } from "./DB0xzveP.js";
import { D as Download } from "./rkplYKOt.js";
import { D as DownloadLink } from "./BFO3TfnI.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { E as Empty } from "./B-xg5Dhl.js";
import { default as default2 } from "./MgHZVtmx.js";
function Copy_1($$anchor, $$props) {
  push($$props, false);
  let copied = mutable_source(false);
  let value = prop($$props, "value", 8);
  let timer;
  function copy_feedback() {
    set(copied, true);
    if (timer) clearTimeout(timer);
    timer = setTimeout(
      () => {
        set(copied, false);
      },
      2e3
    );
  }
  async function handle_copy() {
    if ("clipboard" in navigator) {
      await navigator.clipboard.writeText(value());
      copy_feedback();
    }
  }
  onDestroy(() => {
    if (timer) clearTimeout(timer);
  });
  init();
  {
    let $0 = derived_safe_equal(() => get(copied) ? Check : Copy);
    IconButton($$anchor, {
      get Icon() {
        return get($0);
      },
      $$events: { click: handle_copy }
    });
  }
  pop();
}
function Download_1($$anchor, $$props) {
  push($$props, false);
  const ext = mutable_source();
  const download_value = mutable_source();
  let value = prop($$props, "value", 8);
  let language = prop($$props, "language", 8);
  function get_ext_for_type(type) {
    const exts = {
      py: "py",
      python: "py",
      md: "md",
      markdown: "md",
      json: "json",
      html: "html",
      css: "css",
      js: "js",
      javascript: "js",
      ts: "ts",
      typescript: "ts",
      yaml: "yaml",
      yml: "yml",
      dockerfile: "dockerfile",
      sh: "sh",
      shell: "sh",
      r: "r",
      c: "c",
      cpp: "cpp",
      latex: "tex"
    };
    return exts[type] || "txt";
  }
  let copied = mutable_source(false);
  let timer;
  function copy_feedback() {
    set(copied, true);
    if (timer) clearTimeout(timer);
    timer = setTimeout(
      () => {
        set(copied, false);
      },
      2e3
    );
  }
  onDestroy(() => {
    if (timer) clearTimeout(timer);
  });
  legacy_pre_effect(() => deep_read_state(language()), () => {
    set(ext, get_ext_for_type(language()));
  });
  legacy_pre_effect(() => deep_read_state(value()), () => {
    set(download_value, URL.createObjectURL(new Blob([value()])));
  });
  legacy_pre_effect_reset();
  init();
  DownloadLink($$anchor, {
    get download() {
      return `file.${get(ext) ?? ""}`;
    },
    get href() {
      return get(download_value);
    },
    $$events: { click: copy_feedback },
    children: ($$anchor2, $$slotProps) => {
      {
        let $0 = derived_safe_equal(() => get(copied) ? Check : Download);
        IconButton($$anchor2, {
          get Icon() {
            return get($0);
          }
        });
      }
    },
    $$slots: { default: true }
  });
  pop();
}
var root_1$1 = from_html(`<!> <!>`, 1);
function Widgets($$anchor, $$props) {
  let value = prop($$props, "value", 8);
  let language = prop($$props, "language", 8);
  IconButtonWrapper($$anchor, {
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1$1();
      var node = first_child(fragment_1);
      Download_1(node, {
        get value() {
          return value();
        },
        get language() {
          return language();
        }
      });
      var node_1 = sibling(node, 2);
      Copy_1(node_1, {
        get value() {
          return value();
        }
      });
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
}
var root_5 = from_html(`<!> <!>`, 1);
var root_1 = from_html(`<!> <!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let dark_mode = gradio.shared.theme === "dark";
  let label = user_derived(() => gradio.shared.label || gradio.i18n("code.code"));
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  {
    let $0 = user_derived(() => gradio.props.max_lines && "fit-content");
    Block($$anchor, {
      get height() {
        return get($0);
      },
      variant: "solid",
      padding: false,
      get elem_id() {
        return gradio.shared.elem_id;
      },
      get elem_classes() {
        return gradio.shared.elem_classes;
      },
      get visible() {
        return gradio.shared.visible;
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
          var consequent = ($$anchor3) => {
            BlockLabel($$anchor3, {
              get Icon() {
                return Code;
              },
              get show_label() {
                return gradio.shared.show_label;
              },
              get label() {
                return get(label);
              },
              float: false
            });
          };
          if_block(node_1, ($$render) => {
            if (gradio.shared.show_label) $$render(consequent);
          });
        }
        var node_2 = sibling(node_1, 2);
        {
          var consequent_1 = ($$anchor3) => {
            Empty($$anchor3, {
              unpadded_box: true,
              size: "large",
              children: ($$anchor4, $$slotProps2) => {
                Code($$anchor4);
              },
              $$slots: { default: true }
            });
          };
          var alternate = ($$anchor3) => {
            var fragment_5 = root_5();
            var node_3 = first_child(fragment_5);
            Widgets(node_3, {
              get language() {
                return gradio.props.language;
              },
              get value() {
                return gradio.props.value;
              }
            });
            var node_4 = sibling(node_3, 2);
            {
              let $02 = user_derived(() => !gradio.shared.interactive);
              Code$1(node_4, {
                get language() {
                  return gradio.props.language;
                },
                get lines() {
                  return gradio.props.lines;
                },
                get max_lines() {
                  return gradio.props.max_lines;
                },
                get dark_mode() {
                  return dark_mode;
                },
                get wrap_lines() {
                  return gradio.props.wrap_lines;
                },
                get show_line_numbers() {
                  return gradio.props.show_line_numbers;
                },
                get autocomplete() {
                  return gradio.props.autocomplete;
                },
                get readonly() {
                  return get($02);
                },
                get value() {
                  return gradio.props.value;
                },
                set value($$value) {
                  gradio.props.value = $$value;
                },
                $$events: {
                  blur: () => gradio.dispatch("blur"),
                  focus: () => gradio.dispatch("focus"),
                  change: () => {
                    gradio.dispatch("input");
                  }
                }
              });
            }
            append($$anchor3, fragment_5);
          };
          if_block(node_2, ($$render) => {
            if (!gradio.props.value && !gradio.shared.interactive) $$render(consequent_1);
            else $$render(alternate, false);
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
  Code$1 as BaseCode,
  Copy_1 as BaseCopy,
  Download_1 as BaseDownload,
  default2 as BaseExample,
  Widgets as BaseWidget,
  Index as default
};
//# sourceMappingURL=CxkV7KUw.js.map
