import { b as RichTypeNumber } from "./CERZDFgL.js";
import { b as FlowGraphExecutionBlockWithOutSignal } from "./CWCX69Ol.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphCallCounterBlock extends FlowGraphExecutionBlockWithOutSignal {
  constructor(config) {
    super(config);
    this.count = this.registerDataOutput("count", RichTypeNumber);
    this.reset = this._registerSignalInput("reset");
  }
  _execute(context, callingSignal) {
    if (callingSignal === this.reset) {
      context._setExecutionVariable(this, "count", 0);
      this.count.setValue(0, context);
      return;
    }
    const countValue = context._getExecutionVariable(this, "count", 0) + 1;
    context._setExecutionVariable(this, "count", countValue);
    this.count.setValue(countValue, context);
    this.out._activateSignal(context);
  }
  /**
   * @returns class name of the block.
   */
  getClassName() {
    return "FlowGraphCallCounterBlock";
  }
}
RegisterClass("FlowGraphCallCounterBlock", FlowGraphCallCounterBlock);
export {
  FlowGraphCallCounterBlock
};
//# sourceMappingURL=BDDfLuQE.js.map
