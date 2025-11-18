import "./9B4_veAf.js";
import { f as from_svg, b as append, p as push, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, v as first_child, y as untrack, s as sibling, k as get, o as pop, d as child, x as derived_safe_equal, r as reset, t as template_effect, g as set_text, z as event, q as createEventDispatcher, N as onDestroy, D as comment, M as user_effect, J as state, A as user_derived, F as text, E as next, Y as mutate, V as remove_textarea_child, aQ as autofocus, I as onMount, K as tick } from "./DEzry6cj.js";
import { p as prop, i as if_block, c as component, s as spread_props, b as bind_this, r as rest_props } from "./DUftb7my.js";
import "./BAp-OWo-.js";
import { u as uploadToHuggingFace, b as IconButton, t as each, p as set_style, v as index, H as Check, J as Copy, I as IconButtonWrapper, C as Clear, a as set_class, c as bubble_event, M as MarkdownCode, s as set_attribute, O as stopPropagation, Y as transition, aa as slide, k as clsx, j as Image, q as bind_value, e as ShareError, y as action, K as copy, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { E as Edit } from "./CByIssN2.js";
import { U as Undo } from "./oKXAgRt1.js";
import { F as File } from "./bc1v6JFX.js";
import { d as dequal } from "./DCsjM_Cd.js";
import { C as Community } from "./CeH6vEIM.js";
import { T as Trash } from "./D9zAf8BK.js";
import { M as Music } from "./Dr2P5Z1a.js";
import { B as BlockLabel } from "./DEb09X9A.js";
var root$f = from_svg(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--carbon" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" viewBox="0 0 32 32"><path fill="currentColor" d="M17.74 30L16 29l4-7h6a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h9v2H6a4 4 0 0 1-4-4V8a4 4 0 0 1 4-4h20a4 4 0 0 1 4 4v12a4 4 0 0 1-4 4h-4.84Z"></path><path fill="currentColor" d="M8 10h16v2H8zm0 6h10v2H8z"></path></svg>`);
function Chat($$anchor) {
  var svg = root$f();
  append($$anchor, svg);
}
var root$e = from_svg(`<svg class="dropdown-arrow svelte-1w1fnc7" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 18 18"><circle cx="9" cy="9" r="8" class="circle svelte-1w1fnc7"></circle><path d="M5 8l4 4 4-4z"></path></svg>`);
function DropdownCircularArrow($$anchor) {
  var svg = root$e();
  append($$anchor, svg);
}
var root$d = from_svg(`<svg width="100%" height="100%" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" color="currentColor"><path d="M19.1679 9C18.0247 6.46819 15.3006 4.5 11.9999 4.5C8.31459 4.5 5.05104 7.44668 4.54932 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M16 9H19.4C19.7314 9 20 8.73137 20 8.4V5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M4.88146 15C5.92458 17.5318 8.64874 19.5 12.0494 19.5C15.7347 19.5 18.9983 16.5533 19.5 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path><path d="M8.04932 15H4.64932C4.31795 15 4.04932 15.2686 4.04932 15.6V19" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path></svg>`);
function Retry($$anchor) {
  var svg = root$d();
  append($$anchor, svg);
}
var root$c = from_svg(`<svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 20L12 4M12 20L7 15M12 20L17 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>`);
function ScrollDownArrow($$anchor) {
  var svg = root$c();
  append($$anchor, svg);
}
const format_chat_for_sharing = async (chat, url_length_limit = 1800) => {
  let messages_to_share = [...chat];
  let formatted = await format_messages(messages_to_share);
  if (formatted.length > url_length_limit && messages_to_share.length > 2) {
    const first_message = messages_to_share[0];
    const last_message = messages_to_share[messages_to_share.length - 1];
    messages_to_share = [first_message, last_message];
    formatted = await format_messages(messages_to_share);
  }
  if (formatted.length > url_length_limit && messages_to_share.length > 0) {
    const truncated_messages = messages_to_share.map((msg) => {
      if (msg.type === "text") {
        const max_length = Math.floor(url_length_limit / messages_to_share.length) - 20;
        if (msg.content.length > max_length) {
          return {
            ...msg,
            content: msg.content.substring(0, max_length) + "..."
          };
        }
      }
      return msg;
    });
    messages_to_share = truncated_messages;
    formatted = await format_messages(messages_to_share);
  }
  return formatted;
};
const format_messages = async (chat) => {
  let messages = await Promise.all(
    chat.map(async (message) => {
      if (message.role === "system") return "";
      let speaker_emoji = message.role === "user" ? "😃" : "🤖";
      let html_content = "";
      if (message.type === "text") {
        const regexPatterns = {
          audio: /<audio.*?src="(\/file=.*?)"/g,
          video: /<video.*?src="(\/file=.*?)"/g,
          image: /<img.*?src="(\/file=.*?)".*?\/>|!\[.*?\]\((\/file=.*?)\)/g
        };
        html_content = message.content;
        for (let [_, regex] of Object.entries(regexPatterns)) {
          let match;
          while ((match = regex.exec(message.content)) !== null) {
            const fileUrl = match[1] || match[2];
            const newUrl = await uploadToHuggingFace(fileUrl);
            html_content = html_content.replace(fileUrl, newUrl);
          }
        }
      } else {
        if (!message.content.value) return "";
        const url = message.content.component === "video" ? message.content.value?.video.path : message.content.value;
        const file_url = await uploadToHuggingFace(url);
        if (message.content.component === "audio") {
          html_content = `<audio controls src="${file_url}"></audio>`;
        } else if (message.content.component === "video") {
          html_content = file_url;
        } else if (message.content.component === "image") {
          html_content = `<img src="${file_url}" />`;
        }
      }
      return `${speaker_emoji}: ${html_content}`;
    })
  );
  return messages.filter((msg) => msg !== "").join("\n");
};
const redirect_src_url = (src, root2) => src.replace('src="/file', `src="${root2}file`);
function get_component_for_mime_type(mime_type, file) {
  if (!mime_type) {
    const path = file?.path;
    if (path) {
      const lower_path = path.toLowerCase();
      if (lower_path.endsWith(".glb") || lower_path.endsWith(".gltf") || lower_path.endsWith(".obj") || lower_path.endsWith(".stl") || lower_path.endsWith(".splat") || lower_path.endsWith(".ply")) {
        return "model3d";
      }
    }
    return "file";
  }
  if (mime_type.includes("audio")) return "audio";
  if (mime_type.includes("video")) return "video";
  if (mime_type.includes("image")) return "image";
  if (mime_type.includes("model")) return "model3d";
  return "file";
}
function convert_file_message_to_component_message(message) {
  const _file = Array.isArray(message.file) ? message.file[0] : message.file;
  return {
    component: get_component_for_mime_type(_file?.mime_type, _file),
    value: message.file,
    alt_text: message.alt_text,
    constructor_args: {},
    props: {}
  };
}
function normalise_message(message, content, root2, i) {
  let normalized;
  if (content.type === "text") {
    normalized = {
      role: message.role,
      metadata: message.metadata,
      content: redirect_src_url(content.text, root2),
      type: "text",
      index: i,
      options: message.options
    };
  } else if (content.type === "file") {
    normalized = {
      role: message.role,
      metadata: message.metadata,
      content: convert_file_message_to_component_message(content),
      type: "component",
      index: i,
      options: message.options
    };
  } else {
    normalized = {
      role: message.role,
      metadata: message.metadata,
      content,
      type: "component",
      index: i,
      options: message.options
    };
  }
  return normalized;
}
function normalise_messages(messages, root2) {
  if (messages === null) return messages;
  const thought_map = /* @__PURE__ */ new Map();
  return messages.flatMap((message, i) => {
    const normalized = message.content.map(
      (content) => normalise_message(message, content, root2, i)
    );
    for (const msg of normalized) {
      const { id, title, parent_id } = message.metadata || {};
      if (parent_id) {
        const parent = thought_map.get(String(parent_id));
        if (parent) {
          const thought = { ...msg, children: [] };
          parent.children.push(thought);
          if (id && title) {
            thought_map.set(String(id), thought);
          }
          return null;
        }
      }
      if (id && title) {
        const thought = { ...msg, children: [] };
        thought_map.set(String(id), thought);
        return thought;
      }
    }
    return normalized;
  }).filter((msg) => msg !== null);
}
function is_component_message(message) {
  return message.type === "component";
}
function is_last_bot_message(messages, all_messages) {
  const is_bot = messages[messages.length - 1].role === "assistant";
  const last_index = messages[messages.length - 1].index;
  const is_last = JSON.stringify(last_index) === JSON.stringify(all_messages[all_messages.length - 1].index);
  return is_last && is_bot;
}
function group_messages(messages, display_consecutive_in_same_bubble = true) {
  const groupedMessages = [];
  let currentGroup = [];
  let currentRole = null;
  for (const message of messages) {
    if (!(message.role === "assistant" || message.role === "user")) {
      continue;
    }
    if (!display_consecutive_in_same_bubble) {
      groupedMessages.push([message]);
      continue;
    }
    if (message.role === currentRole) {
      currentGroup.push(message);
    } else {
      if (currentGroup.length > 0) {
        groupedMessages.push(currentGroup);
      }
      currentGroup = [message];
      currentRole = message.role;
    }
  }
  if (currentGroup.length > 0) {
    groupedMessages.push(currentGroup);
  }
  return groupedMessages;
}
async function load_components(component_names, _components, load_component) {
  for (const component_name of component_names) {
    if (_components[component_name] || component_name === "file") {
      continue;
    }
    const variant = component_name === "dataframe" ? "component" : "base";
    const comp = await load_component(component_name, variant);
    _components[component_name] = comp.default;
  }
  return _components;
}
function get_components_from_messages(messages) {
  if (!messages) return [];
  let components = /* @__PURE__ */ new Set();
  messages.forEach((message) => {
    if (message.type === "component") {
      components.add(message.content.component);
    }
  });
  return Array.from(components);
}
function get_thought_content(msg, depth = 0) {
  let content = "";
  const indent = "  ".repeat(depth);
  if (msg.metadata?.title) {
    content += `${indent}${depth > 0 ? "- " : ""}${msg.metadata.title}
`;
  }
  if (typeof msg.content === "string") {
    content += `${indent}  ${msg.content}
`;
  }
  const thought = msg;
  if (thought.children?.length > 0) {
    content += thought.children.map((child2) => get_thought_content(child2, depth + 1)).join("");
  }
  return content;
}
function all_text(message) {
  if (Array.isArray(message)) {
    return message.map((m) => {
      if (m.metadata?.title) {
        return get_thought_content(m);
      }
      return m.content;
    }).join("\n");
  }
  if (message.metadata?.title) {
    return get_thought_content(message);
  }
  return message.content;
}
function is_all_text(message) {
  return Array.isArray(message) && message.every((m) => typeof m.content === "string") || !Array.isArray(message) && typeof message.content === "string";
}
var root$b = from_svg(`<svg width="100%" height="100%" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11.25 6.61523H9.375V1.36523H11.25V6.61523ZM3.375 1.36523H8.625V6.91636L7.48425 8.62748L7.16737 10.8464C7.14108 11.0248 7.05166 11.1879 6.91535 11.3061C6.77904 11.4242 6.60488 11.4896 6.4245 11.4902H6.375C6.07672 11.4899 5.79075 11.3713 5.57983 11.1604C5.36892 10.9495 5.2503 10.6635 5.25 10.3652V8.11523H2.25C1.85233 8.11474 1.47109 7.95654 1.18989 7.67535C0.908691 7.39415 0.750496 7.01291 0.75 6.61523V3.99023C0.750992 3.29435 1.02787 2.62724 1.51994 2.13517C2.01201 1.64311 2.67911 1.36623 3.375 1.36523Z" fill="currentColor"></path></svg>`);
function ThumbDownActive($$anchor) {
  var svg = root$b();
  append($$anchor, svg);
}
var root$a = from_svg(`<svg width="100%" height="100%" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.25 8.11523H4.5V10.3652C4.5003 10.6635 4.61892 10.9495 4.82983 11.1604C5.04075 11.3713 5.32672 11.4899 5.625 11.4902H6.42488C6.60519 11.4895 6.77926 11.4241 6.91549 11.3059C7.05172 11.1878 7.14109 11.0248 7.16737 10.8464L7.48425 8.62748L8.82562 6.61523H11.25V1.36523H3.375C2.67911 1.36623 2.01201 1.64311 1.51994 2.13517C1.02787 2.62724 0.750992 3.29435 0.75 3.99023V6.61523C0.750496 7.01291 0.908691 7.39415 1.18989 7.67535C1.47109 7.95654 1.85233 8.11474 2.25 8.11523ZM9 2.11523H10.5V5.86523H9V2.11523ZM1.5 3.99023C1.5006 3.49314 1.69833 3.01657 2.04983 2.66507C2.40133 2.31356 2.8779 2.11583 3.375 2.11523H8.25V6.12661L6.76575 8.35298L6.4245 10.7402H5.625C5.52554 10.7402 5.43016 10.7007 5.35983 10.6304C5.28951 10.5601 5.25 10.4647 5.25 10.3652V7.36523H2.25C2.05118 7.36494 1.86059 7.28582 1.72 7.14524C1.57941 7.00465 1.5003 6.81406 1.5 6.61523V3.99023Z" fill="currentColor"></path></svg>`);
function ThumbDownDefault($$anchor) {
  var svg = root$a();
  append($$anchor, svg);
}
var root$9 = from_svg(`<svg width="100%" height="100%" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M0.75 6.24023H2.625V11.4902H0.75V6.24023ZM8.625 11.4902H3.375V5.93911L4.51575 4.22798L4.83263 2.00911C4.85892 1.83065 4.94834 1.66754 5.08465 1.5494C5.22096 1.43125 5.39512 1.36591 5.5755 1.36523H5.625C5.92328 1.36553 6.20925 1.48415 6.42017 1.69507C6.63108 1.90598 6.7497 2.19196 6.75 2.49023V4.74023H9.75C10.1477 4.74073 10.5289 4.89893 10.8101 5.18012C11.0913 5.46132 11.2495 5.84256 11.25 6.24023V8.86523C11.249 9.56112 10.9721 10.2282 10.4801 10.7203C9.98799 11.2124 9.32089 11.4892 8.625 11.4902Z" fill="currentColor"></path></svg>`);
function ThumbUpActive($$anchor) {
  var svg = root$9();
  append($$anchor, svg);
}
var root$8 = from_svg(`<svg width="100%" height="100%" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9.75 4.74023H7.5V2.49023C7.4997 2.19196 7.38108 1.90598 7.17017 1.69507C6.95925 1.48415 6.67328 1.36553 6.375 1.36523H5.57512C5.39481 1.366 5.22074 1.43138 5.08451 1.54952C4.94828 1.66766 4.85891 1.83072 4.83262 2.00911L4.51575 4.22798L3.17438 6.24023H0.75V11.4902H8.625C9.32089 11.4892 9.98799 11.2124 10.4801 10.7203C10.9721 10.2282 11.249 9.56112 11.25 8.86523V6.24023C11.2495 5.84256 11.0913 5.46132 10.8101 5.18012C10.5289 4.89893 10.1477 4.74073 9.75 4.74023ZM3 10.7402H1.5V6.99023H3V10.7402ZM10.5 8.86523C10.4994 9.36233 10.3017 9.8389 9.95017 10.1904C9.59867 10.5419 9.1221 10.7396 8.625 10.7402H3.75V6.72886L5.23425 4.50248L5.5755 2.11523H6.375C6.47446 2.11523 6.56984 2.15474 6.64017 2.22507C6.71049 2.2954 6.75 2.39078 6.75 2.49023V5.49023H9.75C9.94882 5.49053 10.1394 5.56965 10.28 5.71023C10.4206 5.85082 10.4997 6.04141 10.5 6.24023V8.86523Z" fill="currentColor"></path></svg>`);
function ThumbUpDefault($$anchor) {
  var svg = root$8();
  append($$anchor, svg);
}
var root$7 = from_svg(`<svg id="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none"><path fill="currentColor" d="M6,30H4V2H28l-5.8,9L28,20H6ZM6,18H24.33L19.8,11l4.53-7H6Z"></path></svg>`);
function Flag($$anchor) {
  var svg = root$7();
  append($$anchor, svg);
}
var root$6 = from_svg(`<svg id="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none"><path fill="currentColor" d="M4,2H28l-5.8,9L28,20H6v10H4V2z"></path></svg>`);
function FlagActive($$anchor) {
  var svg = root$6();
  append($$anchor, svg);
}
var root_1$7 = from_html(`<!> <!>`, 1);
var root_5$2 = from_html(`<button class="extra-feedback-option svelte-fvat56"> </button>`);
var root_4$4 = from_html(`<div class="extra-feedback no-border svelte-fvat56"><!> <div class="extra-feedback-options svelte-fvat56"></div></div>`);
var root$5 = from_html(`<!> <!>`, 1);
function LikeDislike($$anchor, $$props) {
  push($$props, false);
  const extra_feedback = mutable_source();
  let i18n = prop($$props, "i18n", 8);
  let handle_action = prop($$props, "handle_action", 8);
  let feedback_options = prop($$props, "feedback_options", 8);
  let selected = prop($$props, "selected", 12, null);
  function toggleSelection(newSelection) {
    selected(selected() === newSelection ? null : newSelection);
    handle_action()(selected());
  }
  legacy_pre_effect(() => deep_read_state(feedback_options()), () => {
    set(extra_feedback, feedback_options().filter((option) => option !== "Like" && option !== "Dislike"));
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root$5();
  var node = first_child(fragment);
  {
    var consequent_2 = ($$anchor2) => {
      var fragment_1 = root_1$7();
      var node_1 = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          {
            let $0 = derived_safe_equal(() => selected() === "Dislike" ? ThumbDownActive : ThumbDownDefault);
            let $1 = derived_safe_equal(() => (deep_read_state(selected()), deep_read_state(i18n()), untrack(() => selected() === "Dislike" ? "clicked dislike" : i18n()("chatbot.dislike"))));
            let $2 = derived_safe_equal(() => selected() === "Dislike" ? "var(--color-accent)" : "var(--block-label-text-color)");
            IconButton($$anchor3, {
              get Icon() {
                return get($0);
              },
              get label() {
                return get($1);
              },
              get color() {
                return get($2);
              },
              $$events: { click: () => toggleSelection("Dislike") }
            });
          }
        };
        if_block(node_1, ($$render) => {
          if (deep_read_state(feedback_options()), untrack(() => feedback_options().includes("Dislike"))) $$render(consequent);
        });
      }
      var node_2 = sibling(node_1, 2);
      {
        var consequent_1 = ($$anchor3) => {
          {
            let $0 = derived_safe_equal(() => selected() === "Like" ? ThumbUpActive : ThumbUpDefault);
            let $1 = derived_safe_equal(() => (deep_read_state(selected()), deep_read_state(i18n()), untrack(() => selected() === "Like" ? "clicked like" : i18n()("chatbot.like"))));
            let $2 = derived_safe_equal(() => selected() === "Like" ? "var(--color-accent)" : "var(--block-label-text-color)");
            IconButton($$anchor3, {
              get Icon() {
                return get($0);
              },
              get label() {
                return get($1);
              },
              get color() {
                return get($2);
              },
              $$events: { click: () => toggleSelection("Like") }
            });
          }
        };
        if_block(node_2, ($$render) => {
          if (deep_read_state(feedback_options()), untrack(() => feedback_options().includes("Like"))) $$render(consequent_1);
        });
      }
      append($$anchor2, fragment_1);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(feedback_options()), untrack(() => feedback_options().includes("Like") || feedback_options().includes("Dislike"))) $$render(consequent_2);
    });
  }
  var node_3 = sibling(node, 2);
  {
    var consequent_3 = ($$anchor2) => {
      var div = root_4$4();
      var node_4 = child(div);
      {
        let $0 = derived_safe_equal(() => (deep_read_state(selected()), get(extra_feedback), deep_read_state(FlagActive), deep_read_state(Flag), untrack(() => selected() && get(extra_feedback).includes(selected()) ? FlagActive : Flag)));
        let $1 = derived_safe_equal(() => (deep_read_state(selected()), get(extra_feedback), untrack(() => selected() && get(extra_feedback).includes(selected()) ? "var(--color-accent)" : "var(--block-label-text-color)")));
        IconButton(node_4, {
          get Icon() {
            return get($0);
          },
          label: "Feedback",
          get color() {
            return get($1);
          }
        });
      }
      var div_1 = sibling(node_4, 2);
      each(div_1, 5, () => get(extra_feedback), index, ($$anchor3, option) => {
        var button = root_5$2();
        let styles;
        var text2 = child(button, true);
        reset(button);
        template_effect(() => {
          styles = set_style(button, "", styles, {
            "font-weight": selected() === get(option) ? "bold" : "normal"
          });
          set_text(text2, get(option));
        });
        event("click", button, () => {
          toggleSelection(get(option));
          handle_action()(selected() ? selected() : null);
        });
        append($$anchor3, button);
      });
      reset(div_1);
      reset(div);
      append($$anchor2, div);
    };
    if_block(node_3, ($$render) => {
      if (get(extra_feedback), untrack(() => get(extra_feedback).length > 0)) $$render(consequent_3);
    });
  }
  append($$anchor, fragment);
  pop();
}
function Copy_1($$anchor, $$props) {
  push($$props, false);
  const dispatch = createEventDispatcher();
  let copied = mutable_source(false);
  let value = prop($$props, "value", 8);
  let watermark = prop($$props, "watermark", 8, null);
  let i18n = prop($$props, "i18n", 8);
  let timer;
  function copy_feedback() {
    set(copied, true);
    if (timer) clearTimeout(timer);
    timer = setTimeout(
      () => {
        set(copied, false);
      },
      2e3
    );
  }
  async function handle_copy() {
    if ("clipboard" in navigator) {
      dispatch("copy", { value: value() });
      const text_to_copy = watermark() ? `${value()}

${watermark()}` : value();
      await navigator.clipboard.writeText(text_to_copy);
      copy_feedback();
    } else {
      const textArea = document.createElement("textarea");
      const text_to_copy = watermark() ? `${value()}

${watermark()}` : value();
      textArea.value = text_to_copy;
      textArea.style.position = "absolute";
      textArea.style.left = "-999999px";
      document.body.prepend(textArea);
      textArea.select();
      try {
        document.execCommand("copy");
        copy_feedback();
      } catch (error) {
        console.error(error);
      } finally {
        textArea.remove();
      }
    }
  }
  onDestroy(() => {
    if (timer) clearTimeout(timer);
  });
  init();
  {
    let $0 = derived_safe_equal(() => (get(copied), deep_read_state(i18n()), untrack(() => get(copied) ? i18n()("chatbot.copied_message") : i18n()("chatbot.copy_message"))));
    let $1 = derived_safe_equal(() => get(copied) ? Check : Copy);
    IconButton($$anchor, {
      get label() {
        return get($0);
      },
      get Icon() {
        return get($1);
      },
      $$events: { click: handle_copy }
    });
  }
  pop();
}
var root_3$2 = from_html(`<!> <!>`, 1);
var root_4$3 = from_html(`<!> <!> <!> <!> <!>`, 1);
var root_1$6 = from_html(`<div><!></div>`);
function ButtonPanel($$anchor, $$props) {
  push($$props, false);
  const message_text = mutable_source();
  const show_copy = mutable_source();
  let i18n = prop($$props, "i18n", 8);
  let likeable = prop($$props, "likeable", 8);
  let feedback_options = prop($$props, "feedback_options", 8);
  let show_retry = prop($$props, "show_retry", 8);
  let show_undo = prop($$props, "show_undo", 8);
  let show_edit = prop($$props, "show_edit", 8);
  let in_edit_mode = prop($$props, "in_edit_mode", 8);
  let show_copy_button = prop($$props, "show_copy_button", 8);
  let watermark = prop($$props, "watermark", 8, null);
  let message = prop($$props, "message", 8);
  let position = prop($$props, "position", 8);
  let avatar = prop($$props, "avatar", 8);
  let generating = prop($$props, "generating", 8);
  let current_feedback = prop($$props, "current_feedback", 8);
  let handle_action = prop($$props, "handle_action", 8);
  let layout = prop($$props, "layout", 8);
  let dispatch = prop($$props, "dispatch", 8);
  legacy_pre_effect(() => (deep_read_state(message()), all_text), () => {
    set(message_text, is_all_text(message()) ? all_text(message()) : "");
  });
  legacy_pre_effect(
    () => (deep_read_state(show_copy_button()), deep_read_state(message()), is_all_text),
    () => {
      set(show_copy, show_copy_button() && message() && is_all_text(message()));
    }
  );
  legacy_pre_effect_reset();
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent_6 = ($$anchor2) => {
      var div = root_1$6();
      var node_1 = child(div);
      IconButtonWrapper(node_1, {
        top_panel: false,
        children: ($$anchor3, $$slotProps) => {
          var fragment_1 = comment();
          var node_2 = first_child(fragment_1);
          {
            var consequent = ($$anchor4) => {
              var fragment_2 = root_3$2();
              var node_3 = first_child(fragment_2);
              {
                let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("chatbot.submit"))));
                IconButton(node_3, {
                  get label() {
                    return get($0);
                  },
                  get Icon() {
                    return Check;
                  },
                  get disabled() {
                    return generating();
                  },
                  $$events: { click: () => handle_action()("edit_submit") }
                });
              }
              var node_4 = sibling(node_3, 2);
              {
                let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("chatbot.cancel"))));
                IconButton(node_4, {
                  get label() {
                    return get($0);
                  },
                  get Icon() {
                    return Clear;
                  },
                  get disabled() {
                    return generating();
                  },
                  $$events: { click: () => handle_action()("edit_cancel") }
                });
              }
              append($$anchor4, fragment_2);
            };
            var alternate = ($$anchor4) => {
              var fragment_3 = root_4$3();
              var node_5 = first_child(fragment_3);
              {
                var consequent_1 = ($$anchor5) => {
                  Copy_1($$anchor5, {
                    get value() {
                      return get(message_text);
                    },
                    get watermark() {
                      return watermark();
                    },
                    get i18n() {
                      return i18n();
                    },
                    $$events: { copy: (e) => dispatch()("copy", e.detail) }
                  });
                };
                if_block(node_5, ($$render) => {
                  if (get(show_copy)) $$render(consequent_1);
                });
              }
              var node_6 = sibling(node_5, 2);
              {
                var consequent_2 = ($$anchor5) => {
                  {
                    let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("chatbot.retry"))));
                    IconButton($$anchor5, {
                      get Icon() {
                        return Retry;
                      },
                      get label() {
                        return get($0);
                      },
                      get disabled() {
                        return generating();
                      },
                      $$events: { click: () => handle_action()("retry") }
                    });
                  }
                };
                if_block(node_6, ($$render) => {
                  if (show_retry()) $$render(consequent_2);
                });
              }
              var node_7 = sibling(node_6, 2);
              {
                var consequent_3 = ($$anchor5) => {
                  {
                    let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("chatbot.undo"))));
                    IconButton($$anchor5, {
                      get label() {
                        return get($0);
                      },
                      get Icon() {
                        return Undo;
                      },
                      get disabled() {
                        return generating();
                      },
                      $$events: { click: () => handle_action()("undo") }
                    });
                  }
                };
                if_block(node_7, ($$render) => {
                  if (show_undo()) $$render(consequent_3);
                });
              }
              var node_8 = sibling(node_7, 2);
              {
                var consequent_4 = ($$anchor5) => {
                  {
                    let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("chatbot.edit"))));
                    IconButton($$anchor5, {
                      get label() {
                        return get($0);
                      },
                      get Icon() {
                        return Edit;
                      },
                      get disabled() {
                        return generating();
                      },
                      $$events: { click: () => handle_action()("edit") }
                    });
                  }
                };
                if_block(node_8, ($$render) => {
                  if (show_edit()) $$render(consequent_4);
                });
              }
              var node_9 = sibling(node_8, 2);
              {
                var consequent_5 = ($$anchor5) => {
                  LikeDislike($$anchor5, {
                    get handle_action() {
                      return handle_action();
                    },
                    get feedback_options() {
                      return feedback_options();
                    },
                    get selected() {
                      return current_feedback();
                    },
                    get i18n() {
                      return i18n();
                    }
                  });
                };
                if_block(node_9, ($$render) => {
                  if (likeable()) $$render(consequent_5);
                });
              }
              append($$anchor4, fragment_3);
            };
            if_block(node_2, ($$render) => {
              if (in_edit_mode()) $$render(consequent);
              else $$render(alternate, false);
            });
          }
          append($$anchor3, fragment_1);
        },
        $$slots: { default: true }
      });
      reset(div);
      template_effect(() => set_class(div, 1, `message-buttons-${position() ?? ""} ${layout() ?? ""} message-buttons ${avatar() !== null && "with-avatar"}`, "svelte-704d7y"));
      append($$anchor2, div);
    };
    if_block(node, ($$render) => {
      if (get(show_copy) || show_retry() || show_undo() || show_edit() || likeable()) $$render(consequent_6);
    });
  }
  append($$anchor, fragment);
  pop();
}
var root_7 = from_html(`<div style="position: relative;"><!></div>`);
var root_10$2 = from_html(`<track kind="captions"/>`);
function Component($$anchor, $$props) {
  push($$props, false);
  let type = prop($$props, "type", 8);
  let components = prop($$props, "components", 8);
  let value = prop($$props, "value", 8);
  let target = prop($$props, "target", 8);
  let theme_mode = prop($$props, "theme_mode", 8);
  let props = prop($$props, "props", 8);
  let i18n = prop($$props, "i18n", 8);
  let upload = prop($$props, "upload", 8);
  let _fetch = prop($$props, "_fetch", 8);
  let allow_file_downloads = prop($$props, "allow_file_downloads", 8);
  let display_icon_button_wrapper_top_corner = prop($$props, "display_icon_button_wrapper_top_corner", 8, false);
  legacy_pre_effect(() => (deep_read_state(type()), deep_read_state(components())), () => {
    console.log("Rendering component of type:", type(), components()[type()]);
  });
  legacy_pre_effect_reset();
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      var fragment_1 = comment();
      var node_1 = first_child(fragment_1);
      {
        let $0 = derived_safe_equal(() => (deep_read_state(props()), untrack(() => props().label ? true : false)));
        component(node_1, () => components()[type()], ($$anchor3, $$component) => {
          $$component($$anchor3, spread_props(props, {
            get value() {
              return value();
            },
            get display_icon_button_wrapper_top_corner() {
              return display_icon_button_wrapper_top_corner();
            },
            get show_label() {
              return get($0);
            },
            get i18n() {
              return i18n();
            },
            get _fetch() {
              return _fetch();
            },
            allow_preview: false,
            interactive: false,
            mode: "minimal",
            fixed_height: 1,
            $$events: {
              load($$arg) {
                bubble_event.call(this, $$props, $$arg);
              }
            }
          }));
        });
      }
      append($$anchor2, fragment_1);
    };
    var alternate_6 = ($$anchor2) => {
      var fragment_2 = comment();
      var node_2 = first_child(fragment_2);
      {
        var consequent_1 = ($$anchor3) => {
          var fragment_3 = comment();
          var node_3 = first_child(fragment_3);
          {
            let $0 = derived_safe_equal(() => (deep_read_state(props()), untrack(() => props().label ? true : false)));
            let $1 = derived_safe_equal(() => ({ dispatch: () => {
            }, i18n: i18n() }));
            component(node_3, () => components()[type()], ($$anchor4, $$component) => {
              $$component($$anchor4, spread_props(props, {
                get value() {
                  return value();
                },
                get show_label() {
                  return get($0);
                },
                get i18n() {
                  return i18n();
                },
                interactive: false,
                get line_breaks() {
                  return deep_read_state(props()), untrack(() => props().line_breaks);
                },
                wrap: true,
                root: "",
                get gradio() {
                  return get($1);
                },
                get datatype() {
                  return deep_read_state(props()), untrack(() => props().datatype);
                },
                get latex_delimiters() {
                  return deep_read_state(props()), untrack(() => props().latex_delimiters);
                },
                get col_count() {
                  return deep_read_state(props()), untrack(() => props().col_count);
                },
                get row_count() {
                  return deep_read_state(props()), untrack(() => props().row_count);
                },
                $$events: {
                  load($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  }
                }
              }));
            });
          }
          append($$anchor3, fragment_3);
        };
        var alternate_5 = ($$anchor3) => {
          var fragment_4 = comment();
          var node_4 = first_child(fragment_4);
          {
            var consequent_2 = ($$anchor4) => {
              var fragment_5 = comment();
              var node_5 = first_child(fragment_5);
              {
                let $0 = derived_safe_equal(() => (deep_read_state(props()), untrack(() => props().caption || "")));
                component(node_5, () => components()[type()], ($$anchor5, $$component) => {
                  $$component($$anchor5, spread_props(props, {
                    get value() {
                      return value();
                    },
                    get target() {
                      return target();
                    },
                    get theme_mode() {
                      return theme_mode();
                    },
                    get bokeh_version() {
                      return deep_read_state(props()), untrack(() => props().bokeh_version);
                    },
                    get caption() {
                      return get($0);
                    },
                    show_actions_button: true,
                    $$events: {
                      load($$arg) {
                        bubble_event.call(this, $$props, $$arg);
                      }
                    }
                  }));
                });
              }
              append($$anchor4, fragment_5);
            };
            var alternate_4 = ($$anchor4) => {
              var fragment_6 = comment();
              var node_6 = first_child(fragment_6);
              {
                var consequent_3 = ($$anchor5) => {
                  var div = root_7();
                  var node_7 = child(div);
                  {
                    let $0 = derived_safe_equal(() => (deep_read_state(props()), untrack(() => props().label ? true : false)));
                    let $1 = derived_safe_equal(() => (deep_read_state(props()), untrack(() => ({ ...props().waveform_settings, autoplay: props().autoplay }))));
                    component(node_7, () => components()[type()], ($$anchor6, $$component) => {
                      $$component($$anchor6, spread_props(props, {
                        get value() {
                          return value();
                        },
                        get show_label() {
                          return get($0);
                        },
                        show_share_button: true,
                        get i18n() {
                          return i18n();
                        },
                        get waveform_settings() {
                          return get($1);
                        },
                        get show_download_button() {
                          return allow_file_downloads();
                        },
                        get display_icon_button_wrapper_top_corner() {
                          return display_icon_button_wrapper_top_corner();
                        },
                        $$events: {
                          load($$arg) {
                            bubble_event.call(this, $$props, $$arg);
                          }
                        }
                      }));
                    });
                  }
                  reset(div);
                  append($$anchor5, div);
                };
                var alternate_3 = ($$anchor5) => {
                  var fragment_7 = comment();
                  var node_8 = first_child(fragment_7);
                  {
                    var consequent_4 = ($$anchor6) => {
                      var fragment_8 = comment();
                      var node_9 = first_child(fragment_8);
                      {
                        let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value().video || value())));
                        let $1 = derived_safe_equal(() => (deep_read_state(props()), untrack(() => props().label ? true : false)));
                        component(node_9, () => components()[type()], ($$anchor7, $$component) => {
                          $$component($$anchor7, spread_props(props, {
                            get autoplay() {
                              return deep_read_state(props()), untrack(() => props().autoplay);
                            },
                            get value() {
                              return get($0);
                            },
                            get show_label() {
                              return get($1);
                            },
                            show_share_button: true,
                            get i18n() {
                              return i18n();
                            },
                            get upload() {
                              return upload();
                            },
                            get display_icon_button_wrapper_top_corner() {
                              return display_icon_button_wrapper_top_corner();
                            },
                            get show_download_button() {
                              return allow_file_downloads();
                            },
                            $$events: {
                              load($$arg) {
                                bubble_event.call(this, $$props, $$arg);
                              }
                            },
                            children: ($$anchor8, $$slotProps) => {
                              var track = root_10$2();
                              append($$anchor8, track);
                            },
                            $$slots: { default: true }
                          }));
                        });
                      }
                      append($$anchor6, fragment_8);
                    };
                    var alternate_2 = ($$anchor6) => {
                      var fragment_9 = comment();
                      var node_10 = first_child(fragment_9);
                      {
                        var consequent_5 = ($$anchor7) => {
                          var fragment_10 = comment();
                          var node_11 = first_child(fragment_10);
                          {
                            let $0 = derived_safe_equal(() => (deep_read_state(props()), untrack(() => props().label ? true : false)));
                            component(node_11, () => components()[type()], ($$anchor8, $$component) => {
                              $$component($$anchor8, spread_props(props, {
                                get value() {
                                  return value();
                                },
                                get show_label() {
                                  return get($0);
                                },
                                get show_download_button() {
                                  return allow_file_downloads();
                                },
                                get display_icon_button_wrapper_top_corner() {
                                  return display_icon_button_wrapper_top_corner();
                                },
                                get i18n() {
                                  return i18n();
                                },
                                $$events: {
                                  load($$arg) {
                                    bubble_event.call(this, $$props, $$arg);
                                  }
                                }
                              }));
                            });
                          }
                          append($$anchor7, fragment_10);
                        };
                        var alternate_1 = ($$anchor7) => {
                          var fragment_11 = comment();
                          var node_12 = first_child(fragment_11);
                          {
                            var consequent_6 = ($$anchor8) => {
                              var fragment_12 = comment();
                              var node_13 = first_child(fragment_12);
                              component(node_13, () => components()[type()], ($$anchor9, $$component) => {
                                $$component($$anchor9, spread_props(props, {
                                  get value() {
                                    return value();
                                  },
                                  show_label: false,
                                  show_share_button: true,
                                  get i18n() {
                                    return i18n();
                                  },
                                  gradio: { dispatch: () => {
                                  } },
                                  $$events: {
                                    load($$arg) {
                                      bubble_event.call(this, $$props, $$arg);
                                    }
                                  }
                                }));
                              });
                              append($$anchor8, fragment_12);
                            };
                            var alternate = ($$anchor8) => {
                              var fragment_13 = comment();
                              var node_14 = first_child(fragment_13);
                              {
                                var consequent_7 = ($$anchor9) => {
                                  var fragment_14 = comment();
                                  var node_15 = first_child(fragment_14);
                                  {
                                    let $0 = derived_safe_equal(() => (deep_read_state(props()), untrack(() => props().label ? true : false)));
                                    let $1 = derived_safe_equal(() => ({ dispatch: () => {
                                    }, i18n: i18n() }));
                                    component(node_15, () => components()[type()], ($$anchor10, $$component) => {
                                      $$component($$anchor10, spread_props(
                                        props,
                                        {
                                          get value() {
                                            return value();
                                          },
                                          get clear_color() {
                                            return deep_read_state(props()), untrack(() => props().clear_color);
                                          },
                                          get display_mode() {
                                            return deep_read_state(props()), untrack(() => props().display_mode);
                                          },
                                          get zoom_speed() {
                                            return deep_read_state(props()), untrack(() => props().zoom_speed);
                                          },
                                          get pan_speed() {
                                            return deep_read_state(props()), untrack(() => props().pan_speed);
                                          }
                                        },
                                        () => props().camera_position !== void 0 && { camera_position: props().camera_position },
                                        {
                                          has_change_history: true,
                                          get show_label() {
                                            return get($0);
                                          },
                                          root: "",
                                          interactive: false,
                                          show_share_button: true,
                                          get gradio() {
                                            return get($1);
                                          },
                                          get i18n() {
                                            return i18n();
                                          },
                                          $$events: {
                                            load($$arg) {
                                              bubble_event.call(this, $$props, $$arg);
                                            }
                                          }
                                        }
                                      ));
                                    });
                                  }
                                  append($$anchor9, fragment_14);
                                };
                                if_block(
                                  node_14,
                                  ($$render) => {
                                    if (type() === "model3d") $$render(consequent_7);
                                  },
                                  true
                                );
                              }
                              append($$anchor8, fragment_13);
                            };
                            if_block(
                              node_12,
                              ($$render) => {
                                if (type() === "html") $$render(consequent_6);
                                else $$render(alternate, false);
                              },
                              true
                            );
                          }
                          append($$anchor7, fragment_11);
                        };
                        if_block(
                          node_10,
                          ($$render) => {
                            if (type() === "image") $$render(consequent_5);
                            else $$render(alternate_1, false);
                          },
                          true
                        );
                      }
                      append($$anchor6, fragment_9);
                    };
                    if_block(
                      node_8,
                      ($$render) => {
                        if (type() === "video") $$render(consequent_4);
                        else $$render(alternate_2, false);
                      },
                      true
                    );
                  }
                  append($$anchor5, fragment_7);
                };
                if_block(
                  node_6,
                  ($$render) => {
                    if (type() === "audio") $$render(consequent_3);
                    else $$render(alternate_3, false);
                  },
                  true
                );
              }
              append($$anchor4, fragment_6);
            };
            if_block(
              node_4,
              ($$render) => {
                if (type() === "plot") $$render(consequent_2);
                else $$render(alternate_4, false);
              },
              true
            );
          }
          append($$anchor3, fragment_4);
        };
        if_block(
          node_2,
          ($$render) => {
            if (type() === "dataframe") $$render(consequent_1);
            else $$render(alternate_5, false);
          },
          true
        );
      }
      append($$anchor2, fragment_2);
    };
    if_block(node, ($$render) => {
      if (type() === "gallery") $$render(consequent);
      else $$render(alternate_6, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
var root_1$5 = from_html(`<div class="message-content"><!></div>`);
var root_5$1 = from_html(`<div class="file-container svelte-e5gd5s"><div class="file-icon svelte-e5gd5s"><!></div> <div class="file-info svelte-e5gd5s"><a data-testid="chatbot-file" class="file-link svelte-e5gd5s" target="_blank"><span class="file-name svelte-e5gd5s"> </span></a> <span class="file-type svelte-e5gd5s"> </span></div></div>`);
function MessageContent($$anchor, $$props) {
  push($$props, false);
  let latex_delimiters = prop($$props, "latex_delimiters", 8);
  let sanitize_html = prop($$props, "sanitize_html", 8);
  let _fetch = prop($$props, "_fetch", 8);
  let i18n = prop($$props, "i18n", 8);
  let line_breaks = prop($$props, "line_breaks", 8);
  let upload = prop($$props, "upload", 8);
  let target = prop($$props, "target", 8);
  let theme_mode = prop($$props, "theme_mode", 8);
  let _components = prop($$props, "_components", 8);
  let render_markdown = prop($$props, "render_markdown", 8);
  let scroll2 = prop($$props, "scroll", 8);
  let allow_file_downloads = prop($$props, "allow_file_downloads", 8);
  let display_consecutive_in_same_bubble = prop($$props, "display_consecutive_in_same_bubble", 8);
  let thought_index = prop($$props, "thought_index", 8);
  let allow_tags = prop($$props, "allow_tags", 8, false);
  let message = prop($$props, "message", 8);
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      var div = root_1$5();
      var node_1 = child(div);
      MarkdownCode(node_1, {
        get message() {
          return deep_read_state(message()), untrack(() => message().content);
        },
        get latex_delimiters() {
          return latex_delimiters();
        },
        get sanitize_html() {
          return sanitize_html();
        },
        get render_markdown() {
          return render_markdown();
        },
        get line_breaks() {
          return line_breaks();
        },
        get allow_tags() {
          return allow_tags();
        },
        get theme_mode() {
          return theme_mode();
        },
        $$events: {
          load(...$$args) {
            scroll2()?.apply(this, $$args);
          }
        }
      });
      reset(div);
      append($$anchor2, div);
    };
    var alternate_1 = ($$anchor2) => {
      var fragment_1 = comment();
      var node_2 = first_child(fragment_1);
      {
        var consequent_1 = ($$anchor3) => {
          {
            let $0 = derived_safe_equal(() => thought_index() > 0 && display_consecutive_in_same_bubble());
            Component($$anchor3, {
              get target() {
                return target();
              },
              get theme_mode() {
                return theme_mode();
              },
              get props() {
                return deep_read_state(message()), untrack(() => message().content.props);
              },
              get type() {
                return deep_read_state(message()), untrack(() => message().content.component);
              },
              get components() {
                return _components();
              },
              get value() {
                return deep_read_state(message()), untrack(() => message().content.value);
              },
              get display_icon_button_wrapper_top_corner() {
                return get($0);
              },
              get i18n() {
                return i18n();
              },
              get upload() {
                return upload();
              },
              get _fetch() {
                return _fetch();
              },
              get allow_file_downloads() {
                return allow_file_downloads();
              },
              $$events: { load: () => scroll2()() }
            });
          }
        };
        var alternate = ($$anchor3) => {
          var fragment_3 = comment();
          var node_3 = first_child(fragment_3);
          {
            var consequent_2 = ($$anchor4) => {
              var div_1 = root_5$1();
              var div_2 = child(div_1);
              var node_4 = child(div_2);
              File(node_4);
              reset(div_2);
              var div_3 = sibling(div_2, 2);
              var a = child(div_3);
              var span = child(a);
              var text2 = child(span, true);
              reset(span);
              reset(a);
              var span_1 = sibling(a, 2);
              var text_1 = child(span_1, true);
              reset(span_1);
              reset(div_3);
              reset(div_1);
              template_effect(
                ($0, $1, $2) => {
                  set_attribute(a, "href", (deep_read_state(message()), untrack(() => message().content.value.url)));
                  set_attribute(a, "download", $0);
                  set_text(text2, $1);
                  set_text(text_1, $2);
                },
                [
                  () => (deep_read_state(message()), untrack(() => window.__is_colab__ ? null : message().content.value?.orig_name || message().content.value?.path.split("/").pop() || "file")),
                  () => (deep_read_state(message()), untrack(() => message().content.value?.orig_name || message().content.value?.path.split("/").pop() || "file")),
                  () => (deep_read_state(message()), untrack(() => (message().content.value?.orig_name || message().content.value?.path || "").split(".").pop().toUpperCase()))
                ]
              );
              append($$anchor4, div_1);
            };
            if_block(
              node_3,
              ($$render) => {
                if (deep_read_state(message()), untrack(() => message().type === "component" && message().content.component === "file")) $$render(consequent_2);
              },
              true
            );
          }
          append($$anchor3, fragment_3);
        };
        if_block(
          node_2,
          ($$render) => {
            if (deep_read_state(message()), deep_read_state(_components()), untrack(() => message().type === "component" && message().content.component in _components())) $$render(consequent_1);
            else $$render(alternate, false);
          },
          true
        );
      }
      append($$anchor2, fragment_1);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(message()), untrack(() => message().type === "text")) $$render(consequent);
      else $$render(alternate_1, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
var root_1$4 = from_html(`<span class="loading-spinner svelte-18cn3o3"></span>`);
var root_4$2 = from_html(`(<!>)`, 1);
var root_2$3 = from_html(`<span class="duration svelte-18cn3o3"><!> <!></span>`);
var root_10$1 = from_html(`<div class="children svelte-18cn3o3"></div>`);
var root_9$1 = from_html(`<div><!> <!></div>`);
var root$4 = from_html(`<div class="thought-group svelte-18cn3o3"><div role="button" tabindex="0"><span class="arrow svelte-18cn3o3"><!></span> <!> <!> <!></div> <!></div>`);
function Thought($$anchor, $$props) {
  push($$props, true);
  function is_thought_node(msg) {
    return "children" in msg;
  }
  let user_expanded_toggled = state(false);
  let content_preview_element;
  let user_is_scrolling = state(false);
  let thought_node = user_derived(() => ({
    ...$$props.thought,
    children: is_thought_node($$props.thought) ? $$props.thought.children : []
  }));
  let expanded = state(false);
  user_effect(() => {
    if (!get(user_expanded_toggled)) {
      set(expanded, get(thought_node)?.metadata?.status !== "done");
    }
  });
  function toggleExpanded() {
    set(expanded, !get(expanded));
    set(user_expanded_toggled, true);
  }
  function scrollToBottom() {
    if (content_preview_element && !get(user_is_scrolling)) {
      content_preview_element.scrollTop = content_preview_element.scrollHeight;
    }
  }
  function handleScroll() {
    if (content_preview_element) {
      const is_at_bottom = content_preview_element.scrollHeight - content_preview_element.scrollTop <= content_preview_element.clientHeight + 10;
      if (!is_at_bottom) {
        set(user_is_scrolling, true);
      }
    }
  }
  user_effect(() => {
    if (get(thought_node).content && get(thought_node).metadata?.status !== "done") setTimeout(scrollToBottom, 0);
  });
  var div = root$4();
  var div_1 = child(div);
  let classes;
  var span = child(div_1);
  let styles;
  var node = child(span);
  IconButton(node, {
    get Icon() {
      return DropdownCircularArrow;
    }
  });
  reset(span);
  var node_1 = sibling(span, 2);
  {
    let $0 = user_derived(() => get(thought_node).metadata?.title || "");
    let $1 = user_derived(() => $$props.allow_tags || false);
    MarkdownCode(node_1, {
      get message() {
        return get($0);
      },
      get render_markdown() {
        return $$props.render_markdown;
      },
      get latex_delimiters() {
        return $$props.latex_delimiters;
      },
      get sanitize_html() {
        return $$props.sanitize_html;
      },
      get allow_tags() {
        return get($1);
      }
    });
  }
  var node_2 = sibling(node_1, 2);
  {
    var consequent = ($$anchor2) => {
      var span_1 = root_1$4();
      append($$anchor2, span_1);
    };
    if_block(node_2, ($$render) => {
      if (get(thought_node).metadata?.status === "pending") $$render(consequent);
    });
  }
  var node_3 = sibling(node_2, 2);
  {
    var consequent_5 = ($$anchor2) => {
      var span_2 = root_2$3();
      var node_4 = child(span_2);
      {
        var consequent_1 = ($$anchor3) => {
          var text$1 = text();
          template_effect(() => set_text(text$1, get(thought_node).metadata.log));
          append($$anchor3, text$1);
        };
        if_block(node_4, ($$render) => {
          if (get(thought_node).metadata.log) $$render(consequent_1);
        });
      }
      var node_5 = sibling(node_4, 2);
      {
        var consequent_4 = ($$anchor3) => {
          var fragment_1 = root_4$2();
          var node_6 = sibling(first_child(fragment_1));
          {
            var consequent_2 = ($$anchor4) => {
              var text_1 = text();
              template_effect(() => set_text(text_1, `${get(thought_node).metadata.duration ?? ""}s`));
              append($$anchor4, text_1);
            };
            var alternate_1 = ($$anchor4) => {
              var fragment_3 = comment();
              var node_7 = first_child(fragment_3);
              {
                var consequent_3 = ($$anchor5) => {
                  var text_2 = text();
                  template_effect(($0) => set_text(text_2, `${$0 ?? ""}s`), [() => get(thought_node).metadata.duration.toFixed(1)]);
                  append($$anchor5, text_2);
                };
                var alternate = ($$anchor5) => {
                  var text_3 = text();
                  template_effect(($0) => set_text(text_3, `${$0 ?? ""}ms`), [
                    () => (get(thought_node).metadata.duration * 1e3).toFixed(1)
                  ]);
                  append($$anchor5, text_3);
                };
                if_block(
                  node_7,
                  ($$render) => {
                    if (get(thought_node).metadata.duration >= 0.1) $$render(consequent_3);
                    else $$render(alternate, false);
                  },
                  true
                );
              }
              append($$anchor4, fragment_3);
            };
            if_block(node_6, ($$render) => {
              if (Number.isInteger(get(thought_node).metadata.duration)) $$render(consequent_2);
              else $$render(alternate_1, false);
            });
          }
          next();
          append($$anchor3, fragment_1);
        };
        if_block(node_5, ($$render) => {
          if (get(thought_node).metadata.duration !== void 0) $$render(consequent_4);
        });
      }
      reset(span_2);
      append($$anchor2, span_2);
    };
    if_block(node_3, ($$render) => {
      if (get(thought_node)?.metadata?.log || get(thought_node)?.metadata?.duration) $$render(consequent_5);
    });
  }
  reset(div_1);
  var node_8 = sibling(div_1, 2);
  {
    var consequent_7 = ($$anchor2) => {
      var div_2 = root_9$1();
      let classes_1;
      var node_9 = child(div_2);
      MessageContent(node_9, {
        get message() {
          return get(thought_node);
        },
        get sanitize_html() {
          return $$props.sanitize_html;
        },
        get allow_tags() {
          return $$props.allow_tags;
        },
        get latex_delimiters() {
          return $$props.latex_delimiters;
        },
        get render_markdown() {
          return $$props.render_markdown;
        },
        get _components() {
          return $$props._components;
        },
        get upload() {
          return $$props.upload;
        },
        get thought_index() {
          return $$props.thought_index;
        },
        get target() {
          return $$props.target;
        },
        get theme_mode() {
          return $$props.theme_mode;
        },
        get _fetch() {
          return $$props._fetch;
        },
        get scroll() {
          return $$props.scroll;
        },
        get allow_file_downloads() {
          return $$props.allow_file_downloads;
        },
        get display_consecutive_in_same_bubble() {
          return $$props.display_consecutive_in_same_bubble;
        },
        get i18n() {
          return $$props.i18n;
        },
        get line_breaks() {
          return $$props.line_breaks;
        }
      });
      var node_10 = sibling(node_9, 2);
      {
        var consequent_6 = ($$anchor3) => {
          var div_3 = root_10$1();
          each(div_3, 21, () => get(thought_node).children, index, ($$anchor4, child2) => {
            var fragment_6 = comment();
            var node_11 = first_child(fragment_6);
            {
              let $0 = user_derived(() => $$props.rtl || false);
              let $1 = user_derived(() => $$props.thought_index + 1);
              Thought(node_11, {
                get thought() {
                  return get(child2);
                },
                get rtc() {
                  return get($0);
                },
                get sanitize_html() {
                  return $$props.sanitize_html;
                },
                get latex_delimiters() {
                  return $$props.latex_delimiters;
                },
                get render_markdown() {
                  return $$props.render_markdown;
                },
                get _components() {
                  return $$props._components;
                },
                get upload() {
                  return $$props.upload;
                },
                get thought_index() {
                  return get($1);
                },
                get target() {
                  return $$props.target;
                },
                get theme_mode() {
                  return $$props.theme_mode;
                },
                get _fetch() {
                  return $$props._fetch;
                },
                get scroll() {
                  return $$props.scroll;
                },
                get allow_file_downloads() {
                  return $$props.allow_file_downloads;
                },
                get display_consecutive_in_same_bubble() {
                  return $$props.display_consecutive_in_same_bubble;
                },
                get i18n() {
                  return $$props.i18n;
                },
                get line_breaks() {
                  return $$props.line_breaks;
                }
              });
            }
            append($$anchor4, fragment_6);
          });
          reset(div_3);
          append($$anchor3, div_3);
        };
        if_block(node_10, ($$render) => {
          if (get(thought_node).children?.length > 0) $$render(consequent_6);
        });
      }
      reset(div_2);
      bind_this(div_2, ($$value) => content_preview_element = $$value, () => content_preview_element);
      template_effect(() => classes_1 = set_class(div_2, 1, "svelte-18cn3o3", null, classes_1, {
        content: get(expanded),
        "content-preview": !get(expanded) && get(thought_node).metadata?.status !== "done"
      }));
      event("scroll", div_2, handleScroll);
      transition(3, div_2, () => slide);
      append($$anchor2, div_2);
    };
    if_block(node_8, ($$render) => {
      if (get(expanded)) $$render(consequent_7);
    });
  }
  reset(div);
  template_effect(() => {
    classes = set_class(div_1, 1, "title svelte-18cn3o3", null, classes, { expanded: get(expanded) });
    set_attribute(div_1, "aria-busy", get(thought_node).content === "" || get(thought_node).content === null);
    styles = set_style(span, "", styles, {
      transform: get(expanded) ? "rotate(180deg)" : "rotate(0deg)"
    });
  });
  event("click", div_1, stopPropagation(toggleExpanded));
  event("keydown", div_1, (e) => e.key === "Enter" && toggleExpanded());
  append($$anchor, div);
  pop();
}
var root_1$3 = from_html(`<div class="avatar-container svelte-1nr59td"><!></div>`);
var root_3$1 = from_html(`<textarea class="edit-textarea svelte-1nr59td"></textarea>`);
var root_4$1 = from_html(`<div><!></div>`);
var root_2$2 = from_html(`<div><!></div> <!>`, 1);
var root$3 = from_html(`<div><!> <div><div></div></div></div> <!>`, 1);
function Message($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  let avatar_img = prop($$props, "avatar_img", 8);
  let opposite_avatar_img = prop($$props, "opposite_avatar_img", 8, null);
  let role = prop($$props, "role", 8, "user");
  let messages = prop($$props, "messages", 24, () => []);
  let layout = prop($$props, "layout", 8);
  let render_markdown = prop($$props, "render_markdown", 8);
  let latex_delimiters = prop($$props, "latex_delimiters", 8);
  let sanitize_html = prop($$props, "sanitize_html", 8);
  let selectable = prop($$props, "selectable", 8);
  let _fetch = prop($$props, "_fetch", 8);
  let rtl = prop($$props, "rtl", 8);
  let dispatch = prop($$props, "dispatch", 8);
  let i18n = prop($$props, "i18n", 8);
  let line_breaks = prop($$props, "line_breaks", 8);
  let upload = prop($$props, "upload", 8);
  let target = prop($$props, "target", 8);
  let theme_mode = prop($$props, "theme_mode", 8);
  let _components = prop($$props, "_components", 8);
  let i = prop($$props, "i", 8);
  let show_copy_button = prop($$props, "show_copy_button", 8);
  let generating = prop($$props, "generating", 8);
  let feedback_options = prop($$props, "feedback_options", 8);
  let show_like = prop($$props, "show_like", 8);
  let show_edit = prop($$props, "show_edit", 8);
  let show_retry = prop($$props, "show_retry", 8);
  let show_undo = prop($$props, "show_undo", 8);
  let handle_action = prop($$props, "handle_action", 8);
  let scroll2 = prop($$props, "scroll", 8);
  let allow_file_downloads = prop($$props, "allow_file_downloads", 8);
  let in_edit_mode = prop($$props, "in_edit_mode", 8);
  let edit_messages = prop($$props, "edit_messages", 12);
  let display_consecutive_in_same_bubble = prop($$props, "display_consecutive_in_same_bubble", 8);
  let current_feedback = prop($$props, "current_feedback", 8, null);
  let allow_tags = prop($$props, "allow_tags", 8, false);
  let watermark = prop($$props, "watermark", 8, null);
  let messageElements = mutable_source([]);
  let message_widths = mutable_source(Array(messages().length).fill(160));
  let message_heights = mutable_source(Array(messages().length).fill(0));
  function handle_select(i2, message) {
    dispatch()("select", { index: message.index, value: message.content });
  }
  function get_message_label_data(message) {
    if (message.type === "text") {
      return message.content;
    } else if (message.type === "component" && message.content.component === "file") {
      if (Array.isArray(message.content.value)) {
        return `file of extension type: ${message.content.value[0].orig_name?.split(".").pop()}`;
      }
      return `file of extension type: ${message.content.value?.orig_name?.split(".").pop()}` + (message.content.value?.orig_name ?? "");
    }
    return `a component of type ${message.content.component ?? "unknown"}`;
  }
  let button_panel_props = mutable_source();
  legacy_pre_effect(
    () => (deep_read_state(in_edit_mode()), get(messageElements), deep_read_state(messages())),
    () => {
      if (in_edit_mode() && true) {
        const offset = get(messageElements).length - messages().length;
        for (let idx = offset; idx < get(messageElements).length; idx++) {
          if (idx >= 0) {
            mutate(message_widths, get(message_widths)[idx - offset] = get(messageElements)[idx]?.clientWidth);
            mutate(message_heights, get(message_heights)[idx - offset] = get(messageElements)[idx]?.clientHeight);
          }
        }
      }
    }
  );
  legacy_pre_effect(
    () => (deep_read_state(handle_action()), deep_read_state(show_like()), deep_read_state(feedback_options()), deep_read_state(show_retry()), deep_read_state(show_undo()), deep_read_state(show_edit()), deep_read_state(in_edit_mode()), deep_read_state(generating()), deep_read_state(show_copy_button()), deep_read_state(messages()), deep_read_state(role()), deep_read_state(avatar_img()), deep_read_state(layout()), deep_read_state(dispatch()), deep_read_state(current_feedback()), deep_read_state(watermark())),
    () => {
      set(button_panel_props, {
        handle_action: handle_action(),
        likeable: show_like(),
        feedback_options: feedback_options(),
        show_retry: show_retry(),
        show_undo: show_undo(),
        show_edit: show_edit(),
        in_edit_mode: in_edit_mode(),
        generating: generating(),
        show_copy_button: show_copy_button(),
        message: messages(),
        position: role() === "user" ? "right" : "left",
        avatar: avatar_img(),
        layout: layout(),
        dispatch: dispatch(),
        current_feedback: current_feedback(),
        watermark: watermark()
      });
    }
  );
  legacy_pre_effect_reset();
  init();
  var fragment = root$3();
  var div = first_child(fragment);
  let classes;
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      var div_1 = root_1$3();
      var node_1 = child(div_1);
      {
        let $0 = derived_safe_equal(() => (deep_read_state(avatar_img()), untrack(() => avatar_img()?.url)));
        Image(node_1, {
          class: "avatar-image",
          get src() {
            return get($0);
          },
          get alt() {
            return `${role() ?? ""} avatar`;
          }
        });
      }
      reset(div_1);
      append($$anchor2, div_1);
    };
    if_block(node, ($$render) => {
      if (avatar_img() !== null) $$render(consequent);
    });
  }
  var div_2 = sibling(node, 2);
  let classes_1;
  var div_3 = child(div_2);
  let classes_2;
  each(div_3, 5, messages, index, ($$anchor2, message, thought_index) => {
    var fragment_1 = root_2$2();
    var div_4 = first_child(fragment_1);
    let classes_3;
    var node_2 = child(div_4);
    {
      var consequent_1 = ($$anchor3) => {
        var textarea = root_3$1();
        remove_textarea_child(textarea);
        autofocus(textarea, true);
        let styles;
        template_effect(() => styles = set_style(textarea, "", styles, {
          width: (get(message_widths), untrack(() => `max(${get(message_widths)[thought_index]}px, 160px)`)),
          "min-height": (get(message_heights), untrack(() => `${get(message_heights)[thought_index]}px`))
        }));
        bind_value(textarea, () => edit_messages()[thought_index], ($$value) => edit_messages(edit_messages()[thought_index] = $$value, true));
        append($$anchor3, textarea);
      };
      var alternate_1 = ($$anchor3) => {
        var div_5 = root_4$1();
        let classes_4;
        let styles_1;
        var node_3 = child(div_5);
        {
          var consequent_2 = ($$anchor4) => {
            Thought($$anchor4, {
              get thought() {
                return get(message);
              },
              get rtl() {
                return rtl();
              },
              get sanitize_html() {
                return sanitize_html();
              },
              get allow_tags() {
                return allow_tags();
              },
              get latex_delimiters() {
                return latex_delimiters();
              },
              get render_markdown() {
                return render_markdown();
              },
              get _components() {
                return _components();
              },
              get upload() {
                return upload();
              },
              thought_index,
              get target() {
                return target();
              },
              get theme_mode() {
                return theme_mode();
              },
              get _fetch() {
                return _fetch();
              },
              get scroll() {
                return scroll2();
              },
              get allow_file_downloads() {
                return allow_file_downloads();
              },
              get display_consecutive_in_same_bubble() {
                return display_consecutive_in_same_bubble();
              },
              get i18n() {
                return i18n();
              },
              get line_breaks() {
                return line_breaks();
              }
            });
          };
          var alternate = ($$anchor4) => {
            MessageContent($$anchor4, {
              get message() {
                return get(message);
              },
              get sanitize_html() {
                return sanitize_html();
              },
              get allow_tags() {
                return allow_tags();
              },
              get latex_delimiters() {
                return latex_delimiters();
              },
              get render_markdown() {
                return render_markdown();
              },
              get _components() {
                return _components();
              },
              get upload() {
                return upload();
              },
              thought_index,
              get target() {
                return target();
              },
              get theme_mode() {
                return theme_mode();
              },
              get _fetch() {
                return _fetch();
              },
              get scroll() {
                return scroll2();
              },
              get allow_file_downloads() {
                return allow_file_downloads();
              },
              get display_consecutive_in_same_bubble() {
                return display_consecutive_in_same_bubble();
              },
              get i18n() {
                return i18n();
              },
              get line_breaks() {
                return line_breaks();
              }
            });
          };
          if_block(node_3, ($$render) => {
            if (get(message), untrack(() => get(message)?.metadata?.title)) $$render(consequent_2);
            else $$render(alternate, false);
          });
        }
        reset(div_5);
        bind_this(div_5, ($$value, thought_index2) => mutate(messageElements, get(messageElements)[thought_index2] = $$value), (thought_index2) => get(messageElements)?.[thought_index2], () => [thought_index]);
        template_effect(
          ($0) => {
            set_attribute(div_5, "data-testid", role());
            set_attribute(div_5, "dir", rtl() ? "rtl" : "ltr");
            set_attribute(div_5, "aria-label", $0);
            classes_4 = set_class(div_5, 1, "svelte-1nr59td", null, classes_4, {
              latest: i() === value().length - 1,
              "message-markdown-disabled": !render_markdown(),
              selectable: selectable()
            });
            styles_1 = set_style(div_5, "", styles_1, {
              "user-select": "text",
              cursor: selectable() ? "pointer" : "auto",
              "text-align": rtl() ? "right" : "left"
            });
            div_5.dir = div_5.dir;
          },
          [
            () => (deep_read_state(role()), get(message), untrack(() => role() + "'s message: " + get_message_label_data(get(message))))
          ]
        );
        event("click", div_5, () => handle_select(i(), get(message)));
        event("keydown", div_5, (e) => {
          if (e.key === "Enter") {
            handle_select(i(), get(message));
          }
        });
        append($$anchor3, div_5);
      };
      if_block(node_2, ($$render) => {
        if (deep_read_state(in_edit_mode()), get(message), untrack(() => in_edit_mode() && get(message).type === "text")) $$render(consequent_1);
        else $$render(alternate_1, false);
      });
    }
    reset(div_4);
    var node_4 = sibling(div_4, 2);
    {
      var consequent_3 = ($$anchor3) => {
        ButtonPanel($$anchor3, spread_props(() => get(button_panel_props), {
          get current_feedback() {
            return current_feedback();
          },
          get watermark() {
            return watermark();
          },
          get i18n() {
            return i18n();
          },
          $$events: { copy: (e) => dispatch()("copy", e.detail) }
        }));
      };
      if_block(node_4, ($$render) => {
        if (layout() === "panel") $$render(consequent_3);
      });
    }
    template_effect(($0) => classes_3 = set_class(div_4, 1, `message ${(!display_consecutive_in_same_bubble() ? role() : "") ?? ""}`, "svelte-1nr59td", classes_3, $0), [
      () => ({
        "panel-full-width": true,
        "message-markdown-disabled": !render_markdown(),
        component: get(message).type === "component",
        html: is_component_message(get(message)) && get(message).content.component === "html",
        thought: thought_index > 0
      })
    ]);
    append($$anchor2, fragment_1);
  });
  reset(div_3);
  reset(div_2);
  reset(div);
  var node_5 = sibling(div, 2);
  {
    var consequent_4 = ($$anchor2) => {
      ButtonPanel($$anchor2, spread_props(() => get(button_panel_props), {
        get i18n() {
          return i18n();
        }
      }));
    };
    if_block(node_5, ($$render) => {
      if (layout() === "bubble") $$render(consequent_4);
    });
  }
  template_effect(() => {
    classes = set_class(div, 1, `message-row ${layout() ?? ""} ${role() ?? ""}-row`, "svelte-1nr59td", classes, {
      with_avatar: avatar_img() !== null,
      with_opposite_avatar: opposite_avatar_img() !== null
    });
    classes_1 = set_class(div_2, 1, "flex-wrap svelte-1nr59td", null, classes_1, {
      role: role(),
      "component-wrap": messages()[0].type === "component"
    });
    classes_2 = set_class(div_3, 1, clsx(display_consecutive_in_same_bubble() ? role() : ""), "svelte-1nr59td", classes_2, { message: display_consecutive_in_same_bubble() });
  });
  append($$anchor, fragment);
  pop();
}
var root_1$2 = from_html(`<div class="avatar-container svelte-stpvyx"><!></div>`);
var root$2 = from_html(`<div class="container svelte-stpvyx"><!> <div role="status" aria-label="Loading response" aria-live="polite"><div class="message-content svelte-stpvyx"><span class="sr-only svelte-stpvyx">Loading content</span> <div class="dots svelte-stpvyx"><div class="dot svelte-stpvyx"></div> <div class="dot svelte-stpvyx"></div> <div class="dot svelte-stpvyx"></div></div></div></div></div>`);
function Pending($$anchor, $$props) {
  push($$props, false);
  let layout = prop($$props, "layout", 8, "bubble");
  let avatar_images = prop($$props, "avatar_images", 24, () => [null, null]);
  init();
  var div = root$2();
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      var div_1 = root_1$2();
      var node_1 = child(div_1);
      Image(node_1, {
        class: "avatar-image",
        get src() {
          return deep_read_state(avatar_images()), untrack(() => avatar_images()[1].url);
        },
        alt: "bot avatar"
      });
      reset(div_1);
      append($$anchor2, div_1);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(avatar_images()), untrack(() => avatar_images()[1] !== null)) $$render(consequent);
    });
  }
  var div_2 = sibling(node, 2);
  let classes;
  reset(div);
  template_effect(() => classes = set_class(div_2, 1, `message bot pending ${layout() ?? ""}`, "svelte-stpvyx", classes, {
    with_avatar: avatar_images()[1] !== null,
    with_opposite_avatar: avatar_images()[0] !== null
  }));
  append($$anchor, div);
  pop();
}
var root_1$1 = from_html(`<div class="placeholder svelte-1rn3hyj"><!></div>`);
var root_4 = from_html(`<div class="example-image-container svelte-1rn3hyj"><!></div>`);
var root_6$1 = from_html(`<div class="example-icon svelte-1rn3hyj" aria-hidden="true"><span class="text-icon-aa svelte-1rn3hyj">Aa</span></div>`);
var root_12 = from_html(`<div class="image-overlay svelte-1rn3hyj" role="status"> </div>`);
var root_11$1 = from_html(`<div class="example-image-container svelte-1rn3hyj"><!> <!></div>`);
var root_15 = from_html(`<div class="image-overlay svelte-1rn3hyj" role="status"> </div>`);
var root_14 = from_html(`<div class="example-image-container svelte-1rn3hyj"><video class="example-image" aria-hidden="true"></video> <!></div>`, 2);
var root_16 = from_html(`<div class="example-icon svelte-1rn3hyj"><!></div>`);
var root_19 = from_html(`<div class="example-icon svelte-1rn3hyj"><div class="file-overlay svelte-1rn3hyj" role="status"> </div></div>`);
var root_9 = from_html(`<div class="example-icons-grid svelte-1rn3hyj" role="group" aria-label="Example attachments"><!> <!></div>`);
var root_21 = from_html(`<div class="example-image-container svelte-1rn3hyj"><!></div>`);
var root_23 = from_html(`<div class="example-image-container svelte-1rn3hyj"><video class="example-image" aria-hidden="true"></video></div>`, 2);
var root_25 = from_html(`<div class="example-icon svelte-1rn3hyj"><!></div>`);
var root_26 = from_html(`<div class="example-icon svelte-1rn3hyj"><!></div>`);
var root_3 = from_html(`<button class="example svelte-1rn3hyj"><div class="example-content svelte-1rn3hyj"><!> <div class="example-text-content svelte-1rn3hyj"><span class="example-text svelte-1rn3hyj"> </span></div></div></button>`);
var root_2$1 = from_html(`<div class="examples svelte-1rn3hyj" role="list"></div>`);
var root$1 = from_html(`<div class="placeholder-content svelte-1rn3hyj" role="complementary"><!> <!></div>`);
function Examples($$anchor, $$props) {
  push($$props, false);
  let examples = prop($$props, "examples", 8, null);
  let placeholder = prop($$props, "placeholder", 8, null);
  let latex_delimiters = prop($$props, "latex_delimiters", 8);
  const dispatch = createEventDispatcher();
  function handle_example_select(i, example) {
    const example_obj = typeof example === "string" ? { text: example } : example;
    dispatch("example_select", {
      index: i,
      value: { text: example_obj.text, files: example_obj.files }
    });
  }
  init();
  var div = root$1();
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      var div_1 = root_1$1();
      var node_1 = child(div_1);
      MarkdownCode(node_1, {
        get message() {
          return placeholder();
        },
        get latex_delimiters() {
          return latex_delimiters();
        }
      });
      reset(div_1);
      append($$anchor2, div_1);
    };
    if_block(node, ($$render) => {
      if (placeholder() !== null) $$render(consequent);
    });
  }
  var node_2 = sibling(node, 2);
  {
    var consequent_14 = ($$anchor2) => {
      var div_2 = root_2$1();
      each(div_2, 5, examples, index, ($$anchor3, example, i) => {
        var button = root_3();
        var div_3 = child(button);
        var node_3 = child(div_3);
        {
          var consequent_1 = ($$anchor4) => {
            var div_4 = root_4();
            var node_4 = child(div_4);
            Image(node_4, {
              class: "example-image",
              get src() {
                return get(example), untrack(() => get(example).icon.url);
              },
              alt: "Example icon"
            });
            reset(div_4);
            append($$anchor4, div_4);
          };
          var alternate_8 = ($$anchor4) => {
            var fragment = comment();
            var node_5 = first_child(fragment);
            {
              var consequent_2 = ($$anchor5) => {
                var div_5 = root_6$1();
                append($$anchor5, div_5);
              };
              var alternate_7 = ($$anchor5) => {
                var fragment_1 = comment();
                var node_6 = first_child(fragment_1);
                {
                  var consequent_13 = ($$anchor6) => {
                    var fragment_2 = comment();
                    var node_7 = first_child(fragment_2);
                    {
                      var consequent_9 = ($$anchor7) => {
                        var div_6 = root_9();
                        var node_8 = child(div_6);
                        each(
                          node_8,
                          1,
                          () => (get(example), untrack(() => get(example).files.slice(0, 4))),
                          index,
                          ($$anchor8, file, i2, $$array) => {
                            var fragment_3 = comment();
                            var node_9 = first_child(fragment_3);
                            {
                              var consequent_4 = ($$anchor9) => {
                                var div_7 = root_11$1();
                                var node_10 = child(div_7);
                                {
                                  let $0 = derived_safe_equal(() => (get(file), untrack(() => get(file).orig_name || `Example image ${i2 + 1}`)));
                                  Image(node_10, {
                                    class: "example-image",
                                    get src() {
                                      return get(file), untrack(() => get(file).url);
                                    },
                                    get alt() {
                                      return get($0);
                                    }
                                  });
                                }
                                var node_11 = sibling(node_10, 2);
                                {
                                  var consequent_3 = ($$anchor10) => {
                                    var div_8 = root_12();
                                    var text2 = child(div_8);
                                    reset(div_8);
                                    template_effect(() => {
                                      set_attribute(div_8, "aria-label", (get(example), untrack(() => `${get(example).files.length - 4} more files`)));
                                      set_text(text2, `+${(get(example), untrack(() => get(example).files.length - 4)) ?? ""}`);
                                    });
                                    append($$anchor10, div_8);
                                  };
                                  if_block(node_11, ($$render) => {
                                    if (get(example), untrack(() => i2 === 3 && get(example).files.length > 4)) $$render(consequent_3);
                                  });
                                }
                                reset(div_7);
                                append($$anchor9, div_7);
                              };
                              var alternate_2 = ($$anchor9) => {
                                var fragment_4 = comment();
                                var node_12 = first_child(fragment_4);
                                {
                                  var consequent_6 = ($$anchor10) => {
                                    var div_9 = root_14();
                                    var video = child(div_9);
                                    var node_13 = sibling(video, 2);
                                    {
                                      var consequent_5 = ($$anchor11) => {
                                        var div_10 = root_15();
                                        var text_1 = child(div_10);
                                        reset(div_10);
                                        template_effect(() => {
                                          set_attribute(div_10, "aria-label", (get(example), untrack(() => `${get(example).files.length - 4} more files`)));
                                          set_text(text_1, `+${(get(example), untrack(() => get(example).files.length - 4)) ?? ""}`);
                                        });
                                        append($$anchor11, div_10);
                                      };
                                      if_block(node_13, ($$render) => {
                                        if (get(example), untrack(() => i2 === 3 && get(example).files.length > 4)) $$render(consequent_5);
                                      });
                                    }
                                    reset(div_9);
                                    template_effect(() => set_attribute(video, "src", (get(file), untrack(() => get(file).url))));
                                    append($$anchor10, div_9);
                                  };
                                  var alternate_1 = ($$anchor10) => {
                                    var div_11 = root_16();
                                    var node_14 = child(div_11);
                                    {
                                      var consequent_7 = ($$anchor11) => {
                                        Music($$anchor11);
                                      };
                                      var alternate = ($$anchor11) => {
                                        File($$anchor11);
                                      };
                                      if_block(node_14, ($$render) => {
                                        if (get(file), untrack(() => get(file).mime_type?.includes("audio"))) $$render(consequent_7);
                                        else $$render(alternate, false);
                                      });
                                    }
                                    reset(div_11);
                                    template_effect(() => set_attribute(div_11, "aria-label", (get(file), untrack(() => `File: ${get(file).orig_name}`))));
                                    append($$anchor10, div_11);
                                  };
                                  if_block(
                                    node_12,
                                    ($$render) => {
                                      if (get(file), untrack(() => get(file).mime_type?.includes("video"))) $$render(consequent_6);
                                      else $$render(alternate_1, false);
                                    },
                                    true
                                  );
                                }
                                append($$anchor9, fragment_4);
                              };
                              if_block(node_9, ($$render) => {
                                if (get(file), untrack(() => get(file).mime_type?.includes("image"))) $$render(consequent_4);
                                else $$render(alternate_2, false);
                              });
                            }
                            append($$anchor8, fragment_3);
                          }
                        );
                        var node_15 = sibling(node_8, 2);
                        {
                          var consequent_8 = ($$anchor8) => {
                            var div_12 = root_19();
                            var div_13 = child(div_12);
                            var text_2 = child(div_13);
                            reset(div_13);
                            reset(div_12);
                            template_effect(() => {
                              set_attribute(div_13, "aria-label", (get(example), untrack(() => `${get(example).files.length - 4} more files`)));
                              set_text(text_2, `+${(get(example), untrack(() => get(example).files.length - 4)) ?? ""}`);
                            });
                            append($$anchor8, div_12);
                          };
                          if_block(node_15, ($$render) => {
                            if (get(example), untrack(() => get(example).files.length > 4)) $$render(consequent_8);
                          });
                        }
                        reset(div_6);
                        append($$anchor7, div_6);
                      };
                      var alternate_6 = ($$anchor7) => {
                        var fragment_7 = comment();
                        var node_16 = first_child(fragment_7);
                        {
                          var consequent_10 = ($$anchor8) => {
                            var div_14 = root_21();
                            var node_17 = child(div_14);
                            {
                              let $0 = derived_safe_equal(() => (get(example), untrack(() => get(example).files[0].orig_name || "Example image")));
                              Image(node_17, {
                                class: "example-image",
                                get src() {
                                  return get(example), untrack(() => get(example).files[0].url);
                                },
                                get alt() {
                                  return get($0);
                                }
                              });
                            }
                            reset(div_14);
                            append($$anchor8, div_14);
                          };
                          var alternate_5 = ($$anchor8) => {
                            var fragment_8 = comment();
                            var node_18 = first_child(fragment_8);
                            {
                              var consequent_11 = ($$anchor9) => {
                                var div_15 = root_23();
                                var video_1 = child(div_15);
                                reset(div_15);
                                template_effect(() => set_attribute(video_1, "src", (get(example), untrack(() => get(example).files[0].url))));
                                append($$anchor9, div_15);
                              };
                              var alternate_4 = ($$anchor9) => {
                                var fragment_9 = comment();
                                var node_19 = first_child(fragment_9);
                                {
                                  var consequent_12 = ($$anchor10) => {
                                    var div_16 = root_25();
                                    var node_20 = child(div_16);
                                    Music(node_20);
                                    reset(div_16);
                                    template_effect(() => set_attribute(div_16, "aria-label", (get(example), untrack(() => `File: ${get(example).files[0].orig_name}`))));
                                    append($$anchor10, div_16);
                                  };
                                  var alternate_3 = ($$anchor10) => {
                                    var div_17 = root_26();
                                    var node_21 = child(div_17);
                                    File(node_21);
                                    reset(div_17);
                                    template_effect(() => set_attribute(div_17, "aria-label", (get(example), untrack(() => `File: ${get(example).files[0].orig_name}`))));
                                    append($$anchor10, div_17);
                                  };
                                  if_block(
                                    node_19,
                                    ($$render) => {
                                      if (get(example), untrack(() => get(example).files[0].mime_type?.includes("audio"))) $$render(consequent_12);
                                      else $$render(alternate_3, false);
                                    },
                                    true
                                  );
                                }
                                append($$anchor9, fragment_9);
                              };
                              if_block(
                                node_18,
                                ($$render) => {
                                  if (get(example), untrack(() => get(example).files[0].mime_type?.includes("video"))) $$render(consequent_11);
                                  else $$render(alternate_4, false);
                                },
                                true
                              );
                            }
                            append($$anchor8, fragment_8);
                          };
                          if_block(
                            node_16,
                            ($$render) => {
                              if (get(example), untrack(() => get(example).files[0].mime_type?.includes("image"))) $$render(consequent_10);
                              else $$render(alternate_5, false);
                            },
                            true
                          );
                        }
                        append($$anchor7, fragment_7);
                      };
                      if_block(node_7, ($$render) => {
                        if (get(example), untrack(() => get(example).files.length > 1)) $$render(consequent_9);
                        else $$render(alternate_6, false);
                      });
                    }
                    append($$anchor6, fragment_2);
                  };
                  if_block(
                    node_6,
                    ($$render) => {
                      if (get(example), untrack(() => get(example).files !== void 0 && get(example).files.length > 0)) $$render(consequent_13);
                    },
                    true
                  );
                }
                append($$anchor5, fragment_1);
              };
              if_block(
                node_5,
                ($$render) => {
                  if (get(example), untrack(() => get(example)?.icon?.mime_type === "text")) $$render(consequent_2);
                  else $$render(alternate_7, false);
                },
                true
              );
            }
            append($$anchor4, fragment);
          };
          if_block(node_3, ($$render) => {
            if (get(example), untrack(() => get(example)?.icon?.url)) $$render(consequent_1);
            else $$render(alternate_8, false);
          });
        }
        var div_18 = sibling(node_3, 2);
        var span = child(div_18);
        var text_3 = child(span, true);
        reset(span);
        reset(div_18);
        reset(div_3);
        reset(button);
        template_effect(() => {
          set_attribute(button, "aria-label", (get(example), untrack(() => `Select example ${i + 1}: ${get(example).display_text || get(example).text}`)));
          set_text(text_3, (get(example), untrack(() => get(example).display_text || get(example).text)));
        });
        event("click", button, () => handle_example_select(i, typeof get(example) === "string" ? { text: get(example) } : get(example)));
        append($$anchor3, button);
      });
      reset(div_2);
      append($$anchor2, div_2);
    };
    if_block(node_2, ($$render) => {
      if (examples() !== null) $$render(consequent_14);
    });
  }
  reset(div);
  append($$anchor, div);
  pop();
}
function CopyAll($$anchor, $$props) {
  push($$props, false);
  let copied = mutable_source(false);
  let value = prop($$props, "value", 8);
  let watermark = prop($$props, "watermark", 8, null);
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
  const copy_conversation = () => {
    if (value()) {
      const conversation_value = value().map((message) => {
        if (message.type === "text") {
          return `${message.role}: ${message.content}`;
        }
        return `${message.role}: ${message.content.value.url}`;
      }).join("\n\n");
      const text_to_copy = watermark() ? `${conversation_value}

${watermark()}` : conversation_value;
      navigator.clipboard.writeText(text_to_copy).catch((err) => {
        console.error("Failed to copy conversation: ", err);
      });
    }
  };
  async function handle_copy() {
    if ("clipboard" in navigator) {
      copy_conversation();
      copy_feedback();
    }
  }
  onDestroy(() => {
    if (timer) clearTimeout(timer);
  });
  init();
  {
    let $0 = derived_safe_equal(() => get(copied) ? Check : Copy);
    let $1 = derived_safe_equal(() => get(copied) ? "Copied conversation" : "Copy conversation");
    IconButton($$anchor, {
      get Icon() {
        return get($0);
      },
      get label() {
        return get($1);
      },
      $$events: { click: handle_copy }
    });
  }
  pop();
}
var root_2 = from_html(`<!> <!> <!>`, 1);
var root_6 = from_html(`<!> <!>`, 1);
var root_11 = from_html(`<button class="option svelte-kpz1"> </button>`);
var root_10 = from_html(`<div class="options svelte-kpz1"></div>`);
var root_5 = from_html(`<div class="message-wrap svelte-kpz1"><!> <!></div>`);
var root_13 = from_html(`<div class="scroll-down-button-container svelte-kpz1"><!></div>`);
var root = from_html(`<!> <div role="log" aria-label="chatbot conversation" aria-live="polite"><!></div> <!>`, 1);
function ChatBot($$anchor, $$props) {
  push($$props, false);
  const component_names = mutable_source();
  const groupedMessages = mutable_source();
  const options = mutable_source();
  let value = prop($$props, "value", 24, () => []);
  let old_value = mutable_source(null);
  let _fetch = prop($$props, "_fetch", 8);
  let load_component = prop($$props, "load_component", 8);
  let allow_file_downloads = prop($$props, "allow_file_downloads", 8);
  let display_consecutive_in_same_bubble = prop($$props, "display_consecutive_in_same_bubble", 8);
  let _components = mutable_source({});
  const is_browser = typeof window !== "undefined";
  async function update_components() {
    set(_components, await load_components(get_components_from_messages(value()), get(_components), load_component()));
  }
  let latex_delimiters = prop($$props, "latex_delimiters", 8);
  let pending_message = prop($$props, "pending_message", 8, false);
  let generating = prop($$props, "generating", 8, false);
  let selectable = prop($$props, "selectable", 8, false);
  let likeable = prop($$props, "likeable", 8, false);
  let feedback_options = prop($$props, "feedback_options", 8);
  let feedback_value = prop($$props, "feedback_value", 8, null);
  let editable = prop($$props, "editable", 8, null);
  let show_share_button = prop($$props, "show_share_button", 8, false);
  let show_copy_all_button = prop($$props, "show_copy_all_button", 8, false);
  let rtl = prop($$props, "rtl", 8, false);
  let show_copy_button = prop($$props, "show_copy_button", 8, false);
  let avatar_images = prop($$props, "avatar_images", 24, () => [null, null]);
  let sanitize_html = prop($$props, "sanitize_html", 8, true);
  let render_markdown = prop($$props, "render_markdown", 8, true);
  let line_breaks = prop($$props, "line_breaks", 8, true);
  let autoscroll = prop($$props, "autoscroll", 8, true);
  let theme_mode = prop($$props, "theme_mode", 8);
  let i18n = prop($$props, "i18n", 8);
  let layout = prop($$props, "layout", 8, "bubble");
  let placeholder = prop($$props, "placeholder", 8, null);
  let upload = prop($$props, "upload", 8);
  let examples = prop($$props, "examples", 8, null);
  let _retryable = prop($$props, "_retryable", 8, false);
  let _undoable = prop($$props, "_undoable", 8, false);
  let like_user_message = prop($$props, "like_user_message", 8, false);
  let allow_tags = prop($$props, "allow_tags", 8, false);
  let watermark = prop($$props, "watermark", 8, null);
  let show_progress = prop($$props, "show_progress", 8, "full");
  let target = mutable_source(null);
  let edit_index = mutable_source(null);
  let edit_messages = mutable_source([]);
  onMount(() => {
    set(target, document.querySelector("div.gradio-container"));
  });
  let div = mutable_source();
  let show_scroll_button = mutable_source(false);
  const dispatch = createEventDispatcher();
  function is_at_bottom() {
    return get(div) && get(div).offsetHeight + get(div).scrollTop > get(div).scrollHeight - 100;
  }
  function scroll_to_bottom() {
    if (!get(div)) return;
    get(div).scrollTo(0, get(div).scrollHeight);
    set(show_scroll_button, false);
  }
  async function scroll_on_value_update() {
    if (!autoscroll()) return;
    if (is_at_bottom()) {
      await tick();
      await new Promise((resolve) => setTimeout(resolve, 300));
      scroll_to_bottom();
    }
  }
  onMount(() => {
    if (autoscroll()) {
      scroll_to_bottom();
    }
    scroll_on_value_update();
  });
  onMount(() => {
    function handle_scroll() {
      if (is_at_bottom()) {
        set(show_scroll_button, false);
      } else {
        set(show_scroll_button, true);
      }
    }
    get(div)?.addEventListener("scroll", handle_scroll);
    return () => {
      get(div)?.removeEventListener("scroll", handle_scroll);
    };
  });
  function handle_action(i, message, selected) {
    if (selected === "undo" || selected === "retry") {
      const val_ = value();
      let last_index = val_.length - 1;
      while (val_[last_index].role === "assistant") {
        last_index--;
      }
      dispatch(selected, {
        index: val_[last_index].index,
        value: val_[last_index].content
      });
    } else if (selected == "edit") {
      set(edit_index, i);
      get(edit_messages).push(message.content);
    } else if (selected == "edit_cancel") {
      set(edit_index, null);
    } else if (selected == "edit_submit") {
      set(edit_index, null);
      dispatch("edit", {
        index: message.index,
        _dispatch_value: [{ type: "text", text: get(edit_messages)[i].slice() }],
        value: get(edit_messages)[i].slice(),
        previous_value: message.content
      });
    } else {
      let feedback = selected === "Like" ? true : selected === "Dislike" ? false : selected || "";
      if (!get(groupedMessages)) return;
      const message_group = get(groupedMessages)[i];
      const [first] = [message_group[0], message_group[message_group.length - 1]];
      dispatch("like", {
        index: first.index,
        value: message_group.map((m) => m.content),
        liked: feedback
      });
    }
  }
  function get_last_bot_options() {
    if (!value() || !get(groupedMessages) || get(groupedMessages).length === 0) return void 0;
    const last_group = get(groupedMessages)[get(groupedMessages).length - 1];
    if (last_group[0].role !== "assistant") return void 0;
    return last_group[last_group.length - 1].options;
  }
  legacy_pre_effect(() => deep_read_state(value()), () => {
    set(component_names, get_components_from_messages(value()).sort().join(", "));
  });
  legacy_pre_effect(() => get(component_names), () => {
    get(component_names), update_components();
  });
  legacy_pre_effect(
    () => (deep_read_state(value()), deep_read_state(pending_message()), get(_components)),
    () => {
      if (value() || pending_message() || get(_components)) {
        scroll_on_value_update();
      }
    }
  );
  legacy_pre_effect(() => (deep_read_state(value()), get(old_value)), () => {
    if (!dequal(value(), get(old_value))) {
      set(old_value, value());
      dispatch("change");
    }
  });
  legacy_pre_effect(
    () => (deep_read_state(value()), deep_read_state(display_consecutive_in_same_bubble())),
    () => {
      set(groupedMessages, value() && group_messages(value(), display_consecutive_in_same_bubble()));
    }
  );
  legacy_pre_effect(() => deep_read_state(value()), () => {
    set(options, value() && get_last_bot_options());
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root();
  var node = first_child(fragment);
  {
    var consequent_2 = ($$anchor2) => {
      IconButtonWrapper($$anchor2, {
        children: ($$anchor3, $$slotProps) => {
          var fragment_2 = root_2();
          var node_1 = first_child(fragment_2);
          {
            var consequent = ($$anchor4) => {
              IconButton($$anchor4, {
                get Icon() {
                  return Community;
                },
                $$events: {
                  click: async () => {
                    try {
                      const formatted = await format_chat_for_sharing(value());
                      dispatch("share", { description: formatted });
                    } catch (e) {
                      console.error(e);
                      let message = e instanceof ShareError ? e.message : "Share failed.";
                      dispatch("error", message);
                    }
                  }
                }
              });
            };
            if_block(node_1, ($$render) => {
              if (show_share_button()) $$render(consequent);
            });
          }
          var node_2 = sibling(node_1, 2);
          {
            let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("chatbot.clear"))));
            IconButton(node_2, {
              get Icon() {
                return Trash;
              },
              get label() {
                return get($0);
              },
              $$events: { click: () => dispatch("clear") }
            });
          }
          var node_3 = sibling(node_2, 2);
          {
            var consequent_1 = ($$anchor4) => {
              CopyAll($$anchor4, {
                get value() {
                  return value();
                },
                get watermark() {
                  return watermark();
                }
              });
            };
            if_block(node_3, ($$render) => {
              if (show_copy_all_button()) $$render(consequent_1);
            });
          }
          append($$anchor3, fragment_2);
        },
        $$slots: { default: true }
      });
    };
    if_block(node, ($$render) => {
      if (deep_read_state(value()), untrack(() => value() !== null && value().length > 0)) $$render(consequent_2);
    });
  }
  var div_1 = sibling(node, 2);
  var node_4 = child(div_1);
  {
    var consequent_6 = ($$anchor2) => {
      var div_2 = root_5();
      var node_5 = child(div_2);
      each(node_5, 1, () => get(groupedMessages), index, ($$anchor3, messages, i) => {
        const role = derived_safe_equal(() => (get(messages), untrack(() => get(messages)[0].role === "user" ? "user" : "bot")));
        const avatar_img = derived_safe_equal(() => (deep_read_state(avatar_images()), deep_read_state(get(role)), untrack(() => avatar_images()[get(role) === "user" ? 0 : 1])));
        const opposite_avatar_img = derived_safe_equal(() => (deep_read_state(avatar_images()), deep_read_state(get(role)), untrack(() => avatar_images()[get(role) === "user" ? 0 : 1])));
        const feedback_index = derived_safe_equal(() => (get(groupedMessages), untrack(() => get(groupedMessages).slice(0, i).filter((m) => m[0].role === "assistant").length)));
        const current_feedback = derived_safe_equal(() => (deep_read_state(get(role)), deep_read_state(feedback_value()), deep_read_state(get(feedback_index)), untrack(() => get(role) === "bot" && feedback_value() && feedback_value()[get(feedback_index)] ? feedback_value()[get(feedback_index)] : null)));
        var fragment_5 = root_6();
        var node_6 = first_child(fragment_5);
        {
          let $0 = derived_safe_equal(() => get(role) === "user" ? likeable() && like_user_message() : likeable());
          let $1 = derived_safe_equal(() => (deep_read_state(_retryable()), deep_read_state(is_last_bot_message), get(messages), deep_read_state(value()), untrack(() => _retryable() && is_last_bot_message(get(messages), value()))));
          let $2 = derived_safe_equal(() => (deep_read_state(_undoable()), deep_read_state(is_last_bot_message), get(messages), deep_read_state(value()), untrack(() => _undoable() && is_last_bot_message(get(messages), value()))));
          let $3 = derived_safe_equal(() => (deep_read_state(editable()), deep_read_state(get(role)), get(messages), untrack(() => editable() === "all" || editable() == "user" && get(role) === "user" && get(messages).length > 0 && get(messages)[get(messages).length - 1].type == "text")));
          let $4 = derived_safe_equal(() => get(edit_index) === i);
          let $5 = derived_safe_equal(() => is_browser ? scroll : () => {
          });
          Message(node_6, {
            get messages() {
              return get(messages);
            },
            get display_consecutive_in_same_bubble() {
              return display_consecutive_in_same_bubble();
            },
            get opposite_avatar_img() {
              return get(opposite_avatar_img);
            },
            get avatar_img() {
              return get(avatar_img);
            },
            get role() {
              return get(role);
            },
            get layout() {
              return layout();
            },
            get dispatch() {
              return dispatch;
            },
            get i18n() {
              return i18n();
            },
            get _fetch() {
              return _fetch();
            },
            get line_breaks() {
              return line_breaks();
            },
            get theme_mode() {
              return theme_mode();
            },
            get target() {
              return get(target);
            },
            get upload() {
              return upload();
            },
            get selectable() {
              return selectable();
            },
            get sanitize_html() {
              return sanitize_html();
            },
            get render_markdown() {
              return render_markdown();
            },
            get rtl() {
              return rtl();
            },
            i,
            get value() {
              return value();
            },
            get latex_delimiters() {
              return latex_delimiters();
            },
            get _components() {
              return get(_components);
            },
            get generating() {
              return generating();
            },
            get feedback_options() {
              return feedback_options();
            },
            get current_feedback() {
              return get(current_feedback);
            },
            get allow_tags() {
              return allow_tags();
            },
            get watermark() {
              return watermark();
            },
            get show_like() {
              return get($0);
            },
            get show_retry() {
              return get($1);
            },
            get show_undo() {
              return get($2);
            },
            get show_edit() {
              return get($3);
            },
            get in_edit_mode() {
              return get($4);
            },
            get show_copy_button() {
              return show_copy_button();
            },
            handle_action: (selected) => {
              if (selected == "edit") {
                get(edit_messages).splice(0, get(edit_messages).length);
              }
              if (selected === "edit" || selected === "edit_submit") {
                get(messages).forEach((msg, index2) => {
                  handle_action(selected === "edit" ? i : index2, msg, selected);
                });
              } else {
                handle_action(i, get(messages)[0], selected);
              }
            },
            get scroll() {
              return get($5);
            },
            get allow_file_downloads() {
              return allow_file_downloads();
            },
            get edit_messages() {
              return get(edit_messages);
            },
            set edit_messages($$value) {
              set(edit_messages, $$value);
            },
            $$events: { copy: (e) => dispatch("copy", e.detail) },
            $$legacy: true
          });
        }
        var node_7 = sibling(node_6, 2);
        {
          var consequent_3 = ($$anchor4) => {
            Pending($$anchor4, {
              get layout() {
                return layout();
              },
              get avatar_images() {
                return avatar_images();
              }
            });
          };
          if_block(node_7, ($$render) => {
            if (deep_read_state(show_progress()), deep_read_state(generating()), get(messages), untrack(() => show_progress() !== "hidden" && generating() && get(messages)[get(messages).length - 1].role === "assistant" && get(messages)[get(messages).length - 1].metadata?.status === "done")) $$render(consequent_3);
          });
        }
        append($$anchor3, fragment_5);
      });
      var node_8 = sibling(node_5, 2);
      {
        var consequent_4 = ($$anchor3) => {
          Pending($$anchor3, {
            get layout() {
              return layout();
            },
            get avatar_images() {
              return avatar_images();
            }
          });
        };
        var alternate = ($$anchor3) => {
          var fragment_8 = comment();
          var node_9 = first_child(fragment_8);
          {
            var consequent_5 = ($$anchor4) => {
              var div_3 = root_10();
              each(div_3, 5, () => get(options), index, ($$anchor5, option, index2) => {
                var button = root_11();
                var text2 = child(button, true);
                reset(button);
                template_effect(() => set_text(text2, (get(option), untrack(() => get(option).label || get(option).value))));
                event("click", button, () => dispatch("option_select", { index: index2, value: get(option).value }));
                append($$anchor5, button);
              });
              reset(div_3);
              append($$anchor4, div_3);
            };
            if_block(
              node_9,
              ($$render) => {
                if (get(options)) $$render(consequent_5);
              },
              true
            );
          }
          append($$anchor3, fragment_8);
        };
        if_block(node_8, ($$render) => {
          if (show_progress() !== "hidden" && pending_message()) $$render(consequent_4);
          else $$render(alternate, false);
        });
      }
      reset(div_2);
      action(div_2, ($$node) => copy?.($$node));
      append($$anchor2, div_2);
    };
    var alternate_1 = ($$anchor2) => {
      Examples($$anchor2, {
        get examples() {
          return examples();
        },
        get placeholder() {
          return placeholder();
        },
        get latex_delimiters() {
          return latex_delimiters();
        },
        $$events: { example_select: (e) => dispatch("example_select", e.detail) }
      });
    };
    if_block(node_4, ($$render) => {
      if (deep_read_state(value()), get(groupedMessages), untrack(() => value() !== null && value().length > 0 && get(groupedMessages) !== null)) $$render(consequent_6);
      else $$render(alternate_1, false);
    });
  }
  reset(div_1);
  bind_this(div_1, ($$value) => set(div, $$value), () => get(div));
  var node_10 = sibling(div_1, 2);
  {
    var consequent_7 = ($$anchor2) => {
      var div_4 = root_13();
      var node_11 = child(div_4);
      IconButton(node_11, {
        get Icon() {
          return ScrollDownArrow;
        },
        label: "Scroll down",
        size: "large",
        $$events: { click: scroll_to_bottom }
      });
      reset(div_4);
      append($$anchor2, div_4);
    };
    if_block(node_10, ($$render) => {
      if (get(show_scroll_button)) $$render(consequent_7);
    });
  }
  template_effect(() => set_class(div_1, 1, clsx(layout() === "bubble" ? "bubble-wrap" : "panel-wrap"), "svelte-kpz1"));
  append($$anchor, fragment);
  pop();
}
var root_1 = from_html(`<!> <div class="wrapper svelte-1wizwbi"><!> <!></div>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let _value = user_derived(() => normalise_messages(gradio.props.value, gradio.shared.root));
  Block($$anchor, {
    get elem_id() {
      return gradio.shared.elem_id;
    },
    get elem_classes() {
      return gradio.shared.elem_classes;
    },
    get visible() {
      return gradio.shared.visible;
    },
    padding: false,
    get scale() {
      return gradio.shared.scale;
    },
    get min_width() {
      return gradio.shared.min_width;
    },
    get height() {
      return gradio.props.height;
    },
    get resizable() {
      return gradio.props.resizable;
    },
    get min_height() {
      return gradio.props.min_height;
    },
    get max_height() {
      return gradio.props.max_height;
    },
    allow_overflow: true,
    flex: true,
    overflow_behavior: "auto",
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          {
            let $0 = user_derived(() => gradio.shared.loading_status.show_progress === "hidden" ? "hidden" : "minimal");
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
                get show_progress() {
                  return get($0);
                },
                $$events: {
                  clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
                }
              }
            ));
          }
        };
        if_block(node, ($$render) => {
          if (gradio.shared.loading_status) $$render(consequent);
        });
      }
      var div = sibling(node, 2);
      var node_1 = child(div);
      {
        var consequent_1 = ($$anchor3) => {
          {
            let $0 = user_derived(() => gradio.shared.label || "Chatbot");
            BlockLabel($$anchor3, {
              get show_label() {
                return gradio.shared.show_label;
              },
              get Icon() {
                return Chat;
              },
              float: true,
              get label() {
                return get($0);
              }
            });
          }
        };
        if_block(node_1, ($$render) => {
          if (gradio.shared.show_label) $$render(consequent_1);
        });
      }
      var node_2 = sibling(node_1, 2);
      {
        let $0 = user_derived(() => (gradio.props.buttons ?? ["share"]).includes("share"));
        let $1 = user_derived(() => (gradio.props.buttons ?? ["copy_all"]).includes("copy_all"));
        let $2 = user_derived(() => gradio.shared.loading_status?.status === "pending");
        let $3 = user_derived(() => gradio.shared.loading_status?.status === "generating");
        let $4 = user_derived(() => (gradio.props.buttons ?? ["copy"]).includes("copy"));
        let $5 = user_derived(() => gradio.shared.loading_status?.show_progress || "full");
        ChatBot(node_2, {
          get i18n() {
            return gradio.i18n;
          },
          get selectable() {
            return gradio.props._selectable;
          },
          get likeable() {
            return gradio.props.likeable;
          },
          get feedback_options() {
            return gradio.props.feedback_options;
          },
          get feedback_value() {
            return gradio.props.feedback_value;
          },
          get show_share_button() {
            return get($0);
          },
          get show_copy_all_button() {
            return get($1);
          },
          get value() {
            return get(_value);
          },
          get latex_delimiters() {
            return gradio.props.latex_delimiters;
          },
          get display_consecutive_in_same_bubble() {
            return gradio.props.group_consecutive_messages;
          },
          get render_markdown() {
            return gradio.props.render_markdown;
          },
          get theme_mode() {
            return gradio.shared.theme_mode;
          },
          get editable() {
            return gradio.props.editable;
          },
          get pending_message() {
            return get($2);
          },
          get generating() {
            return get($3);
          },
          get rtl() {
            return gradio.props.rtl;
          },
          get show_copy_button() {
            return get($4);
          },
          get like_user_message() {
            return gradio.props.like_user_message;
          },
          get show_progress() {
            return get($5);
          },
          get avatar_images() {
            return gradio.props.avatar_images;
          },
          get sanitize_html() {
            return gradio.props.sanitize_html;
          },
          get line_breaks() {
            return gradio.props.line_breaks;
          },
          get autoscroll() {
            return gradio.shared.autoscroll;
          },
          get layout() {
            return gradio.props.layout;
          },
          get placeholder() {
            return gradio.props.placeholder;
          },
          get examples() {
            return gradio.props.examples;
          },
          get _retryable() {
            return gradio.props._retryable;
          },
          get _undoable() {
            return gradio.props._undoable;
          },
          upload: (...args) => gradio.shared.client.upload(...args),
          _fetch: (...args) => gradio.shared.client.fetch(...args),
          get load_component() {
            return gradio.shared.load_component;
          },
          get allow_file_downloads() {
            return gradio.props.allow_file_downloads;
          },
          get allow_tags() {
            return gradio.props.allow_tags;
          },
          get watermark() {
            return gradio.props.watermark;
          },
          $$events: {
            change: () => (gradio.props.value = gradio.props.value, gradio.dispatch("change", gradio.props.value)),
            select: (e) => gradio.dispatch("select", e.detail),
            like: (e) => gradio.dispatch("like", e.detail),
            share: (e) => gradio.dispatch("share", e.detail),
            error: (e) => gradio.dispatch("error", e.detail),
            example_select: (e) => gradio.dispatch("example_select", e.detail),
            option_select: (e) => gradio.dispatch("option_select", e.detail),
            retry: (e) => gradio.dispatch("retry", e.detail),
            undo: (e) => gradio.dispatch("undo", e.detail),
            clear: () => {
              gradio.props.value = [];
              gradio.dispatch("clear");
            },
            copy: (e) => gradio.dispatch("copy", e.detail),
            edit: (e) => {
              if (gradio.props.value === null || gradio.props.value.length === 0) return;
              gradio.props.value[e.detail.index].content = [{ text: e.detail.value, type: "text" }];
              gradio.dispatch("edit", e.detail);
            }
          }
        });
      }
      reset(div);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  ChatBot as BaseChatBot,
  Index as default
};
//# sourceMappingURL=BI728dH8.js.map
