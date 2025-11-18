const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./BAZBy-k2.js","./DUftb7my.js","./DEzry6cj.js","./DdkXqxbl.js","./9B4_veAf.js","./BAp-OWo-.js","./CswR_hUw.js","./DB0xzveP.js","./CW83eULi.js","./C5p8OC7C.js"])))=>i.map(i=>d[i]);
import { p as prop, i as if_block, _ as __vitePreload, c as component, b as bind_this } from "./DUftb7my.js";
import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, m as mutable_source, i as legacy_pre_effect, j as set, k as get, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, v as first_child, x as derived_safe_equal, s as sibling, b as append, o as pop, y as untrack, d as child, r as reset, t as template_effect, D as comment } from "./DEzry6cj.js";
import { I as IconButtonWrapper, s as set_attribute, b as IconButton } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { D as Download } from "./rkplYKOt.js";
import { F as File } from "./bc1v6JFX.js";
import { U as Undo } from "./oKXAgRt1.js";
import { d as dequal } from "./ShnGN6OY.js";
var root_2 = from_html(`<!> <a><!></a>`, 1);
var root_1 = from_html(`<div class="model3D svelte-pnaihf" data-testid="model3d"><!> <!></div>`);
var root = from_html(`<!> <!>`, 1);
function Model3D($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let display_mode = prop($$props, "display_mode", 8, "solid");
  let clear_color = prop($$props, "clear_color", 24, () => [0, 0, 0, 0]);
  let label = prop($$props, "label", 8, "");
  let show_label = prop($$props, "show_label", 8);
  let i18n = prop($$props, "i18n", 8);
  let zoom_speed = prop($$props, "zoom_speed", 8, 1);
  let pan_speed = prop($$props, "pan_speed", 8, 1);
  let camera_position = prop($$props, "camera_position", 24, () => [null, null, null]);
  let has_change_history = prop($$props, "has_change_history", 8, false);
  let current_settings = mutable_source({
    camera_position: camera_position(),
    zoom_speed: zoom_speed(),
    pan_speed: pan_speed()
  });
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
  function handle_undo() {
    get(canvas3d)?.reset_camera_position();
  }
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
  legacy_pre_effect(
    () => (get(current_settings), deep_read_state(camera_position()), deep_read_state(zoom_speed()), deep_read_state(pan_speed()), get(canvas3d)),
    () => {
      if (!dequal(get(current_settings).camera_position, camera_position()) || get(current_settings).zoom_speed !== zoom_speed() || get(current_settings).pan_speed !== pan_speed()) {
        get(canvas3d)?.update_camera(camera_position(), zoom_speed(), pan_speed());
        set(current_settings, {
          camera_position: camera_position(),
          zoom_speed: zoom_speed(),
          pan_speed: pan_speed()
        });
      }
    }
  );
  legacy_pre_effect_reset();
  init();
  var fragment = root();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => (deep_read_state(label()), deep_read_state(i18n()), untrack(() => label() || i18n()("3D_model.3d_model"))));
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
    var consequent_2 = ($$anchor2) => {
      var div = root_1();
      var node_2 = child(div);
      IconButtonWrapper(node_2, {
        children: ($$anchor3, $$slotProps) => {
          var fragment_1 = root_2();
          var node_3 = first_child(fragment_1);
          {
            var consequent = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => !has_change_history());
                IconButton($$anchor4, {
                  get Icon() {
                    return Undo;
                  },
                  label: "Undo",
                  get disabled() {
                    return get($0);
                  },
                  $$events: { click: () => handle_undo() }
                });
              }
            };
            if_block(node_3, ($$render) => {
              if (!get(use_3dgs)) $$render(consequent);
            });
          }
          var a = sibling(node_3, 2);
          set_attribute(a, "target", untrack(() => window.__is_colab__ ? "_blank" : null));
          var node_4 = child(a);
          {
            let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.download"))));
            IconButton(node_4, {
              get Icon() {
                return Download;
              },
              get label() {
                return get($0);
              }
            });
          }
          reset(a);
          template_effect(() => {
            set_attribute(a, "href", (deep_read_state(value()), untrack(() => value().url)));
            set_attribute(a, "download", (deep_read_state(value()), untrack(() => window.__is_colab__ ? null : value().orig_name || value().path)));
          });
          append($$anchor3, fragment_1);
        },
        $$slots: { default: true }
      });
      var node_5 = sibling(node_2, 2);
      {
        var consequent_1 = ($$anchor3) => {
          var fragment_3 = comment();
          var node_6 = first_child(fragment_3);
          component(node_6, () => get(Canvas3DGSComponent), ($$anchor4, $$component) => {
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
          var node_7 = first_child(fragment_4);
          component(node_7, () => get(Canvas3DComponent), ($$anchor4, $$component) => {
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
        if_block(node_5, ($$render) => {
          if (get(use_3dgs)) $$render(consequent_1);
          else $$render(alternate, false);
        });
      }
      reset(div);
      append($$anchor2, div);
    };
    if_block(node_1, ($$render) => {
      if (value()) $$render(consequent_2);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  Model3D as default
};
//# sourceMappingURL=A4Y-ihWj.js.map
