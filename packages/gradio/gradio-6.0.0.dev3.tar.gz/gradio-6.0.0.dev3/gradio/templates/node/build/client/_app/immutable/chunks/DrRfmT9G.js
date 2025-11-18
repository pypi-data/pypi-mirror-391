import "./9B4_veAf.js";
import { p as push, q as createEventDispatcher, I as onMount, i as legacy_pre_effect, k as get, m as mutable_source, j as set, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, s as sibling, r as reset, t as template_effect, z as event, b as append, o as pop, v as first_child, D as comment } from "./DEzry6cj.js";
import { p as prop, b as bind_this, r as rest_props, s as spread_props, i as if_block } from "./DUftb7my.js";
import { s as slot } from "./DX-MI-YE.js";
import { a as set_class, s as set_attribute, p as set_style, G as Gradio, g as Static, L as BaseColumn } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { i as init } from "./DB0xzveP.js";
var root$1 = from_html(`<div><button class="toggle-button svelte-1uruprb" aria-label="Toggle Sidebar"><div class="chevron svelte-1uruprb"><span class="chevron-left svelte-1uruprb"></span></div></button> <div class="sidebar-content svelte-1uruprb"><!></div></div>`);
function Sidebar($$anchor, $$props) {
  push($$props, false);
  const _elem_classes = mutable_source();
  const dispatch = createEventDispatcher();
  let open = prop($$props, "open", 12, true);
  let width = prop($$props, "width", 8);
  let position = prop($$props, "position", 8, "left");
  let elem_classes = prop($$props, "elem_classes", 24, () => []);
  let elem_id = prop($$props, "elem_id", 8, "");
  let mounted = mutable_source(false);
  let _open = mutable_source(false);
  let sidebar_div = mutable_source();
  let overlap_amount = 0;
  let width_css = typeof width() === "number" ? `${width()}px` : width();
  let prefersReducedMotion = mutable_source();
  function check_overlap() {
    if (!get(sidebar_div).closest(".wrap")) return;
    const parent_rect = get(sidebar_div).closest(".wrap")?.getBoundingClientRect();
    if (!parent_rect) return;
    const sidebar_rect = get(sidebar_div).getBoundingClientRect();
    const available_space = position() === "left" ? parent_rect.left : window.innerWidth - parent_rect.right;
    overlap_amount = Math.max(0, sidebar_rect.width - available_space + 30);
  }
  onMount(() => {
    get(sidebar_div).closest(".wrap")?.classList.add("sidebar-parent");
    check_overlap();
    window.addEventListener("resize", check_overlap);
    const update_parent_overlap = () => {
      document.documentElement.style.setProperty("--overlap-amount", `${overlap_amount}px`);
    };
    update_parent_overlap();
    set(mounted, true);
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    set(prefersReducedMotion, mediaQuery.matches);
    const updateMotionPreference = (e) => {
      set(prefersReducedMotion, e.matches);
    };
    mediaQuery.addEventListener("change", updateMotionPreference);
    return () => {
      window.removeEventListener("resize", check_overlap);
      mediaQuery.removeEventListener("change", updateMotionPreference);
    };
  });
  legacy_pre_effect(() => (get(mounted), deep_read_state(open())), () => {
    if (get(mounted)) set(_open, open());
  });
  legacy_pre_effect(() => deep_read_state(elem_classes()), () => {
    set(_elem_classes, elem_classes()?.join(" ") || "");
  });
  legacy_pre_effect_reset();
  init();
  var div = root$1();
  let classes;
  var button = child(div);
  var div_1 = sibling(button, 2);
  var node = child(div_1);
  slot(node, $$props, "default", {}, null);
  reset(div_1);
  reset(div);
  bind_this(div, ($$value) => set(sidebar_div, $$value), () => get(sidebar_div));
  template_effect(() => {
    classes = set_class(div, 1, `sidebar ${get(_elem_classes) ?? ""}`, "svelte-1uruprb", classes, {
      open: get(_open),
      right: position() === "right",
      "reduce-motion": get(prefersReducedMotion)
    });
    set_attribute(div, "id", elem_id());
    set_style(div, `width: ${width_css ?? ""}; ${position() ?? ""}: calc(${width_css ?? ""} * -1)`);
  });
  event("click", button, () => {
    set(_open, !get(_open));
    open(get(_open));
    if (get(_open)) {
      dispatch("expand");
    } else {
      dispatch("collapse");
    }
  });
  append($$anchor, div);
  pop();
}
var root = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  var fragment = root();
  var node = first_child(fragment);
  Static(node, spread_props(
    {
      get autoscroll() {
        return gradio.shared.autoscroll;
      },
      get i18n() {
        return gradio.i18n;
      }
    },
    () => gradio.shared.loading_status
  ));
  var node_1 = sibling(node, 2);
  {
    var consequent = ($$anchor2) => {
      Sidebar($$anchor2, {
        get width() {
          return gradio.props.width;
        },
        get elem_classes() {
          return gradio.shared.elem_classes;
        },
        get elem_id() {
          return gradio.shared.elem_id;
        },
        get open() {
          return gradio.props.open;
        },
        set open($$value) {
          gradio.props.open = $$value;
        },
        get position() {
          return gradio.props.position;
        },
        set position($$value) {
          gradio.props.position = $$value;
        },
        $$events: {
          expand: () => gradio.dispatch("expand"),
          collapse: () => gradio.dispatch("collapse")
        },
        children: ($$anchor3, $$slotProps) => {
          BaseColumn($$anchor3, {
            children: ($$anchor4, $$slotProps2) => {
              var fragment_3 = comment();
              var node_2 = first_child(fragment_3);
              slot(node_2, $$props, "default", {}, null);
              append($$anchor4, fragment_3);
            },
            $$slots: { default: true }
          });
        },
        $$slots: { default: true }
      });
    };
    if_block(node_1, ($$render) => {
      if (gradio.shared.visible) $$render(consequent);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=DrRfmT9G.js.map
