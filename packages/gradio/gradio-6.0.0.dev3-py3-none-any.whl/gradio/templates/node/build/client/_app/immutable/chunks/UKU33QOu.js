import { aN as unregisterGLTFExtension, aO as registerGLTFExtension } from "./f5NiF4Sn.js";
const NAME = "KHR_mesh_quantization";
class KHR_mesh_quantization {
  /**
   * @internal
   */
  constructor(loader) {
    this.name = NAME;
    this.enabled = loader.isExtensionUsed(NAME);
  }
  /** @internal */
  dispose() {
  }
}
unregisterGLTFExtension(NAME);
registerGLTFExtension(NAME, true, (loader) => new KHR_mesh_quantization(loader));
export {
  KHR_mesh_quantization
};
//# sourceMappingURL=UKU33QOu.js.map
