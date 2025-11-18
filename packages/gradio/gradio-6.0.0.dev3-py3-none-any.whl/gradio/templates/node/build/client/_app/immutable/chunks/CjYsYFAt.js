import { c as RichTypeBoolean } from "./CERZDFgL.js";
import { L as Logger, R as RegisterClass } from "./f5NiF4Sn.js";
import { b as FlowGraphExecutionBlockWithOutSignal } from "./CWCX69Ol.js";
class FlowGraphWhileLoopBlock extends FlowGraphExecutionBlockWithOutSignal {
  constructor(config) {
    super(config);
    this.config = config;
    this.condition = this.registerDataInput("condition", RichTypeBoolean);
    this.executionFlow = this._registerSignalOutput("executionFlow");
    this.completed = this._registerSignalOutput("completed");
    this._unregisterSignalOutput("out");
  }
  _execute(context, _callingSignal) {
    let conditionValue = this.condition.getValue(context);
    if (this.config?.doWhile && !conditionValue) {
      this.executionFlow._activateSignal(context);
    }
    let i = 0;
    while (conditionValue) {
      this.executionFlow._activateSignal(context);
      ++i;
      if (i >= FlowGraphWhileLoopBlock.MaxLoopCount) {
        Logger.Warn("FlowGraphWhileLoopBlock: Max loop count reached. Breaking.");
        break;
      }
      conditionValue = this.condition.getValue(context);
    }
    this.completed._activateSignal(context);
  }
  getClassName() {
    return "FlowGraphWhileLoopBlock";
  }
}
FlowGraphWhileLoopBlock.MaxLoopCount = 1e3;
RegisterClass("FlowGraphWhileLoopBlock", FlowGraphWhileLoopBlock);
export {
  FlowGraphWhileLoopBlock
};
//# sourceMappingURL=CjYsYFAt.js.map
