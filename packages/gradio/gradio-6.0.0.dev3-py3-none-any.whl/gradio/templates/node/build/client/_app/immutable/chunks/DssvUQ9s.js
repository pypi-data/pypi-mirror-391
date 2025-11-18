import { h as hydrating, a as hydrate_next, G as is_runes, H as block } from "./DEzry6cj.js";
import { B as BranchManager } from "./DUftb7my.js";
function key(node, get_key, render_fn) {
  if (hydrating) {
    hydrate_next();
  }
  var branches = new BranchManager(node);
  var legacy = !is_runes();
  block(() => {
    var key2 = get_key();
    if (legacy && key2 !== null && typeof key2 === "object") {
      key2 = /** @type {V} */
      {};
    }
    branches.ensure(key2, render_fn);
  });
}
export {
  key as k
};
//# sourceMappingURL=DssvUQ9s.js.map
