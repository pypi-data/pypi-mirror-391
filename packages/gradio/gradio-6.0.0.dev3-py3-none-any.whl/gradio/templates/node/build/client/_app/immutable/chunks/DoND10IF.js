import "./9B4_veAf.js";
import { p as push, J as state, L as proxy, M as user_effect, k as get, j as set, c as from_html, v as first_child, s as sibling, A as user_derived, d as child, r as reset, b as append, D as comment, t as template_effect, o as pop, g as set_text, z as event } from "./DEzry6cj.js";
import { r as rest_props, s as spread_props, i as if_block, b as bind_this } from "./DUftb7my.js";
import { G as Gradio, B as Block, g as Static, I as IconButtonWrapper, t as each, v as index, s as set_attribute, a as set_class, p as set_style } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { E as Empty } from "./B-xg5Dhl.js";
import { I as Image } from "./dWqAVU0H.js";
import { F as FullscreenButton } from "./BAYq2deR.js";
var root_7 = from_html(`<img/>`);
var root_9 = from_html(`<button class="legend-item svelte-1oizopk"> </button>`);
var root_8 = from_html(`<div class="legend svelte-1oizopk"></div>`);
var root_4 = from_html(`<div class="image-container svelte-1oizopk"><!> <img alt="the base file that is annotated"/> <!></div> <!>`, 1);
var root_1 = from_html(`<!> <!> <div class="container svelte-1oizopk"><!></div>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let old_value = state(proxy(gradio.props.value));
  let active = state(null);
  let image_container;
  let fullscreen = state(false);
  let label = user_derived(() => gradio.shared.label || gradio.i18n("annotated_image.annotated_image"));
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  function handle_mouseover(_label) {
    set(active, _label, true);
  }
  function handle_mouseout() {
    set(active, null);
  }
  function handle_click(i, value) {
    gradio.dispatch("select", { value, index: i });
  }
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
    padding: false,
    get height() {
      return gradio.props.height;
    },
    get width() {
      return gradio.props.width;
    },
    allow_overflow: false,
    get container() {
      return gradio.shared.container;
    },
    get scale() {
      return gradio.shared.scale;
    },
    get min_width() {
      return gradio.shared.min_width;
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
        () => gradio.shared.loading_status
      ));
      var node_1 = sibling(node, 2);
      BlockLabel(node_1, {
        get show_label() {
          return gradio.shared.show_label;
        },
        get Icon() {
          return Image;
        },
        get label() {
          return get(label);
        }
      });
      var div = sibling(node_1, 2);
      var node_2 = child(div);
      {
        var consequent = ($$anchor3) => {
          Empty($$anchor3, {
            size: "large",
            unpadded_box: true,
            children: ($$anchor4, $$slotProps2) => {
              Image($$anchor4);
            },
            $$slots: { default: true }
          });
        };
        var alternate = ($$anchor3) => {
          var fragment_4 = root_4();
          var div_1 = first_child(fragment_4);
          var node_3 = child(div_1);
          IconButtonWrapper(node_3, {
            children: ($$anchor4, $$slotProps2) => {
              var fragment_5 = comment();
              var node_4 = first_child(fragment_5);
              {
                var consequent_1 = ($$anchor5) => {
                  FullscreenButton($$anchor5, {
                    get fullscreen() {
                      return get(fullscreen);
                    },
                    $$events: {
                      fullscreen: ({ detail }) => {
                        set(fullscreen, detail, true);
                      }
                    }
                  });
                };
                if_block(node_4, ($$render) => {
                  if (gradio.props.buttons.includes("fullscreen") ?? true) $$render(consequent_1);
                });
              }
              append($$anchor4, fragment_5);
            },
            $$slots: { default: true }
          });
          var img = sibling(node_3, 2);
          let classes;
          var node_5 = sibling(img, 2);
          each(node_5, 17, () => gradio.props.value ? gradio.props.value.annotations : [], index, ($$anchor4, ann, i) => {
            var img_1 = root_7();
            let classes_1;
            template_effect(
              ($0) => {
                set_attribute(img_1, "alt", `segmentation mask identifying ${gradio.shared.label ?? ""} within the uploaded file`);
                classes_1 = set_class(img_1, 1, "mask fit-height svelte-1oizopk", null, classes_1, {
                  "fit-height": !get(fullscreen),
                  active: get(active) == get(ann).label,
                  inactive: get(active) != get(ann).label && get(active) != null
                });
                set_attribute(img_1, "src", get(ann).image.url);
                set_style(img_1, $0);
              },
              [
                () => gradio.props.color_map && get(ann).label in gradio.props.color_map ? null : `filter: hue-rotate(${Math.round(i * 360 / (gradio.props.value?.annotations.length ?? 1))}deg);`
              ]
            );
            append($$anchor4, img_1);
          });
          reset(div_1);
          bind_this(div_1, ($$value) => image_container = $$value, () => image_container);
          var node_6 = sibling(div_1, 2);
          {
            var consequent_2 = ($$anchor4) => {
              var div_2 = root_8();
              each(div_2, 21, () => gradio.props.value.annotations, index, ($$anchor5, ann, i) => {
                var button = root_9();
                var text = child(button, true);
                reset(button);
                template_effect(
                  ($0) => {
                    set_style(button, `background-color: ${$0 ?? ""}`);
                    set_text(text, get(ann).label);
                  },
                  [
                    () => gradio.props.color_map && get(ann).label in gradio.props.color_map ? gradio.props.color_map[get(ann).label] + "88" : `hsla(${Math.round(i * 360 / gradio.props.value.annotations.length)}, 100%, 50%, 0.3)`
                  ]
                );
                event("mouseover", button, () => handle_mouseover(get(ann).label));
                event("focus", button, () => handle_mouseover(get(ann).label));
                event("mouseout", button, () => handle_mouseout());
                event("blur", button, () => handle_mouseout());
                event("click", button, () => handle_click(i, get(ann).label));
                append($$anchor5, button);
              });
              reset(div_2);
              append($$anchor4, div_2);
            };
            if_block(node_6, ($$render) => {
              if (gradio.props.show_legend && gradio.props.value) $$render(consequent_2);
            });
          }
          template_effect(() => {
            classes = set_class(img, 1, "base-image svelte-1oizopk", null, classes, { "fit-height": gradio.props.height && !get(fullscreen) });
            set_attribute(img, "src", gradio.props.value ? gradio.props.value.image.url : null);
          });
          append($$anchor3, fragment_4);
        };
        if_block(node_2, ($$render) => {
          if (gradio.props.value == null) $$render(consequent);
          else $$render(alternate, false);
        });
      }
      reset(div);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=DoND10IF.js.map
