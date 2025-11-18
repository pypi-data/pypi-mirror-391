import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, r as reset, t as template_effect, b as append, o as pop, k as get, y as untrack, s as sibling, g as set_text, z as event, v as first_child, E as next, x as derived_safe_equal, F as text, D as comment, K as tick } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { s as slot } from "./DX-MI-YE.js";
import { i as init } from "./DB0xzveP.js";
import { t as each, a as set_class, s as set_attribute, N as preventDefault, c as bubble_event, D as html, p as set_style, I as IconButtonWrapper, b as IconButton, C as Clear } from "./DXi4jxVF.js";
import { U as Upload } from "./BcroWaqq.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { F as File } from "./bc1v6JFX.js";
import { U as Upload$1 } from "./m2At3saq.js";
/* empty css         */
import { D as DownloadLink } from "./BFO3TfnI.js";
const prettyBytes = (bytes) => {
  let units = ["B", "KB", "MB", "GB", "PB"];
  let i = 0;
  while (bytes > 1024) {
    bytes /= 1024;
    i++;
  }
  let unit = units[i];
  return bytes.toFixed(1) + "&nbsp;" + unit;
};
var root_2$1 = from_html(`<span class="drag-handle svelte-al0bnp">⋮⋮</span>`);
var root_4 = from_html(`<!>&nbsp;&#8675;`, 1);
var root_6 = from_html(`<td class="svelte-al0bnp"><button class="label-clear-button svelte-al0bnp" aria-label="Remove this file">×</button></td>`);
var root_1$1 = from_html(`<tr><td class="filename svelte-al0bnp"><!> <span class="stem svelte-al0bnp"> </span> <span class="ext svelte-al0bnp"> </span></td><td class="download svelte-al0bnp"><!></td><!></tr>`);
var root = from_html(`<div class="file-preview-holder svelte-al0bnp"><table class="file-preview svelte-al0bnp"><tbody class="svelte-al0bnp"></tbody></table></div>`);
function FilePreview($$anchor, $$props) {
  push($$props, false);
  const normalized_files = mutable_source();
  const dispatch = createEventDispatcher();
  let value = prop($$props, "value", 12);
  let selectable = prop($$props, "selectable", 8, false);
  let height = prop($$props, "height", 8, void 0);
  let i18n = prop($$props, "i18n", 8);
  let allow_reordering = prop($$props, "allow_reordering", 8, false);
  let dragging_index = mutable_source(null);
  let drop_target_index = mutable_source(null);
  function handle_drag_start(event2, index) {
    set(dragging_index, index);
    if (event2.dataTransfer) {
      event2.dataTransfer.effectAllowed = "move";
      event2.dataTransfer.setData("text/plain", index.toString());
    }
  }
  function handle_drag_over(event2, index) {
    event2.preventDefault();
    if (index === get(normalized_files).length - 1) {
      const rect = event2.currentTarget.getBoundingClientRect();
      const midY = rect.top + rect.height / 2;
      set(drop_target_index, event2.clientY > midY ? get(normalized_files).length : index);
    } else {
      set(drop_target_index, index);
    }
    if (event2.dataTransfer) {
      event2.dataTransfer.dropEffect = "move";
    }
  }
  function handle_drag_end(event2) {
    if (!event2.dataTransfer?.dropEffect || event2.dataTransfer.dropEffect === "none") {
      set(dragging_index, null);
      set(drop_target_index, null);
    }
  }
  function handle_drop(event2, index) {
    event2.preventDefault();
    if (get(dragging_index) === null || get(dragging_index) === index) return;
    const files = Array.isArray(value()) ? [...value()] : [value()];
    const [removed] = files.splice(get(dragging_index), 1);
    files.splice(get(drop_target_index) === get(normalized_files).length ? get(normalized_files).length : index, 0, removed);
    const new_value = Array.isArray(value()) ? files : files[0];
    dispatch("change", new_value);
    set(dragging_index, null);
    set(drop_target_index, null);
  }
  function split_filename(filename) {
    const last_dot = filename.lastIndexOf(".");
    if (last_dot === -1) {
      return [filename, ""];
    }
    return [filename.slice(0, last_dot), filename.slice(last_dot)];
  }
  function handle_row_click(event2, index) {
    const tr = event2.currentTarget;
    const should_select = event2.target === tr || // Only select if the click is on the row itself
    tr && tr.firstElementChild && event2.composedPath().includes(tr.firstElementChild);
    if (should_select) {
      dispatch("select", { value: get(normalized_files)[index].orig_name, index });
    }
  }
  function remove_file(index) {
    const removed = get(normalized_files).splice(index, 1);
    set(normalized_files, [...get(normalized_files)]);
    value(get(normalized_files));
    dispatch("delete", removed[0]);
    dispatch("change", get(normalized_files));
  }
  function handle_download(file) {
    dispatch("download", file);
  }
  const is_browser = typeof window !== "undefined";
  legacy_pre_effect(() => deep_read_state(value()), () => {
    set(normalized_files, (Array.isArray(value()) ? value() : [value()]).map((file) => {
      const [filename_stem, filename_ext] = split_filename(file.orig_name ?? "");
      return { ...file, filename_stem, filename_ext };
    }));
  });
  legacy_pre_effect_reset();
  init();
  var div = root();
  let styles;
  var table = child(div);
  var tbody = child(table);
  each(
    tbody,
    7,
    () => get(
      // Only select if the click is on the row itself
      // Or if the click is on the name column
      normalized_files
    ),
    (file) => file.url,
    ($$anchor2, file, i) => {
      var tr_1 = root_1$1();
      let classes;
      var td = child(tr_1);
      var node = child(td);
      {
        var consequent = ($$anchor3) => {
          var span = root_2$1();
          append($$anchor3, span);
        };
        if_block(node, ($$render) => {
          if (deep_read_state(allow_reordering()), get(normalized_files), untrack(() => allow_reordering() && get(normalized_files).length > 1)) $$render(consequent);
        });
      }
      var span_1 = sibling(node, 2);
      var text$1 = child(span_1, true);
      reset(span_1);
      var span_2 = sibling(span_1, 2);
      var text_1 = child(span_2, true);
      reset(span_2);
      reset(td);
      var td_1 = sibling(td);
      var node_1 = child(td_1);
      {
        var consequent_1 = ($$anchor3) => {
          {
            let $0 = derived_safe_equal(() => (get(file), untrack(() => is_browser && window.__is_colab__ ? null : get(file).orig_name)));
            DownloadLink($$anchor3, {
              get href() {
                return get(file), untrack(() => get(file).url);
              },
              get download() {
                return get($0);
              },
              $$events: { click: () => handle_download(get(file)) },
              children: ($$anchor4, $$slotProps) => {
                var fragment_1 = root_4();
                var node_2 = first_child(fragment_1);
                html(node_2, () => (get(file), deep_read_state(prettyBytes), untrack(() => get(file).size != null ? prettyBytes(get(file).size) : "(size unknown)")));
                next();
                append($$anchor4, fragment_1);
              },
              $$slots: { default: true }
            });
          }
        };
        var alternate = ($$anchor3) => {
          var text_2 = text();
          template_effect(($0) => set_text(text_2, $0), [
            () => (deep_read_state(i18n()), untrack(() => i18n()("file.uploading")))
          ]);
          append($$anchor3, text_2);
        };
        if_block(node_1, ($$render) => {
          if (get(file), untrack(() => get(file).url)) $$render(consequent_1);
          else $$render(alternate, false);
        });
      }
      reset(td_1);
      var node_3 = sibling(td_1);
      {
        var consequent_2 = ($$anchor3) => {
          var td_2 = root_6();
          var button = child(td_2);
          reset(td_2);
          event("click", button, () => {
            remove_file(get(i));
          });
          event("keydown", button, (event2) => {
            if (event2.key === "Enter") {
              remove_file(get(i));
            }
          });
          append($$anchor3, td_2);
        };
        if_block(node_3, ($$render) => {
          if (get(normalized_files), untrack(() => get(normalized_files).length > 1)) $$render(consequent_2);
        });
      }
      reset(tr_1);
      template_effect(() => {
        classes = set_class(tr_1, 1, "file svelte-al0bnp", null, classes, {
          selectable: selectable(),
          dragging: get(dragging_index) === get(i),
          "drop-target": get(drop_target_index) === get(i) || get(i) === get(normalized_files).length - 1 && get(drop_target_index) === get(normalized_files).length
        });
        set_attribute(tr_1, "data-drop-target", (get(drop_target_index), get(normalized_files), deep_read_state(get(i)), untrack(() => get(drop_target_index) === get(normalized_files).length && get(i) === get(normalized_files).length - 1 ? "after" : get(drop_target_index) === get(i) + 1 ? "after" : "before")));
        set_attribute(tr_1, "draggable", (deep_read_state(allow_reordering()), get(normalized_files), untrack(() => allow_reordering() && get(normalized_files).length > 1)));
        set_attribute(td, "aria-label", (get(file), untrack(() => get(file).orig_name)));
        set_text(text$1, (get(file), untrack(() => get(file).filename_stem)));
        set_text(text_1, (get(file), untrack(() => get(file).filename_ext)));
      });
      event("click", tr_1, (event2) => {
        handle_row_click(event2, get(i));
      });
      event("dragstart", tr_1, (event2) => handle_drag_start(event2, get(i)));
      event("dragenter", tr_1, preventDefault(function($$arg) {
        bubble_event.call(this, $$props, $$arg);
      }));
      event("dragover", tr_1, (event2) => handle_drag_over(event2, get(i)));
      event("drop", tr_1, (event2) => handle_drop(event2, get(i)));
      event("dragend", tr_1, handle_drag_end);
      append($$anchor2, tr_1);
    }
  );
  reset(tbody);
  reset(table);
  reset(div);
  template_effect(() => styles = set_style(div, "", styles, {
    "max-height": height() ? typeof height() === "number" ? height() + "px" : height() : "auto"
  }));
  append($$anchor, div);
  pop();
}
var root_3 = from_html(`<!> <!>`, 1);
var root_2 = from_html(`<!> <!>`, 1);
var root_1 = from_html(`<!> <!>`, 1);
function FileUpload($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 12);
  let label = prop($$props, "label", 8);
  let show_label = prop($$props, "show_label", 8, true);
  let file_count = prop($$props, "file_count", 8, "single");
  let file_types = prop($$props, "file_types", 8, null);
  let selectable = prop($$props, "selectable", 8, false);
  let root2 = prop($$props, "root", 8);
  let height = prop($$props, "height", 8, void 0);
  let i18n = prop($$props, "i18n", 8);
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let upload = prop($$props, "upload", 8);
  let stream_handler = prop($$props, "stream_handler", 8);
  let uploading = prop($$props, "uploading", 12, false);
  let allow_reordering = prop($$props, "allow_reordering", 8, false);
  let upload_promise = prop($$props, "upload_promise", 12, null);
  async function handle_upload({ detail }) {
    if (Array.isArray(value())) {
      value([...value(), ...Array.isArray(detail) ? detail : [detail]]);
    } else if (value()) {
      value([value(), ...Array.isArray(detail) ? detail : [detail]]);
    } else {
      value(detail);
    }
    await tick();
    dispatch("change", value());
    dispatch("upload", detail);
  }
  function handle_clear() {
    value(null);
    dispatch("change", null);
    dispatch("clear");
  }
  const dispatch = createEventDispatcher();
  let dragging = mutable_source(false);
  legacy_pre_effect(() => get(dragging), () => {
    dispatch("drag", get(dragging));
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root_1();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => !value());
    let $1 = derived_safe_equal(() => label() || "File");
    BlockLabel(node, {
      get show_label() {
        return show_label();
      },
      get Icon() {
        return File;
      },
      get float() {
        return get($0);
      },
      get label() {
        return get($1);
      }
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent_1 = ($$anchor2) => {
      var fragment_1 = root_2();
      var node_2 = first_child(fragment_1);
      IconButtonWrapper(node_2, {
        children: ($$anchor3, $$slotProps) => {
          var fragment_2 = root_3();
          var node_3 = first_child(fragment_2);
          {
            var consequent = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.upload"))));
                IconButton($$anchor4, {
                  get Icon() {
                    return Upload$1;
                  },
                  get label() {
                    return get($0);
                  },
                  children: ($$anchor5, $$slotProps2) => {
                    Upload($$anchor5, {
                      icon_upload: true,
                      get filetype() {
                        return file_types();
                      },
                      get file_count() {
                        return file_count();
                      },
                      get max_file_size() {
                        return max_file_size();
                      },
                      get root() {
                        return root2();
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
                      $$legacy: true
                    });
                  },
                  $$slots: { default: true }
                });
              }
            };
            if_block(node_3, ($$render) => {
              if (deep_read_state(file_count()), deep_read_state(value()), untrack(() => !(file_count() === "single" && (Array.isArray(value()) ? value().length > 0 : value() !== null)))) $$render(consequent);
            });
          }
          var node_4 = sibling(node_3, 2);
          {
            let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.clear"))));
            IconButton(node_4, {
              get Icon() {
                return Clear;
              },
              get label() {
                return get($0);
              },
              $$events: {
                click: (event2) => {
                  dispatch("clear");
                  event2.stopPropagation();
                  handle_clear();
                }
              }
            });
          }
          append($$anchor3, fragment_2);
        },
        $$slots: { default: true }
      });
      var node_5 = sibling(node_2, 2);
      FilePreview(node_5, {
        get i18n() {
          return i18n();
        },
        get selectable() {
          return selectable();
        },
        get value() {
          return value();
        },
        get height() {
          return height();
        },
        get allow_reordering() {
          return allow_reordering();
        },
        $$events: {
          select($$arg) {
            bubble_event.call(this, $$props, $$arg);
          },
          change($$arg) {
            bubble_event.call(this, $$props, $$arg);
          },
          delete($$arg) {
            bubble_event.call(this, $$props, $$arg);
          }
        }
      });
      append($$anchor2, fragment_1);
    };
    var alternate = ($$anchor2) => {
      Upload($$anchor2, {
        get filetype() {
          return file_types();
        },
        get file_count() {
          return file_count();
        },
        get max_file_size() {
          return max_file_size();
        },
        get root() {
          return root2();
        },
        get stream_handler() {
          return stream_handler();
        },
        get upload() {
          return upload();
        },
        get height() {
          return height();
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
          var fragment_6 = comment();
          var node_6 = first_child(fragment_6);
          slot(node_6, $$props, "default", {}, null);
          append($$anchor3, fragment_6);
        },
        $$slots: { default: true },
        $$legacy: true
      });
    };
    if_block(node_1, ($$render) => {
      if (deep_read_state(value()), untrack(() => value() && (Array.isArray(value()) ? value().length > 0 : true))) $$render(consequent_1);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  FileUpload as F,
  FilePreview as a
};
//# sourceMappingURL=B-2qwVul.js.map
