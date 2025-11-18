import { S as ShaderStore } from "./f5NiF4Sn.js";
import "./CFcrUK-J.js";
import "./DITDjThH.js";
import "./BzRGPGbd.js";
const name = "hdrFilteringPixelShader";
const shader = `#include<helperFunctions>
#include<importanceSampling>
#include<pbrBRDFFunctions>
#include<hdrFilteringFunctions>
uniform alphaG: f32;var inputTextureSampler: sampler;var inputTexture: texture_cube<f32>;uniform vFilteringInfo: vec2f;uniform hdrScale: f32;varying direction: vec3f;@fragment
fn main(input: FragmentInputs)->FragmentOutputs {var color: vec3f=radiance(uniforms.alphaG,inputTexture,inputTextureSampler,input.direction,uniforms.vFilteringInfo);fragmentOutputs.color= vec4f(color*uniforms.hdrScale,1.0);}`;
if (!ShaderStore.ShadersStoreWGSL[name]) {
  ShaderStore.ShadersStoreWGSL[name] = shader;
}
const hdrFilteringPixelShaderWGSL = { name, shader };
export {
  hdrFilteringPixelShaderWGSL
};
//# sourceMappingURL=oEE6Z3WR.js.map
