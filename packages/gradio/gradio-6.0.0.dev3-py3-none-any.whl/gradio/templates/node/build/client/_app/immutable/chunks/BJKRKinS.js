import { C as VertexData, D as Mesh } from "./f5NiF4Sn.js";
function CreateDiscVertexData(options) {
  const positions = [];
  const indices = [];
  const normals = [];
  const uvs = [];
  const radius = options.radius || 0.5;
  const tessellation = options.tessellation || 64;
  const arc = options.arc && (options.arc <= 0 || options.arc > 1) ? 1 : options.arc || 1;
  const sideOrientation = options.sideOrientation === 0 ? 0 : options.sideOrientation || VertexData.DEFAULTSIDE;
  positions.push(0, 0, 0);
  uvs.push(0.5, 0.5);
  const theta = Math.PI * 2 * arc;
  const step = arc === 1 ? theta / tessellation : theta / (tessellation - 1);
  let a = 0;
  for (let t = 0; t < tessellation; t++) {
    const x = Math.cos(a);
    const y = Math.sin(a);
    const u = (x + 1) / 2;
    const v = (1 - y) / 2;
    positions.push(radius * x, radius * y, 0);
    uvs.push(u, v);
    a += step;
  }
  if (arc === 1) {
    positions.push(positions[3], positions[4], positions[5]);
    uvs.push(uvs[2], uvs[3]);
  }
  const vertexNb = positions.length / 3;
  for (let i = 1; i < vertexNb - 1; i++) {
    indices.push(i + 1, 0, i);
  }
  VertexData.ComputeNormals(positions, indices, normals);
  VertexData._ComputeSides(sideOrientation, positions, indices, normals, uvs, options.frontUVs, options.backUVs);
  const vertexData = new VertexData();
  vertexData.indices = indices;
  vertexData.positions = positions;
  vertexData.normals = normals;
  vertexData.uvs = uvs;
  return vertexData;
}
function CreateDisc(name, options = {}, scene = null) {
  const disc = new Mesh(name, scene);
  options.sideOrientation = Mesh._GetDefaultSideOrientation(options.sideOrientation);
  disc._originalBuilderSideOrientation = options.sideOrientation;
  const vertexData = CreateDiscVertexData(options);
  vertexData.applyToMesh(disc, options.updatable);
  return disc;
}
const DiscBuilder = {
  // eslint-disable-next-line @typescript-eslint/naming-convention
  CreateDisc
};
VertexData.CreateDisc = CreateDiscVertexData;
Mesh.CreateDisc = (name, radius, tessellation, scene = null, updatable, sideOrientation) => {
  const options = {
    radius,
    tessellation,
    sideOrientation,
    updatable
  };
  return CreateDisc(name, options, scene);
};
export {
  CreateDisc,
  CreateDiscVertexData,
  DiscBuilder
};
//# sourceMappingURL=BJKRKinS.js.map
