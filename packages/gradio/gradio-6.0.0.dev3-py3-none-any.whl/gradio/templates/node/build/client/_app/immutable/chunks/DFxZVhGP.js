import { F as FlowGraphBlock, f as defaultValueSerializationFunction } from "./CWCX69Ol.js";
import { j as getRichTypeFromValue } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphConstantBlock extends FlowGraphBlock {
  constructor(config) {
    super(config);
    this.config = config;
    this.output = this.registerDataOutput("output", getRichTypeFromValue(config.value));
  }
  _updateOutputs(context) {
    this.output.setValue(this.config.value, context);
  }
  /**
   * Gets the class name of this block
   * @returns the class name
   */
  getClassName() {
    return "FlowGraphConstantBlock";
  }
  /**
   * Serializes this block
   * @param serializationObject the object to serialize to
   * @param valueSerializeFunction the function to use to serialize the value
   */
  serialize(serializationObject = {}, valueSerializeFunction = defaultValueSerializationFunction) {
    super.serialize(serializationObject);
    valueSerializeFunction("value", this.config.value, serializationObject.config);
  }
}
RegisterClass("FlowGraphConstantBlock", FlowGraphConstantBlock);
export {
  FlowGraphConstantBlock
};
//# sourceMappingURL=DFxZVhGP.js.map
