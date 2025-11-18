import "./9B4_veAf.js";
import { h as hydrating, a as hydrate_next, G as is_runes, H as block, a9 as is_promise, aa as HYDRATION_START_ELSE, ab as set_hydrate_node, ac as skip_nodes, ad as set_hydrating, ae as queue_micro_task, af as internal_set, ag as source, m as mutable_source, ah as capture, ai as Batch, aj as unset_context, ak as is_flushing_sync, a5 as flushSync, al as UNINITIALIZED, p as push, i as legacy_pre_effect, j as set, u as deep_read_state, k as get, n as legacy_pre_effect_reset, c as from_html, v as first_child, s as sibling, b as append, o as pop, r as reset, D as comment, y as untrack, d as child, z as event, t as template_effect, g as set_text, x as derived_safe_equal, A as user_derived } from "./DEzry6cj.js";
import { B as BranchManager, p as prop, i as if_block, c as component, s as spread_props, r as rest_props } from "./DUftb7my.js";
import { t as each, v as index, p as set_style, a as set_class, k as clsx, G as Gradio, B as Block } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { k as key } from "./DssvUQ9s.js";
import { i as init } from "./DB0xzveP.js";
import Example from "./Bf3It-3j.js";
const PENDING = 0;
const THEN = 1;
function await_block(node, get_input, pending_fn, then_fn, catch_fn) {
  if (hydrating) {
    hydrate_next();
  }
  var runes = is_runes();
  var v = (
    /** @type {V} */
    UNINITIALIZED
  );
  var value = runes ? source(v) : mutable_source(v, false, false);
  var error = runes ? source(v) : mutable_source(v, false, false);
  var branches = new BranchManager(node);
  block(() => {
    var input = get_input();
    var destroyed = false;
    let mismatch = hydrating && is_promise(input) === (node.data === HYDRATION_START_ELSE);
    if (mismatch) {
      set_hydrate_node(skip_nodes());
      set_hydrating(false);
    }
    if (is_promise(input)) {
      var restore = capture();
      var resolved = false;
      const resolve = (fn) => {
        if (destroyed) return;
        resolved = true;
        restore(false);
        Batch.ensure();
        if (hydrating) {
          set_hydrating(false);
        }
        try {
          fn();
        } finally {
          unset_context();
          if (!is_flushing_sync) flushSync();
        }
      };
      input.then(
        (v2) => {
          resolve(() => {
            internal_set(value, v2);
            branches.ensure(THEN, then_fn && ((target) => then_fn(target, value)));
          });
        },
        (e) => {
          resolve(() => {
            internal_set(error, e);
            branches.ensure(THEN, catch_fn && ((target) => catch_fn(target, error)));
            if (!catch_fn) {
              throw error.v;
            }
          });
        }
      );
      if (hydrating) {
        branches.ensure(PENDING, pending_fn);
      } else {
        queue_micro_task(() => {
          if (!resolved) {
            resolve(() => {
              branches.ensure(PENDING, pending_fn);
            });
          }
        });
      }
    } else {
      internal_set(value, input);
      branches.ensure(THEN, then_fn && ((target) => then_fn(target, value)));
    }
    if (mismatch) {
      set_hydrating(true);
    }
    return () => {
      destroyed = true;
    };
  });
}
var root_4 = from_html(`<button class="gallery-item svelte-16f20a1"><!></button>`);
var root_2$1 = from_html(`<div class="gallery svelte-16f20a1"></div>`);
var root_12 = from_html(`<th class="svelte-16f20a1"> </th>`);
var root_15 = from_html(`<td><!></td>`);
var root_13 = from_html(`<tr class="tr-body svelte-16f20a1"></tr>`);
var root_11 = from_html(`<div class="table-wrap svelte-16f20a1"><table tabindex="0" role="grid" class="svelte-16f20a1"><thead><tr class="tr-head svelte-16f20a1"></tr></thead><tbody></tbody></table></div>`);
var root_19 = from_html(`<div>...</div>`);
var root_20 = from_html(`<button> </button>`);
var root_17 = from_html(`<div class="paginate svelte-16f20a1">Pages: <!></div>`);
var root_1$1 = from_html(`<!> <!>`, 1);
function Dataset($$anchor, $$props) {
  push($$props, false);
  const gallery = mutable_source();
  const selected_samples_json = mutable_source();
  let components = prop($$props, "components", 8);
  let component_props = prop($$props, "component_props", 8);
  let load_component = prop($$props, "load_component", 8);
  let headers = prop($$props, "headers", 8);
  let samples = prop($$props, "samples", 12, null);
  let old_samples = mutable_source(null);
  let sample_labels = prop($$props, "sample_labels", 8, null);
  let value = prop($$props, "value", 12, null);
  let root = prop($$props, "root", 8);
  let proxy_url = prop($$props, "proxy_url", 8);
  let samples_per_page = prop($$props, "samples_per_page", 8, 10);
  let onclick = prop($$props, "onclick", 8);
  let onselect = prop($$props, "onselect", 8);
  let layout = prop($$props, "layout", 8, null);
  let samples_dir = proxy_url() ? `/proxy=${proxy_url()}file=` : `${root()}/file=`;
  let page = mutable_source(0);
  let paginate = mutable_source(samples() ? samples().length > samples_per_page() : false);
  let selected_samples = mutable_source();
  let page_count = mutable_source();
  let visible_pages = mutable_source([]);
  let current_hover = mutable_source(-1);
  function handle_mouseenter(i) {
    set(current_hover, i);
  }
  function handle_mouseleave() {
    set(current_hover, -1);
  }
  let component_meta = mutable_source([]);
  async function get_component_meta(selected_samples_json2) {
    const _selected_samples = JSON.parse(selected_samples_json2);
    console.log("+++++++++++++++++++++++++++++++++++++");
    console.log("Getting component meta for samples:", _selected_samples, components());
    set(component_meta, await Promise.all(_selected_samples && _selected_samples.map(async (sample_row) => await Promise.all(sample_row.map(async (sample_cell, j) => {
      console.log("Loading component:", components()[j]);
      return {
        value: sample_cell,
        component: load_component()(components()[j], "example")
      };
    })))));
  }
  legacy_pre_effect(
    () => (deep_read_state(components()), deep_read_state(sample_labels()), deep_read_state(layout())),
    () => {
      set(gallery, (components().length < 2 || sample_labels() !== null) && layout() !== "table");
    }
  );
  legacy_pre_effect(
    () => (deep_read_state(sample_labels()), deep_read_state(samples()), get(old_samples), get(page), get(paginate), deep_read_state(samples_per_page()), get(visible_pages), get(page_count)),
    () => {
      if (sample_labels()) {
        samples(sample_labels().map((e) => [e]));
      } else if (!samples()) {
        samples([]);
      }
      if (JSON.stringify(samples()) !== JSON.stringify(get(old_samples))) {
        set(page, 0);
        set(old_samples, samples());
      }
      set(paginate, samples().length > samples_per_page());
      if (get(paginate)) {
        set(visible_pages, []);
        set(selected_samples, samples().slice(get(page) * samples_per_page(), (get(page) + 1) * samples_per_page()));
        set(page_count, Math.ceil(samples().length / samples_per_page()));
        [0, get(page), get(page_count) - 1].forEach((anchor) => {
          for (let i = anchor - 2; i <= anchor + 2; i++) {
            if (i >= 0 && i < get(page_count) && !get(visible_pages).includes(i)) {
              if (get(visible_pages).length > 0 && i - get(visible_pages)[get(visible_pages).length - 1] > 1) {
                get(visible_pages).push(-1);
              }
              get(visible_pages).push(i);
            }
          }
        });
      } else {
        set(selected_samples, samples().slice());
      }
    }
  );
  legacy_pre_effect(() => get(selected_samples), () => {
    set(selected_samples_json, JSON.stringify(get(selected_samples) || []));
  });
  legacy_pre_effect(() => get(selected_samples_json), () => {
    get_component_meta(get(selected_samples_json));
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root_1$1();
  var node = first_child(fragment);
  {
    var consequent_3 = ($$anchor2) => {
      var div = root_2$1();
      each(div, 5, () => get(selected_samples), index, ($$anchor3, sample_row, i) => {
        var fragment_1 = comment();
        var node_1 = first_child(fragment_1);
        {
          var consequent_2 = ($$anchor4) => {
            var button = root_4();
            var node_2 = child(button);
            {
              var consequent = ($$anchor5) => {
                {
                  let $0 = derived_safe_equal(() => get(current_hover) === i);
                  Example($$anchor5, {
                    get value() {
                      return get(sample_row), untrack(() => get(sample_row)[0]);
                    },
                    get selected() {
                      return get($0);
                    },
                    type: "gallery"
                  });
                }
              };
              var alternate = ($$anchor5) => {
                var fragment_3 = comment();
                var node_3 = first_child(fragment_3);
                {
                  var consequent_1 = ($$anchor6) => {
                    var fragment_4 = comment();
                    var node_4 = first_child(fragment_4);
                    await_block(
                      node_4,
                      () => (get(component_meta), untrack(() => get(component_meta)[0][0].component)),
                      null,
                      ($$anchor7, component$1) => {
                        var fragment_5 = comment();
                        var node_5 = first_child(fragment_5);
                        key(node_5, () => (get(sample_row), untrack(() => get(sample_row)[0])), ($$anchor8) => {
                          var fragment_6 = comment();
                          var node_6 = first_child(fragment_6);
                          {
                            let $0 = derived_safe_equal(() => get(current_hover) === i);
                            component(node_6, () => get(component$1).default, ($$anchor9, $$component) => {
                              $$component($$anchor9, spread_props(() => component_props()[0], {
                                get value() {
                                  return get(sample_row), untrack(() => get(sample_row)[0]);
                                },
                                get samples_dir() {
                                  return samples_dir;
                                },
                                type: "gallery",
                                get selected() {
                                  return get($0);
                                },
                                index: i,
                                get root() {
                                  return root();
                                }
                              }));
                            });
                          }
                          append($$anchor8, fragment_6);
                        });
                        append($$anchor7, fragment_5);
                      }
                    );
                    append($$anchor6, fragment_4);
                  };
                  if_block(
                    node_3,
                    ($$render) => {
                      if (get(component_meta), untrack(() => get(component_meta).length)) $$render(consequent_1);
                    },
                    true
                  );
                }
                append($$anchor5, fragment_3);
              };
              if_block(node_2, ($$render) => {
                if (sample_labels()) $$render(consequent);
                else $$render(alternate, false);
              });
            }
            reset(button);
            event("click", button, () => {
              value(i + get(page) * samples_per_page());
              onclick()({ index: value(), value: get(sample_row) });
              onselect()({ index: value(), value: get(sample_row) });
            });
            event("mouseenter", button, () => handle_mouseenter(i));
            event("mouseleave", button, () => handle_mouseleave());
            append($$anchor4, button);
          };
          if_block(node_1, ($$render) => {
            if (get(sample_row), untrack(() => get(sample_row)[0] != null)) $$render(consequent_2);
          });
        }
        append($$anchor3, fragment_1);
      });
      reset(div);
      append($$anchor2, div);
    };
    var alternate_1 = ($$anchor2) => {
      var fragment_7 = comment();
      var node_7 = first_child(fragment_7);
      {
        var consequent_5 = ($$anchor3) => {
          var div_1 = root_11();
          var table = child(div_1);
          var thead = child(table);
          var tr = child(thead);
          each(tr, 5, headers, index, ($$anchor4, header) => {
            var th = root_12();
            var text = child(th, true);
            reset(th);
            template_effect(() => set_text(text, get(header)));
            append($$anchor4, th);
          });
          reset(tr);
          reset(thead);
          var tbody = sibling(thead);
          each(tbody, 5, () => get(component_meta), index, ($$anchor4, sample_row, i) => {
            var tr_1 = root_13();
            each(tr_1, 5, () => get(sample_row), index, ($$anchor5, $$item, j, $$array) => {
              let value2 = () => get($$item).value;
              let component$1 = () => get($$item).component;
              const component_name = derived_safe_equal(() => (deep_read_state(components()), untrack(() => components()[j])));
              var fragment_8 = comment();
              var node_8 = first_child(fragment_8);
              {
                var consequent_4 = ($$anchor6) => {
                  var td = root_15();
                  var node_9 = child(td);
                  await_block(node_9, component$1, null, ($$anchor7, component$12) => {
                    var fragment_9 = comment();
                    var node_10 = first_child(fragment_9);
                    {
                      let $0 = derived_safe_equal(() => get(current_hover) === i);
                      component(node_10, () => get(component$12).default, ($$anchor8, $$component) => {
                        $$component($$anchor8, spread_props(() => component_props()[j], {
                          get value() {
                            return value2();
                          },
                          get samples_dir() {
                            return samples_dir;
                          },
                          type: "table",
                          get selected() {
                            return get($0);
                          },
                          index: i,
                          get root() {
                            return root();
                          }
                        }));
                      });
                    }
                    append($$anchor7, fragment_9);
                  });
                  reset(td);
                  template_effect(() => {
                    set_style(td, `max-width: ${get(component_name) === "textbox" ? "35ch" : "auto"}`);
                    set_class(td, 1, clsx(get(component_name)), "svelte-16f20a1");
                  });
                  append($$anchor6, td);
                };
                if_block(node_8, ($$render) => {
                  if (get(component_name) !== void 0) $$render(consequent_4);
                });
              }
              append($$anchor5, fragment_8);
            });
            reset(tr_1);
            event("click", tr_1, () => {
              value(i + get(page) * samples_per_page());
              onclick()({ index: value(), value: get(sample_row) });
              onselect()({ index: value(), value: get(selected_samples)[i] });
            });
            event("mouseenter", tr_1, () => handle_mouseenter(i));
            event("mouseleave", tr_1, () => handle_mouseleave());
            append($$anchor4, tr_1);
          });
          reset(tbody);
          reset(table);
          reset(div_1);
          append($$anchor3, div_1);
        };
        if_block(
          node_7,
          ($$render) => {
            if (get(selected_samples), untrack(() => get(selected_samples).length > 0)) $$render(consequent_5);
          },
          true
        );
      }
      append($$anchor2, fragment_7);
    };
    if_block(node, ($$render) => {
      if (get(gallery)) $$render(consequent_3);
      else $$render(alternate_1, false);
    });
  }
  var node_11 = sibling(node, 2);
  {
    var consequent_7 = ($$anchor2) => {
      var div_2 = root_17();
      var node_12 = sibling(child(div_2));
      each(node_12, 1, () => get(visible_pages), index, ($$anchor3, visible_page) => {
        var fragment_10 = comment();
        var node_13 = first_child(fragment_10);
        {
          var consequent_6 = ($$anchor4) => {
            var div_3 = root_19();
            append($$anchor4, div_3);
          };
          var alternate_2 = ($$anchor4) => {
            var button_1 = root_20();
            let classes;
            var text_1 = child(button_1, true);
            reset(button_1);
            template_effect(() => {
              classes = set_class(button_1, 1, "svelte-16f20a1", null, classes, { "current-page": get(page) === get(visible_page) });
              set_text(text_1, get(visible_page) + 1);
            });
            event("click", button_1, () => set(page, get(visible_page)));
            append($$anchor4, button_1);
          };
          if_block(node_13, ($$render) => {
            if (get(visible_page) === -1) $$render(consequent_6);
            else $$render(alternate_2, false);
          });
        }
        append($$anchor3, fragment_10);
      });
      reset(div_2);
      append($$anchor2, div_2);
    };
    if_block(node_11, ($$render) => {
      if (get(paginate)) $$render(consequent_7);
    });
  }
  append($$anchor, fragment);
  pop();
}
var root_2 = from_html(`<div class="label svelte-bnxc4d"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" width="1em" height="1em" preserveAspectRatio="xMidYMid meet" viewBox="0 0 32 32" class="svelte-bnxc4d"><path fill="currentColor" d="M10 6h18v2H10zm0 18h18v2H10zm0-9h18v2H10zm-6 0h2v2H4zm0-9h2v2H4zm0 18h2v2H4z"></path></svg> </div>`);
var root_1 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let samples = user_derived(() => gradio.props.samples ?? []);
  Block($$anchor, {
    get visible() {
      return gradio.shared.visible;
    },
    padding: false,
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
    allow_overflow: false,
    container: false,
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      {
        var consequent = ($$anchor3) => {
          var div = root_2();
          var text = sibling(child(div));
          reset(div);
          template_effect(() => set_text(text, ` ${(gradio.shared.label || "Examples") ?? ""}`));
          append($$anchor3, div);
        };
        if_block(node, ($$render) => {
          if (gradio.shared.show_label) $$render(consequent);
        });
      }
      var node_1 = sibling(node, 2);
      Dataset(node_1, spread_props(
        {
          onclick: (d) => (gradio.props.value = d.index, gradio.dispatch("click", gradio.props.value)),
          onselect: (data) => gradio.dispatch("select", data),
          get load_component() {
            return gradio.shared.load_component;
          },
          get samples() {
            return get(samples);
          }
        },
        () => gradio.props
      ));
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=_PE2j10l.js.map
