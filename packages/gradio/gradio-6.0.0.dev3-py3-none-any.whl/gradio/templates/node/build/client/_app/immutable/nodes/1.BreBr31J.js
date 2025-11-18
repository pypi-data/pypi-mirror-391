import "../chunks/9B4_veAf.js";
import "../chunks/BAp-OWo-.js";
import { p as push, c as from_html, v as first_child, d as child, r as reset, s as sibling, t as template_effect, b as append, o as pop, g as set_text } from "../chunks/DEzry6cj.js";
import { p as page$1, i as init } from "../chunks/DB0xzveP.js";
const page = page$1;
var root = from_html(`<h1> </h1> <p> </p>`, 1);
function Error($$anchor, $$props) {
  push($$props, false);
  init();
  var fragment = root();
  var h1 = first_child(fragment);
  var text = child(h1, true);
  reset(h1);
  var p = sibling(h1, 2);
  var text_1 = child(p, true);
  reset(p);
  template_effect(() => {
    set_text(text, page.status);
    set_text(text_1, page.error?.message);
  });
  append($$anchor, fragment);
  pop();
}
export {
  Error as component
};
//# sourceMappingURL=1.BreBr31J.js.map
