import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, j as set, m as mutable_source, c as from_html, v as first_child, s as sibling, b as append, t as template_effect, z as event, o as pop, k as get, y as untrack, u as deep_read_state, K as tick, L as proxy, M as user_effect, E as next, F as text, A as user_derived, g as set_text } from "./DEzry6cj.js";
import { p as prop, b as bind_this, i as if_block, r as rest_props } from "./DUftb7my.js";
import { f as Button, s as set_attribute, x as prepare_files, G as Gradio } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { s as slot } from "./DX-MI-YE.js";
import { i as init } from "./DB0xzveP.js";
var root_3 = from_html(`<img class="button-icon svelte-94gmgt"/>`);
var root_2 = from_html(`<!> <!>`, 1);
var root_1 = from_html(`<input class="hide svelte-94gmgt" type="file"/> <!>`, 1);
function UploadButton($$anchor, $$props) {
  push($$props, false);
  let elem_id = prop($$props, "elem_id", 8, "");
  let elem_classes = prop($$props, "elem_classes", 24, () => []);
  let visible = prop($$props, "visible", 8, true);
  let label = prop($$props, "label", 8);
  let value = prop($$props, "value", 12);
  let file_count = prop($$props, "file_count", 8);
  let file_types = prop($$props, "file_types", 28, () => []);
  let root = prop($$props, "root", 8);
  let size = prop($$props, "size", 8, "lg");
  let icon = prop($$props, "icon", 8, null);
  let scale = prop($$props, "scale", 8, null);
  let min_width = prop($$props, "min_width", 8, void 0);
  let variant = prop($$props, "variant", 8, "secondary");
  let disabled = prop($$props, "disabled", 8, false);
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let upload = prop($$props, "upload", 8);
  const dispatch = createEventDispatcher();
  let hidden_upload = mutable_source();
  let accept_file_types = mutable_source();
  if (file_types() == null) {
    set(accept_file_types, null);
  } else {
    file_types(file_types().map((x) => {
      if (x.startsWith(".")) {
        return x;
      }
      return x + "/*";
    }));
    set(accept_file_types, file_types().join(", "));
  }
  function open_file_upload() {
    dispatch("click");
    get(hidden_upload).click();
  }
  async function load_files(files) {
    let _files = Array.from(files);
    if (!files.length) {
      return;
    }
    if (file_count() === "single") {
      _files = [files[0]];
    }
    let all_file_data = await prepare_files(_files);
    await tick();
    try {
      all_file_data = (await upload()(all_file_data, root(), void 0, max_file_size() ?? Infinity))?.filter((x) => x !== null);
    } catch (e) {
      dispatch("error", e.message);
      return;
    }
    value(file_count() === "single" ? all_file_data?.[0] : all_file_data);
    dispatch("change", value());
    dispatch("upload", value());
  }
  async function load_files_from_upload(e) {
    const target = e.target;
    if (!target.files) return;
    await load_files(target.files);
  }
  function clear_input_value(e) {
    const target = e.target;
    if (target.value) target.value = "";
  }
  init();
  var fragment = root_1();
  var input = first_child(fragment);
  bind_this(input, ($$value) => set(hidden_upload, $$value), () => get(hidden_upload));
  var node = sibling(input, 2);
  Button(node, {
    get size() {
      return size();
    },
    get variant() {
      return variant();
    },
    get elem_id() {
      return elem_id();
    },
    get elem_classes() {
      return elem_classes();
    },
    get visible() {
      return visible();
    },
    get scale() {
      return scale();
    },
    get min_width() {
      return min_width();
    },
    get disabled() {
      return disabled();
    },
    $$events: { click: open_file_upload },
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_2();
      var node_1 = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          var img = root_3();
          template_effect(() => {
            set_attribute(img, "src", (deep_read_state(icon()), untrack(() => icon().url)));
            set_attribute(img, "alt", `${value()} icon`);
          });
          append($$anchor3, img);
        };
        if_block(node_1, ($$render) => {
          if (icon()) $$render(consequent);
        });
      }
      var node_2 = sibling(node_1, 2);
      slot(node_2, $$props, "default", {}, null);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  template_effect(() => {
    set_attribute(input, "accept", get(accept_file_types));
    input.multiple = file_count() === "multiple" || void 0;
    input.webkitdirectory = file_count() === "directory" || void 0;
    set_attribute(input, "mozdirectory", file_count() === "directory" || void 0);
    set_attribute(input, "data-testid", `${label() ?? ""}-upload-button`);
  });
  event("change", input, load_files_from_upload);
  event("click", input, clear_input_value);
  append($$anchor, fragment);
  pop();
}
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let value = proxy(gradio.props.value);
  user_effect(() => {
    if (value !== gradio.props.value) {
      gradio.props.value = value;
    }
  });
  async function handle_event(detail, event2) {
    gradio.props.value = detail;
    gradio.dispatch(event2);
  }
  const disabled = user_derived(() => !gradio.shared.interactive);
  UploadButton($$anchor, {
    get elem_id() {
      return gradio.shared.elem_id;
    },
    get elem_classes() {
      return gradio.shared.elem_classes;
    },
    get visible() {
      return gradio.shared.visible;
    },
    get file_count() {
      return gradio.props.file_count;
    },
    get file_types() {
      return gradio.props.file_types;
    },
    get size() {
      return gradio.props.size;
    },
    get scale() {
      return gradio.shared.scale;
    },
    get icon() {
      return gradio.props.icon;
    },
    get min_width() {
      return gradio.shared.min_width;
    },
    get root() {
      return gradio.shared.root;
    },
    get value() {
      return value;
    },
    get disabled() {
      return get(disabled);
    },
    get variant() {
      return gradio.props.variant;
    },
    get label() {
      return gradio.shared.label;
    },
    get max_file_size() {
      return gradio.shared.max_file_size;
    },
    upload: (...args) => gradio.shared.client.upload(...args),
    $$events: {
      click: () => gradio.dispatch("click"),
      change: ({ detail }) => handle_event(detail, "change"),
      upload: ({ detail }) => handle_event(detail, "upload"),
      error: ({ detail }) => {
        gradio.dispatch("error", detail);
      }
    },
    children: ($$anchor2, $$slotProps) => {
      next();
      var text$1 = text();
      template_effect(() => set_text(text$1, gradio.shared.label ?? ""));
      append($$anchor2, text$1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  UploadButton as BaseUploadButton,
  Index as default
};
//# sourceMappingURL=YNkpjNUs.js.map
