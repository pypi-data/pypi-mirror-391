import { F as FlowGraphBlock } from "./CWCX69Ol.js";
import { R as RichTypeAny, b as RichTypeNumber } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphContextBlock extends FlowGraphBlock {
  constructor(config) {
    super(config);
    this.userVariables = this.registerDataOutput("userVariables", RichTypeAny);
    this.executionId = this.registerDataOutput("executionId", RichTypeNumber);
  }
  _updateOutputs(context) {
    this.userVariables.setValue(context.userVariables, context);
    this.executionId.setValue(context.executionId, context);
  }
  serialize(serializationObject) {
    super.serialize(serializationObject);
  }
  getClassName() {
    return "FlowGraphContextBlock";
  }
}
RegisterClass("FlowGraphContextBlock", FlowGraphContextBlock);
export {
  FlowGraphContextBlock
};
//# sourceMappingURL=BGrnO98N.js.map
