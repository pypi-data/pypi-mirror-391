import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, D as comment, v as first_child, b as append, o as pop, u as deep_read_state, y as untrack, c as from_html, d as child, k as get, A as user_derived, j as set, m as mutable_source, x as derived_safe_equal, r as reset, t as template_effect, g as set_text, Y as mutate } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { p as playable, V as Video } from "./Br4zzvQm.js";
var root_2 = from_html(`<div><!></div>`);
var root_3 = from_html(`<div> </div>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  let value = prop($$props, "value", 8, null);
  let loop = prop($$props, "loop", 8);
  let video = mutable_source();
  async function init$1() {
    mutate(video, get(video).muted = true);
    mutate(video, get(video).playsInline = true);
    mutate(video, get(video).controls = false);
    get(video).setAttribute("muted", "");
    await get(video).play();
    get(video).pause();
  }
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent_1 = ($$anchor2) => {
      var fragment_1 = comment();
      var node_1 = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          var div = root_2();
          let classes;
          var node_2 = child(div);
          var event_handler = user_derived(() => get(video).play.bind(get(video)));
          var event_handler_1 = user_derived(() => get(video).pause.bind(get(video)));
          {
            let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value()?.url)));
            Video(node_2, {
              muted: true,
              playsinline: true,
              get src() {
                return get($0);
              },
              is_stream: false,
              get loop() {
                return loop();
              },
              get node() {
                return get(video);
              },
              set node($$value) {
                set(video, $$value);
              },
              $$events: {
                loadeddata: init$1,
                mouseover(...$$args) {
                  get(event_handler)?.apply(this, $$args);
                },
                mouseout(...$$args) {
                  get(event_handler_1)?.apply(this, $$args);
                }
              },
              $$legacy: true
            });
          }
          reset(div);
          template_effect(() => classes = set_class(div, 1, "container svelte-1nl1glk", null, classes, {
            table: type() === "table",
            gallery: type() === "gallery",
            selected: selected()
          }));
          append($$anchor3, div);
        };
        var alternate = ($$anchor3) => {
          var div_1 = root_3();
          var text = child(div_1, true);
          reset(div_1);
          template_effect(() => set_text(text, value()));
          append($$anchor3, div_1);
        };
        if_block(node_1, ($$render) => {
          if (deep_read_state(playable), untrack(playable)) $$render(consequent);
          else $$render(alternate, false);
        });
      }
      append($$anchor2, fragment_1);
    };
    if_block(node, ($$render) => {
      if (value()) $$render(consequent_1);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=C6ivXr8W.js.map
