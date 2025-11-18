import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, c as from_html, d as child, u as deep_read_state, y as untrack, s as sibling, r as reset, b as append, o as pop, t as template_effect, D as comment, v as first_child, g as set_text, k as get, z as event, J as state, L as proxy, M as user_effect, j as set, A as user_derived } from "./DEzry6cj.js";
import { p as prop, i as if_block, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { t as each, v as index, a as set_class, p as set_style, s as set_attribute, w as set_value, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { i as init } from "./DB0xzveP.js";
import { L as LineChart } from "./BvRB_Kyc.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { E as Empty } from "./B-xg5Dhl.js";
var root_1$1 = from_html(`<h2 data-testid="label-output-value"> </h2>`);
var root_3 = from_html(`<button><div class="inner-wrap svelte-g2cwl3"><meter aria-valuemin="0" aria-valuemax="100" class="bar svelte-g2cwl3" min="0" max="1"></meter> <dl class="label svelte-g2cwl3"><dt class="text svelte-g2cwl3"> </dt> <div class="line svelte-g2cwl3"></div> <dd class="confidence svelte-g2cwl3"> </dd></dl></div></button>`);
var root = from_html(`<div class="container svelte-g2cwl3"><!> <!></div>`);
function Label($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 8);
  const dispatch = createEventDispatcher();
  let color = prop($$props, "color", 8, void 0);
  let selectable = prop($$props, "selectable", 8, false);
  let show_heading = prop($$props, "show_heading", 8, true);
  function get_aria_referenceable_id(elem_id) {
    return elem_id.replace(/\s/g, "-");
  }
  init();
  var div = root();
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      var h2 = root_1$1();
      let classes;
      let styles;
      var text = child(h2, true);
      reset(h2);
      template_effect(() => {
        classes = set_class(h2, 1, "output-class svelte-g2cwl3", null, classes, { "no-confidence": !("confidences" in value()) });
        styles = set_style(h2, "", styles, { "background-color": color() || "transparent" });
        set_text(text, (deep_read_state(value()), untrack(() => value().label)));
      });
      append($$anchor2, h2);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(show_heading()), deep_read_state(value()), untrack(() => show_heading() || !value().confidences)) $$render(consequent);
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent_1 = ($$anchor2) => {
      var fragment = comment();
      var node_2 = first_child(fragment);
      each(
        node_2,
        1,
        () => (deep_read_state(value()), untrack(() => value().confidences)),
        index,
        ($$anchor3, confidence_set, i) => {
          var button = root_3();
          let classes_1;
          var div_1 = child(button);
          var meter = child(div_1);
          var dl = sibling(meter, 2);
          var dt = child(dl);
          var text_1 = child(dt, true);
          reset(dt);
          var dd = sibling(dt, 4);
          var text_2 = child(dd);
          reset(dd);
          reset(dl);
          reset(div_1);
          reset(button);
          template_effect(
            ($0, $1, $2, $3) => {
              classes_1 = set_class(button, 1, "confidence-set group svelte-g2cwl3", null, classes_1, { selectable: selectable() });
              set_attribute(button, "data-testid", (get(confidence_set), untrack(() => `${get(confidence_set).label}-confidence-set`)));
              set_attribute(meter, "aria-labelledby", $0);
              set_attribute(meter, "aria-label", (get(confidence_set), untrack(() => get(confidence_set).label)));
              set_attribute(meter, "aria-valuenow", $1);
              set_value(meter, (get(confidence_set), untrack(() => get(confidence_set).confidence)));
              set_style(meter, `width: ${(get(confidence_set), untrack(() => get(confidence_set).confidence * 100)) ?? ""}%; background: var(--stat-background-fill);
						`);
              set_attribute(dt, "id", $2);
              set_text(text_1, (get(confidence_set), untrack(() => get(confidence_set).label)));
              set_text(text_2, `${$3 ?? ""}%`);
            },
            [
              () => (get(confidence_set), untrack(() => get_aria_referenceable_id(`meter-text-${get(confidence_set).label}`))),
              () => (get(confidence_set), untrack(() => Math.round(get(confidence_set).confidence * 100))),
              () => (get(confidence_set), untrack(() => get_aria_referenceable_id(`meter-text-${get(confidence_set).label}`))),
              () => (get(confidence_set), untrack(() => Math.round(get(confidence_set).confidence * 100)))
            ]
          );
          event("click", button, () => {
            dispatch("select", { index: i, value: get(confidence_set).label });
          });
          append($$anchor3, button);
        }
      );
      append($$anchor2, fragment);
    };
    if_block(node_1, ($$render) => {
      if (deep_read_state(value()), untrack(() => typeof value() === "object" && value().confidences)) $$render(consequent_1);
    });
  }
  reset(div);
  append($$anchor, div);
  pop();
}
var root_1 = from_html(`<!> <!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let old_value = state(proxy(gradio.props.value));
  let _label = user_derived(() => gradio.props.value.label);
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
    }
  });
  Block($$anchor, {
    test_id: "label",
    get visible() {
      return gradio.shared.visible;
    },
    get elem_id() {
      return gradio.shared.elem_id;
    },
    get elem_classes() {
      return gradio.shared.elem_classes;
    },
    get container() {
      return gradio.shared.container;
    },
    get scale() {
      return gradio.shared.scale;
    },
    get min_width() {
      return gradio.shared.min_width;
    },
    padding: false,
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = root_1();
      var node = first_child(fragment_1);
      Static(node, spread_props(
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
      var node_1 = sibling(node, 2);
      {
        var consequent = ($$anchor3) => {
          {
            let $0 = user_derived(() => gradio.shared.label || gradio.i18n("label.label"));
            let $1 = user_derived(() => gradio.shared.container === false);
            let $2 = user_derived(() => gradio.props.show_heading === true);
            BlockLabel($$anchor3, {
              get Icon() {
                return LineChart;
              },
              get label() {
                return get($0);
              },
              get disable() {
                return get($1);
              },
              get float() {
                return get($2);
              }
            });
          }
        };
        if_block(node_1, ($$render) => {
          if (gradio.shared.show_label) $$render(consequent);
        });
      }
      var node_2 = sibling(node_1, 2);
      {
        var consequent_1 = ($$anchor3) => {
          Label($$anchor3, {
            get selectable() {
              return gradio.props._selectable;
            },
            get value() {
              return gradio.props.value;
            },
            get color() {
              return gradio.props.color;
            },
            get show_heading() {
              return gradio.props.show_heading;
            },
            $$events: { select: ({ detail }) => gradio.dispatch("select", detail) }
          });
        };
        var alternate = ($$anchor3) => {
          Empty($$anchor3, {
            unpadded_box: true,
            children: ($$anchor4, $$slotProps2) => {
              LineChart($$anchor4);
            },
            $$slots: { default: true }
          });
        };
        if_block(node_2, ($$render) => {
          if (get(_label) !== void 0 && get(_label) !== null) $$render(consequent_1);
          else $$render(alternate, false);
        });
      }
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  Label as BaseLabel,
  Index as default
};
//# sourceMappingURL=BCmW2XcH.js.map
