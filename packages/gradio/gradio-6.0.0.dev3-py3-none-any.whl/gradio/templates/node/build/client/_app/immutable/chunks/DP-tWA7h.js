import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, c as from_html, v as first_child, d as child, r as reset, s as sibling, t as template_effect, z as event, b as append, o as pop, g as set_text, D as comment, k as get, A as user_derived } from "./DEzry6cj.js";
import { p as prop, r as rest_props, i as if_block, s as spread_props } from "./DUftb7my.js";
import { s as slot } from "./DX-MI-YE.js";
import "./BAp-OWo-.js";
import { a as set_class, p as set_style, G as Gradio, B as Block, L as BaseColumn, g as Static } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
var root = from_html(`<button><span class="svelte-e5lyqv"> </span> <span class="icon svelte-e5lyqv">▼</span></button> <div><!></div>`, 1);
function Accordion($$anchor, $$props) {
  push($$props, false);
  const dispatch = createEventDispatcher();
  let open = prop($$props, "open", 12, true);
  let label = prop($$props, "label", 8, "");
  init();
  var fragment = root();
  var button = first_child(fragment);
  let classes;
  var span = child(button);
  var text = child(span, true);
  reset(span);
  var span_1 = sibling(span, 2);
  let styles;
  reset(button);
  var div = sibling(button, 2);
  let styles_1;
  var node = child(div);
  slot(node, $$props, "default", {}, null);
  reset(div);
  template_effect(() => {
    classes = set_class(button, 1, "label-wrap svelte-e5lyqv", null, classes, { open: open() });
    set_text(text, label());
    styles = set_style(span_1, "", styles, { transform: open() ? "rotate(0)" : "rotate(90deg)" });
    styles_1 = set_style(div, "", styles_1, { display: open() ? "block" : "none" });
  });
  event("click", button, () => {
    open(!open());
    if (open()) {
      dispatch("expand");
    } else {
      dispatch("collapse");
    }
  });
  append($$anchor, fragment);
  pop();
}
var root_1 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let label = user_derived(() => gradio.shared.label || "");
  Block($$anchor, {
    get elem_id() {
      return gradio.shared.elem_id;
    },
    get elem_classes() {
      return gradio.shared.elem_classes;
    },
    get visible() {
      return gradio.shared.visible;
    },
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          Static($$anchor3, spread_props(
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
        };
        if_block(node, ($$render) => {
          if (gradio.shared.loading_status) $$render(consequent);
        });
      }
      var node_1 = sibling(node, 2);
      Accordion(node_1, {
        get label() {
          return get(label);
        },
        get open() {
          return gradio.props.open;
        },
        $$events: {
          expand: () => gradio.dispatch("expand"),
          collapse: () => gradio.dispatch("collapse")
        },
        children: ($$anchor3, $$slotProps2) => {
          BaseColumn($$anchor3, {
            children: ($$anchor4, $$slotProps3) => {
              var fragment_4 = comment();
              var node_2 = first_child(fragment_4);
              slot(node_2, $$props, "default", {}, null);
              append($$anchor4, fragment_4);
            },
            $$slots: { default: true }
          });
        },
        $$slots: { default: true }
      });
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=DP-tWA7h.js.map
