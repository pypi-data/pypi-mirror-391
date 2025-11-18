import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, i as legacy_pre_effect, u as deep_read_state, j as set, m as mutable_source, k as get, n as legacy_pre_effect_reset, c as from_html, v as first_child, x as derived_safe_equal, s as sibling, d as child, D as comment, y as untrack, b as append, r as reset, t as template_effect, z as event, o as pop, K as tick, J as state, L as proxy, M as user_effect, A as user_derived } from "./DEzry6cj.js";
import { p as prop, i as if_block, b as bind_this, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { I as IconButtonWrapper, b as IconButton, C as Clear, c as bubble_event, a as set_class, p as set_style, F as FileData, j as Image$1, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import { g as get_coordinates_of_clicked_image, I as ImagePreview } from "./nMJBc6y5.js";
import "./BAp-OWo-.js";
import { s as slot } from "./DX-MI-YE.js";
import { i as init } from "./DB0xzveP.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { I as Image } from "./dWqAVU0H.js";
import { S as SelectSource } from "./jPEKutgU.js";
import { F as FullscreenButton } from "./BAYq2deR.js";
import { W as Webcam } from "./BTuysa41.js";
import { U as Upload, a as UploadProgress } from "./BcroWaqq.js";
/* empty css         */
import { E as Empty } from "./B-xg5Dhl.js";
import { U as UploadText } from "./B8mIV0gF.js";
import { default as default2 } from "./MZSzuq-N.js";
var root_3 = from_html(`<!> <!>`, 1);
var root_11 = from_html(`<div><!></div>`);
var root_1 = from_html(`<!> <div data-testid="image" class="image-container svelte-6uxbr3"><!> <div><!> <!></div> <!></div>`, 1);
function ImageUploader($$anchor, $$props) {
  push($$props, false);
  const active_streaming = mutable_source();
  let value = prop($$props, "value", 12, null);
  let label = prop($$props, "label", 8, void 0);
  let show_label = prop($$props, "show_label", 8);
  let sources = prop($$props, "sources", 24, () => ["upload", "clipboard", "webcam"]);
  let streaming = prop($$props, "streaming", 8, false);
  let pending = prop($$props, "pending", 12, false);
  let webcam_options = prop($$props, "webcam_options", 8);
  let selectable = prop($$props, "selectable", 8, false);
  let root = prop($$props, "root", 8);
  let i18n = prop($$props, "i18n", 8);
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let upload = prop($$props, "upload", 8);
  let stream_handler = prop($$props, "stream_handler", 8);
  let stream_every = prop($$props, "stream_every", 8);
  let time_limit = prop($$props, "time_limit", 8);
  let show_fullscreen_button = prop($$props, "show_fullscreen_button", 8, true);
  let stream_state = prop($$props, "stream_state", 8, "closed");
  let upload_promise = prop($$props, "upload_promise", 12, null);
  let upload_input = mutable_source();
  let uploading = prop($$props, "uploading", 12, false);
  let active_source = prop($$props, "active_source", 12, null);
  let fullscreen = prop($$props, "fullscreen", 8, false);
  let files = mutable_source([]);
  let upload_id = mutable_source();
  async function handle_upload({ detail }) {
    if (!streaming()) {
      if (detail.path?.toLowerCase().endsWith(".svg") && detail.url) {
        const response = await fetch(detail.url);
        const svgContent = await response.text();
        value({
          ...detail,
          url: `data:image/svg+xml,${encodeURIComponent(svgContent)}`
        });
      } else {
        value(detail);
      }
      await tick();
      dispatch("upload");
    }
  }
  function handle_clear() {
    value(null);
    dispatch("clear");
    dispatch("change", null);
  }
  function handle_remove_image_click(event2) {
    handle_clear();
    event2.stopPropagation();
  }
  async function handle_save(img_blob, event2) {
    console.log("handle_save", { event: event2, img_blob });
    if (event2 === "stream") {
      dispatch("stream", { value: { url: img_blob }, is_value_data: true });
      return;
    }
    set(upload_id, Math.random().toString(36).substring(2, 15));
    const f_ = new File([img_blob], `image.${streaming() ? "jpeg" : "png"}`);
    set(files, [
      new FileData({
        path: f_.name,
        orig_name: f_.name,
        blob: f_,
        size: f_.size,
        mime_type: f_.type,
        is_stream: false
      })
    ]);
    pending(true);
    const f = await get(upload_input).load_files([f_], get(upload_id));
    console.log("uploaded file", f);
    if (event2 === "change" || event2 === "upload") {
      value(f?.[0] || null);
      await tick();
      dispatch("change");
    }
    pending(false);
  }
  const dispatch = createEventDispatcher();
  let dragging = prop($$props, "dragging", 12, false);
  function handle_click(evt) {
    let coordinates = get_coordinates_of_clicked_image(evt);
    if (coordinates) {
      dispatch("select", { index: coordinates, value: null });
    }
  }
  async function handle_select_source(source) {
    switch (source) {
      case "clipboard":
        get(upload_input).paste_clipboard();
        break;
    }
  }
  let image_container = mutable_source();
  function on_drag_over(evt) {
    evt.preventDefault();
    evt.stopPropagation();
    if (evt.dataTransfer) {
      evt.dataTransfer.dropEffect = "copy";
    }
    dragging(true);
  }
  async function on_drop(evt) {
    evt.preventDefault();
    evt.stopPropagation();
    dragging(false);
    if (value()) {
      handle_clear();
      await tick();
    }
    active_source("upload");
    await tick();
    get(upload_input).load_files_from_drop(evt);
  }
  legacy_pre_effect(
    () => (deep_read_state(active_source()), deep_read_state(sources())),
    () => {
      if (!active_source() && sources()) {
        active_source(sources()[0]);
      }
    }
  );
  legacy_pre_effect(
    () => (deep_read_state(streaming()), deep_read_state(active_source())),
    () => {
      set(active_streaming, streaming() && active_source() === "webcam");
    }
  );
  legacy_pre_effect(() => (deep_read_state(uploading()), get(active_streaming)), () => {
    if (uploading() && !get(active_streaming)) value(null);
  });
  legacy_pre_effect(() => deep_read_state(dragging()), () => {
    dispatch("drag", dragging());
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root_1();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => label() || "Image");
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
  var div = sibling(node, 2);
  var node_1 = child(div);
  IconButtonWrapper(node_1, {
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = comment();
      var node_2 = first_child(fragment_1);
      {
        var consequent_1 = ($$anchor3) => {
          var fragment_2 = root_3();
          var node_3 = first_child(fragment_2);
          {
            var consequent = ($$anchor4) => {
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
              if (show_fullscreen_button()) $$render(consequent);
            });
          }
          var node_4 = sibling(node_3, 2);
          IconButton(node_4, {
            get Icon() {
              return Clear;
            },
            label: "Remove Image",
            $$events: { click: handle_remove_image_click }
          });
          append($$anchor3, fragment_2);
        };
        if_block(node_2, ($$render) => {
          if (deep_read_state(value()), get(active_streaming), untrack(() => value()?.url && !get(active_streaming))) $$render(consequent_1);
        });
      }
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  var div_1 = sibling(node_1, 2);
  let classes;
  let styles;
  var node_5 = child(div_1);
  {
    let $0 = derived_safe_equal(() => value() !== null || active_source() === "webcam");
    let $1 = derived_safe_equal(() => active_source() === "clipboard" ? "clipboard" : "image/*");
    let $2 = derived_safe_equal(() => (deep_read_state(sources()), deep_read_state(value()), untrack(() => !sources().includes("upload") || value() !== null)));
    let $3 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("image.drop_to_upload"))));
    bind_this(
      Upload(node_5, {
        get hidden() {
          return get($0);
        },
        get filetype() {
          return get($1);
        },
        get root() {
          return root();
        },
        get max_file_size() {
          return max_file_size();
        },
        get disable_click() {
          return get($2);
        },
        get upload() {
          return upload();
        },
        get stream_handler() {
          return stream_handler();
        },
        get aria_label() {
          return get($3);
        },
        get upload_promise() {
          return upload_promise();
        },
        set upload_promise($$value) {
          upload_promise($$value);
        },
        get uploading() {
          return uploading();
        },
        set uploading($$value) {
          uploading($$value);
        },
        get dragging() {
          return dragging();
        },
        set dragging($$value) {
          dragging($$value);
        },
        $$events: {
          load: handle_upload,
          error($$arg) {
            bubble_event.call(this, $$props, $$arg);
          }
        },
        children: ($$anchor2, $$slotProps) => {
          var fragment_4 = comment();
          var node_6 = first_child(fragment_4);
          {
            var consequent_2 = ($$anchor3) => {
              var fragment_5 = comment();
              var node_7 = first_child(fragment_5);
              slot(node_7, $$props, "default", {}, null);
              append($$anchor3, fragment_5);
            };
            if_block(node_6, ($$render) => {
              if (value() === null) $$render(consequent_2);
            });
          }
          append($$anchor2, fragment_4);
        },
        $$slots: { default: true },
        $$legacy: true
      }),
      ($$value) => set(upload_input, $$value),
      () => get(upload_input)
    );
  }
  var node_8 = sibling(node_5, 2);
  {
    var consequent_3 = ($$anchor2) => {
      UploadProgress($$anchor2, {
        get root() {
          return root();
        },
        get upload_id() {
          return get(upload_id);
        },
        get stream_handler() {
          return stream_handler();
        },
        get files() {
          return get(files);
        }
      });
    };
    var alternate_1 = ($$anchor2) => {
      var fragment_7 = comment();
      var node_9 = first_child(fragment_7);
      {
        var consequent_4 = ($$anchor3) => {
          Webcam($$anchor3, {
            get root() {
              return root();
            },
            get value() {
              return value();
            },
            get stream_state() {
              return stream_state();
            },
            get mirror_webcam() {
              return deep_read_state(webcam_options()), untrack(() => webcam_options().mirror);
            },
            get stream_every() {
              return stream_every();
            },
            get streaming() {
              return streaming();
            },
            mode: "image",
            include_audio: false,
            get i18n() {
              return i18n();
            },
            get upload() {
              return upload();
            },
            get time_limit() {
              return time_limit();
            },
            get webcam_constraints() {
              return deep_read_state(webcam_options()), untrack(() => webcam_options().constraints);
            },
            $$events: {
              capture: (e) => handle_save(e.detail, "change"),
              stream: (e) => handle_save(e.detail, "stream"),
              error($$arg) {
                bubble_event.call(this, $$props, $$arg);
              },
              drag($$arg) {
                bubble_event.call(this, $$props, $$arg);
              },
              upload: (e) => handle_save(e.detail, "upload"),
              close_stream($$arg) {
                bubble_event.call(this, $$props, $$arg);
              }
            }
          });
        };
        var alternate = ($$anchor3) => {
          var fragment_9 = comment();
          var node_10 = first_child(fragment_9);
          {
            var consequent_5 = ($$anchor4) => {
              var div_2 = root_11();
              let classes_1;
              var node_11 = child(div_2);
              {
                let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => ({ alt: value().alt_text }))));
                Image$1(node_11, {
                  get src() {
                    return deep_read_state(value()), untrack(() => value().url);
                  },
                  get restProps() {
                    return get($0);
                  }
                });
              }
              reset(div_2);
              template_effect(() => classes_1 = set_class(div_2, 1, "image-frame svelte-6uxbr3", null, classes_1, { selectable: selectable() }));
              event("click", div_2, handle_click);
              append($$anchor4, div_2);
            };
            if_block(
              node_10,
              ($$render) => {
                if (value() !== null && !streaming()) $$render(consequent_5);
              },
              true
            );
          }
          append($$anchor3, fragment_9);
        };
        if_block(
          node_9,
          ($$render) => {
            if (active_source() === "webcam" && (streaming() || !streaming() && !value())) $$render(consequent_4);
            else $$render(alternate, false);
          },
          true
        );
      }
      append($$anchor2, fragment_7);
    };
    if_block(node_8, ($$render) => {
      if (active_source() === "webcam" && !streaming() && pending()) $$render(consequent_3);
      else $$render(alternate_1, false);
    });
  }
  reset(div_1);
  var node_12 = sibling(div_1, 2);
  {
    var consequent_6 = ($$anchor2) => {
      SelectSource($$anchor2, {
        get sources() {
          return sources();
        },
        handle_clear,
        handle_select: handle_select_source,
        get active_source() {
          return active_source();
        },
        set active_source($$value) {
          active_source($$value);
        },
        $$legacy: true
      });
    };
    if_block(node_12, ($$render) => {
      if (deep_read_state(sources()), untrack(() => sources().length > 1 || sources().includes("clipboard"))) $$render(consequent_6);
    });
  }
  reset(div);
  bind_this(div, ($$value) => set(image_container, $$value), () => get(image_container));
  template_effect(() => {
    classes = set_class(div_1, 1, "upload-container svelte-6uxbr3", null, classes, { "reduced-height": sources().length > 1 });
    styles = set_style(div_1, "", styles, { width: value() ? "auto" : "100%" });
  });
  event("dragover", div_1, on_drag_over);
  event("drop", div_1, on_drop);
  append($$anchor, fragment);
  pop();
}
var root_2 = from_html(`<!> <!>`, 1);
var root_4 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let stream_data = { value: null };
  let upload_promise = state(void 0);
  class ImageGradio extends Gradio {
    async get_data() {
      if (get(upload_promise)) {
        await get(upload_promise);
        await tick();
      }
      const data = await super.get_data();
      if ($$props.props.streaming) {
        data.value = stream_data.value;
      }
      return data;
    }
  }
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new ImageGradio(props);
  let fullscreen = state(false);
  let dragging = state(false);
  let active_source = user_derived(() => gradio.props.sources ? gradio.props.sources[0] : null);
  let upload_component;
  const handle_drag_event = (event2) => {
    const drag_event = event2;
    drag_event.preventDefault();
    drag_event.stopPropagation();
    if (drag_event.type === "dragenter" || drag_event.type === "dragover") {
      set(dragging, true);
    } else if (drag_event.type === "dragleave") {
      set(dragging, false);
    }
  };
  const handle_drop = (event2) => {
    if (gradio.shared.interactive) {
      const drop_event = event2;
      drop_event.preventDefault();
      drop_event.stopPropagation();
      set(dragging, false);
      if (upload_component) {
        upload_component.loadFilesFromDrop(drop_event);
      }
    }
  };
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  let status = user_derived(() => gradio?.shared?.loading_status.stream_state);
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      {
        let $0 = user_derived(() => get(dragging) ? "focus" : "base");
        let $1 = user_derived(() => gradio.props.height || void 0);
        Block($$anchor2, {
          get visible() {
            return gradio.shared.visible;
          },
          variant: "solid",
          get border_mode() {
            return get($0);
          },
          padding: false,
          get elem_id() {
            return gradio.shared.elem_id;
          },
          get elem_classes() {
            return gradio.shared.elem_classes;
          },
          get height() {
            return get($1);
          },
          get width() {
            return gradio.props.width;
          },
          allow_overflow: false,
          get container() {
            return gradio.shared.container;
          },
          "scale{gradio.shared.scale}": true,
          get min_width() {
            return gradio.shared.min_width;
          },
          get fullscreen() {
            return get(fullscreen);
          },
          set fullscreen($$value) {
            set(fullscreen, $$value, true);
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
              () => gradio.shared.loading_status
            ));
            var node_2 = sibling(node_1, 2);
            ImagePreview(node_2, {
              get fullscreen() {
                return get(fullscreen);
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
              get selectable() {
                return gradio.props._selectable;
              },
              get i18n() {
                return gradio.i18n;
              },
              get buttons() {
                return gradio.props.buttons;
              },
              $$events: {
                select: ({ detail }) => gradio.dispatch("select", detail),
                share: ({ detail }) => gradio.dispatch("share", detail),
                error: ({ detail }) => gradio.dispatch("error", detail),
                fullscreen: ({ detail }) => {
                  set(fullscreen, detail, true);
                }
              }
            });
            append($$anchor3, fragment_2);
          },
          $$slots: { default: true }
        });
      }
    };
    var alternate_2 = ($$anchor2) => {
      {
        let $0 = user_derived(() => gradio.props.value === null ? "dashed" : "solid");
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
          $$events: {
            dragenter: handle_drag_event,
            dragleave: handle_drag_event,
            dragover: handle_drag_event,
            drop: handle_drop
          },
          children: ($$anchor3, $$slotProps) => {
            var fragment_4 = root_4();
            var node_3 = first_child(fragment_4);
            {
              var consequent_1 = ($$anchor4) => {
                Static($$anchor4, spread_props(
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
              };
              if_block(node_3, ($$render) => {
                if (gradio.shared.loading_status.type === "output") $$render(consequent_1);
              });
            }
            var node_4 = sibling(node_3, 2);
            {
              let $02 = user_derived(() => gradio.props.buttons === null ? true : gradio.props.buttons.includes("fullscreen"));
              let $12 = user_derived(() => gradio.shared.loading_status?.status === "pending" || gradio.shared.loading_status?.status === "streaming");
              let $22 = user_derived(() => gradio.shared.loading_status?.time_limit);
              let $3 = user_derived(() => gradio.shared.client?.stream);
              bind_this(
                ImageUploader(node_4, {
                  get selectable() {
                    return gradio.props._selectable;
                  },
                  get root() {
                    return gradio.shared.root;
                  },
                  get sources() {
                    return gradio.props.sources;
                  },
                  get fullscreen() {
                    return get(fullscreen);
                  },
                  get show_fullscreen_button() {
                    return get($02);
                  },
                  get label() {
                    return gradio.shared.label;
                  },
                  get show_label() {
                    return gradio.shared.show_label;
                  },
                  get pending() {
                    return get($12);
                  },
                  get streaming() {
                    return gradio.props.streaming;
                  },
                  get webcam_options() {
                    return gradio.props.webcam_options;
                  },
                  get stream_every() {
                    return gradio.props.stream_every;
                  },
                  get time_limit() {
                    return get($22);
                  },
                  get max_file_size() {
                    return gradio.shared.max_file_size;
                  },
                  get i18n() {
                    return gradio.i18n;
                  },
                  upload: (...args) => gradio.shared.client.upload(...args),
                  get stream_handler() {
                    return get($3);
                  },
                  get stream_state() {
                    return get(status);
                  },
                  get upload_promise() {
                    return get(upload_promise);
                  },
                  set upload_promise($$value) {
                    set(upload_promise, $$value, true);
                  },
                  get active_source() {
                    return get(active_source);
                  },
                  set active_source($$value) {
                    set(active_source, $$value);
                  },
                  get value() {
                    return gradio.props.value;
                  },
                  set value($$value) {
                    gradio.props.value = $$value;
                  },
                  get dragging() {
                    return get(dragging);
                  },
                  set dragging($$value) {
                    set(dragging, $$value, true);
                  },
                  $$events: {
                    edit: () => gradio.dispatch("edit"),
                    clear: () => {
                      set(fullscreen, false);
                      gradio.dispatch("clear");
                      gradio.dispatch("input");
                    },
                    stream: ({ detail }) => {
                      stream_data = detail;
                      gradio.dispatch("stream", detail);
                    },
                    drag: ({ detail }) => set(dragging, detail, true),
                    upload: () => {
                      gradio.dispatch("upload");
                      gradio.dispatch("input");
                    },
                    select: ({ detail }) => gradio.dispatch("select", detail),
                    share: ({ detail }) => gradio.dispatch("share", detail),
                    error: ({ detail }) => {
                      gradio.shared.loading_status.status = "error";
                      gradio.dispatch("error", detail);
                    },
                    close_stream: () => {
                      gradio.dispatch("close_stream");
                    },
                    fullscreen: ({ detail }) => {
                      set(fullscreen, detail, true);
                    }
                  },
                  children: ($$anchor4, $$slotProps2) => {
                    var fragment_6 = comment();
                    var node_5 = first_child(fragment_6);
                    {
                      var consequent_2 = ($$anchor5) => {
                        UploadText($$anchor5, {
                          get i18n() {
                            return gradio.i18n;
                          },
                          type: "image",
                          get placeholder() {
                            return gradio.props.placeholder;
                          }
                        });
                      };
                      var alternate_1 = ($$anchor5) => {
                        var fragment_8 = comment();
                        var node_6 = first_child(fragment_8);
                        {
                          var consequent_3 = ($$anchor6) => {
                            UploadText($$anchor6, {
                              get i18n() {
                                return gradio.i18n;
                              },
                              type: "clipboard",
                              mode: "short"
                            });
                          };
                          var alternate = ($$anchor6) => {
                            Empty($$anchor6, {
                              unpadded_box: true,
                              size: "large",
                              children: ($$anchor7, $$slotProps3) => {
                                Image($$anchor7);
                              },
                              $$slots: { default: true }
                            });
                          };
                          if_block(
                            node_6,
                            ($$render) => {
                              if (get(active_source) === "clipboard") $$render(consequent_3);
                              else $$render(alternate, false);
                            },
                            true
                          );
                        }
                        append($$anchor5, fragment_8);
                      };
                      if_block(node_5, ($$render) => {
                        if (get(active_source) === "upload" || !get(active_source)) $$render(consequent_2);
                        else $$render(alternate_1, false);
                      });
                    }
                    append($$anchor4, fragment_6);
                  },
                  $$slots: { default: true }
                }),
                ($$value) => upload_component = $$value,
                () => upload_component
              );
            }
            append($$anchor3, fragment_4);
          },
          $$slots: { default: true }
        });
      }
    };
    if_block(node, ($$render) => {
      if (!gradio.shared.interactive) $$render(consequent);
      else $$render(alternate_2, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  default2 as BaseExample,
  Image$1 as BaseImage,
  ImageUploader as BaseImageUploader,
  ImagePreview as BaseStaticImage,
  Webcam,
  Index as default
};
//# sourceMappingURL=BsPel4GV.js.map
