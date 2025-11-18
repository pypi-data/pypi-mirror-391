import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, m as mutable_source, q as createEventDispatcher, I as onMount, N as onDestroy, i as legacy_pre_effect, k as get, j as set, n as legacy_pre_effect_reset, c as from_html, d as child, r as reset, s as sibling, t as template_effect, b as append, o as pop, y as untrack, g as set_text, u as deep_read_state, D as comment, v as first_child, z as event, K as tick } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { s as slot } from "./DX-MI-YE.js";
import { w as set_value, a as set_class, x as prepare_files, s as set_attribute, p as set_style, y as action } from "./DXi4jxVF.js";
import { b as bind_prop } from "./CswR_hUw.js";
import { i as init } from "./DB0xzveP.js";
/* empty css         */
import { c as create_drag } from "./ifMVVx36.js";
var root_2$1 = from_html(`<div class="file svelte-ua961l"><span><div class="progress-bar svelte-ua961l"><progress style="visibility:hidden;height:0;width:0;" max="100" class="svelte-ua961l"> </progress></div></span> <span class="file-name svelte-ua961l"> </span></div>`);
var root_1 = from_html(`<div><span class="uploading svelte-ua961l"> </span> <!></div>`);
function UploadProgress($$anchor, $$props) {
  push($$props, false);
  let upload_id = prop($$props, "upload_id", 8);
  let root = prop($$props, "root", 8);
  let files = prop($$props, "files", 8);
  let stream_handler = prop($$props, "stream_handler", 8);
  let stream;
  let progress = mutable_source(false);
  let current_file_upload = mutable_source();
  let file_to_display = mutable_source();
  let files_with_progress = mutable_source(files().map((file) => {
    return { ...file, progress: 0 };
  }));
  const dispatch = createEventDispatcher();
  function handleProgress(filename, chunk_size) {
    set(files_with_progress, get(files_with_progress).map((file) => {
      if (file.orig_name === filename) {
        file.progress += chunk_size;
      }
      return file;
    }));
  }
  function getProgress(file) {
    return file.progress * 100 / (file.size || 0) || 0;
  }
  onMount(async () => {
    stream = await stream_handler()(new URL(`${root()}/gradio_api/upload_progress?upload_id=${upload_id()}`));
    if (stream == null) {
      throw new Error("Event source is not defined");
    }
    stream.onmessage = async function(event2) {
      const _data = JSON.parse(event2.data);
      if (!get(progress)) set(progress, true);
      if (_data.msg === "done") {
        stream?.close();
        dispatch("done");
      } else {
        set(current_file_upload, _data);
        handleProgress(_data.orig_name, _data.chunk_size);
      }
    };
  });
  onDestroy(() => {
    if (stream != null || stream != void 0) stream.close();
  });
  function calculateTotalProgress(files2) {
    let totalProgress = 0;
    files2.forEach((file) => {
      totalProgress += getProgress(file);
    });
    document.documentElement.style.setProperty("--upload-progress-width", (totalProgress / files2.length).toFixed(2) + "%");
    return totalProgress / files2.length;
  }
  legacy_pre_effect(() => get(files_with_progress), () => {
    calculateTotalProgress(get(files_with_progress));
  });
  legacy_pre_effect(() => (get(current_file_upload), get(files_with_progress)), () => {
    set(file_to_display, get(current_file_upload) || get(files_with_progress)[0]);
  });
  legacy_pre_effect_reset();
  init();
  var div = root_1();
  let classes;
  var span = child(div);
  var text = child(span);
  reset(span);
  var node = sibling(span, 2);
  {
    var consequent = ($$anchor2) => {
      var div_1 = root_2$1();
      var span_1 = child(div_1);
      var div_2 = child(span_1);
      var progress_1 = child(div_2);
      var text_1 = child(progress_1, true);
      reset(progress_1);
      reset(div_2);
      reset(span_1);
      var span_2 = sibling(span_1, 2);
      var text_2 = child(span_2, true);
      reset(span_2);
      reset(div_1);
      template_effect(
        ($0, $1) => {
          set_value(progress_1, $0);
          set_text(text_1, $1);
          set_text(text_2, (get(file_to_display), untrack(() => get(file_to_display).orig_name)));
        },
        [
          () => (get(file_to_display), untrack(() => getProgress(get(file_to_display)))),
          () => (get(file_to_display), untrack(() => getProgress(get(file_to_display))))
        ]
      );
      append($$anchor2, div_1);
    };
    if_block(node, ($$render) => {
      if (get(file_to_display)) $$render(consequent);
    });
  }
  reset(div);
  template_effect(() => {
    classes = set_class(div, 1, "wrap svelte-ua961l", null, classes, { progress: get(progress) });
    set_text(text, `Uploading ${(get(files_with_progress), untrack(() => get(files_with_progress).length)) ?? ""}
		${(get(files_with_progress), untrack(() => get(files_with_progress).length > 1 ? "files" : "file")) ?? ""}...`);
  });
  append($$anchor, div);
  pop();
}
var root_2 = from_html(`<button><!></button>`);
var root_6 = from_html(`<button aria-dropeffect="copy"><!></button>`);
function Upload($$anchor, $$props) {
  push($$props, false);
  const ios = mutable_source();
  const { drag, open_file_upload: _open_file_upload } = create_drag();
  let filetype = prop($$props, "filetype", 12, null);
  let dragging = prop($$props, "dragging", 12, false);
  let boundedheight = prop($$props, "boundedheight", 8, true);
  let center = prop($$props, "center", 8, true);
  let flex = prop($$props, "flex", 8, true);
  let file_count = prop($$props, "file_count", 8, "single");
  let disable_click = prop($$props, "disable_click", 8, false);
  let root = prop($$props, "root", 8);
  let hidden = prop($$props, "hidden", 8, false);
  let format = prop($$props, "format", 8, "file");
  let uploading = prop($$props, "uploading", 12, false);
  let show_progress = prop($$props, "show_progress", 8, true);
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let upload = prop($$props, "upload", 8);
  let stream_handler = prop($$props, "stream_handler", 8);
  let icon_upload = prop($$props, "icon_upload", 8, false);
  let height = prop($$props, "height", 8, void 0);
  let aria_label = prop($$props, "aria_label", 8, void 0);
  let upload_promise = prop($$props, "upload_promise", 12, null);
  function open_upload() {
    _open_file_upload();
  }
  let upload_id = mutable_source("");
  let file_data = mutable_source();
  let accept_file_types = mutable_source();
  let use_post_upload_validation = null;
  const get_ios = () => {
    if (typeof navigator !== "undefined") {
      const userAgent = navigator.userAgent.toLowerCase();
      return userAgent.indexOf("iphone") > -1 || userAgent.indexOf("ipad") > -1;
    }
    return false;
  };
  const dispatch = createEventDispatcher();
  const validFileTypes = ["image", "video", "audio", "text", "file"];
  const process_file_type = (type) => {
    if (get(ios) && type.startsWith(".")) {
      use_post_upload_validation = true;
      return type;
    }
    if (get(ios) && type.includes("file/*")) {
      return "*";
    }
    if (type.startsWith(".") || type.endsWith("/*")) {
      return type;
    }
    if (validFileTypes.includes(type)) {
      return type + "/*";
    }
    return "." + type;
  };
  function paste_clipboard() {
    navigator.clipboard.read().then(async (items) => {
      for (let i = 0; i < items.length; i++) {
        const type = items[i].types.find((t) => t.startsWith("image/"));
        if (type) {
          items[i].getType(type).then(async (blob) => {
            const file = new File([blob], `clipboard.${type.replace("image/", "")}`);
            await load_files([file]);
          });
          break;
        }
      }
    });
  }
  function open_file_upload() {
    _open_file_upload();
  }
  function handle_upload(file_data2, _upload_id) {
    upload_promise(new Promise(async (resolve, rej) => {
      await tick();
      if (!_upload_id) {
        set(upload_id, Math.random().toString(36).substring(2, 15));
      } else {
        set(upload_id, _upload_id);
      }
      uploading(true);
      try {
        const _file_data = await upload()(file_data2, root(), get(upload_id), max_file_size() ?? Infinity);
        dispatch("load", file_count() === "single" ? _file_data?.[0] : _file_data);
        resolve(_file_data || []);
        uploading(false);
        return _file_data || [];
      } catch (e) {
        dispatch("error", e.message);
        uploading(false);
        resolve([]);
      }
    }));
    return upload_promise();
  }
  function is_valid_mimetype(file_accept, uploaded_file_extension, uploaded_file_type) {
    if (!file_accept || file_accept === "*" || file_accept === "file/*" || Array.isArray(file_accept) && file_accept.some((accept) => accept === "*" || accept === "file/*")) {
      return true;
    }
    let acceptArray;
    if (typeof file_accept === "string") {
      acceptArray = file_accept.split(",").map((s) => s.trim());
    } else if (Array.isArray(file_accept)) {
      acceptArray = file_accept;
    } else {
      return false;
    }
    return acceptArray.includes(uploaded_file_extension) || acceptArray.some((type) => {
      const [category] = type.split("/").map((s) => s.trim());
      return type.endsWith("/*") && uploaded_file_type.startsWith(category + "/");
    });
  }
  async function load_files(files, upload_id2) {
    if (!files.length) {
      return;
    }
    let _files = files.map((f) => new File([f], f instanceof File ? f.name : "file", { type: f.type }));
    if (get(ios) && use_post_upload_validation) {
      _files = _files.filter((file) => {
        if (is_valid_file(file)) {
          return true;
        }
        dispatch("error", `Invalid file type: ${file.name}. Only ${filetype()} allowed.`);
        return false;
      });
      if (_files.length === 0) {
        return [];
      }
    }
    set(file_data, await prepare_files(_files));
    return await handle_upload(get(file_data), upload_id2);
  }
  function is_valid_file(file) {
    if (!filetype()) return true;
    const allowed_types = Array.isArray(filetype()) ? filetype() : [filetype()];
    return allowed_types.some((type) => {
      const processed_type = process_file_type(type);
      if (processed_type.startsWith(".")) {
        return file.name.toLowerCase().endsWith(processed_type.toLowerCase());
      }
      if (processed_type === "*") {
        return true;
      }
      if (processed_type.endsWith("/*")) {
        const [category] = processed_type.split("/");
        return file.type.startsWith(category + "/");
      }
      return file.type === processed_type;
    });
  }
  async function load_files_from_upload(files) {
    const files_to_load = files.filter((file) => {
      const file_extension = "." + file.name.toLowerCase().split(".").pop();
      if (file_extension && is_valid_mimetype(get(accept_file_types), file_extension, file.type)) {
        return true;
      }
      if (file_extension && Array.isArray(filetype()) ? filetype().includes(file_extension) : file_extension === filetype()) {
        return true;
      }
      dispatch("error", `Invalid file type only ${filetype()} allowed.`);
      return false;
    });
    if (format() != "blob") {
      await load_files(files_to_load);
    } else {
      if (file_count() === "single") {
        dispatch("load", files_to_load[0]);
        return;
      }
      dispatch("load", files_to_load);
    }
  }
  async function load_files_from_drop(e) {
    dragging(false);
    if (!e.dataTransfer?.files) return;
    const files_to_load = Array.from(e.dataTransfer.files).filter(is_valid_file);
    if (format() != "blob") {
      await load_files(files_to_load);
    } else {
      if (file_count() === "single") {
        dispatch("load", files_to_load[0]);
        return;
      }
      dispatch("load", files_to_load);
    }
  }
  legacy_pre_effect(() => {
  }, () => {
    set(ios, get_ios());
  });
  legacy_pre_effect(() => (deep_read_state(filetype()), get(ios)), () => {
    if (filetype() == null) {
      set(accept_file_types, null);
    } else if (typeof filetype() === "string") {
      set(accept_file_types, process_file_type(filetype()));
    } else if (get(ios) && filetype().includes("file/*")) {
      set(accept_file_types, "*");
    } else {
      filetype(filetype().map(process_file_type));
      set(accept_file_types, filetype().join(", "));
    }
  });
  legacy_pre_effect_reset();
  var $$exports = {
    open_upload,
    paste_clipboard,
    open_file_upload,
    load_files,
    load_files_from_drop
  };
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      var button = root_2();
      let classes;
      let styles;
      var node_1 = child(button);
      slot(node_1, $$props, "default", {}, null);
      reset(button);
      template_effect(() => {
        set_attribute(button, "tabindex", hidden() ? -1 : 0);
        set_attribute(button, "aria-label", aria_label() || "Paste from clipboard");
        classes = set_class(button, 1, "svelte-8prmba", null, classes, {
          hidden: hidden(),
          center: center(),
          boundedheight: boundedheight(),
          flex: flex(),
          "icon-mode": icon_upload()
        });
        styles = set_style(button, "", styles, {
          height: icon_upload() ? "" : height() ? typeof height() === "number" ? height() + "px" : height() : "100%"
        });
      });
      event("click", button, paste_clipboard);
      append($$anchor2, button);
    };
    var alternate_1 = ($$anchor2) => {
      var fragment_1 = comment();
      var node_2 = first_child(fragment_1);
      {
        var consequent_2 = ($$anchor3) => {
          var fragment_2 = comment();
          var node_3 = first_child(fragment_2);
          {
            var consequent_1 = ($$anchor4) => {
              UploadProgress($$anchor4, {
                get root() {
                  return root();
                },
                get upload_id() {
                  return get(upload_id);
                },
                get files() {
                  return get(file_data);
                },
                get stream_handler() {
                  return stream_handler();
                }
              });
            };
            if_block(node_3, ($$render) => {
              if (!hidden()) $$render(consequent_1);
            });
          }
          append($$anchor3, fragment_2);
        };
        var alternate = ($$anchor3) => {
          var button_1 = root_6();
          let classes_1;
          let styles_1;
          var node_4 = child(button_1);
          slot(node_4, $$props, "default", {}, null);
          reset(button_1);
          action(button_1, ($$node, $$action_arg) => drag?.($$node, $$action_arg), () => ({
            on_drag_change: (dragging2) => dragging2 = dragging2,
            on_files: (files) => load_files_from_upload(files),
            accepted_types: get(accept_file_types),
            mode: file_count(),
            disable_click: disable_click()
          }));
          template_effect(() => {
            set_attribute(button_1, "tabindex", hidden() ? -1 : 0);
            set_attribute(button_1, "aria-label", aria_label() || "Click to upload or drop files");
            classes_1 = set_class(button_1, 1, "svelte-8prmba", null, classes_1, {
              hidden: hidden(),
              center: center(),
              boundedheight: boundedheight(),
              flex: flex(),
              disable_click: disable_click(),
              "icon-mode": icon_upload()
            });
            styles_1 = set_style(button_1, "", styles_1, {
              height: icon_upload() ? "" : height() ? typeof height() === "number" ? height() + "px" : height() : "100%"
            });
          });
          append($$anchor3, button_1);
        };
        if_block(
          node_2,
          ($$render) => {
            if (uploading() && show_progress()) $$render(consequent_2);
            else $$render(alternate, false);
          },
          true
        );
      }
      append($$anchor2, fragment_1);
    };
    if_block(node, ($$render) => {
      if (filetype() === "clipboard") $$render(consequent);
      else $$render(alternate_1, false);
    });
  }
  append($$anchor, fragment);
  bind_prop($$props, "open_upload", open_upload);
  bind_prop($$props, "paste_clipboard", paste_clipboard);
  bind_prop($$props, "open_file_upload", open_file_upload);
  bind_prop($$props, "load_files", load_files);
  bind_prop($$props, "load_files_from_drop", load_files_from_drop);
  return pop($$exports);
}
export {
  Upload as U,
  UploadProgress as a
};
//# sourceMappingURL=BcroWaqq.js.map
