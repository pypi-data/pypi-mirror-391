import { B as get_descriptor, C as teardown } from "./DEzry6cj.js";
function bind_prop(props, prop, value) {
  var desc = get_descriptor(props, prop);
  if (desc && desc.set) {
    props[prop] = value;
    teardown(() => {
      props[prop] = null;
    });
  }
}
export {
  bind_prop as b
};
//# sourceMappingURL=CswR_hUw.js.map
