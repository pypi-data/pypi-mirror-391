import "./9B4_veAf.js";
import { p as push, c as from_html, v as first_child, k as get, A as user_derived, s as sibling, b as append, j as set, J as state, o as pop } from "./DEzry6cj.js";
import { r as rest_props, i as if_block, s as spread_props } from "./DUftb7my.js";
import { G as Gradio, B as Block, g as Static, I as IconButtonWrapper } from "./DXi4jxVF.js";
import { P as Plot, a as Plot$1 } from "./BFXHQ9DL.js";
import "./BAp-OWo-.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { F as FullscreenButton } from "./BAYq2deR.js";
var root_1 = from_html(`<!> <!> <!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let fullscreen = state(false);
  Block($$anchor, {
    padding: false,
    get elem_id() {
      return gradio.shared.elem_id;
    },
    get elem_classes() {
      return gradio.shared.elem_classes;
    },
    get visible() {
      return gradio.shared.visible;
    },
    get container() {
      return gradio.shared.container;
    },
    get scale() {
      return gradio.shared.scale;
    },
    get min_width() {
      return gradio.shared.min_width;
    },
    allow_overflow: false,
    get fullscreen() {
      return get(fullscreen);
    },
    set fullscreen($$value) {
      set(fullscreen, $$value, true);
    },
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      {
        let $0 = user_derived(() => gradio.shared.label || gradio.i18n("plot.plot"));
        BlockLabel(node, {
          get show_label() {
            return gradio.shared.show_label;
          },
          get label() {
            return get($0);
          },
          get Icon() {
            return Plot;
          }
        });
      }
      var node_1 = sibling(node, 2);
      {
        var consequent = ($$anchor3) => {
          IconButtonWrapper($$anchor3, {
            children: ($$anchor4, $$slotProps2) => {
              FullscreenButton($$anchor4, {
                get fullscreen() {
                  return get(fullscreen);
                },
                $$events: {
                  fullscreen: ({ detail }) => {
                    set(fullscreen, detail, true);
                  }
                }
              });
            },
            $$slots: { default: true }
          });
        };
        if_block(node_1, ($$render) => {
          if (gradio.props.show_fullscreen_button) $$render(consequent);
        });
      }
      var node_2 = sibling(node_1, 2);
      Static(node_2, spread_props(
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
      var node_3 = sibling(node_2, 2);
      Plot$1(node_3, {
        get gradio() {
          return gradio;
        }
      });
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Plot$1 as BasePlot,
  Index as default
};
//# sourceMappingURL=DTN7kQH3.js.map
