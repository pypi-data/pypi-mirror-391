import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, i as legacy_pre_effect, W as to_array, j as set, m as mutable_source, k as get, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, r as reset, s as sibling, t as template_effect, b as append, o as pop, v as first_child, y as untrack, g as set_text } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { a as set_class } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { I as ImagePaste } from "./CCDNiCZn.js";
import { U as Upload } from "./m2At3saq.js";
const RE_HEADING = /^(#\s*)(.+)$/m;
function inject(text) {
  const trimmed_text = text.trim();
  const heading_match = trimmed_text.match(RE_HEADING);
  if (!heading_match) {
    return [false, trimmed_text || false];
  }
  const [full_match, , heading_content] = heading_match;
  const _heading = heading_content.trim();
  if (trimmed_text === full_match) {
    return [_heading, false];
  }
  const heading_end_index = heading_match.index !== void 0 ? heading_match.index + full_match.length : 0;
  const remaining_text = trimmed_text.substring(heading_end_index).trim();
  const _paragraph = remaining_text || false;
  return [_heading, _paragraph];
}
var root_4 = from_html(`<h2 class="svelte-1vmd51o"> </h2>`);
var root_5 = from_html(`<p class="svelte-1vmd51o"> </p>`);
var root_3 = from_html(`<!> <!>`, 1);
var root_7 = from_html(`<span class="or svelte-1vmd51o"> </span> `, 1);
var root_6 = from_html(` <!>`, 1);
var root = from_html(`<div class="wrap svelte-1vmd51o"><span><!></span> <!></div>`);
function UploadText($$anchor, $$props) {
  push($$props, false);
  const heading = mutable_source();
  const paragraph = mutable_source();
  let type = prop($$props, "type", 8, "file");
  let i18n = prop($$props, "i18n", 8);
  let message = prop($$props, "message", 8, void 0);
  let mode = prop($$props, "mode", 8, "full");
  let hovered = prop($$props, "hovered", 8, false);
  let placeholder = prop($$props, "placeholder", 8, void 0);
  const defs = {
    image: "upload_text.drop_image",
    video: "upload_text.drop_video",
    audio: "upload_text.drop_audio",
    file: "upload_text.drop_file",
    csv: "upload_text.drop_csv",
    gallery: "upload_text.drop_gallery",
    clipboard: "upload_text.paste_clipboard"
  };
  legacy_pre_effect(
    () => (get(heading), get(paragraph), deep_read_state(placeholder()), inject),
    () => {
      (($$value) => {
        var $$array = to_array($$value, 2);
        set(heading, $$array[0]);
        set(paragraph, $$array[1]);
      })(placeholder() ? inject(placeholder()) : [false, false]);
    }
  );
  legacy_pre_effect_reset();
  init();
  var div = root();
  var span = child(div);
  let classes;
  var node = child(span);
  {
    var consequent = ($$anchor2) => {
      ImagePaste($$anchor2);
    };
    var alternate = ($$anchor2) => {
      Upload($$anchor2);
    };
    if_block(node, ($$render) => {
      if (type() === "clipboard") $$render(consequent);
      else $$render(alternate, false);
    });
  }
  reset(span);
  var node_1 = sibling(span, 2);
  {
    var consequent_3 = ($$anchor2) => {
      var fragment_2 = root_3();
      var node_2 = first_child(fragment_2);
      {
        var consequent_1 = ($$anchor3) => {
          var h2 = root_4();
          var text = child(h2, true);
          reset(h2);
          template_effect(() => set_text(text, get(heading)));
          append($$anchor3, h2);
        };
        if_block(node_2, ($$render) => {
          if (get(heading)) $$render(consequent_1);
        });
      }
      var node_3 = sibling(node_2, 2);
      {
        var consequent_2 = ($$anchor3) => {
          var p = root_5();
          var text_1 = child(p, true);
          reset(p);
          template_effect(() => set_text(text_1, get(paragraph)));
          append($$anchor3, p);
        };
        if_block(node_3, ($$render) => {
          if (get(paragraph)) $$render(consequent_2);
        });
      }
      append($$anchor2, fragment_2);
    };
    var alternate_1 = ($$anchor2) => {
      var fragment_3 = root_6();
      var text_2 = first_child(fragment_3);
      var node_4 = sibling(text_2);
      {
        var consequent_4 = ($$anchor3) => {
          var fragment_4 = root_7();
          var span_1 = first_child(fragment_4);
          var text_3 = child(span_1);
          reset(span_1);
          var text_4 = sibling(span_1);
          template_effect(
            ($0, $1) => {
              set_text(text_3, `- ${$0 ?? ""} -`);
              set_text(text_4, ` ${$1 ?? ""}`);
            },
            [
              () => (deep_read_state(i18n()), untrack(() => i18n()("common.or"))),
              () => (deep_read_state(message()), deep_read_state(i18n()), untrack(() => message() || i18n()("upload_text.click_to_upload")))
            ]
          );
          append($$anchor3, fragment_4);
        };
        if_block(node_4, ($$render) => {
          if (mode() !== "short") $$render(consequent_4);
        });
      }
      template_effect(($0) => set_text(text_2, `${$0 ?? ""} `), [
        () => (deep_read_state(i18n()), deep_read_state(type()), untrack(() => i18n()(defs[type()] || defs.file)))
      ]);
      append($$anchor2, fragment_3);
    };
    if_block(node_1, ($$render) => {
      if (get(heading) || get(paragraph)) $$render(consequent_3);
      else $$render(alternate_1, false);
    });
  }
  reset(div);
  template_effect(() => classes = set_class(span, 1, "icon-wrap svelte-1vmd51o", null, classes, { hovered: hovered() }));
  append($$anchor, div);
  pop();
}
export {
  UploadText as U
};
//# sourceMappingURL=B8mIV0gF.js.map
