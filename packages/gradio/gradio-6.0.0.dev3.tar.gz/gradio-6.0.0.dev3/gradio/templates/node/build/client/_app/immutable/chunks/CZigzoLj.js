import { c as FlowGraphEventBlock, _ as _IsDescendantOf } from "./CWCX69Ol.js";
import { b as RichTypeNumber, R as RichTypeAny } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphPointerOverEventBlock extends FlowGraphEventBlock {
  constructor(config) {
    super(config);
    this.type = "PointerOver";
    this.pointerId = this.registerDataOutput("pointerId", RichTypeNumber);
    this.targetMesh = this.registerDataInput("targetMesh", RichTypeAny, config?.targetMesh);
    this.meshUnderPointer = this.registerDataOutput("meshUnderPointer", RichTypeAny);
  }
  _executeEvent(context, payload) {
    const mesh = this.targetMesh.getValue(context);
    this.meshUnderPointer.setValue(payload.mesh, context);
    const skipEvent = payload.out && _IsDescendantOf(payload.out, mesh);
    this.pointerId.setValue(payload.pointerId, context);
    if (!skipEvent && (payload.mesh === mesh || _IsDescendantOf(payload.mesh, mesh))) {
      this._execute(context);
      return !this.config?.stopPropagation;
    }
    return true;
  }
  _preparePendingTasks(_context) {
  }
  _cancelPendingTasks(_context) {
  }
  getClassName() {
    return "FlowGraphPointerOverEventBlock";
  }
}
RegisterClass("FlowGraphPointerOverEventBlock", FlowGraphPointerOverEventBlock);
export {
  FlowGraphPointerOverEventBlock
};
//# sourceMappingURL=CZigzoLj.js.map
