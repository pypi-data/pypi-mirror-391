import { GLTFLoader } from "./yHduKdDt.js";
import { F as Color3, aN as unregisterGLTFExtension, aO as registerGLTFExtension } from "./f5NiF4Sn.js";
const NAME = "KHR_materials_diffuse_transmission";
class KHR_materials_diffuse_transmission {
  /**
   * @internal
   */
  constructor(loader) {
    this.name = NAME;
    this.order = 174;
    this._loader = loader;
    this.enabled = this._loader.isExtensionUsed(NAME);
    if (this.enabled) {
      loader.parent.transparencyAsCoverage = true;
    }
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
      promises.push(this._loadTranslucentPropertiesAsync(extensionContext, material, babylonMaterial, extension));
      return await Promise.all(promises).then(() => {
      });
    });
  }
  // eslint-disable-next-line no-restricted-syntax, @typescript-eslint/promise-function-async
  _loadTranslucentPropertiesAsync(context, material, babylonMaterial, extension) {
    const adapter = this._loader._getOrCreateMaterialAdapter(babylonMaterial);
    adapter.configureSubsurface();
    adapter.subsurfaceWeight = extension.diffuseTransmissionFactor ?? 0;
    adapter.subsurfaceColor = extension.diffuseTransmissionColorFactor !== void 0 ? Color3.FromArray(extension.diffuseTransmissionColorFactor) : Color3.White();
    const promises = new Array();
    if (extension.diffuseTransmissionTexture) {
      extension.diffuseTransmissionTexture.nonColorData = true;
      promises.push(this._loader.loadTextureInfoAsync(`${context}/diffuseTransmissionTexture`, extension.diffuseTransmissionTexture).then((texture) => {
        texture.name = `${babylonMaterial.name} (Diffuse Transmission)`;
        adapter.subsurfaceWeightTexture = texture;
      }));
    }
    if (extension.diffuseTransmissionColorTexture) {
      promises.push(this._loader.loadTextureInfoAsync(`${context}/diffuseTransmissionColorTexture`, extension.diffuseTransmissionColorTexture).then((texture) => {
        texture.name = `${babylonMaterial.name} (Diffuse Transmission Color)`;
        adapter.subsurfaceColorTexture = texture;
      }));
    }
    return Promise.all(promises).then(() => {
    });
  }
}
unregisterGLTFExtension(NAME);
registerGLTFExtension(NAME, true, (loader) => new KHR_materials_diffuse_transmission(loader));
export {
  KHR_materials_diffuse_transmission
};
//# sourceMappingURL=CjTJwMYk.js.map
