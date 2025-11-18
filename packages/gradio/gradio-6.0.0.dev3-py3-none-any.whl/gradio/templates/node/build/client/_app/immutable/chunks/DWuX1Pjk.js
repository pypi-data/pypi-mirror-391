import { e as FlowGraphExecutionBlock } from "./CWCX69Ol.js";
import { c as RichTypeBoolean } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphFlipFlopBlock extends FlowGraphExecutionBlock {
  constructor(config) {
    super(config);
    this.onOn = this._registerSignalOutput("onOn");
    this.onOff = this._registerSignalOutput("onOff");
    this.value = this.registerDataOutput("value", RichTypeBoolean);
  }
  _execute(context, _callingSignal) {
    let value = context._getExecutionVariable(this, "value", typeof this.config?.startValue === "boolean" ? !this.config.startValue : false);
    value = !value;
    context._setExecutionVariable(this, "value", value);
    this.value.setValue(value, context);
    if (value) {
      this.onOn._activateSignal(context);
    } else {
      this.onOff._activateSignal(context);
    }
  }
  /**
   * @returns class name of the block.
   */
  getClassName() {
    return "FlowGraphFlipFlopBlock";
  }
}
RegisterClass("FlowGraphFlipFlopBlock", FlowGraphFlipFlopBlock);
export {
  FlowGraphFlipFlopBlock
};
//# sourceMappingURL=DWuX1Pjk.js.map
