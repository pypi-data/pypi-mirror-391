import { F as FlowGraphBlock } from "./CWCX69Ol.js";
import { c as RichTypeBoolean, R as RichTypeAny } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphConditionalDataBlock extends FlowGraphBlock {
  /**
   * Creates a new instance of the block
   * @param config optional configuration for this block
   */
  constructor(config) {
    super(config);
    this.condition = this.registerDataInput("condition", RichTypeBoolean);
    this.onTrue = this.registerDataInput("onTrue", RichTypeAny);
    this.onFalse = this.registerDataInput("onFalse", RichTypeAny);
    this.output = this.registerDataOutput("output", RichTypeAny);
  }
  /**
   * @internal
   */
  _updateOutputs(context) {
    const condition = this.condition.getValue(context);
    this.output.setValue(condition ? this.onTrue.getValue(context) : this.onFalse.getValue(context), context);
  }
  /**
   * Gets the class name of this block
   * @returns the class name
   */
  getClassName() {
    return "FlowGraphConditionalBlock";
  }
}
RegisterClass("FlowGraphConditionalBlock", FlowGraphConditionalDataBlock);
export {
  FlowGraphConditionalDataBlock
};
//# sourceMappingURL=DzcTdlFD.js.map
