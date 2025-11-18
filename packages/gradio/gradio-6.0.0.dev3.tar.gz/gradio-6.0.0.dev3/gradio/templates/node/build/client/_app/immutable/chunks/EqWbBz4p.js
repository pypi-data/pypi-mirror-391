import { c as FlowGraphEventBlock, _ as _IsDescendantOf } from "./CWCX69Ol.js";
import { b as RichTypeNumber, R as RichTypeAny } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphPointerOutEventBlock extends FlowGraphEventBlock {
  constructor(config) {
    super(config);
    this.type = "PointerOut";
    this.pointerId = this.registerDataOutput("pointerId", RichTypeNumber);
    this.targetMesh = this.registerDataInput("targetMesh", RichTypeAny, config?.targetMesh);
    this.meshOutOfPointer = this.registerDataOutput("meshOutOfPointer", RichTypeAny);
  }
  _executeEvent(context, payload) {
    const mesh = this.targetMesh.getValue(context);
    this.meshOutOfPointer.setValue(payload.mesh, context);
    this.pointerId.setValue(payload.pointerId, context);
    const skipEvent = payload.over && _IsDescendantOf(payload.mesh, mesh);
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
    return "FlowGraphPointerOutEventBlock";
  }
}
RegisterClass("FlowGraphPointerOutEventBlock", FlowGraphPointerOutEventBlock);
export {
  FlowGraphPointerOutEventBlock
};
//# sourceMappingURL=EqWbBz4p.js.map
