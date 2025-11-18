import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, c as from_html, v as first_child, s as sibling, k as get, x as derived_safe_equal, b as append, y as untrack, u as deep_read_state, o as pop } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { s as slot } from "./DX-MI-YE.js";
import { i as init } from "./DB0xzveP.js";
import { I as IconButtonWrapper, b as IconButton, C as Clear } from "./DXi4jxVF.js";
import { D as DownloadLink } from "./BFO3TfnI.js";
import { D as Download } from "./rkplYKOt.js";
import { E as Edit } from "./CByIssN2.js";
import { U as Undo } from "./oKXAgRt1.js";
var root_1 = from_html(`<!> <!> <!> <!> <!>`, 1);
function ModifyUpload($$anchor, $$props) {
  push($$props, false);
  let editable = prop($$props, "editable", 8, false);
  let undoable = prop($$props, "undoable", 8, false);
  let download = prop($$props, "download", 8, null);
  let i18n = prop($$props, "i18n", 8);
  const dispatch = createEventDispatcher();
  init();
  IconButtonWrapper($$anchor, {
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          {
            let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.edit"))));
            IconButton($$anchor3, {
              get Icon() {
                return Edit;
              },
              get label() {
                return get($0);
              },
              $$events: { click: () => dispatch("edit") }
            });
          }
        };
        if_block(node, ($$render) => {
          if (editable()) $$render(consequent);
        });
      }
      var node_1 = sibling(node, 2);
      {
        var consequent_1 = ($$anchor3) => {
          {
            let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.undo"))));
            IconButton($$anchor3, {
              get Icon() {
                return Undo;
              },
              get label() {
                return get($0);
              },
              $$events: { click: () => dispatch("undo") }
            });
          }
        };
        if_block(node_1, ($$render) => {
          if (undoable()) $$render(consequent_1);
        });
      }
      var node_2 = sibling(node_1, 2);
      {
        var consequent_2 = ($$anchor3) => {
          DownloadLink($$anchor3, {
            get href() {
              return download();
            },
            download: true,
            children: ($$anchor4, $$slotProps2) => {
              {
                let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.download"))));
                IconButton($$anchor4, {
                  get Icon() {
                    return Download;
                  },
                  get label() {
                    return get($0);
                  }
                });
              }
            },
            $$slots: { default: true }
          });
        };
        if_block(node_2, ($$render) => {
          if (download()) $$render(consequent_2);
        });
      }
      var node_3 = sibling(node_2, 2);
      slot(node_3, $$props, "default", {}, null);
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
            click: (event) => {
              dispatch("clear");
              event.stopPropagation();
            }
          }
        });
      }
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  ModifyUpload as M
};
//# sourceMappingURL=BXBtG43Y.js.map
