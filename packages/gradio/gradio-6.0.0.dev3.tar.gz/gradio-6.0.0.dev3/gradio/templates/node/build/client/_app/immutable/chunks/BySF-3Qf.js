import { S as ShaderStore } from "./f5NiF4Sn.js";
import "./CFcrUK-J.js";
const name = "rgbdDecodePixelShader";
const shader = `varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=vec4f(fromRGBD(textureSample(textureSampler,textureSamplerSampler,input.vUV)),1.0);}`;
if (!ShaderStore.ShadersStoreWGSL[name]) {
  ShaderStore.ShadersStoreWGSL[name] = shader;
}
const rgbdDecodePixelShaderWGSL = { name, shader };
export {
  rgbdDecodePixelShaderWGSL
};
//# sourceMappingURL=BySF-3Qf.js.map
