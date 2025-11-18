import { S as ShaderStore } from "./f5NiF4Sn.js";
import "./C3XE5p5Y.js";
const name$1 = "kernelBlurVertex";
const shader$1 = `vertexOutputs.sampleCoord{X}=vertexOutputs.sampleCenter+uniforms.delta*KERNEL_OFFSET{X};`;
if (!ShaderStore.IncludesShadersStoreWGSL[name$1]) {
  ShaderStore.IncludesShadersStoreWGSL[name$1] = shader$1;
}
const name = "kernelBlurVertexShader";
const shader = `attribute position: vec2f;uniform delta: vec2f;varying sampleCenter: vec2f;
#include<kernelBlurVaryingDeclaration>[0..varyingCount]
#define CUSTOM_VERTEX_DEFINITIONS
@vertex
fn main(input : VertexInputs)->FragmentInputs {const madd: vec2f= vec2f(0.5,0.5);
#define CUSTOM_VERTEX_MAIN_BEGIN
vertexOutputs.sampleCenter=(input.position*madd+madd);
#include<kernelBlurVertex>[0..varyingCount]
vertexOutputs.position= vec4f(input.position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;
if (!ShaderStore.ShadersStoreWGSL[name]) {
  ShaderStore.ShadersStoreWGSL[name] = shader;
}
const kernelBlurVertexShaderWGSL = { name, shader };
export {
  kernelBlurVertexShaderWGSL
};
//# sourceMappingURL=BLB7Lesr.js.map
