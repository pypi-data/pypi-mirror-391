import "./9B4_veAf.js";
import { p as push, c as from_html, v as first_child, s as sibling, b as append, o as pop } from "./DEzry6cj.js";
import { r as rest_props, s as spread_props, i as if_block } from "./DUftb7my.js";
import { G as Gradio, B as Block, g as Static, h as Info } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { C as Checkbox } from "./BbwKRM19.js";
var root_1 = from_html(`<!> <!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
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
        () => gradio.shared.loading_status,
        {
          $$events: {
            clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
          }
        }
      ));
      var node_1 = sibling(node, 2);
      Checkbox(node_1, {
        get gradio() {
          return gradio;
        }
      });
      var node_2 = sibling(node_1, 2);
      {
        var consequent = ($$anchor3) => {
          Info($$anchor3, {
            get info() {
              return gradio.props.info;
            }
          });
        };
        if_block(node_2, ($$render) => {
          if (gradio.props.info) $$render(consequent);
        });
      }
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Checkbox as BaseCheckbox,
  Index as default
};
//# sourceMappingURL=C8qaxsRk.js.map
