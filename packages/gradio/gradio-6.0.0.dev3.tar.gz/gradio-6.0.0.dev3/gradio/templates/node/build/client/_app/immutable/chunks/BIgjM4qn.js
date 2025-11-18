import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, i as legacy_pre_effect, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, s as sibling, r as reset, t as template_effect, y as untrack, b as append, o as pop, k as get, x as derived_safe_equal, m as mutable_source, j as set } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { M as MarkdownCode, y as action, E as css_units, a as set_class, s as set_attribute, p as set_style, I as IconButtonWrapper, b as IconButton, H as Check, J as Copy, K as copy } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
var root = from_html(`<div data-testid="markdown"><!> <!></div>`);
function Markdown($$anchor, $$props) {
  push($$props, false);
  let elem_classes = prop($$props, "elem_classes", 24, () => []);
  let visible = prop($$props, "visible", 8, true);
  let value = prop($$props, "value", 8);
  let min_height = prop($$props, "min_height", 8, void 0);
  let rtl = prop($$props, "rtl", 8, false);
  let sanitize_html = prop($$props, "sanitize_html", 8, true);
  let line_breaks = prop($$props, "line_breaks", 8, false);
  let latex_delimiters = prop($$props, "latex_delimiters", 8);
  let header_links = prop($$props, "header_links", 8, false);
  let height = prop($$props, "height", 8, void 0);
  let show_copy_button = prop($$props, "show_copy_button", 8, false);
  let loading_status = prop($$props, "loading_status", 8, void 0);
  let theme_mode = prop($$props, "theme_mode", 8);
  let copied = mutable_source(false);
  let timer;
  const dispatch = createEventDispatcher();
  async function handle_copy() {
    if ("clipboard" in navigator) {
      await navigator.clipboard.writeText(value());
      dispatch("copy", { value: value() });
      copy_feedback();
    }
  }
  function copy_feedback() {
    set(copied, true);
    if (timer) clearTimeout(timer);
    timer = setTimeout(
      () => {
        set(copied, false);
      },
      1e3
    );
  }
  legacy_pre_effect(() => deep_read_state(value()), () => {
    value(), dispatch("change");
  });
  legacy_pre_effect_reset();
  init();
  var div = root();
  let classes;
  let styles;
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      IconButtonWrapper($$anchor2, {
        children: ($$anchor3, $$slotProps) => {
          {
            let $0 = derived_safe_equal(() => get(copied) ? Check : Copy);
            let $1 = derived_safe_equal(() => get(copied) ? "Copied conversation" : "Copy conversation");
            IconButton($$anchor3, {
              get Icon() {
                return get($0);
              },
              get label() {
                return get($1);
              },
              $$events: { click: handle_copy }
            });
          }
        },
        $$slots: { default: true }
      });
    };
    if_block(node, ($$render) => {
      if (show_copy_button()) $$render(consequent);
    });
  }
  var node_1 = sibling(node, 2);
  MarkdownCode(node_1, {
    get message() {
      return value();
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
    chatbot: false,
    get header_links() {
      return header_links();
    },
    get theme_mode() {
      return theme_mode();
    }
  });
  reset(div);
  action(div, ($$node) => copy?.($$node));
  template_effect(
    ($0, $1, $2) => {
      classes = set_class(div, 1, `prose ${$0 ?? ""}`, "svelte-1xjkzpp", classes, { hide: !visible() });
      set_attribute(div, "dir", rtl() ? "rtl" : "ltr");
      styles = set_style(div, $1, styles, $2);
      div.dir = div.dir;
    },
    [
      () => (deep_read_state(elem_classes()), untrack(() => elem_classes()?.join(" ") || "")),
      () => (deep_read_state(height()), deep_read_state(css_units), untrack(() => height() ? `max-height: ${css_units(height())}; overflow-y: auto;` : "")),
      () => ({
        "min-height": (deep_read_state(min_height()), deep_read_state(loading_status()), deep_read_state(css_units), untrack(() => min_height() && loading_status()?.status !== "pending" ? css_units(min_height()) : void 0))
      })
    ]
  );
  append($$anchor, div);
  pop();
}
export {
  Markdown as M
};
//# sourceMappingURL=BIgjM4qn.js.map
