import "./9B4_veAf.js";
import { p as push, c as from_html, v as first_child, s as sibling, k as get, A as user_derived, b as append, j as set, J as state, o as pop, K as tick } from "./DEzry6cj.js";
import { r as rest_props, s as spread_props, i as if_block } from "./DUftb7my.js";
import { B as Block, g as Static, G as Gradio } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { U as UploadText } from "./B8mIV0gF.js";
import Gallery from "./CBw2PUcx.js";
import { F as FileUpload } from "./B-2qwVul.js";
/* empty css         */
import { default as default2 } from "./gPdA5hey.js";
var root_1 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let upload_promise = state(void 0);
  class GalleryGradio extends Gradio {
    async get_data() {
      if (get(upload_promise)) {
        await get(upload_promise);
        await tick();
      }
      const data = await super.get_data();
      return data;
    }
  }
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new GalleryGradio(props);
  let fullscreen = state(false);
  let no_value = user_derived(() => gradio.props.value === null ? true : gradio.props.value.length === 0);
  function handle_delete(event) {
    if (!gradio.props.value) return;
    const { index } = event.detail;
    gradio.dispatch("delete", event.detail);
    gradio.props.value = gradio.props.value.filter((_, i) => i !== index);
    gradio.dispatch("change", gradio.props.value);
  }
  async function process_upload_files(files) {
    const processed_files = await Promise.all(files.map(async (x) => {
      if (x.path?.toLowerCase().endsWith(".svg") && x.url) {
        const response = await fetch(x.url);
        const svgContent = await response.text();
        return {
          ...x,
          url: `data:image/svg+xml,${encodeURIComponent(svgContent)}`
        };
      }
      return x;
    }));
    return processed_files.map((x) => x.mime_type?.includes("video") ? { video: x, caption: null } : { image: x, caption: null });
  }
  {
    let $0 = user_derived(() => typeof gradio.props.height === "number" ? gradio.props.height : void 0);
    Block($$anchor, {
      get visible() {
        return gradio.shared.visible;
      },
      variant: "solid",
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
      get height() {
        return get($0);
      },
      get fullscreen() {
        return get(fullscreen);
      },
      set fullscreen($$value) {
        set(fullscreen, $$value, true);
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
            FileUpload($$anchor3, {
              value: null,
              get root() {
                return gradio.shared.root;
              },
              get label() {
                return gradio.shared.label;
              },
              get max_file_size() {
                return gradio.shared.max_file_size;
              },
              file_count: "multiple",
              get file_types() {
                return gradio.props.file_types;
              },
              get i18n() {
                return gradio.i18n;
              },
              upload: (...args) => gradio.shared.client.upload(...args),
              stream_handler: (...args) => gradio.shared.client.stream(...args),
              get upload_promise() {
                return get(upload_promise);
              },
              set upload_promise($$value) {
                set(upload_promise, $$value, true);
              },
              $$events: {
                upload: async (e) => {
                  const files = Array.isArray(e.detail) ? e.detail : [e.detail];
                  gradio.props.value = await process_upload_files(files);
                  gradio.dispatch("upload", gradio.props.value);
                  gradio.dispatch("change", gradio.props.value);
                },
                error: ({ detail }) => {
                  gradio.shared.loading_status = gradio.shared.loading_status || {};
                  gradio.shared.loading_status.status = "error";
                  gradio.dispatch("error", detail);
                }
              },
              children: ($$anchor4, $$slotProps2) => {
                UploadText($$anchor4, {
                  get i18n() {
                    return gradio.i18n;
                  },
                  type: "gallery"
                });
              },
              $$slots: { default: true }
            });
          };
          var alternate = ($$anchor3) => {
            {
              let $02 = user_derived(() => gradio.props.buttons.includes("share"));
              let $1 = user_derived(() => gradio.props.buttons.includes("download"));
              let $2 = user_derived(() => gradio.props.buttons.includes("fullscreen"));
              Gallery($$anchor3, {
                get label() {
                  return gradio.shared.label;
                },
                get show_label() {
                  return gradio.shared.show_label;
                },
                get columns() {
                  return gradio.props.columns;
                },
                get rows() {
                  return gradio.props.rows;
                },
                get height() {
                  return gradio.props.height;
                },
                get preview() {
                  return gradio.props.preview;
                },
                get object_fit() {
                  return gradio.props.object_fit;
                },
                get interactive() {
                  return gradio.shared.interactive;
                },
                get allow_preview() {
                  return gradio.props.allow_preview;
                },
                get show_share_button() {
                  return get($02);
                },
                get show_download_button() {
                  return get($1);
                },
                get fit_columns() {
                  return gradio.props.fit_columns;
                },
                get i18n() {
                  return gradio.i18n;
                },
                _fetch: (...args) => gradio.shared.client.fetch(...args),
                get show_fullscreen_button() {
                  return get($2);
                },
                get fullscreen() {
                  return get(fullscreen);
                },
                get root() {
                  return gradio.shared.root;
                },
                get file_types() {
                  return gradio.props.file_types;
                },
                get max_file_size() {
                  return gradio.shared.max_file_size;
                },
                upload: (...args) => gradio.shared.client.upload(...args),
                stream_handler: (...args) => gradio.shared.client.stream(...args),
                get selected_index() {
                  return gradio.props.selected_index;
                },
                set selected_index($$value) {
                  gradio.props.selected_index = $$value;
                },
                get value() {
                  return gradio.props.value;
                },
                set value($$value) {
                  gradio.props.value = $$value;
                },
                $$events: {
                  change: () => gradio.dispatch("change"),
                  clear: () => gradio.dispatch("change"),
                  select: (e) => gradio.dispatch("select", e.detail),
                  share: (e) => gradio.dispatch("share", e.detail),
                  error: (e) => gradio.dispatch("error", e.detail),
                  preview_open: () => gradio.dispatch("preview_open"),
                  preview_close: () => gradio.dispatch("preview_close"),
                  fullscreen: ({ detail }) => {
                    set(fullscreen, detail, true);
                  },
                  delete: handle_delete,
                  upload: async (e) => {
                    const files = Array.isArray(e.detail) ? e.detail : [e.detail];
                    const new_value = await process_upload_files(files);
                    gradio.props.value = gradio.props.value ? [...gradio.props.value, ...new_value] : new_value;
                    gradio.dispatch("upload", new_value);
                    gradio.dispatch("change", gradio.props.value);
                  }
                }
              });
            }
          };
          if_block(node_1, ($$render) => {
            if (gradio.shared.interactive && get(no_value)) $$render(consequent);
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
  Gallery as BaseGallery,
  Index as default
};
//# sourceMappingURL=BCA8BwcG.js.map
