import "./9B4_veAf.js";
import { p as push, I as onMount, i as legacy_pre_effect, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, z as event, $ as $window, d as child, r as reset, s as sibling, E as next, j as set, m as mutable_source, k as get, t as template_effect, b as append, o as pop, q as createEventDispatcher, aR as replay_events, K as tick, v as first_child, x as derived_safe_equal, y as untrack, D as comment, a5 as flushSync, J as state, L as proxy, M as user_effect, A as user_derived } from "./DEzry6cj.js";
import { p as prop, b as bind_this, l as legacy_rest_props, a as store_get, i as if_block, e as setup_stores, r as rest_props, s as spread_props } from "./DUftb7my.js";
import { a6 as raf, a7 as loop, a8 as is_date, a as set_class, p as set_style, d as attribute_effect, S as STYLE, a9 as CLASS, I as IconButtonWrapper, b as IconButton, c as bubble_event, C as Clear, i as bind_element_size, G as Gradio, B as Block, g as Static } from "./DXi4jxVF.js";
import "./BAp-OWo-.js";
import { i as init } from "./DB0xzveP.js";
import { s as slot } from "./DX-MI-YE.js";
import { s as select } from "./DecYamOG.js";
import { d as dispatch } from "./Qrw4qHro.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { D as DownloadLink } from "./BFO3TfnI.js";
import { E as Empty } from "./B-xg5Dhl.js";
import { D as Download } from "./rkplYKOt.js";
import { I as Image } from "./dWqAVU0H.js";
import { U as Undo } from "./oKXAgRt1.js";
import { F as FullscreenButton } from "./BAYq2deR.js";
import { w as writable } from "./DdkXqxbl.js";
import { U as Upload } from "./BcroWaqq.js";
/* empty css         */
import { U as UploadText } from "./B8mIV0gF.js";
function linear(t) {
  return t;
}
function get_interpolator(a, b) {
  if (a === b || a !== a) return () => a;
  const type = typeof a;
  if (type !== typeof b || Array.isArray(a) !== Array.isArray(b)) {
    throw new Error("Cannot interpolate values of different type");
  }
  if (Array.isArray(a)) {
    const arr = (
      /** @type {Array<any>} */
      b.map((bi, i) => {
        return get_interpolator(
          /** @type {Array<any>} */
          a[i],
          bi
        );
      })
    );
    return (t) => arr.map((fn) => fn(t));
  }
  if (type === "object") {
    if (!a || !b) {
      throw new Error("Object cannot be null");
    }
    if (is_date(a) && is_date(b)) {
      const an = a.getTime();
      const bn = b.getTime();
      const delta = bn - an;
      return (t) => new Date(an + t * delta);
    }
    const keys = Object.keys(b);
    const interpolators = {};
    keys.forEach((key) => {
      interpolators[key] = get_interpolator(a[key], b[key]);
    });
    return (t) => {
      const result = {};
      keys.forEach((key) => {
        result[key] = interpolators[key](t);
      });
      return result;
    };
  }
  if (type === "number") {
    const delta = (
      /** @type {number} */
      b - /** @type {number} */
      a
    );
    return (t) => a + t * delta;
  }
  return () => b;
}
function tweened(value, defaults = {}) {
  const store = writable(value);
  let task;
  let target_value = value;
  function set2(new_value, opts) {
    target_value = new_value;
    if (value == null) {
      store.set(value = new_value);
      return Promise.resolve();
    }
    let previous_task = task;
    let started = false;
    let {
      delay = 0,
      duration = 400,
      easing = linear,
      interpolate = get_interpolator
    } = { ...defaults, ...opts };
    if (duration === 0) {
      if (previous_task) {
        previous_task.abort();
        previous_task = null;
      }
      store.set(value = target_value);
      return Promise.resolve();
    }
    const start = raf.now() + delay;
    let fn;
    task = loop((now) => {
      if (now < start) return true;
      if (!started) {
        fn = interpolate(
          /** @type {any} */
          value,
          new_value
        );
        if (typeof duration === "function")
          duration = duration(
            /** @type {any} */
            value,
            new_value
          );
        started = true;
      }
      if (previous_task) {
        previous_task.abort();
        previous_task = null;
      }
      const elapsed = now - start;
      if (elapsed > /** @type {number} */
      duration) {
        store.set(value = new_value);
        return false;
      }
      store.set(value = fn(easing(elapsed / duration)));
      return true;
    });
    return task.promise;
  }
  return {
    set: set2,
    update: (fn, opts) => set2(fn(
      /** @type {any} */
      target_value,
      /** @type {any} */
      value
    ), opts),
    subscribe: store.subscribe
  };
}
function sourceEvent(event2) {
  let sourceEvent2;
  while (sourceEvent2 = event2.sourceEvent) event2 = sourceEvent2;
  return event2;
}
function pointer(event2, node) {
  event2 = sourceEvent(event2);
  if (node === void 0) node = event2.currentTarget;
  if (node) {
    var svg = node.ownerSVGElement || node;
    if (svg.createSVGPoint) {
      var point = svg.createSVGPoint();
      point.x = event2.clientX, point.y = event2.clientY;
      point = point.matrixTransform(node.getScreenCTM().inverse());
      return [point.x, point.y];
    }
    if (node.getBoundingClientRect) {
      var rect = node.getBoundingClientRect();
      return [event2.clientX - rect.left - node.clientLeft, event2.clientY - rect.top - node.clientTop];
    }
  }
  return [event2.pageX, event2.pageY];
}
const nonpassive = { passive: false };
const nonpassivecapture = { capture: true, passive: false };
function nopropagation(event2) {
  event2.stopImmediatePropagation();
}
function noevent(event2) {
  event2.preventDefault();
  event2.stopImmediatePropagation();
}
function dragDisable(view) {
  var root2 = view.document.documentElement, selection = select(view).on("dragstart.drag", noevent, nonpassivecapture);
  if ("onselectstart" in root2) {
    selection.on("selectstart.drag", noevent, nonpassivecapture);
  } else {
    root2.__noselect = root2.style.MozUserSelect;
    root2.style.MozUserSelect = "none";
  }
}
function yesdrag(view, noclick) {
  var root2 = view.document.documentElement, selection = select(view).on("dragstart.drag", null);
  if (noclick) {
    selection.on("click.drag", noevent, nonpassivecapture);
    setTimeout(function() {
      selection.on("click.drag", null);
    }, 0);
  }
  if ("onselectstart" in root2) {
    selection.on("selectstart.drag", null);
  } else {
    root2.style.MozUserSelect = root2.__noselect;
    delete root2.__noselect;
  }
}
const constant = (x) => () => x;
function DragEvent(type, {
  sourceEvent: sourceEvent2,
  subject,
  target,
  identifier,
  active,
  x,
  y,
  dx,
  dy,
  dispatch: dispatch2
}) {
  Object.defineProperties(this, {
    type: { value: type, enumerable: true, configurable: true },
    sourceEvent: { value: sourceEvent2, enumerable: true, configurable: true },
    subject: { value: subject, enumerable: true, configurable: true },
    target: { value: target, enumerable: true, configurable: true },
    identifier: { value: identifier, enumerable: true, configurable: true },
    active: { value: active, enumerable: true, configurable: true },
    x: { value: x, enumerable: true, configurable: true },
    y: { value: y, enumerable: true, configurable: true },
    dx: { value: dx, enumerable: true, configurable: true },
    dy: { value: dy, enumerable: true, configurable: true },
    _: { value: dispatch2 }
  });
}
DragEvent.prototype.on = function() {
  var value = this._.on.apply(this._, arguments);
  return value === this._ ? this : value;
};
function defaultFilter(event2) {
  return !event2.ctrlKey && !event2.button;
}
function defaultContainer() {
  return this.parentNode;
}
function defaultSubject(event2, d) {
  return d == null ? { x: event2.x, y: event2.y } : d;
}
function defaultTouchable() {
  return navigator.maxTouchPoints || "ontouchstart" in this;
}
function drag() {
  var filter = defaultFilter, container = defaultContainer, subject = defaultSubject, touchable = defaultTouchable, gestures = {}, listeners = dispatch("start", "drag", "end"), active = 0, mousedownx, mousedowny, mousemoving, touchending, clickDistance2 = 0;
  function drag2(selection) {
    selection.on("mousedown.drag", mousedowned).filter(touchable).on("touchstart.drag", touchstarted).on("touchmove.drag", touchmoved, nonpassive).on("touchend.drag touchcancel.drag", touchended).style("touch-action", "none").style("-webkit-tap-highlight-color", "rgba(0,0,0,0)");
  }
  function mousedowned(event2, d) {
    if (touchending || !filter.call(this, event2, d)) return;
    var gesture = beforestart(this, container.call(this, event2, d), event2, d, "mouse");
    if (!gesture) return;
    select(event2.view).on("mousemove.drag", mousemoved, nonpassivecapture).on("mouseup.drag", mouseupped, nonpassivecapture);
    dragDisable(event2.view);
    nopropagation(event2);
    mousemoving = false;
    mousedownx = event2.clientX;
    mousedowny = event2.clientY;
    gesture("start", event2);
  }
  function mousemoved(event2) {
    noevent(event2);
    if (!mousemoving) {
      var dx = event2.clientX - mousedownx, dy = event2.clientY - mousedowny;
      mousemoving = dx * dx + dy * dy > clickDistance2;
    }
    gestures.mouse("drag", event2);
  }
  function mouseupped(event2) {
    select(event2.view).on("mousemove.drag mouseup.drag", null);
    yesdrag(event2.view, mousemoving);
    noevent(event2);
    gestures.mouse("end", event2);
  }
  function touchstarted(event2, d) {
    if (!filter.call(this, event2, d)) return;
    var touches = event2.changedTouches, c = container.call(this, event2, d), n = touches.length, i, gesture;
    for (i = 0; i < n; ++i) {
      if (gesture = beforestart(this, c, event2, d, touches[i].identifier, touches[i])) {
        nopropagation(event2);
        gesture("start", event2, touches[i]);
      }
    }
  }
  function touchmoved(event2) {
    var touches = event2.changedTouches, n = touches.length, i, gesture;
    for (i = 0; i < n; ++i) {
      if (gesture = gestures[touches[i].identifier]) {
        noevent(event2);
        gesture("drag", event2, touches[i]);
      }
    }
  }
  function touchended(event2) {
    var touches = event2.changedTouches, n = touches.length, i, gesture;
    if (touchending) clearTimeout(touchending);
    touchending = setTimeout(function() {
      touchending = null;
    }, 500);
    for (i = 0; i < n; ++i) {
      if (gesture = gestures[touches[i].identifier]) {
        nopropagation(event2);
        gesture("end", event2, touches[i]);
      }
    }
  }
  function beforestart(that, container2, event2, d, identifier, touch) {
    var dispatch2 = listeners.copy(), p = pointer(touch || event2, container2), dx, dy, s;
    if ((s = subject.call(that, new DragEvent("beforestart", {
      sourceEvent: event2,
      target: drag2,
      identifier,
      active,
      x: p[0],
      y: p[1],
      dx: 0,
      dy: 0,
      dispatch: dispatch2
    }), d)) == null) return;
    dx = s.x - p[0] || 0;
    dy = s.y - p[1] || 0;
    return function gesture(type, event3, touch2) {
      var p0 = p, n;
      switch (type) {
        case "start":
          gestures[identifier] = gesture, n = active++;
          break;
        case "end":
          delete gestures[identifier], --active;
        // falls through
        case "drag":
          p = pointer(touch2 || event3, container2), n = active;
          break;
      }
      dispatch2.call(
        type,
        that,
        new DragEvent(type, {
          sourceEvent: event3,
          subject: s,
          target: drag2,
          identifier,
          active: n,
          x: p[0] + dx,
          y: p[1] + dy,
          dx: p[0] - p0[0],
          dy: p[1] - p0[1],
          dispatch: dispatch2
        }),
        d
      );
    };
  }
  drag2.filter = function(_) {
    return arguments.length ? (filter = typeof _ === "function" ? _ : constant(!!_), drag2) : filter;
  };
  drag2.container = function(_) {
    return arguments.length ? (container = typeof _ === "function" ? _ : constant(_), drag2) : container;
  };
  drag2.subject = function(_) {
    return arguments.length ? (subject = typeof _ === "function" ? _ : constant(_), drag2) : subject;
  };
  drag2.touchable = function(_) {
    return arguments.length ? (touchable = typeof _ === "function" ? _ : constant(!!_), drag2) : touchable;
  };
  drag2.on = function() {
    var value = listeners.on.apply(listeners, arguments);
    return value === listeners ? drag2 : value;
  };
  drag2.clickDistance = function(_) {
    return arguments.length ? (clickDistance2 = (_ = +_) * _, drag2) : Math.sqrt(clickDistance2);
  };
  return drag2;
}
var root$3 = from_html(`<div class="wrap svelte-b2bl92" role="none"><div class="content svelte-b2bl92"><!></div> <div role="none"><span><span class="icon left svelte-b2bl92">◢</span><span class="icon center svelte-b2bl92"></span><span class="icon right svelte-b2bl92">◢</span></span> <div class="inner svelte-b2bl92"></div></div></div>`);
function Slider($$anchor, $$props) {
  push($$props, false);
  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }
  let position = prop($$props, "position", 12, 0.5);
  let disabled = prop($$props, "disabled", 8, false);
  let slider_color = prop($$props, "slider_color", 8, "var(--border-color-primary)");
  let image_size = prop($$props, "image_size", 28, () => ({ top: 0, left: 0, width: 0, height: 0 }));
  let el = prop($$props, "el", 12, void 0);
  let parent_el = prop($$props, "parent_el", 12, void 0);
  let inner = mutable_source();
  let px = mutable_source(0);
  let active = mutable_source(false);
  let container_width = 0;
  function set_position(width) {
    container_width = parent_el()?.getBoundingClientRect().width || 0;
    if (width === 0) {
      image_size(image_size().width = el()?.getBoundingClientRect().width || 0, true);
    }
    set(px, clamp(image_size().width * position() + image_size().left, 0, container_width));
  }
  function round(n, points) {
    const mod = Math.pow(10, points);
    return Math.round((n + Number.EPSILON) * mod) / mod;
  }
  function update_position(x) {
    set(px, clamp(x, 0, container_width));
    position(round((x - image_size().left) / image_size().width, 5));
  }
  function drag_start(event2) {
    if (disabled()) return;
    set(active, true);
    update_position(event2.x);
  }
  function drag_move(event2) {
    if (disabled()) return;
    update_position(event2.x);
  }
  function drag_end() {
    if (disabled()) return;
    set(active, false);
  }
  function update_position_from_pc(pc) {
    set(px, clamp(image_size().width * pc + image_size().left, 0, container_width));
  }
  onMount(() => {
    set_position(image_size().width);
    const drag_handler = drag().on("start", drag_start).on("drag", drag_move).on("end", drag_end);
    select(get(inner)).call(drag_handler);
  });
  legacy_pre_effect(() => deep_read_state(image_size()), () => {
    set_position(image_size().width);
  });
  legacy_pre_effect(() => deep_read_state(position()), () => {
    update_position_from_pc(position());
  });
  legacy_pre_effect_reset();
  init();
  var div = root$3();
  event("resize", $window, () => set_position(image_size().width));
  var div_1 = child(div);
  var node = child(div_1);
  slot(node, $$props, "default", {}, null);
  reset(div_1);
  bind_this(div_1, ($$value) => el($$value), () => el());
  var div_2 = sibling(div_1, 2);
  let classes;
  var span = child(div_2);
  let classes_1;
  var span_1 = sibling(child(span));
  let styles;
  next();
  reset(span);
  var div_3 = sibling(span, 2);
  let styles_1;
  reset(div_2);
  bind_this(div_2, ($$value) => set(inner, $$value), () => get(inner));
  reset(div);
  bind_this(div, ($$value) => parent_el($$value), () => parent_el());
  template_effect(() => {
    classes = set_class(div_2, 1, "outer svelte-b2bl92", null, classes, { disabled: disabled(), grab: get(active) });
    set_style(div_2, `transform: translateX(${get(px) ?? ""}px)`);
    classes_1 = set_class(span, 1, "icon-wrap svelte-b2bl92", null, classes_1, { active: get(active), disabled: disabled() });
    styles = set_style(span_1, "", styles, { "--color": slider_color() });
    styles_1 = set_style(div_3, "", styles_1, { "--color": slider_color() });
  });
  append($$anchor, div);
  pop();
}
var root$2 = from_html(`<img/>`);
function ImageEl($$anchor, $$props) {
  const $$sanitized_props = legacy_rest_props($$props, ["children", "$$slots", "$$events", "$$legacy"]);
  const $$restProps = legacy_rest_props($$sanitized_props, [
    "src",
    "fullscreen",
    "fixed",
    "transform",
    "img_el",
    "hidden",
    "variant",
    "max_height"
  ]);
  push($$props, false);
  let src = prop($$props, "src", 8, void 0);
  let fullscreen = prop($$props, "fullscreen", 8, false);
  let fixed = prop($$props, "fixed", 8, false);
  let transform = prop($$props, "transform", 8, "translate(0px, 0px) scale(1)");
  let img_el = prop($$props, "img_el", 12, null);
  let hidden = prop($$props, "hidden", 8, false);
  let variant = prop($$props, "variant", 8, "upload");
  let max_height = prop($$props, "max_height", 8, 500);
  const dispatch2 = createEventDispatcher();
  function get_image_size(img) {
    if (!img) return { top: 0, left: 0, width: 0, height: 0 };
    const container = img.parentElement?.getBoundingClientRect();
    if (!container) return { top: 0, left: 0, width: 0, height: 0 };
    const naturalAspect = img.naturalWidth / img.naturalHeight;
    const containerAspect = container.width / container.height;
    let displayedWidth, displayedHeight;
    if (naturalAspect > containerAspect) {
      displayedWidth = container.width;
      displayedHeight = container.width / naturalAspect;
    } else {
      displayedHeight = container.height;
      displayedWidth = container.height * naturalAspect;
    }
    const offsetX = (container.width - displayedWidth) / 2;
    const offsetY = (container.height - displayedHeight) / 2;
    return {
      top: offsetY,
      left: offsetX,
      width: displayedWidth,
      height: displayedHeight
    };
  }
  onMount(() => {
    const resizer = new ResizeObserver(async (entries) => {
      for (const entry of entries) {
        await tick();
        dispatch2("load", get_image_size(img_el()));
      }
    });
    resizer.observe(img_el());
    return () => {
      resizer.disconnect();
    };
  });
  init();
  var img_1 = root$2();
  attribute_effect(
    img_1,
    () => ({
      src: src(),
      ...$$restProps,
      [CLASS]: {
        fixed: fixed(),
        hidden: hidden(),
        preview: variant() === "preview",
        slider: variant() === "upload",
        fullscreen: fullscreen(),
        small: !fullscreen()
      },
      [STYLE]: {
        transform: transform(),
        "max-height": max_height() && !fullscreen() ? `${max_height()}px` : null
      }
    }),
    void 0,
    void 0,
    void 0,
    "svelte-j3ek2n"
  );
  bind_this(img_1, ($$value) => img_el($$value), () => img_el());
  replay_events(img_1);
  event("load", img_1, () => dispatch2("load", get_image_size(img_el())));
  append($$anchor, img_1);
  pop();
}
class ZoomableImage {
  container;
  image;
  scale;
  offsetX;
  offsetY;
  isDragging;
  lastX;
  lastY;
  initial_left_padding;
  initial_top_padding;
  initial_width;
  initial_height;
  subscribers;
  handleImageLoad;
  real_image_size = { top: 0, left: 0, width: 0, height: 0 };
  last_touch_distance;
  constructor(container, image) {
    this.container = container;
    this.image = image;
    this.scale = 1;
    this.offsetX = 0;
    this.offsetY = 0;
    this.isDragging = false;
    this.lastX = 0;
    this.lastY = 0;
    this.initial_left_padding = 0;
    this.initial_top_padding = 0;
    this.initial_width = 0;
    this.initial_height = 0;
    this.subscribers = [];
    this.last_touch_distance = 0;
    this.handleWheel = this.handleWheel.bind(this);
    this.handleMouseDown = this.handleMouseDown.bind(this);
    this.handleMouseMove = this.handleMouseMove.bind(this);
    this.handleMouseUp = this.handleMouseUp.bind(this);
    this.handleImageLoad = this.init.bind(this);
    this.handleTouchStart = this.handleTouchStart.bind(this);
    this.handleTouchMove = this.handleTouchMove.bind(this);
    this.handleTouchEnd = this.handleTouchEnd.bind(this);
    this.image.addEventListener("load", this.handleImageLoad);
    this.container.addEventListener("wheel", this.handleWheel);
    this.container.addEventListener("mousedown", this.handleMouseDown);
    document.addEventListener("mousemove", this.handleMouseMove);
    document.addEventListener("mouseup", this.handleMouseUp);
    this.container.addEventListener("touchstart", this.handleTouchStart);
    document.addEventListener("touchmove", this.handleTouchMove);
    document.addEventListener("touchend", this.handleTouchEnd);
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.target === this.container) {
          this.handleResize();
          this.get_image_size(this.image);
        }
      }
    });
    observer.observe(this.container);
  }
  handleResize() {
    this.init();
  }
  init() {
    const containerRect = this.container.getBoundingClientRect();
    const imageRect = this.image.getBoundingClientRect();
    this.initial_left_padding = imageRect.left - containerRect.left;
    this.initial_top_padding = imageRect.top - containerRect.top;
    this.initial_width = imageRect.width;
    this.initial_height = imageRect.height;
    this.reset_zoom();
    this.updateTransform();
  }
  reset_zoom() {
    this.scale = 1;
    this.offsetX = 0;
    this.offsetY = 0;
    this.updateTransform();
  }
  handleMouseDown(e) {
    const imageRect = this.image.getBoundingClientRect();
    if (e.clientX >= imageRect.left && e.clientX <= imageRect.right && e.clientY >= imageRect.top && e.clientY <= imageRect.bottom) {
      e.preventDefault();
      if (this.scale === 1) return;
      this.isDragging = true;
      this.lastX = e.clientX;
      this.lastY = e.clientY;
      this.image.style.cursor = "grabbing";
    }
  }
  handleMouseMove(e) {
    if (!this.isDragging) return;
    const deltaX = e.clientX - this.lastX;
    const deltaY = e.clientY - this.lastY;
    this.offsetX += deltaX;
    this.offsetY += deltaY;
    this.lastX = e.clientX;
    this.lastY = e.clientY;
    this.updateTransform();
    this.updateTransform();
  }
  handleMouseUp() {
    if (this.isDragging) {
      this.constrain_to_bounds(true);
      this.updateTransform();
      this.isDragging = false;
      this.image.style.cursor = this.scale > 1 ? "grab" : "zoom-in";
    }
  }
  async handleWheel(e) {
    e.preventDefault();
    const containerRect = this.container.getBoundingClientRect();
    const imageRect = this.image.getBoundingClientRect();
    if (e.clientX < imageRect.left || e.clientX > imageRect.right || e.clientY < imageRect.top || e.clientY > imageRect.bottom) {
      return;
    }
    const zoomFactor = 1.05;
    const oldScale = this.scale;
    const newScale = -Math.sign(e.deltaY) > 0 ? Math.min(15, oldScale * zoomFactor) : Math.max(1, oldScale / zoomFactor);
    if (newScale === oldScale) return;
    const cursorX = e.clientX - containerRect.left - this.initial_left_padding;
    const cursorY = e.clientY - containerRect.top - this.initial_top_padding;
    this.scale = newScale;
    this.offsetX = this.compute_new_offset({
      cursor_position: cursorX,
      current_offset: this.offsetX,
      new_scale: newScale,
      old_scale: oldScale
    });
    this.offsetY = this.compute_new_offset({
      cursor_position: cursorY,
      current_offset: this.offsetY,
      new_scale: newScale,
      old_scale: oldScale
    });
    this.updateTransform();
    this.constrain_to_bounds();
    this.updateTransform();
    this.image.style.cursor = this.scale > 1 ? "grab" : "zoom-in";
  }
  // compute_offset_for_positions({ position: number, scale: number }) {
  // 	return position - (scale / this.scale) * (position - this.offset);
  // }
  compute_new_position({
    position,
    scale,
    anchor_position
  }) {
    return position - (position - anchor_position) * (scale / this.scale);
  }
  compute_new_offset({
    cursor_position,
    current_offset,
    new_scale,
    old_scale
  }) {
    return cursor_position - new_scale / old_scale * (cursor_position - current_offset);
  }
  constrain_to_bounds(pan = false) {
    if (this.scale === 1) {
      this.offsetX = 0;
      this.offsetY = 0;
      return;
    }
    const onscreen = {
      top: this.real_image_size.top * this.scale + this.offsetY,
      left: this.real_image_size.left * this.scale + this.offsetX,
      width: this.real_image_size.width * this.scale,
      height: this.real_image_size.height * this.scale,
      bottom: this.real_image_size.top * this.scale + this.offsetY + this.real_image_size.height * this.scale,
      right: this.real_image_size.left * this.scale + this.offsetX + this.real_image_size.width * this.scale
    };
    const real_image_size_right = this.real_image_size.left + this.real_image_size.width;
    const real_image_size_bottom = this.real_image_size.top + this.real_image_size.height;
    if (pan) {
      if (onscreen.top > this.real_image_size.top) {
        this.offsetY = this.calculate_position(
          this.real_image_size.top,
          0,
          "y"
        );
      } else if (onscreen.bottom < real_image_size_bottom) {
        this.offsetY = this.calculate_position(real_image_size_bottom, 1, "y");
      }
      if (onscreen.left > this.real_image_size.left) {
        this.offsetX = this.calculate_position(
          this.real_image_size.left,
          0,
          "x"
        );
      } else if (onscreen.right < real_image_size_right) {
        this.offsetX = this.calculate_position(real_image_size_right, 1, "x");
      }
    }
  }
  updateTransform() {
    this.notify({ x: this.offsetX, y: this.offsetY, scale: this.scale });
  }
  destroy() {
    this.container.removeEventListener("wheel", this.handleWheel);
    this.container.removeEventListener("mousedown", this.handleMouseDown);
    document.removeEventListener("mousemove", this.handleMouseMove);
    document.removeEventListener("mouseup", this.handleMouseUp);
    this.container.removeEventListener("touchstart", this.handleTouchStart);
    document.removeEventListener("touchmove", this.handleTouchMove);
    document.removeEventListener("touchend", this.handleTouchEnd);
    this.image.removeEventListener("load", this.handleImageLoad);
  }
  subscribe(cb) {
    this.subscribers.push(cb);
  }
  unsubscribe(cb) {
    this.subscribers = this.subscribers.filter(
      (subscriber) => subscriber !== cb
    );
  }
  notify({ x, y, scale }) {
    this.subscribers.forEach((subscriber) => subscriber({ x, y, scale }));
  }
  handleTouchStart(e) {
    e.preventDefault();
    const imageRect = this.image.getBoundingClientRect();
    const touch = e.touches[0];
    if (touch.clientX >= imageRect.left && touch.clientX <= imageRect.right && touch.clientY >= imageRect.top && touch.clientY <= imageRect.bottom) {
      if (e.touches.length === 1 && this.scale > 1) {
        this.isDragging = true;
        this.lastX = touch.clientX;
        this.lastY = touch.clientY;
      } else if (e.touches.length === 2) {
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        this.last_touch_distance = Math.hypot(
          touch2.clientX - touch1.clientX,
          touch2.clientY - touch1.clientY
        );
      }
    }
  }
  get_image_size(img) {
    if (!img) return;
    const container = img.parentElement?.getBoundingClientRect();
    if (!container) return;
    const naturalAspect = img.naturalWidth / img.naturalHeight;
    const containerAspect = container.width / container.height;
    let displayedWidth, displayedHeight;
    if (naturalAspect > containerAspect) {
      displayedWidth = container.width;
      displayedHeight = container.width / naturalAspect;
    } else {
      displayedHeight = container.height;
      displayedWidth = container.height * naturalAspect;
    }
    const offsetX = (container.width - displayedWidth) / 2;
    const offsetY = (container.height - displayedHeight) / 2;
    this.real_image_size = {
      top: offsetY,
      left: offsetX,
      width: displayedWidth,
      height: displayedHeight
    };
  }
  handleTouchMove(e) {
    if (e.touches.length === 1 && this.isDragging) {
      e.preventDefault();
      const touch = e.touches[0];
      const deltaX = touch.clientX - this.lastX;
      const deltaY = touch.clientY - this.lastY;
      this.offsetX += deltaX;
      this.offsetY += deltaY;
      this.lastX = touch.clientX;
      this.lastY = touch.clientY;
      this.updateTransform();
    } else if (e.touches.length === 2) {
      e.preventDefault();
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const current_distance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      if (this.last_touch_distance === 0) {
        this.last_touch_distance = current_distance;
        return;
      }
      const zoomFactor = current_distance / this.last_touch_distance;
      const oldScale = this.scale;
      const newScale = Math.min(15, Math.max(1, oldScale * zoomFactor));
      if (newScale === oldScale) {
        this.last_touch_distance = current_distance;
        return;
      }
      const containerRect = this.container.getBoundingClientRect();
      const midX = (touch1.clientX + touch2.clientX) / 2 - containerRect.left - this.initial_left_padding;
      const midY = (touch1.clientY + touch2.clientY) / 2 - containerRect.top - this.initial_top_padding;
      this.scale = newScale;
      this.offsetX = this.compute_new_offset({
        cursor_position: midX,
        current_offset: this.offsetX,
        new_scale: newScale,
        old_scale: oldScale
      });
      this.offsetY = this.compute_new_offset({
        cursor_position: midY,
        current_offset: this.offsetY,
        new_scale: newScale,
        old_scale: oldScale
      });
      this.updateTransform();
      this.constrain_to_bounds();
      this.updateTransform();
      this.last_touch_distance = current_distance;
      this.image.style.cursor = this.scale > 1 ? "grab" : "zoom-in";
    }
  }
  handleTouchEnd(e) {
    if (this.isDragging) {
      this.constrain_to_bounds(true);
      this.updateTransform();
      this.isDragging = false;
    }
    if (e.touches.length === 0) {
      this.last_touch_distance = 0;
    }
  }
  calculate_position(screen_coord, image_anchor, axis) {
    this.container.getBoundingClientRect();
    if (axis === "x") {
      const relative_screen_x = screen_coord;
      const anchor_x = this.real_image_size.left + image_anchor * this.real_image_size.width;
      return relative_screen_x - anchor_x * this.scale;
    }
    if (axis === "y") {
      const relative_screen_y = screen_coord;
      const anchor_y = this.real_image_size.top + image_anchor * this.real_image_size.height;
      return relative_screen_y - anchor_y * this.scale;
    }
    return 0;
  }
}
var root_4$1 = from_html(`<!> <!> <!> <!>`, 1);
var root_9 = from_html(`<!> <!>`, 1);
var root_3$1 = from_html(`<div class="image-container svelte-1880bc6"><!> <div><!></div></div>`);
var root$1 = from_html(`<!> <!>`, 1);
function SliderPreview($$anchor, $$props) {
  push($$props, false);
  const $transform = () => store_get(transform, "$transform", $$stores);
  const [$$stores, $$cleanup] = setup_stores();
  const coords_at_viewport = mutable_source();
  const style = mutable_source();
  let value = prop($$props, "value", 28, () => [null, null]);
  let label = prop($$props, "label", 8, void 0);
  let show_download_button = prop($$props, "show_download_button", 8, true);
  let show_label = prop($$props, "show_label", 8);
  let i18n = prop($$props, "i18n", 8);
  let position = prop($$props, "position", 12);
  let layer_images = prop($$props, "layer_images", 8, true);
  let show_single = prop($$props, "show_single", 8, false);
  let slider_color = prop($$props, "slider_color", 8);
  let show_fullscreen_button = prop($$props, "show_fullscreen_button", 8, true);
  let fullscreen = prop($$props, "fullscreen", 8, false);
  let el_width = prop($$props, "el_width", 12, 0);
  let max_height = prop($$props, "max_height", 8);
  let interactive = prop($$props, "interactive", 8, true);
  const dispatch2 = createEventDispatcher();
  let img = mutable_source();
  let slider_wrap = mutable_source();
  let image_container = mutable_source();
  let transform = tweened({ x: 0, y: 0, z: 1 }, { duration: 75 });
  let parent_el = mutable_source();
  function get_coords_at_viewport(viewport_percent_x, viewportWidth, image_width, img_offset_x, tx, scale) {
    const px_relative_to_image = viewport_percent_x * image_width;
    const pixel_position = px_relative_to_image + img_offset_x;
    const normalised_position = (pixel_position - tx) / scale;
    const percent_position = normalised_position / viewportWidth;
    return percent_position;
  }
  let viewport_width = mutable_source(0);
  let zoomable_image = mutable_source(null);
  let observer = null;
  function init_image(img2, slider_wrap2) {
    if (!img2 || !slider_wrap2) return;
    get(zoomable_image)?.destroy();
    observer?.disconnect();
    img2?.getBoundingClientRect().width || 0;
    set(viewport_width, slider_wrap2?.getBoundingClientRect().width || 0);
    set(zoomable_image, new ZoomableImage(slider_wrap2, img2));
    get(zoomable_image).subscribe(({ x, y, scale }) => {
      transform.set({ x, y, z: scale });
    });
    observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.target === slider_wrap2) {
          set(viewport_width, entry.contentRect.width);
        }
        if (entry.target === img2) {
          entry.contentRect.width;
        }
      }
    });
    observer.observe(slider_wrap2);
    observer.observe(img2);
  }
  onMount(() => {
    return () => {
      get(zoomable_image)?.destroy();
      observer?.disconnect();
    };
  });
  let slider_wrap_parent = mutable_source();
  let image_size = mutable_source({ top: 0, left: 0, width: 0, height: 0 });
  function handle_image_load(event2) {
    set(image_size, event2.detail);
  }
  legacy_pre_effect(
    () => (deep_read_state(position()), get(viewport_width), get(image_size), $transform()),
    () => {
      set(coords_at_viewport, get_coords_at_viewport(position(), get(viewport_width), get(image_size).width, get(image_size).left, $transform().x, $transform().z));
    }
  );
  legacy_pre_effect(() => (deep_read_state(layer_images()), get(coords_at_viewport)), () => {
    set(style, layer_images() ? `clip-path: inset(0 0 0 ${get(coords_at_viewport) * 100}%)` : "");
  });
  legacy_pre_effect(() => (get(img), get(slider_wrap)), () => {
    init_image(get(img), get(slider_wrap));
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root$1();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => (deep_read_state(label()), deep_read_state(i18n()), untrack(() => label() || i18n()("image.image"))));
    BlockLabel(node, {
      get show_label() {
        return show_label();
      },
      get Icon() {
        return Image;
      },
      get label() {
        return get($0);
      }
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent = ($$anchor2) => {
      Empty($$anchor2, {
        unpadded_box: true,
        size: "large",
        children: ($$anchor3, $$slotProps) => {
          Image($$anchor3);
        },
        $$slots: { default: true }
      });
    };
    var alternate = ($$anchor2) => {
      var div = root_3$1();
      var node_2 = child(div);
      IconButtonWrapper(node_2, {
        children: ($$anchor3, $$slotProps) => {
          var fragment_3 = root_4$1();
          var node_3 = first_child(fragment_3);
          {
            let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.undo"))));
            let $1 = derived_safe_equal(() => ($transform(), untrack(() => $transform().z === 1)));
            IconButton(node_3, {
              get Icon() {
                return Undo;
              },
              get label() {
                return get($0);
              },
              get disabled() {
                return get($1);
              },
              $$events: { click: () => get(zoomable_image)?.reset_zoom() }
            });
          }
          var node_4 = sibling(node_3, 2);
          {
            var consequent_1 = ($$anchor4) => {
              FullscreenButton($$anchor4, {
                get fullscreen() {
                  return fullscreen();
                },
                $$events: {
                  fullscreen($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  }
                }
              });
            };
            if_block(node_4, ($$render) => {
              if (show_fullscreen_button()) $$render(consequent_1);
            });
          }
          var node_5 = sibling(node_4, 2);
          {
            var consequent_2 = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value()[1]?.url)));
                let $1 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value()[1]?.orig_name || "image")));
                DownloadLink($$anchor4, {
                  get href() {
                    return get($0);
                  },
                  get download() {
                    return get($1);
                  },
                  children: ($$anchor5, $$slotProps2) => {
                    {
                      let $02 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("common.download"))));
                      IconButton($$anchor5, {
                        get Icon() {
                          return Download;
                        },
                        get label() {
                          return get($02);
                        }
                      });
                    }
                  },
                  $$slots: { default: true }
                });
              }
            };
            if_block(node_5, ($$render) => {
              if (show_download_button()) $$render(consequent_2);
            });
          }
          var node_6 = sibling(node_5, 2);
          {
            var consequent_3 = ($$anchor4) => {
              IconButton($$anchor4, {
                get Icon() {
                  return Clear;
                },
                label: "Remove Image",
                $$events: {
                  click: (event2) => {
                    value([null, null]);
                    dispatch2("clear");
                    event2.stopPropagation();
                  }
                }
              });
            };
            if_block(node_6, ($$render) => {
              if (interactive()) $$render(consequent_3);
            });
          }
          append($$anchor3, fragment_3);
        },
        $$slots: { default: true }
      });
      var div_1 = sibling(node_2, 2);
      let classes;
      var node_7 = child(div_1);
      Slider(node_7, {
        get slider_color() {
          return slider_color();
        },
        get image_size() {
          return get(image_size);
        },
        get position() {
          return position();
        },
        set position($$value) {
          position($$value);
        },
        get el() {
          return get(slider_wrap);
        },
        set el($$value) {
          set(slider_wrap, $$value);
        },
        get parent_el() {
          return get(parent_el);
        },
        set parent_el($$value) {
          set(parent_el, $$value);
        },
        children: ($$anchor3, $$slotProps) => {
          var fragment_8 = root_9();
          var node_8 = first_child(fragment_8);
          {
            let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value()?.[0]?.url)));
            ImageEl(node_8, {
              get src() {
                return get($0);
              },
              alt: "",
              loading: "lazy",
              variant: "preview",
              get transform() {
                return `translate(${($transform(), untrack(() => $transform().x)) ?? ""}px, ${($transform(), untrack(() => $transform().y)) ?? ""}px) scale(${($transform(), untrack(() => $transform().z)) ?? ""})`;
              },
              get fullscreen() {
                return fullscreen();
              },
              get max_height() {
                return max_height();
              },
              get img_el() {
                return get(img);
              },
              set img_el($$value) {
                set(img, $$value);
              },
              $$events: { load: handle_image_load },
              $$legacy: true
            });
          }
          var node_9 = sibling(node_8, 2);
          {
            let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => !value()?.[1]?.url)));
            let $1 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value()?.[1]?.url)));
            ImageEl(node_9, {
              variant: "preview",
              get fixed() {
                return layer_images();
              },
              get hidden() {
                return get($0);
              },
              get src() {
                return get($1);
              },
              alt: "",
              loading: "lazy",
              get style() {
                return `${get(style) ?? ""}; background: var(--block-background-fill);`;
              },
              get transform() {
                return `translate(${($transform(), untrack(() => $transform().x)) ?? ""}px, ${($transform(), untrack(() => $transform().y)) ?? ""}px) scale(${($transform(), untrack(() => $transform().z)) ?? ""})`;
              },
              get fullscreen() {
                return fullscreen();
              },
              get max_height() {
                return max_height();
              },
              $$events: { load: handle_image_load }
            });
          }
          append($$anchor3, fragment_8);
        },
        $$slots: { default: true },
        $$legacy: true
      });
      reset(div_1);
      bind_this(div_1, ($$value) => set(slider_wrap_parent, $$value), () => get(slider_wrap_parent));
      reset(div);
      bind_this(div, ($$value) => set(image_container, $$value), () => get(image_container));
      template_effect(() => classes = set_class(div_1, 1, "slider-wrap svelte-1880bc6", null, classes, { limit_height: !fullscreen() }));
      bind_element_size(div_1, "clientWidth", el_width);
      append($$anchor2, div);
    };
    if_block(node_1, ($$render) => {
      if (deep_read_state(value()), deep_read_state(show_single()), untrack(() => (value() === null || value()[0] === null || value()[1] === null) && !show_single())) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
  $$cleanup();
}
var root = from_html(`<div class="svelte-2ufkjh"><!></div>`);
function ClearImage($$anchor, $$props) {
  push($$props, false);
  const dispatch2 = createEventDispatcher();
  init();
  var div = root();
  var node = child(div);
  IconButton(node, {
    get Icon() {
      return Clear;
    },
    label: "Remove Image",
    $$events: {
      click: (event2) => {
        dispatch2("remove_image");
        event2.stopPropagation();
      }
    }
  });
  reset(div);
  append($$anchor, div);
  pop();
}
var root_3 = from_html(`<div class="icon-buttons svelte-1c8zs50"><!></div>`);
var root_7 = from_html(`<div><!></div>`);
var root_13 = from_html(`<div><!></div>`);
var root_6 = from_html(`<div><!> <!></div>`);
var root_1 = from_html(`<!> <div data-testid="image" class="image-container svelte-1c8zs50"><!> <!> <!></div>`, 1);
function Image_1($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 12);
  let label = prop($$props, "label", 8, void 0);
  let show_label = prop($$props, "show_label", 8);
  let root2 = prop($$props, "root", 8);
  let position = prop($$props, "position", 12);
  let upload_count = prop($$props, "upload_count", 8, 2);
  let show_download_button = prop($$props, "show_download_button", 8, true);
  let slider_color = prop($$props, "slider_color", 8);
  let upload = prop($$props, "upload", 8);
  let stream_handler = prop($$props, "stream_handler", 8);
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let i18n = prop($$props, "i18n", 8);
  let max_height = prop($$props, "max_height", 8);
  let upload_promise = prop($$props, "upload_promise", 12, null);
  let value_ = mutable_source(value() || [null, null]);
  let img = mutable_source();
  let el_width = mutable_source();
  let el_height = mutable_source();
  async function handle_upload({ detail }, n) {
    const new_value = [value()[0], value()[1]];
    if (detail.length > 1) {
      new_value[n] = detail[0];
    } else {
      new_value[n] = detail[n];
    }
    value(new_value);
    await tick();
    dispatch2("upload", new_value);
  }
  let old_value = mutable_source("");
  const dispatch2 = createEventDispatcher();
  let dragging = prop($$props, "dragging", 12, false);
  legacy_pre_effect(() => (deep_read_state(value()), get(old_value)), () => {
    if (JSON.stringify(value()) !== get(old_value)) {
      set(old_value, JSON.stringify(value()));
      set(value_, value());
    }
  });
  legacy_pre_effect(() => deep_read_state(dragging()), () => {
    dispatch2("drag", dragging());
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root_1();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => (deep_read_state(label()), deep_read_state(i18n()), untrack(() => label() || i18n()("image.image"))));
    BlockLabel(node, {
      get show_label() {
        return show_label();
      },
      get Icon() {
        return Image;
      },
      get label() {
        return get($0);
      }
    });
  }
  var div = sibling(node, 2);
  var node_1 = child(div);
  {
    var consequent = ($$anchor2) => {
      ClearImage($$anchor2, {
        $$events: {
          remove_image: () => {
            position(0.5);
            value([null, null]);
            dispatch2("clear");
          }
        }
      });
    };
    if_block(node_1, ($$render) => {
      if (deep_read_state(value()), untrack(() => value()?.[0]?.url || value()?.[1]?.url)) $$render(consequent);
    });
  }
  var node_2 = sibling(node_1, 2);
  {
    var consequent_2 = ($$anchor2) => {
      var div_1 = root_3();
      var node_3 = child(div_1);
      {
        var consequent_1 = ($$anchor3) => {
          {
            let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value()[1].orig_name || "image")));
            DownloadLink($$anchor3, {
              get href() {
                return deep_read_state(value()), untrack(() => value()[1].url);
              },
              get download() {
                return get($0);
              },
              children: ($$anchor4, $$slotProps) => {
                IconButton($$anchor4, {
                  get Icon() {
                    return Download;
                  }
                });
              },
              $$slots: { default: true }
            });
          }
        };
        if_block(node_3, ($$render) => {
          if (show_download_button()) $$render(consequent_1);
        });
      }
      reset(div_1);
      append($$anchor2, div_1);
    };
    if_block(node_2, ($$render) => {
      if (deep_read_state(value()), untrack(() => value()?.[1]?.url)) $$render(consequent_2);
    });
  }
  var node_4 = sibling(node_2, 2);
  {
    let $0 = derived_safe_equal(() => (deep_read_state(upload_count()), deep_read_state(value()), untrack(() => upload_count() == 2 || !value()?.[0])));
    Slider(node_4, {
      get disabled() {
        return get($0);
      },
      get slider_color() {
        return slider_color();
      },
      get position() {
        return position();
      },
      set position($$value) {
        position($$value);
      },
      children: ($$anchor2, $$slotProps) => {
        var div_2 = root_6();
        let classes;
        let styles;
        var node_5 = child(div_2);
        {
          var consequent_3 = ($$anchor3) => {
            var div_3 = root_7();
            let classes_1;
            var node_6 = child(div_3);
            {
              let $02 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => !!value()?.[0])));
              Upload(node_6, {
                filetype: "image/*",
                get disable_click() {
                  return get($02);
                },
                get root() {
                  return root2();
                },
                file_count: "multiple",
                get upload() {
                  return upload();
                },
                get stream_handler() {
                  return stream_handler();
                },
                get max_file_size() {
                  return max_file_size();
                },
                get upload_promise() {
                  return upload_promise();
                },
                set upload_promise($$value) {
                  upload_promise($$value);
                },
                get dragging() {
                  return dragging();
                },
                set dragging($$value) {
                  dragging($$value);
                },
                $$events: { load: (e) => handle_upload(e, 0) },
                children: ($$anchor4, $$slotProps2) => {
                  var fragment_4 = comment();
                  var node_7 = first_child(fragment_4);
                  slot(node_7, $$props, "default", {}, null);
                  append($$anchor4, fragment_4);
                },
                $$slots: { default: true },
                $$legacy: true
              });
            }
            reset(div_3);
            template_effect(() => classes_1 = set_class(div_3, 1, "wrap svelte-1c8zs50", null, classes_1, { "half-wrap": upload_count() === 1 }));
            append($$anchor3, div_3);
          };
          var alternate = ($$anchor3) => {
            {
              let $02 = derived_safe_equal(() => (get(value_), untrack(() => get(value_)[0]?.url)));
              ImageEl($$anchor3, {
                variant: "upload",
                get src() {
                  return get($02);
                },
                alt: "",
                get max_height() {
                  return max_height();
                },
                get img_el() {
                  return get(img);
                },
                set img_el($$value) {
                  set(img, $$value);
                },
                $$legacy: true
              });
            }
          };
          if_block(node_5, ($$render) => {
            if (get(value_), untrack(() => !get(value_)?.[0])) $$render(consequent_3);
            else $$render(alternate, false);
          });
        }
        var node_8 = sibling(node_5, 2);
        {
          var consequent_4 = ($$anchor3) => {
            {
              let $02 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => !!value()?.[1])));
              Upload($$anchor3, {
                filetype: "image/*",
                get disable_click() {
                  return get($02);
                },
                get root() {
                  return root2();
                },
                file_count: "multiple",
                get upload() {
                  return upload();
                },
                get stream_handler() {
                  return stream_handler();
                },
                get max_file_size() {
                  return max_file_size();
                },
                get upload_promise() {
                  return upload_promise();
                },
                set upload_promise($$value) {
                  upload_promise($$value);
                },
                get dragging() {
                  return dragging();
                },
                set dragging($$value) {
                  dragging($$value);
                },
                $$events: { load: (e) => handle_upload(e, 1) },
                children: ($$anchor4, $$slotProps2) => {
                  var fragment_7 = comment();
                  var node_9 = first_child(fragment_7);
                  slot(node_9, $$props, "default", {}, null);
                  append($$anchor4, fragment_7);
                },
                $$slots: { default: true },
                $$legacy: true
              });
            }
          };
          var alternate_2 = ($$anchor3) => {
            var fragment_8 = comment();
            var node_10 = first_child(fragment_8);
            {
              var consequent_5 = ($$anchor4) => {
                var div_4 = root_13();
                let classes_2;
                let styles_1;
                var node_11 = child(div_4);
                Empty(node_11, {
                  unpadded_box: true,
                  size: "large",
                  children: ($$anchor5, $$slotProps2) => {
                    Image($$anchor5);
                  },
                  $$slots: { default: true }
                });
                reset(div_4);
                template_effect(() => {
                  classes_2 = set_class(div_4, 1, "empty-wrap fixed svelte-1c8zs50", null, classes_2, { "white-icon": !value()?.[0]?.url });
                  styles_1 = set_style(div_4, "", styles_1, {
                    width: `${get(el_width) * (1 - position())}px`,
                    transform: `translateX(${get(el_width) * position()}px)`
                  });
                });
                append($$anchor4, div_4);
              };
              var alternate_1 = ($$anchor4) => {
                var fragment_10 = comment();
                var node_12 = first_child(fragment_10);
                {
                  var consequent_6 = ($$anchor5) => {
                    {
                      let $02 = derived_safe_equal(() => upload_count() === 1);
                      ImageEl($$anchor5, {
                        variant: "upload",
                        get src() {
                          return get(value_), untrack(() => get(value_)[1].url);
                        },
                        alt: "",
                        get fixed() {
                          return get($02);
                        },
                        transform: "translate(0px, 0px) scale(1)",
                        get max_height() {
                          return max_height();
                        }
                      });
                    }
                  };
                  if_block(
                    node_12,
                    ($$render) => {
                      if (get(value_), untrack(() => get(value_)?.[1])) $$render(consequent_6);
                    },
                    true
                  );
                }
                append($$anchor4, fragment_10);
              };
              if_block(
                node_10,
                ($$render) => {
                  if (get(value_), deep_read_state(upload_count()), untrack(() => !get(value_)?.[1] && upload_count() === 1)) $$render(consequent_5);
                  else $$render(alternate_1, false);
                },
                true
              );
            }
            append($$anchor3, fragment_8);
          };
          if_block(node_8, ($$render) => {
            if (get(value_), deep_read_state(upload_count()), untrack(() => !get(value_)?.[1] && upload_count() === 2)) $$render(consequent_4);
            else $$render(alternate_2, false);
          });
        }
        reset(div_2);
        template_effect(() => {
          classes = set_class(div_2, 1, "upload-wrap svelte-1c8zs50", null, classes, { "side-by-side": upload_count() === 2 });
          styles = set_style(div_2, "", styles, { display: upload_count() === 2 ? "flex" : "block" });
        });
        append($$anchor2, div_2);
      },
      $$slots: { default: true },
      $$legacy: true
    });
  }
  reset(div);
  bind_element_size(div, "clientWidth", ($$value) => set(el_width, $$value));
  bind_element_size(div, "clientHeight", ($$value) => set(el_height, $$value));
  append($$anchor, fragment);
  pop();
}
function SliderUpload($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 28, () => [null, null]);
  let upload = prop($$props, "upload", 12);
  let stream_handler = prop($$props, "stream_handler", 12);
  let label = prop($$props, "label", 12);
  let show_label = prop($$props, "show_label", 12);
  let i18n = prop($$props, "i18n", 12);
  let root2 = prop($$props, "root", 12);
  let upload_count = prop($$props, "upload_count", 12, 1);
  let dragging = prop($$props, "dragging", 12);
  let max_height = prop($$props, "max_height", 12);
  let max_file_size = prop($$props, "max_file_size", 12, null);
  let upload_promise = prop($$props, "upload_promise", 12, null);
  var $$exports = {
    get value() {
      return value();
    },
    set value($$value) {
      value($$value);
      flushSync();
    },
    get upload() {
      return upload();
    },
    set upload($$value) {
      upload($$value);
      flushSync();
    },
    get stream_handler() {
      return stream_handler();
    },
    set stream_handler($$value) {
      stream_handler($$value);
      flushSync();
    },
    get label() {
      return label();
    },
    set label($$value) {
      label($$value);
      flushSync();
    },
    get show_label() {
      return show_label();
    },
    set show_label($$value) {
      show_label($$value);
      flushSync();
    },
    get i18n() {
      return i18n();
    },
    set i18n($$value) {
      i18n($$value);
      flushSync();
    },
    get root() {
      return root2();
    },
    set root($$value) {
      root2($$value);
      flushSync();
    },
    get upload_count() {
      return upload_count();
    },
    set upload_count($$value) {
      upload_count($$value);
      flushSync();
    },
    get dragging() {
      return dragging();
    },
    set dragging($$value) {
      dragging($$value);
      flushSync();
    },
    get max_height() {
      return max_height();
    },
    set max_height($$value) {
      max_height($$value);
      flushSync();
    },
    get max_file_size() {
      return max_file_size();
    },
    set max_file_size($$value) {
      max_file_size($$value);
      flushSync();
    },
    get upload_promise() {
      return upload_promise();
    },
    set upload_promise($$value) {
      upload_promise($$value);
      flushSync();
    }
  };
  Image_1($$anchor, {
    slider_color: "var(--border-color-primary)",
    position: 0.5,
    get root() {
      return root2();
    },
    get label() {
      return label();
    },
    get show_label() {
      return show_label();
    },
    get upload_count() {
      return upload_count();
    },
    get stream_handler() {
      return stream_handler();
    },
    get upload() {
      return upload();
    },
    get max_file_size() {
      return max_file_size();
    },
    get max_height() {
      return max_height();
    },
    get i18n() {
      return i18n();
    },
    get upload_promise() {
      return upload_promise();
    },
    set upload_promise($$value) {
      upload_promise($$value);
    },
    get value() {
      return value();
    },
    set value($$value) {
      value($$value);
    },
    get dragging() {
      return dragging();
    },
    set dragging($$value) {
      dragging($$value);
    },
    $$events: {
      edit($$arg) {
        bubble_event.call(this, $$props, $$arg);
      },
      clear($$arg) {
        bubble_event.call(this, $$props, $$arg);
      },
      stream($$arg) {
        bubble_event.call(this, $$props, $$arg);
      },
      drag: ({ detail }) => dragging(detail),
      upload($$arg) {
        bubble_event.call(this, $$props, $$arg);
      },
      select($$arg) {
        bubble_event.call(this, $$props, $$arg);
      },
      share($$arg) {
        bubble_event.call(this, $$props, $$arg);
      }
    },
    children: ($$anchor2, $$slotProps) => {
      var fragment_1 = comment();
      var node = first_child(fragment_1);
      slot(node, $$props, "default", {}, null);
      append($$anchor2, fragment_1);
    },
    $$slots: { default: true },
    $$legacy: true
  });
  return pop($$exports);
}
var root_2 = from_html(`<!> <!>`, 1);
var root_4 = from_html(`<!> <!>`, 1);
function Index($$anchor, $$props) {
  push($$props, true);
  let upload_promise = state(void 0);
  class ImageSliderGradio extends Gradio {
    async get_data() {
      if (get(upload_promise)) {
        await get(upload_promise);
        await tick();
      }
      const data = await super.get_data();
      return data;
    }
  }
  const props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new ImageSliderGradio(props);
  let old_value = state(proxy(gradio.props.value));
  let fullscreen = state(false);
  let dragging = state(false);
  let upload_component;
  let normalised_slider_position = user_derived(() => Math.max(0, Math.min(100, gradio.props.slider_position)) / 100);
  user_effect(() => {
    if (get(old_value) != gradio.props.value) {
      set(old_value, gradio.props.value, true);
      gradio.dispatch("change");
      {
        gradio.dispatch("input");
      }
    }
  });
  const handle_drag_event = (event2) => {
    const drag_event = event2;
    drag_event.preventDefault();
    drag_event.stopPropagation();
    if (drag_event.type === "dragenter" || drag_event.type === "dragover") {
      set(dragging, true);
    } else if (drag_event.type === "dragleave") {
      set(dragging, false);
    }
  };
  const handle_drop = (event2) => {
    if (gradio.shared.interactive) {
      const drop_event = event2;
      drop_event.preventDefault();
      drop_event.stopPropagation();
      set(dragging, false);
      if (upload_component) {
        upload_component.loadFilesFromDrop(drop_event);
      }
    }
  };
  var fragment = comment();
  var node = first_child(fragment);
  {
    var consequent = ($$anchor2) => {
      {
        let $0 = user_derived(() => get(dragging) ? "focus" : "base");
        let $1 = user_derived(() => gradio.props.height || void 0);
        Block($$anchor2, {
          get visible() {
            return gradio.shared.visible;
          },
          variant: "solid",
          get border_mode() {
            return get($0);
          },
          padding: false,
          get elem_id() {
            return gradio.shared.elem_id;
          },
          get elem_classes() {
            return gradio.shared.elem_classes;
          },
          get height() {
            return get($1);
          },
          get width() {
            return gradio.props.width;
          },
          allow_overflow: false,
          get container() {
            return gradio.shared.container;
          },
          get scale() {
            return gradio.shared.scale;
          },
          get min_width() {
            return gradio.shared.min_width;
          },
          get fullscreen() {
            return get(fullscreen);
          },
          set fullscreen($$value) {
            set(fullscreen, $$value, true);
          },
          children: ($$anchor3, $$slotProps) => {
            var fragment_2 = root_2();
            var node_1 = first_child(fragment_2);
            Static(node_1, spread_props(
              {
                get autoscroll() {
                  return gradio.shared.autoscroll;
                },
                get i18n() {
                  return gradio.i18n;
                }
              },
              () => gradio.shared.loading_status
            ));
            var node_2 = sibling(node_1, 2);
            {
              let $02 = user_derived(() => gradio.props.buttons.includes("download"));
              let $12 = user_derived(() => gradio.props.buttons.includes("fullscreen"));
              SliderPreview(node_2, {
                get fullscreen() {
                  return get(fullscreen);
                },
                get interactive() {
                  return gradio.shared.interactive;
                },
                get label() {
                  return gradio.shared.label;
                },
                get show_label() {
                  return gradio.shared.show_label;
                },
                get show_download_button() {
                  return get($02);
                },
                get i18n() {
                  return gradio.i18n;
                },
                get show_fullscreen_button() {
                  return get($12);
                },
                get position() {
                  return get(normalised_slider_position);
                },
                get slider_color() {
                  return gradio.props.slider_color;
                },
                get max_height() {
                  return gradio.props.max_height;
                },
                get value() {
                  return gradio.props.value;
                },
                set value($$value) {
                  gradio.props.value = $$value;
                },
                $$events: {
                  select: ({ detail }) => gradio.dispatch("select", detail),
                  share: ({ detail }) => gradio.dispatch("share", detail),
                  error: ({ detail }) => gradio.dispatch("error", detail),
                  clear: () => gradio.dispatch("clear"),
                  fullscreen: ({ detail }) => {
                    set(fullscreen, detail, true);
                  }
                }
              });
            }
            append($$anchor3, fragment_2);
          },
          $$slots: { default: true }
        });
      }
    };
    var alternate_2 = ($$anchor2) => {
      {
        let $0 = user_derived(() => gradio.props.value === null ? "dashed" : "solid");
        let $1 = user_derived(() => get(dragging) ? "focus" : "base");
        let $2 = user_derived(() => gradio.props.height || void 0);
        Block($$anchor2, {
          get visible() {
            return gradio.shared.visible;
          },
          get variant() {
            return get($0);
          },
          get border_mode() {
            return get($1);
          },
          padding: false,
          get elem_id() {
            return gradio.shared.elem_id;
          },
          get elem_classes() {
            return gradio.shared.elem_classes;
          },
          get height() {
            return get($2);
          },
          get width() {
            return gradio.props.width;
          },
          allow_overflow: false,
          get container() {
            return gradio.shared.container;
          },
          get scale() {
            return gradio.shared.scale;
          },
          get min_width() {
            return gradio.shared.min_width;
          },
          $$events: {
            dragenter: handle_drag_event,
            dragleave: handle_drag_event,
            dragover: handle_drag_event,
            drop: handle_drop
          },
          children: ($$anchor3, $$slotProps) => {
            var fragment_4 = root_4();
            var node_3 = first_child(fragment_4);
            Static(node_3, spread_props(
              {
                get autoscroll() {
                  return gradio.shared.autoscroll;
                },
                get i18n() {
                  return gradio.i18n;
                }
              },
              () => gradio.shared.loading_status,
              {
                $$events: {
                  clear_status: () => gradio.dispatch("clear_status", gradio.shared.loading_status)
                }
              }
            ));
            var node_4 = sibling(node_3, 2);
            {
              let $02 = user_derived(() => gradio.shared.client?.stream);
              bind_this(
                SliderUpload(node_4, {
                  get root() {
                    return gradio.shared.root;
                  },
                  get label() {
                    return gradio.shared.label;
                  },
                  get show_label() {
                    return gradio.shared.show_label;
                  },
                  get upload_count() {
                    return gradio.props.upload_count;
                  },
                  get max_file_size() {
                    return gradio.shared.max_file_size;
                  },
                  get i18n() {
                    return gradio.i18n;
                  },
                  upload: (...args) => gradio.shared.client.upload(...args),
                  get stream_handler() {
                    return get($02);
                  },
                  get max_height() {
                    return gradio.props.max_height;
                  },
                  get upload_promise() {
                    return get(upload_promise);
                  },
                  set upload_promise($$value) {
                    set(upload_promise, $$value, true);
                  },
                  get value() {
                    return gradio.props.value;
                  },
                  set value($$value) {
                    gradio.props.value = $$value;
                  },
                  get dragging() {
                    return get(dragging);
                  },
                  set dragging($$value) {
                    set(dragging, $$value, true);
                  },
                  $$events: {
                    edit: () => gradio.dispatch("edit"),
                    clear: () => {
                      gradio.dispatch("clear");
                    },
                    drag: ({ detail }) => set(dragging, detail, true),
                    upload: () => gradio.dispatch("upload"),
                    error: ({ detail }) => {
                      if (gradio.shared.loading_status) gradio.shared.loading_status.status = "error";
                      gradio.dispatch("error", detail);
                    },
                    close_stream: () => {
                      gradio.dispatch("close_stream", "stream");
                    }
                  },
                  children: ($$anchor4, $$slotProps2) => {
                    var fragment_5 = comment();
                    var node_5 = first_child(fragment_5);
                    {
                      var consequent_1 = ($$anchor5) => {
                        UploadText($$anchor5, {
                          get i18n() {
                            return gradio.i18n;
                          },
                          type: "image",
                          get placeholder() {
                            return gradio.props.placeholder;
                          }
                        });
                      };
                      if_block(node_5, ($$render) => {
                        $$render(consequent_1);
                      });
                    }
                    append($$anchor4, fragment_5);
                  },
                  $$slots: { default: true }
                }),
                ($$value) => upload_component = $$value,
                () => upload_component
              );
            }
            append($$anchor3, fragment_4);
          },
          $$slots: { default: true }
        });
      }
    };
    if_block(node, ($$render) => {
      if (!gradio.shared.interactive || gradio.props.value?.[1] && gradio.props.value?.[0]) $$render(consequent);
      else $$render(alternate_2, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=CHr64p-7.js.map
