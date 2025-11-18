import { S as ShaderStore } from "./f5NiF4Sn.js";
import "./RvoTXknD.js";
const name = "rgbdEncodePixelShader";
const shader = `varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=toRGBD(texture2D(textureSampler,vUV).rgb);}`;
if (!ShaderStore.ShadersStore[name]) {
  ShaderStore.ShadersStore[name] = shader;
}
const rgbdEncodePixelShader = { name, shader };
export {
  rgbdEncodePixelShader
};
//# sourceMappingURL=Sk4h6q8f.js.map
