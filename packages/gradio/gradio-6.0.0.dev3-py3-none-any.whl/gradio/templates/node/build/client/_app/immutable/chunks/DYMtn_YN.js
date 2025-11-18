import { S as ShaderStore } from "./f5NiF4Sn.js";
const name$2 = "fogVertexDeclaration";
const shader$2 = `#ifdef FOG
varying vFogDistance: vec3f;
#endif
`;
if (!ShaderStore.IncludesShadersStoreWGSL[name$2]) {
  ShaderStore.IncludesShadersStoreWGSL[name$2] = shader$2;
}
const name$1 = "fogVertex";
const shader$1 = `#ifdef FOG
#ifdef SCENE_UBO
vertexOutputs.vFogDistance=(scene.view*worldPos).xyz;
#else
vertexOutputs.vFogDistance=(uniforms.view*worldPos).xyz;
#endif
#endif
`;
if (!ShaderStore.IncludesShadersStoreWGSL[name$1]) {
  ShaderStore.IncludesShadersStoreWGSL[name$1] = shader$1;
}
const name = "logDepthVertex";
const shader = `#ifdef LOGARITHMICDEPTH
vertexOutputs.vFragmentDepth=1.0+vertexOutputs.position.w;vertexOutputs.position.z=log2(max(0.000001,vertexOutputs.vFragmentDepth))*uniforms.logarithmicDepthConstant;
#endif
`;
if (!ShaderStore.IncludesShadersStoreWGSL[name]) {
  ShaderStore.IncludesShadersStoreWGSL[name] = shader;
}
//# sourceMappingURL=DYMtn_YN.js.map
