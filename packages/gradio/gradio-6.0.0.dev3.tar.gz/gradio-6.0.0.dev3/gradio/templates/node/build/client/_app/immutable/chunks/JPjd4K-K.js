import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { D as comment, v as first_child, b as append, F as text, t as template_effect, g as set_text } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
function Example($$anchor, $$props) {
  let title = prop($$props, "title", 8);
  let x = prop($$props, "x", 8);
  let y = prop($$props, "y", 8);
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      var text$1 = text();
      template_effect(() => set_text(text$1, title()));
      append($$anchor2, text$1);
    };
    var alternate = ($$anchor2) => {
      var text_1 = text();
      template_effect(() => set_text(text_1, `${x() ?? ""} x ${y() ?? ""}`));
      append($$anchor2, text_1);
    };
    if_block(node, ($$render) => {
      if (title()) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
}
export {
  Example as default
};
//# sourceMappingURL=JPjd4K-K.js.map
