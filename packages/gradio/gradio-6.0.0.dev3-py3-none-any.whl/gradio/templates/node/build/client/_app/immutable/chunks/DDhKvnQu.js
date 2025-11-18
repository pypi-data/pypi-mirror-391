import { S as ShaderStore } from "./f5NiF4Sn.js";
const name = "envShadowGroundVertexShader";
const shader = `precision highp float;attribute vec3 position;attribute vec2 uv;uniform mat4 worldViewProjection;varying vec2 vUV;void main(void) {gl_Position=worldViewProjection*vec4(position,1.0);vUV=uv;}`;
if (!ShaderStore.ShadersStore[name]) {
  ShaderStore.ShadersStore[name] = shader;
}
const envShadowGroundVertexShader = { name, shader };
export {
  envShadowGroundVertexShader
};
//# sourceMappingURL=DDhKvnQu.js.map
