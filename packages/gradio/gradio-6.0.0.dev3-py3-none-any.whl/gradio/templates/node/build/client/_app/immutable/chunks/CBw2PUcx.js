import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, m as mutable_source, I as onMount, i as legacy_pre_effect, j as set, k as get, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, v as first_child, s as sibling, y as untrack, b as append, o as pop, K as tick, x as derived_safe_equal, d as child, r as reset, t as template_effect, Y as mutate, z as event, D as comment, g as set_text } from "./DEzry6cj.js";
import { p as prop, i as if_block, b as bind_this } from "./DUftb7my.js";
import { u as uploadToHuggingFace, t as each, v as index, I as IconButtonWrapper, b as IconButton, c as bubble_event, C as Clear, a as set_class, s as set_attribute, j as Image$1, p as set_style, O as stopPropagation } from "./DXi4jxVF.js";
import { b as bind_window_size } from "./Braj6aVO.js";
import { i as init } from "./DB0xzveP.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { E as Empty } from "./B-xg5Dhl.js";
import { S as ShareButton } from "./D6EAw2Po.js";
import { D as Download } from "./rkplYKOt.js";
import { I as Image } from "./dWqAVU0H.js";
import { P as Play } from "./L86yoUex.js";
import { U as Upload$1 } from "./m2At3saq.js";
import { F as FullscreenButton } from "./BAYq2deR.js";
import { U as Upload } from "./BcroWaqq.js";
import { M as ModifyUpload } from "./BXBtG43Y.js";
/* empty css         */
import { V as Video } from "./Br4zzvQm.js";
import { d as dequal } from "./ShnGN6OY.js";
async function format_gallery_for_sharing(value) {
  if (!value) return "";
  let urls = await Promise.all(
    value.map(async ([image, _]) => {
      if (image === null || !image.url) return "";
      return await uploadToHuggingFace(image.url);
    })
  );
  return `<div style="display: flex; flex-wrap: wrap; gap: 16px">${urls.map((url) => `<img src="${url}" style="height: 400px" />`).join("")}</div>`;
}
var root_10 = from_html(`<div class="icon-button"><!></div>`);
var root_7 = from_html(`<!> <!> <!> <!>`, 1);
var root_14 = from_html(`<caption class="caption svelte-7anmrz"> </caption>`);
var root_17 = from_html(`<!> <!>`, 1);
var root_15 = from_html(`<button><!></button>`);
var root_6 = from_html(`<span><!> <button class="media-button svelte-7anmrz" aria-label="detailed view of selected image"><!></button> <!> <div class="thumbnails scroll-hide svelte-7anmrz" data-testid="container_el"></div></span>`);
var root_24 = from_html(`<!> <!>`, 1);
var root_25 = from_html(`<div class="caption-label svelte-7anmrz"> </div>`);
var root_26 = from_html(`<button class="delete-button svelte-7anmrz" aria-label="Delete image"><!></button>`);
var root_22 = from_html(`<div class="gallery-item svelte-7anmrz"><button><!> <!></button> <!></div>`);
var root_5 = from_html(`<div class="gallery-container"><!> <div><!> <div></div></div></div>`);
var root_1 = from_html(`<!> <!>`, 1);
function Gallery($$anchor, $$props) {
  push($$props, false);
  const previous = mutable_source();
  const next = mutable_source();
  const selected_media = mutable_source();
  let show_label = prop($$props, "show_label", 8, true);
  let label = prop($$props, "label", 8);
  let value = prop($$props, "value", 12, null);
  let columns = prop($$props, "columns", 24, () => [2]);
  let rows = prop($$props, "rows", 8, void 0);
  let height = prop($$props, "height", 8, "auto");
  let preview = prop($$props, "preview", 8);
  let allow_preview = prop($$props, "allow_preview", 8, true);
  let object_fit = prop($$props, "object_fit", 8, "cover");
  let show_share_button = prop($$props, "show_share_button", 8, false);
  let show_download_button = prop($$props, "show_download_button", 8, false);
  let i18n = prop($$props, "i18n", 8);
  let selected_index = prop($$props, "selected_index", 12, null);
  let interactive = prop($$props, "interactive", 8);
  let _fetch = prop($$props, "_fetch", 8);
  let mode = prop($$props, "mode", 8, "normal");
  let show_fullscreen_button = prop($$props, "show_fullscreen_button", 8, true);
  let display_icon_button_wrapper_top_corner = prop($$props, "display_icon_button_wrapper_top_corner", 8, false);
  let fullscreen = prop($$props, "fullscreen", 8, false);
  let root = prop($$props, "root", 8, "");
  let file_types = prop($$props, "file_types", 24, () => ["image", "video"]);
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let upload = prop($$props, "upload", 8, void 0);
  let stream_handler = prop($$props, "stream_handler", 8, void 0);
  let fit_columns = prop($$props, "fit_columns", 8, true);
  let upload_promise = prop($$props, "upload_promise", 12, null);
  let is_full_screen = mutable_source(false);
  let image_container = mutable_source();
  const dispatch = createEventDispatcher();
  let was_reset = mutable_source(true);
  let resolved_value = mutable_source(null);
  let effective_columns = mutable_source(columns());
  let prev_value = mutable_source(value());
  if (selected_index() == null && preview() && value()?.length) {
    selected_index(0);
  }
  let old_selected_index = mutable_source(selected_index());
  function handle_preview_click(event2) {
    const element = event2.target;
    const x = event2.offsetX;
    const width = element.offsetWidth;
    const centerX = width / 2;
    if (x < centerX) {
      selected_index(get(previous));
    } else {
      selected_index(get(next));
    }
  }
  function on_keydown(e) {
    switch (e.code) {
      case "Escape":
        e.preventDefault();
        selected_index(null);
        break;
      case "ArrowLeft":
        e.preventDefault();
        selected_index(get(previous));
        break;
      case "ArrowRight":
        e.preventDefault();
        selected_index(get(next));
        break;
    }
  }
  let el = mutable_source([]);
  let container_element = mutable_source();
  async function scroll_to_img(index2) {
    if (typeof index2 !== "number") return;
    await tick();
    if (get(el)[index2] === void 0) return;
    get(el)[index2]?.focus();
    const { left: container_left, width: container_width } = get(container_element).getBoundingClientRect();
    const { left, width } = get(el)[index2].getBoundingClientRect();
    const relative_left = left - container_left;
    const pos = relative_left + width / 2 - container_width / 2 + get(container_element).scrollLeft;
    if (get(container_element) && typeof get(container_element).scrollTo === "function") {
      get(container_element).scrollTo({ left: pos < 0 ? 0 : pos, behavior: "smooth" });
    }
  }
  let window_height = mutable_source(0);
  async function download(file_url, name) {
    let response;
    try {
      response = await _fetch()(file_url);
    } catch (error) {
      if (error instanceof TypeError) {
        window.open(file_url, "_blank", "noreferrer");
        return;
      }
      throw error;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    link.click();
    URL.revokeObjectURL(url);
  }
  let thumbnails_overflow = mutable_source(false);
  function check_thumbnails_overflow() {
    if (get(container_element)) {
      set(thumbnails_overflow, get(container_element).scrollWidth > get(container_element).clientWidth);
    }
  }
  onMount(() => {
    check_thumbnails_overflow();
    document.addEventListener("fullscreenchange", () => {
      set(is_full_screen, !!document.fullscreenElement);
    });
    window.addEventListener("resize", check_thumbnails_overflow);
    return () => window.removeEventListener("resize", check_thumbnails_overflow);
  });
  function handle_item_delete(index2) {
    if (!value() || !get(resolved_value)) return;
    const deleted_item = get(resolved_value)[index2];
    let deleted_file_data;
    if ("image" in deleted_item) {
      deleted_file_data = { file: deleted_item.image, index: index2 };
    } else if ("video" in deleted_item) {
      deleted_file_data = { file: deleted_item.video, index: index2 };
    }
    if (deleted_file_data) {
      dispatch("delete", deleted_file_data);
    }
  }
  let uploading = mutable_source(false);
  legacy_pre_effect(() => (get(was_reset), deep_read_state(value())), () => {
    set(was_reset, value() == null || value().length === 0 ? true : get(was_reset));
  });
  legacy_pre_effect(() => deep_read_state(value()), () => {
    set(resolved_value, value() == null ? null : value().map((data) => {
      if ("video" in data) {
        return { video: data.video, caption: data.caption };
      } else if ("image" in data) {
        return { image: data.image, caption: data.caption };
      }
      return {};
    }));
  });
  legacy_pre_effect(
    () => (get(resolved_value), deep_read_state(columns()), deep_read_state(fit_columns())),
    () => {
      if (get(resolved_value) && columns() && fit_columns()) {
        const item_count = get(resolved_value).length;
        if (Array.isArray(columns())) {
          set(effective_columns, columns().map((col) => Math.min(col, item_count)));
        } else {
          set(effective_columns, Math.min(columns(), item_count));
        }
      } else {
        set(effective_columns, columns());
      }
    }
  );
  legacy_pre_effect(
    () => (get(prev_value), deep_read_state(value()), get(was_reset), deep_read_state(selected_index()), deep_read_state(preview())),
    () => {
      if (!dequal(get(prev_value), value())) {
        if (get(was_reset)) {
          selected_index(preview() && value()?.length ? 0 : null);
          set(was_reset, false);
        } else {
          if (selected_index() !== null && value() !== null) {
            selected_index(Math.max(0, Math.min(selected_index(), value().length - 1)));
          } else {
            selected_index(null);
          }
        }
        dispatch("change");
        set(prev_value, value());
      }
    }
  );
  legacy_pre_effect(
    () => (deep_read_state(selected_index()), get(old_selected_index), get(resolved_value)),
    () => {
      if (selected_index() !== get(old_selected_index)) {
        set(old_selected_index, selected_index());
        if (selected_index() !== null) {
          if (get(resolved_value) != null) {
            selected_index(Math.max(0, Math.min(selected_index(), get(resolved_value).length - 1)));
          }
          dispatch("select", {
            index: selected_index(),
            value: get(resolved_value)?.[selected_index()]
          });
        }
      }
    }
  );
  legacy_pre_effect(() => (deep_read_state(selected_index()), get(resolved_value)), () => {
    set(previous, ((selected_index() ?? 0) + (get(resolved_value)?.length ?? 0) - 1) % (get(resolved_value)?.length ?? 0));
  });
  legacy_pre_effect(() => (deep_read_state(selected_index()), get(resolved_value)), () => {
    set(next, ((selected_index() ?? 0) + 1) % (get(resolved_value)?.length ?? 0));
  });
  legacy_pre_effect(
    () => (deep_read_state(allow_preview()), deep_read_state(selected_index())),
    () => {
      if (allow_preview()) {
        scroll_to_img(selected_index());
      }
    }
  );
  legacy_pre_effect(() => (deep_read_state(selected_index()), get(resolved_value)), () => {
    set(selected_media, selected_index() != null && get(resolved_value) != null ? get(resolved_value)[selected_index()] : null);
  });
  legacy_pre_effect(() => get(resolved_value), () => {
    get(resolved_value), check_thumbnails_overflow();
  });
  legacy_pre_effect(() => get(container_element), () => {
    if (get(container_element)) {
      check_thumbnails_overflow();
    }
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root_1();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      {
        let $0 = derived_safe_equal(() => label() || "Gallery");
        BlockLabel($$anchor2, {
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
    };
    if_block(node, ($$render) => {
      if (show_label()) $$render(consequent);
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent_1 = ($$anchor2) => {
      Empty($$anchor2, {
        unpadded_box: true,
        size: "large",
        children: ($$anchor3, $$slotProps) => {
          Image($$anchor3);
        },
        $$slots: { default: true }
      });
    };
    var alternate_3 = ($$anchor2) => {
      var div = root_5();
      var node_2 = child(div);
      {
        var consequent_9 = ($$anchor3) => {
          var span = root_6();
          let classes;
          var node_3 = child(span);
          IconButtonWrapper(node_3, {
            get display_top_corner() {
              return display_icon_button_wrapper_top_corner();
            },
            children: ($$anchor4, $$slotProps) => {
              var fragment_4 = root_7();
              var node_4 = first_child(fragment_4);
              {
                var consequent_2 = ($$anchor5) => {
                  {
                    let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.download"))));
                    IconButton($$anchor5, {
                      get Icon() {
                        return Download;
                      },
                      get label() {
                        return get($0);
                      },
                      $$events: {
                        click: () => {
                          const image = "image" in get(selected_media) ? get(selected_media)?.image : get(selected_media)?.video;
                          if (image == null) {
                            return;
                          }
                          const { url, orig_name } = image;
                          if (url) {
                            download(url, orig_name ?? "image");
                          }
                        }
                      }
                    });
                  }
                };
                if_block(node_4, ($$render) => {
                  if (show_download_button()) $$render(consequent_2);
                });
              }
              var node_5 = sibling(node_4, 2);
              {
                var consequent_3 = ($$anchor5) => {
                  FullscreenButton($$anchor5, {
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
                if_block(node_5, ($$render) => {
                  if (show_fullscreen_button()) $$render(consequent_3);
                });
              }
              var node_6 = sibling(node_5, 2);
              {
                var consequent_4 = ($$anchor5) => {
                  var div_1 = root_10();
                  var node_7 = child(div_1);
                  ShareButton(node_7, {
                    get i18n() {
                      return i18n();
                    },
                    get value() {
                      return get(resolved_value);
                    },
                    get formatter() {
                      return format_gallery_for_sharing;
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
                  reset(div_1);
                  append($$anchor5, div_1);
                };
                if_block(node_6, ($$render) => {
                  if (show_share_button()) $$render(consequent_4);
                });
              }
              var node_8 = sibling(node_6, 2);
              {
                var consequent_5 = ($$anchor5) => {
                  IconButton($$anchor5, {
                    get Icon() {
                      return Clear;
                    },
                    label: "Close",
                    $$events: {
                      click: () => {
                        selected_index(null);
                        dispatch("preview_close");
                      }
                    }
                  });
                };
                if_block(node_8, ($$render) => {
                  if (!get(is_full_screen)) $$render(consequent_5);
                });
              }
              append($$anchor4, fragment_4);
            },
            $$slots: { default: true }
          });
          var button = sibling(node_3, 2);
          var node_9 = child(button);
          {
            var consequent_6 = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => (get(selected_media), untrack(() => ({
                  alt: get(selected_media).caption || "",
                  title: get(selected_media).caption || null,
                  class: get(selected_media).caption && "with-caption",
                  loading: "lazy"
                }))));
                Image$1($$anchor4, {
                  get restProps() {
                    return get($0);
                  },
                  get src() {
                    return get(selected_media), untrack(() => get(selected_media).image.url);
                  },
                  data_testid: "detailed-image"
                });
              }
            };
            var alternate = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => (get(selected_media), untrack(() => get(selected_media).caption || "")));
                Video($$anchor4, {
                  get src() {
                    return get(selected_media), untrack(() => get(selected_media).video.url);
                  },
                  "data-testid": "detailed-video",
                  get alt() {
                    return get($0);
                  },
                  loading: "lazy",
                  loop: false,
                  is_stream: false,
                  muted: false,
                  controls: true
                });
              }
            };
            if_block(node_9, ($$render) => {
              if ("image" in get(selected_media)) $$render(consequent_6);
              else $$render(alternate, false);
            });
          }
          reset(button);
          var node_10 = sibling(button, 2);
          {
            var consequent_7 = ($$anchor4) => {
              var caption = root_14();
              var text = child(caption, true);
              reset(caption);
              template_effect(() => set_text(text, (get(selected_media), untrack(() => get(selected_media).caption))));
              append($$anchor4, caption);
            };
            if_block(node_10, ($$render) => {
              if (get(selected_media), untrack(() => get(selected_media)?.caption)) $$render(consequent_7);
            });
          }
          var div_2 = sibling(node_10, 2);
          each(div_2, 5, () => get(resolved_value), index, ($$anchor4, media, i) => {
            var button_1 = root_15();
            let classes_1;
            var node_11 = child(button_1);
            {
              var consequent_8 = ($$anchor5) => {
                {
                  let $0 = derived_safe_equal(() => (get(media), untrack(() => ({
                    title: get(media).caption || null,
                    alt: "",
                    class: "with-caption",
                    loading: "lazy"
                  }))));
                  Image$1($$anchor5, {
                    get src() {
                      return get(media), untrack(() => get(media).image.url);
                    },
                    get restProps() {
                      return get($0);
                    },
                    data_testid: `thumbnail ${i + 1}`
                  });
                }
              };
              var alternate_1 = ($$anchor5) => {
                var fragment_11 = root_17();
                var node_12 = first_child(fragment_11);
                Play(node_12);
                var node_13 = sibling(node_12, 2);
                {
                  let $0 = derived_safe_equal(() => (get(media), untrack(() => get(media).caption || null)));
                  Video(node_13, {
                    get src() {
                      return get(media), untrack(() => get(media).video.url);
                    },
                    get title() {
                      return get($0);
                    },
                    is_stream: false,
                    "data-testid": "thumbnail " + (i + 1),
                    alt: "",
                    loading: "lazy",
                    loop: false
                  });
                }
                append($$anchor5, fragment_11);
              };
              if_block(node_11, ($$render) => {
                if ("image" in get(media)) $$render(consequent_8);
                else $$render(alternate_1, false);
              });
            }
            reset(button_1);
            bind_this(button_1, ($$value, i2) => mutate(el, get(el)[i2] = $$value), (i2) => get(el)?.[i2], () => [i]);
            template_effect(() => {
              classes_1 = set_class(button_1, 1, "thumbnail-item thumbnail-small svelte-7anmrz", null, classes_1, { selected: selected_index() === i && mode() !== "minimal" });
              set_attribute(button_1, "aria-label", (get(resolved_value), untrack(() => "Thumbnail " + (i + 1) + " of " + get(resolved_value).length)));
            });
            event("click", button_1, () => selected_index(i));
            append($$anchor4, button_1);
          });
          reset(div_2);
          bind_this(div_2, ($$value) => set(container_element, $$value), () => get(container_element));
          reset(span);
          template_effect(() => {
            classes = set_class(span, 1, "preview svelte-7anmrz", null, classes, { minimal: mode() === "minimal" });
            set_style(button, `height: calc(100% - ${(get(selected_media), untrack(() => get(selected_media).caption ? "80px" : "60px")) ?? ""})`);
            set_style(div_2, `justify-content: ${get(thumbnails_overflow) ? "flex-start" : "center"};`);
          });
          event("click", button, function(...$$args) {
            ("image" in get(selected_media) ? (event2) => handle_preview_click(event2) : null)?.apply(this, $$args);
          });
          event("keydown", span, on_keydown);
          append($$anchor3, span);
        };
        if_block(node_2, ($$render) => {
          if (get(selected_media) && allow_preview()) $$render(consequent_9);
        });
      }
      var div_3 = sibling(node_2, 2);
      let classes_2;
      let styles;
      var node_14 = child(div_3);
      {
        var consequent_11 = ($$anchor3) => {
          ModifyUpload($$anchor3, {
            get i18n() {
              return i18n();
            },
            $$events: {
              clear: () => {
                value([]);
                dispatch("clear");
              }
            },
            children: ($$anchor4, $$slotProps) => {
              var fragment_13 = comment();
              var node_15 = first_child(fragment_13);
              {
                var consequent_10 = ($$anchor5) => {
                  {
                    let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.upload"))));
                    IconButton($$anchor5, {
                      get Icon() {
                        return Upload$1;
                      },
                      get label() {
                        return get($0);
                      },
                      children: ($$anchor6, $$slotProps2) => {
                        Upload($$anchor6, {
                          icon_upload: true,
                          get filetype() {
                            return file_types();
                          },
                          file_count: "multiple",
                          get max_file_size() {
                            return max_file_size();
                          },
                          get root() {
                            return root();
                          },
                          get stream_handler() {
                            return stream_handler();
                          },
                          get upload() {
                            return upload();
                          },
                          get upload_promise() {
                            return upload_promise();
                          },
                          set upload_promise($$value) {
                            upload_promise($$value);
                          },
                          get uploading() {
                            return get(uploading);
                          },
                          set uploading($$value) {
                            set(uploading, $$value);
                          },
                          $$events: {
                            load: (e) => dispatch("upload", e.detail),
                            error: (e) => dispatch("error", e.detail)
                          },
                          $$legacy: true
                        });
                      },
                      $$slots: { default: true }
                    });
                  }
                };
                if_block(node_15, ($$render) => {
                  if (upload() && stream_handler()) $$render(consequent_10);
                });
              }
              append($$anchor4, fragment_13);
            },
            $$slots: { default: true }
          });
        };
        if_block(node_14, ($$render) => {
          if (interactive() && selected_index() === null) $$render(consequent_11);
        });
      }
      var div_4 = sibling(node_14, 2);
      let classes_3;
      each(div_4, 5, () => get(resolved_value), index, ($$anchor3, entry, i) => {
        var div_5 = root_22();
        var button_2 = child(div_5);
        let classes_4;
        var node_16 = child(button_2);
        {
          var consequent_12 = ($$anchor4) => {
            {
              let $0 = derived_safe_equal(() => (get(entry), untrack(() => get(entry).caption || "")));
              let $1 = derived_safe_equal(() => (get(entry), untrack(() => typeof get(entry).image === "string" ? get(entry).image : get(entry).image.url)));
              Image$1($$anchor4, {
                get alt() {
                  return get($0);
                },
                get src() {
                  return get($1);
                },
                loading: "lazy"
              });
            }
          };
          var alternate_2 = ($$anchor4) => {
            var fragment_17 = root_24();
            var node_17 = first_child(fragment_17);
            Play(node_17);
            var node_18 = sibling(node_17, 2);
            {
              let $0 = derived_safe_equal(() => (get(entry), untrack(() => get(entry).caption || null)));
              Video(node_18, {
                get src() {
                  return get(entry), untrack(() => get(entry).video.url);
                },
                get title() {
                  return get($0);
                },
                is_stream: false,
                "data-testid": "thumbnail " + (i + 1),
                alt: "",
                loading: "lazy",
                loop: false
              });
            }
            append($$anchor4, fragment_17);
          };
          if_block(node_16, ($$render) => {
            if ("image" in get(entry)) $$render(consequent_12);
            else $$render(alternate_2, false);
          });
        }
        var node_19 = sibling(node_16, 2);
        {
          var consequent_13 = ($$anchor4) => {
            var div_6 = root_25();
            var text_1 = child(div_6, true);
            reset(div_6);
            template_effect(() => set_text(text_1, (get(entry), untrack(() => get(entry).caption))));
            append($$anchor4, div_6);
          };
          if_block(node_19, ($$render) => {
            if (get(entry), untrack(() => get(entry).caption)) $$render(consequent_13);
          });
        }
        reset(button_2);
        var node_20 = sibling(button_2, 2);
        {
          var consequent_14 = ($$anchor4) => {
            var button_3 = root_26();
            var node_21 = child(button_3);
            Clear(node_21);
            reset(button_3);
            event("click", button_3, stopPropagation(() => handle_item_delete(i)));
            append($$anchor4, button_3);
          };
          if_block(node_20, ($$render) => {
            if (interactive()) $$render(consequent_14);
          });
        }
        reset(div_5);
        template_effect(() => {
          classes_4 = set_class(button_2, 1, "thumbnail-item thumbnail-lg svelte-7anmrz", null, classes_4, { selected: selected_index() === i });
          set_attribute(button_2, "aria-label", (get(resolved_value), untrack(() => "Thumbnail " + (i + 1) + " of " + get(resolved_value).length)));
        });
        event("click", button_2, () => {
          if (selected_index() === null && allow_preview()) {
            dispatch("preview_open");
          }
          selected_index(i);
        });
        append($$anchor3, div_5);
      });
      reset(div_4);
      reset(div_3);
      reset(div);
      bind_this(div, ($$value) => set(image_container, $$value), () => get(image_container));
      template_effect(() => {
        classes_2 = set_class(div_3, 1, "grid-wrap svelte-7anmrz", null, classes_2, {
          minimal: mode() === "minimal",
          "fixed-height": mode() !== "minimal" && (!height() || height() == "auto"),
          hidden: get(is_full_screen)
        });
        styles = set_style(div_3, "", styles, { height: height() !== "auto" ? height() + "px" : null });
        classes_3 = set_class(div_4, 1, "grid-container svelte-7anmrz", null, classes_3, { "pt-6": show_label() });
        set_style(div_4, `--grid-cols:${get(effective_columns) ?? ""}; --grid-rows:${rows() ?? ""}; --object-fit: ${object_fit() ?? ""};`);
      });
      append($$anchor2, div);
    };
    if_block(node_1, ($$render) => {
      if (deep_read_state(value()), get(resolved_value), untrack(() => value() == null || get(resolved_value) == null || get(resolved_value).length === 0)) $$render(consequent_1);
      else $$render(alternate_3, false);
    });
  }
  bind_window_size("innerHeight", ($$value) => set(window_height, $$value));
  append($$anchor, fragment);
  pop();
}
export {
  Gallery as default
};
//# sourceMappingURL=CBw2PUcx.js.map
