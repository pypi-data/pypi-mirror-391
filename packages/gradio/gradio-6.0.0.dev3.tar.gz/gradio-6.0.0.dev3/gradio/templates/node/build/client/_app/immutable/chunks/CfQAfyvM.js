import { F as FlowGraphUnaryOperationBlock } from "./DHe4dnFy.js";
import { b as RichTypeNumber, i as RichTypeFlowGraphInteger, F as FlowGraphInteger, c as RichTypeBoolean } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphBooleanToFloat extends FlowGraphUnaryOperationBlock {
  constructor(config) {
    super(RichTypeBoolean, RichTypeNumber, (a) => +a, "FlowGraphBooleanToFloat", config);
  }
}
RegisterClass("FlowGraphBooleanToFloat", FlowGraphBooleanToFloat);
class FlowGraphBooleanToInt extends FlowGraphUnaryOperationBlock {
  constructor(config) {
    super(RichTypeBoolean, RichTypeFlowGraphInteger, (a) => FlowGraphInteger.FromValue(+a), "FlowGraphBooleanToInt", config);
  }
}
RegisterClass("FlowGraphBooleanToInt", FlowGraphBooleanToInt);
class FlowGraphFloatToBoolean extends FlowGraphUnaryOperationBlock {
  constructor(config) {
    super(RichTypeNumber, RichTypeBoolean, (a) => !!a, "FlowGraphFloatToBoolean", config);
  }
}
RegisterClass("FlowGraphFloatToBoolean", FlowGraphFloatToBoolean);
class FlowGraphIntToBoolean extends FlowGraphUnaryOperationBlock {
  constructor(config) {
    super(RichTypeFlowGraphInteger, RichTypeBoolean, (a) => !!a.value, "FlowGraphIntToBoolean", config);
  }
}
RegisterClass("FlowGraphIntToBoolean", FlowGraphIntToBoolean);
class FlowGraphIntToFloat extends FlowGraphUnaryOperationBlock {
  constructor(config) {
    super(RichTypeFlowGraphInteger, RichTypeNumber, (a) => a.value, "FlowGraphIntToFloat", config);
  }
}
RegisterClass("FlowGraphIntToFloat", FlowGraphIntToFloat);
class FlowGraphFloatToInt extends FlowGraphUnaryOperationBlock {
  constructor(config) {
    super(RichTypeNumber, RichTypeFlowGraphInteger, (a) => {
      const roundingMode = config?.roundingMode;
      switch (roundingMode) {
        case "floor":
          return FlowGraphInteger.FromValue(Math.floor(a));
        case "ceil":
          return FlowGraphInteger.FromValue(Math.ceil(a));
        case "round":
          return FlowGraphInteger.FromValue(Math.round(a));
        default:
          return FlowGraphInteger.FromValue(a);
      }
    }, "FlowGraphFloatToInt", config);
  }
}
RegisterClass("FlowGraphFloatToInt", FlowGraphFloatToInt);
export {
  FlowGraphBooleanToFloat,
  FlowGraphBooleanToInt,
  FlowGraphFloatToBoolean,
  FlowGraphFloatToInt,
  FlowGraphIntToBoolean,
  FlowGraphIntToFloat
};
//# sourceMappingURL=CfQAfyvM.js.map
