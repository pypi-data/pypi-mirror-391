import { b as SceneComponentConstants, c as Scene } from "./f5NiF4Sn.js";
import { G as GeometryBufferRenderer } from "./CwdGFSvq.js";
Object.defineProperty(Scene.prototype, "geometryBufferRenderer", {
  get: function() {
    return this._geometryBufferRenderer;
  },
  set: function(value) {
    if (value && value.isSupported) {
      this._geometryBufferRenderer = value;
    }
  },
  enumerable: true,
  configurable: true
});
Scene.prototype.enableGeometryBufferRenderer = function(ratio = 1, depthFormat = 15, textureTypesAndFormats) {
  if (this._geometryBufferRenderer) {
    return this._geometryBufferRenderer;
  }
  this._geometryBufferRenderer = new GeometryBufferRenderer(this, ratio, depthFormat, textureTypesAndFormats);
  if (!this._geometryBufferRenderer.isSupported) {
    this._geometryBufferRenderer = null;
  }
  return this._geometryBufferRenderer;
};
Scene.prototype.disableGeometryBufferRenderer = function() {
  if (!this._geometryBufferRenderer) {
    return;
  }
  this._geometryBufferRenderer.dispose();
  this._geometryBufferRenderer = null;
};
class GeometryBufferRendererSceneComponent {
  /**
   * Creates a new instance of the component for the given scene
   * @param scene Defines the scene to register the component in
   */
  constructor(scene) {
    this.name = SceneComponentConstants.NAME_GEOMETRYBUFFERRENDERER;
    this.scene = scene;
  }
  /**
   * Registers the component in a given scene
   */
  register() {
    this.scene._gatherRenderTargetsStage.registerStep(SceneComponentConstants.STEP_GATHERRENDERTARGETS_GEOMETRYBUFFERRENDERER, this, this._gatherRenderTargets);
  }
  /**
   * Rebuilds the elements related to this component in case of
   * context lost for instance.
   */
  rebuild() {
  }
  /**
   * Disposes the component and the associated resources
   */
  dispose() {
  }
  _gatherRenderTargets(renderTargets) {
    if (this.scene._geometryBufferRenderer) {
      renderTargets.push(this.scene._geometryBufferRenderer.getGBuffer());
    }
  }
}
GeometryBufferRenderer._SceneComponentInitialization = (scene) => {
  let component = scene._getComponent(SceneComponentConstants.NAME_GEOMETRYBUFFERRENDERER);
  if (!component) {
    component = new GeometryBufferRendererSceneComponent(scene);
    scene._addComponent(component);
  }
};
export {
  GeometryBufferRendererSceneComponent
};
//# sourceMappingURL=D8nhroUF.js.map
