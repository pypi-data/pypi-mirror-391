import "./9B4_veAf.js";
import { p as push, c as from_html, d as child, r as reset, t as template_effect, b as append, o as pop, k as get, A as user_derived } from "./DEzry6cj.js";
import { s as set_attribute } from "./DXi4jxVF.js";
var root = from_html(`<div class="matplotlib layout svelte-n8pych"><img class="svelte-n8pych"/></div>`);
function MatplotlibPlot($$anchor, $$props) {
  push($$props, true);
  let plot = user_derived(() => $$props.value?.plot);
  var div = root();
  set_attribute(div, "data-testid", "matplotlib");
  var img = child(div);
  reset(div);
  template_effect(() => {
    set_attribute(img, "src", get(plot));
    set_attribute(img, "alt", `${$$props.value.chart} plot visualising provided data`);
  });
  append($$anchor, div);
  pop();
}
export {
  MatplotlibPlot as default
};
//# sourceMappingURL=CuZnhSmJ.js.map
