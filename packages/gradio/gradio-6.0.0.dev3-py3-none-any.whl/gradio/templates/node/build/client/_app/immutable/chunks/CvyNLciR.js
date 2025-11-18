import "./9B4_veAf.js";
import { p as push, c as from_html, v as first_child, k as get, A as user_derived, s as sibling, b as append, o as pop, J as state, L as proxy, M as user_effect, j as set, K as tick } from "./DEzry6cj.js";
import { l as snapshot, B as Block, g as Static, G as Gradio } from "./DXi4jxVF.js";
import { i as if_block, r as rest_props, s as spread_props } from "./DUftb7my.js";
import "./BAp-OWo-.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { E as Empty } from "./B-xg5Dhl.js";
import { F as File } from "./bc1v6JFX.js";
import { a as FilePreview, F as FileUpload } from "./B-2qwVul.js";
import { U as UploadText } from "./B8mIV0gF.js";
import { default as default2 } from "./VSLEAopn.js";
var root = from_html(`<!> <!>`, 1);
function File_1($$anchor, $$props) {
  push($$props, true);
  var fragment = root();
  var node = first_child(fragment);
  {
    let $0 = user_derived(() => $$props.value === null);
    let $1 = user_derived(() => $$props.label || "File");
    BlockLabel(node, {
      get show_label() {
        return $$props.show_label;
      },
      get float() {
        return get($0);
      },
      get Icon() {
        return File;
      },
      get label() {
        return get($1);
      }
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent = ($$anchor2) => {
      FilePreview($$anchor2, {
        get i18n() {
          return $$props.i18n;
        },
        get selectable() {
          return $$props.selectable;
        },
        get value() {
          return $$props.value;
        },
        get height() {
          return $$props.height;
        },
        $$events: {
          select(...$$args) {
            $$props.on_select?.apply(this, $$args);
          },
          download(...$$args) {
            $$props.on_download?.apply(this, $$args);
          }
        }
      });
    };
    var alternate = ($$anchor2) => {
      Empty($$anchor2, {
        unpadded_box: true,
        size: "large",
        children: ($$anchor3, $$slotProps) => {
          File($$anchor3);
        },
        $$slots: { default: true }
      });
    };
    if_block(node_1, ($$render) => {
      if ($$props.value && (Array.isArray($$props.value) ? $$props.value.length > 0 : true)) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
var root_1 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  let upload_promise = state(void 0);
  let dragging = state(false);
  class FileGradio extends Gradio {
    async get_data() {
      if (get(upload_promise)) {
        await get(upload_promise);
        await tick();
      }
      const data = await super.get_data();
      return data;
    }
  }
  const gradio = new FileGradio(props);
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) !== gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change", snapshot(gradio.props.value));
    }
  });
  {
    let $0 = user_derived(() => gradio.props.value ? "solid" : "dashed");
    let $1 = user_derived(() => get(dragging) ? "focus" : "base");
    Block($$anchor, {
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
      children: ($$anchor2, $$slotProps) => {
        var fragment_1 = root_1();
        var node = first_child(fragment_1);
        {
          let $02 = user_derived(() => gradio.shared.loading_status?.status || "complete");
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
              get status() {
                return get($02);
              },
              $$events: {
                clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
              }
            }
          ));
        }
        var node_1 = sibling(node, 2);
        {
          var consequent = ($$anchor3) => {
            File_1($$anchor3, {
              on_select: ({ detail }) => gradio.dispatch("select", detail),
              on_download: ({ detail }) => gradio.dispatch("download", detail),
              get selectable() {
                return gradio.props._selectable;
              },
              get value() {
                return gradio.props.value;
              },
              get label() {
                return gradio.shared.label;
              },
              get show_label() {
                return gradio.shared.show_label;
              },
              get height() {
                return gradio.props.height;
              },
              get i18n() {
                return gradio.i18n;
              }
            });
          };
          var alternate = ($$anchor3) => {
            FileUpload($$anchor3, {
              upload: (...args) => gradio.shared.client.upload(...args),
              stream_handler: (...args) => gradio.shared.client.stream(...args),
              get label() {
                return gradio.shared.label;
              },
              get show_label() {
                return gradio.shared.show_label;
              },
              get value() {
                return gradio.props.value;
              },
              get file_count() {
                return gradio.props.file_count;
              },
              get file_types() {
                return gradio.props.file_types;
              },
              get selectable() {
                return gradio.props._selectable;
              },
              get height() {
                return gradio.props.height;
              },
              get root() {
                return gradio.shared.root;
              },
              get allow_reordering() {
                return gradio.props.allow_reordering;
              },
              get max_file_size() {
                return gradio.shared.max_file_size;
              },
              get i18n() {
                return gradio.i18n;
              },
              get upload_promise() {
                return get(upload_promise);
              },
              set upload_promise($$value) {
                set(upload_promise, $$value, true);
              },
              $$events: {
                change: ({ detail }) => {
                  gradio.props.value = detail;
                },
                drag: ({ detail }) => set(dragging, detail, true),
                clear: () => gradio.dispatch("clear"),
                select: ({ detail }) => gradio.dispatch("select", detail),
                upload: () => gradio.dispatch("upload"),
                error: ({ detail }) => {
                  gradio.shared.loading_status = gradio.shared.loading_status || {};
                  gradio.shared.loading_status.status = "error";
                  gradio.dispatch("error", detail);
                },
                delete: ({ detail }) => {
                  gradio.dispatch("delete", detail);
                }
              },
              children: ($$anchor4, $$slotProps2) => {
                UploadText($$anchor4, {
                  get i18n() {
                    return gradio.i18n;
                  },
                  type: "file"
                });
              },
              $$slots: { default: true }
            });
          };
          if_block(node_1, ($$render) => {
            if (!gradio.shared.interactive) $$render(consequent);
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
  default2 as BaseExample,
  File_1 as BaseFile,
  FileUpload as BaseFileUpload,
  FilePreview,
  Index as default
};
//# sourceMappingURL=CvyNLciR.js.map
