import { b as FlowGraphExecutionBlockWithOutSignal } from "./CWCX69Ol.js";
import { R as RichTypeAny } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphSetPropertyBlock extends FlowGraphExecutionBlockWithOutSignal {
  constructor(config) {
    super(config);
    this.config = config;
    this.object = this.registerDataInput("object", RichTypeAny, config.target);
    this.value = this.registerDataInput("value", RichTypeAny);
    this.propertyName = this.registerDataInput("propertyName", RichTypeAny, config.propertyName);
    this.customSetFunction = this.registerDataInput("customSetFunction", RichTypeAny);
  }
  _execute(context, _callingSignal) {
    try {
      const target = this.object.getValue(context);
      const value = this.value.getValue(context);
      const propertyName = this.propertyName.getValue(context);
      this._stopRunningAnimations(context, target, propertyName);
      const setFunction = this.customSetFunction.getValue(context);
      if (setFunction) {
        setFunction(target, propertyName, value, context);
      } else {
        this._setPropertyValue(target, propertyName, value);
      }
    } catch (e) {
      this._reportError(context, e);
    }
    this.out._activateSignal(context);
  }
  _stopRunningAnimations(context, target, propertyName) {
    const currentlyRunningAnimationGroups = context._getGlobalContextVariable("currentlyRunningAnimationGroups", []);
    for (const uniqueId of currentlyRunningAnimationGroups) {
      const animationGroup = context.assetsContext.animationGroups.find((animationGroup2) => animationGroup2.uniqueId === uniqueId);
      if (animationGroup) {
        for (const targetedAnimations of animationGroup.targetedAnimations) {
          if (targetedAnimations.target === target && targetedAnimations.animation.targetProperty === propertyName) {
            animationGroup.stop(true);
            animationGroup.dispose();
            const index = currentlyRunningAnimationGroups.indexOf(uniqueId);
            if (index !== -1) {
              currentlyRunningAnimationGroups.splice(index, 1);
              context._setGlobalContextVariable("currentlyRunningAnimationGroups", currentlyRunningAnimationGroups);
            }
          }
        }
      }
    }
  }
  _setPropertyValue(target, propertyName, value) {
    const path = propertyName.split(".");
    let obj = target;
    for (let i = 0; i < path.length - 1; i++) {
      const prop = path[i];
      if (obj[prop] === void 0) {
        obj[prop] = {};
      }
      obj = obj[prop];
    }
    obj[path[path.length - 1]] = value;
  }
  getClassName() {
    return "FlowGraphSetPropertyBlock";
  }
}
RegisterClass("FlowGraphSetPropertyBlock", FlowGraphSetPropertyBlock);
export {
  FlowGraphSetPropertyBlock
};
//# sourceMappingURL=C3KehDaB.js.map
