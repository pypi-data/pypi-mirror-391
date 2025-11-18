import { GLTFLoader } from "./yHduKdDt.js";
import { aN as unregisterGLTFExtension, aO as registerGLTFExtension } from "./f5NiF4Sn.js";
const NAME = "KHR_materials_ior";
class KHR_materials_ior {
  /**
   * @internal
   */
  constructor(loader) {
    this.name = NAME;
    this.order = 180;
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
      const promises = new Array();
      promises.push(this._loader.loadMaterialPropertiesAsync(context, material, babylonMaterial));
      promises.push(this._loadIorPropertiesAsync(extensionContext, extension, babylonMaterial));
      return await Promise.all(promises).then(() => {
      });
    });
  }
  // eslint-disable-next-line @typescript-eslint/promise-function-async, no-restricted-syntax
  _loadIorPropertiesAsync(context, properties, babylonMaterial) {
    const adapter = this._loader._getOrCreateMaterialAdapter(babylonMaterial);
    const indexOfRefraction = properties.ior !== void 0 ? properties.ior : KHR_materials_ior._DEFAULT_IOR;
    adapter.specularIor = indexOfRefraction;
    return Promise.resolve();
  }
}
KHR_materials_ior._DEFAULT_IOR = 1.5;
unregisterGLTFExtension(NAME);
registerGLTFExtension(NAME, true, (loader) => new KHR_materials_ior(loader));
export {
  KHR_materials_ior
};
//# sourceMappingURL=Cl-SzZ9B.js.map
