import "./9B4_veAf.js";
import { p as push, M as user_effect, N as onDestroy, o as pop } from "./DEzry6cj.js";
import { r as rest_props } from "./DUftb7my.js";
import { G as Gradio } from "./DXi4jxVF.js";
function Index($$anchor, $$props) {
  push($$props, true);
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  let interval = void 0;
  user_effect(() => {
    if (interval) clearInterval(interval);
    if (gradio.props.active) {
      interval = setInterval(
        () => {
          if (document.visibilityState === "visible") {
            gradio.dispatch("tick");
          }
        },
        gradio.props.value * 1e3
      );
    }
  });
  onDestroy(() => {
    if (interval) clearInterval(interval);
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=Cv-odeKu.js.map
