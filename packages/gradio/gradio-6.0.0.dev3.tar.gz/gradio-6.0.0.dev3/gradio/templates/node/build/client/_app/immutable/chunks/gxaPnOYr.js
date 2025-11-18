import "./9B4_veAf.js";
import { f as from_svg, b as append, p as push, q as createEventDispatcher, i as legacy_pre_effect, j as set, m as mutable_source, k as get, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, r as reset, o as pop, v as first_child, s as sibling, t as template_effect, y as untrack, g as set_text, z as event, A as user_derived, D as comment, x as derived_safe_equal, W as to_array, aQ as autofocus, I as onMount, J as state, L as proxy, M as user_effect } from "./DEzry6cj.js";
import { p as prop, i as if_block, r as rest_props, s as spread_props } from "./DUftb7my.js";
import "./BAp-OWo-.js";
import { a5 as colors, t as each, v as index, p as set_style, a as set_class, r as remove_input_defaults, s as set_attribute, w as set_value, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { g as get_next_color } from "./C7iqN3X7.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { E as Empty } from "./B-xg5Dhl.js";
var root$2 = from_svg(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--carbon" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" viewBox="0 0 32 32"><path fill="currentColor" d="M12 15H5a3 3 0 0 1-3-3v-2a3 3 0 0 1 3-3h5V5a1 1 0 0 0-1-1H3V2h6a3 3 0 0 1 3 3zM5 9a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1h5V9zm15 14v2a1 1 0 0 0 1 1h5v-4h-5a1 1 0 0 0-1 1z"></path><path fill="currentColor" d="M2 30h28V2Zm26-2h-7a3 3 0 0 1-3-3v-2a3 3 0 0 1 3-3h5v-2a1 1 0 0 0-1-1h-6v-2h6a3 3 0 0 1 3 3Z"></path></svg>`);
function TextHighlight($$anchor) {
  var svg = root$2();
  append($$anchor, svg);
}
function name_to_rgba(name, a, ctx) {
  if (!ctx) {
    var canvas = document.createElement("canvas");
    ctx = canvas.getContext("2d");
  }
  ctx.fillStyle = name;
  ctx.fillRect(0, 0, 1, 1);
  const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
  ctx.clearRect(0, 0, 1, 1);
  return `rgba(${r}, ${g}, ${b}, ${255 / a})`;
}
function correct_color_map(color_map, _color_map, browser, ctx) {
  for (const col in color_map) {
    const _c = color_map[col].trim();
    if (_c in colors) {
      _color_map[col] = colors[_c];
    } else {
      _color_map[col] = {
        primary: browser ? name_to_rgba(color_map[col], 1, ctx) : color_map[col],
        secondary: browser ? name_to_rgba(color_map[col], 0.5, ctx) : color_map[col]
      };
    }
  }
}
function merge_elements(value, mergeMode) {
  let result = [];
  let tempStr = null;
  let tempVal = null;
  for (const val of value) {
    if (tempVal === val.class_or_confidence) {
      tempStr = tempStr ? tempStr + val.token : val.token;
    } else {
      if (tempStr !== null) {
        result.push({
          token: tempStr,
          class_or_confidence: tempVal
        });
      }
      tempStr = val.token;
      tempVal = val.class_or_confidence;
    }
  }
  if (tempStr !== null) {
    result.push({
      token: tempStr,
      class_or_confidence: tempVal
    });
  }
  return result;
}
var root_3 = from_html(`<div class="category-label svelte-7i12tt"> </div>`);
var root_2$3 = from_html(`<div class="category-legend svelte-7i12tt" data-testid="highlighted-text:category-legend"></div>`);
var root_7$1 = from_html(`&nbsp; <span class="label svelte-7i12tt"> </span>`, 1);
var root_6$1 = from_html(`<span><span> </span> <!></span>`);
var root_8$2 = from_html(`<br/>`);
var root_5 = from_html(`<!> <!>`, 1);
var root_1$2 = from_html(`<!> <div class="textfield svelte-7i12tt"></div>`, 1);
var root_10$1 = from_html(`<div class="color-legend svelte-7i12tt" data-testid="highlighted-text:color-legend"><span>-1</span> <span>0</span> <span>+1</span></div>`);
var root_11$1 = from_html(`<span class="textspan score-text svelte-7i12tt"><span class="text svelte-7i12tt"> </span></span>`);
var root_9$1 = from_html(`<!> <div class="textfield svelte-7i12tt" data-testid="highlighted-text:textfield"></div>`, 1);
var root$1 = from_html(`<div class="container svelte-7i12tt"><!></div>`);
function StaticHighlightedtext($$anchor, $$props) {
  push($$props, false);
  const browser = typeof document !== "undefined";
  let value = prop($$props, "value", 24, () => []);
  let show_legend = prop($$props, "show_legend", 8, false);
  let show_inline_category = prop($$props, "show_inline_category", 8, true);
  let color_map = prop($$props, "color_map", 28, () => ({}));
  let selectable = prop($$props, "selectable", 8, false);
  let ctx;
  let _color_map = mutable_source({});
  let active = mutable_source("");
  function splitTextByNewline(text) {
    return text.split("\n");
  }
  const dispatch = createEventDispatcher();
  let mode = mutable_source();
  function handle_mouseover(label) {
    set(active, label);
  }
  function handle_mouseout() {
    set(active, "");
  }
  legacy_pre_effect(
    () => (deep_read_state(color_map()), deep_read_state(value()), get(_color_map), correct_color_map),
    () => {
      if (!color_map()) {
        color_map({});
      }
      if (value().length > 0) {
        for (let entry of value()) {
          if (entry.class_or_confidence !== null) {
            if (typeof entry.class_or_confidence === "string") {
              set(mode, "categories");
              if (!(entry.class_or_confidence in color_map())) {
                let color = get_next_color(Object.keys(color_map()).length);
                color_map(color_map()[entry.class_or_confidence] = color, true);
              }
            } else {
              set(mode, "scores");
            }
          }
        }
      }
      set(_color_map, {});
      correct_color_map(color_map(), get(_color_map), browser, ctx);
    }
  );
  legacy_pre_effect_reset();
  init();
  var div = root$1();
  var node = child(div);
  {
    var consequent_4 = ($$anchor2) => {
      var fragment = root_1$2();
      var node_1 = first_child(fragment);
      {
        var consequent = ($$anchor3) => {
          var div_1 = root_2$3();
          each(
            div_1,
            5,
            () => (get(_color_map), untrack(() => Object.entries(get(_color_map)))),
            index,
            ($$anchor4, $$item) => {
              var $$array = user_derived(() => to_array(get($$item), 2));
              let category = () => get($$array)[0];
              let color = () => get($$array)[1];
              var div_2 = root_3();
              var text_1 = child(div_2, true);
              reset(div_2);
              template_effect(() => {
                set_style(div_2, (color(), untrack(() => "background-color:" + color().secondary)));
                set_text(text_1, category());
              });
              event("mouseover", div_2, () => handle_mouseover(category()));
              event("focus", div_2, () => handle_mouseover(category()));
              event("mouseout", div_2, () => handle_mouseout());
              event("blur", div_2, () => handle_mouseout());
              append($$anchor4, div_2);
            }
          );
          reset(div_1);
          append($$anchor3, div_1);
        };
        if_block(node_1, ($$render) => {
          if (show_legend()) $$render(consequent);
        });
      }
      var div_3 = sibling(node_1, 2);
      each(div_3, 5, value, index, ($$anchor3, v, i) => {
        var fragment_1 = comment();
        var node_2 = first_child(fragment_1);
        each(
          node_2,
          1,
          () => (get(v), untrack(() => splitTextByNewline(get(v).token))),
          index,
          ($$anchor4, line, j) => {
            var fragment_2 = root_5();
            var node_3 = first_child(fragment_2);
            {
              var consequent_2 = ($$anchor5) => {
                var span = root_6$1();
                let classes;
                let styles;
                var span_1 = child(span);
                let classes_1;
                var text_2 = child(span_1, true);
                reset(span_1);
                var node_4 = sibling(span_1, 2);
                {
                  var consequent_1 = ($$anchor6) => {
                    var fragment_3 = root_7$1();
                    var span_2 = sibling(first_child(fragment_3));
                    let styles_1;
                    var text_3 = child(span_2, true);
                    reset(span_2);
                    template_effect(() => {
                      styles_1 = set_style(span_2, "", styles_1, {
                        "background-color": (get(v), get(active), get(_color_map), untrack(() => get(v).class_or_confidence === null || get(active) && get(active) !== get(v).class_or_confidence ? "" : get(_color_map)[get(v).class_or_confidence].primary))
                      });
                      set_text(text_3, (get(v), untrack(() => get(v).class_or_confidence)));
                    });
                    append($$anchor6, fragment_3);
                  };
                  if_block(node_4, ($$render) => {
                    if (deep_read_state(show_legend()), deep_read_state(show_inline_category()), get(v), untrack(() => !show_legend() && show_inline_category() && get(v).class_or_confidence !== null)) $$render(consequent_1);
                  });
                }
                reset(span);
                template_effect(() => {
                  classes = set_class(span, 1, "textspan svelte-7i12tt", null, classes, {
                    "no-cat": get(v).class_or_confidence === null || get(active) && get(active) !== get(v).class_or_confidence,
                    hl: get(v).class_or_confidence !== null,
                    selectable: selectable()
                  });
                  styles = set_style(span, "", styles, {
                    "background-color": (get(v), get(active), get(_color_map), untrack(() => get(v).class_or_confidence === null || get(active) && get(active) !== get(v).class_or_confidence ? "" : get(_color_map)[get(v).class_or_confidence].secondary))
                  });
                  classes_1 = set_class(span_1, 1, "text svelte-7i12tt", null, classes_1, {
                    "no-label": get(v).class_or_confidence === null || !get(_color_map)[get(v).class_or_confidence]
                  });
                  set_text(text_2, get(line));
                });
                event("click", span, () => {
                  dispatch("select", {
                    index: i,
                    value: [get(v).token, get(v).class_or_confidence]
                  });
                });
                append($$anchor5, span);
              };
              if_block(node_3, ($$render) => {
                if (get(line), untrack(() => get(line).trim() !== "")) $$render(consequent_2);
              });
            }
            var node_5 = sibling(node_3, 2);
            {
              var consequent_3 = ($$anchor5) => {
                var br = root_8$2();
                append($$anchor5, br);
              };
              if_block(node_5, ($$render) => {
                if (get(v), untrack(() => j < splitTextByNewline(get(v).token).length - 1)) $$render(consequent_3);
              });
            }
            append($$anchor4, fragment_2);
          }
        );
        append($$anchor3, fragment_1);
      });
      reset(div_3);
      append($$anchor2, fragment);
    };
    var alternate = ($$anchor2) => {
      var fragment_4 = root_9$1();
      var node_6 = first_child(fragment_4);
      {
        var consequent_5 = ($$anchor3) => {
          var div_4 = root_10$1();
          append($$anchor3, div_4);
        };
        if_block(node_6, ($$render) => {
          if (show_legend()) $$render(consequent_5);
        });
      }
      var div_5 = sibling(node_6, 2);
      each(div_5, 5, value, index, ($$anchor3, v) => {
        const score = derived_safe_equal(() => (get(v), untrack(() => typeof get(v).class_or_confidence === "string" ? parseInt(get(v).class_or_confidence) : get(v).class_or_confidence)));
        var span_3 = root_11$1();
        var span_4 = child(span_3);
        var text_4 = child(span_4, true);
        reset(span_4);
        reset(span_3);
        template_effect(() => {
          set_style(span_3, "background-color: rgba(" + (get(score) && get(score) < 0 ? "128, 90, 213," + -get(score) : "239, 68, 60," + get(score)) + ")");
          set_text(text_4, (get(v), untrack(() => get(v).token)));
        });
        append($$anchor3, span_3);
      });
      reset(div_5);
      append($$anchor2, fragment_4);
    };
    if_block(node, ($$render) => {
      if (get(mode) === "categories") $$render(consequent_4);
      else $$render(alternate, false);
    });
  }
  reset(div);
  append($$anchor, div);
  pop();
}
var root_1$1 = from_html(`<input class="label-input svelte-14ic1z3" type="text" placeholder="label"/>`);
var root_2$2 = from_html(`<input class="label-input svelte-14ic1z3" type="number" step="0.1"/>`);
function LabelInput($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 12);
  let category = prop($$props, "category", 8);
  let active = prop($$props, "active", 8);
  let labelToEdit = prop($$props, "labelToEdit", 12);
  let indexOfLabel = prop($$props, "indexOfLabel", 8);
  let text = prop($$props, "text", 8);
  let handleValueChange = prop($$props, "handleValueChange", 8);
  let isScoresMode = prop($$props, "isScoresMode", 8, false);
  let _color_map = prop($$props, "_color_map", 8);
  let _input_value = mutable_source(category());
  function handleInput(e) {
    let target = e.target;
    if (target) {
      set(_input_value, target.value);
    }
  }
  function updateLabelValue(e, elementIndex, text2) {
    let target = e.target;
    value([
      ...value().slice(0, elementIndex),
      {
        token: text2,
        class_or_confidence: target.value === "" ? null : isScoresMode() ? Number(target.value) : target.value
      },
      ...value().slice(elementIndex + 1)
    ]);
    handleValueChange()();
  }
  function clearPlaceHolderOnFocus(e) {
    let target = e.target;
    if (target && target.placeholder) target.placeholder = "";
  }
  init();
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      var input = root_1$1();
      remove_input_defaults(input);
      autofocus(input, true);
      let styles;
      template_effect(
        ($0) => {
          set_attribute(input, "id", `label-input-${indexOfLabel()}`);
          set_value(input, category());
          styles = set_style(input, "", styles, $0);
        },
        [
          () => ({
            "background-color": (deep_read_state(category()), deep_read_state(active()), deep_read_state(_color_map()), untrack(() => category() === null || active() && active() !== category() ? "" : _color_map()[category()].primary)),
            width: (get(_input_value), untrack(() => get(_input_value) ? get(_input_value).toString()?.length + 4 + "ch" : "8ch"))
          })
        ]
      );
      event("input", input, handleInput);
      event("blur", input, (e) => updateLabelValue(e, indexOfLabel(), text()));
      event("keydown", input, (e) => {
        if (e.key === "Enter") {
          updateLabelValue(e, indexOfLabel(), text());
          labelToEdit(-1);
        }
      });
      event("focus", input, clearPlaceHolderOnFocus);
      append($$anchor2, input);
    };
    var alternate = ($$anchor2) => {
      var input_1 = root_2$2();
      remove_input_defaults(input_1);
      autofocus(input_1, true);
      let styles_1;
      template_effect(() => {
        styles_1 = set_style(
          input_1,
          "background-color: rgba(" + (typeof category() === "number" && category() < 0 ? "128, 90, 213," + -category() : "239, 68, 60," + category()) + ")",
          styles_1,
          { width: "7ch" }
        );
        set_value(input_1, category());
      });
      event("input", input_1, handleInput);
      event("blur", input_1, (e) => updateLabelValue(e, indexOfLabel(), text()));
      event("keydown", input_1, (e) => {
        if (e.key === "Enter") {
          updateLabelValue(e, indexOfLabel(), text());
          labelToEdit(-1);
        }
      });
      append($$anchor2, input_1);
    };
    if_block(node, ($$render) => {
      if (!isScoresMode()) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
var root_4 = from_html(`<div role="button" aria-roledescription="Categories of highlighted text. Hover to see text with this class_or_confidence highlighted." tabindex="0" class="class_or_confidence-label svelte-7z1kwz"> </div>`);
var root_2$1 = from_html(`<div class="class_or_confidence-legend svelte-7z1kwz" data-testid="highlighted-text:class_or_confidence-legend"><!></div>`);
var root_8$1 = from_html(`<span class="label svelte-7z1kwz" role="button" tabindex="0"> </span>`);
var root_9 = from_html(`&nbsp; <!>`, 1);
var root_10 = from_html(`<span class="label-clear-button svelte-7z1kwz" role="button" aria-roledescription="Remove label from text" tabindex="0">×</span>`);
var root_7 = from_html(`<span class="text-class_or_confidence-container svelte-7z1kwz"><span role="button" tabindex="0"><span role="button" tabindex="0"> </span> <!> <!></span> <!></span>`);
var root_11 = from_html(`<br/>`);
var root_6 = from_html(`<!> <!>`, 1);
var root_1 = from_html(`<!> <div class="textfield svelte-7z1kwz"></div>`, 1);
var root_13 = from_html(`<div class="color-legend svelte-7z1kwz" data-testid="highlighted-text:color-legend"><span>-1</span> <span>0</span> <span>+1</span></div>`);
var root_16 = from_html(`<span class="label-clear-button svelte-7z1kwz" role="button" aria-roledescription="Remove label from text" tabindex="0">×</span>`);
var root_14 = from_html(`<span class="score-text-container svelte-7z1kwz"><span role="button" tabindex="0"><span class="text svelte-7z1kwz"> </span> <!></span> <!></span>`);
var root_12 = from_html(`<!> <div class="textfield svelte-7z1kwz" data-testid="highlighted-text:textfield"></div>`, 1);
var root = from_html(`<div class="container svelte-7z1kwz"><!></div>`);
function InteractiveHighlightedtext($$anchor, $$props) {
  push($$props, false);
  const browser = typeof document !== "undefined";
  let value = prop($$props, "value", 28, () => []);
  let show_legend = prop($$props, "show_legend", 8, false);
  let color_map = prop($$props, "color_map", 28, () => ({}));
  let selectable = prop($$props, "selectable", 8, false);
  let activeElementIndex = mutable_source(-1);
  let ctx;
  let _color_map = mutable_source({});
  let active = mutable_source("");
  let selection;
  let labelToEdit = mutable_source(-1);
  onMount(() => {
    const mouseUpHandler = () => {
      selection = window.getSelection();
      handleSelectionComplete();
      window.removeEventListener("mouseup", mouseUpHandler);
    };
    window.addEventListener("mousedown", () => {
      window.addEventListener("mouseup", mouseUpHandler);
    });
  });
  async function handleTextSelected(startIndex, endIndex) {
    if (selection?.toString() && get(activeElementIndex) !== -1 && value()[get(activeElementIndex)].token.toString().includes(selection.toString())) {
      const tempFlag = Symbol();
      const str = value()[get(activeElementIndex)].token;
      const [before, selected, after] = [
        str.substring(0, startIndex),
        str.substring(startIndex, endIndex),
        str.substring(endIndex)
      ];
      let tempValue = [
        ...value().slice(0, get(activeElementIndex)),
        { token: before, class_or_confidence: null },
        {
          token: selected,
          class_or_confidence: get(mode) === "scores" ? 1 : "label",
          flag: tempFlag
        },
        // add a temp flag to the new highlighted text element
        { token: after, class_or_confidence: null },
        ...value().slice(get(activeElementIndex) + 1)
      ];
      set(labelToEdit, tempValue.findIndex(({ flag }) => flag === tempFlag));
      tempValue = tempValue.filter((item) => item.token.trim() !== "");
      value(tempValue.map(({ flag, ...rest }) => rest));
      handleValueChange();
      document.getElementById(`label-input-${get(labelToEdit)}`)?.focus();
    }
  }
  const dispatch = createEventDispatcher();
  function splitTextByNewline(text) {
    return text.split("\n");
  }
  function removeHighlightedText(index2) {
    if (!value() || index2 < 0 || index2 >= value().length) return;
    value(value()[index2].class_or_confidence = null, true);
    value(merge_elements(value()));
    handleValueChange();
    window.getSelection()?.empty();
  }
  function handleValueChange() {
    dispatch("change", value());
    set(labelToEdit, -1);
    if (show_legend()) {
      color_map({});
      set(_color_map, {});
    }
  }
  let mode = mutable_source();
  function handle_mouseover(label) {
    set(active, label);
  }
  function handle_mouseout() {
    set(active, "");
  }
  async function handleKeydownSelection(event2) {
    selection = window.getSelection();
    if (event2.key === "Enter") {
      handleSelectionComplete();
    }
  }
  function handleSelectionComplete() {
    if (selection && selection?.toString().trim() !== "") {
      const textBeginningIndex = selection.getRangeAt(0).startOffset;
      const textEndIndex = selection.getRangeAt(0).endOffset;
      handleTextSelected(textBeginningIndex, textEndIndex);
    }
  }
  function handleSelect(i, text, class_or_confidence) {
    dispatch("select", { index: i, value: [text, class_or_confidence] });
  }
  legacy_pre_effect(
    () => (deep_read_state(color_map()), deep_read_state(value()), get(_color_map), correct_color_map),
    () => {
      if (!color_map()) {
        color_map({});
      }
      if (value().length > 0) {
        for (let entry of value()) {
          if (entry.class_or_confidence !== null) {
            if (typeof entry.class_or_confidence === "string") {
              set(mode, "categories");
              if (!(entry.class_or_confidence in color_map())) {
                let color = get_next_color(Object.keys(color_map()).length);
                color_map(color_map()[entry.class_or_confidence] = color, true);
              }
            } else {
              set(mode, "scores");
            }
          }
        }
      }
      set(_color_map, {});
      correct_color_map(color_map(), get(_color_map), browser, ctx);
    }
  );
  legacy_pre_effect_reset();
  init();
  var div = root();
  var node = child(div);
  {
    var consequent_7 = ($$anchor2) => {
      var fragment = root_1();
      var node_1 = first_child(fragment);
      {
        var consequent_1 = ($$anchor3) => {
          var div_1 = root_2$1();
          var node_2 = child(div_1);
          {
            var consequent = ($$anchor4) => {
              var fragment_1 = comment();
              var node_3 = first_child(fragment_1);
              each(
                node_3,
                1,
                () => (get(_color_map), untrack(() => Object.entries(get(_color_map)))),
                index,
                ($$anchor5, $$item) => {
                  var $$array = user_derived(() => to_array(get($$item), 2));
                  let class_or_confidence = () => get($$array)[0];
                  let color = () => get($$array)[1];
                  var div_2 = root_4();
                  var text_1 = child(div_2, true);
                  reset(div_2);
                  template_effect(() => {
                    set_style(div_2, (color(), untrack(() => "background-color:" + color().secondary)));
                    set_text(text_1, class_or_confidence());
                  });
                  event("mouseover", div_2, () => handle_mouseover(class_or_confidence()));
                  event("focus", div_2, () => handle_mouseover(class_or_confidence()));
                  event("mouseout", div_2, () => handle_mouseout());
                  event("blur", div_2, () => handle_mouseout());
                  append($$anchor5, div_2);
                }
              );
              append($$anchor4, fragment_1);
            };
            if_block(node_2, ($$render) => {
              if (get(_color_map)) $$render(consequent);
            });
          }
          reset(div_1);
          append($$anchor3, div_1);
        };
        if_block(node_1, ($$render) => {
          if (show_legend()) $$render(consequent_1);
        });
      }
      var div_3 = sibling(node_1, 2);
      each(div_3, 5, value, index, ($$anchor3, $$item, i) => {
        let token = () => get($$item).token;
        let class_or_confidence = () => get($$item).class_or_confidence;
        var fragment_2 = comment();
        var node_4 = first_child(fragment_2);
        each(node_4, 1, () => (token(), untrack(() => splitTextByNewline(token()))), index, ($$anchor4, line, j) => {
          var fragment_3 = root_6();
          var node_5 = first_child(fragment_3);
          {
            var consequent_5 = ($$anchor5) => {
              var span = root_7();
              var span_1 = child(span);
              let classes;
              let styles;
              var span_2 = child(span_1);
              let classes_1;
              var text_2 = child(span_2, true);
              reset(span_2);
              var node_6 = sibling(span_2, 2);
              {
                var consequent_2 = ($$anchor6) => {
                  var span_3 = root_8$1();
                  set_attribute(span_3, "id", `label-tag-${i}`);
                  let styles_1;
                  var text_3 = child(span_3, true);
                  reset(span_3);
                  template_effect(() => {
                    styles_1 = set_style(span_3, "", styles_1, {
                      "background-color": (class_or_confidence(), get(active), get(_color_map), untrack(() => class_or_confidence() === null || get(active) && get(active) !== class_or_confidence() ? "" : get(_color_map)[class_or_confidence()].primary))
                    });
                    set_text(text_3, class_or_confidence());
                  });
                  event("click", span_3, () => set(labelToEdit, i));
                  event("keydown", span_3, () => set(labelToEdit, i));
                  append($$anchor6, span_3);
                };
                if_block(node_6, ($$render) => {
                  if (!show_legend() && class_or_confidence() !== null && get(labelToEdit) !== i) $$render(consequent_2);
                });
              }
              var node_7 = sibling(node_6, 2);
              {
                var consequent_3 = ($$anchor6) => {
                  var fragment_4 = root_9();
                  var node_8 = sibling(first_child(fragment_4));
                  LabelInput(node_8, {
                    get labelToEdit() {
                      return get(labelToEdit);
                    },
                    get category() {
                      return class_or_confidence();
                    },
                    get active() {
                      return get(active);
                    },
                    get _color_map() {
                      return get(_color_map);
                    },
                    indexOfLabel: i,
                    get text() {
                      return token();
                    },
                    handleValueChange,
                    get value() {
                      return value();
                    },
                    set value($$value) {
                      value($$value);
                    },
                    $$legacy: true
                  });
                  append($$anchor6, fragment_4);
                };
                if_block(node_7, ($$render) => {
                  if (get(labelToEdit) === i && class_or_confidence() !== null) $$render(consequent_3);
                });
              }
              reset(span_1);
              var node_9 = sibling(span_1, 2);
              {
                var consequent_4 = ($$anchor6) => {
                  var span_4 = root_10();
                  event("click", span_4, () => removeHighlightedText(i));
                  event("keydown", span_4, (event2) => {
                    if (event2.key === "Enter") {
                      removeHighlightedText(i);
                    }
                  });
                  append($$anchor6, span_4);
                };
                if_block(node_9, ($$render) => {
                  if (class_or_confidence() !== null) $$render(consequent_4);
                });
              }
              reset(span);
              template_effect(() => {
                classes = set_class(span_1, 1, "textspan svelte-7z1kwz", null, classes, {
                  "no-cat": class_or_confidence() === null || get(active) && get(active) !== class_or_confidence(),
                  hl: class_or_confidence() !== null,
                  selectable: selectable()
                });
                styles = set_style(span_1, "", styles, {
                  "background-color": (class_or_confidence(), get(active), get(_color_map), untrack(() => class_or_confidence() === null || get(active) && get(active) !== class_or_confidence() ? "" : class_or_confidence() && get(_color_map)[class_or_confidence()] ? get(_color_map)[class_or_confidence()].secondary : ""))
                });
                classes_1 = set_class(span_2, 1, "text svelte-7z1kwz", null, classes_1, { "no-label": class_or_confidence() === null });
                set_text(text_2, get(line));
              });
              event("keydown", span_2, (e) => handleKeydownSelection(e));
              event("focus", span_2, () => set(activeElementIndex, i));
              event("mouseover", span_2, () => set(activeElementIndex, i));
              event("click", span_2, () => set(labelToEdit, i));
              event("click", span_1, () => {
                if (class_or_confidence() !== null) {
                  handleSelect(i, token(), class_or_confidence());
                }
              });
              event("keydown", span_1, (e) => {
                if (class_or_confidence() !== null) {
                  set(labelToEdit, i);
                  handleSelect(i, token(), class_or_confidence());
                } else {
                  handleKeydownSelection(e);
                }
              });
              event("focus", span_1, () => set(activeElementIndex, i));
              event("mouseover", span_1, () => set(activeElementIndex, i));
              append($$anchor5, span);
            };
            if_block(node_5, ($$render) => {
              if (get(line), untrack(() => get(line).trim() !== "")) $$render(consequent_5);
            });
          }
          var node_10 = sibling(node_5, 2);
          {
            var consequent_6 = ($$anchor5) => {
              var br = root_11();
              append($$anchor5, br);
            };
            if_block(node_10, ($$render) => {
              if (token(), untrack(() => j < splitTextByNewline(token()).length - 1)) $$render(consequent_6);
            });
          }
          append($$anchor4, fragment_3);
        });
        append($$anchor3, fragment_2);
      });
      reset(div_3);
      append($$anchor2, fragment);
    };
    var alternate = ($$anchor2) => {
      var fragment_5 = root_12();
      var node_11 = first_child(fragment_5);
      {
        var consequent_8 = ($$anchor3) => {
          var div_4 = root_13();
          append($$anchor3, div_4);
        };
        if_block(node_11, ($$render) => {
          if (show_legend()) $$render(consequent_8);
        });
      }
      var div_5 = sibling(node_11, 2);
      each(div_5, 5, value, index, ($$anchor3, $$item, i) => {
        let token = () => get($$item).token;
        let class_or_confidence = () => get($$item).class_or_confidence;
        const score = derived_safe_equal(() => (class_or_confidence(), untrack(() => typeof class_or_confidence() === "string" ? parseInt(class_or_confidence()) : class_or_confidence())));
        var span_5 = root_14();
        var span_6 = child(span_5);
        let classes_2;
        var span_7 = child(span_6);
        var text_4 = child(span_7, true);
        reset(span_7);
        var node_12 = sibling(span_7, 2);
        {
          var consequent_9 = ($$anchor4) => {
            LabelInput($$anchor4, {
              get labelToEdit() {
                return get(labelToEdit);
              },
              get _color_map() {
                return get(_color_map);
              },
              get category() {
                return class_or_confidence();
              },
              get active() {
                return get(active);
              },
              indexOfLabel: i,
              get text() {
                return token();
              },
              handleValueChange,
              isScoresMode: true,
              get value() {
                return value();
              },
              set value($$value) {
                value($$value);
              },
              $$legacy: true
            });
          };
          if_block(node_12, ($$render) => {
            if (class_or_confidence() && get(labelToEdit) === i) $$render(consequent_9);
          });
        }
        reset(span_6);
        var node_13 = sibling(span_6, 2);
        {
          var consequent_10 = ($$anchor4) => {
            var span_8 = root_16();
            event("click", span_8, () => removeHighlightedText(i));
            event("keydown", span_8, (event2) => {
              if (event2.key === "Enter") {
                removeHighlightedText(i);
              }
            });
            append($$anchor4, span_8);
          };
          if_block(node_13, ($$render) => {
            if (class_or_confidence() && get(activeElementIndex) === i) $$render(consequent_10);
          });
        }
        reset(span_5);
        template_effect(() => {
          classes_2 = set_class(span_6, 1, "textspan score-text svelte-7z1kwz", null, classes_2, {
            "no-cat": class_or_confidence() === null || get(active) && get(active) !== class_or_confidence(),
            hl: class_or_confidence() !== null
          });
          set_style(span_6, "background-color: rgba(" + (get(score) && get(score) < 0 ? "128, 90, 213," + -get(score) : "239, 68, 60," + get(score)) + ")");
          set_text(text_4, token());
        });
        event("mouseover", span_6, () => set(activeElementIndex, i));
        event("focus", span_6, () => set(activeElementIndex, i));
        event("click", span_6, () => set(labelToEdit, i));
        event("keydown", span_6, (e) => {
          if (e.key === "Enter") {
            set(labelToEdit, i);
          }
        });
        append($$anchor3, span_5);
      });
      reset(div_5);
      append($$anchor2, fragment_5);
    };
    if_block(node, ($$render) => {
      if (get(mode) === "categories") $$render(consequent_7);
      else $$render(alternate, false);
    });
  }
  reset(div);
  append($$anchor, div);
  pop();
}
var root_2 = from_html(`<!> <!> <!>`, 1);
var root_8 = from_html(`<!> <!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let old_value = state(proxy(gradio.props.value));
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  let value = user_derived(() => gradio.props.combine_adjacent ? merge_elements(gradio.props.value) : gradio.props.value);
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent_2 = ($$anchor2) => {
      Block($$anchor2, {
        variant: "solid",
        test_id: "highlighted-text",
        get visible() {
          return gradio.shared.visible;
        },
        get elem_id() {
          return gradio.shared.elem_id;
        },
        get elem_classes() {
          return gradio.shared.elem_classes;
        },
        padding: false,
        get container() {
          return gradio.shared.container;
        },
        get scale() {
          return gradio.shared.scale;
        },
        get min_width() {
          return gradio.shared.min_width;
        },
        get rtl() {
          return gradio.props.rtl;
        },
        children: ($$anchor3, $$slotProps) => {
          var fragment_2 = root_2();
          var node_1 = first_child(fragment_2);
          Static(node_1, spread_props(
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
          var node_2 = sibling(node_1, 2);
          {
            var consequent = ($$anchor4) => {
              {
                let $0 = user_derived(() => gradio.shared.label || gradio.i18n("highlighted_text.highlighted_text"));
                let $1 = user_derived(() => gradio.shared.container === false);
                BlockLabel($$anchor4, {
                  get Icon() {
                    return TextHighlight;
                  },
                  get label() {
                    return get($0);
                  },
                  float: false,
                  get disable() {
                    return get($1);
                  },
                  get show_label() {
                    return gradio.shared.show_label;
                  },
                  get rtl() {
                    return gradio.props.rtl;
                  }
                });
              }
            };
            if_block(node_2, ($$render) => {
              if (gradio.shared.label && gradio.shared.show_label) $$render(consequent);
            });
          }
          var node_3 = sibling(node_2, 2);
          {
            var consequent_1 = ($$anchor4) => {
              StaticHighlightedtext($$anchor4, {
                selectable: false,
                get value() {
                  return get(value);
                },
                get show_legend() {
                  return gradio.props.show_legend;
                },
                get show_inline_category() {
                  return gradio.props.show_inline_category;
                },
                get color_map() {
                  return gradio.props.color_map;
                },
                $$events: { select: ({ detail }) => gradio.dispatch("select", detail) }
              });
            };
            var alternate = ($$anchor4) => {
              Empty($$anchor4, {
                children: ($$anchor5, $$slotProps2) => {
                  TextHighlight($$anchor5);
                },
                $$slots: { default: true }
              });
            };
            if_block(node_3, ($$render) => {
              if (get(value)) $$render(consequent_1);
              else $$render(alternate, false);
            });
          }
          append($$anchor3, fragment_2);
        },
        $$slots: { default: true }
      });
    };
    var alternate_2 = ($$anchor2) => {
      {
        let $0 = user_derived(() => gradio.shared.interactive ? "dashed" : "solid");
        Block($$anchor2, {
          get variant() {
            return get($0);
          },
          test_id: "highlighted-text",
          get visible() {
            return gradio.shared.visible;
          },
          get elem_id() {
            return gradio.shared.elem_id;
          },
          get elem_classes() {
            return gradio.shared.elem_classes;
          },
          padding: false,
          get container() {
            return gradio.shared.container;
          },
          get scale() {
            return gradio.shared.scale;
          },
          get min_width() {
            return gradio.shared.min_width;
          },
          children: ($$anchor3, $$slotProps) => {
            var fragment_8 = root_8();
            var node_4 = first_child(fragment_8);
            Static(node_4, spread_props(
              {
                get autoscroll() {
                  return gradio.shared.autoscroll;
                }
              },
              () => gradio.shared.loading_status,
              {
                get i18n() {
                  return gradio.i18n;
                },
                $$events: {
                  clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
                }
              }
            ));
            var node_5 = sibling(node_4, 2);
            {
              var consequent_3 = ($$anchor4) => {
                {
                  let $02 = user_derived(() => gradio.shared.container === false);
                  BlockLabel($$anchor4, {
                    get Icon() {
                      return TextHighlight;
                    },
                    get label() {
                      return gradio.shared.label;
                    },
                    float: false,
                    get disable() {
                      return get($02);
                    },
                    get show_label() {
                      return gradio.shared.show_label;
                    },
                    get rtl() {
                      return gradio.props.rtl;
                    }
                  });
                }
              };
              if_block(node_5, ($$render) => {
                if (gradio.shared.label && gradio.shared.show_label) $$render(consequent_3);
              });
            }
            var node_6 = sibling(node_5, 2);
            {
              var consequent_4 = ($$anchor4) => {
                InteractiveHighlightedtext($$anchor4, {
                  selectable: false,
                  get show_legend() {
                    return gradio.props.show_legend;
                  },
                  get color_map() {
                    return gradio.props.color_map;
                  },
                  get value() {
                    return get(value);
                  },
                  set value($$value) {
                    set(value, $$value);
                  },
                  $$events: {
                    change: () => {
                      gradio.props.value = get(value);
                      gradio.dispatch("change");
                    }
                  }
                });
              };
              var alternate_1 = ($$anchor4) => {
                Empty($$anchor4, {
                  size: "small",
                  unpadded_box: true,
                  children: ($$anchor5, $$slotProps2) => {
                    TextHighlight($$anchor5);
                  },
                  $$slots: { default: true }
                });
              };
              if_block(node_6, ($$render) => {
                if (get(value)) $$render(consequent_4);
                else $$render(alternate_1, false);
              });
            }
            append($$anchor3, fragment_8);
          },
          $$slots: { default: true }
        });
      }
    };
    if_block(node, ($$render) => {
      if (!gradio.shared.interactive) $$render(consequent_2);
      else $$render(alternate_2, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  InteractiveHighlightedtext as BaseInteractiveHighlightedText,
  StaticHighlightedtext as BaseStaticHighlightedText,
  Index as default
};
//# sourceMappingURL=gxaPnOYr.js.map
