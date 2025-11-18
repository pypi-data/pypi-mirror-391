const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./DNw39iJ7.js","./9B4_veAf.js","./DEzry6cj.js","./BAp-OWo-.js","./DXi4jxVF.js","./DUftb7my.js","./DdkXqxbl.js","./DB0xzveP.js","./CW83eULi.js","./DX-MI-YE.js","../assets/2.DSZTpYri.css","./BxirbyRx.js","../assets/BokehPlot.CZZY8n7d.css","./CuZnhSmJ.js","../assets/MatplotlibPlot.D6VqAjMk.css","./B9-xwDB1.js","./C7iqN3X7.js","./B5Kxxbk_.js","./CzSFdLC4.js","./CTO7spbL.js","./Ch2P6CyP.js","./B_xrbhEe.js","./QrCxtVsa.js","./DsLWYO-v.js","./Qrw4qHro.js","./Bs5oKbOs.js","./CykJO7CO.js","./DAbZ0KZY.js","./DLQrrtGG.js","./AYBC7juJ.js","../assets/AltairPlot.vOM03ldU.css"])))=>i.map(i=>d[i]);
import { _ as __vitePreload, i as if_block, c as component } from "./DUftb7my.js";
import "./9B4_veAf.js";
import { f as from_svg, b as append, p as push, M as user_effect, k as get, A as user_derived, y as untrack, j as set, J as state, D as comment, v as first_child, o as pop } from "./DEzry6cj.js";
import { k as key } from "./DssvUQ9s.js";
import { c as bubble_event } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { E as Empty } from "./B-xg5Dhl.js";
var root = from_svg(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--carbon" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" viewBox="0 0 32 32"><circle cx="20" cy="4" r="2" fill="currentColor"></circle><circle cx="8" cy="16" r="2" fill="currentColor"></circle><circle cx="28" cy="12" r="2" fill="currentColor"></circle><circle cx="11" cy="7" r="2" fill="currentColor"></circle><circle cx="16" cy="24" r="2" fill="currentColor"></circle><path fill="currentColor" d="M30 3.413L28.586 2L4 26.585V2H2v26a2 2 0 0 0 2 2h26v-2H5.413Z"></path></svg>`);
function Plot$2($$anchor) {
  var svg = root();
  append($$anchor, svg);
}
function Plot($$anchor, $$props) {
  push($$props, true);
  let PlotComponent = state(null);
  let loaded_plotly_css = state(false);
  let key$1 = state(0);
  const plotTypeMapping = {
    plotly: () => __vitePreload(() => import("./DNw39iJ7.js"), true ? __vite__mapDeps([0,1,2,3,4,5,6,7,8,9,10]) : void 0, import.meta.url),
    bokeh: () => __vitePreload(() => import("./BxirbyRx.js"), true ? __vite__mapDeps([11,1,2,3,4,5,6,7,8,9,10,12]) : void 0, import.meta.url),
    matplotlib: () => __vitePreload(() => import("./CuZnhSmJ.js"), true ? __vite__mapDeps([13,1,2,4,5,6,3,7,8,9,10,14]) : void 0, import.meta.url),
    altair: () => __vitePreload(() => import("./B9-xwDB1.js"), true ? __vite__mapDeps([15,1,2,5,6,4,3,7,8,9,10,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]) : void 0, import.meta.url)
  };
  let loadedPlotTypeMapping = {};
  const is_browser = typeof window !== "undefined";
  let value = user_derived(() => $$props.gradio.props.value);
  let _type = state(null);
  user_effect(() => {
    console.log("Plot value changed:", get(value));
    let type = get(value)?.type;
    untrack(() => {
      set(key$1, get(key$1) + 1);
      if (type !== get(_type)) {
        set(PlotComponent, null);
      }
      if (type && type in plotTypeMapping && is_browser) {
        if (loadedPlotTypeMapping[type]) {
          set(PlotComponent, loadedPlotTypeMapping[type], true);
        } else {
          plotTypeMapping[type]().then((module) => {
            set(PlotComponent, module.default, true);
            loadedPlotTypeMapping[type] = get(PlotComponent);
          });
        }
      }
      set(_type, type, true);
    });
    $$props.gradio.dispatch("change");
  });
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      var fragment_1 = comment();
      var node_1 = first_child(fragment_1);
      key(node_1, () => get(key$1), ($$anchor3) => {
        var fragment_2 = comment();
        var node_2 = first_child(fragment_2);
        component(node_2, () => get(PlotComponent), ($$anchor4, PlotComponent_1) => {
          PlotComponent_1($$anchor4, {
            get value() {
              return $$props.gradio.props.value;
            },
            colors: [],
            get theme_mode() {
              return $$props.gradio.props.theme_mode;
            },
            get show_label() {
              return $$props.gradio.shared.show_label;
            },
            get caption() {
              return $$props.gradio.props.caption;
            },
            get bokeh_version() {
              return $$props.gradio.props.bokeh_version;
            },
            get show_actions_button() {
              return $$props.gradio.props.show_actions_button;
            },
            get gradio() {
              return $$props.gradio;
            },
            get _selectable() {
              return $$props.gradio.props._selectable;
            },
            get x_lim() {
              return $$props.gradio.props.x_lim;
            },
            get loaded_plotly_css() {
              return get(loaded_plotly_css);
            },
            set loaded_plotly_css($$value) {
              set(loaded_plotly_css, $$value, true);
            },
            $$events: {
              select($$arg) {
                bubble_event.call(this, $$props, $$arg);
              }
            }
          });
        });
        append($$anchor3, fragment_2);
      });
      append($$anchor2, fragment_1);
    };
    var alternate = ($$anchor2) => {
      Empty($$anchor2, {
        unpadded_box: true,
        size: "large",
        children: ($$anchor3, $$slotProps) => {
          Plot$2($$anchor3);
        },
        $$slots: { default: true }
      });
    };
    if_block(node, ($$render) => {
      if ($$props.gradio.props.value && get(PlotComponent)) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
const Plot$1 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: Plot
}, Symbol.toStringTag, { value: "Module" }));
export {
  Plot$2 as P,
  Plot as a,
  Plot$1 as b
};
//# sourceMappingURL=BFXHQ9DL.js.map
