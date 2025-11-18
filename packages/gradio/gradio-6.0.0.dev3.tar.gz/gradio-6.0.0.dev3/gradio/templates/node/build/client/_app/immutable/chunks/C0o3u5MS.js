import { S as ShaderStore } from "./f5NiF4Sn.js";
const name = "passPixelShader";
const shader = `varying vec2 vUV;uniform sampler2D textureSampler;
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=texture2D(textureSampler,vUV);}`;
if (!ShaderStore.ShadersStore[name]) {
  ShaderStore.ShadersStore[name] = shader;
}
const passPixelShader = { name, shader };
export {
  passPixelShader
};
//# sourceMappingURL=C0o3u5MS.js.map
