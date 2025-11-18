import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { c as from_html, d as child, k as get, x as derived_safe_equal, r as reset, t as template_effect, b as append, y as untrack, u as deep_read_state } from "./DEzry6cj.js";
import { M as MarkdownCode, a as set_class } from "./DXi4jxVF.js";
import { p as prop } from "./DUftb7my.js";
/* empty css         */
var root = from_html(`<div><!></div>`);
function Example($$anchor, $$props) {
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  let sanitize_html = prop($$props, "sanitize_html", 8);
  let line_breaks = prop($$props, "line_breaks", 8);
  let latex_delimiters = prop($$props, "latex_delimiters", 8);
  function truncate_text(text, max_length = 60) {
    if (!text) return "";
    const str = String(text);
    if (str.length <= max_length) return str;
    return str.slice(0, max_length) + "...";
  }
  var div = root();
  let classes;
  var node = child(div);
  {
    let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => truncate_text(value()))));
    MarkdownCode(node, {
      get message() {
        return get($0);
      },
      get latex_delimiters() {
        return latex_delimiters();
      },
      get sanitize_html() {
        return sanitize_html();
      },
      get line_breaks() {
        return line_breaks();
      },
      chatbot: false
    });
  }
  reset(div);
  template_effect(() => classes = set_class(div, 1, "prose svelte-11ua876", null, classes, {
    table: type() === "table",
    gallery: type() === "gallery",
    selected: selected()
  }));
  append($$anchor, div);
}
export {
  Example as default
};
//# sourceMappingURL=JuE3hNoR.js.map
