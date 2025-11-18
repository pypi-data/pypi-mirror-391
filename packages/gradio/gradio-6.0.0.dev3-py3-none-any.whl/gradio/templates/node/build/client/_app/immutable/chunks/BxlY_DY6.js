import { F as Color3, aN as unregisterGLTFExtension, aO as registerGLTFExtension } from "./f5NiF4Sn.js";
import { GLTFLoader } from "./yHduKdDt.js";
const NAME = "KHR_materials_volume";
class KHR_materials_volume {
  /**
   * @internal
   */
  constructor(loader) {
    this.name = NAME;
    this.order = 173;
    this._loader = loader;
    this.enabled = this._loader.isExtensionUsed(NAME);
    if (this.enabled) {
      this._loader._disableInstancedMesh++;
    }
  }
  /** @internal */
  dispose() {
    if (this.enabled) {
      this._loader._disableInstancedMesh--;
    }
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
      promises.push(this._loadVolumePropertiesAsync(extensionContext, material, babylonMaterial, extension));
      return await Promise.all(promises).then(() => {
      });
    });
  }
  // eslint-disable-next-line @typescript-eslint/promise-function-async, no-restricted-syntax
  _loadVolumePropertiesAsync(context, material, babylonMaterial, extension) {
    const adapter = this._loader._getOrCreateMaterialAdapter(babylonMaterial);
    if (adapter.transmissionWeight === 0 && adapter.subsurfaceWeight === 0 || !extension.thicknessFactor) {
      return Promise.resolve();
    }
    adapter.transmissionDepth = extension.attenuationDistance !== void 0 ? extension.attenuationDistance : Number.MAX_VALUE;
    adapter.transmissionColor = extension.attenuationColor !== void 0 && extension.attenuationColor.length == 3 ? Color3.FromArray(extension.attenuationColor) : Color3.White();
    adapter.volumeThickness = extension.thicknessFactor ?? 0;
    const promises = new Array();
    if (extension.thicknessTexture) {
      extension.thicknessTexture.nonColorData = true;
      promises.push(this._loader.loadTextureInfoAsync(`${context}/thicknessTexture`, extension.thicknessTexture, (texture) => {
        texture.name = `${babylonMaterial.name} (Thickness)`;
        adapter.volumeThicknessTexture = texture;
      }));
    }
    return Promise.all(promises).then(() => {
    });
  }
}
unregisterGLTFExtension(NAME);
registerGLTFExtension(NAME, true, (loader) => new KHR_materials_volume(loader));
export {
  KHR_materials_volume
};
//# sourceMappingURL=BxlY_DY6.js.map
