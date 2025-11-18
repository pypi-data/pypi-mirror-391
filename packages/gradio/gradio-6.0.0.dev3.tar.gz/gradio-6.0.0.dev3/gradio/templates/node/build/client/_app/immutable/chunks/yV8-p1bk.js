import { F as FlowGraphBlock } from "./CWCX69Ol.js";
import { R as RichTypeAny } from "./CERZDFgL.js";
class FlowGraphGLTFDataProvider extends FlowGraphBlock {
  constructor(config) {
    super();
    const glTF = config.glTF;
    const animationGroups = glTF.animations?.map((a) => a._babylonAnimationGroup) || [];
    this.animationGroups = this.registerDataOutput("animationGroups", RichTypeAny, animationGroups);
    const nodes = glTF.nodes?.map((n) => n._babylonTransformNode) || [];
    this.nodes = this.registerDataOutput("nodes", RichTypeAny, nodes);
  }
  getClassName() {
    return "FlowGraphGLTFDataProvider";
  }
}
export {
  FlowGraphGLTFDataProvider
};
//# sourceMappingURL=yV8-p1bk.js.map
