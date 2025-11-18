import { b as SceneComponentConstants, av as ShadowGenerator } from "./f5NiF4Sn.js";
class ShadowGeneratorSceneComponent {
  /**
   * Creates a new instance of the component for the given scene
   * @param scene Defines the scene to register the component in
   */
  constructor(scene) {
    this.name = SceneComponentConstants.NAME_SHADOWGENERATOR;
    this.scene = scene;
  }
  /**
   * Registers the component in a given scene
   */
  register() {
    this.scene._gatherRenderTargetsStage.registerStep(SceneComponentConstants.STEP_GATHERRENDERTARGETS_SHADOWGENERATOR, this, this._gatherRenderTargets);
  }
  /**
   * Rebuilds the elements related to this component in case of
   * context lost for instance.
   */
  rebuild() {
  }
  /**
   * Serializes the component data to the specified json object
   * @param serializationObject The object to serialize to
   */
  serialize(serializationObject) {
    serializationObject.shadowGenerators = [];
    const lights = this.scene.lights;
    for (const light of lights) {
      if (light.doNotSerialize) {
        continue;
      }
      const shadowGenerators = light.getShadowGenerators();
      if (shadowGenerators) {
        const iterator = shadowGenerators.values();
        for (let key = iterator.next(); key.done !== true; key = iterator.next()) {
          const shadowGenerator = key.value;
          if (shadowGenerator.doNotSerialize) {
            continue;
          }
          serializationObject.shadowGenerators.push(shadowGenerator.serialize());
        }
      }
    }
  }
  /**
   * Adds all the elements from the container to the scene
   * @param container the container holding the elements
   */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  addFromContainer(container) {
  }
  /**
   * Removes all the elements in the container from the scene
   * @param container contains the elements to remove
   * @param dispose if the removed element should be disposed (default: false)
   */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  removeFromContainer(container, dispose) {
  }
  /**
   * Rebuilds the elements related to this component in case of
   * context lost for instance.
   */
  dispose() {
  }
  _gatherRenderTargets(renderTargets) {
    const scene = this.scene;
    if (this.scene.shadowsEnabled) {
      for (let lightIndex = 0; lightIndex < scene.lights.length; lightIndex++) {
        const light = scene.lights[lightIndex];
        const shadowGenerators = light.getShadowGenerators();
        if (light.isEnabled() && light.shadowEnabled && shadowGenerators) {
          const iterator = shadowGenerators.values();
          for (let key = iterator.next(); key.done !== true; key = iterator.next()) {
            const shadowGenerator = key.value;
            const shadowMap = shadowGenerator.getShadowMap();
            if (scene.textures.indexOf(shadowMap) !== -1) {
              renderTargets.push(shadowMap);
            }
          }
        }
      }
    }
  }
}
ShadowGenerator._SceneComponentInitialization = (scene) => {
  let component = scene._getComponent(SceneComponentConstants.NAME_SHADOWGENERATOR);
  if (!component) {
    component = new ShadowGeneratorSceneComponent(scene);
    scene._addComponent(component);
  }
};
export {
  ShadowGeneratorSceneComponent
};
//# sourceMappingURL=DY-cr9vZ.js.map
