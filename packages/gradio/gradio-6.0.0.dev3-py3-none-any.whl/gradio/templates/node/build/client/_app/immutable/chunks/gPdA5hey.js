import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, c as from_html, d as child, u as deep_read_state, y as untrack, r as reset, t as template_effect, b as append, o as pop, s as sibling, D as comment, v as first_child, k as get, g as set_text } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { t as each, v as index, s as set_attribute, a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
var root_4 = from_html(`<span class="caption svelte-xds4q5"> </span>`);
var root_3 = from_html(`<div class="image-container svelte-xds4q5"><img class="svelte-xds4q5"/> <!></div>`);
var root_7 = from_html(`<span class="caption svelte-xds4q5"> </span>`);
var root_6 = from_html(`<div class="image-container svelte-xds4q5"><video preload="metadata" class="svelte-xds4q5"></video> <!></div>`, 2);
var root_8 = from_html(`<div class="more-indicator svelte-xds4q5">…</div>`);
var root_1 = from_html(`<div class="images-wrapper svelte-xds4q5"><!> <!></div>`);
var root = from_html(`<div><!></div>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  init();
  var div = root();
  let classes;
  var node = child(div);
  {
    var consequent_5 = ($$anchor2) => {
      var div_1 = root_1();
      var node_1 = child(div_1);
      each(
        node_1,
        1,
        () => (deep_read_state(value()), untrack(() => value().slice(0, 3))),
        index,
        ($$anchor3, item) => {
          var fragment = comment();
          var node_2 = first_child(fragment);
          {
            var consequent_1 = ($$anchor4) => {
              var div_2 = root_3();
              var img = child(div_2);
              var node_3 = sibling(img, 2);
              {
                var consequent = ($$anchor5) => {
                  var span = root_4();
                  var text = child(span, true);
                  reset(span);
                  template_effect(() => set_text(text, (get(item), untrack(() => get(item).caption))));
                  append($$anchor5, span);
                };
                if_block(node_3, ($$render) => {
                  if (get(item), untrack(() => get(item).caption)) $$render(consequent);
                });
              }
              reset(div_2);
              template_effect(() => {
                set_attribute(img, "src", (get(item), untrack(() => get(item).image.url)));
                set_attribute(img, "alt", (get(item), untrack(() => get(item).caption || "")));
              });
              append($$anchor4, div_2);
            };
            var alternate = ($$anchor4) => {
              var fragment_1 = comment();
              var node_4 = first_child(fragment_1);
              {
                var consequent_3 = ($$anchor5) => {
                  var div_3 = root_6();
                  var video = child(div_3);
                  video.controls = false;
                  video.muted = true;
                  var node_5 = sibling(video, 2);
                  {
                    var consequent_2 = ($$anchor6) => {
                      var span_1 = root_7();
                      var text_1 = child(span_1, true);
                      reset(span_1);
                      template_effect(() => set_text(text_1, (get(item), untrack(() => get(item).caption))));
                      append($$anchor6, span_1);
                    };
                    if_block(node_5, ($$render) => {
                      if (get(item), untrack(() => get(item).caption)) $$render(consequent_2);
                    });
                  }
                  reset(div_3);
                  template_effect(() => set_attribute(video, "src", (get(item), untrack(() => get(item).video.url))));
                  append($$anchor5, div_3);
                };
                if_block(
                  node_4,
                  ($$render) => {
                    if (get(item), untrack(() => "video" in get(item) && get(item).video)) $$render(consequent_3);
                  },
                  true
                );
              }
              append($$anchor4, fragment_1);
            };
            if_block(node_2, ($$render) => {
              if (get(item), untrack(() => "image" in get(item) && get(item).image)) $$render(consequent_1);
              else $$render(alternate, false);
            });
          }
          append($$anchor3, fragment);
        }
      );
      var node_6 = sibling(node_1, 2);
      {
        var consequent_4 = ($$anchor3) => {
          var div_4 = root_8();
          append($$anchor3, div_4);
        };
        if_block(node_6, ($$render) => {
          if (deep_read_state(value()), untrack(() => value().length > 3)) $$render(consequent_4);
        });
      }
      reset(div_1);
      append($$anchor2, div_1);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(value()), untrack(() => value() && value().length > 0)) $$render(consequent_5);
    });
  }
  reset(div);
  template_effect(() => classes = set_class(div, 1, "container svelte-xds4q5", null, classes, {
    table: type() === "table",
    gallery: type() === "gallery",
    selected: selected()
  }));
  append($$anchor, div);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=gPdA5hey.js.map
