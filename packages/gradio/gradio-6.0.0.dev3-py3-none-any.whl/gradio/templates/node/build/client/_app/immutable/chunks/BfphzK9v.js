import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, c as from_html, d as child, s as sibling, r as reset, t as template_effect, z as event, b as append, o as pop, g as set_text, J as state, L as proxy, M as user_effect, j as set, A as user_derived, k as get, I as onMount, E as next, F as text, $ as $window, D as comment, v as first_child, V as remove_textarea_child, K as tick } from "./DEzry6cj.js";
import { p as prop, i as if_block, b as bind_this, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { s as set_attribute, z as BlockTitle, I as IconButtonWrapper, b as IconButton, H as Check, J as Copy, t as each, v as index, a as set_class, Y as transition, Z as fade, p as set_style, q as bind_value, _ as Send, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { P as Plus } from "./CCzZQFML.js";
import { T as Trash } from "./D9zAf8BK.js";
import { b as Dropdown, D as DropdownOptions } from "./CxkJXoI9.js";
/* empty css         */
import { i as init } from "./DB0xzveP.js";
import { default as default2 } from "./SosDKSfR.js";
var root$1 = from_html(`<div class="s s--slider svelte-1io85vl" style="font-size:var(--font-size-sm)px"><button role="switch" class="svelte-1io85vl"></button> <span> </span></div>`);
function Switch($$anchor, $$props) {
  push($$props, false);
  let label = prop($$props, "label", 8);
  let checked = prop($$props, "checked", 12, false);
  let disabled = prop($$props, "disabled", 8, false);
  const dispatch = createEventDispatcher();
  function handleClick(event2) {
    const target = event2.target;
    const state2 = target.getAttribute("aria-checked");
    checked(state2 === "true" ? false : true);
    dispatch("click", { checked: checked() });
  }
  init();
  var div = root$1();
  var button = child(div);
  var span = sibling(button, 2);
  var text2 = child(span, true);
  reset(span);
  reset(div);
  template_effect(() => {
    set_attribute(button, "aria-checked", checked());
    button.disabled = disabled();
    set_text(text2, label());
  });
  event("click", button, handleClick);
  append($$anchor, div);
  pop();
}
var root_4 = from_html(`<div><!></div>`);
var root_6 = from_html(`<div class="loading-overlay svelte-1p54cvv"><div class="loading-spinner svelte-1p54cvv"></div> <div class="loading-text svelte-1p54cvv">Converting to dialogue format...</div></div>`);
var root_8 = from_html(`<textarea rows="1" readonly="" class="svelte-1p54cvv"></textarea>`);
var root_10 = from_html(`<div id="tag-menu" class="tag-menu svelte-1p54cvv"><!></div>`);
var root_11 = from_html(`<div><button class="add-button svelte-1p54cvv" aria-label="Add new line"><!></button></div>`);
var root_7 = from_html(`<div class="dialogue-line svelte-1p54cvv"><div class="speaker-column svelte-1p54cvv" role="button" tabindex="0"><!></div> <div class="text-column svelte-1p54cvv"><div class="input-container svelte-1p54cvv"><textarea rows="1" class="svelte-1p54cvv"></textarea> <!></div></div> <!> <div><button class="delete-button svelte-1p54cvv" aria-label="Remove current line"><!></button></div></div>`);
var root_5 = from_html(`<div><!> <!></div>`);
var root_14 = from_html(`<div class="loading-overlay svelte-1p54cvv"><div class="loading-spinner svelte-1p54cvv"></div> <div class="loading-text svelte-1p54cvv">Converting to plain text...</div></div>`);
var root_15 = from_html(`<div id="tag-menu" class="tag-menu-plain-text svelte-1p54cvv"><!></div>`);
var root_13 = from_html(`<div><!> <textarea data-testid="textbox" class="svelte-1p54cvv"></textarea> <!></div>`);
var root_16 = from_html(`<div class="submit-container svelte-1p54cvv"><button class="submit-button svelte-1p54cvv"><!></button></div>`);
var root = from_html(`<label><!> <!> <!> <!> <!></label>`);
function Dialogue($$anchor, $$props) {
  push($$props, true);
  const gradio = $$props.gradio;
  let checked = user_derived(() => false);
  let disabled = user_derived(() => !gradio.shared.interactive);
  let dialogue_lines = state(proxy([]));
  user_effect(() => {
    if (gradio.props.value && gradio.props.value.length && typeof gradio.props.value !== "string") {
      set(dialogue_lines, [...gradio.props.value], true);
    } else if (gradio.props.value && typeof gradio.props.value !== "string") {
      set(
        dialogue_lines,
        [
          {
            speaker: `${gradio.props.speakers.length ? gradio.props.speakers[0] : ""}`,
            text: ""
          }
        ],
        true
      );
    } else if (typeof gradio.props.value === "string") {
      set(textbox_value, gradio.props.value, true);
      set(checked, true);
    }
  });
  let buttons = user_derived(() => gradio.props.buttons || ["copy"]);
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  let dialogue_container_element;
  let showTagMenu = state(false);
  let currentLineIndex = state(-1);
  let selectedOptionIndex = state(0);
  let filtered_tags = state(proxy([]));
  let input_elements = proxy([]);
  let textarea_element;
  let offset_from_top = state(0);
  let copied = state(false);
  let timer;
  let textbox_value = state("");
  let hoveredSpeaker = state(null);
  let is_unformatting = state(false);
  let is_formatting = state(false);
  const defaultColorNames = [
    "red",
    "green",
    "blue",
    "yellow",
    "purple",
    "teal",
    "orange",
    "cyan",
    "lime",
    "pink"
  ];
  const colorNameToHex = {
    red: "rgba(254, 202, 202, 0.7)",
    green: "rgba(209, 250, 229, 0.7)",
    blue: "rgba(219, 234, 254, 0.7)",
    yellow: "rgba(254, 243, 199, 0.7)",
    purple: "rgba(233, 213, 255, 0.7)",
    teal: "rgba(204, 251, 241, 0.7)",
    orange: "rgba(254, 215, 170, 0.7)",
    cyan: "rgba(207, 250, 254, 0.7)",
    lime: "rgba(217, 249, 157, 0.7)",
    pink: "rgba(252, 231, 243, 0.7)"
  };
  let speakerColors = user_derived(() => {
    let _speakerColors = {};
    if (gradio.props.color_map) {
      _speakerColors = { ...gradio.props.color_map };
    } else {
      _speakerColors = {};
      gradio.props.speakers.forEach((speaker, index2) => {
        const colorName = defaultColorNames[index2 % defaultColorNames.length];
        _speakerColors[speaker] = colorNameToHex[colorName];
      });
    }
    return _speakerColors;
  });
  function add_line(index2) {
    const newSpeaker = gradio.props.speakers.length > 0 ? gradio.props.speakers[0] : "";
    set(
      dialogue_lines,
      [
        ...get(dialogue_lines).slice(0, index2 + 1),
        { speaker: newSpeaker, text: "" },
        ...get(dialogue_lines).slice(index2 + 1)
      ],
      true
    );
    tick().then(() => {
      if (input_elements[index2 + 1]) {
        input_elements[index2 + 1].focus();
      }
    });
    gradio.props.value = [...get(dialogue_lines)];
  }
  function delete_line(index2) {
    set(
      dialogue_lines,
      [
        ...get(dialogue_lines).slice(0, index2),
        ...get(dialogue_lines).slice(index2 + 1)
      ],
      true
    );
    gradio.props.value = [...get(dialogue_lines)];
  }
  function update_line(index2, key, value) {
    get(dialogue_lines)[index2][key] = value;
    set(dialogue_lines, [...get(dialogue_lines)], true);
    gradio.props.value = [...get(dialogue_lines)];
  }
  function handle_input(event2, index2) {
    const input = event2.target || HTMLTextAreaElement;
    if (input && !input_elements[index2]) {
      input_elements[index2] = input;
    }
    const cursor_position = input.selectionStart || 0;
    const text2 = input.value;
    let show_menu = false;
    let position_reference_index = -1;
    if (text2[cursor_position - 1] === ":") {
      set(currentLineIndex, index2, true);
      position_reference_index = cursor_position;
      const search_text = get_tag_search_text(text2, cursor_position);
      set(filtered_tags, gradio.props.tags.filter((tag) => search_text === "" || tag.toLowerCase().includes(search_text.toLowerCase())), true);
      show_menu = get(filtered_tags).length > 0;
      set(selectedOptionIndex, 0);
    } else {
      const lastColonIndex = text2.lastIndexOf(":", cursor_position - 1);
      if (lastColonIndex >= 0 && !text2.substring(lastColonIndex + 1, cursor_position).includes(" ")) {
        set(currentLineIndex, index2, true);
        position_reference_index = lastColonIndex + 1;
        const searchText = text2.substring(lastColonIndex + 1, cursor_position);
        set(filtered_tags, gradio.props.tags.filter((tag) => searchText === "" || tag.toLowerCase().includes(searchText.toLowerCase())), true);
        show_menu = get(filtered_tags).length > 0;
        set(selectedOptionIndex, 0);
      }
    }
    if (show_menu && position_reference_index !== -1) {
      set(showTagMenu, true);
      const input_rect = input.getBoundingClientRect();
      if (dialogue_container_element) {
        const container_rect = dialogue_container_element.getBoundingClientRect();
        set(offset_from_top, container_rect.top + input_rect.height * (index2 + 1.5));
      }
    } else {
      set(showTagMenu, false);
    }
    gradio.dispatch("input");
  }
  function get_tag_search_text(text2, cursorPosition) {
    const lastColonIndex = text2.lastIndexOf(":", cursorPosition - 1);
    if (lastColonIndex >= 0) {
      return text2.substring(lastColonIndex + 1, cursorPosition);
    }
    return "";
  }
  async function insert_selected_tag() {
    const tag = get(filtered_tags)[get(selectedOptionIndex)];
    if (tag) {
      let text2;
      let currentInput;
      if (get(checked)) {
        currentInput = textarea_element;
        text2 = get(textbox_value);
      } else {
        currentInput = input_elements[get(currentLineIndex)];
        text2 = get(dialogue_lines)[get(currentLineIndex)].text;
      }
      const cursorPosition = currentInput?.selectionStart || 0;
      const lastColonIndex = text2.lastIndexOf(":", cursorPosition - 1);
      if (lastColonIndex >= 0) {
        const beforeColon = text2.substring(0, lastColonIndex);
        const afterCursor = text2.substring(cursorPosition);
        if (get(checked)) {
          const newText = `${beforeColon}${tag} ${afterCursor}`;
          set(textbox_value, newText);
          if (gradio.props.speakers.length === 0) {
            gradio.props.value = newText;
          } else {
            gradio.props.value = await gradio.shared.server.unformat({ text: newText });
          }
          tick().then(() => {
            if (textarea_element) {
              const newCursorPosition = beforeColon.length + tag.length + 1;
              textarea_element.setSelectionRange(newCursorPosition, newCursorPosition);
              textarea_element.focus();
            }
          });
        } else {
          const filteredBeforeColon = beforeColon.replace(/\[S\d+\]/g, "").trim();
          const newText = `${filteredBeforeColon}${tag} ${afterCursor}`;
          update_line(get(currentLineIndex), "text", newText);
          tick().then(() => {
            const updatedInput = input_elements[get(currentLineIndex)];
            if (updatedInput) {
              const newCursorPosition = filteredBeforeColon.length + tag.length + 1;
              updatedInput.setSelectionRange(newCursorPosition, newCursorPosition);
              updatedInput.focus();
            }
          });
        }
      }
      set(showTagMenu, false);
      set(selectedOptionIndex, 0);
    }
  }
  async function insert_tag(e) {
    const tag = gradio.props.tags[e.detail.target.dataset.index];
    if (tag) {
      let text2;
      let currentInput;
      if (get(checked)) {
        currentInput = textarea_element;
        text2 = get(textbox_value);
      } else {
        currentInput = input_elements[get(currentLineIndex)];
        text2 = get(dialogue_lines)[get(currentLineIndex)].text;
      }
      const cursorPosition = currentInput?.selectionStart || 0;
      const lastColonIndex = text2.lastIndexOf(":", cursorPosition - 1);
      if (lastColonIndex >= 0) {
        const beforeColon = text2.substring(0, lastColonIndex);
        const afterCursor = text2.substring(cursorPosition);
        if (get(checked)) {
          const newText = `${beforeColon}${tag} ${afterCursor}`;
          set(textbox_value, newText);
          if (gradio.props.speakers.length === 0) {
            gradio.props.value = newText;
          } else {
            gradio.props.value = await gradio.shared.server.unformat({ text: newText });
          }
          tick().then(() => {
            if (textarea_element) {
              const newCursorPosition = beforeColon.length + tag.length + 1;
              textarea_element.setSelectionRange(newCursorPosition, newCursorPosition);
              textarea_element.focus();
            }
          });
        } else {
          const filteredBeforeColon = beforeColon.replace(/\[S\d+\]/g, "").trim();
          const newText = `${filteredBeforeColon}${tag} ${afterCursor}`;
          update_line(get(currentLineIndex), "text", newText);
          tick().then(() => {
            const updatedInput = input_elements[get(currentLineIndex)];
            if (updatedInput) {
              const newCursorPosition = filteredBeforeColon.length + tag.length + 1;
              updatedInput.setSelectionRange(newCursorPosition, newCursorPosition);
              updatedInput.focus();
            }
          });
        }
      }
      set(showTagMenu, false);
      set(selectedOptionIndex, 0);
    }
  }
  function handle_click_outside(event2) {
    if (get(showTagMenu)) {
      const target = event2.target;
      const tagMenu = document.getElementById("tag-menu");
      if (tagMenu && !tagMenu.contains(target)) {
        set(showTagMenu, false);
      }
    }
  }
  async function value_to_string(value) {
    if (typeof value === "string") {
      return value;
    }
    return await gradio.shared.server.format(value);
  }
  async function handle_copy() {
    if ("clipboard" in navigator) {
      const text2 = await value_to_string(gradio.props.value);
      await navigator.clipboard.writeText(text2);
      copy_feedback();
    }
  }
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
  async function handle_submit() {
    if (get(checked)) {
      gradio.props.value = await gradio.shared.server.unformat({ text: get(textbox_value) });
    }
    gradio.dispatch("submit");
  }
  onMount(async () => {
    if (typeof gradio.props.value === "string") {
      set(textbox_value, gradio.props.value, true);
    } else if (gradio.props.value && gradio.props.value.length > 0) {
      const formatted = await value_to_string(gradio.props.value);
      set(textbox_value, formatted, true);
    } else {
      set(textbox_value, "");
    }
  });
  var label = root();
  event("click", $window, handle_click_outside);
  let classes;
  var node = child(label);
  {
    var consequent = ($$anchor2) => {
      IconButtonWrapper($$anchor2, {
        children: ($$anchor3, $$slotProps) => {
          {
            let $0 = user_derived(() => get(copied) ? Check : Copy);
            let $1 = user_derived(() => get(copied) ? "Copied" : "Copy");
            IconButton($$anchor3, {
              get Icon() {
                return get($0);
              },
              get label() {
                return get($1);
              },
              $$events: { click: handle_copy }
            });
          }
        },
        $$slots: { default: true }
      });
    };
    if_block(node, ($$render) => {
      if (gradio.shared.show_label && get(buttons).includes("copy")) $$render(consequent);
    });
  }
  var node_1 = sibling(node, 2);
  BlockTitle(node_1, {
    get show_label() {
      return gradio.shared.show_label;
    },
    get info() {
      return gradio.props.info;
    },
    children: ($$anchor2, $$slotProps) => {
      next();
      var text_1 = text();
      template_effect(() => set_text(text_1, gradio.shared.label || "Dialogue"));
      append($$anchor2, text_1);
    },
    $$slots: { default: true }
  });
  var node_2 = sibling(node_1, 2);
  {
    var consequent_1 = ($$anchor2) => {
      var div = root_4();
      let classes_1;
      var node_3 = child(div);
      {
        let $0 = user_derived(() => get(is_formatting) || get(is_unformatting));
        Switch(node_3, {
          label: "Plain Text",
          get disabled() {
            return get($0);
          },
          get checked() {
            return get(checked);
          },
          set checked($$value) {
            set(checked, $$value);
          },
          $$events: {
            click: async (e) => {
              if (!e.detail.checked) {
                set(is_unformatting, true);
                try {
                  gradio.props.value = await gradio.shared.server.unformat({ text: get(textbox_value) });
                  set(dialogue_lines, [...gradio.props.value], true);
                } finally {
                  set(is_unformatting, false);
                }
              } else {
                set(is_formatting, true);
                try {
                  set(textbox_value, await value_to_string(get(dialogue_lines)), true);
                } finally {
                  set(is_formatting, false);
                }
              }
            }
          }
        });
      }
      reset(div);
      template_effect(() => classes_1 = set_class(div, 1, "switch-container top-switch svelte-1p54cvv", null, classes_1, {
        "switch-disabled": get(is_formatting) || get(is_unformatting)
      }));
      append($$anchor2, div);
    };
    if_block(node_2, ($$render) => {
      if (gradio.props.ui_mode === "both") $$render(consequent_1);
    });
  }
  var node_4 = sibling(node_2, 2);
  {
    var consequent_6 = ($$anchor2) => {
      var div_1 = root_5();
      let classes_2;
      var node_5 = child(div_1);
      {
        var consequent_2 = ($$anchor3) => {
          var div_2 = root_6();
          transition(3, div_2, () => fade, () => ({ duration: 200 }));
          append($$anchor3, div_2);
        };
        if_block(node_5, ($$render) => {
          if (get(is_unformatting)) $$render(consequent_2);
        });
      }
      var node_6 = sibling(node_5, 2);
      each(node_6, 17, () => get(dialogue_lines), index, ($$anchor3, line, i) => {
        var div_3 = root_7();
        var div_4 = child(div_3);
        var node_7 = child(div_4);
        {
          var consequent_3 = ($$anchor4) => {
            var textarea = root_8();
            remove_textarea_child(textarea);
            template_effect(() => textarea.disabled = get(disabled));
            bind_value(textarea, () => get(line).speaker, ($$value) => get(line).speaker = $$value);
            append($$anchor4, textarea);
          };
          var alternate = ($$anchor4) => {
            const dd_props = user_derived(() => new Gradio({
              shared_props: {
                container: true,
                show_label: false,
                interactive: true,
                label: ""
              },
              props: {
                value: get(line).speaker,
                choices: gradio.props.speakers.map((s) => [s, s])
              }
            }));
            Dropdown($$anchor4, {
              on_change: () => update_line(i, "speaker", get(dd_props).props.value),
              get gradio() {
                return get(dd_props);
              }
            });
          };
          if_block(node_7, ($$render) => {
            if (get(disabled)) $$render(consequent_3);
            else $$render(alternate, false);
          });
        }
        reset(div_4);
        var div_5 = sibling(div_4, 2);
        var div_6 = child(div_5);
        var textarea_1 = child(div_6);
        remove_textarea_child(textarea_1);
        bind_this(textarea_1, ($$value, i2) => input_elements[i2] = $$value, (i2) => input_elements?.[i2], () => [i]);
        var node_8 = sibling(textarea_1, 2);
        {
          var consequent_4 = ($$anchor4) => {
            var div_7 = root_10();
            var node_9 = child(div_7);
            {
              let $0 = user_derived(() => gradio.props.tags.map((s, i2) => [s, i2]));
              let $1 = user_derived(() => get(filtered_tags).map((s) => gradio.props.tags.indexOf(s)));
              let $2 = user_derived(() => get(filtered_tags).map((s) => gradio.props.tags.indexOf(s))[get(selectedOptionIndex)]);
              DropdownOptions(node_9, {
                get choices() {
                  return get($0);
                },
                get filtered_indices() {
                  return get($1);
                },
                get active_index() {
                  return get($2);
                },
                show_options: true,
                get offset_from_top() {
                  return get(offset_from_top);
                },
                from_top: true,
                $$events: { change: (e) => insert_tag(e) }
              });
            }
            reset(div_7);
            transition(3, div_7, () => fade, () => ({ duration: 100 }));
            append($$anchor4, div_7);
          };
          if_block(node_8, ($$render) => {
            if (get(showTagMenu) && get(currentLineIndex) === i) $$render(consequent_4);
          });
        }
        reset(div_6);
        reset(div_5);
        var node_10 = sibling(div_5, 2);
        {
          var consequent_5 = ($$anchor4) => {
            var div_8 = root_11();
            let classes_3;
            var button = child(div_8);
            var node_11 = child(button);
            Plus(node_11);
            reset(button);
            reset(div_8);
            template_effect(() => {
              classes_3 = set_class(div_8, 1, "svelte-1p54cvv", null, classes_3, { "action-column": i == 0, hidden: get(disabled) });
              button.disabled = get(disabled);
            });
            event("click", button, () => add_line(i));
            append($$anchor4, div_8);
          };
          if_block(node_10, ($$render) => {
            if (gradio.props.max_lines == void 0 || gradio.props.max_lines && i < gradio.props.max_lines - 1) $$render(consequent_5);
          });
        }
        var div_9 = sibling(node_10, 2);
        let classes_4;
        var button_1 = child(div_9);
        var node_12 = child(button_1);
        Trash(node_12);
        reset(button_1);
        reset(div_9);
        reset(div_3);
        template_effect(() => {
          set_style(div_3, `--speaker-bg-color: ${(get(disabled) && (get(hoveredSpeaker) === null || get(hoveredSpeaker) === get(line).speaker) ? get(speakerColors)[get(line).speaker] || "transparent" : "transparent") ?? ""}`);
          set_attribute(textarea_1, "placeholder", gradio.props.placeholder);
          textarea_1.disabled = get(disabled);
          classes_4 = set_class(div_9, 1, "action-column svelte-1p54cvv", null, classes_4, { hidden: get(disabled) || i == 0 });
          button_1.disabled = get(disabled);
        });
        event("mouseenter", div_4, () => get(disabled) && set(hoveredSpeaker, get(line).speaker, true));
        event("mouseleave", div_4, () => get(disabled) && set(hoveredSpeaker, null));
        bind_value(textarea_1, () => get(line).text, ($$value) => get(line).text = $$value);
        event("input", textarea_1, (event2) => handle_input(event2, i));
        event("focus", textarea_1, (event2) => handle_input(event2, i));
        event("keydown", textarea_1, (event2) => {
          if (event2.key === "Escape" && get(showTagMenu)) {
            set(showTagMenu, false);
            set(selectedOptionIndex, 0);
            event2.preventDefault();
          } else if (get(showTagMenu) && get(currentLineIndex) === i) {
            if (event2.key === "ArrowDown") {
              set(selectedOptionIndex, Math.min(get(selectedOptionIndex) + 1, get(filtered_tags).length - 1), true);
              event2.preventDefault();
            } else if (event2.key === "ArrowUp") {
              set(selectedOptionIndex, Math.max(get(selectedOptionIndex) - 1, 0), true);
              event2.preventDefault();
            } else if (event2.key === "Enter") {
              if (get(filtered_tags)[get(selectedOptionIndex)]) {
                insert_selected_tag();
              }
              event2.preventDefault();
            }
          }
        });
        event("click", button_1, () => delete_line(i));
        append($$anchor3, div_3);
      });
      reset(div_1);
      bind_this(div_1, ($$value) => dialogue_container_element = $$value, () => dialogue_container_element);
      template_effect(() => classes_2 = set_class(div_1, 1, "dialogue-container svelte-1p54cvv", null, classes_2, { loading: get(is_unformatting) }));
      append($$anchor2, div_1);
    };
    var alternate_1 = ($$anchor2) => {
      var fragment_4 = comment();
      var node_13 = first_child(fragment_4);
      {
        var consequent_9 = ($$anchor3) => {
          var div_10 = root_13();
          let classes_5;
          var node_14 = child(div_10);
          {
            var consequent_7 = ($$anchor4) => {
              var div_11 = root_14();
              transition(3, div_11, () => fade, () => ({ duration: 200 }));
              append($$anchor4, div_11);
            };
            if_block(node_14, ($$render) => {
              if (get(is_formatting)) $$render(consequent_7);
            });
          }
          var textarea_2 = sibling(node_14, 2);
          remove_textarea_child(textarea_2);
          set_attribute(textarea_2, "rows", 5);
          bind_this(textarea_2, ($$value) => textarea_element = $$value, () => textarea_element);
          var node_15 = sibling(textarea_2, 2);
          {
            var consequent_8 = ($$anchor4) => {
              var div_12 = root_15();
              var node_16 = child(div_12);
              {
                let $0 = user_derived(() => gradio.props.tags.map((s, i) => [s, i]));
                let $1 = user_derived(() => get(filtered_tags).map((s) => gradio.props.tags.indexOf(s)));
                let $2 = user_derived(() => get(filtered_tags).map((s) => gradio.props.tags.indexOf(s))[get(selectedOptionIndex)]);
                DropdownOptions(node_16, {
                  get choices() {
                    return get($0);
                  },
                  get filtered_indices() {
                    return get($1);
                  },
                  get active_index() {
                    return get($2);
                  },
                  show_options: true,
                  $$events: { change: (e) => insert_tag(e) }
                });
              }
              reset(div_12);
              transition(3, div_12, () => fade, () => ({ duration: 100 }));
              append($$anchor4, div_12);
            };
            if_block(node_15, ($$render) => {
              if (get(showTagMenu)) $$render(consequent_8);
            });
          }
          reset(div_10);
          template_effect(() => {
            classes_5 = set_class(div_10, 1, "textarea-container svelte-1p54cvv", null, classes_5, { loading: get(is_formatting) });
            set_attribute(textarea_2, "placeholder", gradio.props.placeholder);
            textarea_2.disabled = get(disabled);
          });
          bind_value(textarea_2, () => get(textbox_value), ($$value) => set(textbox_value, $$value));
          event("input", textarea_2, (event2) => {
            handle_input(event2, 0);
            gradio.props.value = get(textbox_value);
          });
          event("focus", textarea_2, (event2) => handle_input(event2, 0));
          event("keydown", textarea_2, (event2) => {
            if (event2.key === "Escape" && get(showTagMenu)) {
              set(showTagMenu, false);
              set(selectedOptionIndex, 0);
              event2.preventDefault();
            } else if (get(showTagMenu)) {
              if (event2.key === "ArrowDown") {
                set(selectedOptionIndex, Math.min(get(selectedOptionIndex) + 1, get(filtered_tags).length - 1), true);
                event2.preventDefault();
              } else if (event2.key === "ArrowUp") {
                set(selectedOptionIndex, Math.max(get(selectedOptionIndex) - 1, 0), true);
                event2.preventDefault();
              } else if (event2.key === "Enter") {
                if (get(filtered_tags)[get(selectedOptionIndex)]) {
                  insert_selected_tag();
                }
                event2.preventDefault();
              }
            }
          });
          append($$anchor3, div_10);
        };
        if_block(
          node_13,
          ($$render) => {
            if (get(checked) || gradio.props.ui_mode !== "dialogue") $$render(consequent_9);
          },
          true
        );
      }
      append($$anchor2, fragment_4);
    };
    if_block(node_4, ($$render) => {
      if (!get(checked) && gradio.props.ui_mode !== "text") $$render(consequent_6);
      else $$render(alternate_1, false);
    });
  }
  var node_17 = sibling(node_4, 2);
  {
    var consequent_11 = ($$anchor2) => {
      var div_13 = root_16();
      var button_2 = child(div_13);
      var node_18 = child(button_2);
      {
        var consequent_10 = ($$anchor3) => {
          var text_2 = text();
          template_effect(() => set_text(text_2, gradio.props.submit_btn));
          append($$anchor3, text_2);
        };
        var alternate_2 = ($$anchor3) => {
          Send($$anchor3);
        };
        if_block(node_18, ($$render) => {
          if (typeof gradio.props.submit_btn === "string") $$render(consequent_10);
          else $$render(alternate_2, false);
        });
      }
      reset(button_2);
      reset(div_13);
      template_effect(() => button_2.disabled = get(disabled));
      event("click", button_2, handle_submit);
      append($$anchor2, div_13);
    };
    if_block(node_17, ($$render) => {
      if (gradio.props.submit_btn && !get(disabled)) $$render(consequent_11);
    });
  }
  reset(label);
  template_effect(() => classes = set_class(label, 1, "svelte-1p54cvv", null, classes, { container: gradio.shared.container }));
  append($$anchor, label);
  pop();
}
var root_1 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
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
    get scale() {
      return gradio.shared.scale;
    },
    get min_width() {
      return gradio.shared.min_width;
    },
    allow_overflow: true,
    get padding() {
      return gradio.shared.container;
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
      Dialogue(node_1, {
        get gradio() {
          return gradio;
        }
      });
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Dialogue as BaseDialogue,
  default2 as BaseExample,
  Index as default
};
//# sourceMappingURL=BfphzK9v.js.map
