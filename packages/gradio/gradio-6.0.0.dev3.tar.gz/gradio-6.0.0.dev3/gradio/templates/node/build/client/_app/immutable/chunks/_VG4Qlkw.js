import { b as FlowGraphExecutionBlockWithOutSignal } from "./CWCX69Ol.js";
import { R as RichTypeAny } from "./CERZDFgL.js";
import { R as RegisterClass } from "./f5NiF4Sn.js";
class FlowGraphPauseAnimationBlock extends FlowGraphExecutionBlockWithOutSignal {
  constructor(config) {
    super(config);
    this.animationToPause = this.registerDataInput("animationToPause", RichTypeAny);
  }
  _execute(context) {
    const animationToPauseValue = this.animationToPause.getValue(context);
    animationToPauseValue.pause();
    this.out._activateSignal(context);
  }
  /**
   * @returns class name of the block.
   */
  getClassName() {
    return "FlowGraphPauseAnimationBlock";
  }
}
RegisterClass("FlowGraphPauseAnimationBlock", FlowGraphPauseAnimationBlock);
export {
  FlowGraphPauseAnimationBlock
};
//# sourceMappingURL=_VG4Qlkw.js.map
