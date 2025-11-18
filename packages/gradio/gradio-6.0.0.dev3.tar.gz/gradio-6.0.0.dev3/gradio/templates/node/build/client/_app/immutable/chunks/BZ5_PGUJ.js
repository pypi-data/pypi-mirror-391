import { c as FlowGraphEventBlock } from "./CWCX69Ol.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
import { b as RichTypeNumber } from "./CERZDFgL.js";
class FlowGraphSceneTickEventBlock extends FlowGraphEventBlock {
  constructor() {
    super();
    this.type = "SceneBeforeRender";
    this.timeSinceStart = this.registerDataOutput("timeSinceStart", RichTypeNumber);
    this.deltaTime = this.registerDataOutput("deltaTime", RichTypeNumber);
  }
  /**
   * @internal
   */
  _preparePendingTasks(_context) {
  }
  /**
   * @internal
   */
  _executeEvent(context, payload) {
    this.timeSinceStart.setValue(payload.timeSinceStart, context);
    this.deltaTime.setValue(payload.deltaTime, context);
    this._execute(context);
    return true;
  }
  /**
   * @internal
   */
  _cancelPendingTasks(_context) {
  }
  /**
   * @returns class name of the block.
   */
  getClassName() {
    return "FlowGraphSceneTickEventBlock";
  }
}
RegisterClass("FlowGraphSceneTickEventBlock", FlowGraphSceneTickEventBlock);
export {
  FlowGraphSceneTickEventBlock
};
//# sourceMappingURL=BZ5_PGUJ.js.map
