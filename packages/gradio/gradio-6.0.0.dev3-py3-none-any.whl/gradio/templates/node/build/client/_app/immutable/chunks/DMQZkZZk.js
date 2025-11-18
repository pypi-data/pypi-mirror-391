import { R as RegisterClass } from "./f5NiF4Sn.js";
import { b as FlowGraphExecutionBlockWithOutSignal } from "./CWCX69Ol.js";
import { R as RichTypeAny } from "./CERZDFgL.js";
class FlowGraphSetVariableBlock extends FlowGraphExecutionBlockWithOutSignal {
  constructor(config) {
    super(config);
    if (!config.variable && !config.variables) {
      throw new Error("FlowGraphSetVariableBlock: variable/variables is not defined");
    }
    if (config.variables && config.variable) {
      throw new Error("FlowGraphSetVariableBlock: variable and variables are both defined");
    }
    if (config.variables) {
      for (const variable of config.variables) {
        this.registerDataInput(variable, RichTypeAny);
      }
    } else {
      this.registerDataInput("value", RichTypeAny);
    }
  }
  _execute(context, _callingSignal) {
    if (this.config?.variables) {
      for (const variable of this.config.variables) {
        this._saveVariable(context, variable);
      }
    } else {
      this._saveVariable(context, this.config?.variable, "value");
    }
    this.out._activateSignal(context);
  }
  _saveVariable(context, variableName, inputName) {
    const currentlyRunningAnimationGroups = context._getGlobalContextVariable("currentlyRunningAnimationGroups", []);
    for (const animationUniqueId of currentlyRunningAnimationGroups) {
      const animationGroup = context.assetsContext.animationGroups.find((animationGroup2) => animationGroup2.uniqueId == animationUniqueId);
      if (animationGroup) {
        for (const targetAnimation of animationGroup.targetedAnimations) {
          if (targetAnimation.target === context) {
            if (targetAnimation.animation.targetProperty === variableName) {
              animationGroup.stop();
              const index = currentlyRunningAnimationGroups.indexOf(animationUniqueId);
              if (index > -1) {
                currentlyRunningAnimationGroups.splice(index, 1);
              }
              context._setGlobalContextVariable("currentlyRunningAnimationGroups", currentlyRunningAnimationGroups);
              break;
            }
          }
        }
      }
    }
    const value = this.getDataInput(inputName || variableName)?.getValue(context);
    context.setVariable(variableName, value);
  }
  getClassName() {
    return "FlowGraphSetVariableBlock";
  }
  serialize(serializationObject) {
    super.serialize(serializationObject);
    serializationObject.config.variable = this.config?.variable;
  }
}
RegisterClass("FlowGraphSetVariableBlock", FlowGraphSetVariableBlock);
export {
  FlowGraphSetVariableBlock
};
//# sourceMappingURL=DMQZkZZk.js.map
