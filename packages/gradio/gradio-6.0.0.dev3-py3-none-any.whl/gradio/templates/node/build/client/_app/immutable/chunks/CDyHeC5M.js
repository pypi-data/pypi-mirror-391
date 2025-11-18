import { p as set_style } from "./DXi4jxVF.js";
import { ac, ai, g, ah, g as g2 } from "./DXi4jxVF.js";
import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { D as comment, v as first_child, b as append, c as from_html, t as template_effect } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
var root_1 = from_html(`<div class="streaming-bar svelte-1au5sp1"></div>`);
function StreamingBar($$anchor, $$props) {
  let time_limit = prop($$props, "time_limit", 8);
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      var div = root_1();
      let styles;
      template_effect(() => styles = set_style(div, "", styles, { "animation-duration": `${time_limit() ?? ""}s` }));
      append($$anchor2, div);
    };
    if_block(node, ($$render) => {
      if (time_limit()) $$render(consequent);
    });
  }
  append($$anchor, fragment);
}
export {
  ac as Loader,
  ai as LoadingStatus,
  g as StatusTracker,
  StreamingBar,
  ah as Toast,
  g2 as default
};
//# sourceMappingURL=CDyHeC5M.js.map
