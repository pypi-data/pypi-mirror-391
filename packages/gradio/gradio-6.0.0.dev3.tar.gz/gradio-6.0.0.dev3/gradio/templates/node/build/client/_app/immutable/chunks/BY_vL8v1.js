import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, _ as getContext, I as onMount, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, k as get, K as tick, n as legacy_pre_effect_reset, c as from_html, d as child, D as comment, v as first_child, b as append, x as derived_safe_equal, r as reset, t as template_effect, y as untrack, o as pop } from "./DEzry6cj.js";
import { s as slot } from "./DX-MI-YE.js";
import { p as prop, a as store_get, e as setup_stores, r as rest_props } from "./DUftb7my.js";
import { L as BaseColumn, s as set_attribute, a as set_class, p as set_style, G as Gradio } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { i as init } from "./DB0xzveP.js";
import { T as TABS } from "./CZRd2l0M.js";
var root = from_html(`<div role="tabpanel"><!></div>`);
function TabItem($$anchor, $$props) {
  push($$props, false);
  const $selected_tab_index = () => store_get(selected_tab_index, "$selected_tab_index", $$stores);
  const $selected_tab = () => store_get(selected_tab, "$selected_tab", $$stores);
  const [$$stores, $$cleanup] = setup_stores();
  const props_json = mutable_source();
  let elem_id = prop($$props, "elem_id", 8, "");
  let elem_classes = prop($$props, "elem_classes", 24, () => []);
  let label = prop($$props, "label", 8);
  let id = prop($$props, "id", 24, () => ({}));
  let visible = prop($$props, "visible", 8);
  let interactive = prop($$props, "interactive", 8);
  let order = prop($$props, "order", 8);
  let scale = prop($$props, "scale", 8);
  const dispatch = createEventDispatcher();
  const {
    register_tab,
    unregister_tab,
    selected_tab,
    selected_tab_index
  } = getContext(TABS);
  let tab_index = mutable_source();
  function _register_tab(obj, order2) {
    obj = JSON.parse(obj);
    return register_tab(obj, order2);
  }
  onMount(() => {
    return () => unregister_tab({ label: label(), id: id(), elem_id: elem_id() }, order());
  });
  legacy_pre_effect(
    () => (deep_read_state(label()), deep_read_state(id()), deep_read_state(elem_id()), deep_read_state(visible()), deep_read_state(interactive()), deep_read_state(scale())),
    () => {
      set(props_json, JSON.stringify({
        label: label(),
        id: id(),
        elem_id: elem_id(),
        visible: visible(),
        interactive: interactive(),
        scale: scale()
      }));
    }
  );
  legacy_pre_effect(() => (get(props_json), deep_read_state(order())), () => {
    set(tab_index, _register_tab(get(props_json), order()));
  });
  legacy_pre_effect(
    () => ($selected_tab_index(), get(tab_index), deep_read_state(label())),
    () => {
      $selected_tab_index() === get(tab_index) && tick().then(() => dispatch("select", { value: label(), index: get(tab_index) }));
    }
  );
  legacy_pre_effect_reset();
  init();
  var div = root();
  let classes;
  let styles;
  var node = child(div);
  {
    let $0 = derived_safe_equal(() => scale() >= 1 ? scale() : null);
    BaseColumn(node, {
      get scale() {
        return get($0);
      },
      children: ($$anchor2, $$slotProps) => {
        var fragment = comment();
        var node_1 = first_child(fragment);
        slot(node_1, $$props, "default", {}, null);
        append($$anchor2, fragment);
      },
      $$slots: { default: true }
    });
  }
  reset(div);
  template_effect(
    ($0) => {
      set_attribute(div, "id", elem_id());
      classes = set_class(div, 1, `tabitem ${$0 ?? ""}`, "svelte-dmtrd3", classes, { "grow-children": scale() >= 1 });
      styles = set_style(div, "", styles, {
        display: $selected_tab() === id() && visible() !== false ? "flex" : "none",
        "flex-grow": scale()
      });
    },
    [
      () => (deep_read_state(elem_classes()), untrack(() => elem_classes().join(" ")))
    ]
  );
  append($$anchor, div);
  pop();
  $$cleanup();
}
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  TabItem($$anchor, {
    get elem_id() {
      return gradio.shared.elem_id;
    },
    get elem_classes() {
      return gradio.shared.elem_classes;
    },
    get label() {
      return gradio.shared.label;
    },
    get visible() {
      return gradio.shared.visible;
    },
    get interactive() {
      return gradio.shared.interactive;
    },
    get id() {
      return gradio.props.id;
    },
    get order() {
      return gradio.props.order;
    },
    get scale() {
      return gradio.props.scale;
    },
    $$events: { select: ({ detail }) => gradio.dispatch("select", detail) },
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = comment();
      var node = first_child(fragment_1);
      slot(node, $$props, "default", {}, null);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  TabItem as BaseTabItem,
  Index as default
};
//# sourceMappingURL=BY_vL8v1.js.map
