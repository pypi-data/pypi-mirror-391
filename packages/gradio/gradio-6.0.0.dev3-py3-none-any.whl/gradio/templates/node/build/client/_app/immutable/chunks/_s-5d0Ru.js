import { c as FlowGraphEventBlock, _ as _IsDescendantOf } from "./CWCX69Ol.js";
import { aX as PointerEventTypes, R as RegisterClass } from "./f5NiF4Sn.js";
import { R as RichTypeAny, e as RichTypeVector3, b as RichTypeNumber } from "./CERZDFgL.js";
class FlowGraphMeshPickEventBlock extends FlowGraphEventBlock {
  constructor(config) {
    super(config);
    this.config = config;
    this.type = "MeshPick";
    this.asset = this.registerDataInput("asset", RichTypeAny, config?.targetMesh);
    this.pickedPoint = this.registerDataOutput("pickedPoint", RichTypeVector3);
    this.pickOrigin = this.registerDataOutput("pickOrigin", RichTypeVector3);
    this.pointerId = this.registerDataOutput("pointerId", RichTypeNumber);
    this.pickedMesh = this.registerDataOutput("pickedMesh", RichTypeAny);
    this.pointerType = this.registerDataInput("pointerType", RichTypeAny, PointerEventTypes.POINTERPICK);
  }
  _getReferencedMesh(context) {
    return this.asset.getValue(context);
  }
  _executeEvent(context, pickedInfo) {
    const pointerType = this.pointerType.getValue(context);
    if (pointerType !== pickedInfo.type) {
      return true;
    }
    const mesh = this._getReferencedMesh(context);
    if (mesh && pickedInfo.pickInfo?.pickedMesh && (pickedInfo.pickInfo?.pickedMesh === mesh || _IsDescendantOf(pickedInfo.pickInfo?.pickedMesh, mesh))) {
      this.pointerId.setValue(pickedInfo.event.pointerId, context);
      this.pickOrigin.setValue(pickedInfo.pickInfo.ray?.origin, context);
      this.pickedPoint.setValue(pickedInfo.pickInfo.pickedPoint, context);
      this.pickedMesh.setValue(pickedInfo.pickInfo.pickedMesh, context);
      this._execute(context);
      return !this.config?.stopPropagation;
    } else {
      this.pointerId.resetToDefaultValue(context);
      this.pickOrigin.resetToDefaultValue(context);
      this.pickedPoint.resetToDefaultValue(context);
      this.pickedMesh.resetToDefaultValue(context);
    }
    return true;
  }
  /**
   * @internal
   */
  _preparePendingTasks(_context) {
  }
  /**
   * @internal
   */
  _cancelPendingTasks(_context) {
  }
  /**
   * @returns class name of the block.
   */
  getClassName() {
    return "FlowGraphMeshPickEventBlock";
  }
}
RegisterClass("FlowGraphMeshPickEventBlock", FlowGraphMeshPickEventBlock);
export {
  FlowGraphMeshPickEventBlock
};
//# sourceMappingURL=_s-5d0Ru.js.map
