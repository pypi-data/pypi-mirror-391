import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { f as from_svg, b as append, p as push, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, n as legacy_pre_effect_reset, D as comment, v as first_child, k as get, y as untrack, o as pop, c as from_html, d as child, s as sibling, r as reset, t as template_effect, z as event } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { I as ImagePaste } from "./CCDNiCZn.js";
import { U as Upload } from "./m2At3saq.js";
import { W as Webcam } from "./CgQP50mE.js";
var root = from_svg(`<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-mic"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`);
function Microphone($$anchor) {
  var svg = root();
  append($$anchor, svg);
}
var root_2 = from_html(`<button aria-label="Upload file"><!></button>`);
var root_3 = from_html(`<button aria-label="Record audio"><!></button>`);
var root_4 = from_html(`<button aria-label="Capture from camera"><!></button>`);
var root_5 = from_html(`<button aria-label="Paste from clipboard"><!></button>`);
var root_1 = from_html(`<span class="source-selection svelte-exvkcd" data-testid="source-select"><!> <!> <!> <!></span>`);
function SelectSource($$anchor, $$props) {
  push($$props, false);
  const unique_sources = mutable_source();
  let sources = prop($$props, "sources", 8);
  let active_source = prop($$props, "active_source", 12);
  let handle_clear = prop($$props, "handle_clear", 8, () => {
  });
  let handle_select = prop($$props, "handle_select", 8, () => {
  });
  async function handle_select_source(source) {
    handle_clear()();
    active_source(source);
    handle_select()(source);
  }
  legacy_pre_effect(() => deep_read_state(sources()), () => {
    set(unique_sources, [...new Set(sources())]);
  });
  legacy_pre_effect_reset();
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent_4 = ($$anchor2) => {
      var span = root_1();
      var node_1 = child(span);
      {
        var consequent = ($$anchor3) => {
          var button = root_2();
          let classes;
          var node_2 = child(button);
          Upload(node_2);
          reset(button);
          template_effect(() => classes = set_class(button, 1, "icon svelte-exvkcd", null, classes, { selected: active_source() === "upload" || !active_source() }));
          event("click", button, () => handle_select_source("upload"));
          append($$anchor3, button);
        };
        if_block(node_1, ($$render) => {
          if (deep_read_state(sources()), untrack(() => sources().includes("upload"))) $$render(consequent);
        });
      }
      var node_3 = sibling(node_1, 2);
      {
        var consequent_1 = ($$anchor3) => {
          var button_1 = root_3();
          let classes_1;
          var node_4 = child(button_1);
          Microphone(node_4);
          reset(button_1);
          template_effect(() => classes_1 = set_class(button_1, 1, "icon svelte-exvkcd", null, classes_1, { selected: active_source() === "microphone" }));
          event("click", button_1, () => handle_select_source("microphone"));
          append($$anchor3, button_1);
        };
        if_block(node_3, ($$render) => {
          if (deep_read_state(sources()), untrack(() => sources().includes("microphone"))) $$render(consequent_1);
        });
      }
      var node_5 = sibling(node_3, 2);
      {
        var consequent_2 = ($$anchor3) => {
          var button_2 = root_4();
          let classes_2;
          var node_6 = child(button_2);
          Webcam(node_6);
          reset(button_2);
          template_effect(() => classes_2 = set_class(button_2, 1, "icon svelte-exvkcd", null, classes_2, { selected: active_source() === "webcam" }));
          event("click", button_2, () => handle_select_source("webcam"));
          append($$anchor3, button_2);
        };
        if_block(node_5, ($$render) => {
          if (deep_read_state(sources()), untrack(() => sources().includes("webcam"))) $$render(consequent_2);
        });
      }
      var node_7 = sibling(node_5, 2);
      {
        var consequent_3 = ($$anchor3) => {
          var button_3 = root_5();
          let classes_3;
          var node_8 = child(button_3);
          ImagePaste(node_8);
          reset(button_3);
          template_effect(() => classes_3 = set_class(button_3, 1, "icon svelte-exvkcd", null, classes_3, { selected: active_source() === "clipboard" }));
          event("click", button_3, () => handle_select_source("clipboard"));
          append($$anchor3, button_3);
        };
        if_block(node_7, ($$render) => {
          if (deep_read_state(sources()), untrack(() => sources().includes("clipboard"))) $$render(consequent_3);
        });
      }
      reset(span);
      append($$anchor2, span);
    };
    if_block(node, ($$render) => {
      if (get(unique_sources), untrack(() => get(unique_sources).length > 1)) $$render(consequent_4);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  Microphone as M,
  SelectSource as S
};
//# sourceMappingURL=jPEKutgU.js.map
