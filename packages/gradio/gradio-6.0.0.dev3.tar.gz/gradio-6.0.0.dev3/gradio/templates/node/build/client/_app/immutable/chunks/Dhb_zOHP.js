import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, c as from_html, v as first_child, s as sibling, b as append, t as template_effect, o as pop, y as untrack, u as deep_read_state, E as next, F as text, k as get, A as user_derived, g as set_text } from "./DEzry6cj.js";
import { p as prop, i as if_block, r as rest_props } from "./DUftb7my.js";
import { f as Button, s as set_attribute, G as Gradio } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { s as slot } from "./DX-MI-YE.js";
import { i as init } from "./DB0xzveP.js";
var root_2 = from_html(`<img class="button-icon svelte-4ac0fl"/>`);
var root_1 = from_html(`<!> <!>`, 1);
function DownloadButton($$anchor, $$props) {
  push($$props, false);
  let elem_id = prop($$props, "elem_id", 8, "");
  let elem_classes = prop($$props, "elem_classes", 24, () => []);
  let visible = prop($$props, "visible", 8, true);
  let variant = prop($$props, "variant", 8, "secondary");
  let size = prop($$props, "size", 8, "lg");
  let value = prop($$props, "value", 8);
  let icon = prop($$props, "icon", 8);
  let disabled = prop($$props, "disabled", 8, false);
  let scale = prop($$props, "scale", 8, null);
  let min_width = prop($$props, "min_width", 8, void 0);
  const dispatch = createEventDispatcher();
  function download_file() {
    dispatch("click");
    if (!value()?.url) {
      return;
    }
    let file_name;
    if (!value().orig_name && value().url) {
      const parts = value().url.split("/");
      file_name = parts[parts.length - 1];
      file_name = file_name.split("?")[0].split("#")[0];
    } else {
      file_name = value().orig_name;
    }
    const a = document.createElement("a");
    a.href = value().url;
    a.download = file_name || "file";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
  init();
  Button($$anchor, {
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
    $$events: { click: download_file },
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          var img = root_2();
          template_effect(() => {
            set_attribute(img, "src", (deep_read_state(icon()), untrack(() => icon().url)));
            set_attribute(img, "alt", `${value()} icon`);
          });
          append($$anchor3, img);
        };
        if_block(node, ($$render) => {
          if (icon()) $$render(consequent);
        });
      }
      var node_1 = sibling(node, 2);
      slot(node_1, $$props, "default", {}, null);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  {
    let $0 = user_derived(() => !gradio.shared.interactive);
    DownloadButton($$anchor, {
      get value() {
        return gradio.props.value;
      },
      get variant() {
        return gradio.props.variant;
      },
      get elem_id() {
        return gradio.shared.elem_id;
      },
      get elem_classes() {
        return gradio.shared.elem_classes;
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
      get visible() {
        return gradio.shared.visible;
      },
      get disabled() {
        return get($0);
      },
      $$events: { click: () => gradio.dispatch("click") },
      children: ($$anchor2, $$slotProps) => {
        next();
        var text$1 = text();
        template_effect(() => set_text(text$1, gradio.shared.label ?? ""));
        append($$anchor2, text$1);
      },
      $$slots: { default: true }
    });
  }
  pop();
}
export {
  DownloadButton as BaseButton,
  Index as default
};
//# sourceMappingURL=Dhb_zOHP.js.map
