const node_env = globalThis.process?.env?.NODE_ENV;
const DEV = node_env && !node_env.toLowerCase().startsWith("prod");

const BROWSER = typeof window !== "undefined";

export { BROWSER as B, DEV as D };
//# sourceMappingURL=browser-fallback-CYSLhaFr.js.map
