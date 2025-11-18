import "./9B4_veAf.js";
import { p as push, I as onMount, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, s as sibling, k as get, r as reset, t as template_effect, y as untrack, b as append, o as pop, z as event, g as set_text, v as first_child } from "./DEzry6cj.js";
import { p as prop, i as if_block, b as bind_this, r as rest_props } from "./DUftb7my.js";
import { p as set_style, t as each, a3 as Prism$1, s as set_attribute, a as set_class, D as html, G as Gradio } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { i as init } from "./DB0xzveP.js";
var prismTypescript = {};
var hasRequiredPrismTypescript;
function requirePrismTypescript() {
  if (hasRequiredPrismTypescript) return prismTypescript;
  hasRequiredPrismTypescript = 1;
  (function(Prism2) {
    Prism2.languages.typescript = Prism2.languages.extend("javascript", {
      "class-name": {
        pattern: /(\b(?:class|extends|implements|instanceof|interface|new|type)\s+)(?!keyof\b)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?:\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>)?/,
        lookbehind: true,
        greedy: true,
        inside: null
        // see below
      },
      "builtin": /\b(?:Array|Function|Promise|any|boolean|console|never|number|string|symbol|unknown)\b/
    });
    Prism2.languages.typescript.keyword.push(
      /\b(?:abstract|declare|is|keyof|readonly|require)\b/,
      // keywords that have to be followed by an identifier
      /\b(?:asserts|infer|interface|module|namespace|type)\b(?=\s*(?:[{_$a-zA-Z\xA0-\uFFFF]|$))/,
      // This is for `import type *, {}`
      /\btype\b(?=\s*(?:[\{*]|$))/
    );
    delete Prism2.languages.typescript["parameter"];
    delete Prism2.languages.typescript["literal-property"];
    var typeInside = Prism2.languages.extend("typescript", {});
    delete typeInside["class-name"];
    Prism2.languages.typescript["class-name"].inside = typeInside;
    Prism2.languages.insertBefore("typescript", "function", {
      "decorator": {
        pattern: /@[$\w\xA0-\uFFFF]+/,
        inside: {
          "at": {
            pattern: /^@/,
            alias: "operator"
          },
          "function": /^[\s\S]+/
        }
      },
      "generic-function": {
        // e.g. foo<T extends "bar" | "baz">( ...
        pattern: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>(?=\s*\()/,
        greedy: true,
        inside: {
          "function": /^#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*/,
          "generic": {
            pattern: /<[\s\S]+/,
            // everything after the first <
            alias: "class-name",
            inside: typeInside
          }
        }
      }
    });
    Prism2.languages.ts = Prism2.languages.typescript;
  })(Prism);
  return prismTypescript;
}
requirePrismTypescript();
var root_1 = from_html(`<div class="header svelte-1kuiw39"><span class="title svelte-1kuiw39"> </span> <button class="toggle-all svelte-1kuiw39">▼</button></div>`);
var root_4 = from_html(`<a class="param-link svelte-1kuiw39"><span class="link-icon svelte-1kuiw39">🔗</span></a>`);
var root_5 = from_html(`: <!>`, 1);
var root_6 = from_html(`<div><span class="svelte-1kuiw39">default</span> <code class="svelte-1kuiw39">= <!></code></div>`);
var root_7 = from_html(`<div class="description svelte-1kuiw39"><p><!></p></div>`);
var root_3 = from_html(`<details class="param md svelte-1kuiw39"><summary class="type svelte-1kuiw39"><!> <pre><code class="svelte-1kuiw39"> <!></code></pre></summary> <!> <!></details>`);
var root_2 = from_html(`<div class="param-content svelte-1kuiw39"></div>`);
var root = from_html(`<div class="wrap svelte-1kuiw39"><!> <!></div>`);
function ParamViewer($$anchor, $$props) {
  push($$props, false);
  let docs = prop($$props, "docs", 8);
  let lang = prop($$props, "lang", 8, "python");
  let linkify = prop($$props, "linkify", 24, () => []);
  let header = prop($$props, "header", 8);
  let anchor_links = prop($$props, "anchor_links", 8, false);
  let max_height = prop($$props, "max_height", 8, void 0);
  let component_root = mutable_source();
  let _docs = mutable_source();
  let all_open = mutable_source(false);
  function create_slug(name, anchor_links2) {
    let prefix = "param-";
    if (typeof anchor_links2 === "string") {
      prefix += anchor_links2 + "-";
    }
    return prefix + name.toLowerCase().replace(/[^a-z0-9]+/g, "-");
  }
  function highlight(code, lang2) {
    let highlighted = Prism$1.highlight(code, Prism$1.languages[lang2], lang2);
    for (const link of linkify()) {
      highlighted = highlighted.replace(new RegExp(link, "g"), `<a href="#h-${link.toLocaleLowerCase()}">${link}</a>`);
    }
    return highlighted;
  }
  function highlight_code(_docs2, lang2) {
    if (!_docs2) {
      return [];
    }
    return Object.entries(_docs2).map(([name, { type, description, default: _default }]) => {
      let highlighted_type = type ? highlight(type, lang2) : null;
      return {
        name,
        type: highlighted_type,
        description,
        default: _default ? highlight(_default, lang2) : null
      };
    });
  }
  function toggle_all() {
    set(all_open, !get(all_open));
    const details = get(component_root).querySelectorAll(".param");
    details.forEach((detail) => {
      if (detail instanceof HTMLDetailsElement) {
        detail.open = get(all_open);
      }
    });
  }
  function render_links(description) {
    const escaped = description.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    const markdown_links = escaped.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    return markdown_links;
  }
  onMount(() => {
    if (window.location.hash) {
      open_parameter_from_hash(window.location.hash);
    }
    window.addEventListener("hashchange", (e) => {
      open_parameter_from_hash(window.location.hash);
    });
  });
  function open_parameter_from_hash(hash) {
    if (!get(component_root)) return;
    const id = hash.slice(1);
    const detail = get(component_root).querySelector(`#${id}`);
    if (detail instanceof HTMLDetailsElement) {
      detail.open = true;
      detail.scrollIntoView({ behavior: "smooth" });
    }
  }
  const get_dimension = (dimension_value) => {
    if (dimension_value === void 0) {
      return void 0;
    }
    if (typeof dimension_value === "number") {
      return dimension_value + "px";
    } else if (typeof dimension_value === "string") {
      return dimension_value;
    }
  };
  legacy_pre_effect(() => (deep_read_state(docs()), deep_read_state(lang())), () => {
    set(_docs, highlight_code(docs(), lang()));
  });
  legacy_pre_effect_reset();
  init();
  var div = root();
  let styles;
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      var div_1 = root_1();
      var span = child(div_1);
      var text = child(span, true);
      reset(span);
      var button = sibling(span, 2);
      reset(div_1);
      template_effect(() => {
        set_text(text, header());
        set_attribute(button, "title", get(all_open) ? "Close All" : "Open All");
      });
      event("click", button, toggle_all);
      append($$anchor2, div_1);
    };
    if_block(node, ($$render) => {
      if (header() !== null) $$render(consequent);
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent_5 = ($$anchor2) => {
      var div_2 = root_2();
      each(div_2, 5, () => get(_docs), ({ type, description, default: _default, name }) => name, ($$anchor3, $$item) => {
        let type = () => get($$item).type;
        let description = () => get($$item).description;
        let _default = () => get($$item).default;
        let name = () => get($$item).name;
        var details_1 = root_3();
        var summary = child(details_1);
        var node_2 = child(summary);
        {
          var consequent_1 = ($$anchor4) => {
            var a = root_4();
            template_effect(($0) => set_attribute(a, "href", `#${$0 ?? ""}`), [
              () => (name(), deep_read_state(anchor_links()), untrack(() => create_slug(name() || "", anchor_links())))
            ]);
            append($$anchor4, a);
          };
          if_block(node_2, ($$render) => {
            if (anchor_links()) $$render(consequent_1);
          });
        }
        var pre = sibling(node_2, 2);
        var code_1 = child(pre);
        var text_1 = child(code_1, true);
        var node_3 = sibling(text_1);
        {
          var consequent_2 = ($$anchor4) => {
            var fragment = root_5();
            var node_4 = sibling(first_child(fragment));
            html(node_4, type);
            append($$anchor4, fragment);
          };
          if_block(node_3, ($$render) => {
            if (type()) $$render(consequent_2);
          });
        }
        reset(code_1);
        reset(pre);
        reset(summary);
        var node_5 = sibling(summary, 2);
        {
          var consequent_3 = ($$anchor4) => {
            var div_3 = root_6();
            let classes;
            var span_1 = child(div_3);
            set_style(span_1, "", {}, { "padding-right": "4px" });
            var code_2 = sibling(span_1, 2);
            var node_6 = sibling(child(code_2));
            html(node_6, _default);
            reset(code_2);
            reset(div_3);
            template_effect(() => classes = set_class(div_3, 1, "default svelte-1kuiw39", null, classes, { last: !description() }));
            append($$anchor4, div_3);
          };
          if_block(node_5, ($$render) => {
            if (_default()) $$render(consequent_3);
          });
        }
        var node_7 = sibling(node_5, 2);
        {
          var consequent_4 = ($$anchor4) => {
            var div_4 = root_7();
            var p = child(div_4);
            var node_8 = child(p);
            html(node_8, () => (description(), untrack(() => render_links(description()))));
            reset(p);
            reset(div_4);
            append($$anchor4, div_4);
          };
          if_block(node_7, ($$render) => {
            if (description()) $$render(consequent_4);
          });
        }
        reset(details_1);
        template_effect(
          ($0) => {
            set_attribute(details_1, "id", $0);
            set_class(pre, 1, `language-${lang() ?? ""}`, "svelte-1kuiw39");
            set_text(text_1, name());
          },
          [
            () => (deep_read_state(anchor_links()), name(), untrack(() => anchor_links() ? create_slug(name() || "", anchor_links()) : void 0))
          ]
        );
        append($$anchor3, details_1);
      });
      reset(div_2);
      append($$anchor2, div_2);
    };
    if_block(node_1, ($$render) => {
      if (get(_docs)) $$render(consequent_5);
    });
  }
  reset(div);
  bind_this(div, ($$value) => set(component_root, $$value), () => get(component_root));
  template_effect(($0) => styles = set_style(div, "", styles, $0), [
    () => ({
      "max-height": (deep_read_state(max_height()), untrack(() => get_dimension(max_height())))
    })
  ]);
  append($$anchor, div);
  pop();
}
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  ParamViewer($$anchor, {
    get docs() {
      return gradio.props.value;
    },
    get linkify() {
      return gradio.props.linkify;
    },
    get header() {
      return gradio.props.header;
    },
    get anchor_links() {
      return gradio.props.anchor_links;
    },
    get max_height() {
      return gradio.props.max_height;
    }
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=DJoh2taj.js.map
