import { S as ShaderStore } from "./f5NiF4Sn.js";
import "./RvoTXknD.js";
import "./CaXKuKNR.js";
import "./CsIa_EcK.js";
const name = "hdrIrradianceFilteringPixelShader";
const shader = `#include<helperFunctions>
#include<importanceSampling>
#include<pbrBRDFFunctions>
#include<hdrFilteringFunctions>
uniform samplerCube inputTexture;
#ifdef IBL_CDF_FILTERING
uniform sampler2D icdfTexture;
#endif
uniform vec2 vFilteringInfo;uniform float hdrScale;varying vec3 direction;void main() {vec3 color=irradiance(inputTexture,direction,vFilteringInfo,0.0,vec3(1.0),direction
#ifdef IBL_CDF_FILTERING
,icdfTexture
#endif
);gl_FragColor=vec4(color*hdrScale,1.0);}`;
if (!ShaderStore.ShadersStore[name]) {
  ShaderStore.ShadersStore[name] = shader;
}
const hdrIrradianceFilteringPixelShader = { name, shader };
export {
  hdrIrradianceFilteringPixelShader
};
//# sourceMappingURL=D_RwE03s.js.map
