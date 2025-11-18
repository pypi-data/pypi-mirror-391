import { c as FlowGraphEventBlock } from "./CWCX69Ol.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphSceneReadyEventBlock extends FlowGraphEventBlock {
  constructor() {
    super(...arguments);
    this.initPriority = -1;
    this.type = "SceneReady";
  }
  _executeEvent(context, _payload) {
    this._execute(context);
    return true;
  }
  _preparePendingTasks(context) {
  }
  _cancelPendingTasks(context) {
  }
  /**
   * @returns class name of the block.
   */
  getClassName() {
    return "FlowGraphSceneReadyEventBlock";
  }
}
RegisterClass("FlowGraphSceneReadyEventBlock", FlowGraphSceneReadyEventBlock);
export {
  FlowGraphSceneReadyEventBlock
};
//# sourceMappingURL=DMRGJmKa.js.map
