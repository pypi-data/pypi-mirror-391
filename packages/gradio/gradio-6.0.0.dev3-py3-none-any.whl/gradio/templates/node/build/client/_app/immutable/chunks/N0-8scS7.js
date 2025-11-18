import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { f as from_svg, b as append, p as push, q as createEventDispatcher, I as onMount, a0 as afterUpdate, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, k as get, n as legacy_pre_effect_reset, c as from_html, d as child, s as sibling, y as untrack, r as reset, t as template_effect, z as event, o as pop, v as first_child, E as next, g as set_text, D as comment, K as tick, x as derived_safe_equal, A as user_derived, W as to_array, N as onDestroy } from "./DEzry6cj.js";
import { p as prop, i as if_block, b as bind_this } from "./DUftb7my.js";
import { a as set_class, t as each, v as index, c as bubble_event, s as set_attribute, p as set_style, I as IconButtonWrapper, b as IconButton, H as Check, J as Copy } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { E as Empty } from "./B-xg5Dhl.js";
var root$1 = from_svg(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--mdi" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" viewBox="0 0 24 24"><path fill="currentColor" d="M5 3h2v2H5v5a2 2 0 0 1-2 2a2 2 0 0 1 2 2v5h2v2H5c-1.07-.27-2-.9-2-2v-4a2 2 0 0 0-2-2H0v-2h1a2 2 0 0 0 2-2V5a2 2 0 0 1 2-2m14 0a2 2 0 0 1 2 2v4a2 2 0 0 0 2 2h1v2h-1a2 2 0 0 0-2 2v4a2 2 0 0 1-2 2h-2v-2h2v-5a2 2 0 0 1 2-2a2 2 0 0 1-2-2V5h-2V3h2m-7 12a1 1 0 0 1 1 1a1 1 0 0 1-1 1a1 1 0 0 1-1-1a1 1 0 0 1 1-1m-4 0a1 1 0 0 1 1 1a1 1 0 0 1-1 1a1 1 0 0 1-1-1a1 1 0 0 1 1-1m8 0a1 1 0 0 1 1 1a1 1 0 0 1-1 1a1 1 0 0 1-1-1a1 1 0 0 1 1-1Z"></path></svg>`);
function JSON$1($$anchor) {
  var svg = root$1();
  append($$anchor, svg);
}
var root_1$1 = from_html(`<button class="toggle svelte-1olemhd"></button>`);
var root_2 = from_html(`<span class="key svelte-1olemhd"> </span><span class="punctuation colon svelte-1olemhd">:</span>`, 1);
var root_4$1 = from_html(`<button class="preview svelte-1olemhd"> </button> <span> </span>`, 1);
var root_3 = from_html(`<span> </span> <!>`, 1);
var root_6 = from_html(`<span class="value string svelte-1olemhd"> </span>`);
var root_8 = from_html(`<span class="value number svelte-1olemhd"> </span>`);
var root_10 = from_html(`<span class="value bool svelte-1olemhd"> </span>`);
var root_12 = from_html(`<span class="value null svelte-1olemhd">null</span>`);
var root_13 = from_html(`<span> </span>`);
var root_14 = from_html(`<span class="punctuation svelte-1olemhd">,</span>`);
var root_17 = from_html(`<span class="punctuation svelte-1olemhd">,</span>`);
var root_15 = from_html(`<div><!> <div class="line svelte-1olemhd"><span class="line-number svelte-1olemhd"></span> <span class="content svelte-1olemhd"><span> </span> <!></span></div></div>`);
var root = from_html(`<div><div><span class="line-number svelte-1olemhd"></span> <span class="content svelte-1olemhd"><!> <!> <!> <!></span></div> <!></div>`);
function JSONNode($$anchor, $$props) {
  push($$props, false);
  const collapsed = mutable_source();
  let value = prop($$props, "value", 8);
  let depth = prop($$props, "depth", 8, 0);
  let is_root = prop($$props, "is_root", 8, false);
  let is_last_item = prop($$props, "is_last_item", 8, true);
  let key = prop($$props, "key", 8, null);
  let open = prop($$props, "open", 8, false);
  let theme_mode = prop($$props, "theme_mode", 8, "system");
  let show_indices = prop($$props, "show_indices", 8, false);
  let interactive = prop($$props, "interactive", 8, true);
  const dispatch = createEventDispatcher();
  let root_element = mutable_source();
  let child_nodes = mutable_source([]);
  function is_collapsible(val) {
    return val !== null && (typeof val === "object" || Array.isArray(val));
  }
  async function toggle_collapse() {
    set(collapsed, !get(collapsed));
    await tick();
    dispatch("toggle", { collapsed: get(collapsed), depth: depth() });
  }
  function get_collapsed_preview(val) {
    if (Array.isArray(val)) return `Array(${val.length})`;
    if (typeof val === "object" && val !== null) return `Object(${Object.keys(val).length})`;
    return String(val);
  }
  function updateLineNumbers() {
    const lines = get(root_element).querySelectorAll(".line");
    lines.forEach((line, index2) => {
      const line_number = line.querySelector(".line-number");
      if (line_number) {
        line_number.setAttribute("data-pseudo-content", (index2 + 1).toString());
        line_number?.setAttribute("aria-roledescription", `Line number ${index2 + 1}`);
        line_number?.setAttribute("title", `Line number ${index2 + 1}`);
      }
    });
  }
  onMount(() => {
    if (is_root()) {
      updateLineNumbers();
    }
  });
  afterUpdate(() => {
    if (is_root()) {
      updateLineNumbers();
    }
  });
  legacy_pre_effect(() => (deep_read_state(open()), deep_read_state(depth())), () => {
    set(collapsed, open() ? false : depth() >= 3);
  });
  legacy_pre_effect(() => deep_read_state(value()), () => {
    if (is_collapsible(value())) {
      set(child_nodes, Object.entries(value()));
    } else {
      set(child_nodes, []);
    }
  });
  legacy_pre_effect(() => (deep_read_state(is_root()), get(root_element)), () => {
    if (is_root() && get(root_element)) {
      updateLineNumbers();
    }
  });
  legacy_pre_effect_reset();
  init();
  var div = root();
  let classes;
  var div_1 = child(div);
  let classes_1;
  var span = sibling(child(div_1), 2);
  var node = child(span);
  {
    var consequent = ($$anchor2) => {
      var button = root_1$1();
      template_effect(() => {
        set_attribute(button, "data-pseudo-content", interactive() ? get(collapsed) ? "▶" : "▼" : "");
        set_attribute(button, "aria-label", get(collapsed) ? "Expand" : "Collapse");
        button.disabled = !interactive();
      });
      event("click", button, toggle_collapse);
      append($$anchor2, button);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(value()), untrack(() => is_collapsible(value()))) $$render(consequent);
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent_1 = ($$anchor2) => {
      var fragment = root_2();
      var span_1 = first_child(fragment);
      var text = child(span_1);
      reset(span_1);
      next();
      template_effect(() => set_text(text, `"${key() ?? ""}"`));
      append($$anchor2, fragment);
    };
    if_block(node_1, ($$render) => {
      if (key() !== null) $$render(consequent_1);
    });
  }
  var node_2 = sibling(node_1, 2);
  {
    var consequent_3 = ($$anchor2) => {
      var fragment_1 = root_3();
      var span_2 = first_child(fragment_1);
      let classes_2;
      var text_1 = child(span_2, true);
      reset(span_2);
      var node_3 = sibling(span_2, 2);
      {
        var consequent_2 = ($$anchor3) => {
          var fragment_2 = root_4$1();
          var button_1 = first_child(fragment_2);
          var text_2 = child(button_1, true);
          reset(button_1);
          var span_3 = sibling(button_1, 2);
          let classes_3;
          var text_3 = child(span_3, true);
          reset(span_3);
          template_effect(
            ($0, $1, $2) => {
              set_text(text_2, $0);
              classes_3 = set_class(span_3, 1, "punctuation bracket svelte-1olemhd", null, classes_3, $1);
              set_text(text_3, $2);
            },
            [
              () => (deep_read_state(value()), untrack(() => get_collapsed_preview(value()))),
              () => ({ "square-bracket": Array.isArray(value()) }),
              () => (deep_read_state(value()), untrack(() => Array.isArray(value()) ? "]" : "}"))
            ]
          );
          event("click", button_1, toggle_collapse);
          append($$anchor3, fragment_2);
        };
        if_block(node_3, ($$render) => {
          if (get(collapsed)) $$render(consequent_2);
        });
      }
      template_effect(
        ($0, $1) => {
          classes_2 = set_class(span_2, 1, "punctuation bracket svelte-1olemhd", null, classes_2, $0);
          set_text(text_1, $1);
        },
        [
          () => ({ "square-bracket": Array.isArray(value()) }),
          () => (deep_read_state(value()), untrack(() => Array.isArray(value()) ? "[" : "{"))
        ]
      );
      append($$anchor2, fragment_1);
    };
    var alternate_4 = ($$anchor2) => {
      var fragment_3 = comment();
      var node_4 = first_child(fragment_3);
      {
        var consequent_4 = ($$anchor3) => {
          var span_4 = root_6();
          var text_4 = child(span_4);
          reset(span_4);
          template_effect(() => set_text(text_4, `"${value() ?? ""}"`));
          append($$anchor3, span_4);
        };
        var alternate_3 = ($$anchor3) => {
          var fragment_4 = comment();
          var node_5 = first_child(fragment_4);
          {
            var consequent_5 = ($$anchor4) => {
              var span_5 = root_8();
              var text_5 = child(span_5, true);
              reset(span_5);
              template_effect(() => set_text(text_5, value()));
              append($$anchor4, span_5);
            };
            var alternate_2 = ($$anchor4) => {
              var fragment_5 = comment();
              var node_6 = first_child(fragment_5);
              {
                var consequent_6 = ($$anchor5) => {
                  var span_6 = root_10();
                  var text_6 = child(span_6, true);
                  reset(span_6);
                  template_effect(($0) => set_text(text_6, $0), [
                    () => (deep_read_state(value()), untrack(() => value().toString()))
                  ]);
                  append($$anchor5, span_6);
                };
                var alternate_1 = ($$anchor5) => {
                  var fragment_6 = comment();
                  var node_7 = first_child(fragment_6);
                  {
                    var consequent_7 = ($$anchor6) => {
                      var span_7 = root_12();
                      append($$anchor6, span_7);
                    };
                    var alternate = ($$anchor6) => {
                      var span_8 = root_13();
                      var text_7 = child(span_8, true);
                      reset(span_8);
                      template_effect(() => set_text(text_7, value()));
                      append($$anchor6, span_8);
                    };
                    if_block(
                      node_7,
                      ($$render) => {
                        if (value() === null) $$render(consequent_7);
                        else $$render(alternate, false);
                      },
                      true
                    );
                  }
                  append($$anchor5, fragment_6);
                };
                if_block(
                  node_6,
                  ($$render) => {
                    if (typeof value() === "boolean") $$render(consequent_6);
                    else $$render(alternate_1, false);
                  },
                  true
                );
              }
              append($$anchor4, fragment_5);
            };
            if_block(
              node_5,
              ($$render) => {
                if (typeof value() === "number") $$render(consequent_5);
                else $$render(alternate_2, false);
              },
              true
            );
          }
          append($$anchor3, fragment_4);
        };
        if_block(
          node_4,
          ($$render) => {
            if (typeof value() === "string") $$render(consequent_4);
            else $$render(alternate_3, false);
          },
          true
        );
      }
      append($$anchor2, fragment_3);
    };
    if_block(node_2, ($$render) => {
      if (deep_read_state(value()), untrack(() => is_collapsible(value()))) $$render(consequent_3);
      else $$render(alternate_4, false);
    });
  }
  var node_8 = sibling(node_2, 2);
  {
    var consequent_8 = ($$anchor2) => {
      var span_9 = root_14();
      append($$anchor2, span_9);
    };
    if_block(node_8, ($$render) => {
      if (deep_read_state(is_last_item()), deep_read_state(value()), get(collapsed), untrack(() => !is_last_item() && (!is_collapsible(value()) || get(collapsed)))) $$render(consequent_8);
    });
  }
  reset(span);
  reset(div_1);
  var node_9 = sibling(div_1, 2);
  {
    var consequent_10 = ($$anchor2) => {
      var div_2 = root_15();
      let classes_4;
      var node_10 = child(div_2);
      each(node_10, 1, () => get(child_nodes), index, ($$anchor3, $$item, i) => {
        var $$array = user_derived(() => to_array(get($$item), 2));
        let subKey = () => get($$array)[0];
        let subVal = () => get($$array)[1];
        var fragment_7 = comment();
        var node_11 = first_child(fragment_7);
        {
          let $0 = derived_safe_equal(() => depth() + 1);
          let $1 = derived_safe_equal(() => (get(child_nodes), untrack(() => i === get(child_nodes).length - 1)));
          let $2 = derived_safe_equal(() => (deep_read_state(value()), deep_read_state(show_indices()), subKey(), untrack(() => Array.isArray(value()) && !show_indices() ? null : subKey())));
          JSONNode(node_11, {
            get value() {
              return subVal();
            },
            get depth() {
              return get($0);
            },
            get is_last_item() {
              return get($1);
            },
            get key() {
              return get($2);
            },
            get open() {
              return open();
            },
            get theme_mode() {
              return theme_mode();
            },
            get show_indices() {
              return show_indices();
            },
            $$events: {
              toggle($$arg) {
                bubble_event.call(this, $$props, $$arg);
              }
            }
          });
        }
        append($$anchor3, fragment_7);
      });
      var div_3 = sibling(node_10, 2);
      var span_10 = sibling(child(div_3), 2);
      var span_11 = child(span_10);
      let classes_5;
      var text_8 = child(span_11, true);
      reset(span_11);
      var node_12 = sibling(span_11, 2);
      {
        var consequent_9 = ($$anchor3) => {
          var span_12 = root_17();
          append($$anchor3, span_12);
        };
        if_block(node_12, ($$render) => {
          if (!is_last_item()) $$render(consequent_9);
        });
      }
      reset(span_10);
      reset(div_3);
      reset(div_2);
      template_effect(
        ($0, $1) => {
          classes_4 = set_class(div_2, 1, "children svelte-1olemhd", null, classes_4, { hidden: get(collapsed) });
          classes_5 = set_class(span_11, 1, "punctuation bracket svelte-1olemhd", null, classes_5, $0);
          set_text(text_8, $1);
        },
        [
          () => ({ "square-bracket": Array.isArray(value()) }),
          () => (deep_read_state(value()), untrack(() => Array.isArray(value()) ? "]" : "}"))
        ]
      );
      append($$anchor2, div_2);
    };
    if_block(node_9, ($$render) => {
      if (deep_read_state(value()), untrack(() => is_collapsible(value()))) $$render(consequent_10);
    });
  }
  reset(div);
  bind_this(div, ($$value) => set(root_element, $$value), () => get(root_element));
  template_effect(() => {
    classes = set_class(div, 1, "json-node svelte-1olemhd", null, classes, { root: is_root(), "dark-mode": theme_mode() === "dark" });
    set_style(div, `--depth: ${depth() ?? ""};`);
    classes_1 = set_class(div_1, 1, "line svelte-1olemhd", null, classes_1, { collapsed: get(collapsed) });
  });
  event("toggle", div, function($$arg) {
    bubble_event.call(this, $$props, $$arg);
  });
  append($$anchor, div);
  pop();
}
var root_1 = from_html(`<!> <div class="json-holder svelte-1lc38wd"><!></div>`, 1);
var root_4 = from_html(`<div class="empty-wrapper svelte-1lc38wd"><!></div>`);
function JSON_1($$anchor, $$props) {
  push($$props, false);
  const json_max_height = mutable_source();
  let value = prop($$props, "value", 24, () => ({}));
  let open = prop($$props, "open", 8, false);
  let theme_mode = prop($$props, "theme_mode", 8, "system");
  let show_indices = prop($$props, "show_indices", 8, false);
  let label_height = prop($$props, "label_height", 8);
  let interactive = prop($$props, "interactive", 8, true);
  let show_copy_button = prop($$props, "show_copy_button", 8, true);
  let copied = mutable_source(false);
  let timer;
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
  async function handle_copy() {
    if ("clipboard" in navigator) {
      await navigator.clipboard.writeText(JSON.stringify(value(), null, 2));
      copy_feedback();
    }
  }
  function is_empty(obj) {
    return obj && Object.keys(obj).length === 0 && Object.getPrototypeOf(obj) === Object.prototype && JSON.stringify(obj) === JSON.stringify({});
  }
  onDestroy(() => {
    if (timer) clearTimeout(timer);
  });
  legacy_pre_effect(() => deep_read_state(label_height()), () => {
    set(json_max_height, `calc(100% - ${label_height()}px)`);
  });
  legacy_pre_effect_reset();
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent_1 = ($$anchor2) => {
      var fragment_1 = root_1();
      var node_1 = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          IconButtonWrapper($$anchor3, {
            children: ($$anchor4, $$slotProps) => {
              {
                let $0 = derived_safe_equal(() => get(copied) ? "Copied" : "Copy");
                let $1 = derived_safe_equal(() => get(copied) ? Check : Copy);
                IconButton($$anchor4, {
                  show_label: false,
                  get label() {
                    return get($0);
                  },
                  get Icon() {
                    return get($1);
                  },
                  $$events: { click: () => handle_copy() }
                });
              }
            },
            $$slots: { default: true }
          });
        };
        if_block(node_1, ($$render) => {
          if (show_copy_button()) $$render(consequent);
        });
      }
      var div = sibling(node_1, 2);
      let styles;
      var node_2 = child(div);
      JSONNode(node_2, {
        get value() {
          return value();
        },
        depth: 0,
        is_root: true,
        get open() {
          return open();
        },
        get theme_mode() {
          return theme_mode();
        },
        get show_indices() {
          return show_indices();
        },
        get interactive() {
          return interactive();
        }
      });
      reset(div);
      template_effect(() => styles = set_style(div, "", styles, { "max-height": get(json_max_height) }));
      append($$anchor2, fragment_1);
    };
    var alternate = ($$anchor2) => {
      var div_1 = root_4();
      var node_3 = child(div_1);
      Empty(node_3, {
        children: ($$anchor3, $$slotProps) => {
          JSON$1($$anchor3);
        },
        $$slots: { default: true }
      });
      reset(div_1);
      append($$anchor2, div_1);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(value()), untrack(() => value() && value() !== '""' && !is_empty(value()))) $$render(consequent_1);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  JSON_1 as J,
  JSON$1 as a
};
//# sourceMappingURL=N0-8scS7.js.map
