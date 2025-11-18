import { S as ShaderStore } from "./f5NiF4Sn.js";
const name = "mainUVVaryingDeclaration";
const shader = `#ifdef MAINUV{X}
varying vec2 vMainUV{X};
#endif
`;
if (!ShaderStore.IncludesShadersStore[name]) {
  ShaderStore.IncludesShadersStore[name] = shader;
}
//# sourceMappingURL=BlFtyhuI.js.map
