import { S as ShaderStore } from "./f5NiF4Sn.js";
import "./CFcrUK-J.js";
const name = "rgbdEncodePixelShader";
const shader = `varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=toRGBD(textureSample(textureSampler,textureSamplerSampler,input.vUV).rgb);}`;
if (!ShaderStore.ShadersStoreWGSL[name]) {
  ShaderStore.ShadersStoreWGSL[name] = shader;
}
const rgbdEncodePixelShaderWGSL = { name, shader };
export {
  rgbdEncodePixelShaderWGSL
};
//# sourceMappingURL=z89kcPSh.js.map
