import { S as ShaderStore } from "./f5NiF4Sn.js";
const name = "envShadowGroundVertexShader";
const shader = `attribute position: vec3f;attribute uv: vec2f;uniform viewProjection: mat4x4f;uniform worldViewProjection: mat4x4f;varying vUV: vec2f;@vertex
fn main(input : VertexInputs)->FragmentInputs {vertexOutputs.position=uniforms.worldViewProjection*vec4f(input.position,1.0);vertexOutputs.vUV=input.uv;}`;
if (!ShaderStore.ShadersStoreWGSL[name]) {
  ShaderStore.ShadersStoreWGSL[name] = shader;
}
const envShadowGroundVertexShaderWGSL = { name, shader };
export {
  envShadowGroundVertexShaderWGSL
};
//# sourceMappingURL=wtC4TvsK.js.map
