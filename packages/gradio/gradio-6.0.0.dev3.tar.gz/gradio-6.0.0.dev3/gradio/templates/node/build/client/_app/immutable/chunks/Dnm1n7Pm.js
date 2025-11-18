import { GLTFLoader } from "./yHduKdDt.js";
import { aN as unregisterGLTFExtension, aO as registerGLTFExtension } from "./f5NiF4Sn.js";
const NAME = "KHR_materials_emissive_strength";
class KHR_materials_emissive_strength {
  /**
   * @internal
   */
  constructor(loader) {
    this.name = NAME;
    this.order = 170;
    this._loader = loader;
    this.enabled = this._loader.isExtensionUsed(NAME);
  }
  /** @internal */
  dispose() {
    this._loader = null;
  }
  /**
   * @internal
   */
  // eslint-disable-next-line no-restricted-syntax
  loadMaterialPropertiesAsync(context, material, babylonMaterial) {
    return GLTFLoader.LoadExtensionAsync(context, material, this.name, async (extensionContext, extension) => {
      await this._loader.loadMaterialPropertiesAsync(context, material, babylonMaterial);
      this._loadEmissiveProperties(extensionContext, extension, babylonMaterial);
      return await Promise.resolve();
    });
  }
  _loadEmissiveProperties(context, properties, babylonMaterial) {
    if (properties.emissiveStrength !== void 0) {
      const adapter = this._loader._getOrCreateMaterialAdapter(babylonMaterial);
      adapter.emissionLuminance = properties.emissiveStrength;
    }
  }
}
unregisterGLTFExtension(NAME);
registerGLTFExtension(NAME, true, (loader) => new KHR_materials_emissive_strength(loader));
export {
  KHR_materials_emissive_strength
};
//# sourceMappingURL=Dnm1n7Pm.js.map
