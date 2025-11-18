const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./BAZBy-k2.js","./DUftb7my.js","./DEzry6cj.js","./DdkXqxbl.js","./9B4_veAf.js","./BAp-OWo-.js","./CswR_hUw.js","./DB0xzveP.js","./CW83eULi.js","./C5p8OC7C.js"])))=>i.map(i=>d[i]);
import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, i as legacy_pre_effect, j as set, m as mutable_source, k as get, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, v as first_child, x as derived_safe_equal, s as sibling, b as append, o as pop, D as comment, d as child, r as reset, K as tick, y as untrack, J as state, L as proxy, M as user_effect, A as user_derived } from "./DEzry6cj.js";
import { p as prop, i as if_block, _ as __vitePreload, c as component, b as bind_this, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { c as bubble_event, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import Model3D from "./A4Y-ihWj.js";
import "./BAp-OWo-.js";
import { s as slot } from "./DX-MI-YE.js";
import { i as init } from "./DB0xzveP.js";
import { U as Upload } from "./BcroWaqq.js";
import { M as ModifyUpload } from "./BXBtG43Y.js";
/* empty css         */
import { B as BlockLabel } from "./DEb09X9A.js";
import { F as File } from "./bc1v6JFX.js";
import { E as Empty } from "./B-xg5Dhl.js";
import { U as UploadText } from "./B8mIV0gF.js";
import { default as default2 } from "./FplWS8BC.js";
var root_4$1 = from_html(`<div class="input-model svelte-18wa0f8"><!> <!></div>`);
var root_1 = from_html(`<!> <!>`, 1);
function Model3DUpload($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 12);
  let display_mode = prop($$props, "display_mode", 8, "solid");
  let clear_color = prop($$props, "clear_color", 24, () => [0, 0, 0, 0]);
  let label = prop($$props, "label", 8, "");
  let show_label = prop($$props, "show_label", 8);
  let root = prop($$props, "root", 8);
  let i18n = prop($$props, "i18n", 8);
  let zoom_speed = prop($$props, "zoom_speed", 8, 1);
  let pan_speed = prop($$props, "pan_speed", 8, 1);
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let uploading = prop($$props, "uploading", 12, false);
  let upload_promise = prop($$props, "upload_promise", 12, null);
  let camera_position = prop($$props, "camera_position", 24, () => [null, null, null]);
  let upload = prop($$props, "upload", 8);
  let stream_handler = prop($$props, "stream_handler", 8);
  async function handle_upload({ detail }) {
    value(detail);
    await tick();
    dispatch("change", value());
    dispatch("load", value());
  }
  async function handle_clear() {
    value(null);
    await tick();
    dispatch("clear");
    dispatch("change");
  }
  let use_3dgs = mutable_source(false);
  let Canvas3DGSComponent = mutable_source();
  let Canvas3DComponent = mutable_source();
  async function loadCanvas3D() {
    const module = await __vitePreload(() => import("./BAZBy-k2.js"), true ? __vite__mapDeps([0,1,2,3,4,5,6,7,8]) : void 0, import.meta.url);
    return module.default;
  }
  async function loadCanvas3DGS() {
    const module = await __vitePreload(() => import("./C5p8OC7C.js"), true ? __vite__mapDeps([9,4,2,5,1,3,7,8]) : void 0, import.meta.url);
    return module.default;
  }
  let canvas3d = mutable_source();
  async function handle_undo() {
    get(canvas3d)?.reset_camera_position();
  }
  const dispatch = createEventDispatcher();
  let dragging = mutable_source(false);
  legacy_pre_effect(() => (deep_read_state(value()), get(use_3dgs)), () => {
    if (value()) {
      set(use_3dgs, value().path.endsWith(".splat") || value().path.endsWith(".ply"));
      if (get(use_3dgs)) {
        loadCanvas3DGS().then((component2) => {
          set(Canvas3DGSComponent, component2);
        });
      } else {
        loadCanvas3D().then((component2) => {
          set(Canvas3DComponent, component2);
        });
      }
    }
  });
  legacy_pre_effect(() => get(dragging), () => {
    dispatch("drag", get(dragging));
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root_1();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => label() || "3D Model");
    BlockLabel(node, {
      get show_label() {
        return show_label();
      },
      get Icon() {
        return File;
      },
      get label() {
        return get($0);
      }
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent = ($$anchor2) => {
      {
        let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("model3d.drop_to_upload"))));
        Upload($$anchor2, {
          get upload() {
            return upload();
          },
          get stream_handler() {
            return stream_handler();
          },
          get root() {
            return root();
          },
          get max_file_size() {
            return max_file_size();
          },
          filetype: [
            ".stl",
            ".obj",
            ".gltf",
            ".glb",
            "model/obj",
            ".splat",
            ".ply"
          ],
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
            load: handle_upload,
            error($$arg) {
              bubble_event.call(this, $$props, $$arg);
            }
          },
          children: ($$anchor3, $$slotProps) => {
            var fragment_2 = comment();
            var node_2 = first_child(fragment_2);
            slot(node_2, $$props, "default", {}, null);
            append($$anchor3, fragment_2);
          },
          $$slots: { default: true },
          $$legacy: true
        });
      }
    };
    var alternate_1 = ($$anchor2) => {
      var div = root_4$1();
      var node_3 = child(div);
      {
        let $0 = derived_safe_equal(() => !get(use_3dgs));
        ModifyUpload(node_3, {
          get undoable() {
            return get($0);
          },
          get i18n() {
            return i18n();
          },
          $$events: { clear: handle_clear, undo: handle_undo }
        });
      }
      var node_4 = sibling(node_3, 2);
      {
        var consequent_1 = ($$anchor3) => {
          var fragment_3 = comment();
          var node_5 = first_child(fragment_3);
          component(node_5, () => get(Canvas3DGSComponent), ($$anchor4, $$component) => {
            $$component($$anchor4, {
              get value() {
                return value();
              },
              get zoom_speed() {
                return zoom_speed();
              },
              get pan_speed() {
                return pan_speed();
              }
            });
          });
          append($$anchor3, fragment_3);
        };
        var alternate = ($$anchor3) => {
          var fragment_4 = comment();
          var node_6 = first_child(fragment_4);
          component(node_6, () => get(Canvas3DComponent), ($$anchor4, $$component) => {
            bind_this(
              $$component($$anchor4, {
                get value() {
                  return value();
                },
                get display_mode() {
                  return display_mode();
                },
                get clear_color() {
                  return clear_color();
                },
                get camera_position() {
                  return camera_position();
                },
                get zoom_speed() {
                  return zoom_speed();
                },
                get pan_speed() {
                  return pan_speed();
                },
                $$legacy: true
              }),
              ($$value) => set(canvas3d, $$value),
              () => get(canvas3d)
            );
          });
          append($$anchor3, fragment_4);
        };
        if_block(node_4, ($$render) => {
          if (get(use_3dgs)) $$render(consequent_1);
          else $$render(alternate, false);
        });
      }
      reset(div);
      append($$anchor2, div);
    };
    if_block(node_1, ($$render) => {
      if (value() == null) $$render(consequent);
      else $$render(alternate_1, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
var root_4 = from_html(`<!> <!>`, 1);
var root_2 = from_html(`<!> <!>`, 1);
var root_7 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  class Model3dGradio extends Gradio {
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
  const gradio = new Model3dGradio(props);
  let old_value = state(proxy(gradio.props.value));
  let uploading = state(false);
  let dragging = state(false);
  let has_change_history = state(false);
  let upload_promise = state(void 0);
  const is_browser = typeof window !== "undefined";
  user_effect(() => {
    if (get(old_value) !== gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  function handle_change(detail) {
    gradio.props.value = detail;
    gradio.dispatch("change", detail);
    set(has_change_history, true);
  }
  function handle_drag(detail) {
    set(dragging, detail, true);
  }
  function handle_clear() {
    gradio.props.value = null;
    gradio.dispatch("clear");
  }
  function handle_load(detail) {
    gradio.props.value = detail;
    gradio.dispatch("upload");
  }
  function handle_error(detail) {
    if (gradio.shared.loading_status) gradio.shared.loading_status.status = "error";
    gradio.dispatch("error", detail);
  }
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent_1 = ($$anchor2) => {
      {
        let $0 = user_derived(() => gradio.props.value === null ? "dashed" : "solid");
        let $1 = user_derived(() => get(dragging) ? "focus" : "base");
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
          get container() {
            return gradio.shared.container;
          },
          get scale() {
            return gradio.shared.scale;
          },
          get min_width() {
            return gradio.shared.min_width;
          },
          get height() {
            return gradio.props.height;
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
              var consequent = ($$anchor4) => {
                Model3D($$anchor4, {
                  get value() {
                    return gradio.props.value;
                  },
                  get i18n() {
                    return gradio.i18n;
                  },
                  get display_mode() {
                    return gradio.props.display_mode;
                  },
                  get clear_color() {
                    return gradio.props.clear_color;
                  },
                  get label() {
                    return gradio.shared.label;
                  },
                  get show_label() {
                    return gradio.shared.show_label;
                  },
                  get camera_position() {
                    return gradio.props.camera_position;
                  },
                  get zoom_speed() {
                    return gradio.props.zoom_speed;
                  },
                  get has_change_history() {
                    return get(has_change_history);
                  }
                });
              };
              var alternate = ($$anchor4) => {
                var fragment_4 = root_4();
                var node_3 = first_child(fragment_4);
                {
                  let $02 = user_derived(() => gradio.shared.label || "3D Model");
                  BlockLabel(node_3, {
                    get show_label() {
                      return gradio.shared.show_label;
                    },
                    get Icon() {
                      return File;
                    },
                    get label() {
                      return get($02);
                    }
                  });
                }
                var node_4 = sibling(node_3, 2);
                Empty(node_4, {
                  unpadded_box: true,
                  size: "large",
                  children: ($$anchor5, $$slotProps2) => {
                    File($$anchor5);
                  },
                  $$slots: { default: true }
                });
                append($$anchor4, fragment_4);
              };
              if_block(node_2, ($$render) => {
                if (gradio.props.value && is_browser) $$render(consequent);
                else $$render(alternate, false);
              });
            }
            append($$anchor3, fragment_2);
          },
          $$slots: { default: true }
        });
      }
    };
    var alternate_1 = ($$anchor2) => {
      {
        let $0 = user_derived(() => gradio.props.value === null ? "dashed" : "solid");
        let $1 = user_derived(() => get(dragging) ? "focus" : "base");
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
          get container() {
            return gradio.shared.container;
          },
          get scale() {
            return gradio.shared.scale;
          },
          get min_width() {
            return gradio.shared.min_width;
          },
          get height() {
            return gradio.props.height;
          },
          children: ($$anchor3, $$slotProps) => {
            var fragment_7 = root_7();
            var node_5 = first_child(fragment_7);
            Static(node_5, spread_props(
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
            var node_6 = sibling(node_5, 2);
            Model3DUpload(node_6, {
              get label() {
                return gradio.shared.label;
              },
              get show_label() {
                return gradio.shared.show_label;
              },
              get root() {
                return gradio.shared.root;
              },
              get display_mode() {
                return gradio.props.display_mode;
              },
              get clear_color() {
                return gradio.props.clear_color;
              },
              get value() {
                return gradio.props.value;
              },
              get camera_position() {
                return gradio.props.camera_position;
              },
              get zoom_speed() {
                return gradio.props.zoom_speed;
              },
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
                change: ({ detail }) => handle_change(detail),
                drag: ({ detail }) => handle_drag(detail),
                clear: handle_clear,
                load: ({ detail }) => handle_load(detail),
                error: ({ detail }) => handle_error(detail)
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
            append($$anchor3, fragment_7);
          },
          $$slots: { default: true }
        });
      }
    };
    if_block(node, ($$render) => {
      if (!gradio.shared.interactive) $$render(consequent_1);
      else $$render(alternate_1, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  default2 as BaseExample,
  Model3D as BaseModel3D,
  Model3DUpload as BaseModel3DUpload,
  Index as default
};
//# sourceMappingURL=fMSg9-W6.js.map
