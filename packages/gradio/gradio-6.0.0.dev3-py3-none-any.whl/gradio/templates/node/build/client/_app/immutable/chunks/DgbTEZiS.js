import { aN as unregisterGLTFExtension, aO as registerGLTFExtension } from "./f5NiF4Sn.js";
import { a as addNewInteractivityFlowGraphMapping } from "./CERZDFgL.js";
import { A as AddObjectAccessorToKey } from "./BPsPsVTI.js";
const NAME = "KHR_node_selectability";
addNewInteractivityFlowGraphMapping("event/onSelect", NAME, {
  // using GetVariable as the nodeIndex is a configuration and not a value (i.e. it's not mutable)
  blocks: ["FlowGraphMeshPickEventBlock", "FlowGraphGetVariableBlock", "FlowGraphIndexOfBlock", "KHR_interactivity/FlowGraphGLTFDataProvider"],
  configuration: {
    stopPropagation: { name: "stopPropagation" },
    nodeIndex: {
      name: "variable",
      toBlock: "FlowGraphGetVariableBlock",
      dataTransformer(data) {
        return ["pickedMesh_" + data[0]];
      }
    }
  },
  outputs: {
    values: {
      selectedNodeIndex: {
        name: "index",
        toBlock: "FlowGraphIndexOfBlock"
        /* FlowGraphBlockNames.IndexOf */
      },
      controllerIndex: { name: "pointerId" },
      selectionPoint: { name: "pickedPoint" },
      selectionRayOrigin: { name: "pickOrigin" }
    },
    flows: {
      out: { name: "done" }
    }
  },
  interBlockConnectors: [
    {
      input: "asset",
      output: "value",
      inputBlockIndex: 0,
      outputBlockIndex: 1,
      isVariable: true
    },
    {
      input: "array",
      output: "nodes",
      inputBlockIndex: 2,
      outputBlockIndex: 3,
      isVariable: true
    },
    {
      input: "object",
      output: "pickedMesh",
      inputBlockIndex: 2,
      outputBlockIndex: 0,
      isVariable: true
    }
  ],
  extraProcessor(gltfBlock, _declaration, _mapping, _arrays, serializedObjects, context, globalGLTF) {
    const serializedObject = serializedObjects[serializedObjects.length - 1];
    serializedObject.config = serializedObject.config || {};
    serializedObject.config.glTF = globalGLTF;
    const nodeIndex = gltfBlock.configuration?.["nodeIndex"]?.value[0];
    if (nodeIndex === void 0 || typeof nodeIndex !== "number") {
      throw new Error("nodeIndex not found in configuration");
    }
    const variableName = "pickedMesh_" + nodeIndex;
    serializedObjects[1].config.variable = variableName;
    context._userVariables[variableName] = {
      className: "Mesh",
      id: globalGLTF?.nodes?.[nodeIndex]._babylonTransformNode?.id,
      uniqueId: globalGLTF?.nodes?.[nodeIndex]._babylonTransformNode?.uniqueId
    };
    return serializedObjects;
  }
});
AddObjectAccessorToKey("/nodes/{}/extensions/KHR_node_selectability/selectable", {
  get: (node) => {
    const tn = node._babylonTransformNode;
    if (tn && tn.isPickable !== void 0) {
      return tn.isPickable;
    }
    return true;
  },
  set: (value, node) => {
    node._primitiveBabylonMeshes?.forEach((mesh) => {
      mesh.isPickable = value;
    });
  },
  getTarget: (node) => node._babylonTransformNode,
  getPropertyName: [() => "isPickable"],
  type: "boolean"
});
class KHR_node_selectability {
  /**
   * @internal
   */
  constructor(loader) {
    this.name = NAME;
    this._loader = loader;
    this.enabled = loader.isExtensionUsed(NAME);
  }
  // eslint-disable-next-line @typescript-eslint/naming-convention, @typescript-eslint/no-misused-promises
  async onReady() {
    this._loader.gltf.nodes?.forEach((node) => {
      if (node.extensions?.KHR_node_selectability && node.extensions?.KHR_node_selectability.selectable === false) {
        node._babylonTransformNode?.getChildMeshes().forEach((mesh) => {
          mesh.isPickable = false;
        });
      }
    });
  }
  dispose() {
    this._loader = null;
  }
}
unregisterGLTFExtension(NAME);
registerGLTFExtension(NAME, true, (loader) => new KHR_node_selectability(loader));
export {
  KHR_node_selectability
};
//# sourceMappingURL=DgbTEZiS.js.map
