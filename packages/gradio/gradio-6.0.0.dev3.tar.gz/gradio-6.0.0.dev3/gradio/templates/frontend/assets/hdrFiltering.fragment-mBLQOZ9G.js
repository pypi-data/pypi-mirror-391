import{S as i}from"./index-BcVZ0Vib.js";import"./helperFunctions-D7jkIueJ.js";import"./hdrFilteringFunctions-DwRSRlGS.js";import"./pbrBRDFFunctions-BMbD5iO3.js";import"./index-C_pgmrh1.js";const r="hdrFilteringPixelShader",e=`#include<helperFunctions>
#include<importanceSampling>
#include<pbrBRDFFunctions>
#include<hdrFilteringFunctions>
uniform float alphaG;uniform samplerCube inputTexture;uniform vec2 vFilteringInfo;uniform float hdrScale;varying vec3 direction;void main() {vec3 color=radiance(alphaG,inputTexture,direction,vFilteringInfo);gl_FragColor=vec4(color*hdrScale,1.0);}`;i.ShadersStore[r]||(i.ShadersStore[r]=e);const c={name:r,shader:e};export{c as hdrFilteringPixelShader};
//# sourceMappingURL=hdrFiltering.fragment-mBLQOZ9G.js.map
