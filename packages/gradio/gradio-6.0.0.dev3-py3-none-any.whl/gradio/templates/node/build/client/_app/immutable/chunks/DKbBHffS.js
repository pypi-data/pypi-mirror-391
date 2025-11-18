import { b as FlowGraphExecutionBlockWithOutSignal, g as getNumericValue } from "./CWCX69Ol.js";
import { R as RichTypeAny, b as RichTypeNumber, i as RichTypeFlowGraphInteger, F as FlowGraphInteger } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphForLoopBlock extends FlowGraphExecutionBlockWithOutSignal {
  constructor(config) {
    super(config);
    this.startIndex = this.registerDataInput("startIndex", RichTypeAny, 0);
    this.endIndex = this.registerDataInput("endIndex", RichTypeAny);
    this.step = this.registerDataInput("step", RichTypeNumber, 1);
    this.index = this.registerDataOutput("index", RichTypeFlowGraphInteger, new FlowGraphInteger(getNumericValue(config?.initialIndex ?? 0)));
    this.executionFlow = this._registerSignalOutput("executionFlow");
    this.completed = this._registerSignalOutput("completed");
    this._unregisterSignalOutput("out");
  }
  /**
   * @internal
   */
  _execute(context) {
    const index = getNumericValue(this.startIndex.getValue(context));
    const step = this.step.getValue(context);
    let endIndex = getNumericValue(this.endIndex.getValue(context));
    for (let i = index; i < endIndex; i += step) {
      this.index.setValue(new FlowGraphInteger(i), context);
      this.executionFlow._activateSignal(context);
      endIndex = getNumericValue(this.endIndex.getValue(context));
      if (i > FlowGraphForLoopBlock.MaxLoopIterations * step) {
        break;
      }
    }
    if (this.config?.incrementIndexWhenLoopDone) {
      this.index.setValue(new FlowGraphInteger(getNumericValue(this.index.getValue(context)) + step), context);
    }
    this.completed._activateSignal(context);
  }
  /**
   * @returns class name of the block.
   */
  getClassName() {
    return "FlowGraphForLoopBlock";
  }
}
FlowGraphForLoopBlock.MaxLoopIterations = 1e3;
RegisterClass("FlowGraphForLoopBlock", FlowGraphForLoopBlock);
export {
  FlowGraphForLoopBlock
};
//# sourceMappingURL=DKbBHffS.js.map
