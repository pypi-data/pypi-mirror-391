import { GLTFLoader } from "./yHduKdDt.js";
import { aN as unregisterGLTFExtension, aO as registerGLTFExtension } from "./f5NiF4Sn.js";
const NAME = "MSFT_minecraftMesh";
class MSFT_minecraftMesh {
  /** @internal */
  constructor(loader) {
    this.name = NAME;
    this._loader = loader;
    this.enabled = this._loader.isExtensionUsed(NAME);
  }
  /** @internal */
  dispose() {
    this._loader = null;
  }
  /** @internal */
  // eslint-disable-next-line no-restricted-syntax
  loadMaterialPropertiesAsync(context, material, babylonMaterial) {
    return GLTFLoader.LoadExtraAsync(context, material, this.name, async (extraContext, extra) => {
      if (extra) {
        if (!this._loader._pbrMaterialImpl) {
          throw new Error(`${extraContext}: Material type not supported`);
        }
        const promise = this._loader.loadMaterialPropertiesAsync(context, material, babylonMaterial);
        if (babylonMaterial.needAlphaBlending()) {
          babylonMaterial.forceDepthWrite = true;
          babylonMaterial.separateCullingPass = true;
        }
        babylonMaterial.backFaceCulling = babylonMaterial.forceDepthWrite;
        babylonMaterial.twoSidedLighting = true;
        return await promise;
      }
    });
  }
}
unregisterGLTFExtension(NAME);
registerGLTFExtension(NAME, true, (loader) => new MSFT_minecraftMesh(loader));
export {
  MSFT_minecraftMesh
};
//# sourceMappingURL=BURYav_r.js.map
