import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, i as legacy_pre_effect, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, s as sibling, v as first_child, r as reset, y as untrack, t as template_effect, g as set_text, b as append, o as pop } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { i as init } from "./DB0xzveP.js";
import { f as Button } from "./DXi4jxVF.js";
var root_2 = from_html(`<span class="api-name svelte-1kdww8a"> </span>`);
var root_1 = from_html(`<div class="loading-dot self-baseline svelte-1kdww8a"></div> <p class="self-baseline svelte-1kdww8a">Recording API Calls:</p> <p class="self-baseline api-section svelte-1kdww8a"><span class="api-count svelte-1kdww8a"> </span> <!></p>`, 1);
var root = from_html(`<div id="api-recorder" class="svelte-1kdww8a"><!></div>`);
function ApiRecorder($$anchor, $$props) {
  push($$props, false);
  let api_calls = prop($$props, "api_calls", 24, () => []);
  let dependencies = prop($$props, "dependencies", 8);
  legacy_pre_effect(() => deep_read_state(api_calls()), () => {
    console.log("API CALLS UPDATED:", api_calls());
  });
  legacy_pre_effect(() => deep_read_state(dependencies()), () => {
    console.log("DEPENDENCIES:", dependencies());
  });
  legacy_pre_effect_reset();
  init();
  var div = root();
  var node = child(div);
  Button(node, {
    size: "sm",
    variant: "secondary",
    children: ($$anchor2, $$slotProps) => {
      var fragment = root_1();
      var p = sibling(first_child(fragment), 4);
      var span = child(p);
      var text = child(span);
      reset(span);
      var node_1 = sibling(span, 2);
      {
        var consequent = ($$anchor3) => {
          var span_1 = root_2();
          var text_1 = child(span_1);
          reset(span_1);
          template_effect(() => set_text(text_1, `/${(deep_read_state(dependencies()), deep_read_state(api_calls()), untrack(() => dependencies()[api_calls()[api_calls().length - 1].fn_index].api_name)) ?? ""}`));
          append($$anchor3, span_1);
        };
        if_block(node_1, ($$render) => {
          if (deep_read_state(api_calls()), untrack(() => api_calls().length > 0)) $$render(consequent);
        });
      }
      reset(p);
      template_effect(() => set_text(text, `[${(deep_read_state(api_calls()), untrack(() => api_calls().length)) ?? ""}]`));
      append($$anchor2, fragment);
    },
    $$slots: { default: true }
  });
  reset(div);
  append($$anchor, div);
  pop();
}
export {
  ApiRecorder as default
};
//# sourceMappingURL=CNLp0Zgf.js.map
