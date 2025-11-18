const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./f5NiF4Sn.js","./DUftb7my.js","./DEzry6cj.js","./DdkXqxbl.js"])))=>i.map(i=>d[i]);
import { p as prop, b as bind_this, _ as __vitePreload } from "./DUftb7my.js";
import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, I as onMount, i as legacy_pre_effect, j as set, m as mutable_source, u as deep_read_state, k as get, n as legacy_pre_effect_reset, c as from_html, b as append, o as pop } from "./DEzry6cj.js";
import { b as bind_prop } from "./CswR_hUw.js";
import { i as init } from "./DB0xzveP.js";
var root = from_html(`<canvas></canvas>`);
function Canvas3D($$anchor, $$props) {
  push($$props, false);
  const url = mutable_source();
  let BABYLON_VIEWER;
  let value = prop($$props, "value", 8);
  let display_mode = prop($$props, "display_mode", 8);
  let clear_color = prop($$props, "clear_color", 8);
  let camera_position = prop($$props, "camera_position", 8);
  let zoom_speed = prop($$props, "zoom_speed", 8);
  let pan_speed = prop($$props, "pan_speed", 8);
  let canvas = mutable_source();
  let viewer;
  let viewerDetails;
  let mounted = mutable_source(false);
  onMount(() => {
    const initViewer = async () => {
      BABYLON_VIEWER = await __vitePreload(() => import("./f5NiF4Sn.js").then((n) => n.cq), true ? __vite__mapDeps([0,1,2,3]) : void 0, import.meta.url);
      BABYLON_VIEWER.CreateViewerForCanvas(get(canvas), {
        clearColor: clear_color(),
        useRightHandedSystem: true,
        animationAutoPlay: true,
        cameraAutoOrbit: { enabled: false },
        onInitialized: (details) => {
          viewerDetails = details;
        }
      }).then((promiseViewer) => {
        viewer = promiseViewer;
        set(mounted, true);
      });
    };
    initViewer();
    return () => {
      viewer?.dispose();
    };
  });
  function setRenderingMode(pointsCloud, wireframe) {
    viewerDetails.scene.forcePointsCloud = pointsCloud;
    viewerDetails.scene.forceWireframe = wireframe;
  }
  function load_model(url2) {
    if (viewer) {
      if (url2) {
        viewer.loadModel(url2, { pluginOptions: { obj: { importVertexColors: true } } }).then(() => {
          if (display_mode() === "point_cloud") {
            setRenderingMode(true, false);
          } else if (display_mode() === "wireframe") {
            setRenderingMode(false, true);
          } else {
            update_camera(camera_position(), zoom_speed(), pan_speed());
          }
        });
      } else {
        viewer.resetModel();
      }
    }
  }
  function update_camera(camera_position2, zoom_speed2, pan_speed2) {
    const camera = viewerDetails.camera;
    if (camera_position2[0] !== null) {
      camera.alpha = camera_position2[0] * Math.PI / 180;
    }
    if (camera_position2[1] !== null) {
      camera.beta = camera_position2[1] * Math.PI / 180;
    }
    if (camera_position2[2] !== null) {
      camera.radius = camera_position2[2];
    }
    camera.lowerRadiusLimit = 0.1;
    const updateCameraSensibility = () => {
      camera.wheelPrecision = 250 / (camera.radius * zoom_speed2);
      camera.panningSensibility = 1e4 * pan_speed2 / camera.radius;
    };
    updateCameraSensibility();
    camera.onAfterCheckInputsObservable.add(updateCameraSensibility);
  }
  function reset_camera_position() {
    if (viewerDetails) {
      viewer.resetCamera();
    }
  }
  legacy_pre_effect(() => deep_read_state(value()), () => {
    set(url, value().url);
  });
  legacy_pre_effect(() => (get(mounted), get(url)), () => {
    get(mounted) && load_model(get(url));
  });
  legacy_pre_effect_reset();
  var $$exports = { update_camera, reset_camera_position };
  init();
  var canvas_1 = root();
  bind_this(canvas_1, ($$value) => set(canvas, $$value), () => get(canvas));
  append($$anchor, canvas_1);
  bind_prop($$props, "update_camera", update_camera);
  bind_prop($$props, "reset_camera_position", reset_camera_position);
  return pop($$exports);
}
export {
  Canvas3D as default
};
//# sourceMappingURL=BAZBy-k2.js.map
