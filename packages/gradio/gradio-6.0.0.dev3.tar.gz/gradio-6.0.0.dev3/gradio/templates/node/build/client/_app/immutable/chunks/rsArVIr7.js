import { F as FlowGraphBlock } from "./CWCX69Ol.js";
import { R as RichTypeAny, i as RichTypeFlowGraphInteger, F as FlowGraphInteger } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphIndexOfBlock extends FlowGraphBlock {
  /**
   * Construct a FlowGraphIndexOfBlock.
   * @param config construction parameters
   */
  constructor(config) {
    super(config);
    this.config = config;
    this.object = this.registerDataInput("object", RichTypeAny);
    this.array = this.registerDataInput("array", RichTypeAny);
    this.index = this.registerDataOutput("index", RichTypeFlowGraphInteger, new FlowGraphInteger(-1));
  }
  /**
   * @internal
   */
  _updateOutputs(context) {
    const object = this.object.getValue(context);
    const array = this.array.getValue(context);
    if (array) {
      this.index.setValue(new FlowGraphInteger(array.indexOf(object)), context);
    }
  }
  /**
   * Serializes this block
   * @param serializationObject the object to serialize to
   */
  serialize(serializationObject) {
    super.serialize(serializationObject);
  }
  getClassName() {
    return "FlowGraphIndexOfBlock";
  }
}
RegisterClass("FlowGraphIndexOfBlock", FlowGraphIndexOfBlock);
export {
  FlowGraphIndexOfBlock
};
//# sourceMappingURL=rsArVIr7.js.map
