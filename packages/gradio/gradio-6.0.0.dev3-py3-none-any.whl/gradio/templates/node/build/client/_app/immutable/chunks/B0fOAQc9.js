import { az as Animation, V as Vector3, M as Matrix, e as Tools, Q as Quaternion, b9 as BVHFileLoaderMetadata, aE as RegisterSceneLoaderPlugin } from "./f5NiF4Sn.js";
import { A as AssetContainer } from "./CqN91lEU.js";
import { B as Bone } from "./C-03jIP4.js";
import { S as Skeleton } from "./BM0izeeK.js";
const _XPosition = "Xposition";
const _YPosition = "Yposition";
const _ZPosition = "Zposition";
const _XRotation = "Xrotation";
const _YRotation = "Yrotation";
const _ZRotation = "Zrotation";
const _HierarchyNode = "HIERARCHY";
const _MotionNode = "MOTION";
class LoaderContext {
  constructor(skeleton) {
    this.loopMode = Animation.ANIMATIONLOOPMODE_CYCLE;
    this.list = [];
    this.root = CreateBVHNode();
    this.numFrames = 0;
    this.frameRate = 0;
    this.skeleton = skeleton;
  }
}
function CreateBVHNode() {
  return {
    name: "",
    type: "",
    offset: new Vector3(),
    channels: [],
    children: [],
    frames: [],
    parent: null
  };
}
function CreateBVHKeyFrame() {
  return {
    frame: 0,
    position: new Vector3(),
    rotation: new Quaternion()
  };
}
function BoneOffset(node) {
  const x = node.offset.x;
  const y = node.offset.y;
  const z = node.offset.z;
  return Matrix.Translation(x, y, z);
}
function CreateAnimations(node, context) {
  if (node.frames.length === 0) {
    return [];
  }
  const animations = [];
  const hasPosition = node.channels.some((c) => c === _XPosition || c === _YPosition || c === _ZPosition);
  const hasRotation = node.channels.some((c) => c === _XRotation || c === _YRotation || c === _ZRotation);
  const posAnim = new Animation(`${node.name}_pos`, "position", context.frameRate, Animation.ANIMATIONTYPE_VECTOR3, context.loopMode);
  const rotAnim = new Animation(`${node.name}_rot`, "rotationQuaternion", context.frameRate, Animation.ANIMATIONTYPE_QUATERNION, context.loopMode);
  const posKeys = [];
  const rotKeys = [];
  for (let i = 0; i < node.frames.length; i++) {
    const frame = node.frames[i];
    if (hasPosition && frame.position) {
      posKeys.push({
        frame: frame.frame,
        value: frame.position.clone()
      });
    }
    if (hasRotation) {
      rotKeys.push({
        frame: frame.frame,
        value: frame.rotation.clone()
      });
    }
  }
  if (posKeys.length > 0) {
    posAnim.setKeys(posKeys);
    animations.push(posAnim);
  }
  if (rotKeys.length > 0) {
    rotAnim.setKeys(rotKeys);
    animations.push(rotAnim);
  }
  return animations;
}
function ConvertNode(node, parent, context) {
  const matrix = BoneOffset(node);
  const bone = new Bone(node.name, context.skeleton, parent, matrix);
  const animations = CreateAnimations(node, context);
  for (const animation of animations) {
    if (animation.getKeys() && animation.getKeys().length > 0) {
      bone.animations.push(animation);
    }
  }
  for (const child of node.children) {
    ConvertNode(child, bone, context);
  }
}
function ReadFrameData(data, frameNumber, bone, tokenIndex) {
  if (bone.type === "ENDSITE") {
    return;
  }
  const keyframe = CreateBVHKeyFrame();
  keyframe.frame = frameNumber;
  keyframe.position = new Vector3();
  keyframe.rotation = new Quaternion();
  bone.frames.push(keyframe);
  let combinedRotation = Matrix.Identity();
  for (let i = 0; i < bone.channels.length; ++i) {
    const channel = bone.channels[i];
    const value = data[tokenIndex.i++];
    if (!value) {
      continue;
    }
    const parsedValue = parseFloat(value.trim());
    if (channel.endsWith("position")) {
      switch (channel) {
        case _XPosition:
          keyframe.position.x = parsedValue;
          break;
        case _YPosition:
          keyframe.position.y = parsedValue;
          break;
        case _ZPosition:
          keyframe.position.z = parsedValue;
          break;
      }
    } else if (channel.endsWith("rotation")) {
      const angle = Tools.ToRadians(parsedValue);
      let rotationMatrix;
      switch (channel) {
        case _XRotation:
          rotationMatrix = Matrix.RotationX(angle);
          break;
        case _YRotation:
          rotationMatrix = Matrix.RotationY(angle);
          break;
        case _ZRotation:
          rotationMatrix = Matrix.RotationZ(angle);
          break;
      }
      combinedRotation = rotationMatrix.multiply(combinedRotation);
    }
  }
  Quaternion.FromRotationMatrixToRef(combinedRotation, keyframe.rotation);
  for (const child of bone.children) {
    ReadFrameData(data, frameNumber, child, tokenIndex);
  }
}
function ReadNode(lines, firstLine, parent, context) {
  const node = CreateBVHNode();
  node.parent = parent;
  context.list.push(node);
  let tokens = firstLine.trim().split(/\s+/);
  if (tokens[0].toUpperCase() === "END" && tokens[1].toUpperCase() === "SITE") {
    node.type = "ENDSITE";
    node.name = "ENDSITE";
  } else {
    node.name = tokens[1];
    node.type = tokens[0].toUpperCase();
  }
  if (lines.shift()?.trim() != "{") {
    throw new Error("Expected opening { after type & name");
  }
  const tokensSplit = lines.shift()?.trim().split(/\s+/);
  if (!tokensSplit) {
    throw new Error("Unexpected end of file: missing OFFSET");
  }
  tokens = tokensSplit;
  if (tokens[0].toUpperCase() != "OFFSET") {
    throw new Error("Expected OFFSET, but got: " + tokens[0]);
  }
  if (tokens.length != 4) {
    throw new Error("OFFSET: Invalid number of values");
  }
  const offset = new Vector3(parseFloat(tokens[1]), parseFloat(tokens[2]), parseFloat(tokens[3]));
  if (isNaN(offset.x) || isNaN(offset.y) || isNaN(offset.z)) {
    throw new Error("OFFSET: Invalid values");
  }
  node.offset = offset;
  if (node.type != "ENDSITE") {
    tokens = lines.shift()?.trim().split(/\s+/);
    if (!tokens) {
      throw new Error("Unexpected end of file: missing CHANNELS");
    }
    if (tokens[0].toUpperCase() != "CHANNELS") {
      throw new Error("Expected CHANNELS definition");
    }
    const numChannels = parseInt(tokens[1]);
    node.channels = tokens.splice(2, numChannels);
    node.children = [];
  }
  while (lines.length > 0) {
    const line = lines.shift()?.trim();
    if (line === "}") {
      return node;
    } else if (line) {
      node.children.push(ReadNode(lines, line, node, context));
    }
  }
  throw new Error("Unexpected end of file: missing closing brace");
}
function ReadBvh(text, scene, assetContainer, loadingOptions) {
  const lines = text.split("\n");
  const { loopMode } = loadingOptions;
  scene._blockEntityCollection = !!assetContainer;
  const skeleton = new Skeleton("", "", scene);
  skeleton._parentContainer = assetContainer;
  scene._blockEntityCollection = false;
  const context = new LoaderContext(skeleton);
  context.loopMode = loopMode;
  const firstLine = lines.shift();
  if (!firstLine || firstLine.trim().toUpperCase() !== _HierarchyNode) {
    throw new Error("HIERARCHY expected");
  }
  const nodeLine = lines.shift();
  if (!nodeLine) {
    throw new Error("Unexpected end of file after HIERARCHY");
  }
  const root = ReadNode(lines, nodeLine.trim(), null, context);
  const motionLine = lines.shift();
  if (!motionLine || motionLine.trim().toUpperCase() !== _MotionNode) {
    throw new Error("MOTION expected");
  }
  const framesLine = lines.shift();
  if (!framesLine) {
    throw new Error("Unexpected end of file before frame count");
  }
  const framesTokens = framesLine.trim().split(/[\s]+/);
  if (framesTokens.length < 2) {
    throw new Error("Invalid frame count line");
  }
  const numFrames = parseInt(framesTokens[1]);
  if (isNaN(numFrames)) {
    throw new Error("Failed to read number of frames.");
  }
  context.numFrames = numFrames;
  const frameTimeLine = lines.shift();
  if (!frameTimeLine) {
    throw new Error("Unexpected end of file before frame time");
  }
  const frameTimeTokens = frameTimeLine.trim().split(/[\s]+/);
  if (frameTimeTokens.length < 3) {
    throw new Error("Invalid frame time line");
  }
  const frameTime = parseFloat(frameTimeTokens[2]);
  if (isNaN(frameTime)) {
    throw new Error("Failed to read frame time.");
  }
  if (frameTime <= 0) {
    throw new Error("Failed to read frame time. Invalid value " + frameTime);
  }
  context.frameRate = 1 / frameTime;
  for (let i = 0; i < numFrames; ++i) {
    const frameLine = lines.shift();
    if (!frameLine) {
      continue;
    }
    const tokens = frameLine.trim().split(/[\s]+/) || [];
    ReadFrameData(tokens, i, root, { i: 0 });
  }
  context.root = root;
  ConvertNode(context.root, null, context);
  context.skeleton.returnToRest();
  return context.skeleton;
}
class BVHFileLoader {
  /**
   * Creates loader for bvh motion files
   * @param loadingOptions - Options for the bvh loader
   */
  constructor(loadingOptions) {
    this.name = BVHFileLoaderMetadata.name;
    this.extensions = BVHFileLoaderMetadata.extensions;
    this._loadingOptions = { ...BVHFileLoader._DefaultLoadingOptions, ...loadingOptions ?? {} };
  }
  static get _DefaultLoadingOptions() {
    return {
      loopMode: Animation.ANIMATIONLOOPMODE_CYCLE
    };
  }
  /** @internal */
  createPlugin(options) {
    return new BVHFileLoader(options[BVHFileLoaderMetadata.name]);
  }
  /**
   * If the data string can be loaded directly.
   * @param data - direct load data
   * @returns if the data can be loaded directly
   */
  canDirectLoad(data) {
    return this.isBvhHeader(data);
  }
  isBvhHeader(text) {
    return text.split("\n")[0] == "HIERARCHY";
  }
  isNotBvhHeader(text) {
    return !this.isBvhHeader(text);
  }
  /**
   * Imports  from the loaded gaussian splatting data and adds them to the scene
   * @param _meshesNames a string or array of strings of the mesh names that should be loaded from the file
   * @param scene the scene the meshes should be added to
   * @param data the bvh data to load
   * @returns a promise containing the loaded skeletons and animations
   */
  // eslint-disable-next-line @typescript-eslint/promise-function-async, no-restricted-syntax
  importMeshAsync(_meshesNames, scene, data) {
    if (typeof data !== "string") {
      return Promise.reject("BVH loader expects string data.");
    }
    if (this.isNotBvhHeader(data)) {
      return Promise.reject("BVH loader expects HIERARCHY header.");
    }
    try {
      const skeleton = ReadBvh(data, scene, null, this._loadingOptions);
      return Promise.resolve({
        meshes: [],
        particleSystems: [],
        skeletons: [skeleton],
        animationGroups: [],
        transformNodes: [],
        geometries: [],
        lights: [],
        spriteManagers: []
      });
    } catch (e) {
      return Promise.reject(e);
    }
  }
  /**
   * Imports all objects from the loaded bvh data and adds them to the scene
   * @param scene the scene the objects should be added to
   * @param data the bvh data to load
   * @returns a promise which completes when objects have been loaded to the scene
   */
  // eslint-disable-next-line no-restricted-syntax, @typescript-eslint/promise-function-async
  loadAsync(scene, data) {
    if (typeof data !== "string") {
      return Promise.reject("BVH loader expects string data.");
    }
    if (this.isNotBvhHeader(data)) {
      return Promise.reject("BVH loader expects HIERARCHY header.");
    }
    return this.importMeshAsync(null, scene, data).then(() => {
    });
  }
  /**
   * Load into an asset container.
   * @param scene The scene to load into
   * @param data The data to import
   * @returns The loaded asset container
   */
  // eslint-disable-next-line @typescript-eslint/promise-function-async, no-restricted-syntax
  loadAssetContainerAsync(scene, data) {
    if (typeof data !== "string") {
      return Promise.reject("BVH loader expects string data.");
    }
    if (this.isNotBvhHeader(data)) {
      return Promise.reject("BVH loader expects HIERARCHY header.");
    }
    const assetContainer = new AssetContainer(scene);
    try {
      const skeleton = ReadBvh(data, scene, assetContainer, this._loadingOptions);
      assetContainer.skeletons.push(skeleton);
      return Promise.resolve(assetContainer);
    } catch (e) {
      return Promise.reject(e);
    }
  }
}
RegisterSceneLoaderPlugin(new BVHFileLoader());
export {
  BVHFileLoader
};
//# sourceMappingURL=B0fOAQc9.js.map
