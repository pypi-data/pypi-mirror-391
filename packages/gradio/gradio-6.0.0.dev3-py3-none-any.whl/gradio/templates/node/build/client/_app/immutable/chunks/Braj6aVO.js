import { l as listen, w as without_reactive_context } from "./DEzry6cj.js";
function bind_window_size(type, set) {
  listen(window, ["resize"], () => without_reactive_context(() => set(window[type])));
}
export {
  bind_window_size as b
};
//# sourceMappingURL=Braj6aVO.js.map
