import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, I as onMount, c as from_html, d as child, r as reset, s as sibling, t as template_effect, b as append, o as pop, y as untrack, u as deep_read_state, j as set, m as mutable_source, k as get, D as comment, v as first_child, g as set_text, F as text } from "./DEzry6cj.js";
import { p as prop, b as bind_this, i as if_block } from "./DUftb7my.js";
import { t as each, i as bind_element_size, v as index, j as Image, a as set_class, s as set_attribute } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { V as Video } from "./Br4zzvQm.js";
var root_6 = from_html(`<audio controls></audio>`);
var root = from_html(`<div><p> </p> <!></div>`);
function Example($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 24, () => ({ text: "", files: [] }));
  let type = prop($$props, "type", 8);
  let selected = prop($$props, "selected", 8, false);
  let size = mutable_source();
  let el = mutable_source();
  function set_styles(element, el_width) {
    element.style.setProperty("--local-text-width", `${el_width && el_width < 150 ? el_width : 200}px`);
    element.style.whiteSpace = "unset";
  }
  onMount(() => {
    set_styles(get(el), get(size));
  });
  init();
  var div = root();
  let classes;
  var p = child(div);
  var text$1 = child(p, true);
  reset(p);
  var node = sibling(p, 2);
  each(node, 1, () => (deep_read_state(value()), untrack(() => value().files)), index, ($$anchor2, file) => {
    var fragment = comment();
    var node_1 = first_child(fragment);
    {
      var consequent = ($$anchor3) => {
        Image($$anchor3, {
          get src() {
            return get(file), untrack(() => get(file).url);
          },
          alt: ""
        });
      };
      var alternate_2 = ($$anchor3) => {
        var fragment_2 = comment();
        var node_2 = first_child(fragment_2);
        {
          var consequent_1 = ($$anchor4) => {
            Video($$anchor4, {
              get src() {
                return get(file), untrack(() => get(file).url);
              },
              alt: "",
              loop: true,
              is_stream: false
            });
          };
          var alternate_1 = ($$anchor4) => {
            var fragment_4 = comment();
            var node_3 = first_child(fragment_4);
            {
              var consequent_2 = ($$anchor5) => {
                var audio = root_6();
                template_effect(() => set_attribute(audio, "src", (get(file), untrack(() => get(file).url))));
                append($$anchor5, audio);
              };
              var alternate = ($$anchor5) => {
                var text_1 = text();
                template_effect(() => set_text(text_1, (get(file), untrack(() => get(file).orig_name))));
                append($$anchor5, text_1);
              };
              if_block(
                node_3,
                ($$render) => {
                  if (get(file), untrack(() => get(file).mime_type && get(file).mime_type.includes("audio"))) $$render(consequent_2);
                  else $$render(alternate, false);
                },
                true
              );
            }
            append($$anchor4, fragment_4);
          };
          if_block(
            node_2,
            ($$render) => {
              if (get(file), untrack(() => get(file).mime_type && get(file).mime_type.includes("video"))) $$render(consequent_1);
              else $$render(alternate_1, false);
            },
            true
          );
        }
        append($$anchor3, fragment_2);
      };
      if_block(node_1, ($$render) => {
        if (get(file), untrack(() => get(file).mime_type && get(file).mime_type.includes("image"))) $$render(consequent);
        else $$render(alternate_2, false);
      });
    }
    append($$anchor2, fragment);
  });
  reset(div);
  bind_this(div, ($$value) => set(el, $$value), () => get(el));
  template_effect(() => {
    classes = set_class(div, 1, "container svelte-xz0m7l", null, classes, {
      table: type() === "table",
      gallery: type() === "gallery",
      selected: selected(),
      border: value()
    });
    set_text(text$1, (deep_read_state(value()), untrack(() => value().text ? value().text : "")));
  });
  bind_element_size(div, "clientWidth", ($$value) => set(size, $$value));
  append($$anchor, div);
  pop();
}
export {
  Example as default
};
//# sourceMappingURL=BJZZzk1u.js.map
