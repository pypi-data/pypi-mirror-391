import "./9B4_veAf.js";
import { p as push, E as next, F as text, t as template_effect, b as append, k as get, A as user_derived, o as pop, g as set_text } from "./DEzry6cj.js";
import { r as rest_props } from "./DUftb7my.js";
import { G as Gradio, f as Button } from "./DXi4jxVF.js";
function Index($$anchor, $$props) {
  push($$props, true);
  let _props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(_props);
  function handle_click() {
    gradio.dispatch("click");
  }
  {
    let $0 = user_derived(() => !gradio.shared.interactive);
    Button($$anchor, {
      get value() {
        return gradio.props.value;
      },
      get variant() {
        return gradio.props.variant;
      },
      get elem_id() {
        return gradio.shared.elem_id;
      },
      get elem_classes() {
        return gradio.shared.elem_classes;
      },
      get size() {
        return gradio.props.size;
      },
      get scale() {
        return gradio.props.scale;
      },
      get link() {
        return gradio.props.link;
      },
      get icon() {
        return gradio.props.icon;
      },
      get min_width() {
        return gradio.shared.min_width;
      },
      get visible() {
        return gradio.shared.visible;
      },
      get disabled() {
        return get($0);
      },
      $$events: { click: handle_click },
      children: ($$anchor2, $$slotProps) => {
        next();
        var text$1 = text();
        template_effect(() => set_text(text$1, gradio.props.value ?? ""));
        append($$anchor2, text$1);
      },
      $$slots: { default: true }
    });
  }
  pop();
}
export {
  Button as BaseButton,
  Index as default
};
//# sourceMappingURL=BpyQ6xj6.js.map
