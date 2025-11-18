import { d as dev } from './index4-DpKVuxl4.js';
import './browser-fallback-CYSLhaFr.js';

async function load({ request }) {
  const server = request.headers.get("x-gradio-server") || "http://127.0.0.1:7860";
  const port = request.headers.get("x-gradio-port") || "7860";
  const local_dev_mode = request.headers.get("x-gradio-local-dev-mode") || dev ? "true" : void 0;
  const accept_language = request.headers.get("accept-language") || "en";
  return {
    server,
    port,
    local_dev_mode,
    accept_language
  };
}

var _page_server_ts = /*#__PURE__*/Object.freeze({
  __proto__: null,
  load: load
});

const index = 2;
let component_cache;
const component = async () => component_cache ??= (await import('./_page.svelte-BjD6lkEd.js')).default;
const universal = {
  "ssr": false,
  "load": null
};
const universal_id = "src/routes/[...catchall]/+page.ts";
const server_id = "src/routes/[...catchall]/+page.server.ts";
const imports = ["_app/immutable/nodes/2.CmU23AS-.js","_app/immutable/chunks/DXi4jxVF.js","_app/immutable/chunks/DUftb7my.js","_app/immutable/chunks/DEzry6cj.js","_app/immutable/chunks/DdkXqxbl.js","_app/immutable/chunks/9B4_veAf.js","_app/immutable/chunks/BAp-OWo-.js","_app/immutable/chunks/DB0xzveP.js","_app/immutable/chunks/CW83eULi.js","_app/immutable/chunks/DX-MI-YE.js"];
const stylesheets = ["_app/immutable/assets/2.DSZTpYri.css","_app/immutable/assets/Index.z1Q1BLUi.css","_app/immutable/assets/Index.SFJBH4GU.css","_app/immutable/assets/AudioPlayer.CDTZSNZJ.css","_app/immutable/assets/Example.CbYyX-DE.css","_app/immutable/assets/Upload.CkLifYXt.css","_app/immutable/assets/InteractiveAudio.BkTyVXRP.css","_app/immutable/assets/Index.KiAI3qf7.css","_app/immutable/assets/Example.BaaVYcTJ.css","_app/immutable/assets/Checkbox.v4NVC93a.css","_app/immutable/assets/Example.aemMVOi4.css","_app/immutable/assets/Index.C_9LVFgp.css","_app/immutable/assets/Example.Cr7N_YHz.css","_app/immutable/assets/Code.B_2QfHa0.css","_app/immutable/assets/Example.DPDBEP7R.css","_app/immutable/assets/Index.faAaJXRt.css","_app/immutable/assets/Example.Iq6Y1YEN.css","_app/immutable/assets/Index.CruQM7I9.css","_app/immutable/assets/Index.C9EBQKP4.css","_app/immutable/assets/Example.Cn68kxMG.css","_app/immutable/assets/Dropdown.WahRM7My.css","_app/immutable/assets/Index.C1WKuLXm.css","_app/immutable/assets/Example.D4W_iyXU.css","_app/immutable/assets/Index.CdC8Zumz.css","_app/immutable/assets/Index.CiSEGdRh.css","_app/immutable/assets/Example.B4-DUzTq.css","_app/immutable/assets/FileUpload.DixEntvj.css","_app/immutable/assets/Example.TZ_g5uyS.css","_app/immutable/assets/Index.B8SWaQIt.css","_app/immutable/assets/Video.Ii87aI7h.css","_app/immutable/assets/Gallery.4Q949fZj.css","_app/immutable/assets/Example.CeI2SKn-.css","_app/immutable/assets/Index.CN6cETkQ.css","_app/immutable/assets/Index.CP9g_Xcx.css","_app/immutable/assets/Example.Ch1jJlud.css","_app/immutable/assets/Index.DfqJuaiU.css","_app/immutable/assets/Example.B6_5FSub.css","_app/immutable/assets/ImageUploader.DpCMavgB.css","_app/immutable/assets/Example.Fxea8K5o.css","_app/immutable/assets/Example.CzZrT1Fw.css","_app/immutable/assets/Index.B-7HbVC7.css","_app/immutable/assets/JSON.DShdQ2eF.css","_app/immutable/assets/Example.Dc-SgtDH.css","_app/immutable/assets/Index.B9F8Mxmi.css","_app/immutable/assets/Example.DW7nfzdH.css","_app/immutable/assets/Index.CvDaX1Zt.css","_app/immutable/assets/Model3D.CeJUxvsm.css","_app/immutable/assets/Example.acVGYfNi.css","_app/immutable/assets/Index.Cq3-9UCk.css","_app/immutable/assets/Example.TBCHg6Rz.css","_app/immutable/assets/Index.BGQbMMbV.css","_app/immutable/assets/Index.C8sj9vD6.css","_app/immutable/assets/Example.WCM3sPJO.css","_app/immutable/assets/Index.DuulgjS0.css","_app/immutable/assets/Example.DNdIRtpk.css","_app/immutable/assets/Index.CWaMU9BY.css","_app/immutable/assets/Example.DIVYDZzk.css","_app/immutable/assets/Index.D_WH52UF.css","_app/immutable/assets/Index.BaylBtTi.css","_app/immutable/assets/Index.BNaD7NMv.css","_app/immutable/assets/Index.BMBhLAvj.css","_app/immutable/assets/Example.DIaUx3h9.css","_app/immutable/assets/Index.BcfSzwkn.css","_app/immutable/assets/Walkthrough.CqIjWApt.css","_app/immutable/assets/Index.CIrlx8XY.css","_app/immutable/assets/Index.BR163DB2.css","_app/immutable/assets/Index.Ci5QmlEg.css","_app/immutable/assets/Example.DWE_gt69.css","_app/immutable/assets/index.C8ybR3Sf.css","_app/immutable/assets/Example.BRolBDk-.css","_app/immutable/assets/Index.Byzu8nVj.css"];
const fonts = [];

export { component, fonts, imports, index, _page_server_ts as server, server_id, stylesheets, universal, universal_id };
//# sourceMappingURL=2-D3mEGBAY.js.map
