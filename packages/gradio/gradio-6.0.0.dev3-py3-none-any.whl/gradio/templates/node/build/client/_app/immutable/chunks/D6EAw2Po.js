import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, j as set, m as mutable_source, k as get, x as derived_safe_equal, o as pop, y as untrack, u as deep_read_state } from "./DEzry6cj.js";
import { i as init } from "./DB0xzveP.js";
import { p as prop } from "./DUftb7my.js";
import { b as IconButton, e as ShareError } from "./DXi4jxVF.js";
import { C as Community } from "./CeH6vEIM.js";
function ShareButton($$anchor, $$props) {
  push($$props, false);
  const dispatch = createEventDispatcher();
  let formatter = prop($$props, "formatter", 8);
  let value = prop($$props, "value", 8);
  let i18n = prop($$props, "i18n", 8);
  let pending = mutable_source(false);
  init();
  {
    let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.share"))));
    IconButton($$anchor, {
      get Icon() {
        return Community;
      },
      get label() {
        return get($0);
      },
      get pending() {
        return get(pending);
      },
      $$events: {
        click: async () => {
          try {
            set(pending, true);
            const formatted = await formatter()(value());
            dispatch("share", { description: formatted });
          } catch (e) {
            console.error(e);
            let message = e instanceof ShareError ? e.message : "Share failed.";
            dispatch("error", message);
          } finally {
            set(pending, false);
          }
        }
      }
    });
  }
  pop();
}
export {
  ShareButton as S
};
//# sourceMappingURL=D6EAw2Po.js.map
