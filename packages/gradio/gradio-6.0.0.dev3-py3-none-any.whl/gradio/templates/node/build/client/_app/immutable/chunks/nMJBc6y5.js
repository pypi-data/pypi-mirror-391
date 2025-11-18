import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, c as from_html, v as first_child, k as get, x as derived_safe_equal, s as sibling, u as deep_read_state, y as untrack, b as append, o as pop, d as child, r as reset, t as template_effect, z as event, m as mutable_source, j as set } from "./DEzry6cj.js";
import { p as prop, i as if_block, b as bind_this } from "./DUftb7my.js";
import { I as IconButtonWrapper, c as bubble_event, b as IconButton, u as uploadToHuggingFace, j as Image$1, a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { D as DownloadLink } from "./BFO3TfnI.js";
import { E as Empty } from "./B-xg5Dhl.js";
import { S as ShareButton } from "./D6EAw2Po.js";
import { D as Download } from "./rkplYKOt.js";
import { I as Image } from "./dWqAVU0H.js";
import { F as FullscreenButton } from "./BAYq2deR.js";
const get_coordinates_of_clicked_image = (evt) => {
  let image;
  if (evt.currentTarget instanceof Element) {
    image = evt.currentTarget.querySelector("img");
  } else {
    return [NaN, NaN];
  }
  const imageRect = image.getBoundingClientRect();
  const xScale = image.naturalWidth / imageRect.width;
  const yScale = image.naturalHeight / imageRect.height;
  if (xScale > yScale) {
    const displayed_height = image.naturalHeight / xScale;
    const y_offset = (imageRect.height - displayed_height) / 2;
    var x = Math.round((evt.clientX - imageRect.left) * xScale);
    var y = Math.round((evt.clientY - imageRect.top - y_offset) * xScale);
  } else {
    const displayed_width = image.naturalWidth / yScale;
    const x_offset = (imageRect.width - displayed_width) / 2;
    var x = Math.round((evt.clientX - imageRect.left - x_offset) * yScale);
    var y = Math.round((evt.clientY - imageRect.top) * yScale);
  }
  if (x < 0 || x >= image.naturalWidth || y < 0 || y >= image.naturalHeight) {
    return null;
  }
  return [x, y];
};
var root_4 = from_html(`<!> <!> <!>`, 1);
var root_3 = from_html(`<div class="image-container svelte-12vrxzd"><!> <button class="svelte-12vrxzd"><div><!></div></button></div>`);
var root = from_html(`<!> <!>`, 1);
function ImagePreview($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let label = prop($$props, "label", 8, void 0);
  let show_label = prop($$props, "show_label", 8);
  let buttons = prop($$props, "buttons", 8, null);
  let selectable = prop($$props, "selectable", 8, false);
  let i18n = prop($$props, "i18n", 8);
  let display_icon_button_wrapper_top_corner = prop($$props, "display_icon_button_wrapper_top_corner", 8, false);
  let fullscreen = prop($$props, "fullscreen", 8, false);
  const dispatch = createEventDispatcher();
  const handle_click = (evt) => {
    let coordinates = get_coordinates_of_clicked_image(evt);
    if (coordinates) {
      dispatch("select", { index: coordinates, value: null });
    }
  };
  let image_container = mutable_source();
  init();
  var fragment = root();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => (deep_read_state(show_label()), deep_read_state(label()), deep_read_state(i18n()), untrack(() => !show_label() ? "" : label() || i18n()("image.image"))));
    BlockLabel(node, {
      get show_label() {
        return show_label();
      },
      get Icon() {
        return Image;
      },
      get label() {
        return get($0);
      }
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent = ($$anchor2) => {
      Empty($$anchor2, {
        unpadded_box: true,
        size: "large",
        children: ($$anchor3, $$slotProps) => {
          Image($$anchor3);
        },
        $$slots: { default: true }
      });
    };
    var alternate = ($$anchor2) => {
      var div = root_3();
      var node_2 = child(div);
      IconButtonWrapper(node_2, {
        get display_top_corner() {
          return display_icon_button_wrapper_top_corner();
        },
        children: ($$anchor3, $$slotProps) => {
          var fragment_3 = root_4();
          var node_3 = first_child(fragment_3);
          {
            var consequent_1 = ($$anchor4) => {
              FullscreenButton($$anchor4, {
                get fullscreen() {
                  return fullscreen();
                },
                $$events: {
                  fullscreen($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  }
                }
              });
            };
            if_block(node_3, ($$render) => {
              if (deep_read_state(buttons()), untrack(() => buttons() === null ? true : buttons().includes("fullscreen"))) $$render(consequent_1);
            });
          }
          var node_4 = sibling(node_3, 2);
          {
            var consequent_2 = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value().orig_name || "image")));
                DownloadLink($$anchor4, {
                  get href() {
                    return deep_read_state(value()), untrack(() => value().url);
                  },
                  get download() {
                    return get($0);
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
            if_block(node_4, ($$render) => {
              if (deep_read_state(buttons()), untrack(() => buttons() === null ? true : buttons().includes("download"))) $$render(consequent_2);
            });
          }
          var node_5 = sibling(node_4, 2);
          {
            var consequent_3 = ($$anchor4) => {
              ShareButton($$anchor4, {
                get i18n() {
                  return i18n();
                },
                formatter: async (value2) => {
                  if (!value2) return "";
                  let url = await uploadToHuggingFace(value2);
                  return `<img src="${url}" />`;
                },
                get value() {
                  return value();
                },
                $$events: {
                  share($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  error($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  }
                }
              });
            };
            if_block(node_5, ($$render) => {
              if (deep_read_state(buttons()), untrack(() => buttons() === null ? true : buttons().includes("share"))) $$render(consequent_3);
            });
          }
          append($$anchor3, fragment_3);
        },
        $$slots: { default: true }
      });
      var button = sibling(node_2, 2);
      var div_1 = child(button);
      let classes;
      var node_6 = child(div_1);
      Image$1(node_6, {
        get src() {
          return deep_read_state(value()), untrack(() => value().url);
        },
        restProps: { loading: "lazy", alt: "" },
        $$events: {
          load($$arg) {
            bubble_event.call(this, $$props, $$arg);
          }
        }
      });
      reset(div_1);
      reset(button);
      reset(div);
      bind_this(div, ($$value) => set(image_container, $$value), () => get(image_container));
      template_effect(() => classes = set_class(div_1, 1, "image-frame svelte-12vrxzd", null, classes, { selectable: selectable() }));
      event("click", button, handle_click);
      append($$anchor2, div);
    };
    if_block(node_1, ($$render) => {
      if (deep_read_state(value()), untrack(() => value() == null || !value()?.url)) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
const ImagePreview$1 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: ImagePreview
}, Symbol.toStringTag, { value: "Module" }));
export {
  ImagePreview as I,
  ImagePreview$1 as a,
  get_coordinates_of_clicked_image as g
};
//# sourceMappingURL=nMJBc6y5.js.map
