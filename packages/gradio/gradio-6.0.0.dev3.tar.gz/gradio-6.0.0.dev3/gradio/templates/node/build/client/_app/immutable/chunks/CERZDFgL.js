import { R as RegisterClass, ap as Vector2, V as Vector3, Q as Quaternion, M as Matrix, aq as Vector4, bh as Color4, F as Color3, L as Logger } from "./f5NiF4Sn.js";
class FlowGraphInteger {
  constructor(value) {
    this.value = this._toInt(value);
  }
  /**
   * Converts a float to an integer.
   * @param n the float to convert
   * @returns the result of n | 0 - converting it to a int
   */
  _toInt(n) {
    return n | 0;
  }
  /**
   * Adds two integers together.
   * @param other the other integer to add
   * @returns a FlowGraphInteger with the result of the addition
   */
  add(other) {
    return new FlowGraphInteger(this.value + other.value);
  }
  /**
   * Subtracts two integers.
   * @param other the other integer to subtract
   * @returns a FlowGraphInteger with the result of the subtraction
   */
  subtract(other) {
    return new FlowGraphInteger(this.value - other.value);
  }
  /**
   * Multiplies two integers.
   * @param other the other integer to multiply
   * @returns a FlowGraphInteger with the result of the multiplication
   */
  multiply(other) {
    return new FlowGraphInteger(Math.imul(this.value, other.value));
  }
  /**
   * Divides two integers.
   * @param other the other integer to divide
   * @returns a FlowGraphInteger with the result of the division
   */
  divide(other) {
    return new FlowGraphInteger(this.value / other.value);
  }
  /**
   * The class name of this type.
   * @returns
   */
  getClassName() {
    return FlowGraphInteger.ClassName;
  }
  /**
   * Compares two integers for equality.
   * @param other the other integer to compare
   * @returns
   */
  equals(other) {
    return this.value === other.value;
  }
  /**
   * Parses a FlowGraphInteger from a serialization object.
   * @param value te number to parse
   * @returns
   */
  static FromValue(value) {
    return new FlowGraphInteger(value);
  }
  toString() {
    return this.value.toString();
  }
}
FlowGraphInteger.ClassName = "FlowGraphInteger";
RegisterClass("FlowGraphInteger", FlowGraphInteger);
class FlowGraphMatrix2D {
  constructor(m = [1, 0, 0, 1]) {
    this._m = m;
  }
  get m() {
    return this._m;
  }
  transformVector(v) {
    return this.transformVectorToRef(v, new Vector2());
  }
  transformVectorToRef(v, result) {
    result.x = v.x * this._m[0] + v.y * this._m[1];
    result.y = v.x * this._m[2] + v.y * this._m[3];
    return result;
  }
  asArray() {
    return this.toArray();
  }
  toArray(emptyArray = []) {
    for (let i = 0; i < 4; i++) {
      emptyArray[i] = this._m[i];
    }
    return emptyArray;
  }
  fromArray(array) {
    for (let i = 0; i < 4; i++) {
      this._m[i] = array[i];
    }
    return this;
  }
  multiplyToRef(other, result) {
    const otherMatrix = other._m;
    const thisMatrix = this._m;
    const r = result._m;
    r[0] = otherMatrix[0] * thisMatrix[0] + otherMatrix[1] * thisMatrix[2];
    r[1] = otherMatrix[0] * thisMatrix[1] + otherMatrix[1] * thisMatrix[3];
    r[2] = otherMatrix[2] * thisMatrix[0] + otherMatrix[3] * thisMatrix[2];
    r[3] = otherMatrix[2] * thisMatrix[1] + otherMatrix[3] * thisMatrix[3];
    return result;
  }
  multiply(other) {
    return this.multiplyToRef(other, new FlowGraphMatrix2D());
  }
  divideToRef(other, result) {
    const m = this._m;
    const o = other._m;
    const r = result._m;
    r[0] = m[0] / o[0];
    r[1] = m[1] / o[1];
    r[2] = m[2] / o[2];
    r[3] = m[3] / o[3];
    return result;
  }
  divide(other) {
    return this.divideToRef(other, new FlowGraphMatrix2D());
  }
  addToRef(other, result) {
    const m = this._m;
    const o = other.m;
    const r = result.m;
    r[0] = m[0] + o[0];
    r[1] = m[1] + o[1];
    r[2] = m[2] + o[2];
    r[3] = m[3] + o[3];
    return result;
  }
  add(other) {
    return this.addToRef(other, new FlowGraphMatrix2D());
  }
  subtractToRef(other, result) {
    const m = this._m;
    const o = other.m;
    const r = result.m;
    r[0] = m[0] - o[0];
    r[1] = m[1] - o[1];
    r[2] = m[2] - o[2];
    r[3] = m[3] - o[3];
    return result;
  }
  subtract(other) {
    return this.subtractToRef(other, new FlowGraphMatrix2D());
  }
  transpose() {
    const m = this._m;
    return new FlowGraphMatrix2D([m[0], m[2], m[1], m[3]]);
  }
  determinant() {
    const m = this._m;
    return m[0] * m[3] - m[1] * m[2];
  }
  inverse() {
    const det = this.determinant();
    if (det === 0) {
      throw new Error("Matrix is not invertible");
    }
    const m = this._m;
    const invDet = 1 / det;
    return new FlowGraphMatrix2D([m[3] * invDet, -m[1] * invDet, -m[2] * invDet, m[0] * invDet]);
  }
  equals(other, epsilon = 0) {
    const m = this._m;
    const o = other.m;
    if (epsilon === 0) {
      return m[0] === o[0] && m[1] === o[1] && m[2] === o[2] && m[3] === o[3];
    }
    return Math.abs(m[0] - o[0]) < epsilon && Math.abs(m[1] - o[1]) < epsilon && Math.abs(m[2] - o[2]) < epsilon && Math.abs(m[3] - o[3]) < epsilon;
  }
  getClassName() {
    return "FlowGraphMatrix2D";
  }
  toString() {
    return `FlowGraphMatrix2D(${this._m.join(", ")})`;
  }
}
class FlowGraphMatrix3D {
  constructor(array = [1, 0, 0, 0, 1, 0, 0, 0, 1]) {
    this._m = array;
  }
  get m() {
    return this._m;
  }
  transformVector(v) {
    return this.transformVectorToRef(v, new Vector3());
  }
  transformVectorToRef(v, result) {
    const m = this._m;
    result.x = v.x * m[0] + v.y * m[1] + v.z * m[2];
    result.y = v.x * m[3] + v.y * m[4] + v.z * m[5];
    result.z = v.x * m[6] + v.y * m[7] + v.z * m[8];
    return result;
  }
  multiplyToRef(other, result) {
    const otherMatrix = other._m;
    const thisMatrix = this._m;
    const r = result.m;
    r[0] = otherMatrix[0] * thisMatrix[0] + otherMatrix[1] * thisMatrix[3] + otherMatrix[2] * thisMatrix[6];
    r[1] = otherMatrix[0] * thisMatrix[1] + otherMatrix[1] * thisMatrix[4] + otherMatrix[2] * thisMatrix[7];
    r[2] = otherMatrix[0] * thisMatrix[2] + otherMatrix[1] * thisMatrix[5] + otherMatrix[2] * thisMatrix[8];
    r[3] = otherMatrix[3] * thisMatrix[0] + otherMatrix[4] * thisMatrix[3] + otherMatrix[5] * thisMatrix[6];
    r[4] = otherMatrix[3] * thisMatrix[1] + otherMatrix[4] * thisMatrix[4] + otherMatrix[5] * thisMatrix[7];
    r[5] = otherMatrix[3] * thisMatrix[2] + otherMatrix[4] * thisMatrix[5] + otherMatrix[5] * thisMatrix[8];
    r[6] = otherMatrix[6] * thisMatrix[0] + otherMatrix[7] * thisMatrix[3] + otherMatrix[8] * thisMatrix[6];
    r[7] = otherMatrix[6] * thisMatrix[1] + otherMatrix[7] * thisMatrix[4] + otherMatrix[8] * thisMatrix[7];
    r[8] = otherMatrix[6] * thisMatrix[2] + otherMatrix[7] * thisMatrix[5] + otherMatrix[8] * thisMatrix[8];
    return result;
  }
  multiply(other) {
    return this.multiplyToRef(other, new FlowGraphMatrix3D());
  }
  divideToRef(other, result) {
    const m = this._m;
    const o = other.m;
    const r = result.m;
    r[0] = m[0] / o[0];
    r[1] = m[1] / o[1];
    r[2] = m[2] / o[2];
    r[3] = m[3] / o[3];
    r[4] = m[4] / o[4];
    r[5] = m[5] / o[5];
    r[6] = m[6] / o[6];
    r[7] = m[7] / o[7];
    r[8] = m[8] / o[8];
    return result;
  }
  divide(other) {
    return this.divideToRef(other, new FlowGraphMatrix3D());
  }
  addToRef(other, result) {
    const m = this._m;
    const o = other.m;
    const r = result.m;
    r[0] = m[0] + o[0];
    r[1] = m[1] + o[1];
    r[2] = m[2] + o[2];
    r[3] = m[3] + o[3];
    r[4] = m[4] + o[4];
    r[5] = m[5] + o[5];
    r[6] = m[6] + o[6];
    r[7] = m[7] + o[7];
    r[8] = m[8] + o[8];
    return result;
  }
  add(other) {
    return this.addToRef(other, new FlowGraphMatrix3D());
  }
  subtractToRef(other, result) {
    const m = this._m;
    const o = other.m;
    const r = result.m;
    r[0] = m[0] - o[0];
    r[1] = m[1] - o[1];
    r[2] = m[2] - o[2];
    r[3] = m[3] - o[3];
    r[4] = m[4] - o[4];
    r[5] = m[5] - o[5];
    r[6] = m[6] - o[6];
    r[7] = m[7] - o[7];
    r[8] = m[8] - o[8];
    return result;
  }
  subtract(other) {
    return this.subtractToRef(other, new FlowGraphMatrix3D());
  }
  toArray(emptyArray = []) {
    for (let i = 0; i < 9; i++) {
      emptyArray[i] = this._m[i];
    }
    return emptyArray;
  }
  asArray() {
    return this.toArray();
  }
  fromArray(array) {
    for (let i = 0; i < 9; i++) {
      this._m[i] = array[i];
    }
    return this;
  }
  transpose() {
    const m = this._m;
    return new FlowGraphMatrix3D([m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8]]);
  }
  determinant() {
    const m = this._m;
    return m[0] * (m[4] * m[8] - m[5] * m[7]) - m[1] * (m[3] * m[8] - m[5] * m[6]) + m[2] * (m[3] * m[7] - m[4] * m[6]);
  }
  inverse() {
    const det = this.determinant();
    if (det === 0) {
      throw new Error("Matrix is not invertible");
    }
    const m = this._m;
    const invDet = 1 / det;
    return new FlowGraphMatrix3D([
      (m[4] * m[8] - m[5] * m[7]) * invDet,
      (m[2] * m[7] - m[1] * m[8]) * invDet,
      (m[1] * m[5] - m[2] * m[4]) * invDet,
      (m[5] * m[6] - m[3] * m[8]) * invDet,
      (m[0] * m[8] - m[2] * m[6]) * invDet,
      (m[2] * m[3] - m[0] * m[5]) * invDet,
      (m[3] * m[7] - m[4] * m[6]) * invDet,
      (m[1] * m[6] - m[0] * m[7]) * invDet,
      (m[0] * m[4] - m[1] * m[3]) * invDet
    ]);
  }
  equals(other, epsilon = 0) {
    const m = this._m;
    const o = other.m;
    if (epsilon === 0) {
      return m[0] === o[0] && m[1] === o[1] && m[2] === o[2] && m[3] === o[3] && m[4] === o[4] && m[5] === o[5] && m[6] === o[6] && m[7] === o[7] && m[8] === o[8];
    }
    return Math.abs(m[0] - o[0]) < epsilon && Math.abs(m[1] - o[1]) < epsilon && Math.abs(m[2] - o[2]) < epsilon && Math.abs(m[3] - o[3]) < epsilon && Math.abs(m[4] - o[4]) < epsilon && Math.abs(m[5] - o[5]) < epsilon && Math.abs(m[6] - o[6]) < epsilon && Math.abs(m[7] - o[7]) < epsilon && Math.abs(m[8] - o[8]) < epsilon;
  }
  getClassName() {
    return "FlowGraphMatrix3D";
  }
  toString() {
    return `FlowGraphMatrix3D(${this._m.join(", ")})`;
  }
}
var FlowGraphTypes;
(function(FlowGraphTypes2) {
  FlowGraphTypes2["Any"] = "any";
  FlowGraphTypes2["String"] = "string";
  FlowGraphTypes2["Number"] = "number";
  FlowGraphTypes2["Boolean"] = "boolean";
  FlowGraphTypes2["Object"] = "object";
  FlowGraphTypes2["Integer"] = "FlowGraphInteger";
  FlowGraphTypes2["Vector2"] = "Vector2";
  FlowGraphTypes2["Vector3"] = "Vector3";
  FlowGraphTypes2["Vector4"] = "Vector4";
  FlowGraphTypes2["Quaternion"] = "Quaternion";
  FlowGraphTypes2["Matrix"] = "Matrix";
  FlowGraphTypes2["Matrix2D"] = "Matrix2D";
  FlowGraphTypes2["Matrix3D"] = "Matrix3D";
  FlowGraphTypes2["Color3"] = "Color3";
  FlowGraphTypes2["Color4"] = "Color4";
})(FlowGraphTypes || (FlowGraphTypes = {}));
class RichType {
  constructor(typeName, defaultValue, animationType = -1) {
    this.typeName = typeName;
    this.defaultValue = defaultValue;
    this.animationType = animationType;
  }
  /**
   * Serializes this rich type into a serialization object.
   * @param serializationObject the object to serialize to
   */
  serialize(serializationObject) {
    serializationObject.typeName = this.typeName;
    serializationObject.defaultValue = this.defaultValue;
  }
}
const RichTypeAny = new RichType("any", void 0);
const RichTypeString = new RichType("string", "");
const RichTypeNumber = new RichType("number", 0, 0);
const RichTypeBoolean = new RichType("boolean", false);
const RichTypeVector2 = new RichType("Vector2", Vector2.Zero(), 5);
const RichTypeVector3 = new RichType("Vector3", Vector3.Zero(), 1);
const RichTypeVector4 = new RichType("Vector4", Vector4.Zero());
const RichTypeMatrix = new RichType("Matrix", Matrix.Identity(), 3);
const RichTypeMatrix2D = new RichType("Matrix2D", new FlowGraphMatrix2D());
const RichTypeMatrix3D = new RichType("Matrix3D", new FlowGraphMatrix3D());
const RichTypeColor3 = new RichType("Color3", Color3.Black(), 4);
const RichTypeColor4 = new RichType("Color4", new Color4(0, 0, 0, 0), 7);
const RichTypeQuaternion = new RichType("Quaternion", Quaternion.Identity(), 2);
RichTypeQuaternion.typeTransformer = (value) => {
  if (value.getClassName) {
    if (value.getClassName() === "Vector4") {
      return Quaternion.FromArray(value.asArray());
    } else if (value.getClassName() === "Vector3") {
      return Quaternion.FromEulerVector(value);
    } else if (value.getClassName() === "Matrix") {
      return Quaternion.FromRotationMatrix(value);
    }
  }
  return value;
};
const RichTypeFlowGraphInteger = new RichType("FlowGraphInteger", new FlowGraphInteger(0), 0);
function getRichTypeFromValue(value) {
  const anyValue = value;
  switch (typeof value) {
    case "string":
      return RichTypeString;
    case "number":
      return RichTypeNumber;
    case "boolean":
      return RichTypeBoolean;
    case "object":
      if (anyValue.getClassName) {
        switch (anyValue.getClassName()) {
          case "Vector2":
            return RichTypeVector2;
          case "Vector3":
            return RichTypeVector3;
          case "Vector4":
            return RichTypeVector4;
          case "Matrix":
            return RichTypeMatrix;
          case "Color3":
            return RichTypeColor3;
          case "Color4":
            return RichTypeColor4;
          case "Quaternion":
            return RichTypeQuaternion;
          case "FlowGraphInteger":
            return RichTypeFlowGraphInteger;
          case "Matrix2D":
            return RichTypeMatrix2D;
          case "Matrix3D":
            return RichTypeMatrix3D;
        }
      }
      return RichTypeAny;
    default:
      return RichTypeAny;
  }
}
function getRichTypeByFlowGraphType(flowGraphType) {
  switch (flowGraphType) {
    case "string":
      return RichTypeString;
    case "number":
      return RichTypeNumber;
    case "boolean":
      return RichTypeBoolean;
    case "Vector2":
      return RichTypeVector2;
    case "Vector3":
      return RichTypeVector3;
    case "Vector4":
      return RichTypeVector4;
    case "Matrix":
      return RichTypeMatrix;
    case "Color3":
      return RichTypeColor3;
    case "Color4":
      return RichTypeColor4;
    case "Quaternion":
      return RichTypeQuaternion;
    case "FlowGraphInteger":
      return RichTypeFlowGraphInteger;
    case "Matrix2D":
      return RichTypeMatrix2D;
    case "Matrix3D":
      return RichTypeMatrix3D;
    default:
      return RichTypeAny;
  }
}
function getAnimationTypeByFlowGraphType(flowGraphType) {
  switch (flowGraphType) {
    case "number":
      return 0;
    case "Vector2":
      return 5;
    case "Vector3":
      return 1;
    case "Matrix":
      return 3;
    case "Color3":
      return 4;
    case "Color4":
      return 7;
    case "Quaternion":
      return 2;
    default:
      return 0;
  }
}
function getRichTypeByAnimationType(animationType) {
  switch (animationType) {
    case 0:
      return RichTypeNumber;
    case 5:
      return RichTypeVector2;
    case 1:
      return RichTypeVector3;
    case 3:
      return RichTypeMatrix;
    case 4:
      return RichTypeColor3;
    case 7:
      return RichTypeColor4;
    case 2:
      return RichTypeQuaternion;
    default:
      return RichTypeAny;
  }
}
function getMappingForFullOperationName(fullOperationName) {
  const [op, extension] = fullOperationName.split(":");
  return getMappingForDeclaration({ op, extension });
}
function getMappingForDeclaration(declaration, returnNoOpIfNotAvailable = true) {
  const mapping = declaration.extension ? gltfExtensionsToFlowGraphMapping[declaration.extension]?.[declaration.op] : gltfToFlowGraphMapping[declaration.op];
  if (!mapping) {
    Logger.Warn(`No mapping found for operation ${declaration.op} and extension ${declaration.extension || "KHR_interactivity"}`);
    if (returnNoOpIfNotAvailable) {
      const inputs = {};
      const outputs = {
        flows: {}
      };
      if (declaration.inputValueSockets) {
        inputs.values = {};
        for (const key in declaration.inputValueSockets) {
          inputs.values[key] = {
            name: key
          };
        }
      }
      if (declaration.outputValueSockets) {
        outputs.values = {};
        Object.keys(declaration.outputValueSockets).forEach((key) => {
          outputs.values[key] = {
            name: key
          };
        });
      }
      return {
        blocks: [],
        // no blocks, just mapping
        inputs,
        outputs
      };
    }
  }
  return mapping;
}
function addNewInteractivityFlowGraphMapping(key, extension, mapping) {
  gltfExtensionsToFlowGraphMapping[extension] || (gltfExtensionsToFlowGraphMapping[extension] = {});
  gltfExtensionsToFlowGraphMapping[extension][key] = mapping;
}
const gltfExtensionsToFlowGraphMapping = {
  /**
   * This is the BABYLON extension for glTF interactivity.
   * It defines babylon-specific blocks and operations.
   */
  BABYLON: {
    /**
     * flow/log is a flow node that logs input to the console.
     * It has "in" and "out" flows, and takes a message as input.
     * The message can be any type of value.
     * The message is logged to the console when the "in" flow is triggered.
     * The "out" flow is triggered when the message is logged.
     */
    "flow/log": {
      blocks: [
        "FlowGraphConsoleLogBlock"
        /* FlowGraphBlockNames.ConsoleLog */
      ],
      inputs: {
        values: {
          message: { name: "message" }
        }
      }
    }
  }
};
const gltfToFlowGraphMapping = {
  "event/onStart": {
    blocks: [
      "FlowGraphSceneReadyEventBlock"
      /* FlowGraphBlockNames.SceneReadyEvent */
    ],
    outputs: {
      flows: {
        out: { name: "done" }
      }
    }
  },
  "event/onTick": {
    blocks: [
      "FlowGraphSceneTickEventBlock"
      /* FlowGraphBlockNames.SceneTickEvent */
    ],
    inputs: {},
    outputs: {
      values: {
        timeSinceLastTick: {
          name: "deltaTime",
          gltfType: "number"
          /*, dataTransformer: (time: number) => time / 1000*/
        }
      },
      flows: {
        out: { name: "done" }
      }
    }
  },
  "event/send": {
    blocks: [
      "FlowGraphSendCustomEventBlock"
      /* FlowGraphBlockNames.SendCustomEvent */
    ],
    extraProcessor(gltfBlock, declaration, _mapping, parser, serializedObjects) {
      if (declaration.op !== "event/send" || !gltfBlock.configuration || Object.keys(gltfBlock.configuration).length !== 1) {
        throw new Error("Receive event should have a single configuration object, the event itself");
      }
      const eventConfiguration = gltfBlock.configuration["event"];
      const eventId = eventConfiguration.value[0];
      if (typeof eventId !== "number") {
        throw new Error("Event id should be a number");
      }
      const event = parser.arrays.events[eventId];
      const serializedObject = serializedObjects[0];
      serializedObject.config || (serializedObject.config = {});
      serializedObject.config.eventId = event.eventId;
      serializedObject.config.eventData = event.eventData;
      return serializedObjects;
    }
  },
  "event/receive": {
    blocks: [
      "FlowGraphReceiveCustomEventBlock"
      /* FlowGraphBlockNames.ReceiveCustomEvent */
    ],
    outputs: {
      flows: {
        out: { name: "done" }
      }
    },
    validation(gltfBlock, interactivityGraph) {
      if (!gltfBlock.configuration) {
        Logger.Error("Receive event should have a configuration object");
        return { valid: false, error: "Receive event should have a configuration object" };
      }
      const eventConfiguration = gltfBlock.configuration["event"];
      if (!eventConfiguration) {
        Logger.Error("Receive event should have a single configuration object, the event itself");
        return { valid: false, error: "Receive event should have a single configuration object, the event itself" };
      }
      const eventId = eventConfiguration.value[0];
      if (typeof eventId !== "number") {
        Logger.Error("Event id should be a number");
        return { valid: false, error: "Event id should be a number" };
      }
      const event = interactivityGraph.events?.[eventId];
      if (!event) {
        Logger.Error(`Event with id ${eventId} not found`);
        return { valid: false, error: `Event with id ${eventId} not found` };
      }
      return { valid: true };
    },
    extraProcessor(gltfBlock, declaration, _mapping, parser, serializedObjects) {
      if (declaration.op !== "event/receive" || !gltfBlock.configuration || Object.keys(gltfBlock.configuration).length !== 1) {
        throw new Error("Receive event should have a single configuration object, the event itself");
      }
      const eventConfiguration = gltfBlock.configuration["event"];
      const eventId = eventConfiguration.value[0];
      if (typeof eventId !== "number") {
        throw new Error("Event id should be a number");
      }
      const event = parser.arrays.events[eventId];
      const serializedObject = serializedObjects[0];
      serializedObject.config || (serializedObject.config = {});
      serializedObject.config.eventId = event.eventId;
      serializedObject.config.eventData = event.eventData;
      return serializedObjects;
    }
  },
  "math/E": getSimpleInputMapping(
    "FlowGraphEBlock"
    /* FlowGraphBlockNames.E */
  ),
  "math/Pi": getSimpleInputMapping(
    "FlowGraphPIBlock"
    /* FlowGraphBlockNames.PI */
  ),
  "math/Inf": getSimpleInputMapping(
    "FlowGraphInfBlock"
    /* FlowGraphBlockNames.Inf */
  ),
  "math/NaN": getSimpleInputMapping(
    "FlowGraphNaNBlock"
    /* FlowGraphBlockNames.NaN */
  ),
  "math/abs": getSimpleInputMapping(
    "FlowGraphAbsBlock"
    /* FlowGraphBlockNames.Abs */
  ),
  "math/sign": getSimpleInputMapping(
    "FlowGraphSignBlock"
    /* FlowGraphBlockNames.Sign */
  ),
  "math/trunc": getSimpleInputMapping(
    "FlowGraphTruncBlock"
    /* FlowGraphBlockNames.Trunc */
  ),
  "math/floor": getSimpleInputMapping(
    "FlowGraphFloorBlock"
    /* FlowGraphBlockNames.Floor */
  ),
  "math/ceil": getSimpleInputMapping(
    "FlowGraphCeilBlock"
    /* FlowGraphBlockNames.Ceil */
  ),
  "math/round": {
    blocks: [
      "FlowGraphRoundBlock"
      /* FlowGraphBlockNames.Round */
    ],
    configuration: {},
    inputs: {
      values: {
        a: { name: "a" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(gltfBlock, declaration, _mapping, parser, serializedObjects) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      serializedObjects[0].config.roundHalfAwayFromZero = true;
      return serializedObjects;
    }
  },
  "math/fract": getSimpleInputMapping(
    "FlowGraphFractBlock"
    /* FlowGraphBlockNames.Fraction */
  ),
  "math/neg": getSimpleInputMapping(
    "FlowGraphNegationBlock"
    /* FlowGraphBlockNames.Negation */
  ),
  "math/add": getSimpleInputMapping("FlowGraphAddBlock", ["a", "b"], true),
  "math/sub": getSimpleInputMapping("FlowGraphSubtractBlock", ["a", "b"], true),
  "math/mul": {
    blocks: [
      "FlowGraphMultiplyBlock"
      /* FlowGraphBlockNames.Multiply */
    ],
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      serializedObjects[0].config.useMatrixPerComponent = true;
      serializedObjects[0].config.preventIntegerFloatArithmetic = true;
      let type = -1;
      Object.keys(_gltfBlock.values || {}).find((value) => {
        if (_gltfBlock.values?.[value].type !== void 0) {
          type = _gltfBlock.values[value].type;
          return true;
        }
        return false;
      });
      if (type !== -1) {
        serializedObjects[0].config.type = _parser.arrays.types[type].flowGraphType;
      }
      return serializedObjects;
    },
    validation(gltfBlock) {
      if (gltfBlock.values) {
        return ValidateTypes(gltfBlock);
      }
      return { valid: true };
    }
  },
  "math/div": getSimpleInputMapping("FlowGraphDivideBlock", ["a", "b"], true),
  "math/rem": getSimpleInputMapping("FlowGraphModuloBlock", ["a", "b"]),
  "math/min": getSimpleInputMapping("FlowGraphMinBlock", ["a", "b"]),
  "math/max": getSimpleInputMapping("FlowGraphMaxBlock", ["a", "b"]),
  "math/clamp": getSimpleInputMapping("FlowGraphClampBlock", ["a", "b", "c"]),
  "math/saturate": getSimpleInputMapping(
    "FlowGraphSaturateBlock"
    /* FlowGraphBlockNames.Saturate */
  ),
  "math/mix": getSimpleInputMapping("FlowGraphMathInterpolationBlock", ["a", "b", "c"]),
  "math/eq": getSimpleInputMapping("FlowGraphEqualityBlock", ["a", "b"]),
  "math/lt": getSimpleInputMapping("FlowGraphLessThanBlock", ["a", "b"]),
  "math/le": getSimpleInputMapping("FlowGraphLessThanOrEqualBlock", ["a", "b"]),
  "math/gt": getSimpleInputMapping("FlowGraphGreaterThanBlock", ["a", "b"]),
  "math/ge": getSimpleInputMapping("FlowGraphGreaterThanOrEqualBlock", ["a", "b"]),
  "math/isNaN": getSimpleInputMapping(
    "FlowGraphIsNaNBlock"
    /* FlowGraphBlockNames.IsNaN */
  ),
  "math/isInf": getSimpleInputMapping(
    "FlowGraphIsInfBlock"
    /* FlowGraphBlockNames.IsInfinity */
  ),
  "math/select": {
    blocks: [
      "FlowGraphConditionalBlock"
      /* FlowGraphBlockNames.Conditional */
    ],
    inputs: {
      values: {
        condition: { name: "condition" },
        // Should we validate those have the same type here, or assume it is already validated?
        a: { name: "onTrue" },
        b: { name: "onFalse" }
      }
    },
    outputs: {
      values: {
        value: { name: "output" }
      }
    }
  },
  "math/random": {
    blocks: [
      "FlowGraphRandomBlock"
      /* FlowGraphBlockNames.Random */
    ],
    outputs: {
      values: {
        value: { name: "value" }
      }
    }
  },
  "math/sin": getSimpleInputMapping(
    "FlowGraphSinBlock"
    /* FlowGraphBlockNames.Sin */
  ),
  "math/cos": getSimpleInputMapping(
    "FlowGraphCosBlock"
    /* FlowGraphBlockNames.Cos */
  ),
  "math/tan": getSimpleInputMapping(
    "FlowGraphTanBlock"
    /* FlowGraphBlockNames.Tan */
  ),
  "math/asin": getSimpleInputMapping(
    "FlowGraphASinBlock"
    /* FlowGraphBlockNames.Asin */
  ),
  "math/acos": getSimpleInputMapping(
    "FlowGraphACosBlock"
    /* FlowGraphBlockNames.Acos */
  ),
  "math/atan": getSimpleInputMapping(
    "FlowGraphATanBlock"
    /* FlowGraphBlockNames.Atan */
  ),
  "math/atan2": getSimpleInputMapping("FlowGraphATan2Block", ["a", "b"]),
  "math/sinh": getSimpleInputMapping(
    "FlowGraphSinhBlock"
    /* FlowGraphBlockNames.Sinh */
  ),
  "math/cosh": getSimpleInputMapping(
    "FlowGraphCoshBlock"
    /* FlowGraphBlockNames.Cosh */
  ),
  "math/tanh": getSimpleInputMapping(
    "FlowGraphTanhBlock"
    /* FlowGraphBlockNames.Tanh */
  ),
  "math/asinh": getSimpleInputMapping(
    "FlowGraphASinhBlock"
    /* FlowGraphBlockNames.Asinh */
  ),
  "math/acosh": getSimpleInputMapping(
    "FlowGraphACoshBlock"
    /* FlowGraphBlockNames.Acosh */
  ),
  "math/atanh": getSimpleInputMapping(
    "FlowGraphATanhBlock"
    /* FlowGraphBlockNames.Atanh */
  ),
  "math/exp": getSimpleInputMapping(
    "FlowGraphExponentialBlock"
    /* FlowGraphBlockNames.Exponential */
  ),
  "math/log": getSimpleInputMapping(
    "FlowGraphLogBlock"
    /* FlowGraphBlockNames.Log */
  ),
  "math/log2": getSimpleInputMapping(
    "FlowGraphLog2Block"
    /* FlowGraphBlockNames.Log2 */
  ),
  "math/log10": getSimpleInputMapping(
    "FlowGraphLog10Block"
    /* FlowGraphBlockNames.Log10 */
  ),
  "math/sqrt": getSimpleInputMapping(
    "FlowGraphSquareRootBlock"
    /* FlowGraphBlockNames.SquareRoot */
  ),
  "math/cbrt": getSimpleInputMapping(
    "FlowGraphCubeRootBlock"
    /* FlowGraphBlockNames.CubeRoot */
  ),
  "math/pow": getSimpleInputMapping("FlowGraphPowerBlock", ["a", "b"]),
  "math/length": getSimpleInputMapping(
    "FlowGraphLengthBlock"
    /* FlowGraphBlockNames.Length */
  ),
  "math/normalize": getSimpleInputMapping(
    "FlowGraphNormalizeBlock"
    /* FlowGraphBlockNames.Normalize */
  ),
  "math/dot": getSimpleInputMapping("FlowGraphDotBlock", ["a", "b"]),
  "math/cross": getSimpleInputMapping("FlowGraphCrossBlock", ["a", "b"]),
  "math/rotate2D": {
    blocks: [
      "FlowGraphRotate2DBlock"
      /* FlowGraphBlockNames.Rotate2D */
    ],
    inputs: {
      values: {
        a: { name: "a" },
        angle: { name: "b" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    }
  },
  "math/rotate3D": {
    blocks: [
      "FlowGraphRotate3DBlock"
      /* FlowGraphBlockNames.Rotate3D */
    ],
    inputs: {
      values: {
        a: { name: "a" },
        rotation: { name: "b" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    }
  },
  "math/transform": {
    // glTF transform is vectorN with matrixN
    blocks: [
      "FlowGraphTransformVectorBlock"
      /* FlowGraphBlockNames.TransformVector */
    ],
    inputs: {
      values: {
        a: { name: "a" },
        b: { name: "b" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    }
  },
  "math/combine2": {
    blocks: [
      "FlowGraphCombineVector2Block"
      /* FlowGraphBlockNames.CombineVector2 */
    ],
    inputs: {
      values: {
        a: { name: "input_0", gltfType: "number" },
        b: { name: "input_1", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    }
  },
  "math/combine3": {
    blocks: [
      "FlowGraphCombineVector3Block"
      /* FlowGraphBlockNames.CombineVector3 */
    ],
    inputs: {
      values: {
        a: { name: "input_0", gltfType: "number" },
        b: { name: "input_1", gltfType: "number" },
        c: { name: "input_2", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    }
  },
  "math/combine4": {
    blocks: [
      "FlowGraphCombineVector4Block"
      /* FlowGraphBlockNames.CombineVector4 */
    ],
    inputs: {
      values: {
        a: { name: "input_0", gltfType: "number" },
        b: { name: "input_1", gltfType: "number" },
        c: { name: "input_2", gltfType: "number" },
        d: { name: "input_3", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    }
  },
  // one input, N outputs! outputs named using numbers.
  "math/extract2": {
    blocks: [
      "FlowGraphExtractVector2Block"
      /* FlowGraphBlockNames.ExtractVector2 */
    ],
    inputs: {
      values: {
        a: { name: "input", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        "0": { name: "output_0" },
        "1": { name: "output_1" }
      }
    }
  },
  "math/extract3": {
    blocks: [
      "FlowGraphExtractVector3Block"
      /* FlowGraphBlockNames.ExtractVector3 */
    ],
    inputs: {
      values: {
        a: { name: "input", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        "0": { name: "output_0" },
        "1": { name: "output_1" },
        "2": { name: "output_2" }
      }
    }
  },
  "math/extract4": {
    blocks: [
      "FlowGraphExtractVector4Block"
      /* FlowGraphBlockNames.ExtractVector4 */
    ],
    inputs: {
      values: {
        a: { name: "input", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        "0": { name: "output_0" },
        "1": { name: "output_1" },
        "2": { name: "output_2" },
        "3": { name: "output_3" }
      }
    }
  },
  "math/transpose": getSimpleInputMapping(
    "FlowGraphTransposeBlock"
    /* FlowGraphBlockNames.Transpose */
  ),
  "math/determinant": getSimpleInputMapping(
    "FlowGraphDeterminantBlock"
    /* FlowGraphBlockNames.Determinant */
  ),
  "math/inverse": getSimpleInputMapping(
    "FlowGraphInvertMatrixBlock"
    /* FlowGraphBlockNames.InvertMatrix */
  ),
  "math/matMul": getSimpleInputMapping("FlowGraphMatrixMultiplicationBlock", ["a", "b"]),
  "math/matCompose": {
    blocks: [
      "FlowGraphMatrixCompose"
      /* FlowGraphBlockNames.MatrixCompose */
    ],
    inputs: {
      values: {
        translation: { name: "position", gltfType: "float3" },
        rotation: { name: "rotationQuaternion", gltfType: "float4" },
        scale: { name: "scaling", gltfType: "float3" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects, context) {
      const d = serializedObjects[0].dataInputs.find((input) => input.name === "rotationQuaternion");
      if (!d) {
        throw new Error("Rotation quaternion input not found");
      }
      if (context._connectionValues[d.uniqueId]) {
        context._connectionValues[d.uniqueId].type = "Quaternion";
      }
      return serializedObjects;
    }
  },
  "math/matDecompose": {
    blocks: [
      "FlowGraphMatrixDecompose"
      /* FlowGraphBlockNames.MatrixDecompose */
    ],
    inputs: {
      values: {
        a: { name: "input", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        translation: { name: "position" },
        rotation: { name: "rotationQuaternion" },
        scale: { name: "scaling" }
      }
    }
  },
  "math/quatConjugate": getSimpleInputMapping("FlowGraphConjugateBlock", ["a"]),
  "math/quatMul": {
    blocks: [
      "FlowGraphMultiplyBlock"
      /* FlowGraphBlockNames.Multiply */
    ],
    inputs: {
      values: {
        a: { name: "a", gltfType: "vector4" },
        b: { name: "b", gltfType: "vector4" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      serializedObjects[0].config.type = "Quaternion";
      return serializedObjects;
    }
  },
  "math/quatAngleBetween": getSimpleInputMapping("FlowGraphAngleBetweenBlock", ["a", "b"]),
  "math/quatFromAxisAngle": {
    blocks: [
      "FlowGraphQuaternionFromAxisAngleBlock"
      /* FlowGraphBlockNames.QuaternionFromAxisAngle */
    ],
    inputs: {
      values: {
        axis: { name: "a", gltfType: "float3" },
        angle: { name: "b", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    }
  },
  "math/quatToAxisAngle": getSimpleInputMapping("FlowGraphAxisAngleFromQuaternionBlock", ["a"]),
  "math/quatFromDirections": getSimpleInputMapping("FlowGraphQuaternionFromDirectionsBlock", ["a", "b"]),
  "math/combine2x2": {
    blocks: [
      "FlowGraphCombineMatrix2DBlock"
      /* FlowGraphBlockNames.CombineMatrix2D */
    ],
    inputs: {
      values: {
        a: { name: "input_0", gltfType: "number" },
        b: { name: "input_1", gltfType: "number" },
        c: { name: "input_2", gltfType: "number" },
        d: { name: "input_3", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      serializedObjects[0].config.inputIsColumnMajor = true;
      return serializedObjects;
    }
  },
  "math/extract2x2": {
    blocks: [
      "FlowGraphExtractMatrix2DBlock"
      /* FlowGraphBlockNames.ExtractMatrix2D */
    ],
    inputs: {
      values: {
        a: { name: "input", gltfType: "float2x2" }
      }
    },
    outputs: {
      values: {
        "0": { name: "output_0" },
        "1": { name: "output_1" },
        "2": { name: "output_2" },
        "3": { name: "output_3" }
      }
    }
  },
  "math/combine3x3": {
    blocks: [
      "FlowGraphCombineMatrix3DBlock"
      /* FlowGraphBlockNames.CombineMatrix3D */
    ],
    inputs: {
      values: {
        a: { name: "input_0", gltfType: "number" },
        b: { name: "input_1", gltfType: "number" },
        c: { name: "input_2", gltfType: "number" },
        d: { name: "input_3", gltfType: "number" },
        e: { name: "input_4", gltfType: "number" },
        f: { name: "input_5", gltfType: "number" },
        g: { name: "input_6", gltfType: "number" },
        h: { name: "input_7", gltfType: "number" },
        i: { name: "input_8", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      serializedObjects[0].config.inputIsColumnMajor = true;
      return serializedObjects;
    }
  },
  "math/extract3x3": {
    blocks: [
      "FlowGraphExtractMatrix3DBlock"
      /* FlowGraphBlockNames.ExtractMatrix3D */
    ],
    inputs: {
      values: {
        a: { name: "input", gltfType: "float3x3" }
      }
    },
    outputs: {
      values: {
        "0": { name: "output_0" },
        "1": { name: "output_1" },
        "2": { name: "output_2" },
        "3": { name: "output_3" },
        "4": { name: "output_4" },
        "5": { name: "output_5" },
        "6": { name: "output_6" },
        "7": { name: "output_7" },
        "8": { name: "output_8" }
      }
    }
  },
  "math/combine4x4": {
    blocks: [
      "FlowGraphCombineMatrixBlock"
      /* FlowGraphBlockNames.CombineMatrix */
    ],
    inputs: {
      values: {
        a: { name: "input_0", gltfType: "number" },
        b: { name: "input_1", gltfType: "number" },
        c: { name: "input_2", gltfType: "number" },
        d: { name: "input_3", gltfType: "number" },
        e: { name: "input_4", gltfType: "number" },
        f: { name: "input_5", gltfType: "number" },
        g: { name: "input_6", gltfType: "number" },
        h: { name: "input_7", gltfType: "number" },
        i: { name: "input_8", gltfType: "number" },
        j: { name: "input_9", gltfType: "number" },
        k: { name: "input_10", gltfType: "number" },
        l: { name: "input_11", gltfType: "number" },
        m: { name: "input_12", gltfType: "number" },
        n: { name: "input_13", gltfType: "number" },
        o: { name: "input_14", gltfType: "number" },
        p: { name: "input_15", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      serializedObjects[0].config.inputIsColumnMajor = true;
      return serializedObjects;
    }
  },
  "math/extract4x4": {
    blocks: [
      "FlowGraphExtractMatrixBlock"
      /* FlowGraphBlockNames.ExtractMatrix */
    ],
    configuration: {},
    inputs: {
      values: {
        a: { name: "input", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        "0": { name: "output_0" },
        "1": { name: "output_1" },
        "2": { name: "output_2" },
        "3": { name: "output_3" },
        "4": { name: "output_4" },
        "5": { name: "output_5" },
        "6": { name: "output_6" },
        "7": { name: "output_7" },
        "8": { name: "output_8" },
        "9": { name: "output_9" },
        "10": { name: "output_10" },
        "11": { name: "output_11" },
        "12": { name: "output_12" },
        "13": { name: "output_13" },
        "14": { name: "output_14" },
        "15": { name: "output_15" }
      }
    }
  },
  "math/not": {
    blocks: [
      "FlowGraphBitwiseNotBlock"
      /* FlowGraphBlockNames.BitwiseNot */
    ],
    inputs: {
      values: {
        a: { name: "a" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects, context) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      const socketIn = serializedObjects[0].dataInputs[0];
      serializedObjects[0].config.valueType = context._connectionValues[socketIn.uniqueId]?.type ?? "FlowGraphInteger";
      return serializedObjects;
    }
  },
  "math/and": {
    blocks: [
      "FlowGraphBitwiseAndBlock"
      /* FlowGraphBlockNames.BitwiseAnd */
    ],
    inputs: {
      values: {
        a: { name: "a" },
        b: { name: "b" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects, context) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      const socketInA = serializedObjects[0].dataInputs[0];
      const socketInB = serializedObjects[0].dataInputs[1];
      serializedObjects[0].config.valueType = context._connectionValues[socketInA.uniqueId]?.type ?? context._connectionValues[socketInB.uniqueId]?.type ?? "FlowGraphInteger";
      return serializedObjects;
    }
  },
  "math/or": {
    blocks: [
      "FlowGraphBitwiseOrBlock"
      /* FlowGraphBlockNames.BitwiseOr */
    ],
    inputs: {
      values: {
        a: { name: "a" },
        b: { name: "b" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects, context) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      const socketInA = serializedObjects[0].dataInputs[0];
      const socketInB = serializedObjects[0].dataInputs[1];
      serializedObjects[0].config.valueType = context._connectionValues[socketInA.uniqueId]?.type ?? context._connectionValues[socketInB.uniqueId]?.type ?? "FlowGraphInteger";
      return serializedObjects;
    }
  },
  "math/xor": {
    blocks: [
      "FlowGraphBitwiseXorBlock"
      /* FlowGraphBlockNames.BitwiseXor */
    ],
    inputs: {
      values: {
        a: { name: "a" },
        b: { name: "b" }
      }
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _parser, serializedObjects, context) {
      var _a;
      (_a = serializedObjects[0]).config || (_a.config = {});
      const socketInA = serializedObjects[0].dataInputs[0];
      const socketInB = serializedObjects[0].dataInputs[1];
      serializedObjects[0].config.valueType = context._connectionValues[socketInA.uniqueId]?.type ?? context._connectionValues[socketInB.uniqueId]?.type ?? "FlowGraphInteger";
      return serializedObjects;
    }
  },
  "math/asr": getSimpleInputMapping("FlowGraphBitwiseRightShiftBlock", ["a", "b"]),
  "math/lsl": getSimpleInputMapping("FlowGraphBitwiseLeftShiftBlock", ["a", "b"]),
  "math/clz": getSimpleInputMapping(
    "FlowGraphLeadingZerosBlock"
    /* FlowGraphBlockNames.LeadingZeros */
  ),
  "math/ctz": getSimpleInputMapping(
    "FlowGraphTrailingZerosBlock"
    /* FlowGraphBlockNames.TrailingZeros */
  ),
  "math/popcnt": getSimpleInputMapping(
    "FlowGraphOneBitsCounterBlock"
    /* FlowGraphBlockNames.OneBitsCounter */
  ),
  "math/rad": getSimpleInputMapping(
    "FlowGraphDegToRadBlock"
    /* FlowGraphBlockNames.DegToRad */
  ),
  "math/deg": getSimpleInputMapping(
    "FlowGraphRadToDegBlock"
    /* FlowGraphBlockNames.RadToDeg */
  ),
  "type/boolToInt": getSimpleInputMapping(
    "FlowGraphBooleanToInt"
    /* FlowGraphBlockNames.BooleanToInt */
  ),
  "type/boolToFloat": getSimpleInputMapping(
    "FlowGraphBooleanToFloat"
    /* FlowGraphBlockNames.BooleanToFloat */
  ),
  "type/intToBool": getSimpleInputMapping(
    "FlowGraphIntToBoolean"
    /* FlowGraphBlockNames.IntToBoolean */
  ),
  "type/intToFloat": getSimpleInputMapping(
    "FlowGraphIntToFloat"
    /* FlowGraphBlockNames.IntToFloat */
  ),
  "type/floatToInt": getSimpleInputMapping(
    "FlowGraphFloatToInt"
    /* FlowGraphBlockNames.FloatToInt */
  ),
  "type/floatToBool": getSimpleInputMapping(
    "FlowGraphFloatToBoolean"
    /* FlowGraphBlockNames.FloatToBoolean */
  ),
  // flows
  "flow/sequence": {
    blocks: [
      "FlowGraphSequenceBlock"
      /* FlowGraphBlockNames.Sequence */
    ],
    extraProcessor(gltfBlock, _declaration, _mapping, _arrays, serializedObjects) {
      const serializedObject = serializedObjects[0];
      serializedObject.config || (serializedObject.config = {});
      serializedObject.config.outputSignalCount = Object.keys(gltfBlock.flows || []).length;
      serializedObject.signalOutputs.forEach((output, index) => {
        output.name = "out_" + index;
      });
      return serializedObjects;
    }
  },
  "flow/branch": {
    blocks: [
      "FlowGraphBranchBlock"
      /* FlowGraphBlockNames.Branch */
    ],
    outputs: {
      flows: {
        true: { name: "onTrue" },
        false: { name: "onFalse" }
      }
    }
  },
  "flow/switch": {
    blocks: [
      "FlowGraphSwitchBlock"
      /* FlowGraphBlockNames.Switch */
    ],
    configuration: {
      cases: { name: "cases", inOptions: true, defaultValue: [] }
    },
    inputs: {
      values: {
        selection: { name: "case" },
        default: { name: "default" }
      }
    },
    validation(gltfBlock) {
      if (gltfBlock.configuration && gltfBlock.configuration.cases) {
        const cases = gltfBlock.configuration.cases.value;
        const onlyIntegers = cases.every((caseValue) => {
          return typeof caseValue === "number" && /^-?\d+$/.test(caseValue.toString());
        });
        if (!onlyIntegers) {
          Logger.Warn("Switch cases should be integers. Using empty array instead.");
          gltfBlock.configuration.cases.value = [];
          return { valid: true };
        }
        const uniqueCases = new Set(cases);
        gltfBlock.configuration.cases.value = Array.from(uniqueCases);
      }
      return { valid: true };
    },
    extraProcessor(gltfBlock, declaration, _mapping, _arrays, serializedObjects) {
      if (declaration.op !== "flow/switch" || !gltfBlock.flows || Object.keys(gltfBlock.flows).length === 0) {
        throw new Error("Switch should have a single configuration object, the cases array");
      }
      const serializedObject = serializedObjects[0];
      serializedObject.signalOutputs.forEach((output) => {
        if (output.name !== "default") {
          output.name = "out_" + output.name;
        }
      });
      return serializedObjects;
    }
  },
  "flow/while": {
    blocks: [
      "FlowGraphWhileLoopBlock"
      /* FlowGraphBlockNames.WhileLoop */
    ],
    outputs: {
      flows: {
        loopBody: { name: "executionFlow" }
      }
    }
  },
  "flow/for": {
    blocks: [
      "FlowGraphForLoopBlock"
      /* FlowGraphBlockNames.ForLoop */
    ],
    configuration: {
      initialIndex: { name: "initialIndex", gltfType: "number", inOptions: true, defaultValue: 0 }
    },
    inputs: {
      values: {
        startIndex: { name: "startIndex", gltfType: "number" },
        endIndex: { name: "endIndex", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        index: { name: "index" }
      },
      flows: {
        loopBody: { name: "executionFlow" }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _arrays, serializedObjects) {
      const serializedObject = serializedObjects[0];
      serializedObject.config || (serializedObject.config = {});
      serializedObject.config.incrementIndexWhenLoopDone = true;
      return serializedObjects;
    }
  },
  "flow/doN": {
    blocks: [
      "FlowGraphDoNBlock"
      /* FlowGraphBlockNames.DoN */
    ],
    configuration: {},
    inputs: {
      values: {
        n: { name: "maxExecutions", gltfType: "number" }
      }
    },
    outputs: {
      values: {
        currentCount: { name: "executionCount" }
      }
    }
  },
  "flow/multiGate": {
    blocks: [
      "FlowGraphMultiGateBlock"
      /* FlowGraphBlockNames.MultiGate */
    ],
    configuration: {
      isRandom: { name: "isRandom", gltfType: "boolean", inOptions: true, defaultValue: false },
      isLoop: { name: "isLoop", gltfType: "boolean", inOptions: true, defaultValue: false }
    },
    extraProcessor(gltfBlock, declaration, _mapping, _arrays, serializedObjects) {
      if (declaration.op !== "flow/multiGate" || !gltfBlock.flows || Object.keys(gltfBlock.flows).length === 0) {
        throw new Error("MultiGate should have a single configuration object, the number of output flows");
      }
      const serializedObject = serializedObjects[0];
      serializedObject.config || (serializedObject.config = {});
      serializedObject.config.outputSignalCount = Object.keys(gltfBlock.flows).length;
      serializedObject.signalOutputs.forEach((output, index) => {
        output.name = "out_" + index;
      });
      return serializedObjects;
    }
  },
  "flow/waitAll": {
    blocks: [
      "FlowGraphWaitAllBlock"
      /* FlowGraphBlockNames.WaitAll */
    ],
    configuration: {
      inputFlows: { name: "inputSignalCount", gltfType: "number", inOptions: true, defaultValue: 0 }
    },
    inputs: {
      flows: {
        reset: { name: "reset" },
        "[segment]": { name: "in_$1" }
      }
    },
    validation(gltfBlock) {
      if (typeof gltfBlock.configuration?.inputFlows?.value[0] !== "number") {
        gltfBlock.configuration = gltfBlock.configuration || {
          inputFlows: { value: [0] }
        };
        gltfBlock.configuration.inputFlows.value = [0];
      }
      return { valid: true };
    }
  },
  "flow/throttle": {
    blocks: [
      "FlowGraphThrottleBlock"
      /* FlowGraphBlockNames.Throttle */
    ],
    outputs: {
      flows: {
        err: { name: "error" }
      }
    }
  },
  "flow/setDelay": {
    blocks: [
      "FlowGraphSetDelayBlock"
      /* FlowGraphBlockNames.SetDelay */
    ],
    outputs: {
      flows: {
        err: { name: "error" }
      }
    }
  },
  "flow/cancelDelay": {
    blocks: [
      "FlowGraphCancelDelayBlock"
      /* FlowGraphBlockNames.CancelDelay */
    ]
  },
  "variable/get": {
    blocks: [
      "FlowGraphGetVariableBlock"
      /* FlowGraphBlockNames.GetVariable */
    ],
    validation(gltfBlock) {
      if (!gltfBlock.configuration?.variable?.value) {
        Logger.Error("Variable get block should have a variable configuration");
        return { valid: false, error: "Variable get block should have a variable configuration" };
      }
      return { valid: true };
    },
    configuration: {
      variable: {
        name: "variable",
        gltfType: "number",
        flowGraphType: "string",
        inOptions: true,
        isVariable: true,
        dataTransformer(index, parser) {
          return [parser.getVariableName(index[0])];
        }
      }
    }
  },
  "variable/set": {
    blocks: [
      "FlowGraphSetVariableBlock"
      /* FlowGraphBlockNames.SetVariable */
    ],
    configuration: {
      variable: {
        name: "variable",
        gltfType: "number",
        flowGraphType: "string",
        inOptions: true,
        isVariable: true,
        dataTransformer(index, parser) {
          return [parser.getVariableName(index[0])];
        }
      }
    }
  },
  "variable/setMultiple": {
    blocks: [
      "FlowGraphSetVariableBlock"
      /* FlowGraphBlockNames.SetVariable */
    ],
    configuration: {
      variables: {
        name: "variables",
        gltfType: "number",
        flowGraphType: "string",
        inOptions: true,
        dataTransformer(index, parser) {
          return [index[0].map((i) => parser.getVariableName(i))];
        }
      }
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, parser, serializedObjects) {
      const serializedGetVariable = serializedObjects[0];
      serializedGetVariable.dataInputs.forEach((input) => {
        input.name = parser.getVariableName(+input.name);
      });
      return serializedObjects;
    }
  },
  "variable/interpolate": {
    blocks: [
      "FlowGraphInterpolationBlock",
      "FlowGraphContextBlock",
      "FlowGraphPlayAnimationBlock",
      "FlowGraphBezierCurveEasing",
      "FlowGraphGetVariableBlock"
    ],
    configuration: {
      variable: {
        name: "propertyName",
        inOptions: true,
        isVariable: true,
        dataTransformer(index, parser) {
          return [parser.getVariableName(index[0])];
        }
      },
      useSlerp: {
        name: "animationType",
        inOptions: true,
        defaultValue: false,
        dataTransformer: (value) => {
          if (value[0] === true) {
            return [
              "Quaternion"
              /* FlowGraphTypes.Quaternion */
            ];
          } else {
            return [void 0];
          }
        }
      }
    },
    inputs: {
      values: {
        value: { name: "value_1" },
        duration: { name: "duration_1", gltfType: "number" },
        p1: {
          name: "controlPoint1",
          toBlock: "FlowGraphBezierCurveEasing"
          /* FlowGraphBlockNames.BezierCurveEasing */
        },
        p2: {
          name: "controlPoint2",
          toBlock: "FlowGraphBezierCurveEasing"
          /* FlowGraphBlockNames.BezierCurveEasing */
        }
      },
      flows: {
        in: {
          name: "in",
          toBlock: "FlowGraphPlayAnimationBlock"
          /* FlowGraphBlockNames.PlayAnimation */
        }
      }
    },
    outputs: {
      flows: {
        err: {
          name: "error",
          toBlock: "FlowGraphPlayAnimationBlock"
          /* FlowGraphBlockNames.PlayAnimation */
        },
        out: {
          name: "out",
          toBlock: "FlowGraphPlayAnimationBlock"
          /* FlowGraphBlockNames.PlayAnimation */
        },
        done: {
          name: "done",
          toBlock: "FlowGraphPlayAnimationBlock"
          /* FlowGraphBlockNames.PlayAnimation */
        }
      }
    },
    interBlockConnectors: [
      {
        input: "object",
        output: "userVariables",
        inputBlockIndex: 2,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "animation",
        output: "animation",
        inputBlockIndex: 2,
        outputBlockIndex: 0,
        isVariable: true
      },
      {
        input: "easingFunction",
        output: "easingFunction",
        inputBlockIndex: 0,
        outputBlockIndex: 3,
        isVariable: true
      },
      {
        input: "value_0",
        output: "value",
        inputBlockIndex: 0,
        outputBlockIndex: 4,
        isVariable: true
      }
    ],
    extraProcessor(gltfBlock, _declaration, _mapping, parser, serializedObjects) {
      var _a, _b;
      const serializedValueInterpolation = serializedObjects[0];
      const propertyIndex = gltfBlock.configuration?.variable.value[0];
      if (typeof propertyIndex !== "number") {
        Logger.Error("Variable index is not defined for variable interpolation block");
        throw new Error("Variable index is not defined for variable interpolation block");
      }
      const variable = parser.arrays.staticVariables[propertyIndex];
      if (typeof serializedValueInterpolation.config.animationType.value === "undefined") {
        parser.arrays.staticVariables;
        serializedValueInterpolation.config.animationType.value = getAnimationTypeByFlowGraphType(variable.type);
      }
      const serializedGetVariable = serializedObjects[4];
      serializedGetVariable.config || (serializedGetVariable.config = {});
      (_a = serializedGetVariable.config).variable || (_a.variable = {});
      serializedGetVariable.config.variable.value = parser.getVariableName(propertyIndex);
      (_b = serializedObjects[3]).config || (_b.config = {});
      return serializedObjects;
    }
  },
  "pointer/get": {
    blocks: [
      "FlowGraphGetPropertyBlock",
      "FlowGraphJsonPointerParserBlock"
      /* FlowGraphBlockNames.JsonPointerParser */
    ],
    configuration: {
      pointer: {
        name: "jsonPointer",
        toBlock: "FlowGraphJsonPointerParserBlock"
        /* FlowGraphBlockNames.JsonPointerParser */
      }
    },
    inputs: {
      values: {
        "[segment]": {
          name: "$1",
          toBlock: "FlowGraphJsonPointerParserBlock"
          /* FlowGraphBlockNames.JsonPointerParser */
        }
      }
    },
    interBlockConnectors: [
      {
        input: "object",
        output: "object",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "propertyName",
        output: "propertyName",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "customGetFunction",
        output: "getFunction",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      }
    ],
    extraProcessor(gltfBlock, _declaration, _mapping, parser, serializedObjects) {
      serializedObjects.forEach((serializedObject) => {
        if (serializedObject.className === "FlowGraphJsonPointerParserBlock") {
          serializedObject.config || (serializedObject.config = {});
          serializedObject.config.outputValue = true;
        }
      });
      return serializedObjects;
    }
  },
  "pointer/set": {
    blocks: [
      "FlowGraphSetPropertyBlock",
      "FlowGraphJsonPointerParserBlock"
      /* FlowGraphBlockNames.JsonPointerParser */
    ],
    configuration: {
      pointer: {
        name: "jsonPointer",
        toBlock: "FlowGraphJsonPointerParserBlock"
        /* FlowGraphBlockNames.JsonPointerParser */
      }
    },
    inputs: {
      values: {
        // must be defined due to the array taking over
        value: { name: "value" },
        "[segment]": {
          name: "$1",
          toBlock: "FlowGraphJsonPointerParserBlock"
          /* FlowGraphBlockNames.JsonPointerParser */
        }
      }
    },
    outputs: {
      flows: {
        err: { name: "error" }
      }
    },
    interBlockConnectors: [
      {
        input: "object",
        output: "object",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "propertyName",
        output: "propertyName",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "customSetFunction",
        output: "setFunction",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      }
    ],
    extraProcessor(gltfBlock, _declaration, _mapping, parser, serializedObjects) {
      serializedObjects.forEach((serializedObject) => {
        if (serializedObject.className === "FlowGraphJsonPointerParserBlock") {
          serializedObject.config || (serializedObject.config = {});
          serializedObject.config.outputValue = true;
        }
      });
      return serializedObjects;
    }
  },
  "pointer/interpolate": {
    // interpolate, parse the pointer and play the animation generated. 3 blocks!
    blocks: [
      "FlowGraphInterpolationBlock",
      "FlowGraphJsonPointerParserBlock",
      "FlowGraphPlayAnimationBlock",
      "FlowGraphBezierCurveEasing"
      /* FlowGraphBlockNames.BezierCurveEasing */
    ],
    configuration: {
      pointer: {
        name: "jsonPointer",
        toBlock: "FlowGraphJsonPointerParserBlock"
        /* FlowGraphBlockNames.JsonPointerParser */
      }
    },
    inputs: {
      values: {
        value: { name: "value_1" },
        "[segment]": {
          name: "$1",
          toBlock: "FlowGraphJsonPointerParserBlock"
          /* FlowGraphBlockNames.JsonPointerParser */
        },
        duration: {
          name: "duration_1",
          gltfType: "number"
          /*, inOptions: true */
        },
        p1: {
          name: "controlPoint1",
          toBlock: "FlowGraphBezierCurveEasing"
          /* FlowGraphBlockNames.BezierCurveEasing */
        },
        p2: {
          name: "controlPoint2",
          toBlock: "FlowGraphBezierCurveEasing"
          /* FlowGraphBlockNames.BezierCurveEasing */
        }
      },
      flows: {
        in: {
          name: "in",
          toBlock: "FlowGraphPlayAnimationBlock"
          /* FlowGraphBlockNames.PlayAnimation */
        }
      }
    },
    outputs: {
      flows: {
        err: {
          name: "error",
          toBlock: "FlowGraphPlayAnimationBlock"
          /* FlowGraphBlockNames.PlayAnimation */
        },
        out: {
          name: "out",
          toBlock: "FlowGraphPlayAnimationBlock"
          /* FlowGraphBlockNames.PlayAnimation */
        },
        done: {
          name: "done",
          toBlock: "FlowGraphPlayAnimationBlock"
          /* FlowGraphBlockNames.PlayAnimation */
        }
      }
    },
    interBlockConnectors: [
      {
        input: "object",
        output: "object",
        inputBlockIndex: 2,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "propertyName",
        output: "propertyName",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "customBuildAnimation",
        output: "generateAnimationsFunction",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "animation",
        output: "animation",
        inputBlockIndex: 2,
        outputBlockIndex: 0,
        isVariable: true
      },
      {
        input: "easingFunction",
        output: "easingFunction",
        inputBlockIndex: 0,
        outputBlockIndex: 3,
        isVariable: true
      },
      {
        input: "value_0",
        output: "value",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      }
    ],
    extraProcessor(gltfBlock, _declaration, _mapping, parser, serializedObjects) {
      serializedObjects.forEach((serializedObject) => {
        if (serializedObject.className === "FlowGraphJsonPointerParserBlock") {
          serializedObject.config || (serializedObject.config = {});
          serializedObject.config.outputValue = true;
        } else if (serializedObject.className === "FlowGraphInterpolationBlock") {
          serializedObject.config || (serializedObject.config = {});
          Object.keys(gltfBlock.values || []).forEach((key) => {
            const value = gltfBlock.values?.[key];
            if (key === "value" && value) {
              const type = value.type;
              if (type !== void 0) {
                serializedObject.config.animationType = parser.arrays.types[type].flowGraphType;
              }
            }
          });
        }
      });
      return serializedObjects;
    }
  },
  "animation/start": {
    blocks: ["FlowGraphPlayAnimationBlock", "FlowGraphArrayIndexBlock", "KHR_interactivity/FlowGraphGLTFDataProvider"],
    inputs: {
      values: {
        animation: {
          name: "index",
          gltfType: "number",
          toBlock: "FlowGraphArrayIndexBlock"
          /* FlowGraphBlockNames.ArrayIndex */
        },
        speed: { name: "speed", gltfType: "number" },
        startTime: { name: "from", gltfType: "number", dataTransformer: (time, parser) => [time[0] * parser._animationTargetFps] },
        endTime: { name: "to", gltfType: "number", dataTransformer: (time, parser) => [time[0] * parser._animationTargetFps] }
      }
    },
    outputs: {
      flows: {
        err: { name: "error" }
      }
    },
    interBlockConnectors: [
      {
        input: "animationGroup",
        output: "value",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "array",
        output: "animationGroups",
        inputBlockIndex: 1,
        outputBlockIndex: 2,
        isVariable: true
      }
    ],
    extraProcessor(_gltfBlock, _declaration, _mapping, _arrays, serializedObjects, _context, globalGLTF) {
      const serializedObject = serializedObjects[serializedObjects.length - 1];
      serializedObject.config || (serializedObject.config = {});
      serializedObject.config.glTF = globalGLTF;
      return serializedObjects;
    }
  },
  "animation/stop": {
    blocks: ["FlowGraphStopAnimationBlock", "FlowGraphArrayIndexBlock", "KHR_interactivity/FlowGraphGLTFDataProvider"],
    inputs: {
      values: {
        animation: {
          name: "index",
          gltfType: "number",
          toBlock: "FlowGraphArrayIndexBlock"
          /* FlowGraphBlockNames.ArrayIndex */
        }
      }
    },
    outputs: {
      flows: {
        err: { name: "error" }
      }
    },
    interBlockConnectors: [
      {
        input: "animationGroup",
        output: "value",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "array",
        output: "animationGroups",
        inputBlockIndex: 1,
        outputBlockIndex: 2,
        isVariable: true
      }
    ],
    extraProcessor(_gltfBlock, _declaration, _mapping, _arrays, serializedObjects, _context, globalGLTF) {
      const serializedObject = serializedObjects[serializedObjects.length - 1];
      serializedObject.config || (serializedObject.config = {});
      serializedObject.config.glTF = globalGLTF;
      return serializedObjects;
    }
  },
  "animation/stopAt": {
    blocks: ["FlowGraphStopAnimationBlock", "FlowGraphArrayIndexBlock", "KHR_interactivity/FlowGraphGLTFDataProvider"],
    configuration: {},
    inputs: {
      values: {
        animation: {
          name: "index",
          gltfType: "number",
          toBlock: "FlowGraphArrayIndexBlock"
          /* FlowGraphBlockNames.ArrayIndex */
        },
        stopTime: { name: "stopAtFrame", gltfType: "number", dataTransformer: (time, parser) => [time[0] * parser._animationTargetFps] }
      }
    },
    outputs: {
      flows: {
        err: { name: "error" }
      }
    },
    interBlockConnectors: [
      {
        input: "animationGroup",
        output: "value",
        inputBlockIndex: 0,
        outputBlockIndex: 1,
        isVariable: true
      },
      {
        input: "array",
        output: "animationGroups",
        inputBlockIndex: 1,
        outputBlockIndex: 2,
        isVariable: true
      }
    ],
    extraProcessor(_gltfBlock, _declaration, _mapping, _arrays, serializedObjects, _context, globalGLTF) {
      const serializedObject = serializedObjects[serializedObjects.length - 1];
      serializedObject.config || (serializedObject.config = {});
      serializedObject.config.glTF = globalGLTF;
      return serializedObjects;
    }
  },
  "math/switch": {
    blocks: [
      "FlowGraphDataSwitchBlock"
      /* FlowGraphBlockNames.DataSwitch */
    ],
    configuration: {
      cases: { name: "cases", inOptions: true, defaultValue: [] }
    },
    inputs: {
      values: {
        selection: { name: "case" }
      }
    },
    validation(gltfBlock) {
      if (gltfBlock.configuration && gltfBlock.configuration.cases) {
        const cases = gltfBlock.configuration.cases.value;
        const onlyIntegers = cases.every((caseValue) => {
          return typeof caseValue === "number" && /^-?\d+$/.test(caseValue.toString());
        });
        if (!onlyIntegers) {
          Logger.Warn("Switch cases should be integers. Using empty array instead.");
          gltfBlock.configuration.cases.value = [];
          return { valid: true };
        }
        const uniqueCases = new Set(cases);
        gltfBlock.configuration.cases.value = Array.from(uniqueCases);
      }
      return { valid: true };
    },
    extraProcessor(_gltfBlock, _declaration, _mapping, _arrays, serializedObjects) {
      const serializedObject = serializedObjects[0];
      serializedObject.dataInputs.forEach((input) => {
        if (input.name !== "default" && input.name !== "case") {
          input.name = "in_" + input.name;
        }
      });
      serializedObject.config || (serializedObject.config = {});
      serializedObject.config.treatCasesAsIntegers = true;
      return serializedObjects;
    }
  },
  "debug/log": {
    blocks: [
      "FlowGraphConsoleLogBlock"
      /* FlowGraphBlockNames.ConsoleLog */
    ],
    configuration: {
      message: { name: "messageTemplate", inOptions: true }
    }
  }
};
function getSimpleInputMapping(type, inputs = ["a"], inferType) {
  return {
    blocks: [type],
    inputs: {
      values: inputs.reduce((acc, input) => {
        acc[input] = { name: input };
        return acc;
      }, {})
    },
    outputs: {
      values: {
        value: { name: "value" }
      }
    },
    extraProcessor(gltfBlock, _declaration, _mapping, _parser, serializedObjects) {
      var _a;
      if (inferType) {
        (_a = serializedObjects[0]).config || (_a.config = {});
        serializedObjects[0].config.preventIntegerFloatArithmetic = true;
        let type2 = -1;
        Object.keys(gltfBlock.values || {}).find((value) => {
          if (gltfBlock.values?.[value].type !== void 0) {
            type2 = gltfBlock.values[value].type;
            return true;
          }
          return false;
        });
        if (type2 !== -1) {
          serializedObjects[0].config.type = _parser.arrays.types[type2].flowGraphType;
        }
      }
      return serializedObjects;
    },
    validation(gltfBlock) {
      if (inferType) {
        return ValidateTypes(gltfBlock);
      }
      return { valid: true };
    }
  };
}
function ValidateTypes(gltfBlock) {
  if (gltfBlock.values) {
    const types = Object.keys(gltfBlock.values).map((key) => gltfBlock.values[key].type).filter((type) => type !== void 0);
    const allSameType = types.every((type) => type === types[0]);
    if (!allSameType) {
      return { valid: false, error: "All inputs must be of the same type" };
    }
  }
  return { valid: true };
}
export {
  FlowGraphInteger as F,
  RichTypeAny as R,
  addNewInteractivityFlowGraphMapping as a,
  RichTypeNumber as b,
  RichTypeBoolean as c,
  getRichTypeByAnimationType as d,
  RichTypeVector3 as e,
  RichTypeQuaternion as f,
  getRichTypeByFlowGraphType as g,
  RichTypeMatrix as h,
  RichTypeFlowGraphInteger as i,
  getRichTypeFromValue as j,
  RichTypeVector4 as k,
  RichTypeVector2 as l,
  RichTypeMatrix2D as m,
  FlowGraphMatrix2D as n,
  RichTypeMatrix3D as o,
  FlowGraphMatrix3D as p,
  RichTypeString as q,
  getMappingForDeclaration as r,
  getMappingForFullOperationName as s
};
//# sourceMappingURL=CERZDFgL.js.map
