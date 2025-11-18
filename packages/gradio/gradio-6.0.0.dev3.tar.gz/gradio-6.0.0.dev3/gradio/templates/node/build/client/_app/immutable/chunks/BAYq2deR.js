import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { f as from_svg, b as append, p as push, q as createEventDispatcher, D as comment, v as first_child, o as pop } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { i as init } from "./DB0xzveP.js";
import { b as IconButton } from "./DXi4jxVF.js";
import { M as Maximize } from "./BS-YSHQt.js";
var root = from_svg(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-minimize" width="100%" height="100%"><path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"></path></svg>`);
function Minimize($$anchor) {
  var svg = root();
  append($$anchor, svg);
}
function FullscreenButton($$anchor, $$props) {
  push($$props, false);
  const dispatch = createEventDispatcher();
  let fullscreen = prop($$props, "fullscreen", 8);
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      IconButton($$anchor2, {
        get Icon() {
          return Minimize;
        },
        label: "Exit fullscreen mode",
        $$events: { click: () => dispatch("fullscreen", false) }
      });
    };
    var alternate = ($$anchor2) => {
      IconButton($$anchor2, {
        get Icon() {
          return Maximize;
        },
        label: "Fullscreen",
        $$events: { click: () => dispatch("fullscreen", true) }
      });
    };
    if_block(node, ($$render) => {
      if (fullscreen()) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  FullscreenButton as F
};
//# sourceMappingURL=BAYq2deR.js.map
