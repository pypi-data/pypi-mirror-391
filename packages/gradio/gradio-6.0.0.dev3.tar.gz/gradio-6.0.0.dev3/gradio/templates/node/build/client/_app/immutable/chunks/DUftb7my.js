import { an as current_batch, ao as resume_effect, ap as destroy_effect, aq as pause_effect, ar as should_defer_append, as as create_text, at as branch, h as hydrating, au as hydrate_node, av as move_effect, a as hydrate_next, H as block, aw as EFFECT_TRANSPARENT, ax as read_hydration_instruction, aa as HYDRATION_START_ELSE, ac as skip_nodes, ab as set_hydrate_node, ad as set_hydrating, a8 as effect, ay as render_effect, y as untrack, ae as queue_micro_task, az as STATE_SYMBOL, T as noop, m as mutable_source, aA as DEV, j as set, k as get$1, C as teardown, a6 as define_property, B as get_descriptor, aB as props_invalid_value, aC as PROPS_IS_UPDATED, S as derived, x as derived_safe_equal, L as proxy, aD as is_destroying_effect, aE as active_effect, aF as DESTROYED, aG as PROPS_IS_BINDABLE, aH as legacy_mode_flag, aI as PROPS_IS_RUNES, aJ as PROPS_IS_IMMUTABLE, aK as props_rest_readonly, aL as is_function, a1 as LEGACY_PROPS, aM as PROPS_IS_LAZY_INITIAL, ag as source, aN as update, aO as set_active_effect } from "./DEzry6cj.js";
import { s as subscribe_to_store, g as get } from "./DdkXqxbl.js";
class BranchManager {
  /** @type {TemplateNode} */
  anchor;
  /** @type {Map<Batch, Key>} */
  #batches = /* @__PURE__ */ new Map();
  /** @type {Map<Key, Effect>} */
  #onscreen = /* @__PURE__ */ new Map();
  /** @type {Map<Key, Branch>} */
  #offscreen = /* @__PURE__ */ new Map();
  /**
   * Whether to pause (i.e. outro) on change, or destroy immediately.
   * This is necessary for `<svelte:element>`
   */
  #transition = true;
  /**
   * @param {TemplateNode} anchor
   * @param {boolean} transition
   */
  constructor(anchor, transition = true) {
    this.anchor = anchor;
    this.#transition = transition;
  }
  #commit = () => {
    var batch = (
      /** @type {Batch} */
      current_batch
    );
    if (!this.#batches.has(batch)) return;
    var key = (
      /** @type {Key} */
      this.#batches.get(batch)
    );
    var onscreen = this.#onscreen.get(key);
    if (onscreen) {
      resume_effect(onscreen);
    } else {
      var offscreen = this.#offscreen.get(key);
      if (offscreen) {
        this.#onscreen.set(key, offscreen.effect);
        this.#offscreen.delete(key);
        offscreen.fragment.lastChild.remove();
        this.anchor.before(offscreen.fragment);
        onscreen = offscreen.effect;
      }
    }
    for (const [b, k] of this.#batches) {
      this.#batches.delete(b);
      if (b === batch) {
        break;
      }
      const offscreen2 = this.#offscreen.get(k);
      if (offscreen2) {
        destroy_effect(offscreen2.effect);
        this.#offscreen.delete(k);
      }
    }
    for (const [k, effect2] of this.#onscreen) {
      if (k === key) continue;
      const on_destroy = () => {
        const keys = Array.from(this.#batches.values());
        if (keys.includes(k)) {
          var fragment = document.createDocumentFragment();
          move_effect(effect2, fragment);
          fragment.append(create_text());
          this.#offscreen.set(k, { effect: effect2, fragment });
        } else {
          destroy_effect(effect2);
        }
        this.#onscreen.delete(k);
      };
      if (this.#transition || !onscreen) {
        pause_effect(effect2, on_destroy, false);
      } else {
        on_destroy();
      }
    }
  };
  /**
   * @param {Batch} batch
   */
  #discard = (batch) => {
    this.#batches.delete(batch);
    const keys = Array.from(this.#batches.values());
    for (const [k, branch2] of this.#offscreen) {
      if (!keys.includes(k)) {
        destroy_effect(branch2.effect);
        this.#offscreen.delete(k);
      }
    }
  };
  /**
   *
   * @param {any} key
   * @param {null | ((target: TemplateNode) => void)} fn
   */
  ensure(key, fn) {
    var batch = (
      /** @type {Batch} */
      current_batch
    );
    var defer = should_defer_append();
    if (fn && !this.#onscreen.has(key) && !this.#offscreen.has(key)) {
      if (defer) {
        var fragment = document.createDocumentFragment();
        var target = create_text();
        fragment.append(target);
        this.#offscreen.set(key, {
          effect: branch(() => fn(target)),
          fragment
        });
      } else {
        this.#onscreen.set(
          key,
          branch(() => fn(this.anchor))
        );
      }
    }
    this.#batches.set(batch, key);
    if (defer) {
      for (const [k, effect2] of this.#onscreen) {
        if (k === key) {
          batch.skipped_effects.delete(effect2);
        } else {
          batch.skipped_effects.add(effect2);
        }
      }
      for (const [k, branch2] of this.#offscreen) {
        if (k === key) {
          batch.skipped_effects.delete(branch2.effect);
        } else {
          batch.skipped_effects.add(branch2.effect);
        }
      }
      batch.oncommit(this.#commit);
      batch.ondiscard(this.#discard);
    } else {
      if (hydrating) {
        this.anchor = hydrate_node;
      }
      this.#commit();
    }
  }
}
function if_block(node, fn, elseif = false) {
  if (hydrating) {
    hydrate_next();
  }
  var branches = new BranchManager(node);
  var flags = elseif ? EFFECT_TRANSPARENT : 0;
  function update_branch(condition, fn2) {
    if (hydrating) {
      const is_else = read_hydration_instruction(node) === HYDRATION_START_ELSE;
      if (condition === is_else) {
        var anchor = skip_nodes();
        set_hydrate_node(anchor);
        branches.anchor = anchor;
        set_hydrating(false);
        branches.ensure(condition, fn2);
        set_hydrating(true);
        return;
      }
    }
    branches.ensure(condition, fn2);
  }
  block(() => {
    var has_branch = false;
    fn((fn2, flag = true) => {
      has_branch = true;
      update_branch(flag, fn2);
    });
    if (!has_branch) {
      update_branch(false, null);
    }
  }, flags);
}
function component(node, get_component, render_fn) {
  if (hydrating) {
    hydrate_next();
  }
  var branches = new BranchManager(node);
  block(() => {
    var component2 = get_component() ?? null;
    branches.ensure(component2, component2 && ((target) => render_fn(target, component2)));
  }, EFFECT_TRANSPARENT);
}
function is_bound_this(bound_value, element_or_component) {
  return bound_value === element_or_component || bound_value?.[STATE_SYMBOL] === element_or_component;
}
function bind_this(element_or_component = {}, update2, get_value, get_parts) {
  effect(() => {
    var old_parts;
    var parts;
    render_effect(() => {
      old_parts = parts;
      parts = get_parts?.() || [];
      untrack(() => {
        if (element_or_component !== get_value(...parts)) {
          update2(element_or_component, ...parts);
          if (old_parts && is_bound_this(get_value(...old_parts), element_or_component)) {
            update2(null, ...old_parts);
          }
        }
      });
    });
    return () => {
      queue_micro_task(() => {
        if (parts && is_bound_this(get_value(...parts), element_or_component)) {
          update2(null, ...parts);
        }
      });
    };
  });
  return element_or_component;
}
let is_store_binding = false;
let IS_UNMOUNTED = Symbol();
function store_get(store, store_name, stores) {
  const entry = stores[store_name] ??= {
    store: null,
    source: mutable_source(void 0),
    unsubscribe: noop
  };
  if (DEV) {
    entry.source.label = store_name;
  }
  if (entry.store !== store && !(IS_UNMOUNTED in stores)) {
    entry.unsubscribe();
    entry.store = store ?? null;
    if (store == null) {
      entry.source.v = void 0;
      entry.unsubscribe = noop;
    } else {
      var is_synchronous_callback = true;
      entry.unsubscribe = subscribe_to_store(store, (v) => {
        if (is_synchronous_callback) {
          entry.source.v = v;
        } else {
          set(entry.source, v);
        }
      });
      is_synchronous_callback = false;
    }
  }
  if (store && IS_UNMOUNTED in stores) {
    return get(store);
  }
  return get$1(entry.source);
}
function store_set(store, value) {
  store.set(value);
  return value;
}
function setup_stores() {
  const stores = {};
  function cleanup() {
    teardown(() => {
      for (var store_name in stores) {
        const ref = stores[store_name];
        ref.unsubscribe();
      }
      define_property(stores, IS_UNMOUNTED, {
        enumerable: false,
        value: true
      });
    });
  }
  return [stores, cleanup];
}
function capture_store_binding(fn) {
  var previous_is_store_binding = is_store_binding;
  try {
    is_store_binding = false;
    return [fn(), is_store_binding];
  } finally {
    is_store_binding = previous_is_store_binding;
  }
}
function update_prop(fn, d = 1) {
  const value = fn();
  fn(value + d);
  return value;
}
const rest_props_handler = {
  get(target, key) {
    if (target.exclude.includes(key)) return;
    return target.props[key];
  },
  set(target, key) {
    if (DEV) {
      props_rest_readonly(`${target.name}.${String(key)}`);
    }
    return false;
  },
  getOwnPropertyDescriptor(target, key) {
    if (target.exclude.includes(key)) return;
    if (key in target.props) {
      return {
        enumerable: true,
        configurable: true,
        value: target.props[key]
      };
    }
  },
  has(target, key) {
    if (target.exclude.includes(key)) return false;
    return key in target.props;
  },
  ownKeys(target) {
    return Reflect.ownKeys(target.props).filter((key) => !target.exclude.includes(key));
  }
};
// @__NO_SIDE_EFFECTS__
function rest_props(props, exclude, name) {
  return new Proxy(
    DEV ? { props, exclude, name, other: {}, to_proxy: [] } : { props, exclude },
    rest_props_handler
  );
}
const legacy_rest_props_handler = {
  get(target, key) {
    if (target.exclude.includes(key)) return;
    get$1(target.version);
    return key in target.special ? target.special[key]() : target.props[key];
  },
  set(target, key, value) {
    if (!(key in target.special)) {
      var previous_effect = active_effect;
      try {
        set_active_effect(target.parent_effect);
        target.special[key] = prop(
          {
            get [key]() {
              return target.props[key];
            }
          },
          /** @type {string} */
          key,
          PROPS_IS_UPDATED
        );
      } finally {
        set_active_effect(previous_effect);
      }
    }
    target.special[key](value);
    update(target.version);
    return true;
  },
  getOwnPropertyDescriptor(target, key) {
    if (target.exclude.includes(key)) return;
    if (key in target.props) {
      return {
        enumerable: true,
        configurable: true,
        value: target.props[key]
      };
    }
  },
  deleteProperty(target, key) {
    if (target.exclude.includes(key)) return true;
    target.exclude.push(key);
    update(target.version);
    return true;
  },
  has(target, key) {
    if (target.exclude.includes(key)) return false;
    return key in target.props;
  },
  ownKeys(target) {
    return Reflect.ownKeys(target.props).filter((key) => !target.exclude.includes(key));
  }
};
function legacy_rest_props(props, exclude) {
  return new Proxy(
    {
      props,
      exclude,
      special: {},
      version: source(0),
      // TODO this is only necessary because we need to track component
      // destruction inside `prop`, because of `bind:this`, but it
      // seems likely that we can simplify `bind:this` instead
      parent_effect: (
        /** @type {Effect} */
        active_effect
      )
    },
    legacy_rest_props_handler
  );
}
const spread_props_handler = {
  get(target, key) {
    let i = target.props.length;
    while (i--) {
      let p = target.props[i];
      if (is_function(p)) p = p();
      if (typeof p === "object" && p !== null && key in p) return p[key];
    }
  },
  set(target, key, value) {
    let i = target.props.length;
    while (i--) {
      let p = target.props[i];
      if (is_function(p)) p = p();
      const desc = get_descriptor(p, key);
      if (desc && desc.set) {
        desc.set(value);
        return true;
      }
    }
    return false;
  },
  getOwnPropertyDescriptor(target, key) {
    let i = target.props.length;
    while (i--) {
      let p = target.props[i];
      if (is_function(p)) p = p();
      if (typeof p === "object" && p !== null && key in p) {
        const descriptor = get_descriptor(p, key);
        if (descriptor && !descriptor.configurable) {
          descriptor.configurable = true;
        }
        return descriptor;
      }
    }
  },
  has(target, key) {
    if (key === STATE_SYMBOL || key === LEGACY_PROPS) return false;
    for (let p of target.props) {
      if (is_function(p)) p = p();
      if (p != null && key in p) return true;
    }
    return false;
  },
  ownKeys(target) {
    const keys = [];
    for (let p of target.props) {
      if (is_function(p)) p = p();
      if (!p) continue;
      for (const key in p) {
        if (!keys.includes(key)) keys.push(key);
      }
      for (const key of Object.getOwnPropertySymbols(p)) {
        if (!keys.includes(key)) keys.push(key);
      }
    }
    return keys;
  }
};
function spread_props(...props) {
  return new Proxy({ props }, spread_props_handler);
}
function prop(props, key, flags, fallback) {
  var runes = !legacy_mode_flag || (flags & PROPS_IS_RUNES) !== 0;
  var bindable = (flags & PROPS_IS_BINDABLE) !== 0;
  var lazy = (flags & PROPS_IS_LAZY_INITIAL) !== 0;
  var fallback_value = (
    /** @type {V} */
    fallback
  );
  var fallback_dirty = true;
  var get_fallback = () => {
    if (fallback_dirty) {
      fallback_dirty = false;
      fallback_value = lazy ? untrack(
        /** @type {() => V} */
        fallback
      ) : (
        /** @type {V} */
        fallback
      );
    }
    return fallback_value;
  };
  var setter;
  if (bindable) {
    var is_entry_props = STATE_SYMBOL in props || LEGACY_PROPS in props;
    setter = get_descriptor(props, key)?.set ?? (is_entry_props && key in props ? (v) => props[key] = v : void 0);
  }
  var initial_value;
  var is_store_sub = false;
  if (bindable) {
    [initial_value, is_store_sub] = capture_store_binding(() => (
      /** @type {V} */
      props[key]
    ));
  } else {
    initial_value = /** @type {V} */
    props[key];
  }
  if (initial_value === void 0 && fallback !== void 0) {
    initial_value = get_fallback();
    if (setter) {
      if (runes) props_invalid_value(key);
      setter(initial_value);
    }
  }
  var getter;
  if (runes) {
    getter = () => {
      var value = (
        /** @type {V} */
        props[key]
      );
      if (value === void 0) return get_fallback();
      fallback_dirty = true;
      return value;
    };
  } else {
    getter = () => {
      var value = (
        /** @type {V} */
        props[key]
      );
      if (value !== void 0) {
        fallback_value = /** @type {V} */
        void 0;
      }
      return value === void 0 ? fallback_value : value;
    };
  }
  if (runes && (flags & PROPS_IS_UPDATED) === 0) {
    return getter;
  }
  if (setter) {
    var legacy_parent = props.$$legacy;
    return (
      /** @type {() => V} */
      (function(value, mutation) {
        if (arguments.length > 0) {
          if (!runes || !mutation || legacy_parent || is_store_sub) {
            setter(mutation ? getter() : value);
          }
          return value;
        }
        return getter();
      })
    );
  }
  var overridden = false;
  var d = ((flags & PROPS_IS_IMMUTABLE) !== 0 ? derived : derived_safe_equal)(() => {
    overridden = false;
    return getter();
  });
  if (DEV) {
    d.label = key;
  }
  if (bindable) get$1(d);
  var parent_effect = (
    /** @type {Effect} */
    active_effect
  );
  return (
    /** @type {() => V} */
    (function(value, mutation) {
      if (arguments.length > 0) {
        const new_value = mutation ? get$1(d) : runes && bindable ? proxy(value) : value;
        set(d, new_value);
        overridden = true;
        if (fallback_value !== void 0) {
          fallback_value = new_value;
        }
        return value;
      }
      if (is_destroying_effect && overridden || (parent_effect.f & DESTROYED) !== 0) {
        return d.v;
      }
      return get$1(d);
    })
  );
}
const scriptRel = "modulepreload";
const assetsURL = function(dep, importerUrl) {
  return new URL(dep, importerUrl).href;
};
const seen = {};
const __vitePreload = function preload(baseModule, deps, importerUrl) {
  let promise = Promise.resolve();
  if (deps && deps.length > 0) {
    let allSettled = function(promises$2) {
      return Promise.all(promises$2.map((p) => Promise.resolve(p).then((value$1) => ({
        status: "fulfilled",
        value: value$1
      }), (reason) => ({
        status: "rejected",
        reason
      }))));
    };
    const links = document.getElementsByTagName("link");
    const cspNonceMeta = document.querySelector("meta[property=csp-nonce]");
    const cspNonce = cspNonceMeta?.nonce || cspNonceMeta?.getAttribute("nonce");
    promise = allSettled(deps.map((dep) => {
      dep = assetsURL(dep, importerUrl);
      if (dep in seen) return;
      seen[dep] = true;
      const isCss = dep.endsWith(".css");
      const cssSelector = isCss ? '[rel="stylesheet"]' : "";
      if (!!importerUrl) for (let i$1 = links.length - 1; i$1 >= 0; i$1--) {
        const link$1 = links[i$1];
        if (link$1.href === dep && (!isCss || link$1.rel === "stylesheet")) return;
      }
      else if (document.querySelector(`link[href="${dep}"]${cssSelector}`)) return;
      const link = document.createElement("link");
      link.rel = isCss ? "stylesheet" : scriptRel;
      if (!isCss) link.as = "script";
      link.crossOrigin = "";
      link.href = dep;
      if (cspNonce) link.setAttribute("nonce", cspNonce);
      document.head.appendChild(link);
      if (isCss) return new Promise((res, rej) => {
        link.addEventListener("load", res);
        link.addEventListener("error", () => rej(/* @__PURE__ */ new Error(`Unable to preload CSS for ${dep}`)));
      });
    }));
  }
  function handlePreloadError(err$2) {
    const e$1 = new Event("vite:preloadError", { cancelable: true });
    e$1.payload = err$2;
    window.dispatchEvent(e$1);
    if (!e$1.defaultPrevented) throw err$2;
  }
  return promise.then((res) => {
    for (const item of res || []) {
      if (item.status !== "rejected") continue;
      handlePreloadError(item.reason);
    }
    return baseModule().catch(handlePreloadError);
  });
};
export {
  BranchManager as B,
  __vitePreload as _,
  store_get as a,
  bind_this as b,
  component as c,
  store_set as d,
  setup_stores as e,
  if_block as i,
  legacy_rest_props as l,
  prop as p,
  rest_props as r,
  spread_props as s,
  update_prop as u
};
//# sourceMappingURL=DUftb7my.js.map
