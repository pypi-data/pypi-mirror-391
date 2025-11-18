import { R as RegisterClass } from "./f5NiF4Sn.js";
import { b as FlowGraphExecutionBlockWithOutSignal, g as getNumericValue } from "./CWCX69Ol.js";
import { i as RichTypeFlowGraphInteger } from "./CERZDFgL.js";
class FlowGraphCancelDelayBlock extends FlowGraphExecutionBlockWithOutSignal {
  constructor(config) {
    super(config);
    this.delayIndex = this.registerDataInput("delayIndex", RichTypeFlowGraphInteger);
  }
  _execute(context, _callingSignal) {
    const delayIndex = getNumericValue(this.delayIndex.getValue(context));
    if (delayIndex <= 0 || isNaN(delayIndex) || !isFinite(delayIndex)) {
      return this._reportError(context, "Invalid delay index");
    }
    const timers = context._getGlobalContextVariable("pendingDelays", []);
    const timer = timers[delayIndex];
    if (timer) {
      timer.dispose();
    }
    this.out._activateSignal(context);
  }
  getClassName() {
    return "FlowGraphCancelDelayBlock";
  }
}
RegisterClass("FlowGraphCancelDelayBlock", FlowGraphCancelDelayBlock);
export {
  FlowGraphCancelDelayBlock
};
//# sourceMappingURL=BUG55UVv.js.map
