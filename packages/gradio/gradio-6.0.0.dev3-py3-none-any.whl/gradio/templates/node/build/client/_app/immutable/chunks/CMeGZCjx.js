import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, s as sibling, d as child, y as untrack, r as reset, t as template_effect, z as event, b as append, o as pop, D as comment, v as first_child, k as get, g as set_text, A as user_derived } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { t as each, a as set_class, v as index } from "./DXi4jxVF.js";
import { s as slot } from "./DX-MI-YE.js";
import { i as init } from "./DB0xzveP.js";
var root_1 = from_html(`<div class="component-name svelte-1dqn2lk"><span class="svelte-1dqn2lk"> </span> </div>`);
var root_4 = from_html(`<button> </button>`);
var root_3 = from_html(`<div class="button-set svelte-1dqn2lk"><button>input</button> <button>output</button> | <!></div>`);
var root_6 = from_html(`<button class="action modify svelte-1dqn2lk">✎</button> <button class="action delete svelte-1dqn2lk">✗</button>`, 1);
var root_5 = from_html(`<button class="add up svelte-1dqn2lk">+</button> <button class="add left svelte-1dqn2lk">+</button> <button class="add right svelte-1dqn2lk">+</button> <button class="add down svelte-1dqn2lk">+</button> <!>`, 1);
var root = from_html(`<div><div class="cover svelte-1dqn2lk"></div>  <div class="interaction svelte-1dqn2lk"><!> <!></div> <!></div>`);
function Index($$anchor, $$props) {
  push($$props, false);
  const is_function = mutable_source();
  let row = prop($$props, "row", 8);
  let is_container = prop($$props, "is_container", 8);
  let component_type = prop($$props, "component_type", 8);
  let var_name = prop($$props, "var_name", 8);
  let active = prop($$props, "active", 8, false);
  let function_mode = prop($$props, "function_mode", 8, false);
  let event_list = prop($$props, "event_list", 8);
  let is_input = prop($$props, "is_input", 8, false);
  let is_output = prop($$props, "is_output", 8, false);
  let triggers = prop($$props, "triggers", 24, () => []);
  let gradio = prop($$props, "gradio", 8);
  const dispatch = (type) => {
    return (event2) => {
      event2.stopPropagation();
      gradio().dispatch("select", { index: 0, value: type });
    };
  };
  const invisible_components = ["state", "browserstate", "function"];
  legacy_pre_effect(() => deep_read_state(component_type()), () => {
    set(is_function, component_type() === "function");
  });
  legacy_pre_effect_reset();
  init();
  var div = root();
  let classes;
  var div_1 = sibling(child(div), 2);
  var event_handler = user_derived(() => is_container() ? void 0 : dispatch("modify"));
  var node = child(div_1);
  {
    var consequent = ($$anchor2) => {
      var div_2 = root_1();
      var span = child(div_2);
      var text = child(span);
      reset(span);
      var text_1 = sibling(span);
      reset(div_2);
      template_effect(() => {
        set_text(text, `${component_type() ?? ""}:`);
        set_text(text_1, ` ${var_name() ?? ""}`);
      });
      append($$anchor2, div_2);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(component_type()), untrack(() => invisible_components.includes(component_type()))) $$render(consequent);
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent_2 = ($$anchor2) => {
      var fragment = comment();
      var node_2 = first_child(fragment);
      {
        var consequent_1 = ($$anchor3) => {
          var div_3 = root_3();
          var button = child(div_3);
          var event_handler_1 = user_derived(() => dispatch("input"));
          let classes_1;
          var button_1 = sibling(button, 2);
          var event_handler_2 = user_derived(() => dispatch("output"));
          let classes_2;
          var node_3 = sibling(button_1, 2);
          each(node_3, 1, event_list, index, ($$anchor4, event$1) => {
            var button_2 = root_4();
            var event_handler_3 = user_derived(() => dispatch("on:" + get(event$1)));
            let classes_3;
            var text_2 = child(button_2);
            reset(button_2);
            template_effect(
              ($0) => {
                classes_3 = set_class(button_2, 1, "function event svelte-1dqn2lk", null, classes_3, $0);
                set_text(text_2, `on:${get(event$1) ?? ""}`);
              },
              [() => ({ selected: triggers().includes(get(event$1)) })]
            );
            event("click", button_2, function(...$$args) {
              get(event_handler_3)?.apply(this, $$args);
            });
            append($$anchor4, button_2);
          });
          reset(div_3);
          template_effect(() => {
            classes_1 = set_class(button, 1, "function input svelte-1dqn2lk", null, classes_1, { selected: is_input() });
            classes_2 = set_class(button_1, 1, "function output svelte-1dqn2lk", null, classes_2, { selected: is_output() });
          });
          event("click", button, function(...$$args) {
            get(event_handler_1)?.apply(this, $$args);
          });
          event("click", button_1, function(...$$args) {
            get(event_handler_2)?.apply(this, $$args);
          });
          append($$anchor3, div_3);
        };
        if_block(node_2, ($$render) => {
          if (!get(is_function) && !is_container()) $$render(consequent_1);
        });
      }
      append($$anchor2, fragment);
    };
    var alternate = ($$anchor2) => {
      var fragment_1 = root_5();
      var button_3 = first_child(fragment_1);
      var event_handler_4 = user_derived(() => dispatch("up"));
      var button_4 = sibling(button_3, 2);
      var event_handler_5 = user_derived(() => dispatch("left"));
      var button_5 = sibling(button_4, 2);
      var event_handler_6 = user_derived(() => dispatch("right"));
      var button_6 = sibling(button_5, 2);
      var event_handler_7 = user_derived(() => dispatch("down"));
      var node_4 = sibling(button_6, 2);
      {
        var consequent_3 = ($$anchor3) => {
          var fragment_2 = root_6();
          var button_7 = first_child(fragment_2);
          var event_handler_8 = user_derived(() => dispatch("modify"));
          var button_8 = sibling(button_7, 2);
          var event_handler_9 = user_derived(() => dispatch("delete"));
          event("click", button_7, function(...$$args) {
            get(event_handler_8)?.apply(this, $$args);
          });
          event("click", button_8, function(...$$args) {
            get(event_handler_9)?.apply(this, $$args);
          });
          append($$anchor3, fragment_2);
        };
        if_block(node_4, ($$render) => {
          if (!is_container()) $$render(consequent_3);
        });
      }
      event("click", button_3, function(...$$args) {
        get(event_handler_4)?.apply(this, $$args);
      });
      event("click", button_4, function(...$$args) {
        get(event_handler_5)?.apply(this, $$args);
      });
      event("click", button_5, function(...$$args) {
        get(event_handler_6)?.apply(this, $$args);
      });
      event("click", button_6, function(...$$args) {
        get(event_handler_7)?.apply(this, $$args);
      });
      append($$anchor2, fragment_1);
    };
    if_block(node_1, ($$render) => {
      if (function_mode()) $$render(consequent_2);
      else $$render(alternate, false);
    });
  }
  reset(div_1);
  var node_5 = sibling(div_1, 2);
  slot(node_5, $$props, "default", {}, null);
  reset(div);
  template_effect(() => classes = set_class(div, 1, "sketchbox svelte-1dqn2lk", null, classes, { function_mode: function_mode(), row: row(), active: active() }));
  event("click", div_1, function(...$$args) {
    get(event_handler)?.apply(this, $$args);
  });
  append($$anchor, div);
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=CMeGZCjx.js.map
