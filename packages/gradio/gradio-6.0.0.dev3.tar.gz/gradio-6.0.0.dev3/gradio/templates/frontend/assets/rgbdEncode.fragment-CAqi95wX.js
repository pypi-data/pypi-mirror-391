import{S as r}from"./index-BcVZ0Vib.js";import"./helperFunctions-D7jkIueJ.js";import"./index-C_pgmrh1.js";const e="rgbdEncodePixelShader",o=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=toRGBD(texture2D(textureSampler,vUV).rgb);}`;r.ShadersStore[e]||(r.ShadersStore[e]=o);const i={name:e,shader:o};export{i as rgbdEncodePixelShader};
//# sourceMappingURL=rgbdEncode.fragment-CAqi95wX.js.map
