import "./9B4_veAf.js";
import { p as push, i as legacy_pre_effect, j as set, m as mutable_source, k as get, u as deep_read_state, n as legacy_pre_effect_reset, D as comment, v as first_child, y as untrack, b as append, o as pop, c as from_html, d as child, r as reset, s as sibling, t as template_effect, g as set_text, z as event, E as next, x as derived_safe_equal } from "./DEzry6cj.js";
import { p as prop, i as if_block, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { a as set_class, t as each, v as index, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { i as init } from "./DB0xzveP.js";
var root_2 = from_html(`<span class="_jsonSep svelte-10qgcdp">,</span>`);
var root_1$1 = from_html(`<span> </span><!>`, 1);
var root_5 = from_html(`<span class="_jsonSep svelte-10qgcdp">,</span>`);
var root_4 = from_html(`<span role="button" tabindex="0"> </span><!>`, 1);
var root_8 = from_html(`<span class="_jsonKey svelte-10qgcdp"> </span><span class="_jsonSep svelte-10qgcdp">:</span>`, 1);
var root_11 = from_html(`<span class="_jsonSep svelte-10qgcdp">,</span>`);
var root_10 = from_html(`<span> </span><!>`, 1);
var root_7 = from_html(`<li><!> <!></li>`);
var root_12 = from_html(`<span class="_jsonSep svelte-10qgcdp">,</span>`);
var root_6 = from_html(`<span role="button" tabindex="0"> </span> <ul class="_jsonList svelte-10qgcdp"></ul> <span role="button" tabindex="0"> </span><!>`, 1);
function JsonView($$anchor, $$props) {
  push($$props, false);
  let json = prop($$props, "json", 8);
  let depth = prop($$props, "depth", 8, Infinity);
  let _cur = prop($$props, "_cur", 8, 0);
  let _last = prop($$props, "_last", 8, true);
  let items = mutable_source([]);
  let isArray = mutable_source(false);
  let brackets = mutable_source(["", ""]);
  let collapsed = mutable_source(false);
  function getType(i) {
    if (i === null) return "null";
    return typeof i;
  }
  function stringify(i) {
    return JSON.stringify(i);
  }
  function format(i) {
    switch (getType(i)) {
      case "function":
        return "f () {...}";
      case "symbol":
        return i.toString();
      default:
        return stringify(i);
    }
  }
  function clicked() {
    set(collapsed, !get(collapsed));
  }
  function pressed(e) {
    if (e instanceof KeyboardEvent && ["Enter", " "].includes(e.key)) clicked();
  }
  legacy_pre_effect(() => (deep_read_state(json()), get(isArray)), () => {
    set(items, getType(json()) === "object" ? Object.keys(json()) : []);
    set(isArray, Array.isArray(json()));
    set(brackets, get(isArray) ? ["[", "]"] : ["{", "}"]);
  });
  legacy_pre_effect(() => (deep_read_state(depth()), deep_read_state(_cur())), () => {
    set(collapsed, depth() < _cur());
  });
  legacy_pre_effect_reset();
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent_1 = ($$anchor2) => {
      var fragment_1 = root_1$1();
      var span = first_child(fragment_1);
      let classes;
      var text = child(span);
      reset(span);
      var node_1 = sibling(span);
      {
        var consequent = ($$anchor3) => {
          var span_1 = root_2();
          append($$anchor3, span_1);
        };
        if_block(node_1, ($$render) => {
          if (!_last()) $$render(consequent);
        });
      }
      template_effect(() => {
        classes = set_class(span, 1, "_jsonBkt empty svelte-10qgcdp", null, classes, { isArray: get(isArray) });
        set_text(text, `${(get(brackets), untrack(() => get(brackets)[0])) ?? ""}${(get(brackets), untrack(() => get(brackets)[1])) ?? ""}`);
      });
      append($$anchor2, fragment_1);
    };
    var alternate_2 = ($$anchor2) => {
      var fragment_2 = comment();
      var node_2 = first_child(fragment_2);
      {
        var consequent_3 = ($$anchor3) => {
          var fragment_3 = root_4();
          var span_2 = first_child(fragment_3);
          let classes_1;
          var text_1 = child(span_2);
          reset(span_2);
          var node_3 = sibling(span_2);
          {
            var consequent_2 = ($$anchor4) => {
              var span_3 = root_5();
              append($$anchor4, span_3);
            };
            if_block(node_3, ($$render) => {
              if (!_last() && get(collapsed)) $$render(consequent_2);
            });
          }
          template_effect(() => {
            classes_1 = set_class(span_2, 1, "_jsonBkt svelte-10qgcdp", null, classes_1, { isArray: get(isArray) });
            set_text(text_1, `${(get(brackets), untrack(() => get(brackets)[0])) ?? ""}...${(get(brackets), untrack(() => get(brackets)[1])) ?? ""}`);
          });
          event("click", span_2, clicked);
          event("keydown", span_2, pressed);
          append($$anchor3, fragment_3);
        };
        var alternate_1 = ($$anchor3) => {
          var fragment_4 = root_6();
          var span_4 = first_child(fragment_4);
          let classes_2;
          var text_2 = child(span_4, true);
          reset(span_4);
          var ul = sibling(span_4, 2);
          each(ul, 5, () => get(items), index, ($$anchor4, i, idx) => {
            var li = root_7();
            var node_4 = child(li);
            {
              var consequent_4 = ($$anchor5) => {
                var fragment_5 = root_8();
                var span_5 = first_child(fragment_5);
                var text_3 = child(span_5, true);
                reset(span_5);
                next();
                template_effect(($0) => set_text(text_3, $0), [() => (get(i), untrack(() => stringify(get(i))))]);
                append($$anchor5, fragment_5);
              };
              if_block(node_4, ($$render) => {
                if (!get(isArray)) $$render(consequent_4);
              });
            }
            var node_5 = sibling(node_4, 2);
            {
              var consequent_5 = ($$anchor5) => {
                var fragment_6 = comment();
                var node_6 = first_child(fragment_6);
                {
                  let $0 = derived_safe_equal(() => _cur() + 1);
                  let $1 = derived_safe_equal(() => (get(items), untrack(() => idx === get(items).length - 1)));
                  JsonView(node_6, {
                    get json() {
                      return deep_read_state(json()), get(i), untrack(() => json()[get(i)]);
                    },
                    get depth() {
                      return depth();
                    },
                    get _cur() {
                      return get($0);
                    },
                    get _last() {
                      return get($1);
                    }
                  });
                }
                append($$anchor5, fragment_6);
              };
              var alternate = ($$anchor5) => {
                var fragment_7 = root_10();
                var span_6 = first_child(fragment_7);
                var text_4 = child(span_6, true);
                reset(span_6);
                var node_7 = sibling(span_6);
                {
                  var consequent_6 = ($$anchor6) => {
                    var span_7 = root_11();
                    append($$anchor6, span_7);
                  };
                  if_block(node_7, ($$render) => {
                    if (get(items), untrack(() => idx < get(items).length - 1)) $$render(consequent_6);
                  });
                }
                template_effect(
                  ($0, $1) => {
                    set_class(span_6, 1, `_jsonVal ${$0 ?? ""}`, "svelte-10qgcdp");
                    set_text(text_4, $1);
                  },
                  [
                    () => (deep_read_state(json()), get(i), untrack(() => getType(json()[get(i)]))),
                    () => (deep_read_state(json()), get(i), untrack(() => format(json()[get(i)])))
                  ]
                );
                append($$anchor5, fragment_7);
              };
              if_block(node_5, ($$render) => {
                if (deep_read_state(json()), get(i), untrack(() => getType(json()[get(i)]) === "object")) $$render(consequent_5);
                else $$render(alternate, false);
              });
            }
            reset(li);
            append($$anchor4, li);
          });
          reset(ul);
          var span_8 = sibling(ul, 2);
          let classes_3;
          var text_5 = child(span_8, true);
          reset(span_8);
          var node_8 = sibling(span_8);
          {
            var consequent_7 = ($$anchor4) => {
              var span_9 = root_12();
              append($$anchor4, span_9);
            };
            if_block(node_8, ($$render) => {
              if (!_last()) $$render(consequent_7);
            });
          }
          template_effect(() => {
            classes_2 = set_class(span_4, 1, "_jsonBkt svelte-10qgcdp", null, classes_2, { isArray: get(isArray) });
            set_text(text_2, (get(brackets), untrack(() => get(brackets)[0])));
            classes_3 = set_class(span_8, 1, "_jsonBkt svelte-10qgcdp", null, classes_3, { isArray: get(isArray) });
            set_text(text_5, (get(brackets), untrack(() => get(brackets)[1])));
          });
          event("click", span_4, clicked);
          event("keydown", span_4, pressed);
          event("click", span_8, clicked);
          event("keydown", span_8, pressed);
          append($$anchor3, fragment_4);
        };
        if_block(
          node_2,
          ($$render) => {
            if (get(collapsed)) $$render(consequent_3);
            else $$render(alternate_1, false);
          },
          true
        );
      }
      append($$anchor2, fragment_2);
    };
    if_block(node, ($$render) => {
      if (get(items), untrack(() => !get(items).length)) $$render(consequent_1);
      else $$render(alternate_2, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
var root_1 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  const container = true;
  Block($$anchor, {
    get visible() {
      return gradio.shared.visible;
    },
    get elem_id() {
      return gradio.shared.elem_id;
    },
    get elem_classes() {
      return gradio.shared.elem_classes;
    },
    container,
    get scale() {
      return gradio.shared.scale;
    },
    get min_width() {
      return gradio.shared.min_width;
    },
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          Static($$anchor3, spread_props(
            {
              get autoscroll() {
                return gradio.shared.autoscroll;
              },
              get i18n() {
                return gradio.i18n;
              }
            },
            () => gradio.shared.loading_status,
            {
              $$events: {
                clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
              }
            }
          ));
        };
        if_block(node, ($$render) => {
          if (gradio.shared.loading_status) $$render(consequent);
        });
      }
      var node_1 = sibling(node, 2);
      JsonView(node_1, {
        get json() {
          return gradio.props.value;
        }
      });
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=DTHb1x4A.js.map
