import { I as InternSet } from "./CzSFdLC4.js";
import { f as ascending, n as numbers, m as number, j as interpolate$1, o as array$1, q as date, r as numberArray, s as object$1, i as interpolateRound, u as number$1, v as linearish, w as transformer$3, a as copy$1, x as ticks, y as identity$3, h as bisectRight } from "./Ch2P6CyP.js";
import { R as Rgb, x as rgbConvert, y as define, z as extend, Y as darker, Z as brighter, C as Color, B as hue$1, X as hsl$1, A as nogamma, _ as basis, $ as basisClosed, q as interpolateNumber, r as interpolateRgb, a0 as rgbBasis, a1 as rgbBasisClosed, u as interpolateString, a2 as interpolateTransformCss, a3 as interpolateTransformSvg, a4 as Timer, a5 as now, a6 as timer, w as withPath, a as constant$2, K as curveLinear, a7 as x$2, a8 as y$2, n as array$2, l as line, b as sqrt$3, t as tau$2, p as pi$2 } from "./B_xrbhEe.js";
import { m as min, a as max, F as degrees$1, G as radians$1, E as lab$1, i as interpolateHcl, H as hclLong, I as nice, J as calendar, A as utcFormat, s as second, u as utcMinute, r as utcHour, v as utcDay, w as utcSunday, x as utcMonth, y as utcYear, K as utcTickInterval, L as utcTicks } from "./DsLWYO-v.js";
import { d as dispatch } from "./Qrw4qHro.js";
import { r as range$1 } from "./Bs5oKbOs.js";
import { o as optional, d as constantZero, e as constant$1, r as roundNode, c as treemapDice, N as Node$1, f as computeHeight, b as treemapSlice, s as squarifyRatio, p as phi } from "./CykJO7CO.js";
import { i as initRange, a as initInterpolator } from "./CTO7spbL.js";
import { a as formatSpecifier, f as format } from "./QrCxtVsa.js";
import { c as colors } from "./DAbZ0KZY.js";
function variance(values, valueof) {
  let count = 0;
  let delta;
  let mean2 = 0;
  let sum2 = 0;
  if (valueof === void 0) {
    for (let value of values) {
      if (value != null && (value = +value) >= value) {
        delta = value - mean2;
        mean2 += delta / ++count;
        sum2 += delta * (value - mean2);
      }
    }
  } else {
    let index2 = -1;
    for (let value of values) {
      if ((value = valueof(value, ++index2, values)) != null && (value = +value) >= value) {
        delta = value - mean2;
        mean2 += delta / ++count;
        sum2 += delta * (value - mean2);
      }
    }
  }
  if (count > 1) return sum2 / (count - 1);
}
function deviation(values, valueof) {
  const v = variance(values, valueof);
  return v ? Math.sqrt(v) : v;
}
class Adder {
  constructor() {
    this._partials = new Float64Array(32);
    this._n = 0;
  }
  add(x2) {
    const p = this._partials;
    let i = 0;
    for (let j = 0; j < this._n && j < 32; j++) {
      const y2 = p[j], hi = x2 + y2, lo = Math.abs(x2) < Math.abs(y2) ? x2 - (hi - y2) : y2 - (hi - x2);
      if (lo) p[i++] = lo;
      x2 = hi;
    }
    p[i] = x2;
    this._n = i + 1;
    return this;
  }
  valueOf() {
    const p = this._partials;
    let n = this._n, x2, y2, lo, hi = 0;
    if (n > 0) {
      hi = p[--n];
      while (n > 0) {
        x2 = hi;
        y2 = p[--n];
        hi = x2 + y2;
        lo = y2 - (hi - x2);
        if (lo) break;
      }
      if (n > 0 && (lo < 0 && p[n - 1] < 0 || lo > 0 && p[n - 1] > 0)) {
        y2 = lo * 2;
        x2 = hi + y2;
        if (y2 == x2 - hi) hi = x2;
      }
    }
    return hi;
  }
}
function permute(source, keys) {
  return Array.from(keys, (key) => source[key]);
}
function compareDefined(compare = ascending) {
  if (compare === ascending) return ascendingDefined;
  if (typeof compare !== "function") throw new TypeError("compare is not a function");
  return (a2, b) => {
    const x2 = compare(a2, b);
    if (x2 || x2 === 0) return x2;
    return (compare(b, b) === 0) - (compare(a2, a2) === 0);
  };
}
function ascendingDefined(a2, b) {
  return (a2 == null || !(a2 >= a2)) - (b == null || !(b >= b)) || (a2 < b ? -1 : a2 > b ? 1 : 0);
}
function quickselect(array2, k, left = 0, right = Infinity, compare) {
  k = Math.floor(k);
  left = Math.floor(Math.max(0, left));
  right = Math.floor(Math.min(array2.length - 1, right));
  if (!(left <= k && k <= right)) return array2;
  compare = compare === void 0 ? ascendingDefined : compareDefined(compare);
  while (right > left) {
    if (right - left > 600) {
      const n = right - left + 1;
      const m2 = k - left + 1;
      const z = Math.log(n);
      const s = 0.5 * Math.exp(2 * z / 3);
      const sd = 0.5 * Math.sqrt(z * s * (n - s) / n) * (m2 - n / 2 < 0 ? -1 : 1);
      const newLeft = Math.max(left, Math.floor(k - m2 * s / n + sd));
      const newRight = Math.min(right, Math.floor(k + (n - m2) * s / n + sd));
      quickselect(array2, k, newLeft, newRight, compare);
    }
    const t = array2[k];
    let i = left;
    let j = right;
    swap$1(array2, left, k);
    if (compare(array2[right], t) > 0) swap$1(array2, left, right);
    while (i < j) {
      swap$1(array2, i, j), ++i, --j;
      while (compare(array2[i], t) < 0) ++i;
      while (compare(array2[j], t) > 0) --j;
    }
    if (compare(array2[left], t) === 0) swap$1(array2, left, j);
    else ++j, swap$1(array2, j, right);
    if (j <= k) left = j + 1;
    if (k <= j) right = j - 1;
  }
  return array2;
}
function swap$1(array2, i, j) {
  const t = array2[i];
  array2[i] = array2[j];
  array2[j] = t;
}
function quantile$1(values, p, valueof) {
  values = Float64Array.from(numbers(values, valueof));
  if (!(n = values.length) || isNaN(p = +p)) return;
  if (p <= 0 || n < 2) return min(values);
  if (p >= 1) return max(values);
  var n, i = (n - 1) * p, i0 = Math.floor(i), value0 = max(quickselect(values, i0).subarray(0, i0 + 1)), value1 = min(values.subarray(i0 + 1));
  return value0 + (value1 - value0) * (i - i0);
}
function quantileSorted(values, p, valueof = number) {
  if (!(n = values.length) || isNaN(p = +p)) return;
  if (p <= 0 || n < 2) return +valueof(values[0], 0, values);
  if (p >= 1) return +valueof(values[n - 1], n - 1, values);
  var n, i = (n - 1) * p, i0 = Math.floor(i), value0 = +valueof(values[i0], i0, values), value1 = +valueof(values[i0 + 1], i0 + 1, values);
  return value0 + (value1 - value0) * (i - i0);
}
function mean(values, valueof) {
  let count = 0;
  let sum2 = 0;
  if (valueof === void 0) {
    for (let value of values) {
      if (value != null && (value = +value) >= value) {
        ++count, sum2 += value;
      }
    }
  } else {
    let index2 = -1;
    for (let value of values) {
      if ((value = valueof(value, ++index2, values)) != null && (value = +value) >= value) {
        ++count, sum2 += value;
      }
    }
  }
  if (count) return sum2 / count;
}
function median(values, valueof) {
  return quantile$1(values, 0.5, valueof);
}
function* flatten(arrays) {
  for (const array2 of arrays) {
    yield* array2;
  }
}
function merge(arrays) {
  return Array.from(flatten(arrays));
}
function sum$1(values, valueof) {
  let sum2 = 0;
  {
    for (let value of values) {
      if (value = +value) {
        sum2 += value;
      }
    }
  }
  return sum2;
}
function intersection(values, ...others) {
  values = new InternSet(values);
  others = others.map(set);
  out: for (const value of values) {
    for (const other of others) {
      if (!other.has(value)) {
        values.delete(value);
        continue out;
      }
    }
  }
  return values;
}
function set(values) {
  return values instanceof InternSet ? values : new InternSet(values);
}
function union(...others) {
  const set2 = new InternSet();
  for (const other of others) {
    for (const o of other) {
      set2.add(o);
    }
  }
  return set2;
}
var A = -0.14861, B$1 = 1.78277, C = -0.29227, D$1 = -0.90649, E = 1.97294, ED = E * D$1, EB = E * B$1, BC_DA = B$1 * C - D$1 * A;
function cubehelixConvert(o) {
  if (o instanceof Cubehelix) return new Cubehelix(o.h, o.s, o.l, o.opacity);
  if (!(o instanceof Rgb)) o = rgbConvert(o);
  var r = o.r / 255, g = o.g / 255, b = o.b / 255, l = (BC_DA * b + ED * r - EB * g) / (BC_DA + ED - EB), bl = b - l, k = (E * (g - l) - C * bl) / D$1, s = Math.sqrt(k * k + bl * bl) / (E * l * (1 - l)), h = s ? Math.atan2(k, bl) * degrees$1 - 120 : NaN;
  return new Cubehelix(h < 0 ? h + 360 : h, s, l, o.opacity);
}
function cubehelix$1(h, s, l, opacity) {
  return arguments.length === 1 ? cubehelixConvert(h) : new Cubehelix(h, s, l, opacity == null ? 1 : opacity);
}
function Cubehelix(h, s, l, opacity) {
  this.h = +h;
  this.s = +s;
  this.l = +l;
  this.opacity = +opacity;
}
define(Cubehelix, cubehelix$1, extend(Color, {
  brighter(k) {
    k = k == null ? brighter : Math.pow(brighter, k);
    return new Cubehelix(this.h, this.s, this.l * k, this.opacity);
  },
  darker(k) {
    k = k == null ? darker : Math.pow(darker, k);
    return new Cubehelix(this.h, this.s, this.l * k, this.opacity);
  },
  rgb() {
    var h = isNaN(this.h) ? 0 : (this.h + 120) * radians$1, l = +this.l, a2 = isNaN(this.s) ? 0 : this.s * l * (1 - l), cosh2 = Math.cos(h), sinh2 = Math.sin(h);
    return new Rgb(
      255 * (l + a2 * (A * cosh2 + B$1 * sinh2)),
      255 * (l + a2 * (C * cosh2 + D$1 * sinh2)),
      255 * (l + a2 * (E * cosh2)),
      this.opacity
    );
  }
}));
function discrete(range2) {
  var n = range2.length;
  return function(t) {
    return range2[Math.max(0, Math.min(n - 1, Math.floor(t * n)))];
  };
}
function hue(a2, b) {
  var i = hue$1(+a2, +b);
  return function(t) {
    var x2 = i(t);
    return x2 - 360 * Math.floor(x2 / 360);
  };
}
var epsilon2$1 = 1e-12;
function cosh(x2) {
  return ((x2 = Math.exp(x2)) + 1 / x2) / 2;
}
function sinh(x2) {
  return ((x2 = Math.exp(x2)) - 1 / x2) / 2;
}
function tanh(x2) {
  return ((x2 = Math.exp(2 * x2)) - 1) / (x2 + 1);
}
const interpolateZoom = (function zoomRho(rho, rho2, rho4) {
  function zoom(p02, p1) {
    var ux0 = p02[0], uy0 = p02[1], w0 = p02[2], ux1 = p1[0], uy1 = p1[1], w1 = p1[2], dx = ux1 - ux0, dy = uy1 - uy0, d2 = dx * dx + dy * dy, i, S;
    if (d2 < epsilon2$1) {
      S = Math.log(w1 / w0) / rho;
      i = function(t) {
        return [
          ux0 + t * dx,
          uy0 + t * dy,
          w0 * Math.exp(rho * t * S)
        ];
      };
    } else {
      var d1 = Math.sqrt(d2), b0 = (w1 * w1 - w0 * w0 + rho4 * d2) / (2 * w0 * rho2 * d1), b1 = (w1 * w1 - w0 * w0 - rho4 * d2) / (2 * w1 * rho2 * d1), r0 = Math.log(Math.sqrt(b0 * b0 + 1) - b0), r1 = Math.log(Math.sqrt(b1 * b1 + 1) - b1);
      S = (r1 - r0) / rho;
      i = function(t) {
        var s = t * S, coshr0 = cosh(r0), u2 = w0 / (rho2 * d1) * (coshr0 * tanh(rho * s + r0) - sinh(r0));
        return [
          ux0 + u2 * dx,
          uy0 + u2 * dy,
          w0 * coshr0 / cosh(rho * s + r0)
        ];
      };
    }
    i.duration = S * 1e3 * rho / Math.SQRT2;
    return i;
  }
  zoom.rho = function(_) {
    var _1 = Math.max(1e-3, +_), _2 = _1 * _1, _4 = _2 * _2;
    return zoomRho(_1, _2, _4);
  };
  return zoom;
})(Math.SQRT2, 2, 4);
function hsl(hue2) {
  return function(start, end) {
    var h = hue2((start = hsl$1(start)).h, (end = hsl$1(end)).h), s = nogamma(start.s, end.s), l = nogamma(start.l, end.l), opacity = nogamma(start.opacity, end.opacity);
    return function(t) {
      start.h = h(t);
      start.s = s(t);
      start.l = l(t);
      start.opacity = opacity(t);
      return start + "";
    };
  };
}
const hsl_default = hsl(hue$1);
var hslLong = hsl(nogamma);
function lab(start, end) {
  var l = nogamma((start = lab$1(start)).l, (end = lab$1(end)).l), a2 = nogamma(start.a, end.a), b = nogamma(start.b, end.b), opacity = nogamma(start.opacity, end.opacity);
  return function(t) {
    start.l = l(t);
    start.a = a2(t);
    start.b = b(t);
    start.opacity = opacity(t);
    return start + "";
  };
}
function cubehelix(hue2) {
  return (function cubehelixGamma(y2) {
    y2 = +y2;
    function cubehelix2(start, end) {
      var h = hue2((start = cubehelix$1(start)).h, (end = cubehelix$1(end)).h), s = nogamma(start.s, end.s), l = nogamma(start.l, end.l), opacity = nogamma(start.opacity, end.opacity);
      return function(t) {
        start.h = h(t);
        start.s = s(t);
        start.l = l(Math.pow(t, y2));
        start.opacity = opacity(t);
        return start + "";
      };
    }
    cubehelix2.gamma = cubehelixGamma;
    return cubehelix2;
  })(1);
}
const cubehelix_default = cubehelix(hue$1);
var cubehelixLong = cubehelix(nogamma);
function piecewise(interpolate, values) {
  if (values === void 0) values = interpolate, interpolate = interpolate$1;
  var i = 0, n = values.length - 1, v = values[0], I = new Array(n < 0 ? 0 : n);
  while (i < n) I[i] = interpolate(v, v = values[++i]);
  return function(t) {
    var i2 = Math.max(0, Math.min(n - 1, Math.floor(t *= n)));
    return I[i2](t - i2);
  };
}
function quantize$1(interpolator, n) {
  var samples = new Array(n);
  for (var i = 0; i < n; ++i) samples[i] = interpolator(i / (n - 1));
  return samples;
}
const $$1 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  interpolate: interpolate$1,
  interpolateArray: array$1,
  interpolateBasis: basis,
  interpolateBasisClosed: basisClosed,
  interpolateCubehelix: cubehelix_default,
  interpolateCubehelixLong: cubehelixLong,
  interpolateDate: date,
  interpolateDiscrete: discrete,
  interpolateHcl,
  interpolateHclLong: hclLong,
  interpolateHsl: hsl_default,
  interpolateHslLong: hslLong,
  interpolateHue: hue,
  interpolateLab: lab,
  interpolateNumber,
  interpolateNumberArray: numberArray,
  interpolateObject: object$1,
  interpolateRgb,
  interpolateRgbBasis: rgbBasis,
  interpolateRgbBasisClosed: rgbBasisClosed,
  interpolateRound,
  interpolateString,
  interpolateTransformCss,
  interpolateTransformSvg,
  interpolateZoom,
  piecewise,
  quantize: quantize$1
}, Symbol.toStringTag, { value: "Module" }));
function interval(callback, delay, time) {
  var t = new Timer(), total = delay;
  if (delay == null) return t.restart(callback, delay, time), t;
  t._restart = t.restart;
  t.restart = function(callback2, delay2, time2) {
    delay2 = +delay2, time2 = time2 == null ? now() : +time2;
    t._restart(function tick(elapsed) {
      elapsed += total;
      t._restart(tick, total += delay2, time2);
      callback2(elapsed);
    }, delay2, time2);
  };
  t.restart(callback, delay, time);
  return t;
}
const epsilon$3 = 11102230246251565e-32;
const splitter = 134217729;
const resulterrbound = (3 + 8 * epsilon$3) * epsilon$3;
function sum(elen, e, flen, f, h) {
  let Q, Qnew, hh, bvirt;
  let enow = e[0];
  let fnow = f[0];
  let eindex = 0;
  let findex = 0;
  if (fnow > enow === fnow > -enow) {
    Q = enow;
    enow = e[++eindex];
  } else {
    Q = fnow;
    fnow = f[++findex];
  }
  let hindex = 0;
  if (eindex < elen && findex < flen) {
    if (fnow > enow === fnow > -enow) {
      Qnew = enow + Q;
      hh = Q - (Qnew - enow);
      enow = e[++eindex];
    } else {
      Qnew = fnow + Q;
      hh = Q - (Qnew - fnow);
      fnow = f[++findex];
    }
    Q = Qnew;
    if (hh !== 0) {
      h[hindex++] = hh;
    }
    while (eindex < elen && findex < flen) {
      if (fnow > enow === fnow > -enow) {
        Qnew = Q + enow;
        bvirt = Qnew - Q;
        hh = Q - (Qnew - bvirt) + (enow - bvirt);
        enow = e[++eindex];
      } else {
        Qnew = Q + fnow;
        bvirt = Qnew - Q;
        hh = Q - (Qnew - bvirt) + (fnow - bvirt);
        fnow = f[++findex];
      }
      Q = Qnew;
      if (hh !== 0) {
        h[hindex++] = hh;
      }
    }
  }
  while (eindex < elen) {
    Qnew = Q + enow;
    bvirt = Qnew - Q;
    hh = Q - (Qnew - bvirt) + (enow - bvirt);
    enow = e[++eindex];
    Q = Qnew;
    if (hh !== 0) {
      h[hindex++] = hh;
    }
  }
  while (findex < flen) {
    Qnew = Q + fnow;
    bvirt = Qnew - Q;
    hh = Q - (Qnew - bvirt) + (fnow - bvirt);
    fnow = f[++findex];
    Q = Qnew;
    if (hh !== 0) {
      h[hindex++] = hh;
    }
  }
  if (Q !== 0 || hindex === 0) {
    h[hindex++] = Q;
  }
  return hindex;
}
function estimate(elen, e) {
  let Q = e[0];
  for (let i = 1; i < elen; i++) Q += e[i];
  return Q;
}
function vec(n) {
  return new Float64Array(n);
}
const ccwerrboundA = (3 + 16 * epsilon$3) * epsilon$3;
const ccwerrboundB = (2 + 12 * epsilon$3) * epsilon$3;
const ccwerrboundC = (9 + 64 * epsilon$3) * epsilon$3 * epsilon$3;
const B = vec(4);
const C1 = vec(8);
const C2 = vec(12);
const D = vec(16);
const u = vec(4);
function orient2dadapt(ax, ay, bx, by, cx, cy, detsum) {
  let acxtail, acytail, bcxtail, bcytail;
  let bvirt, c2, ahi, alo, bhi, blo, _i, _j, _0, s1, s0, t1, t0, u3;
  const acx = ax - cx;
  const bcx = bx - cx;
  const acy = ay - cy;
  const bcy = by - cy;
  s1 = acx * bcy;
  c2 = splitter * acx;
  ahi = c2 - (c2 - acx);
  alo = acx - ahi;
  c2 = splitter * bcy;
  bhi = c2 - (c2 - bcy);
  blo = bcy - bhi;
  s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo);
  t1 = acy * bcx;
  c2 = splitter * acy;
  ahi = c2 - (c2 - acy);
  alo = acy - ahi;
  c2 = splitter * bcx;
  bhi = c2 - (c2 - bcx);
  blo = bcx - bhi;
  t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo);
  _i = s0 - t0;
  bvirt = s0 - _i;
  B[0] = s0 - (_i + bvirt) + (bvirt - t0);
  _j = s1 + _i;
  bvirt = _j - s1;
  _0 = s1 - (_j - bvirt) + (_i - bvirt);
  _i = _0 - t1;
  bvirt = _0 - _i;
  B[1] = _0 - (_i + bvirt) + (bvirt - t1);
  u3 = _j + _i;
  bvirt = u3 - _j;
  B[2] = _j - (u3 - bvirt) + (_i - bvirt);
  B[3] = u3;
  let det = estimate(4, B);
  let errbound = ccwerrboundB * detsum;
  if (det >= errbound || -det >= errbound) {
    return det;
  }
  bvirt = ax - acx;
  acxtail = ax - (acx + bvirt) + (bvirt - cx);
  bvirt = bx - bcx;
  bcxtail = bx - (bcx + bvirt) + (bvirt - cx);
  bvirt = ay - acy;
  acytail = ay - (acy + bvirt) + (bvirt - cy);
  bvirt = by - bcy;
  bcytail = by - (bcy + bvirt) + (bvirt - cy);
  if (acxtail === 0 && acytail === 0 && bcxtail === 0 && bcytail === 0) {
    return det;
  }
  errbound = ccwerrboundC * detsum + resulterrbound * Math.abs(det);
  det += acx * bcytail + bcy * acxtail - (acy * bcxtail + bcx * acytail);
  if (det >= errbound || -det >= errbound) return det;
  s1 = acxtail * bcy;
  c2 = splitter * acxtail;
  ahi = c2 - (c2 - acxtail);
  alo = acxtail - ahi;
  c2 = splitter * bcy;
  bhi = c2 - (c2 - bcy);
  blo = bcy - bhi;
  s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo);
  t1 = acytail * bcx;
  c2 = splitter * acytail;
  ahi = c2 - (c2 - acytail);
  alo = acytail - ahi;
  c2 = splitter * bcx;
  bhi = c2 - (c2 - bcx);
  blo = bcx - bhi;
  t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo);
  _i = s0 - t0;
  bvirt = s0 - _i;
  u[0] = s0 - (_i + bvirt) + (bvirt - t0);
  _j = s1 + _i;
  bvirt = _j - s1;
  _0 = s1 - (_j - bvirt) + (_i - bvirt);
  _i = _0 - t1;
  bvirt = _0 - _i;
  u[1] = _0 - (_i + bvirt) + (bvirt - t1);
  u3 = _j + _i;
  bvirt = u3 - _j;
  u[2] = _j - (u3 - bvirt) + (_i - bvirt);
  u[3] = u3;
  const C1len = sum(4, B, 4, u, C1);
  s1 = acx * bcytail;
  c2 = splitter * acx;
  ahi = c2 - (c2 - acx);
  alo = acx - ahi;
  c2 = splitter * bcytail;
  bhi = c2 - (c2 - bcytail);
  blo = bcytail - bhi;
  s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo);
  t1 = acy * bcxtail;
  c2 = splitter * acy;
  ahi = c2 - (c2 - acy);
  alo = acy - ahi;
  c2 = splitter * bcxtail;
  bhi = c2 - (c2 - bcxtail);
  blo = bcxtail - bhi;
  t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo);
  _i = s0 - t0;
  bvirt = s0 - _i;
  u[0] = s0 - (_i + bvirt) + (bvirt - t0);
  _j = s1 + _i;
  bvirt = _j - s1;
  _0 = s1 - (_j - bvirt) + (_i - bvirt);
  _i = _0 - t1;
  bvirt = _0 - _i;
  u[1] = _0 - (_i + bvirt) + (bvirt - t1);
  u3 = _j + _i;
  bvirt = u3 - _j;
  u[2] = _j - (u3 - bvirt) + (_i - bvirt);
  u[3] = u3;
  const C2len = sum(C1len, C1, 4, u, C2);
  s1 = acxtail * bcytail;
  c2 = splitter * acxtail;
  ahi = c2 - (c2 - acxtail);
  alo = acxtail - ahi;
  c2 = splitter * bcytail;
  bhi = c2 - (c2 - bcytail);
  blo = bcytail - bhi;
  s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo);
  t1 = acytail * bcxtail;
  c2 = splitter * acytail;
  ahi = c2 - (c2 - acytail);
  alo = acytail - ahi;
  c2 = splitter * bcxtail;
  bhi = c2 - (c2 - bcxtail);
  blo = bcxtail - bhi;
  t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo);
  _i = s0 - t0;
  bvirt = s0 - _i;
  u[0] = s0 - (_i + bvirt) + (bvirt - t0);
  _j = s1 + _i;
  bvirt = _j - s1;
  _0 = s1 - (_j - bvirt) + (_i - bvirt);
  _i = _0 - t1;
  bvirt = _0 - _i;
  u[1] = _0 - (_i + bvirt) + (bvirt - t1);
  u3 = _j + _i;
  bvirt = u3 - _j;
  u[2] = _j - (u3 - bvirt) + (_i - bvirt);
  u[3] = u3;
  const Dlen = sum(C2len, C2, 4, u, D);
  return D[Dlen - 1];
}
function orient2d(ax, ay, bx, by, cx, cy) {
  const detleft = (ay - cy) * (bx - cx);
  const detright = (ax - cx) * (by - cy);
  const det = detleft - detright;
  const detsum = Math.abs(detleft + detright);
  if (Math.abs(det) >= ccwerrboundA * detsum) return det;
  return -orient2dadapt(ax, ay, bx, by, cx, cy, detsum);
}
const EPSILON = Math.pow(2, -52);
const EDGE_STACK = new Uint32Array(512);
class Delaunator {
  static from(points, getX = defaultGetX, getY = defaultGetY) {
    const n = points.length;
    const coords = new Float64Array(n * 2);
    for (let i = 0; i < n; i++) {
      const p = points[i];
      coords[2 * i] = getX(p);
      coords[2 * i + 1] = getY(p);
    }
    return new Delaunator(coords);
  }
  constructor(coords) {
    const n = coords.length >> 1;
    if (n > 0 && typeof coords[0] !== "number") throw new Error("Expected coords to contain numbers.");
    this.coords = coords;
    const maxTriangles = Math.max(2 * n - 5, 0);
    this._triangles = new Uint32Array(maxTriangles * 3);
    this._halfedges = new Int32Array(maxTriangles * 3);
    this._hashSize = Math.ceil(Math.sqrt(n));
    this._hullPrev = new Uint32Array(n);
    this._hullNext = new Uint32Array(n);
    this._hullTri = new Uint32Array(n);
    this._hullHash = new Int32Array(this._hashSize);
    this._ids = new Uint32Array(n);
    this._dists = new Float64Array(n);
    this.update();
  }
  update() {
    const { coords, _hullPrev: hullPrev, _hullNext: hullNext, _hullTri: hullTri, _hullHash: hullHash } = this;
    const n = coords.length >> 1;
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY2 = -Infinity;
    for (let i = 0; i < n; i++) {
      const x2 = coords[2 * i];
      const y2 = coords[2 * i + 1];
      if (x2 < minX) minX = x2;
      if (y2 < minY) minY = y2;
      if (x2 > maxX) maxX = x2;
      if (y2 > maxY2) maxY2 = y2;
      this._ids[i] = i;
    }
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY2) / 2;
    let i0, i1, i2;
    for (let i = 0, minDist = Infinity; i < n; i++) {
      const d = dist(cx, cy, coords[2 * i], coords[2 * i + 1]);
      if (d < minDist) {
        i0 = i;
        minDist = d;
      }
    }
    const i0x = coords[2 * i0];
    const i0y = coords[2 * i0 + 1];
    for (let i = 0, minDist = Infinity; i < n; i++) {
      if (i === i0) continue;
      const d = dist(i0x, i0y, coords[2 * i], coords[2 * i + 1]);
      if (d < minDist && d > 0) {
        i1 = i;
        minDist = d;
      }
    }
    let i1x = coords[2 * i1];
    let i1y = coords[2 * i1 + 1];
    let minRadius = Infinity;
    for (let i = 0; i < n; i++) {
      if (i === i0 || i === i1) continue;
      const r = circumradius(i0x, i0y, i1x, i1y, coords[2 * i], coords[2 * i + 1]);
      if (r < minRadius) {
        i2 = i;
        minRadius = r;
      }
    }
    let i2x = coords[2 * i2];
    let i2y = coords[2 * i2 + 1];
    if (minRadius === Infinity) {
      for (let i = 0; i < n; i++) {
        this._dists[i] = coords[2 * i] - coords[0] || coords[2 * i + 1] - coords[1];
      }
      quicksort(this._ids, this._dists, 0, n - 1);
      const hull = new Uint32Array(n);
      let j = 0;
      for (let i = 0, d0 = -Infinity; i < n; i++) {
        const id = this._ids[i];
        const d = this._dists[id];
        if (d > d0) {
          hull[j++] = id;
          d0 = d;
        }
      }
      this.hull = hull.subarray(0, j);
      this.triangles = new Uint32Array(0);
      this.halfedges = new Uint32Array(0);
      return;
    }
    if (orient2d(i0x, i0y, i1x, i1y, i2x, i2y) < 0) {
      const i = i1;
      const x2 = i1x;
      const y2 = i1y;
      i1 = i2;
      i1x = i2x;
      i1y = i2y;
      i2 = i;
      i2x = x2;
      i2y = y2;
    }
    const center = circumcenter(i0x, i0y, i1x, i1y, i2x, i2y);
    this._cx = center.x;
    this._cy = center.y;
    for (let i = 0; i < n; i++) {
      this._dists[i] = dist(coords[2 * i], coords[2 * i + 1], center.x, center.y);
    }
    quicksort(this._ids, this._dists, 0, n - 1);
    this._hullStart = i0;
    let hullSize = 3;
    hullNext[i0] = hullPrev[i2] = i1;
    hullNext[i1] = hullPrev[i0] = i2;
    hullNext[i2] = hullPrev[i1] = i0;
    hullTri[i0] = 0;
    hullTri[i1] = 1;
    hullTri[i2] = 2;
    hullHash.fill(-1);
    hullHash[this._hashKey(i0x, i0y)] = i0;
    hullHash[this._hashKey(i1x, i1y)] = i1;
    hullHash[this._hashKey(i2x, i2y)] = i2;
    this.trianglesLen = 0;
    this._addTriangle(i0, i1, i2, -1, -1, -1);
    for (let k = 0, xp, yp; k < this._ids.length; k++) {
      const i = this._ids[k];
      const x2 = coords[2 * i];
      const y2 = coords[2 * i + 1];
      if (k > 0 && Math.abs(x2 - xp) <= EPSILON && Math.abs(y2 - yp) <= EPSILON) continue;
      xp = x2;
      yp = y2;
      if (i === i0 || i === i1 || i === i2) continue;
      let start = 0;
      for (let j = 0, key = this._hashKey(x2, y2); j < this._hashSize; j++) {
        start = hullHash[(key + j) % this._hashSize];
        if (start !== -1 && start !== hullNext[start]) break;
      }
      start = hullPrev[start];
      let e = start, q;
      while (q = hullNext[e], orient2d(x2, y2, coords[2 * e], coords[2 * e + 1], coords[2 * q], coords[2 * q + 1]) >= 0) {
        e = q;
        if (e === start) {
          e = -1;
          break;
        }
      }
      if (e === -1) continue;
      let t = this._addTriangle(e, i, hullNext[e], -1, -1, hullTri[e]);
      hullTri[i] = this._legalize(t + 2);
      hullTri[e] = t;
      hullSize++;
      let n2 = hullNext[e];
      while (q = hullNext[n2], orient2d(x2, y2, coords[2 * n2], coords[2 * n2 + 1], coords[2 * q], coords[2 * q + 1]) < 0) {
        t = this._addTriangle(n2, i, q, hullTri[i], -1, hullTri[n2]);
        hullTri[i] = this._legalize(t + 2);
        hullNext[n2] = n2;
        hullSize--;
        n2 = q;
      }
      if (e === start) {
        while (q = hullPrev[e], orient2d(x2, y2, coords[2 * q], coords[2 * q + 1], coords[2 * e], coords[2 * e + 1]) < 0) {
          t = this._addTriangle(q, i, e, -1, hullTri[e], hullTri[q]);
          this._legalize(t + 2);
          hullTri[q] = t;
          hullNext[e] = e;
          hullSize--;
          e = q;
        }
      }
      this._hullStart = hullPrev[i] = e;
      hullNext[e] = hullPrev[n2] = i;
      hullNext[i] = n2;
      hullHash[this._hashKey(x2, y2)] = i;
      hullHash[this._hashKey(coords[2 * e], coords[2 * e + 1])] = e;
    }
    this.hull = new Uint32Array(hullSize);
    for (let i = 0, e = this._hullStart; i < hullSize; i++) {
      this.hull[i] = e;
      e = hullNext[e];
    }
    this.triangles = this._triangles.subarray(0, this.trianglesLen);
    this.halfedges = this._halfedges.subarray(0, this.trianglesLen);
  }
  _hashKey(x2, y2) {
    return Math.floor(pseudoAngle(x2 - this._cx, y2 - this._cy) * this._hashSize) % this._hashSize;
  }
  _legalize(a2) {
    const { _triangles: triangles, _halfedges: halfedges, coords } = this;
    let i = 0;
    let ar = 0;
    while (true) {
      const b = halfedges[a2];
      const a0 = a2 - a2 % 3;
      ar = a0 + (a2 + 2) % 3;
      if (b === -1) {
        if (i === 0) break;
        a2 = EDGE_STACK[--i];
        continue;
      }
      const b0 = b - b % 3;
      const al = a0 + (a2 + 1) % 3;
      const bl = b0 + (b + 2) % 3;
      const p02 = triangles[ar];
      const pr = triangles[a2];
      const pl = triangles[al];
      const p1 = triangles[bl];
      const illegal = inCircle(
        coords[2 * p02],
        coords[2 * p02 + 1],
        coords[2 * pr],
        coords[2 * pr + 1],
        coords[2 * pl],
        coords[2 * pl + 1],
        coords[2 * p1],
        coords[2 * p1 + 1]
      );
      if (illegal) {
        triangles[a2] = p1;
        triangles[b] = p02;
        const hbl = halfedges[bl];
        if (hbl === -1) {
          let e = this._hullStart;
          do {
            if (this._hullTri[e] === bl) {
              this._hullTri[e] = a2;
              break;
            }
            e = this._hullPrev[e];
          } while (e !== this._hullStart);
        }
        this._link(a2, hbl);
        this._link(b, halfedges[ar]);
        this._link(ar, bl);
        const br = b0 + (b + 1) % 3;
        if (i < EDGE_STACK.length) {
          EDGE_STACK[i++] = br;
        }
      } else {
        if (i === 0) break;
        a2 = EDGE_STACK[--i];
      }
    }
    return ar;
  }
  _link(a2, b) {
    this._halfedges[a2] = b;
    if (b !== -1) this._halfedges[b] = a2;
  }
  // add a new triangle given vertex indices and adjacent half-edge ids
  _addTriangle(i0, i1, i2, a2, b, c2) {
    const t = this.trianglesLen;
    this._triangles[t] = i0;
    this._triangles[t + 1] = i1;
    this._triangles[t + 2] = i2;
    this._link(t, a2);
    this._link(t + 1, b);
    this._link(t + 2, c2);
    this.trianglesLen += 3;
    return t;
  }
}
function pseudoAngle(dx, dy) {
  const p = dx / (Math.abs(dx) + Math.abs(dy));
  return (dy > 0 ? 3 - p : 1 + p) / 4;
}
function dist(ax, ay, bx, by) {
  const dx = ax - bx;
  const dy = ay - by;
  return dx * dx + dy * dy;
}
function inCircle(ax, ay, bx, by, cx, cy, px, py) {
  const dx = ax - px;
  const dy = ay - py;
  const ex = bx - px;
  const ey = by - py;
  const fx = cx - px;
  const fy = cy - py;
  const ap = dx * dx + dy * dy;
  const bp = ex * ex + ey * ey;
  const cp = fx * fx + fy * fy;
  return dx * (ey * cp - bp * fy) - dy * (ex * cp - bp * fx) + ap * (ex * fy - ey * fx) < 0;
}
function circumradius(ax, ay, bx, by, cx, cy) {
  const dx = bx - ax;
  const dy = by - ay;
  const ex = cx - ax;
  const ey = cy - ay;
  const bl = dx * dx + dy * dy;
  const cl = ex * ex + ey * ey;
  const d = 0.5 / (dx * ey - dy * ex);
  const x2 = (ey * bl - dy * cl) * d;
  const y2 = (dx * cl - ex * bl) * d;
  return x2 * x2 + y2 * y2;
}
function circumcenter(ax, ay, bx, by, cx, cy) {
  const dx = bx - ax;
  const dy = by - ay;
  const ex = cx - ax;
  const ey = cy - ay;
  const bl = dx * dx + dy * dy;
  const cl = ex * ex + ey * ey;
  const d = 0.5 / (dx * ey - dy * ex);
  const x2 = ax + (ey * bl - dy * cl) * d;
  const y2 = ay + (dx * cl - ex * bl) * d;
  return { x: x2, y: y2 };
}
function quicksort(ids, dists, left, right) {
  if (right - left <= 20) {
    for (let i = left + 1; i <= right; i++) {
      const temp = ids[i];
      const tempDist = dists[temp];
      let j = i - 1;
      while (j >= left && dists[ids[j]] > tempDist) ids[j + 1] = ids[j--];
      ids[j + 1] = temp;
    }
  } else {
    const median2 = left + right >> 1;
    let i = left + 1;
    let j = right;
    swap(ids, median2, i);
    if (dists[ids[left]] > dists[ids[right]]) swap(ids, left, right);
    if (dists[ids[i]] > dists[ids[right]]) swap(ids, i, right);
    if (dists[ids[left]] > dists[ids[i]]) swap(ids, left, i);
    const temp = ids[i];
    const tempDist = dists[temp];
    while (true) {
      do
        i++;
      while (dists[ids[i]] < tempDist);
      do
        j--;
      while (dists[ids[j]] > tempDist);
      if (j < i) break;
      swap(ids, i, j);
    }
    ids[left + 1] = ids[j];
    ids[j] = temp;
    if (right - i + 1 >= j - left) {
      quicksort(ids, dists, i, right);
      quicksort(ids, dists, left, j - 1);
    } else {
      quicksort(ids, dists, left, j - 1);
      quicksort(ids, dists, i, right);
    }
  }
}
function swap(arr, i, j) {
  const tmp = arr[i];
  arr[i] = arr[j];
  arr[j] = tmp;
}
function defaultGetX(p) {
  return p[0];
}
function defaultGetY(p) {
  return p[1];
}
const epsilon$2 = 1e-6;
class Path {
  constructor() {
    this._x0 = this._y0 = // start of current subpath
    this._x1 = this._y1 = null;
    this._ = "";
  }
  moveTo(x2, y2) {
    this._ += `M${this._x0 = this._x1 = +x2},${this._y0 = this._y1 = +y2}`;
  }
  closePath() {
    if (this._x1 !== null) {
      this._x1 = this._x0, this._y1 = this._y0;
      this._ += "Z";
    }
  }
  lineTo(x2, y2) {
    this._ += `L${this._x1 = +x2},${this._y1 = +y2}`;
  }
  arc(x2, y2, r) {
    x2 = +x2, y2 = +y2, r = +r;
    const x02 = x2 + r;
    const y02 = y2;
    if (r < 0) throw new Error("negative radius");
    if (this._x1 === null) this._ += `M${x02},${y02}`;
    else if (Math.abs(this._x1 - x02) > epsilon$2 || Math.abs(this._y1 - y02) > epsilon$2) this._ += "L" + x02 + "," + y02;
    if (!r) return;
    this._ += `A${r},${r},0,1,1,${x2 - r},${y2}A${r},${r},0,1,1,${this._x1 = x02},${this._y1 = y02}`;
  }
  rect(x2, y2, w, h) {
    this._ += `M${this._x0 = this._x1 = +x2},${this._y0 = this._y1 = +y2}h${+w}v${+h}h${-w}Z`;
  }
  value() {
    return this._ || null;
  }
}
class Polygon {
  constructor() {
    this._ = [];
  }
  moveTo(x2, y2) {
    this._.push([x2, y2]);
  }
  closePath() {
    this._.push(this._[0].slice());
  }
  lineTo(x2, y2) {
    this._.push([x2, y2]);
  }
  value() {
    return this._.length ? this._ : null;
  }
}
class Voronoi {
  constructor(delaunay, [xmin, ymin, xmax, ymax] = [0, 0, 960, 500]) {
    if (!((xmax = +xmax) >= (xmin = +xmin)) || !((ymax = +ymax) >= (ymin = +ymin))) throw new Error("invalid bounds");
    this.delaunay = delaunay;
    this._circumcenters = new Float64Array(delaunay.points.length * 2);
    this.vectors = new Float64Array(delaunay.points.length * 2);
    this.xmax = xmax, this.xmin = xmin;
    this.ymax = ymax, this.ymin = ymin;
    this._init();
  }
  update() {
    this.delaunay.update();
    this._init();
    return this;
  }
  _init() {
    const { delaunay: { points, hull, triangles }, vectors } = this;
    let bx, by;
    const circumcenters = this.circumcenters = this._circumcenters.subarray(0, triangles.length / 3 * 2);
    for (let i = 0, j = 0, n = triangles.length, x2, y2; i < n; i += 3, j += 2) {
      const t1 = triangles[i] * 2;
      const t2 = triangles[i + 1] * 2;
      const t3 = triangles[i + 2] * 2;
      const x13 = points[t1];
      const y13 = points[t1 + 1];
      const x22 = points[t2];
      const y22 = points[t2 + 1];
      const x3 = points[t3];
      const y3 = points[t3 + 1];
      const dx = x22 - x13;
      const dy = y22 - y13;
      const ex = x3 - x13;
      const ey = y3 - y13;
      const ab = (dx * ey - dy * ex) * 2;
      if (Math.abs(ab) < 1e-9) {
        if (bx === void 0) {
          bx = by = 0;
          for (const i2 of hull) bx += points[i2 * 2], by += points[i2 * 2 + 1];
          bx /= hull.length, by /= hull.length;
        }
        const a2 = 1e9 * Math.sign((bx - x13) * ey - (by - y13) * ex);
        x2 = (x13 + x3) / 2 - a2 * ey;
        y2 = (y13 + y3) / 2 + a2 * ex;
      } else {
        const d = 1 / ab;
        const bl = dx * dx + dy * dy;
        const cl = ex * ex + ey * ey;
        x2 = x13 + (ey * bl - dy * cl) * d;
        y2 = y13 + (dx * cl - ex * bl) * d;
      }
      circumcenters[j] = x2;
      circumcenters[j + 1] = y2;
    }
    let h = hull[hull.length - 1];
    let p02, p1 = h * 4;
    let x02, x12 = points[2 * h];
    let y02, y12 = points[2 * h + 1];
    vectors.fill(0);
    for (let i = 0; i < hull.length; ++i) {
      h = hull[i];
      p02 = p1, x02 = x12, y02 = y12;
      p1 = h * 4, x12 = points[2 * h], y12 = points[2 * h + 1];
      vectors[p02 + 2] = vectors[p1] = y02 - y12;
      vectors[p02 + 3] = vectors[p1 + 1] = x12 - x02;
    }
  }
  render(context) {
    const buffer = context == null ? context = new Path() : void 0;
    const { delaunay: { halfedges, inedges, hull }, circumcenters, vectors } = this;
    if (hull.length <= 1) return null;
    for (let i = 0, n = halfedges.length; i < n; ++i) {
      const j = halfedges[i];
      if (j < i) continue;
      const ti = Math.floor(i / 3) * 2;
      const tj = Math.floor(j / 3) * 2;
      const xi = circumcenters[ti];
      const yi = circumcenters[ti + 1];
      const xj = circumcenters[tj];
      const yj = circumcenters[tj + 1];
      this._renderSegment(xi, yi, xj, yj, context);
    }
    let h0, h1 = hull[hull.length - 1];
    for (let i = 0; i < hull.length; ++i) {
      h0 = h1, h1 = hull[i];
      const t = Math.floor(inedges[h1] / 3) * 2;
      const x2 = circumcenters[t];
      const y2 = circumcenters[t + 1];
      const v = h0 * 4;
      const p = this._project(x2, y2, vectors[v + 2], vectors[v + 3]);
      if (p) this._renderSegment(x2, y2, p[0], p[1], context);
    }
    return buffer && buffer.value();
  }
  renderBounds(context) {
    const buffer = context == null ? context = new Path() : void 0;
    context.rect(this.xmin, this.ymin, this.xmax - this.xmin, this.ymax - this.ymin);
    return buffer && buffer.value();
  }
  renderCell(i, context) {
    const buffer = context == null ? context = new Path() : void 0;
    const points = this._clip(i);
    if (points === null || !points.length) return;
    context.moveTo(points[0], points[1]);
    let n = points.length;
    while (points[0] === points[n - 2] && points[1] === points[n - 1] && n > 1) n -= 2;
    for (let i2 = 2; i2 < n; i2 += 2) {
      if (points[i2] !== points[i2 - 2] || points[i2 + 1] !== points[i2 - 1])
        context.lineTo(points[i2], points[i2 + 1]);
    }
    context.closePath();
    return buffer && buffer.value();
  }
  *cellPolygons() {
    const { delaunay: { points } } = this;
    for (let i = 0, n = points.length / 2; i < n; ++i) {
      const cell = this.cellPolygon(i);
      if (cell) cell.index = i, yield cell;
    }
  }
  cellPolygon(i) {
    const polygon = new Polygon();
    this.renderCell(i, polygon);
    return polygon.value();
  }
  _renderSegment(x02, y02, x12, y12, context) {
    let S;
    const c0 = this._regioncode(x02, y02);
    const c1 = this._regioncode(x12, y12);
    if (c0 === 0 && c1 === 0) {
      context.moveTo(x02, y02);
      context.lineTo(x12, y12);
    } else if (S = this._clipSegment(x02, y02, x12, y12, c0, c1)) {
      context.moveTo(S[0], S[1]);
      context.lineTo(S[2], S[3]);
    }
  }
  contains(i, x2, y2) {
    if ((x2 = +x2, x2 !== x2) || (y2 = +y2, y2 !== y2)) return false;
    return this.delaunay._step(i, x2, y2) === i;
  }
  *neighbors(i) {
    const ci = this._clip(i);
    if (ci) for (const j of this.delaunay.neighbors(i)) {
      const cj = this._clip(j);
      if (cj) loop: for (let ai = 0, li = ci.length; ai < li; ai += 2) {
        for (let aj = 0, lj = cj.length; aj < lj; aj += 2) {
          if (ci[ai] === cj[aj] && ci[ai + 1] === cj[aj + 1] && ci[(ai + 2) % li] === cj[(aj + lj - 2) % lj] && ci[(ai + 3) % li] === cj[(aj + lj - 1) % lj]) {
            yield j;
            break loop;
          }
        }
      }
    }
  }
  _cell(i) {
    const { circumcenters, delaunay: { inedges, halfedges, triangles } } = this;
    const e0 = inedges[i];
    if (e0 === -1) return null;
    const points = [];
    let e = e0;
    do {
      const t = Math.floor(e / 3);
      points.push(circumcenters[t * 2], circumcenters[t * 2 + 1]);
      e = e % 3 === 2 ? e - 2 : e + 1;
      if (triangles[e] !== i) break;
      e = halfedges[e];
    } while (e !== e0 && e !== -1);
    return points;
  }
  _clip(i) {
    if (i === 0 && this.delaunay.hull.length === 1) {
      return [this.xmax, this.ymin, this.xmax, this.ymax, this.xmin, this.ymax, this.xmin, this.ymin];
    }
    const points = this._cell(i);
    if (points === null) return null;
    const { vectors: V } = this;
    const v = i * 4;
    return this._simplify(V[v] || V[v + 1] ? this._clipInfinite(i, points, V[v], V[v + 1], V[v + 2], V[v + 3]) : this._clipFinite(i, points));
  }
  _clipFinite(i, points) {
    const n = points.length;
    let P = null;
    let x02, y02, x12 = points[n - 2], y12 = points[n - 1];
    let c0, c1 = this._regioncode(x12, y12);
    let e0, e1 = 0;
    for (let j = 0; j < n; j += 2) {
      x02 = x12, y02 = y12, x12 = points[j], y12 = points[j + 1];
      c0 = c1, c1 = this._regioncode(x12, y12);
      if (c0 === 0 && c1 === 0) {
        e0 = e1, e1 = 0;
        if (P) P.push(x12, y12);
        else P = [x12, y12];
      } else {
        let S, sx0, sy0, sx1, sy1;
        if (c0 === 0) {
          if ((S = this._clipSegment(x02, y02, x12, y12, c0, c1)) === null) continue;
          [sx0, sy0, sx1, sy1] = S;
        } else {
          if ((S = this._clipSegment(x12, y12, x02, y02, c1, c0)) === null) continue;
          [sx1, sy1, sx0, sy0] = S;
          e0 = e1, e1 = this._edgecode(sx0, sy0);
          if (e0 && e1) this._edge(i, e0, e1, P, P.length);
          if (P) P.push(sx0, sy0);
          else P = [sx0, sy0];
        }
        e0 = e1, e1 = this._edgecode(sx1, sy1);
        if (e0 && e1) this._edge(i, e0, e1, P, P.length);
        if (P) P.push(sx1, sy1);
        else P = [sx1, sy1];
      }
    }
    if (P) {
      e0 = e1, e1 = this._edgecode(P[0], P[1]);
      if (e0 && e1) this._edge(i, e0, e1, P, P.length);
    } else if (this.contains(i, (this.xmin + this.xmax) / 2, (this.ymin + this.ymax) / 2)) {
      return [this.xmax, this.ymin, this.xmax, this.ymax, this.xmin, this.ymax, this.xmin, this.ymin];
    }
    return P;
  }
  _clipSegment(x02, y02, x12, y12, c0, c1) {
    const flip = c0 < c1;
    if (flip) [x02, y02, x12, y12, c0, c1] = [x12, y12, x02, y02, c1, c0];
    while (true) {
      if (c0 === 0 && c1 === 0) return flip ? [x12, y12, x02, y02] : [x02, y02, x12, y12];
      if (c0 & c1) return null;
      let x2, y2, c2 = c0 || c1;
      if (c2 & 8) x2 = x02 + (x12 - x02) * (this.ymax - y02) / (y12 - y02), y2 = this.ymax;
      else if (c2 & 4) x2 = x02 + (x12 - x02) * (this.ymin - y02) / (y12 - y02), y2 = this.ymin;
      else if (c2 & 2) y2 = y02 + (y12 - y02) * (this.xmax - x02) / (x12 - x02), x2 = this.xmax;
      else y2 = y02 + (y12 - y02) * (this.xmin - x02) / (x12 - x02), x2 = this.xmin;
      if (c0) x02 = x2, y02 = y2, c0 = this._regioncode(x02, y02);
      else x12 = x2, y12 = y2, c1 = this._regioncode(x12, y12);
    }
  }
  _clipInfinite(i, points, vx0, vy0, vxn, vyn) {
    let P = Array.from(points), p;
    if (p = this._project(P[0], P[1], vx0, vy0)) P.unshift(p[0], p[1]);
    if (p = this._project(P[P.length - 2], P[P.length - 1], vxn, vyn)) P.push(p[0], p[1]);
    if (P = this._clipFinite(i, P)) {
      for (let j = 0, n = P.length, c0, c1 = this._edgecode(P[n - 2], P[n - 1]); j < n; j += 2) {
        c0 = c1, c1 = this._edgecode(P[j], P[j + 1]);
        if (c0 && c1) j = this._edge(i, c0, c1, P, j), n = P.length;
      }
    } else if (this.contains(i, (this.xmin + this.xmax) / 2, (this.ymin + this.ymax) / 2)) {
      P = [this.xmin, this.ymin, this.xmax, this.ymin, this.xmax, this.ymax, this.xmin, this.ymax];
    }
    return P;
  }
  _edge(i, e0, e1, P, j) {
    while (e0 !== e1) {
      let x2, y2;
      switch (e0) {
        case 5:
          e0 = 4;
          continue;
        // top-left
        case 4:
          e0 = 6, x2 = this.xmax, y2 = this.ymin;
          break;
        // top
        case 6:
          e0 = 2;
          continue;
        // top-right
        case 2:
          e0 = 10, x2 = this.xmax, y2 = this.ymax;
          break;
        // right
        case 10:
          e0 = 8;
          continue;
        // bottom-right
        case 8:
          e0 = 9, x2 = this.xmin, y2 = this.ymax;
          break;
        // bottom
        case 9:
          e0 = 1;
          continue;
        // bottom-left
        case 1:
          e0 = 5, x2 = this.xmin, y2 = this.ymin;
          break;
      }
      if ((P[j] !== x2 || P[j + 1] !== y2) && this.contains(i, x2, y2)) {
        P.splice(j, 0, x2, y2), j += 2;
      }
    }
    return j;
  }
  _project(x02, y02, vx, vy) {
    let t = Infinity, c2, x2, y2;
    if (vy < 0) {
      if (y02 <= this.ymin) return null;
      if ((c2 = (this.ymin - y02) / vy) < t) y2 = this.ymin, x2 = x02 + (t = c2) * vx;
    } else if (vy > 0) {
      if (y02 >= this.ymax) return null;
      if ((c2 = (this.ymax - y02) / vy) < t) y2 = this.ymax, x2 = x02 + (t = c2) * vx;
    }
    if (vx > 0) {
      if (x02 >= this.xmax) return null;
      if ((c2 = (this.xmax - x02) / vx) < t) x2 = this.xmax, y2 = y02 + (t = c2) * vy;
    } else if (vx < 0) {
      if (x02 <= this.xmin) return null;
      if ((c2 = (this.xmin - x02) / vx) < t) x2 = this.xmin, y2 = y02 + (t = c2) * vy;
    }
    return [x2, y2];
  }
  _edgecode(x2, y2) {
    return (x2 === this.xmin ? 1 : x2 === this.xmax ? 2 : 0) | (y2 === this.ymin ? 4 : y2 === this.ymax ? 8 : 0);
  }
  _regioncode(x2, y2) {
    return (x2 < this.xmin ? 1 : x2 > this.xmax ? 2 : 0) | (y2 < this.ymin ? 4 : y2 > this.ymax ? 8 : 0);
  }
  _simplify(P) {
    if (P && P.length > 4) {
      for (let i = 0; i < P.length; i += 2) {
        const j = (i + 2) % P.length, k = (i + 4) % P.length;
        if (P[i] === P[j] && P[j] === P[k] || P[i + 1] === P[j + 1] && P[j + 1] === P[k + 1]) {
          P.splice(j, 2), i -= 2;
        }
      }
      if (!P.length) P = null;
    }
    return P;
  }
}
const tau$1 = 2 * Math.PI, pow$2 = Math.pow;
function pointX(p) {
  return p[0];
}
function pointY(p) {
  return p[1];
}
function collinear(d) {
  const { triangles, coords } = d;
  for (let i = 0; i < triangles.length; i += 3) {
    const a2 = 2 * triangles[i], b = 2 * triangles[i + 1], c2 = 2 * triangles[i + 2], cross = (coords[c2] - coords[a2]) * (coords[b + 1] - coords[a2 + 1]) - (coords[b] - coords[a2]) * (coords[c2 + 1] - coords[a2 + 1]);
    if (cross > 1e-10) return false;
  }
  return true;
}
function jitter(x2, y2, r) {
  return [x2 + Math.sin(x2 + y2) * r, y2 + Math.cos(x2 - y2) * r];
}
class Delaunay {
  static from(points, fx = pointX, fy = pointY, that) {
    return new Delaunay("length" in points ? flatArray(points, fx, fy, that) : Float64Array.from(flatIterable(points, fx, fy, that)));
  }
  constructor(points) {
    this._delaunator = new Delaunator(points);
    this.inedges = new Int32Array(points.length / 2);
    this._hullIndex = new Int32Array(points.length / 2);
    this.points = this._delaunator.coords;
    this._init();
  }
  update() {
    this._delaunator.update();
    this._init();
    return this;
  }
  _init() {
    const d = this._delaunator, points = this.points;
    if (d.hull && d.hull.length > 2 && collinear(d)) {
      this.collinear = Int32Array.from({ length: points.length / 2 }, (_, i) => i).sort((i, j) => points[2 * i] - points[2 * j] || points[2 * i + 1] - points[2 * j + 1]);
      const e = this.collinear[0], f = this.collinear[this.collinear.length - 1], bounds = [points[2 * e], points[2 * e + 1], points[2 * f], points[2 * f + 1]], r = 1e-8 * Math.hypot(bounds[3] - bounds[1], bounds[2] - bounds[0]);
      for (let i = 0, n = points.length / 2; i < n; ++i) {
        const p = jitter(points[2 * i], points[2 * i + 1], r);
        points[2 * i] = p[0];
        points[2 * i + 1] = p[1];
      }
      this._delaunator = new Delaunator(points);
    } else {
      delete this.collinear;
    }
    const halfedges = this.halfedges = this._delaunator.halfedges;
    const hull = this.hull = this._delaunator.hull;
    const triangles = this.triangles = this._delaunator.triangles;
    const inedges = this.inedges.fill(-1);
    const hullIndex = this._hullIndex.fill(-1);
    for (let e = 0, n = halfedges.length; e < n; ++e) {
      const p = triangles[e % 3 === 2 ? e - 2 : e + 1];
      if (halfedges[e] === -1 || inedges[p] === -1) inedges[p] = e;
    }
    for (let i = 0, n = hull.length; i < n; ++i) {
      hullIndex[hull[i]] = i;
    }
    if (hull.length <= 2 && hull.length > 0) {
      this.triangles = new Int32Array(3).fill(-1);
      this.halfedges = new Int32Array(3).fill(-1);
      this.triangles[0] = hull[0];
      inedges[hull[0]] = 1;
      if (hull.length === 2) {
        inedges[hull[1]] = 0;
        this.triangles[1] = hull[1];
        this.triangles[2] = hull[1];
      }
    }
  }
  voronoi(bounds) {
    return new Voronoi(this, bounds);
  }
  *neighbors(i) {
    const { inedges, hull, _hullIndex, halfedges, triangles, collinear: collinear2 } = this;
    if (collinear2) {
      const l = collinear2.indexOf(i);
      if (l > 0) yield collinear2[l - 1];
      if (l < collinear2.length - 1) yield collinear2[l + 1];
      return;
    }
    const e0 = inedges[i];
    if (e0 === -1) return;
    let e = e0, p02 = -1;
    do {
      yield p02 = triangles[e];
      e = e % 3 === 2 ? e - 2 : e + 1;
      if (triangles[e] !== i) return;
      e = halfedges[e];
      if (e === -1) {
        const p = hull[(_hullIndex[i] + 1) % hull.length];
        if (p !== p02) yield p;
        return;
      }
    } while (e !== e0);
  }
  find(x2, y2, i = 0) {
    if ((x2 = +x2, x2 !== x2) || (y2 = +y2, y2 !== y2)) return -1;
    const i0 = i;
    let c2;
    while ((c2 = this._step(i, x2, y2)) >= 0 && c2 !== i && c2 !== i0) i = c2;
    return c2;
  }
  _step(i, x2, y2) {
    const { inedges, hull, _hullIndex, halfedges, triangles, points } = this;
    if (inedges[i] === -1 || !points.length) return (i + 1) % (points.length >> 1);
    let c2 = i;
    let dc = pow$2(x2 - points[i * 2], 2) + pow$2(y2 - points[i * 2 + 1], 2);
    const e0 = inedges[i];
    let e = e0;
    do {
      let t = triangles[e];
      const dt = pow$2(x2 - points[t * 2], 2) + pow$2(y2 - points[t * 2 + 1], 2);
      if (dt < dc) dc = dt, c2 = t;
      e = e % 3 === 2 ? e - 2 : e + 1;
      if (triangles[e] !== i) break;
      e = halfedges[e];
      if (e === -1) {
        e = hull[(_hullIndex[i] + 1) % hull.length];
        if (e !== t) {
          if (pow$2(x2 - points[e * 2], 2) + pow$2(y2 - points[e * 2 + 1], 2) < dc) return e;
        }
        break;
      }
    } while (e !== e0);
    return c2;
  }
  render(context) {
    const buffer = context == null ? context = new Path() : void 0;
    const { points, halfedges, triangles } = this;
    for (let i = 0, n = halfedges.length; i < n; ++i) {
      const j = halfedges[i];
      if (j < i) continue;
      const ti = triangles[i] * 2;
      const tj = triangles[j] * 2;
      context.moveTo(points[ti], points[ti + 1]);
      context.lineTo(points[tj], points[tj + 1]);
    }
    this.renderHull(context);
    return buffer && buffer.value();
  }
  renderPoints(context, r) {
    if (r === void 0 && (!context || typeof context.moveTo !== "function")) r = context, context = null;
    r = r == void 0 ? 2 : +r;
    const buffer = context == null ? context = new Path() : void 0;
    const { points } = this;
    for (let i = 0, n = points.length; i < n; i += 2) {
      const x2 = points[i], y2 = points[i + 1];
      context.moveTo(x2 + r, y2);
      context.arc(x2, y2, r, 0, tau$1);
    }
    return buffer && buffer.value();
  }
  renderHull(context) {
    const buffer = context == null ? context = new Path() : void 0;
    const { hull, points } = this;
    const h = hull[0] * 2, n = hull.length;
    context.moveTo(points[h], points[h + 1]);
    for (let i = 1; i < n; ++i) {
      const h2 = 2 * hull[i];
      context.lineTo(points[h2], points[h2 + 1]);
    }
    context.closePath();
    return buffer && buffer.value();
  }
  hullPolygon() {
    const polygon = new Polygon();
    this.renderHull(polygon);
    return polygon.value();
  }
  renderTriangle(i, context) {
    const buffer = context == null ? context = new Path() : void 0;
    const { points, triangles } = this;
    const t0 = triangles[i *= 3] * 2;
    const t1 = triangles[i + 1] * 2;
    const t2 = triangles[i + 2] * 2;
    context.moveTo(points[t0], points[t0 + 1]);
    context.lineTo(points[t1], points[t1 + 1]);
    context.lineTo(points[t2], points[t2 + 1]);
    context.closePath();
    return buffer && buffer.value();
  }
  *trianglePolygons() {
    const { triangles } = this;
    for (let i = 0, n = triangles.length / 3; i < n; ++i) {
      yield this.trianglePolygon(i);
    }
  }
  trianglePolygon(i) {
    const polygon = new Polygon();
    this.renderTriangle(i, polygon);
    return polygon.value();
  }
}
function flatArray(points, fx, fy, that) {
  const n = points.length;
  const array2 = new Float64Array(n * 2);
  for (let i = 0; i < n; ++i) {
    const p = points[i];
    array2[i * 2] = fx.call(that, p, i, points);
    array2[i * 2 + 1] = fy.call(that, p, i, points);
  }
  return array2;
}
function* flatIterable(points, fx, fy, that) {
  let i = 0;
  for (const p of points) {
    yield fx.call(that, p, i, points);
    yield fy.call(that, p, i, points);
    ++i;
  }
}
function forceCenter(x2, y2) {
  var nodes, strength = 1;
  if (x2 == null) x2 = 0;
  if (y2 == null) y2 = 0;
  function force() {
    var i, n = nodes.length, node, sx = 0, sy = 0;
    for (i = 0; i < n; ++i) {
      node = nodes[i], sx += node.x, sy += node.y;
    }
    for (sx = (sx / n - x2) * strength, sy = (sy / n - y2) * strength, i = 0; i < n; ++i) {
      node = nodes[i], node.x -= sx, node.y -= sy;
    }
  }
  force.initialize = function(_) {
    nodes = _;
  };
  force.x = function(_) {
    return arguments.length ? (x2 = +_, force) : x2;
  };
  force.y = function(_) {
    return arguments.length ? (y2 = +_, force) : y2;
  };
  force.strength = function(_) {
    return arguments.length ? (strength = +_, force) : strength;
  };
  return force;
}
function tree_add(d) {
  const x2 = +this._x.call(null, d), y2 = +this._y.call(null, d);
  return add(this.cover(x2, y2), x2, y2, d);
}
function add(tree2, x2, y2, d) {
  if (isNaN(x2) || isNaN(y2)) return tree2;
  var parent, node = tree2._root, leaf = { data: d }, x02 = tree2._x0, y02 = tree2._y0, x12 = tree2._x1, y12 = tree2._y1, xm, ym, xp, yp, right, bottom, i, j;
  if (!node) return tree2._root = leaf, tree2;
  while (node.length) {
    if (right = x2 >= (xm = (x02 + x12) / 2)) x02 = xm;
    else x12 = xm;
    if (bottom = y2 >= (ym = (y02 + y12) / 2)) y02 = ym;
    else y12 = ym;
    if (parent = node, !(node = node[i = bottom << 1 | right])) return parent[i] = leaf, tree2;
  }
  xp = +tree2._x.call(null, node.data);
  yp = +tree2._y.call(null, node.data);
  if (x2 === xp && y2 === yp) return leaf.next = node, parent ? parent[i] = leaf : tree2._root = leaf, tree2;
  do {
    parent = parent ? parent[i] = new Array(4) : tree2._root = new Array(4);
    if (right = x2 >= (xm = (x02 + x12) / 2)) x02 = xm;
    else x12 = xm;
    if (bottom = y2 >= (ym = (y02 + y12) / 2)) y02 = ym;
    else y12 = ym;
  } while ((i = bottom << 1 | right) === (j = (yp >= ym) << 1 | xp >= xm));
  return parent[j] = node, parent[i] = leaf, tree2;
}
function addAll(data) {
  var d, i, n = data.length, x2, y2, xz = new Array(n), yz = new Array(n), x02 = Infinity, y02 = Infinity, x12 = -Infinity, y12 = -Infinity;
  for (i = 0; i < n; ++i) {
    if (isNaN(x2 = +this._x.call(null, d = data[i])) || isNaN(y2 = +this._y.call(null, d))) continue;
    xz[i] = x2;
    yz[i] = y2;
    if (x2 < x02) x02 = x2;
    if (x2 > x12) x12 = x2;
    if (y2 < y02) y02 = y2;
    if (y2 > y12) y12 = y2;
  }
  if (x02 > x12 || y02 > y12) return this;
  this.cover(x02, y02).cover(x12, y12);
  for (i = 0; i < n; ++i) {
    add(this, xz[i], yz[i], data[i]);
  }
  return this;
}
function tree_cover(x2, y2) {
  if (isNaN(x2 = +x2) || isNaN(y2 = +y2)) return this;
  var x02 = this._x0, y02 = this._y0, x12 = this._x1, y12 = this._y1;
  if (isNaN(x02)) {
    x12 = (x02 = Math.floor(x2)) + 1;
    y12 = (y02 = Math.floor(y2)) + 1;
  } else {
    var z = x12 - x02 || 1, node = this._root, parent, i;
    while (x02 > x2 || x2 >= x12 || y02 > y2 || y2 >= y12) {
      i = (y2 < y02) << 1 | x2 < x02;
      parent = new Array(4), parent[i] = node, node = parent, z *= 2;
      switch (i) {
        case 0:
          x12 = x02 + z, y12 = y02 + z;
          break;
        case 1:
          x02 = x12 - z, y12 = y02 + z;
          break;
        case 2:
          x12 = x02 + z, y02 = y12 - z;
          break;
        case 3:
          x02 = x12 - z, y02 = y12 - z;
          break;
      }
    }
    if (this._root && this._root.length) this._root = node;
  }
  this._x0 = x02;
  this._y0 = y02;
  this._x1 = x12;
  this._y1 = y12;
  return this;
}
function tree_data() {
  var data = [];
  this.visit(function(node) {
    if (!node.length) do
      data.push(node.data);
    while (node = node.next);
  });
  return data;
}
function tree_extent(_) {
  return arguments.length ? this.cover(+_[0][0], +_[0][1]).cover(+_[1][0], +_[1][1]) : isNaN(this._x0) ? void 0 : [[this._x0, this._y0], [this._x1, this._y1]];
}
function Quad(node, x02, y02, x12, y12) {
  this.node = node;
  this.x0 = x02;
  this.y0 = y02;
  this.x1 = x12;
  this.y1 = y12;
}
function tree_find(x2, y2, radius) {
  var data, x02 = this._x0, y02 = this._y0, x12, y12, x22, y22, x3 = this._x1, y3 = this._y1, quads = [], node = this._root, q, i;
  if (node) quads.push(new Quad(node, x02, y02, x3, y3));
  if (radius == null) radius = Infinity;
  else {
    x02 = x2 - radius, y02 = y2 - radius;
    x3 = x2 + radius, y3 = y2 + radius;
    radius *= radius;
  }
  while (q = quads.pop()) {
    if (!(node = q.node) || (x12 = q.x0) > x3 || (y12 = q.y0) > y3 || (x22 = q.x1) < x02 || (y22 = q.y1) < y02) continue;
    if (node.length) {
      var xm = (x12 + x22) / 2, ym = (y12 + y22) / 2;
      quads.push(
        new Quad(node[3], xm, ym, x22, y22),
        new Quad(node[2], x12, ym, xm, y22),
        new Quad(node[1], xm, y12, x22, ym),
        new Quad(node[0], x12, y12, xm, ym)
      );
      if (i = (y2 >= ym) << 1 | x2 >= xm) {
        q = quads[quads.length - 1];
        quads[quads.length - 1] = quads[quads.length - 1 - i];
        quads[quads.length - 1 - i] = q;
      }
    } else {
      var dx = x2 - +this._x.call(null, node.data), dy = y2 - +this._y.call(null, node.data), d2 = dx * dx + dy * dy;
      if (d2 < radius) {
        var d = Math.sqrt(radius = d2);
        x02 = x2 - d, y02 = y2 - d;
        x3 = x2 + d, y3 = y2 + d;
        data = node.data;
      }
    }
  }
  return data;
}
function tree_remove(d) {
  if (isNaN(x2 = +this._x.call(null, d)) || isNaN(y2 = +this._y.call(null, d))) return this;
  var parent, node = this._root, retainer, previous, next, x02 = this._x0, y02 = this._y0, x12 = this._x1, y12 = this._y1, x2, y2, xm, ym, right, bottom, i, j;
  if (!node) return this;
  if (node.length) while (true) {
    if (right = x2 >= (xm = (x02 + x12) / 2)) x02 = xm;
    else x12 = xm;
    if (bottom = y2 >= (ym = (y02 + y12) / 2)) y02 = ym;
    else y12 = ym;
    if (!(parent = node, node = node[i = bottom << 1 | right])) return this;
    if (!node.length) break;
    if (parent[i + 1 & 3] || parent[i + 2 & 3] || parent[i + 3 & 3]) retainer = parent, j = i;
  }
  while (node.data !== d) if (!(previous = node, node = node.next)) return this;
  if (next = node.next) delete node.next;
  if (previous) return next ? previous.next = next : delete previous.next, this;
  if (!parent) return this._root = next, this;
  next ? parent[i] = next : delete parent[i];
  if ((node = parent[0] || parent[1] || parent[2] || parent[3]) && node === (parent[3] || parent[2] || parent[1] || parent[0]) && !node.length) {
    if (retainer) retainer[j] = node;
    else this._root = node;
  }
  return this;
}
function removeAll(data) {
  for (var i = 0, n = data.length; i < n; ++i) this.remove(data[i]);
  return this;
}
function tree_root() {
  return this._root;
}
function tree_size() {
  var size = 0;
  this.visit(function(node) {
    if (!node.length) do
      ++size;
    while (node = node.next);
  });
  return size;
}
function tree_visit(callback) {
  var quads = [], q, node = this._root, child, x02, y02, x12, y12;
  if (node) quads.push(new Quad(node, this._x0, this._y0, this._x1, this._y1));
  while (q = quads.pop()) {
    if (!callback(node = q.node, x02 = q.x0, y02 = q.y0, x12 = q.x1, y12 = q.y1) && node.length) {
      var xm = (x02 + x12) / 2, ym = (y02 + y12) / 2;
      if (child = node[3]) quads.push(new Quad(child, xm, ym, x12, y12));
      if (child = node[2]) quads.push(new Quad(child, x02, ym, xm, y12));
      if (child = node[1]) quads.push(new Quad(child, xm, y02, x12, ym));
      if (child = node[0]) quads.push(new Quad(child, x02, y02, xm, ym));
    }
  }
  return this;
}
function tree_visitAfter(callback) {
  var quads = [], next = [], q;
  if (this._root) quads.push(new Quad(this._root, this._x0, this._y0, this._x1, this._y1));
  while (q = quads.pop()) {
    var node = q.node;
    if (node.length) {
      var child, x02 = q.x0, y02 = q.y0, x12 = q.x1, y12 = q.y1, xm = (x02 + x12) / 2, ym = (y02 + y12) / 2;
      if (child = node[0]) quads.push(new Quad(child, x02, y02, xm, ym));
      if (child = node[1]) quads.push(new Quad(child, xm, y02, x12, ym));
      if (child = node[2]) quads.push(new Quad(child, x02, ym, xm, y12));
      if (child = node[3]) quads.push(new Quad(child, xm, ym, x12, y12));
    }
    next.push(q);
  }
  while (q = next.pop()) {
    callback(q.node, q.x0, q.y0, q.x1, q.y1);
  }
  return this;
}
function defaultX(d) {
  return d[0];
}
function tree_x(_) {
  return arguments.length ? (this._x = _, this) : this._x;
}
function defaultY(d) {
  return d[1];
}
function tree_y(_) {
  return arguments.length ? (this._y = _, this) : this._y;
}
function quadtree(nodes, x2, y2) {
  var tree2 = new Quadtree(x2 == null ? defaultX : x2, y2 == null ? defaultY : y2, NaN, NaN, NaN, NaN);
  return nodes == null ? tree2 : tree2.addAll(nodes);
}
function Quadtree(x2, y2, x02, y02, x12, y12) {
  this._x = x2;
  this._y = y2;
  this._x0 = x02;
  this._y0 = y02;
  this._x1 = x12;
  this._y1 = y12;
  this._root = void 0;
}
function leaf_copy(leaf) {
  var copy2 = { data: leaf.data }, next = copy2;
  while (leaf = leaf.next) next = next.next = { data: leaf.data };
  return copy2;
}
var treeProto = quadtree.prototype = Quadtree.prototype;
treeProto.copy = function() {
  var copy2 = new Quadtree(this._x, this._y, this._x0, this._y0, this._x1, this._y1), node = this._root, nodes, child;
  if (!node) return copy2;
  if (!node.length) return copy2._root = leaf_copy(node), copy2;
  nodes = [{ source: node, target: copy2._root = new Array(4) }];
  while (node = nodes.pop()) {
    for (var i = 0; i < 4; ++i) {
      if (child = node.source[i]) {
        if (child.length) nodes.push({ source: child, target: node.target[i] = new Array(4) });
        else node.target[i] = leaf_copy(child);
      }
    }
  }
  return copy2;
};
treeProto.add = tree_add;
treeProto.addAll = addAll;
treeProto.cover = tree_cover;
treeProto.data = tree_data;
treeProto.extent = tree_extent;
treeProto.find = tree_find;
treeProto.remove = tree_remove;
treeProto.removeAll = removeAll;
treeProto.root = tree_root;
treeProto.size = tree_size;
treeProto.visit = tree_visit;
treeProto.visitAfter = tree_visitAfter;
treeProto.x = tree_x;
treeProto.y = tree_y;
function constant(x2) {
  return function() {
    return x2;
  };
}
function jiggle(random) {
  return (random() - 0.5) * 1e-6;
}
function x$1(d) {
  return d.x + d.vx;
}
function y$1(d) {
  return d.y + d.vy;
}
function forceCollide(radius) {
  var nodes, radii, random, strength = 1, iterations2 = 1;
  if (typeof radius !== "function") radius = constant(radius == null ? 1 : +radius);
  function force() {
    var i, n = nodes.length, tree2, node, xi, yi, ri, ri2;
    for (var k = 0; k < iterations2; ++k) {
      tree2 = quadtree(nodes, x$1, y$1).visitAfter(prepare);
      for (i = 0; i < n; ++i) {
        node = nodes[i];
        ri = radii[node.index], ri2 = ri * ri;
        xi = node.x + node.vx;
        yi = node.y + node.vy;
        tree2.visit(apply);
      }
    }
    function apply(quad, x02, y02, x12, y12) {
      var data = quad.data, rj = quad.r, r = ri + rj;
      if (data) {
        if (data.index > node.index) {
          var x2 = xi - data.x - data.vx, y2 = yi - data.y - data.vy, l = x2 * x2 + y2 * y2;
          if (l < r * r) {
            if (x2 === 0) x2 = jiggle(random), l += x2 * x2;
            if (y2 === 0) y2 = jiggle(random), l += y2 * y2;
            l = (r - (l = Math.sqrt(l))) / l * strength;
            node.vx += (x2 *= l) * (r = (rj *= rj) / (ri2 + rj));
            node.vy += (y2 *= l) * r;
            data.vx -= x2 * (r = 1 - r);
            data.vy -= y2 * r;
          }
        }
        return;
      }
      return x02 > xi + r || x12 < xi - r || y02 > yi + r || y12 < yi - r;
    }
  }
  function prepare(quad) {
    if (quad.data) return quad.r = radii[quad.data.index];
    for (var i = quad.r = 0; i < 4; ++i) {
      if (quad[i] && quad[i].r > quad.r) {
        quad.r = quad[i].r;
      }
    }
  }
  function initialize() {
    if (!nodes) return;
    var i, n = nodes.length, node;
    radii = new Array(n);
    for (i = 0; i < n; ++i) node = nodes[i], radii[node.index] = +radius(node, i, nodes);
  }
  force.initialize = function(_nodes, _random) {
    nodes = _nodes;
    random = _random;
    initialize();
  };
  force.iterations = function(_) {
    return arguments.length ? (iterations2 = +_, force) : iterations2;
  };
  force.strength = function(_) {
    return arguments.length ? (strength = +_, force) : strength;
  };
  force.radius = function(_) {
    return arguments.length ? (radius = typeof _ === "function" ? _ : constant(+_), initialize(), force) : radius;
  };
  return force;
}
function index(d) {
  return d.index;
}
function find(nodeById, nodeId) {
  var node = nodeById.get(nodeId);
  if (!node) throw new Error("node not found: " + nodeId);
  return node;
}
function forceLink(links) {
  var id = index, strength = defaultStrength, strengths, distance = constant(30), distances, nodes, count, bias, random, iterations2 = 1;
  if (links == null) links = [];
  function defaultStrength(link2) {
    return 1 / Math.min(count[link2.source.index], count[link2.target.index]);
  }
  function force(alpha) {
    for (var k = 0, n = links.length; k < iterations2; ++k) {
      for (var i = 0, link2, source, target, x2, y2, l, b; i < n; ++i) {
        link2 = links[i], source = link2.source, target = link2.target;
        x2 = target.x + target.vx - source.x - source.vx || jiggle(random);
        y2 = target.y + target.vy - source.y - source.vy || jiggle(random);
        l = Math.sqrt(x2 * x2 + y2 * y2);
        l = (l - distances[i]) / l * alpha * strengths[i];
        x2 *= l, y2 *= l;
        target.vx -= x2 * (b = bias[i]);
        target.vy -= y2 * b;
        source.vx += x2 * (b = 1 - b);
        source.vy += y2 * b;
      }
    }
  }
  function initialize() {
    if (!nodes) return;
    var i, n = nodes.length, m2 = links.length, nodeById = new Map(nodes.map((d, i2) => [id(d, i2, nodes), d])), link2;
    for (i = 0, count = new Array(n); i < m2; ++i) {
      link2 = links[i], link2.index = i;
      if (typeof link2.source !== "object") link2.source = find(nodeById, link2.source);
      if (typeof link2.target !== "object") link2.target = find(nodeById, link2.target);
      count[link2.source.index] = (count[link2.source.index] || 0) + 1;
      count[link2.target.index] = (count[link2.target.index] || 0) + 1;
    }
    for (i = 0, bias = new Array(m2); i < m2; ++i) {
      link2 = links[i], bias[i] = count[link2.source.index] / (count[link2.source.index] + count[link2.target.index]);
    }
    strengths = new Array(m2), initializeStrength();
    distances = new Array(m2), initializeDistance();
  }
  function initializeStrength() {
    if (!nodes) return;
    for (var i = 0, n = links.length; i < n; ++i) {
      strengths[i] = +strength(links[i], i, links);
    }
  }
  function initializeDistance() {
    if (!nodes) return;
    for (var i = 0, n = links.length; i < n; ++i) {
      distances[i] = +distance(links[i], i, links);
    }
  }
  force.initialize = function(_nodes, _random) {
    nodes = _nodes;
    random = _random;
    initialize();
  };
  force.links = function(_) {
    return arguments.length ? (links = _, initialize(), force) : links;
  };
  force.id = function(_) {
    return arguments.length ? (id = _, force) : id;
  };
  force.iterations = function(_) {
    return arguments.length ? (iterations2 = +_, force) : iterations2;
  };
  force.strength = function(_) {
    return arguments.length ? (strength = typeof _ === "function" ? _ : constant(+_), initializeStrength(), force) : strength;
  };
  force.distance = function(_) {
    return arguments.length ? (distance = typeof _ === "function" ? _ : constant(+_), initializeDistance(), force) : distance;
  };
  return force;
}
const a$1 = 1664525;
const c$1 = 1013904223;
const m$1 = 4294967296;
function lcg$1() {
  let s = 1;
  return () => (s = (a$1 * s + c$1) % m$1) / m$1;
}
function x(d) {
  return d.x;
}
function y(d) {
  return d.y;
}
var initialRadius = 10, initialAngle = Math.PI * (3 - Math.sqrt(5));
function forceSimulation(nodes) {
  var simulation, alpha = 1, alphaMin = 1e-3, alphaDecay = 1 - Math.pow(alphaMin, 1 / 300), alphaTarget = 0, velocityDecay = 0.6, forces = /* @__PURE__ */ new Map(), stepper = timer(step), event = dispatch("tick", "end"), random = lcg$1();
  if (nodes == null) nodes = [];
  function step() {
    tick();
    event.call("tick", simulation);
    if (alpha < alphaMin) {
      stepper.stop();
      event.call("end", simulation);
    }
  }
  function tick(iterations2) {
    var i, n = nodes.length, node;
    if (iterations2 === void 0) iterations2 = 1;
    for (var k = 0; k < iterations2; ++k) {
      alpha += (alphaTarget - alpha) * alphaDecay;
      forces.forEach(function(force) {
        force(alpha);
      });
      for (i = 0; i < n; ++i) {
        node = nodes[i];
        if (node.fx == null) node.x += node.vx *= velocityDecay;
        else node.x = node.fx, node.vx = 0;
        if (node.fy == null) node.y += node.vy *= velocityDecay;
        else node.y = node.fy, node.vy = 0;
      }
    }
    return simulation;
  }
  function initializeNodes() {
    for (var i = 0, n = nodes.length, node; i < n; ++i) {
      node = nodes[i], node.index = i;
      if (node.fx != null) node.x = node.fx;
      if (node.fy != null) node.y = node.fy;
      if (isNaN(node.x) || isNaN(node.y)) {
        var radius = initialRadius * Math.sqrt(0.5 + i), angle2 = i * initialAngle;
        node.x = radius * Math.cos(angle2);
        node.y = radius * Math.sin(angle2);
      }
      if (isNaN(node.vx) || isNaN(node.vy)) {
        node.vx = node.vy = 0;
      }
    }
  }
  function initializeForce(force) {
    if (force.initialize) force.initialize(nodes, random);
    return force;
  }
  initializeNodes();
  return simulation = {
    tick,
    restart: function() {
      return stepper.restart(step), simulation;
    },
    stop: function() {
      return stepper.stop(), simulation;
    },
    nodes: function(_) {
      return arguments.length ? (nodes = _, initializeNodes(), forces.forEach(initializeForce), simulation) : nodes;
    },
    alpha: function(_) {
      return arguments.length ? (alpha = +_, simulation) : alpha;
    },
    alphaMin: function(_) {
      return arguments.length ? (alphaMin = +_, simulation) : alphaMin;
    },
    alphaDecay: function(_) {
      return arguments.length ? (alphaDecay = +_, simulation) : +alphaDecay;
    },
    alphaTarget: function(_) {
      return arguments.length ? (alphaTarget = +_, simulation) : alphaTarget;
    },
    velocityDecay: function(_) {
      return arguments.length ? (velocityDecay = 1 - _, simulation) : 1 - velocityDecay;
    },
    randomSource: function(_) {
      return arguments.length ? (random = _, forces.forEach(initializeForce), simulation) : random;
    },
    force: function(name, _) {
      return arguments.length > 1 ? (_ == null ? forces.delete(name) : forces.set(name, initializeForce(_)), simulation) : forces.get(name);
    },
    find: function(x2, y2, radius) {
      var i = 0, n = nodes.length, dx, dy, d2, node, closest;
      if (radius == null) radius = Infinity;
      else radius *= radius;
      for (i = 0; i < n; ++i) {
        node = nodes[i];
        dx = x2 - node.x;
        dy = y2 - node.y;
        d2 = dx * dx + dy * dy;
        if (d2 < radius) closest = node, radius = d2;
      }
      return closest;
    },
    on: function(name, _) {
      return arguments.length > 1 ? (event.on(name, _), simulation) : event.on(name);
    }
  };
}
function forceManyBody() {
  var nodes, node, random, alpha, strength = constant(-30), strengths, distanceMin2 = 1, distanceMax2 = Infinity, theta2 = 0.81;
  function force(_) {
    var i, n = nodes.length, tree2 = quadtree(nodes, x, y).visitAfter(accumulate);
    for (alpha = _, i = 0; i < n; ++i) node = nodes[i], tree2.visit(apply);
  }
  function initialize() {
    if (!nodes) return;
    var i, n = nodes.length, node2;
    strengths = new Array(n);
    for (i = 0; i < n; ++i) node2 = nodes[i], strengths[node2.index] = +strength(node2, i, nodes);
  }
  function accumulate(quad) {
    var strength2 = 0, q, c2, weight = 0, x2, y2, i;
    if (quad.length) {
      for (x2 = y2 = i = 0; i < 4; ++i) {
        if ((q = quad[i]) && (c2 = Math.abs(q.value))) {
          strength2 += q.value, weight += c2, x2 += c2 * q.x, y2 += c2 * q.y;
        }
      }
      quad.x = x2 / weight;
      quad.y = y2 / weight;
    } else {
      q = quad;
      q.x = q.data.x;
      q.y = q.data.y;
      do
        strength2 += strengths[q.data.index];
      while (q = q.next);
    }
    quad.value = strength2;
  }
  function apply(quad, x12, _, x2) {
    if (!quad.value) return true;
    var x3 = quad.x - node.x, y2 = quad.y - node.y, w = x2 - x12, l = x3 * x3 + y2 * y2;
    if (w * w / theta2 < l) {
      if (l < distanceMax2) {
        if (x3 === 0) x3 = jiggle(random), l += x3 * x3;
        if (y2 === 0) y2 = jiggle(random), l += y2 * y2;
        if (l < distanceMin2) l = Math.sqrt(distanceMin2 * l);
        node.vx += x3 * quad.value * alpha / l;
        node.vy += y2 * quad.value * alpha / l;
      }
      return true;
    } else if (quad.length || l >= distanceMax2) return;
    if (quad.data !== node || quad.next) {
      if (x3 === 0) x3 = jiggle(random), l += x3 * x3;
      if (y2 === 0) y2 = jiggle(random), l += y2 * y2;
      if (l < distanceMin2) l = Math.sqrt(distanceMin2 * l);
    }
    do
      if (quad.data !== node) {
        w = strengths[quad.data.index] * alpha / l;
        node.vx += x3 * w;
        node.vy += y2 * w;
      }
    while (quad = quad.next);
  }
  force.initialize = function(_nodes, _random) {
    nodes = _nodes;
    random = _random;
    initialize();
  };
  force.strength = function(_) {
    return arguments.length ? (strength = typeof _ === "function" ? _ : constant(+_), initialize(), force) : strength;
  };
  force.distanceMin = function(_) {
    return arguments.length ? (distanceMin2 = _ * _, force) : Math.sqrt(distanceMin2);
  };
  force.distanceMax = function(_) {
    return arguments.length ? (distanceMax2 = _ * _, force) : Math.sqrt(distanceMax2);
  };
  force.theta = function(_) {
    return arguments.length ? (theta2 = _ * _, force) : Math.sqrt(theta2);
  };
  return force;
}
function forceX(x2) {
  var strength = constant(0.1), nodes, strengths, xz;
  if (typeof x2 !== "function") x2 = constant(x2 == null ? 0 : +x2);
  function force(alpha) {
    for (var i = 0, n = nodes.length, node; i < n; ++i) {
      node = nodes[i], node.vx += (xz[i] - node.x) * strengths[i] * alpha;
    }
  }
  function initialize() {
    if (!nodes) return;
    var i, n = nodes.length;
    strengths = new Array(n);
    xz = new Array(n);
    for (i = 0; i < n; ++i) {
      strengths[i] = isNaN(xz[i] = +x2(nodes[i], i, nodes)) ? 0 : +strength(nodes[i], i, nodes);
    }
  }
  force.initialize = function(_) {
    nodes = _;
    initialize();
  };
  force.strength = function(_) {
    return arguments.length ? (strength = typeof _ === "function" ? _ : constant(+_), initialize(), force) : strength;
  };
  force.x = function(_) {
    return arguments.length ? (x2 = typeof _ === "function" ? _ : constant(+_), initialize(), force) : x2;
  };
  return force;
}
function forceY(y2) {
  var strength = constant(0.1), nodes, strengths, yz;
  if (typeof y2 !== "function") y2 = constant(y2 == null ? 0 : +y2);
  function force(alpha) {
    for (var i = 0, n = nodes.length, node; i < n; ++i) {
      node = nodes[i], node.vy += (yz[i] - node.y) * strengths[i] * alpha;
    }
  }
  function initialize() {
    if (!nodes) return;
    var i, n = nodes.length;
    strengths = new Array(n);
    yz = new Array(n);
    for (i = 0; i < n; ++i) {
      strengths[i] = isNaN(yz[i] = +y2(nodes[i], i, nodes)) ? 0 : +strength(nodes[i], i, nodes);
    }
  }
  force.initialize = function(_) {
    nodes = _;
    initialize();
  };
  force.strength = function(_) {
    return arguments.length ? (strength = typeof _ === "function" ? _ : constant(+_), initialize(), force) : strength;
  };
  force.y = function(_) {
    return arguments.length ? (y2 = typeof _ === "function" ? _ : constant(+_), initialize(), force) : y2;
  };
  return force;
}
var epsilon$1 = 1e-6;
var epsilon2 = 1e-12;
var pi$1 = Math.PI;
var halfPi$1 = pi$1 / 2;
var quarterPi = pi$1 / 4;
var tau = pi$1 * 2;
var degrees = 180 / pi$1;
var radians = pi$1 / 180;
var abs$1 = Math.abs;
var atan = Math.atan;
var atan2 = Math.atan2;
var cos$1 = Math.cos;
var ceil = Math.ceil;
var exp = Math.exp;
var hypot = Math.hypot;
var log$1 = Math.log;
var pow$1 = Math.pow;
var sin$1 = Math.sin;
var sign = Math.sign || function(x2) {
  return x2 > 0 ? 1 : x2 < 0 ? -1 : 0;
};
var sqrt$2 = Math.sqrt;
var tan = Math.tan;
function acos(x2) {
  return x2 > 1 ? 0 : x2 < -1 ? pi$1 : Math.acos(x2);
}
function asin$1(x2) {
  return x2 > 1 ? halfPi$1 : x2 < -1 ? -halfPi$1 : Math.asin(x2);
}
function noop() {
}
function streamGeometry(geometry, stream) {
  if (geometry && streamGeometryType.hasOwnProperty(geometry.type)) {
    streamGeometryType[geometry.type](geometry, stream);
  }
}
var streamObjectType = {
  Feature: function(object2, stream) {
    streamGeometry(object2.geometry, stream);
  },
  FeatureCollection: function(object2, stream) {
    var features = object2.features, i = -1, n = features.length;
    while (++i < n) streamGeometry(features[i].geometry, stream);
  }
};
var streamGeometryType = {
  Sphere: function(object2, stream) {
    stream.sphere();
  },
  Point: function(object2, stream) {
    object2 = object2.coordinates;
    stream.point(object2[0], object2[1], object2[2]);
  },
  MultiPoint: function(object2, stream) {
    var coordinates = object2.coordinates, i = -1, n = coordinates.length;
    while (++i < n) object2 = coordinates[i], stream.point(object2[0], object2[1], object2[2]);
  },
  LineString: function(object2, stream) {
    streamLine(object2.coordinates, stream, 0);
  },
  MultiLineString: function(object2, stream) {
    var coordinates = object2.coordinates, i = -1, n = coordinates.length;
    while (++i < n) streamLine(coordinates[i], stream, 0);
  },
  Polygon: function(object2, stream) {
    streamPolygon(object2.coordinates, stream);
  },
  MultiPolygon: function(object2, stream) {
    var coordinates = object2.coordinates, i = -1, n = coordinates.length;
    while (++i < n) streamPolygon(coordinates[i], stream);
  },
  GeometryCollection: function(object2, stream) {
    var geometries = object2.geometries, i = -1, n = geometries.length;
    while (++i < n) streamGeometry(geometries[i], stream);
  }
};
function streamLine(coordinates, stream, closed) {
  var i = -1, n = coordinates.length - closed, coordinate;
  stream.lineStart();
  while (++i < n) coordinate = coordinates[i], stream.point(coordinate[0], coordinate[1], coordinate[2]);
  stream.lineEnd();
}
function streamPolygon(coordinates, stream) {
  var i = -1, n = coordinates.length;
  stream.polygonStart();
  while (++i < n) streamLine(coordinates[i], stream, 1);
  stream.polygonEnd();
}
function geoStream(object2, stream) {
  if (object2 && streamObjectType.hasOwnProperty(object2.type)) {
    streamObjectType[object2.type](object2, stream);
  } else {
    streamGeometry(object2, stream);
  }
}
var areaRingSum$1 = new Adder();
var areaSum$1 = new Adder(), lambda00$2, phi00$2, lambda0$1, cosPhi0, sinPhi0;
var areaStream$1 = {
  point: noop,
  lineStart: noop,
  lineEnd: noop,
  polygonStart: function() {
    areaRingSum$1 = new Adder();
    areaStream$1.lineStart = areaRingStart$1;
    areaStream$1.lineEnd = areaRingEnd$1;
  },
  polygonEnd: function() {
    var areaRing = +areaRingSum$1;
    areaSum$1.add(areaRing < 0 ? tau + areaRing : areaRing);
    this.lineStart = this.lineEnd = this.point = noop;
  },
  sphere: function() {
    areaSum$1.add(tau);
  }
};
function areaRingStart$1() {
  areaStream$1.point = areaPointFirst$1;
}
function areaRingEnd$1() {
  areaPoint$1(lambda00$2, phi00$2);
}
function areaPointFirst$1(lambda, phi2) {
  areaStream$1.point = areaPoint$1;
  lambda00$2 = lambda, phi00$2 = phi2;
  lambda *= radians, phi2 *= radians;
  lambda0$1 = lambda, cosPhi0 = cos$1(phi2 = phi2 / 2 + quarterPi), sinPhi0 = sin$1(phi2);
}
function areaPoint$1(lambda, phi2) {
  lambda *= radians, phi2 *= radians;
  phi2 = phi2 / 2 + quarterPi;
  var dLambda = lambda - lambda0$1, sdLambda = dLambda >= 0 ? 1 : -1, adLambda = sdLambda * dLambda, cosPhi = cos$1(phi2), sinPhi = sin$1(phi2), k = sinPhi0 * sinPhi, u2 = cosPhi0 * cosPhi + k * cos$1(adLambda), v = k * sdLambda * sin$1(adLambda);
  areaRingSum$1.add(atan2(v, u2));
  lambda0$1 = lambda, cosPhi0 = cosPhi, sinPhi0 = sinPhi;
}
function geoArea$1(object2) {
  areaSum$1 = new Adder();
  geoStream(object2, areaStream$1);
  return areaSum$1 * 2;
}
function spherical(cartesian2) {
  return [atan2(cartesian2[1], cartesian2[0]), asin$1(cartesian2[2])];
}
function cartesian(spherical2) {
  var lambda = spherical2[0], phi2 = spherical2[1], cosPhi = cos$1(phi2);
  return [cosPhi * cos$1(lambda), cosPhi * sin$1(lambda), sin$1(phi2)];
}
function cartesianDot(a2, b) {
  return a2[0] * b[0] + a2[1] * b[1] + a2[2] * b[2];
}
function cartesianCross(a2, b) {
  return [a2[1] * b[2] - a2[2] * b[1], a2[2] * b[0] - a2[0] * b[2], a2[0] * b[1] - a2[1] * b[0]];
}
function cartesianAddInPlace(a2, b) {
  a2[0] += b[0], a2[1] += b[1], a2[2] += b[2];
}
function cartesianScale(vector, k) {
  return [vector[0] * k, vector[1] * k, vector[2] * k];
}
function cartesianNormalizeInPlace(d) {
  var l = sqrt$2(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
  d[0] /= l, d[1] /= l, d[2] /= l;
}
var lambda0, phi0, lambda1, phi1, lambda2, lambda00$1, phi00$1, p0, deltaSum, ranges, range;
var boundsStream$1 = {
  point: boundsPoint$1,
  lineStart: boundsLineStart,
  lineEnd: boundsLineEnd,
  polygonStart: function() {
    boundsStream$1.point = boundsRingPoint;
    boundsStream$1.lineStart = boundsRingStart;
    boundsStream$1.lineEnd = boundsRingEnd;
    deltaSum = new Adder();
    areaStream$1.polygonStart();
  },
  polygonEnd: function() {
    areaStream$1.polygonEnd();
    boundsStream$1.point = boundsPoint$1;
    boundsStream$1.lineStart = boundsLineStart;
    boundsStream$1.lineEnd = boundsLineEnd;
    if (areaRingSum$1 < 0) lambda0 = -(lambda1 = 180), phi0 = -(phi1 = 90);
    else if (deltaSum > epsilon$1) phi1 = 90;
    else if (deltaSum < -epsilon$1) phi0 = -90;
    range[0] = lambda0, range[1] = lambda1;
  },
  sphere: function() {
    lambda0 = -(lambda1 = 180), phi0 = -(phi1 = 90);
  }
};
function boundsPoint$1(lambda, phi2) {
  ranges.push(range = [lambda0 = lambda, lambda1 = lambda]);
  if (phi2 < phi0) phi0 = phi2;
  if (phi2 > phi1) phi1 = phi2;
}
function linePoint(lambda, phi2) {
  var p = cartesian([lambda * radians, phi2 * radians]);
  if (p0) {
    var normal = cartesianCross(p0, p), equatorial = [normal[1], -normal[0], 0], inflection = cartesianCross(equatorial, normal);
    cartesianNormalizeInPlace(inflection);
    inflection = spherical(inflection);
    var delta = lambda - lambda2, sign2 = delta > 0 ? 1 : -1, lambdai = inflection[0] * degrees * sign2, phii, antimeridian = abs$1(delta) > 180;
    if (antimeridian ^ (sign2 * lambda2 < lambdai && lambdai < sign2 * lambda)) {
      phii = inflection[1] * degrees;
      if (phii > phi1) phi1 = phii;
    } else if (lambdai = (lambdai + 360) % 360 - 180, antimeridian ^ (sign2 * lambda2 < lambdai && lambdai < sign2 * lambda)) {
      phii = -inflection[1] * degrees;
      if (phii < phi0) phi0 = phii;
    } else {
      if (phi2 < phi0) phi0 = phi2;
      if (phi2 > phi1) phi1 = phi2;
    }
    if (antimeridian) {
      if (lambda < lambda2) {
        if (angle(lambda0, lambda) > angle(lambda0, lambda1)) lambda1 = lambda;
      } else {
        if (angle(lambda, lambda1) > angle(lambda0, lambda1)) lambda0 = lambda;
      }
    } else {
      if (lambda1 >= lambda0) {
        if (lambda < lambda0) lambda0 = lambda;
        if (lambda > lambda1) lambda1 = lambda;
      } else {
        if (lambda > lambda2) {
          if (angle(lambda0, lambda) > angle(lambda0, lambda1)) lambda1 = lambda;
        } else {
          if (angle(lambda, lambda1) > angle(lambda0, lambda1)) lambda0 = lambda;
        }
      }
    }
  } else {
    ranges.push(range = [lambda0 = lambda, lambda1 = lambda]);
  }
  if (phi2 < phi0) phi0 = phi2;
  if (phi2 > phi1) phi1 = phi2;
  p0 = p, lambda2 = lambda;
}
function boundsLineStart() {
  boundsStream$1.point = linePoint;
}
function boundsLineEnd() {
  range[0] = lambda0, range[1] = lambda1;
  boundsStream$1.point = boundsPoint$1;
  p0 = null;
}
function boundsRingPoint(lambda, phi2) {
  if (p0) {
    var delta = lambda - lambda2;
    deltaSum.add(abs$1(delta) > 180 ? delta + (delta > 0 ? 360 : -360) : delta);
  } else {
    lambda00$1 = lambda, phi00$1 = phi2;
  }
  areaStream$1.point(lambda, phi2);
  linePoint(lambda, phi2);
}
function boundsRingStart() {
  areaStream$1.lineStart();
}
function boundsRingEnd() {
  boundsRingPoint(lambda00$1, phi00$1);
  areaStream$1.lineEnd();
  if (abs$1(deltaSum) > epsilon$1) lambda0 = -(lambda1 = 180);
  range[0] = lambda0, range[1] = lambda1;
  p0 = null;
}
function angle(lambda02, lambda12) {
  return (lambda12 -= lambda02) < 0 ? lambda12 + 360 : lambda12;
}
function rangeCompare(a2, b) {
  return a2[0] - b[0];
}
function rangeContains(range2, x2) {
  return range2[0] <= range2[1] ? range2[0] <= x2 && x2 <= range2[1] : x2 < range2[0] || range2[1] < x2;
}
function geoBounds$1(feature2) {
  var i, n, a2, b, merged, deltaMax, delta;
  phi1 = lambda1 = -(lambda0 = phi0 = Infinity);
  ranges = [];
  geoStream(feature2, boundsStream$1);
  if (n = ranges.length) {
    ranges.sort(rangeCompare);
    for (i = 1, a2 = ranges[0], merged = [a2]; i < n; ++i) {
      b = ranges[i];
      if (rangeContains(a2, b[0]) || rangeContains(a2, b[1])) {
        if (angle(a2[0], b[1]) > angle(a2[0], a2[1])) a2[1] = b[1];
        if (angle(b[0], a2[1]) > angle(a2[0], a2[1])) a2[0] = b[0];
      } else {
        merged.push(a2 = b);
      }
    }
    for (deltaMax = -Infinity, n = merged.length - 1, i = 0, a2 = merged[n]; i <= n; a2 = b, ++i) {
      b = merged[i];
      if ((delta = angle(a2[1], b[0])) > deltaMax) deltaMax = delta, lambda0 = b[0], lambda1 = a2[1];
    }
  }
  ranges = range = null;
  return lambda0 === Infinity || phi0 === Infinity ? [[NaN, NaN], [NaN, NaN]] : [[lambda0, phi0], [lambda1, phi1]];
}
var W0, W1, X0$1, Y0$1, Z0$1, X1$1, Y1$1, Z1$1, X2$1, Y2$1, Z2$1, lambda00, phi00, x0$4, y0$4, z0;
var centroidStream$1 = {
  sphere: noop,
  point: centroidPoint$1,
  lineStart: centroidLineStart$1,
  lineEnd: centroidLineEnd$1,
  polygonStart: function() {
    centroidStream$1.lineStart = centroidRingStart$1;
    centroidStream$1.lineEnd = centroidRingEnd$1;
  },
  polygonEnd: function() {
    centroidStream$1.lineStart = centroidLineStart$1;
    centroidStream$1.lineEnd = centroidLineEnd$1;
  }
};
function centroidPoint$1(lambda, phi2) {
  lambda *= radians, phi2 *= radians;
  var cosPhi = cos$1(phi2);
  centroidPointCartesian(cosPhi * cos$1(lambda), cosPhi * sin$1(lambda), sin$1(phi2));
}
function centroidPointCartesian(x2, y2, z) {
  ++W0;
  X0$1 += (x2 - X0$1) / W0;
  Y0$1 += (y2 - Y0$1) / W0;
  Z0$1 += (z - Z0$1) / W0;
}
function centroidLineStart$1() {
  centroidStream$1.point = centroidLinePointFirst;
}
function centroidLinePointFirst(lambda, phi2) {
  lambda *= radians, phi2 *= radians;
  var cosPhi = cos$1(phi2);
  x0$4 = cosPhi * cos$1(lambda);
  y0$4 = cosPhi * sin$1(lambda);
  z0 = sin$1(phi2);
  centroidStream$1.point = centroidLinePoint;
  centroidPointCartesian(x0$4, y0$4, z0);
}
function centroidLinePoint(lambda, phi2) {
  lambda *= radians, phi2 *= radians;
  var cosPhi = cos$1(phi2), x2 = cosPhi * cos$1(lambda), y2 = cosPhi * sin$1(lambda), z = sin$1(phi2), w = atan2(sqrt$2((w = y0$4 * z - z0 * y2) * w + (w = z0 * x2 - x0$4 * z) * w + (w = x0$4 * y2 - y0$4 * x2) * w), x0$4 * x2 + y0$4 * y2 + z0 * z);
  W1 += w;
  X1$1 += w * (x0$4 + (x0$4 = x2));
  Y1$1 += w * (y0$4 + (y0$4 = y2));
  Z1$1 += w * (z0 + (z0 = z));
  centroidPointCartesian(x0$4, y0$4, z0);
}
function centroidLineEnd$1() {
  centroidStream$1.point = centroidPoint$1;
}
function centroidRingStart$1() {
  centroidStream$1.point = centroidRingPointFirst;
}
function centroidRingEnd$1() {
  centroidRingPoint(lambda00, phi00);
  centroidStream$1.point = centroidPoint$1;
}
function centroidRingPointFirst(lambda, phi2) {
  lambda00 = lambda, phi00 = phi2;
  lambda *= radians, phi2 *= radians;
  centroidStream$1.point = centroidRingPoint;
  var cosPhi = cos$1(phi2);
  x0$4 = cosPhi * cos$1(lambda);
  y0$4 = cosPhi * sin$1(lambda);
  z0 = sin$1(phi2);
  centroidPointCartesian(x0$4, y0$4, z0);
}
function centroidRingPoint(lambda, phi2) {
  lambda *= radians, phi2 *= radians;
  var cosPhi = cos$1(phi2), x2 = cosPhi * cos$1(lambda), y2 = cosPhi * sin$1(lambda), z = sin$1(phi2), cx = y0$4 * z - z0 * y2, cy = z0 * x2 - x0$4 * z, cz = x0$4 * y2 - y0$4 * x2, m2 = hypot(cx, cy, cz), w = asin$1(m2), v = m2 && -w / m2;
  X2$1.add(v * cx);
  Y2$1.add(v * cy);
  Z2$1.add(v * cz);
  W1 += w;
  X1$1 += w * (x0$4 + (x0$4 = x2));
  Y1$1 += w * (y0$4 + (y0$4 = y2));
  Z1$1 += w * (z0 + (z0 = z));
  centroidPointCartesian(x0$4, y0$4, z0);
}
function geoCentroid$1(object2) {
  W0 = W1 = X0$1 = Y0$1 = Z0$1 = X1$1 = Y1$1 = Z1$1 = 0;
  X2$1 = new Adder();
  Y2$1 = new Adder();
  Z2$1 = new Adder();
  geoStream(object2, centroidStream$1);
  var x2 = +X2$1, y2 = +Y2$1, z = +Z2$1, m2 = hypot(x2, y2, z);
  if (m2 < epsilon2) {
    x2 = X1$1, y2 = Y1$1, z = Z1$1;
    if (W1 < epsilon$1) x2 = X0$1, y2 = Y0$1, z = Z0$1;
    m2 = hypot(x2, y2, z);
    if (m2 < epsilon2) return [NaN, NaN];
  }
  return [atan2(y2, x2) * degrees, asin$1(z / m2) * degrees];
}
function compose(a2, b) {
  function compose2(x2, y2) {
    return x2 = a2(x2, y2), b(x2[0], x2[1]);
  }
  if (a2.invert && b.invert) compose2.invert = function(x2, y2) {
    return x2 = b.invert(x2, y2), x2 && a2.invert(x2[0], x2[1]);
  };
  return compose2;
}
function rotationIdentity(lambda, phi2) {
  if (abs$1(lambda) > pi$1) lambda -= Math.round(lambda / tau) * tau;
  return [lambda, phi2];
}
rotationIdentity.invert = rotationIdentity;
function rotateRadians(deltaLambda, deltaPhi, deltaGamma) {
  return (deltaLambda %= tau) ? deltaPhi || deltaGamma ? compose(rotationLambda(deltaLambda), rotationPhiGamma(deltaPhi, deltaGamma)) : rotationLambda(deltaLambda) : deltaPhi || deltaGamma ? rotationPhiGamma(deltaPhi, deltaGamma) : rotationIdentity;
}
function forwardRotationLambda(deltaLambda) {
  return function(lambda, phi2) {
    lambda += deltaLambda;
    if (abs$1(lambda) > pi$1) lambda -= Math.round(lambda / tau) * tau;
    return [lambda, phi2];
  };
}
function rotationLambda(deltaLambda) {
  var rotation2 = forwardRotationLambda(deltaLambda);
  rotation2.invert = forwardRotationLambda(-deltaLambda);
  return rotation2;
}
function rotationPhiGamma(deltaPhi, deltaGamma) {
  var cosDeltaPhi = cos$1(deltaPhi), sinDeltaPhi = sin$1(deltaPhi), cosDeltaGamma = cos$1(deltaGamma), sinDeltaGamma = sin$1(deltaGamma);
  function rotation2(lambda, phi2) {
    var cosPhi = cos$1(phi2), x2 = cos$1(lambda) * cosPhi, y2 = sin$1(lambda) * cosPhi, z = sin$1(phi2), k = z * cosDeltaPhi + x2 * sinDeltaPhi;
    return [
      atan2(y2 * cosDeltaGamma - k * sinDeltaGamma, x2 * cosDeltaPhi - z * sinDeltaPhi),
      asin$1(k * cosDeltaGamma + y2 * sinDeltaGamma)
    ];
  }
  rotation2.invert = function(lambda, phi2) {
    var cosPhi = cos$1(phi2), x2 = cos$1(lambda) * cosPhi, y2 = sin$1(lambda) * cosPhi, z = sin$1(phi2), k = z * cosDeltaGamma - y2 * sinDeltaGamma;
    return [
      atan2(y2 * cosDeltaGamma + z * sinDeltaGamma, x2 * cosDeltaPhi + k * sinDeltaPhi),
      asin$1(k * cosDeltaPhi - x2 * sinDeltaPhi)
    ];
  };
  return rotation2;
}
function rotation(rotate) {
  rotate = rotateRadians(rotate[0] * radians, rotate[1] * radians, rotate.length > 2 ? rotate[2] * radians : 0);
  function forward(coordinates) {
    coordinates = rotate(coordinates[0] * radians, coordinates[1] * radians);
    return coordinates[0] *= degrees, coordinates[1] *= degrees, coordinates;
  }
  forward.invert = function(coordinates) {
    coordinates = rotate.invert(coordinates[0] * radians, coordinates[1] * radians);
    return coordinates[0] *= degrees, coordinates[1] *= degrees, coordinates;
  };
  return forward;
}
function circleStream(stream, radius, delta, direction, t0, t1) {
  if (!delta) return;
  var cosRadius = cos$1(radius), sinRadius = sin$1(radius), step = direction * delta;
  if (t0 == null) {
    t0 = radius + direction * tau;
    t1 = radius - step / 2;
  } else {
    t0 = circleRadius(cosRadius, t0);
    t1 = circleRadius(cosRadius, t1);
    if (direction > 0 ? t0 < t1 : t0 > t1) t0 += direction * tau;
  }
  for (var point, t = t0; direction > 0 ? t > t1 : t < t1; t -= step) {
    point = spherical([cosRadius, -sinRadius * cos$1(t), -sinRadius * sin$1(t)]);
    stream.point(point[0], point[1]);
  }
}
function circleRadius(cosRadius, point) {
  point = cartesian(point), point[0] -= cosRadius;
  cartesianNormalizeInPlace(point);
  var radius = acos(-point[1]);
  return ((-point[2] < 0 ? -radius : radius) + tau - epsilon$1) % tau;
}
function clipBuffer() {
  var lines = [], line2;
  return {
    point: function(x2, y2, m2) {
      line2.push([x2, y2, m2]);
    },
    lineStart: function() {
      lines.push(line2 = []);
    },
    lineEnd: noop,
    rejoin: function() {
      if (lines.length > 1) lines.push(lines.pop().concat(lines.shift()));
    },
    result: function() {
      var result = lines;
      lines = [];
      line2 = null;
      return result;
    }
  };
}
function pointEqual(a2, b) {
  return abs$1(a2[0] - b[0]) < epsilon$1 && abs$1(a2[1] - b[1]) < epsilon$1;
}
function Intersection(point, points, other, entry) {
  this.x = point;
  this.z = points;
  this.o = other;
  this.e = entry;
  this.v = false;
  this.n = this.p = null;
}
function clipRejoin(segments, compareIntersection2, startInside, interpolate, stream) {
  var subject = [], clip2 = [], i, n;
  segments.forEach(function(segment) {
    if ((n2 = segment.length - 1) <= 0) return;
    var n2, p02 = segment[0], p1 = segment[n2], x2;
    if (pointEqual(p02, p1)) {
      if (!p02[2] && !p1[2]) {
        stream.lineStart();
        for (i = 0; i < n2; ++i) stream.point((p02 = segment[i])[0], p02[1]);
        stream.lineEnd();
        return;
      }
      p1[0] += 2 * epsilon$1;
    }
    subject.push(x2 = new Intersection(p02, segment, null, true));
    clip2.push(x2.o = new Intersection(p02, null, x2, false));
    subject.push(x2 = new Intersection(p1, segment, null, false));
    clip2.push(x2.o = new Intersection(p1, null, x2, true));
  });
  if (!subject.length) return;
  clip2.sort(compareIntersection2);
  link(subject);
  link(clip2);
  for (i = 0, n = clip2.length; i < n; ++i) {
    clip2[i].e = startInside = !startInside;
  }
  var start = subject[0], points, point;
  while (1) {
    var current = start, isSubject = true;
    while (current.v) if ((current = current.n) === start) return;
    points = current.z;
    stream.lineStart();
    do {
      current.v = current.o.v = true;
      if (current.e) {
        if (isSubject) {
          for (i = 0, n = points.length; i < n; ++i) stream.point((point = points[i])[0], point[1]);
        } else {
          interpolate(current.x, current.n.x, 1, stream);
        }
        current = current.n;
      } else {
        if (isSubject) {
          points = current.p.z;
          for (i = points.length - 1; i >= 0; --i) stream.point((point = points[i])[0], point[1]);
        } else {
          interpolate(current.x, current.p.x, -1, stream);
        }
        current = current.p;
      }
      current = current.o;
      points = current.z;
      isSubject = !isSubject;
    } while (!current.v);
    stream.lineEnd();
  }
}
function link(array2) {
  if (!(n = array2.length)) return;
  var n, i = 0, a2 = array2[0], b;
  while (++i < n) {
    a2.n = b = array2[i];
    b.p = a2;
    a2 = b;
  }
  a2.n = b = array2[0];
  b.p = a2;
}
function longitude(point) {
  return abs$1(point[0]) <= pi$1 ? point[0] : sign(point[0]) * ((abs$1(point[0]) + pi$1) % tau - pi$1);
}
function polygonContains(polygon, point) {
  var lambda = longitude(point), phi2 = point[1], sinPhi = sin$1(phi2), normal = [sin$1(lambda), -cos$1(lambda), 0], angle2 = 0, winding = 0;
  var sum2 = new Adder();
  if (sinPhi === 1) phi2 = halfPi$1 + epsilon$1;
  else if (sinPhi === -1) phi2 = -halfPi$1 - epsilon$1;
  for (var i = 0, n = polygon.length; i < n; ++i) {
    if (!(m2 = (ring = polygon[i]).length)) continue;
    var ring, m2, point0 = ring[m2 - 1], lambda02 = longitude(point0), phi02 = point0[1] / 2 + quarterPi, sinPhi02 = sin$1(phi02), cosPhi02 = cos$1(phi02);
    for (var j = 0; j < m2; ++j, lambda02 = lambda12, sinPhi02 = sinPhi1, cosPhi02 = cosPhi1, point0 = point1) {
      var point1 = ring[j], lambda12 = longitude(point1), phi12 = point1[1] / 2 + quarterPi, sinPhi1 = sin$1(phi12), cosPhi1 = cos$1(phi12), delta = lambda12 - lambda02, sign2 = delta >= 0 ? 1 : -1, absDelta = sign2 * delta, antimeridian = absDelta > pi$1, k = sinPhi02 * sinPhi1;
      sum2.add(atan2(k * sign2 * sin$1(absDelta), cosPhi02 * cosPhi1 + k * cos$1(absDelta)));
      angle2 += antimeridian ? delta + sign2 * tau : delta;
      if (antimeridian ^ lambda02 >= lambda ^ lambda12 >= lambda) {
        var arc = cartesianCross(cartesian(point0), cartesian(point1));
        cartesianNormalizeInPlace(arc);
        var intersection2 = cartesianCross(normal, arc);
        cartesianNormalizeInPlace(intersection2);
        var phiArc = (antimeridian ^ delta >= 0 ? -1 : 1) * asin$1(intersection2[2]);
        if (phi2 > phiArc || phi2 === phiArc && (arc[0] || arc[1])) {
          winding += antimeridian ^ delta >= 0 ? 1 : -1;
        }
      }
    }
  }
  return (angle2 < -epsilon$1 || angle2 < epsilon$1 && sum2 < -epsilon2) ^ winding & 1;
}
function clip(pointVisible, clipLine2, interpolate, start) {
  return function(sink) {
    var line2 = clipLine2(sink), ringBuffer = clipBuffer(), ringSink = clipLine2(ringBuffer), polygonStarted = false, polygon, segments, ring;
    var clip2 = {
      point,
      lineStart,
      lineEnd,
      polygonStart: function() {
        clip2.point = pointRing;
        clip2.lineStart = ringStart;
        clip2.lineEnd = ringEnd;
        segments = [];
        polygon = [];
      },
      polygonEnd: function() {
        clip2.point = point;
        clip2.lineStart = lineStart;
        clip2.lineEnd = lineEnd;
        segments = merge(segments);
        var startInside = polygonContains(polygon, start);
        if (segments.length) {
          if (!polygonStarted) sink.polygonStart(), polygonStarted = true;
          clipRejoin(segments, compareIntersection, startInside, interpolate, sink);
        } else if (startInside) {
          if (!polygonStarted) sink.polygonStart(), polygonStarted = true;
          sink.lineStart();
          interpolate(null, null, 1, sink);
          sink.lineEnd();
        }
        if (polygonStarted) sink.polygonEnd(), polygonStarted = false;
        segments = polygon = null;
      },
      sphere: function() {
        sink.polygonStart();
        sink.lineStart();
        interpolate(null, null, 1, sink);
        sink.lineEnd();
        sink.polygonEnd();
      }
    };
    function point(lambda, phi2) {
      if (pointVisible(lambda, phi2)) sink.point(lambda, phi2);
    }
    function pointLine(lambda, phi2) {
      line2.point(lambda, phi2);
    }
    function lineStart() {
      clip2.point = pointLine;
      line2.lineStart();
    }
    function lineEnd() {
      clip2.point = point;
      line2.lineEnd();
    }
    function pointRing(lambda, phi2) {
      ring.push([lambda, phi2]);
      ringSink.point(lambda, phi2);
    }
    function ringStart() {
      ringSink.lineStart();
      ring = [];
    }
    function ringEnd() {
      pointRing(ring[0][0], ring[0][1]);
      ringSink.lineEnd();
      var clean = ringSink.clean(), ringSegments = ringBuffer.result(), i, n = ringSegments.length, m2, segment, point2;
      ring.pop();
      polygon.push(ring);
      ring = null;
      if (!n) return;
      if (clean & 1) {
        segment = ringSegments[0];
        if ((m2 = segment.length - 1) > 0) {
          if (!polygonStarted) sink.polygonStart(), polygonStarted = true;
          sink.lineStart();
          for (i = 0; i < m2; ++i) sink.point((point2 = segment[i])[0], point2[1]);
          sink.lineEnd();
        }
        return;
      }
      if (n > 1 && clean & 2) ringSegments.push(ringSegments.pop().concat(ringSegments.shift()));
      segments.push(ringSegments.filter(validSegment));
    }
    return clip2;
  };
}
function validSegment(segment) {
  return segment.length > 1;
}
function compareIntersection(a2, b) {
  return ((a2 = a2.x)[0] < 0 ? a2[1] - halfPi$1 - epsilon$1 : halfPi$1 - a2[1]) - ((b = b.x)[0] < 0 ? b[1] - halfPi$1 - epsilon$1 : halfPi$1 - b[1]);
}
const clipAntimeridian = clip(
  function() {
    return true;
  },
  clipAntimeridianLine,
  clipAntimeridianInterpolate,
  [-pi$1, -halfPi$1]
);
function clipAntimeridianLine(stream) {
  var lambda02 = NaN, phi02 = NaN, sign0 = NaN, clean;
  return {
    lineStart: function() {
      stream.lineStart();
      clean = 1;
    },
    point: function(lambda12, phi12) {
      var sign1 = lambda12 > 0 ? pi$1 : -pi$1, delta = abs$1(lambda12 - lambda02);
      if (abs$1(delta - pi$1) < epsilon$1) {
        stream.point(lambda02, phi02 = (phi02 + phi12) / 2 > 0 ? halfPi$1 : -halfPi$1);
        stream.point(sign0, phi02);
        stream.lineEnd();
        stream.lineStart();
        stream.point(sign1, phi02);
        stream.point(lambda12, phi02);
        clean = 0;
      } else if (sign0 !== sign1 && delta >= pi$1) {
        if (abs$1(lambda02 - sign0) < epsilon$1) lambda02 -= sign0 * epsilon$1;
        if (abs$1(lambda12 - sign1) < epsilon$1) lambda12 -= sign1 * epsilon$1;
        phi02 = clipAntimeridianIntersect(lambda02, phi02, lambda12, phi12);
        stream.point(sign0, phi02);
        stream.lineEnd();
        stream.lineStart();
        stream.point(sign1, phi02);
        clean = 0;
      }
      stream.point(lambda02 = lambda12, phi02 = phi12);
      sign0 = sign1;
    },
    lineEnd: function() {
      stream.lineEnd();
      lambda02 = phi02 = NaN;
    },
    clean: function() {
      return 2 - clean;
    }
  };
}
function clipAntimeridianIntersect(lambda02, phi02, lambda12, phi12) {
  var cosPhi02, cosPhi1, sinLambda0Lambda1 = sin$1(lambda02 - lambda12);
  return abs$1(sinLambda0Lambda1) > epsilon$1 ? atan((sin$1(phi02) * (cosPhi1 = cos$1(phi12)) * sin$1(lambda12) - sin$1(phi12) * (cosPhi02 = cos$1(phi02)) * sin$1(lambda02)) / (cosPhi02 * cosPhi1 * sinLambda0Lambda1)) : (phi02 + phi12) / 2;
}
function clipAntimeridianInterpolate(from, to, direction, stream) {
  var phi2;
  if (from == null) {
    phi2 = direction * halfPi$1;
    stream.point(-pi$1, phi2);
    stream.point(0, phi2);
    stream.point(pi$1, phi2);
    stream.point(pi$1, 0);
    stream.point(pi$1, -phi2);
    stream.point(0, -phi2);
    stream.point(-pi$1, -phi2);
    stream.point(-pi$1, 0);
    stream.point(-pi$1, phi2);
  } else if (abs$1(from[0] - to[0]) > epsilon$1) {
    var lambda = from[0] < to[0] ? pi$1 : -pi$1;
    phi2 = direction * lambda / 2;
    stream.point(-lambda, phi2);
    stream.point(0, phi2);
    stream.point(lambda, phi2);
  } else {
    stream.point(to[0], to[1]);
  }
}
function clipCircle(radius) {
  var cr = cos$1(radius), delta = 2 * radians, smallRadius = cr > 0, notHemisphere = abs$1(cr) > epsilon$1;
  function interpolate(from, to, direction, stream) {
    circleStream(stream, radius, delta, direction, from, to);
  }
  function visible(lambda, phi2) {
    return cos$1(lambda) * cos$1(phi2) > cr;
  }
  function clipLine2(stream) {
    var point0, c0, v0, v00, clean;
    return {
      lineStart: function() {
        v00 = v0 = false;
        clean = 1;
      },
      point: function(lambda, phi2) {
        var point1 = [lambda, phi2], point2, v = visible(lambda, phi2), c2 = smallRadius ? v ? 0 : code(lambda, phi2) : v ? code(lambda + (lambda < 0 ? pi$1 : -pi$1), phi2) : 0;
        if (!point0 && (v00 = v0 = v)) stream.lineStart();
        if (v !== v0) {
          point2 = intersect(point0, point1);
          if (!point2 || pointEqual(point0, point2) || pointEqual(point1, point2))
            point1[2] = 1;
        }
        if (v !== v0) {
          clean = 0;
          if (v) {
            stream.lineStart();
            point2 = intersect(point1, point0);
            stream.point(point2[0], point2[1]);
          } else {
            point2 = intersect(point0, point1);
            stream.point(point2[0], point2[1], 2);
            stream.lineEnd();
          }
          point0 = point2;
        } else if (notHemisphere && point0 && smallRadius ^ v) {
          var t;
          if (!(c2 & c0) && (t = intersect(point1, point0, true))) {
            clean = 0;
            if (smallRadius) {
              stream.lineStart();
              stream.point(t[0][0], t[0][1]);
              stream.point(t[1][0], t[1][1]);
              stream.lineEnd();
            } else {
              stream.point(t[1][0], t[1][1]);
              stream.lineEnd();
              stream.lineStart();
              stream.point(t[0][0], t[0][1], 3);
            }
          }
        }
        if (v && (!point0 || !pointEqual(point0, point1))) {
          stream.point(point1[0], point1[1]);
        }
        point0 = point1, v0 = v, c0 = c2;
      },
      lineEnd: function() {
        if (v0) stream.lineEnd();
        point0 = null;
      },
      // Rejoin first and last segments if there were intersections and the first
      // and last points were visible.
      clean: function() {
        return clean | (v00 && v0) << 1;
      }
    };
  }
  function intersect(a2, b, two) {
    var pa = cartesian(a2), pb = cartesian(b);
    var n1 = [1, 0, 0], n2 = cartesianCross(pa, pb), n2n2 = cartesianDot(n2, n2), n1n2 = n2[0], determinant = n2n2 - n1n2 * n1n2;
    if (!determinant) return !two && a2;
    var c1 = cr * n2n2 / determinant, c2 = -cr * n1n2 / determinant, n1xn2 = cartesianCross(n1, n2), A5 = cartesianScale(n1, c1), B2 = cartesianScale(n2, c2);
    cartesianAddInPlace(A5, B2);
    var u2 = n1xn2, w = cartesianDot(A5, u2), uu = cartesianDot(u2, u2), t2 = w * w - uu * (cartesianDot(A5, A5) - 1);
    if (t2 < 0) return;
    var t = sqrt$2(t2), q = cartesianScale(u2, (-w - t) / uu);
    cartesianAddInPlace(q, A5);
    q = spherical(q);
    if (!two) return q;
    var lambda02 = a2[0], lambda12 = b[0], phi02 = a2[1], phi12 = b[1], z;
    if (lambda12 < lambda02) z = lambda02, lambda02 = lambda12, lambda12 = z;
    var delta2 = lambda12 - lambda02, polar = abs$1(delta2 - pi$1) < epsilon$1, meridian = polar || delta2 < epsilon$1;
    if (!polar && phi12 < phi02) z = phi02, phi02 = phi12, phi12 = z;
    if (meridian ? polar ? phi02 + phi12 > 0 ^ q[1] < (abs$1(q[0] - lambda02) < epsilon$1 ? phi02 : phi12) : phi02 <= q[1] && q[1] <= phi12 : delta2 > pi$1 ^ (lambda02 <= q[0] && q[0] <= lambda12)) {
      var q1 = cartesianScale(u2, (-w + t) / uu);
      cartesianAddInPlace(q1, A5);
      return [q, spherical(q1)];
    }
  }
  function code(lambda, phi2) {
    var r = smallRadius ? radius : pi$1 - radius, code2 = 0;
    if (lambda < -r) code2 |= 1;
    else if (lambda > r) code2 |= 2;
    if (phi2 < -r) code2 |= 4;
    else if (phi2 > r) code2 |= 8;
    return code2;
  }
  return clip(visible, clipLine2, interpolate, smallRadius ? [0, -radius] : [-pi$1, radius - pi$1]);
}
function clipLine(a2, b, x02, y02, x12, y12) {
  var ax = a2[0], ay = a2[1], bx = b[0], by = b[1], t0 = 0, t1 = 1, dx = bx - ax, dy = by - ay, r;
  r = x02 - ax;
  if (!dx && r > 0) return;
  r /= dx;
  if (dx < 0) {
    if (r < t0) return;
    if (r < t1) t1 = r;
  } else if (dx > 0) {
    if (r > t1) return;
    if (r > t0) t0 = r;
  }
  r = x12 - ax;
  if (!dx && r < 0) return;
  r /= dx;
  if (dx < 0) {
    if (r > t1) return;
    if (r > t0) t0 = r;
  } else if (dx > 0) {
    if (r < t0) return;
    if (r < t1) t1 = r;
  }
  r = y02 - ay;
  if (!dy && r > 0) return;
  r /= dy;
  if (dy < 0) {
    if (r < t0) return;
    if (r < t1) t1 = r;
  } else if (dy > 0) {
    if (r > t1) return;
    if (r > t0) t0 = r;
  }
  r = y12 - ay;
  if (!dy && r < 0) return;
  r /= dy;
  if (dy < 0) {
    if (r > t1) return;
    if (r > t0) t0 = r;
  } else if (dy > 0) {
    if (r < t0) return;
    if (r < t1) t1 = r;
  }
  if (t0 > 0) a2[0] = ax + t0 * dx, a2[1] = ay + t0 * dy;
  if (t1 < 1) b[0] = ax + t1 * dx, b[1] = ay + t1 * dy;
  return true;
}
var clipMax = 1e9, clipMin = -clipMax;
function clipRectangle(x02, y02, x12, y12) {
  function visible(x2, y2) {
    return x02 <= x2 && x2 <= x12 && y02 <= y2 && y2 <= y12;
  }
  function interpolate(from, to, direction, stream) {
    var a2 = 0, a1 = 0;
    if (from == null || (a2 = corner(from, direction)) !== (a1 = corner(to, direction)) || comparePoint(from, to) < 0 ^ direction > 0) {
      do
        stream.point(a2 === 0 || a2 === 3 ? x02 : x12, a2 > 1 ? y12 : y02);
      while ((a2 = (a2 + direction + 4) % 4) !== a1);
    } else {
      stream.point(to[0], to[1]);
    }
  }
  function corner(p, direction) {
    return abs$1(p[0] - x02) < epsilon$1 ? direction > 0 ? 0 : 3 : abs$1(p[0] - x12) < epsilon$1 ? direction > 0 ? 2 : 1 : abs$1(p[1] - y02) < epsilon$1 ? direction > 0 ? 1 : 0 : direction > 0 ? 3 : 2;
  }
  function compareIntersection2(a2, b) {
    return comparePoint(a2.x, b.x);
  }
  function comparePoint(a2, b) {
    var ca = corner(a2, 1), cb = corner(b, 1);
    return ca !== cb ? ca - cb : ca === 0 ? b[1] - a2[1] : ca === 1 ? a2[0] - b[0] : ca === 2 ? a2[1] - b[1] : b[0] - a2[0];
  }
  return function(stream) {
    var activeStream = stream, bufferStream = clipBuffer(), segments, polygon, ring, x__, y__, v__, x_, y_, v_, first, clean;
    var clipStream = {
      point,
      lineStart,
      lineEnd,
      polygonStart,
      polygonEnd
    };
    function point(x2, y2) {
      if (visible(x2, y2)) activeStream.point(x2, y2);
    }
    function polygonInside() {
      var winding = 0;
      for (var i = 0, n = polygon.length; i < n; ++i) {
        for (var ring2 = polygon[i], j = 1, m2 = ring2.length, point2 = ring2[0], a0, a1, b0 = point2[0], b1 = point2[1]; j < m2; ++j) {
          a0 = b0, a1 = b1, point2 = ring2[j], b0 = point2[0], b1 = point2[1];
          if (a1 <= y12) {
            if (b1 > y12 && (b0 - a0) * (y12 - a1) > (b1 - a1) * (x02 - a0)) ++winding;
          } else {
            if (b1 <= y12 && (b0 - a0) * (y12 - a1) < (b1 - a1) * (x02 - a0)) --winding;
          }
        }
      }
      return winding;
    }
    function polygonStart() {
      activeStream = bufferStream, segments = [], polygon = [], clean = true;
    }
    function polygonEnd() {
      var startInside = polygonInside(), cleanInside = clean && startInside, visible2 = (segments = merge(segments)).length;
      if (cleanInside || visible2) {
        stream.polygonStart();
        if (cleanInside) {
          stream.lineStart();
          interpolate(null, null, 1, stream);
          stream.lineEnd();
        }
        if (visible2) {
          clipRejoin(segments, compareIntersection2, startInside, interpolate, stream);
        }
        stream.polygonEnd();
      }
      activeStream = stream, segments = polygon = ring = null;
    }
    function lineStart() {
      clipStream.point = linePoint2;
      if (polygon) polygon.push(ring = []);
      first = true;
      v_ = false;
      x_ = y_ = NaN;
    }
    function lineEnd() {
      if (segments) {
        linePoint2(x__, y__);
        if (v__ && v_) bufferStream.rejoin();
        segments.push(bufferStream.result());
      }
      clipStream.point = point;
      if (v_) activeStream.lineEnd();
    }
    function linePoint2(x2, y2) {
      var v = visible(x2, y2);
      if (polygon) ring.push([x2, y2]);
      if (first) {
        x__ = x2, y__ = y2, v__ = v;
        first = false;
        if (v) {
          activeStream.lineStart();
          activeStream.point(x2, y2);
        }
      } else {
        if (v && v_) activeStream.point(x2, y2);
        else {
          var a2 = [x_ = Math.max(clipMin, Math.min(clipMax, x_)), y_ = Math.max(clipMin, Math.min(clipMax, y_))], b = [x2 = Math.max(clipMin, Math.min(clipMax, x2)), y2 = Math.max(clipMin, Math.min(clipMax, y2))];
          if (clipLine(a2, b, x02, y02, x12, y12)) {
            if (!v_) {
              activeStream.lineStart();
              activeStream.point(a2[0], a2[1]);
            }
            activeStream.point(b[0], b[1]);
            if (!v) activeStream.lineEnd();
            clean = false;
          } else if (v) {
            activeStream.lineStart();
            activeStream.point(x2, y2);
            clean = false;
          }
        }
      }
      x_ = x2, y_ = y2, v_ = v;
    }
    return clipStream;
  };
}
function graticuleX(y02, y12, dy) {
  var y2 = range$1(y02, y12 - epsilon$1, dy).concat(y12);
  return function(x2) {
    return y2.map(function(y3) {
      return [x2, y3];
    });
  };
}
function graticuleY(x02, x12, dx) {
  var x2 = range$1(x02, x12 - epsilon$1, dx).concat(x12);
  return function(y2) {
    return x2.map(function(x3) {
      return [x3, y2];
    });
  };
}
function graticule() {
  var x12, x02, X12, X02, y12, y02, Y12, Y02, dx = 10, dy = dx, DX = 90, DY = 360, x2, y2, X, Y, precision = 2.5;
  function graticule2() {
    return { type: "MultiLineString", coordinates: lines() };
  }
  function lines() {
    return range$1(ceil(X02 / DX) * DX, X12, DX).map(X).concat(range$1(ceil(Y02 / DY) * DY, Y12, DY).map(Y)).concat(range$1(ceil(x02 / dx) * dx, x12, dx).filter(function(x3) {
      return abs$1(x3 % DX) > epsilon$1;
    }).map(x2)).concat(range$1(ceil(y02 / dy) * dy, y12, dy).filter(function(y3) {
      return abs$1(y3 % DY) > epsilon$1;
    }).map(y2));
  }
  graticule2.lines = function() {
    return lines().map(function(coordinates) {
      return { type: "LineString", coordinates };
    });
  };
  graticule2.outline = function() {
    return {
      type: "Polygon",
      coordinates: [
        X(X02).concat(
          Y(Y12).slice(1),
          X(X12).reverse().slice(1),
          Y(Y02).reverse().slice(1)
        )
      ]
    };
  };
  graticule2.extent = function(_) {
    if (!arguments.length) return graticule2.extentMinor();
    return graticule2.extentMajor(_).extentMinor(_);
  };
  graticule2.extentMajor = function(_) {
    if (!arguments.length) return [[X02, Y02], [X12, Y12]];
    X02 = +_[0][0], X12 = +_[1][0];
    Y02 = +_[0][1], Y12 = +_[1][1];
    if (X02 > X12) _ = X02, X02 = X12, X12 = _;
    if (Y02 > Y12) _ = Y02, Y02 = Y12, Y12 = _;
    return graticule2.precision(precision);
  };
  graticule2.extentMinor = function(_) {
    if (!arguments.length) return [[x02, y02], [x12, y12]];
    x02 = +_[0][0], x12 = +_[1][0];
    y02 = +_[0][1], y12 = +_[1][1];
    if (x02 > x12) _ = x02, x02 = x12, x12 = _;
    if (y02 > y12) _ = y02, y02 = y12, y12 = _;
    return graticule2.precision(precision);
  };
  graticule2.step = function(_) {
    if (!arguments.length) return graticule2.stepMinor();
    return graticule2.stepMajor(_).stepMinor(_);
  };
  graticule2.stepMajor = function(_) {
    if (!arguments.length) return [DX, DY];
    DX = +_[0], DY = +_[1];
    return graticule2;
  };
  graticule2.stepMinor = function(_) {
    if (!arguments.length) return [dx, dy];
    dx = +_[0], dy = +_[1];
    return graticule2;
  };
  graticule2.precision = function(_) {
    if (!arguments.length) return precision;
    precision = +_;
    x2 = graticuleX(y02, y12, 90);
    y2 = graticuleY(x02, x12, precision);
    X = graticuleX(Y02, Y12, 90);
    Y = graticuleY(X02, X12, precision);
    return graticule2;
  };
  return graticule2.extentMajor([[-180, -90 + epsilon$1], [180, 90 - epsilon$1]]).extentMinor([[-180, -80 - epsilon$1], [180, 80 + epsilon$1]]);
}
const identity$2 = (x2) => x2;
var areaSum = new Adder(), areaRingSum = new Adder(), x00$2, y00$2, x0$3, y0$3;
var areaStream = {
  point: noop,
  lineStart: noop,
  lineEnd: noop,
  polygonStart: function() {
    areaStream.lineStart = areaRingStart;
    areaStream.lineEnd = areaRingEnd;
  },
  polygonEnd: function() {
    areaStream.lineStart = areaStream.lineEnd = areaStream.point = noop;
    areaSum.add(abs$1(areaRingSum));
    areaRingSum = new Adder();
  },
  result: function() {
    var area = areaSum / 2;
    areaSum = new Adder();
    return area;
  }
};
function areaRingStart() {
  areaStream.point = areaPointFirst;
}
function areaPointFirst(x2, y2) {
  areaStream.point = areaPoint;
  x00$2 = x0$3 = x2, y00$2 = y0$3 = y2;
}
function areaPoint(x2, y2) {
  areaRingSum.add(y0$3 * x2 - x0$3 * y2);
  x0$3 = x2, y0$3 = y2;
}
function areaRingEnd() {
  areaPoint(x00$2, y00$2);
}
var x0$2 = Infinity, y0$2 = x0$2, x1 = -x0$2, y1 = x1;
var boundsStream = {
  point: boundsPoint,
  lineStart: noop,
  lineEnd: noop,
  polygonStart: noop,
  polygonEnd: noop,
  result: function() {
    var bounds = [[x0$2, y0$2], [x1, y1]];
    x1 = y1 = -(y0$2 = x0$2 = Infinity);
    return bounds;
  }
};
function boundsPoint(x2, y2) {
  if (x2 < x0$2) x0$2 = x2;
  if (x2 > x1) x1 = x2;
  if (y2 < y0$2) y0$2 = y2;
  if (y2 > y1) y1 = y2;
}
var X0 = 0, Y0 = 0, Z0 = 0, X1 = 0, Y1 = 0, Z1 = 0, X2 = 0, Y2 = 0, Z2 = 0, x00$1, y00$1, x0$1, y0$1;
var centroidStream = {
  point: centroidPoint,
  lineStart: centroidLineStart,
  lineEnd: centroidLineEnd,
  polygonStart: function() {
    centroidStream.lineStart = centroidRingStart;
    centroidStream.lineEnd = centroidRingEnd;
  },
  polygonEnd: function() {
    centroidStream.point = centroidPoint;
    centroidStream.lineStart = centroidLineStart;
    centroidStream.lineEnd = centroidLineEnd;
  },
  result: function() {
    var centroid = Z2 ? [X2 / Z2, Y2 / Z2] : Z1 ? [X1 / Z1, Y1 / Z1] : Z0 ? [X0 / Z0, Y0 / Z0] : [NaN, NaN];
    X0 = Y0 = Z0 = X1 = Y1 = Z1 = X2 = Y2 = Z2 = 0;
    return centroid;
  }
};
function centroidPoint(x2, y2) {
  X0 += x2;
  Y0 += y2;
  ++Z0;
}
function centroidLineStart() {
  centroidStream.point = centroidPointFirstLine;
}
function centroidPointFirstLine(x2, y2) {
  centroidStream.point = centroidPointLine;
  centroidPoint(x0$1 = x2, y0$1 = y2);
}
function centroidPointLine(x2, y2) {
  var dx = x2 - x0$1, dy = y2 - y0$1, z = sqrt$2(dx * dx + dy * dy);
  X1 += z * (x0$1 + x2) / 2;
  Y1 += z * (y0$1 + y2) / 2;
  Z1 += z;
  centroidPoint(x0$1 = x2, y0$1 = y2);
}
function centroidLineEnd() {
  centroidStream.point = centroidPoint;
}
function centroidRingStart() {
  centroidStream.point = centroidPointFirstRing;
}
function centroidRingEnd() {
  centroidPointRing(x00$1, y00$1);
}
function centroidPointFirstRing(x2, y2) {
  centroidStream.point = centroidPointRing;
  centroidPoint(x00$1 = x0$1 = x2, y00$1 = y0$1 = y2);
}
function centroidPointRing(x2, y2) {
  var dx = x2 - x0$1, dy = y2 - y0$1, z = sqrt$2(dx * dx + dy * dy);
  X1 += z * (x0$1 + x2) / 2;
  Y1 += z * (y0$1 + y2) / 2;
  Z1 += z;
  z = y0$1 * x2 - x0$1 * y2;
  X2 += z * (x0$1 + x2);
  Y2 += z * (y0$1 + y2);
  Z2 += z * 3;
  centroidPoint(x0$1 = x2, y0$1 = y2);
}
function PathContext(context) {
  this._context = context;
}
PathContext.prototype = {
  _radius: 4.5,
  pointRadius: function(_) {
    return this._radius = _, this;
  },
  polygonStart: function() {
    this._line = 0;
  },
  polygonEnd: function() {
    this._line = NaN;
  },
  lineStart: function() {
    this._point = 0;
  },
  lineEnd: function() {
    if (this._line === 0) this._context.closePath();
    this._point = NaN;
  },
  point: function(x2, y2) {
    switch (this._point) {
      case 0: {
        this._context.moveTo(x2, y2);
        this._point = 1;
        break;
      }
      case 1: {
        this._context.lineTo(x2, y2);
        break;
      }
      default: {
        this._context.moveTo(x2 + this._radius, y2);
        this._context.arc(x2, y2, this._radius, 0, tau);
        break;
      }
    }
  },
  result: noop
};
var lengthSum = new Adder(), lengthRing, x00, y00, x0, y0;
var lengthStream = {
  point: noop,
  lineStart: function() {
    lengthStream.point = lengthPointFirst;
  },
  lineEnd: function() {
    if (lengthRing) lengthPoint(x00, y00);
    lengthStream.point = noop;
  },
  polygonStart: function() {
    lengthRing = true;
  },
  polygonEnd: function() {
    lengthRing = null;
  },
  result: function() {
    var length = +lengthSum;
    lengthSum = new Adder();
    return length;
  }
};
function lengthPointFirst(x2, y2) {
  lengthStream.point = lengthPoint;
  x00 = x0 = x2, y00 = y0 = y2;
}
function lengthPoint(x2, y2) {
  x0 -= x2, y0 -= y2;
  lengthSum.add(sqrt$2(x0 * x0 + y0 * y0));
  x0 = x2, y0 = y2;
}
let cacheDigits, cacheAppend, cacheRadius, cacheCircle;
class PathString {
  constructor(digits) {
    this._append = digits == null ? append : appendRound(digits);
    this._radius = 4.5;
    this._ = "";
  }
  pointRadius(_) {
    this._radius = +_;
    return this;
  }
  polygonStart() {
    this._line = 0;
  }
  polygonEnd() {
    this._line = NaN;
  }
  lineStart() {
    this._point = 0;
  }
  lineEnd() {
    if (this._line === 0) this._ += "Z";
    this._point = NaN;
  }
  point(x2, y2) {
    switch (this._point) {
      case 0: {
        this._append`M${x2},${y2}`;
        this._point = 1;
        break;
      }
      case 1: {
        this._append`L${x2},${y2}`;
        break;
      }
      default: {
        this._append`M${x2},${y2}`;
        if (this._radius !== cacheRadius || this._append !== cacheAppend) {
          const r = this._radius;
          const s = this._;
          this._ = "";
          this._append`m0,${r}a${r},${r} 0 1,1 0,${-2 * r}a${r},${r} 0 1,1 0,${2 * r}z`;
          cacheRadius = r;
          cacheAppend = this._append;
          cacheCircle = this._;
          this._ = s;
        }
        this._ += cacheCircle;
        break;
      }
    }
  }
  result() {
    const result = this._;
    this._ = "";
    return result.length ? result : null;
  }
}
function append(strings) {
  let i = 1;
  this._ += strings[0];
  for (const j = strings.length; i < j; ++i) {
    this._ += arguments[i] + strings[i];
  }
}
function appendRound(digits) {
  const d = Math.floor(digits);
  if (!(d >= 0)) throw new RangeError(`invalid digits: ${digits}`);
  if (d > 15) return append;
  if (d !== cacheDigits) {
    const k = 10 ** d;
    cacheDigits = d;
    cacheAppend = function append2(strings) {
      let i = 1;
      this._ += strings[0];
      for (const j = strings.length; i < j; ++i) {
        this._ += Math.round(arguments[i] * k) / k + strings[i];
      }
    };
  }
  return cacheAppend;
}
function geoPath(projection2, context) {
  let digits = 3, pointRadius = 4.5, projectionStream, contextStream;
  function path(object2) {
    if (object2) {
      if (typeof pointRadius === "function") contextStream.pointRadius(+pointRadius.apply(this, arguments));
      geoStream(object2, projectionStream(contextStream));
    }
    return contextStream.result();
  }
  path.area = function(object2) {
    geoStream(object2, projectionStream(areaStream));
    return areaStream.result();
  };
  path.measure = function(object2) {
    geoStream(object2, projectionStream(lengthStream));
    return lengthStream.result();
  };
  path.bounds = function(object2) {
    geoStream(object2, projectionStream(boundsStream));
    return boundsStream.result();
  };
  path.centroid = function(object2) {
    geoStream(object2, projectionStream(centroidStream));
    return centroidStream.result();
  };
  path.projection = function(_) {
    if (!arguments.length) return projection2;
    projectionStream = _ == null ? (projection2 = null, identity$2) : (projection2 = _).stream;
    return path;
  };
  path.context = function(_) {
    if (!arguments.length) return context;
    contextStream = _ == null ? (context = null, new PathString(digits)) : new PathContext(context = _);
    if (typeof pointRadius !== "function") contextStream.pointRadius(pointRadius);
    return path;
  };
  path.pointRadius = function(_) {
    if (!arguments.length) return pointRadius;
    pointRadius = typeof _ === "function" ? _ : (contextStream.pointRadius(+_), +_);
    return path;
  };
  path.digits = function(_) {
    if (!arguments.length) return digits;
    if (_ == null) digits = null;
    else {
      const d = Math.floor(_);
      if (!(d >= 0)) throw new RangeError(`invalid digits: ${_}`);
      digits = d;
    }
    if (context === null) contextStream = new PathString(digits);
    return path;
  };
  return path.projection(projection2).digits(digits).context(context);
}
function transformer$2(methods) {
  return function(stream) {
    var s = new TransformStream();
    for (var key in methods) s[key] = methods[key];
    s.stream = stream;
    return s;
  };
}
function TransformStream() {
}
TransformStream.prototype = {
  constructor: TransformStream,
  point: function(x2, y2) {
    this.stream.point(x2, y2);
  },
  sphere: function() {
    this.stream.sphere();
  },
  lineStart: function() {
    this.stream.lineStart();
  },
  lineEnd: function() {
    this.stream.lineEnd();
  },
  polygonStart: function() {
    this.stream.polygonStart();
  },
  polygonEnd: function() {
    this.stream.polygonEnd();
  }
};
function fit(projection2, fitBounds, object2) {
  var clip2 = projection2.clipExtent && projection2.clipExtent();
  projection2.scale(150).translate([0, 0]);
  if (clip2 != null) projection2.clipExtent(null);
  geoStream(object2, projection2.stream(boundsStream));
  fitBounds(boundsStream.result());
  if (clip2 != null) projection2.clipExtent(clip2);
  return projection2;
}
function fitExtent(projection2, extent, object2) {
  return fit(projection2, function(b) {
    var w = extent[1][0] - extent[0][0], h = extent[1][1] - extent[0][1], k = Math.min(w / (b[1][0] - b[0][0]), h / (b[1][1] - b[0][1])), x2 = +extent[0][0] + (w - k * (b[1][0] + b[0][0])) / 2, y2 = +extent[0][1] + (h - k * (b[1][1] + b[0][1])) / 2;
    projection2.scale(150 * k).translate([x2, y2]);
  }, object2);
}
function fitSize(projection2, size, object2) {
  return fitExtent(projection2, [[0, 0], size], object2);
}
function fitWidth(projection2, width, object2) {
  return fit(projection2, function(b) {
    var w = +width, k = w / (b[1][0] - b[0][0]), x2 = (w - k * (b[1][0] + b[0][0])) / 2, y2 = -k * b[0][1];
    projection2.scale(150 * k).translate([x2, y2]);
  }, object2);
}
function fitHeight(projection2, height, object2) {
  return fit(projection2, function(b) {
    var h = +height, k = h / (b[1][1] - b[0][1]), x2 = -k * b[0][0], y2 = (h - k * (b[1][1] + b[0][1])) / 2;
    projection2.scale(150 * k).translate([x2, y2]);
  }, object2);
}
var maxDepth = 16, cosMinDistance = cos$1(30 * radians);
function resample(project, delta2) {
  return +delta2 ? resample$1(project, delta2) : resampleNone(project);
}
function resampleNone(project) {
  return transformer$2({
    point: function(x2, y2) {
      x2 = project(x2, y2);
      this.stream.point(x2[0], x2[1]);
    }
  });
}
function resample$1(project, delta2) {
  function resampleLineTo(x02, y02, lambda02, a0, b0, c0, x12, y12, lambda12, a1, b1, c1, depth, stream) {
    var dx = x12 - x02, dy = y12 - y02, d2 = dx * dx + dy * dy;
    if (d2 > 4 * delta2 && depth--) {
      var a2 = a0 + a1, b = b0 + b1, c2 = c0 + c1, m2 = sqrt$2(a2 * a2 + b * b + c2 * c2), phi2 = asin$1(c2 /= m2), lambda22 = abs$1(abs$1(c2) - 1) < epsilon$1 || abs$1(lambda02 - lambda12) < epsilon$1 ? (lambda02 + lambda12) / 2 : atan2(b, a2), p = project(lambda22, phi2), x2 = p[0], y2 = p[1], dx2 = x2 - x02, dy2 = y2 - y02, dz = dy * dx2 - dx * dy2;
      if (dz * dz / d2 > delta2 || abs$1((dx * dx2 + dy * dy2) / d2 - 0.5) > 0.3 || a0 * a1 + b0 * b1 + c0 * c1 < cosMinDistance) {
        resampleLineTo(x02, y02, lambda02, a0, b0, c0, x2, y2, lambda22, a2 /= m2, b /= m2, c2, depth, stream);
        stream.point(x2, y2);
        resampleLineTo(x2, y2, lambda22, a2, b, c2, x12, y12, lambda12, a1, b1, c1, depth, stream);
      }
    }
  }
  return function(stream) {
    var lambda002, x002, y002, a00, b00, c00, lambda02, x02, y02, a0, b0, c0;
    var resampleStream = {
      point,
      lineStart,
      lineEnd,
      polygonStart: function() {
        stream.polygonStart();
        resampleStream.lineStart = ringStart;
      },
      polygonEnd: function() {
        stream.polygonEnd();
        resampleStream.lineStart = lineStart;
      }
    };
    function point(x2, y2) {
      x2 = project(x2, y2);
      stream.point(x2[0], x2[1]);
    }
    function lineStart() {
      x02 = NaN;
      resampleStream.point = linePoint2;
      stream.lineStart();
    }
    function linePoint2(lambda, phi2) {
      var c2 = cartesian([lambda, phi2]), p = project(lambda, phi2);
      resampleLineTo(x02, y02, lambda02, a0, b0, c0, x02 = p[0], y02 = p[1], lambda02 = lambda, a0 = c2[0], b0 = c2[1], c0 = c2[2], maxDepth, stream);
      stream.point(x02, y02);
    }
    function lineEnd() {
      resampleStream.point = point;
      stream.lineEnd();
    }
    function ringStart() {
      lineStart();
      resampleStream.point = ringPoint;
      resampleStream.lineEnd = ringEnd;
    }
    function ringPoint(lambda, phi2) {
      linePoint2(lambda002 = lambda, phi2), x002 = x02, y002 = y02, a00 = a0, b00 = b0, c00 = c0;
      resampleStream.point = linePoint2;
    }
    function ringEnd() {
      resampleLineTo(x02, y02, lambda02, a0, b0, c0, x002, y002, lambda002, a00, b00, c00, maxDepth, stream);
      resampleStream.lineEnd = lineEnd;
      lineEnd();
    }
    return resampleStream;
  };
}
var transformRadians = transformer$2({
  point: function(x2, y2) {
    this.stream.point(x2 * radians, y2 * radians);
  }
});
function transformRotate(rotate) {
  return transformer$2({
    point: function(x2, y2) {
      var r = rotate(x2, y2);
      return this.stream.point(r[0], r[1]);
    }
  });
}
function scaleTranslate(k, dx, dy, sx, sy) {
  function transform2(x2, y2) {
    x2 *= sx;
    y2 *= sy;
    return [dx + k * x2, dy - k * y2];
  }
  transform2.invert = function(x2, y2) {
    return [(x2 - dx) / k * sx, (dy - y2) / k * sy];
  };
  return transform2;
}
function scaleTranslateRotate(k, dx, dy, sx, sy, alpha) {
  if (!alpha) return scaleTranslate(k, dx, dy, sx, sy);
  var cosAlpha = cos$1(alpha), sinAlpha = sin$1(alpha), a2 = cosAlpha * k, b = sinAlpha * k, ai = cosAlpha / k, bi = sinAlpha / k, ci = (sinAlpha * dy - cosAlpha * dx) / k, fi = (sinAlpha * dx + cosAlpha * dy) / k;
  function transform2(x2, y2) {
    x2 *= sx;
    y2 *= sy;
    return [a2 * x2 - b * y2 + dx, dy - b * x2 - a2 * y2];
  }
  transform2.invert = function(x2, y2) {
    return [sx * (ai * x2 - bi * y2 + ci), sy * (fi - bi * x2 - ai * y2)];
  };
  return transform2;
}
function projection(project) {
  return projectionMutator(function() {
    return project;
  })();
}
function projectionMutator(projectAt) {
  var project, k = 150, x2 = 480, y2 = 250, lambda = 0, phi2 = 0, deltaLambda = 0, deltaPhi = 0, deltaGamma = 0, rotate, alpha = 0, sx = 1, sy = 1, theta = null, preclip = clipAntimeridian, x02 = null, y02, x12, y12, postclip = identity$2, delta2 = 0.5, projectResample, projectTransform, projectRotateTransform, cache, cacheStream;
  function projection2(point) {
    return projectRotateTransform(point[0] * radians, point[1] * radians);
  }
  function invert(point) {
    point = projectRotateTransform.invert(point[0], point[1]);
    return point && [point[0] * degrees, point[1] * degrees];
  }
  projection2.stream = function(stream) {
    return cache && cacheStream === stream ? cache : cache = transformRadians(transformRotate(rotate)(preclip(projectResample(postclip(cacheStream = stream)))));
  };
  projection2.preclip = function(_) {
    return arguments.length ? (preclip = _, theta = void 0, reset()) : preclip;
  };
  projection2.postclip = function(_) {
    return arguments.length ? (postclip = _, x02 = y02 = x12 = y12 = null, reset()) : postclip;
  };
  projection2.clipAngle = function(_) {
    return arguments.length ? (preclip = +_ ? clipCircle(theta = _ * radians) : (theta = null, clipAntimeridian), reset()) : theta * degrees;
  };
  projection2.clipExtent = function(_) {
    return arguments.length ? (postclip = _ == null ? (x02 = y02 = x12 = y12 = null, identity$2) : clipRectangle(x02 = +_[0][0], y02 = +_[0][1], x12 = +_[1][0], y12 = +_[1][1]), reset()) : x02 == null ? null : [[x02, y02], [x12, y12]];
  };
  projection2.scale = function(_) {
    return arguments.length ? (k = +_, recenter()) : k;
  };
  projection2.translate = function(_) {
    return arguments.length ? (x2 = +_[0], y2 = +_[1], recenter()) : [x2, y2];
  };
  projection2.center = function(_) {
    return arguments.length ? (lambda = _[0] % 360 * radians, phi2 = _[1] % 360 * radians, recenter()) : [lambda * degrees, phi2 * degrees];
  };
  projection2.rotate = function(_) {
    return arguments.length ? (deltaLambda = _[0] % 360 * radians, deltaPhi = _[1] % 360 * radians, deltaGamma = _.length > 2 ? _[2] % 360 * radians : 0, recenter()) : [deltaLambda * degrees, deltaPhi * degrees, deltaGamma * degrees];
  };
  projection2.angle = function(_) {
    return arguments.length ? (alpha = _ % 360 * radians, recenter()) : alpha * degrees;
  };
  projection2.reflectX = function(_) {
    return arguments.length ? (sx = _ ? -1 : 1, recenter()) : sx < 0;
  };
  projection2.reflectY = function(_) {
    return arguments.length ? (sy = _ ? -1 : 1, recenter()) : sy < 0;
  };
  projection2.precision = function(_) {
    return arguments.length ? (projectResample = resample(projectTransform, delta2 = _ * _), reset()) : sqrt$2(delta2);
  };
  projection2.fitExtent = function(extent, object2) {
    return fitExtent(projection2, extent, object2);
  };
  projection2.fitSize = function(size, object2) {
    return fitSize(projection2, size, object2);
  };
  projection2.fitWidth = function(width, object2) {
    return fitWidth(projection2, width, object2);
  };
  projection2.fitHeight = function(height, object2) {
    return fitHeight(projection2, height, object2);
  };
  function recenter() {
    var center = scaleTranslateRotate(k, 0, 0, sx, sy, alpha).apply(null, project(lambda, phi2)), transform2 = scaleTranslateRotate(k, x2 - center[0], y2 - center[1], sx, sy, alpha);
    rotate = rotateRadians(deltaLambda, deltaPhi, deltaGamma);
    projectTransform = compose(project, transform2);
    projectRotateTransform = compose(rotate, projectTransform);
    projectResample = resample(projectTransform, delta2);
    return reset();
  }
  function reset() {
    cache = cacheStream = null;
    return projection2;
  }
  return function() {
    project = projectAt.apply(this, arguments);
    projection2.invert = project.invert && invert;
    return recenter();
  };
}
function conicProjection(projectAt) {
  var phi02 = 0, phi12 = pi$1 / 3, m2 = projectionMutator(projectAt), p = m2(phi02, phi12);
  p.parallels = function(_) {
    return arguments.length ? m2(phi02 = _[0] * radians, phi12 = _[1] * radians) : [phi02 * degrees, phi12 * degrees];
  };
  return p;
}
function cylindricalEqualAreaRaw(phi02) {
  var cosPhi02 = cos$1(phi02);
  function forward(lambda, phi2) {
    return [lambda * cosPhi02, sin$1(phi2) / cosPhi02];
  }
  forward.invert = function(x2, y2) {
    return [x2 / cosPhi02, asin$1(y2 * cosPhi02)];
  };
  return forward;
}
function conicEqualAreaRaw(y02, y12) {
  var sy0 = sin$1(y02), n = (sy0 + sin$1(y12)) / 2;
  if (abs$1(n) < epsilon$1) return cylindricalEqualAreaRaw(y02);
  var c2 = 1 + sy0 * (2 * n - sy0), r0 = sqrt$2(c2) / n;
  function project(x2, y2) {
    var r = sqrt$2(c2 - 2 * n * sin$1(y2)) / n;
    return [r * sin$1(x2 *= n), r0 - r * cos$1(x2)];
  }
  project.invert = function(x2, y2) {
    var r0y = r0 - y2, l = atan2(x2, abs$1(r0y)) * sign(r0y);
    if (r0y * n < 0)
      l -= pi$1 * sign(x2) * sign(r0y);
    return [l / n, asin$1((c2 - (x2 * x2 + r0y * r0y) * n * n) / (2 * n))];
  };
  return project;
}
function geoConicEqualArea() {
  return conicProjection(conicEqualAreaRaw).scale(155.424).center([0, 33.6442]);
}
function geoAlbers() {
  return geoConicEqualArea().parallels([29.5, 45.5]).scale(1070).translate([480, 250]).rotate([96, 0]).center([-0.6, 38.7]);
}
function multiplex(streams) {
  var n = streams.length;
  return {
    point: function(x2, y2) {
      var i = -1;
      while (++i < n) streams[i].point(x2, y2);
    },
    sphere: function() {
      var i = -1;
      while (++i < n) streams[i].sphere();
    },
    lineStart: function() {
      var i = -1;
      while (++i < n) streams[i].lineStart();
    },
    lineEnd: function() {
      var i = -1;
      while (++i < n) streams[i].lineEnd();
    },
    polygonStart: function() {
      var i = -1;
      while (++i < n) streams[i].polygonStart();
    },
    polygonEnd: function() {
      var i = -1;
      while (++i < n) streams[i].polygonEnd();
    }
  };
}
function geoAlbersUsa() {
  var cache, cacheStream, lower48 = geoAlbers(), lower48Point, alaska = geoConicEqualArea().rotate([154, 0]).center([-2, 58.5]).parallels([55, 65]), alaskaPoint, hawaii = geoConicEqualArea().rotate([157, 0]).center([-3, 19.9]).parallels([8, 18]), hawaiiPoint, point, pointStream = { point: function(x2, y2) {
    point = [x2, y2];
  } };
  function albersUsa(coordinates) {
    var x2 = coordinates[0], y2 = coordinates[1];
    return point = null, (lower48Point.point(x2, y2), point) || (alaskaPoint.point(x2, y2), point) || (hawaiiPoint.point(x2, y2), point);
  }
  albersUsa.invert = function(coordinates) {
    var k = lower48.scale(), t = lower48.translate(), x2 = (coordinates[0] - t[0]) / k, y2 = (coordinates[1] - t[1]) / k;
    return (y2 >= 0.12 && y2 < 0.234 && x2 >= -0.425 && x2 < -0.214 ? alaska : y2 >= 0.166 && y2 < 0.234 && x2 >= -0.214 && x2 < -0.115 ? hawaii : lower48).invert(coordinates);
  };
  albersUsa.stream = function(stream) {
    return cache && cacheStream === stream ? cache : cache = multiplex([lower48.stream(cacheStream = stream), alaska.stream(stream), hawaii.stream(stream)]);
  };
  albersUsa.precision = function(_) {
    if (!arguments.length) return lower48.precision();
    lower48.precision(_), alaska.precision(_), hawaii.precision(_);
    return reset();
  };
  albersUsa.scale = function(_) {
    if (!arguments.length) return lower48.scale();
    lower48.scale(_), alaska.scale(_ * 0.35), hawaii.scale(_);
    return albersUsa.translate(lower48.translate());
  };
  albersUsa.translate = function(_) {
    if (!arguments.length) return lower48.translate();
    var k = lower48.scale(), x2 = +_[0], y2 = +_[1];
    lower48Point = lower48.translate(_).clipExtent([[x2 - 0.455 * k, y2 - 0.238 * k], [x2 + 0.455 * k, y2 + 0.238 * k]]).stream(pointStream);
    alaskaPoint = alaska.translate([x2 - 0.307 * k, y2 + 0.201 * k]).clipExtent([[x2 - 0.425 * k + epsilon$1, y2 + 0.12 * k + epsilon$1], [x2 - 0.214 * k - epsilon$1, y2 + 0.234 * k - epsilon$1]]).stream(pointStream);
    hawaiiPoint = hawaii.translate([x2 - 0.205 * k, y2 + 0.212 * k]).clipExtent([[x2 - 0.214 * k + epsilon$1, y2 + 0.166 * k + epsilon$1], [x2 - 0.115 * k - epsilon$1, y2 + 0.234 * k - epsilon$1]]).stream(pointStream);
    return reset();
  };
  albersUsa.fitExtent = function(extent, object2) {
    return fitExtent(albersUsa, extent, object2);
  };
  albersUsa.fitSize = function(size, object2) {
    return fitSize(albersUsa, size, object2);
  };
  albersUsa.fitWidth = function(width, object2) {
    return fitWidth(albersUsa, width, object2);
  };
  albersUsa.fitHeight = function(height, object2) {
    return fitHeight(albersUsa, height, object2);
  };
  function reset() {
    cache = cacheStream = null;
    return albersUsa;
  }
  return albersUsa.scale(1070);
}
function azimuthalRaw(scale) {
  return function(x2, y2) {
    var cx = cos$1(x2), cy = cos$1(y2), k = scale(cx * cy);
    if (k === Infinity) return [2, 0];
    return [
      k * cy * sin$1(x2),
      k * sin$1(y2)
    ];
  };
}
function azimuthalInvert(angle2) {
  return function(x2, y2) {
    var z = sqrt$2(x2 * x2 + y2 * y2), c2 = angle2(z), sc = sin$1(c2), cc = cos$1(c2);
    return [
      atan2(x2 * sc, z * cc),
      asin$1(z && y2 * sc / z)
    ];
  };
}
var azimuthalEqualAreaRaw = azimuthalRaw(function(cxcy) {
  return sqrt$2(2 / (1 + cxcy));
});
azimuthalEqualAreaRaw.invert = azimuthalInvert(function(z) {
  return 2 * asin$1(z / 2);
});
function geoAzimuthalEqualArea() {
  return projection(azimuthalEqualAreaRaw).scale(124.75).clipAngle(180 - 1e-3);
}
var azimuthalEquidistantRaw = azimuthalRaw(function(c2) {
  return (c2 = acos(c2)) && c2 / sin$1(c2);
});
azimuthalEquidistantRaw.invert = azimuthalInvert(function(z) {
  return z;
});
function geoAzimuthalEquidistant() {
  return projection(azimuthalEquidistantRaw).scale(79.4188).clipAngle(180 - 1e-3);
}
function mercatorRaw(lambda, phi2) {
  return [lambda, log$1(tan((halfPi$1 + phi2) / 2))];
}
mercatorRaw.invert = function(x2, y2) {
  return [x2, 2 * atan(exp(y2)) - halfPi$1];
};
function geoMercator() {
  return mercatorProjection(mercatorRaw).scale(961 / tau);
}
function mercatorProjection(project) {
  var m2 = projection(project), center = m2.center, scale = m2.scale, translate = m2.translate, clipExtent = m2.clipExtent, x02 = null, y02, x12, y12;
  m2.scale = function(_) {
    return arguments.length ? (scale(_), reclip()) : scale();
  };
  m2.translate = function(_) {
    return arguments.length ? (translate(_), reclip()) : translate();
  };
  m2.center = function(_) {
    return arguments.length ? (center(_), reclip()) : center();
  };
  m2.clipExtent = function(_) {
    return arguments.length ? (_ == null ? x02 = y02 = x12 = y12 = null : (x02 = +_[0][0], y02 = +_[0][1], x12 = +_[1][0], y12 = +_[1][1]), reclip()) : x02 == null ? null : [[x02, y02], [x12, y12]];
  };
  function reclip() {
    var k = pi$1 * scale(), t = m2(rotation(m2.rotate()).invert([0, 0]));
    return clipExtent(x02 == null ? [[t[0] - k, t[1] - k], [t[0] + k, t[1] + k]] : project === mercatorRaw ? [[Math.max(t[0] - k, x02), y02], [Math.min(t[0] + k, x12), y12]] : [[x02, Math.max(t[1] - k, y02)], [x12, Math.min(t[1] + k, y12)]]);
  }
  return reclip();
}
function tany(y2) {
  return tan((halfPi$1 + y2) / 2);
}
function conicConformalRaw(y02, y12) {
  var cy0 = cos$1(y02), n = y02 === y12 ? sin$1(y02) : log$1(cy0 / cos$1(y12)) / log$1(tany(y12) / tany(y02)), f = cy0 * pow$1(tany(y02), n) / n;
  if (!n) return mercatorRaw;
  function project(x2, y2) {
    if (f > 0) {
      if (y2 < -halfPi$1 + epsilon$1) y2 = -halfPi$1 + epsilon$1;
    } else {
      if (y2 > halfPi$1 - epsilon$1) y2 = halfPi$1 - epsilon$1;
    }
    var r = f / pow$1(tany(y2), n);
    return [r * sin$1(n * x2), f - r * cos$1(n * x2)];
  }
  project.invert = function(x2, y2) {
    var fy = f - y2, r = sign(n) * sqrt$2(x2 * x2 + fy * fy), l = atan2(x2, abs$1(fy)) * sign(fy);
    if (fy * n < 0)
      l -= pi$1 * sign(x2) * sign(fy);
    return [l / n, 2 * atan(pow$1(f / r, 1 / n)) - halfPi$1];
  };
  return project;
}
function geoConicConformal() {
  return conicProjection(conicConformalRaw).scale(109.5).parallels([30, 30]);
}
function equirectangularRaw(lambda, phi2) {
  return [lambda, phi2];
}
equirectangularRaw.invert = equirectangularRaw;
function geoEquirectangular() {
  return projection(equirectangularRaw).scale(152.63);
}
function conicEquidistantRaw(y02, y12) {
  var cy0 = cos$1(y02), n = y02 === y12 ? sin$1(y02) : (cy0 - cos$1(y12)) / (y12 - y02), g = cy0 / n + y02;
  if (abs$1(n) < epsilon$1) return equirectangularRaw;
  function project(x2, y2) {
    var gy = g - y2, nx = n * x2;
    return [gy * sin$1(nx), g - gy * cos$1(nx)];
  }
  project.invert = function(x2, y2) {
    var gy = g - y2, l = atan2(x2, abs$1(gy)) * sign(gy);
    if (gy * n < 0)
      l -= pi$1 * sign(x2) * sign(gy);
    return [l / n, g - sign(n) * sqrt$2(x2 * x2 + gy * gy)];
  };
  return project;
}
function geoConicEquidistant() {
  return conicProjection(conicEquidistantRaw).scale(131.154).center([0, 13.9389]);
}
var A1 = 1.340264, A2 = -0.081106, A3 = 893e-6, A4 = 3796e-6, M = sqrt$2(3) / 2, iterations = 12;
function equalEarthRaw(lambda, phi2) {
  var l = asin$1(M * sin$1(phi2)), l2 = l * l, l6 = l2 * l2 * l2;
  return [
    lambda * cos$1(l) / (M * (A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2))),
    l * (A1 + A2 * l2 + l6 * (A3 + A4 * l2))
  ];
}
equalEarthRaw.invert = function(x2, y2) {
  var l = y2, l2 = l * l, l6 = l2 * l2 * l2;
  for (var i = 0, delta, fy, fpy; i < iterations; ++i) {
    fy = l * (A1 + A2 * l2 + l6 * (A3 + A4 * l2)) - y2;
    fpy = A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2);
    l -= delta = fy / fpy, l2 = l * l, l6 = l2 * l2 * l2;
    if (abs$1(delta) < epsilon2) break;
  }
  return [
    M * x2 * (A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)) / cos$1(l),
    asin$1(sin$1(l) / M)
  ];
};
function geoEqualEarth() {
  return projection(equalEarthRaw).scale(177.158);
}
function gnomonicRaw(x2, y2) {
  var cy = cos$1(y2), k = cos$1(x2) * cy;
  return [cy * sin$1(x2) / k, sin$1(y2) / k];
}
gnomonicRaw.invert = azimuthalInvert(atan);
function geoGnomonic() {
  return projection(gnomonicRaw).scale(144.049).clipAngle(60);
}
function geoIdentity() {
  var k = 1, tx = 0, ty = 0, sx = 1, sy = 1, alpha = 0, ca, sa, x02 = null, y02, x12, y12, kx = 1, ky = 1, transform2 = transformer$2({
    point: function(x2, y2) {
      var p = projection2([x2, y2]);
      this.stream.point(p[0], p[1]);
    }
  }), postclip = identity$2, cache, cacheStream;
  function reset() {
    kx = k * sx;
    ky = k * sy;
    cache = cacheStream = null;
    return projection2;
  }
  function projection2(p) {
    var x2 = p[0] * kx, y2 = p[1] * ky;
    if (alpha) {
      var t = y2 * ca - x2 * sa;
      x2 = x2 * ca + y2 * sa;
      y2 = t;
    }
    return [x2 + tx, y2 + ty];
  }
  projection2.invert = function(p) {
    var x2 = p[0] - tx, y2 = p[1] - ty;
    if (alpha) {
      var t = y2 * ca + x2 * sa;
      x2 = x2 * ca - y2 * sa;
      y2 = t;
    }
    return [x2 / kx, y2 / ky];
  };
  projection2.stream = function(stream) {
    return cache && cacheStream === stream ? cache : cache = transform2(postclip(cacheStream = stream));
  };
  projection2.postclip = function(_) {
    return arguments.length ? (postclip = _, x02 = y02 = x12 = y12 = null, reset()) : postclip;
  };
  projection2.clipExtent = function(_) {
    return arguments.length ? (postclip = _ == null ? (x02 = y02 = x12 = y12 = null, identity$2) : clipRectangle(x02 = +_[0][0], y02 = +_[0][1], x12 = +_[1][0], y12 = +_[1][1]), reset()) : x02 == null ? null : [[x02, y02], [x12, y12]];
  };
  projection2.scale = function(_) {
    return arguments.length ? (k = +_, reset()) : k;
  };
  projection2.translate = function(_) {
    return arguments.length ? (tx = +_[0], ty = +_[1], reset()) : [tx, ty];
  };
  projection2.angle = function(_) {
    return arguments.length ? (alpha = _ % 360 * radians, sa = sin$1(alpha), ca = cos$1(alpha), reset()) : alpha * degrees;
  };
  projection2.reflectX = function(_) {
    return arguments.length ? (sx = _ ? -1 : 1, reset()) : sx < 0;
  };
  projection2.reflectY = function(_) {
    return arguments.length ? (sy = _ ? -1 : 1, reset()) : sy < 0;
  };
  projection2.fitExtent = function(extent, object2) {
    return fitExtent(projection2, extent, object2);
  };
  projection2.fitSize = function(size, object2) {
    return fitSize(projection2, size, object2);
  };
  projection2.fitWidth = function(width, object2) {
    return fitWidth(projection2, width, object2);
  };
  projection2.fitHeight = function(height, object2) {
    return fitHeight(projection2, height, object2);
  };
  return projection2;
}
function naturalEarth1Raw(lambda, phi2) {
  var phi22 = phi2 * phi2, phi4 = phi22 * phi22;
  return [
    lambda * (0.8707 - 0.131979 * phi22 + phi4 * (-0.013791 + phi4 * (3971e-6 * phi22 - 1529e-6 * phi4))),
    phi2 * (1.007226 + phi22 * (0.015085 + phi4 * (-0.044475 + 0.028874 * phi22 - 5916e-6 * phi4)))
  ];
}
naturalEarth1Raw.invert = function(x2, y2) {
  var phi2 = y2, i = 25, delta;
  do {
    var phi22 = phi2 * phi2, phi4 = phi22 * phi22;
    phi2 -= delta = (phi2 * (1.007226 + phi22 * (0.015085 + phi4 * (-0.044475 + 0.028874 * phi22 - 5916e-6 * phi4))) - y2) / (1.007226 + phi22 * (0.015085 * 3 + phi4 * (-0.044475 * 7 + 0.028874 * 9 * phi22 - 5916e-6 * 11 * phi4)));
  } while (abs$1(delta) > epsilon$1 && --i > 0);
  return [
    x2 / (0.8707 + (phi22 = phi2 * phi2) * (-0.131979 + phi22 * (-0.013791 + phi22 * phi22 * phi22 * (3971e-6 - 1529e-6 * phi22)))),
    phi2
  ];
};
function geoNaturalEarth1() {
  return projection(naturalEarth1Raw).scale(175.295);
}
function orthographicRaw(x2, y2) {
  return [cos$1(y2) * sin$1(x2), sin$1(y2)];
}
orthographicRaw.invert = azimuthalInvert(asin$1);
function geoOrthographic() {
  return projection(orthographicRaw).scale(249.5).clipAngle(90 + epsilon$1);
}
function stereographicRaw(x2, y2) {
  var cy = cos$1(y2), k = 1 + cos$1(x2) * cy;
  return [cy * sin$1(x2) / k, sin$1(y2) / k];
}
stereographicRaw.invert = azimuthalInvert(function(z) {
  return 2 * atan(z);
});
function geoStereographic() {
  return projection(stereographicRaw).scale(250).clipAngle(142);
}
function transverseMercatorRaw(lambda, phi2) {
  return [log$1(tan((halfPi$1 + phi2) / 2)), -lambda];
}
transverseMercatorRaw.invert = function(x2, y2) {
  return [-y2, 2 * atan(exp(x2)) - halfPi$1];
};
function geoTransverseMercator() {
  var m2 = mercatorProjection(transverseMercatorRaw), center = m2.center, rotate = m2.rotate;
  m2.center = function(_) {
    return arguments.length ? center([-_[1], _[0]]) : (_ = center(), [_[1], -_[0]]);
  };
  m2.rotate = function(_) {
    return arguments.length ? rotate([_[0], _[1], _.length > 2 ? _[2] + 90 : 90]) : (_ = rotate(), [_[0], _[1], _[2] - 90]);
  };
  return rotate([0, 0, 90]).scale(159.155);
}
function defaultSeparation$1(a2, b) {
  return a2.parent === b.parent ? 1 : 2;
}
function meanX(children) {
  return children.reduce(meanXReduce, 0) / children.length;
}
function meanXReduce(x2, c2) {
  return x2 + c2.x;
}
function maxY(children) {
  return 1 + children.reduce(maxYReduce, 0);
}
function maxYReduce(y2, c2) {
  return Math.max(y2, c2.y);
}
function leafLeft(node) {
  var children;
  while (children = node.children) node = children[0];
  return node;
}
function leafRight(node) {
  var children;
  while (children = node.children) node = children[children.length - 1];
  return node;
}
function cluster() {
  var separation = defaultSeparation$1, dx = 1, dy = 1, nodeSize = false;
  function cluster2(root) {
    var previousNode, x2 = 0;
    root.eachAfter(function(node) {
      var children = node.children;
      if (children) {
        node.x = meanX(children);
        node.y = maxY(children);
      } else {
        node.x = previousNode ? x2 += separation(node, previousNode) : 0;
        node.y = 0;
        previousNode = node;
      }
    });
    var left = leafLeft(root), right = leafRight(root), x02 = left.x - separation(left, right) / 2, x12 = right.x + separation(right, left) / 2;
    return root.eachAfter(nodeSize ? function(node) {
      node.x = (node.x - root.x) * dx;
      node.y = (root.y - node.y) * dy;
    } : function(node) {
      node.x = (node.x - x02) / (x12 - x02) * dx;
      node.y = (1 - (root.y ? node.y / root.y : 1)) * dy;
    });
  }
  cluster2.separation = function(x2) {
    return arguments.length ? (separation = x2, cluster2) : separation;
  };
  cluster2.size = function(x2) {
    return arguments.length ? (nodeSize = false, dx = +x2[0], dy = +x2[1], cluster2) : nodeSize ? null : [dx, dy];
  };
  cluster2.nodeSize = function(x2) {
    return arguments.length ? (nodeSize = true, dx = +x2[0], dy = +x2[1], cluster2) : nodeSize ? [dx, dy] : null;
  };
  return cluster2;
}
const a = 1664525;
const c = 1013904223;
const m = 4294967296;
function lcg() {
  let s = 1;
  return () => (s = (a * s + c) % m) / m;
}
function array(x2) {
  return typeof x2 === "object" && "length" in x2 ? x2 : Array.from(x2);
}
function shuffle(array2, random) {
  let m2 = array2.length, t, i;
  while (m2) {
    i = random() * m2-- | 0;
    t = array2[m2];
    array2[m2] = array2[i];
    array2[i] = t;
  }
  return array2;
}
function packEncloseRandom(circles, random) {
  var i = 0, n = (circles = shuffle(Array.from(circles), random)).length, B2 = [], p, e;
  while (i < n) {
    p = circles[i];
    if (e && enclosesWeak(e, p)) ++i;
    else e = encloseBasis(B2 = extendBasis(B2, p)), i = 0;
  }
  return e;
}
function extendBasis(B2, p) {
  var i, j;
  if (enclosesWeakAll(p, B2)) return [p];
  for (i = 0; i < B2.length; ++i) {
    if (enclosesNot(p, B2[i]) && enclosesWeakAll(encloseBasis2(B2[i], p), B2)) {
      return [B2[i], p];
    }
  }
  for (i = 0; i < B2.length - 1; ++i) {
    for (j = i + 1; j < B2.length; ++j) {
      if (enclosesNot(encloseBasis2(B2[i], B2[j]), p) && enclosesNot(encloseBasis2(B2[i], p), B2[j]) && enclosesNot(encloseBasis2(B2[j], p), B2[i]) && enclosesWeakAll(encloseBasis3(B2[i], B2[j], p), B2)) {
        return [B2[i], B2[j], p];
      }
    }
  }
  throw new Error();
}
function enclosesNot(a2, b) {
  var dr = a2.r - b.r, dx = b.x - a2.x, dy = b.y - a2.y;
  return dr < 0 || dr * dr < dx * dx + dy * dy;
}
function enclosesWeak(a2, b) {
  var dr = a2.r - b.r + Math.max(a2.r, b.r, 1) * 1e-9, dx = b.x - a2.x, dy = b.y - a2.y;
  return dr > 0 && dr * dr > dx * dx + dy * dy;
}
function enclosesWeakAll(a2, B2) {
  for (var i = 0; i < B2.length; ++i) {
    if (!enclosesWeak(a2, B2[i])) {
      return false;
    }
  }
  return true;
}
function encloseBasis(B2) {
  switch (B2.length) {
    case 1:
      return encloseBasis1(B2[0]);
    case 2:
      return encloseBasis2(B2[0], B2[1]);
    case 3:
      return encloseBasis3(B2[0], B2[1], B2[2]);
  }
}
function encloseBasis1(a2) {
  return {
    x: a2.x,
    y: a2.y,
    r: a2.r
  };
}
function encloseBasis2(a2, b) {
  var x12 = a2.x, y12 = a2.y, r1 = a2.r, x2 = b.x, y2 = b.y, r2 = b.r, x21 = x2 - x12, y21 = y2 - y12, r21 = r2 - r1, l = Math.sqrt(x21 * x21 + y21 * y21);
  return {
    x: (x12 + x2 + x21 / l * r21) / 2,
    y: (y12 + y2 + y21 / l * r21) / 2,
    r: (l + r1 + r2) / 2
  };
}
function encloseBasis3(a2, b, c2) {
  var x12 = a2.x, y12 = a2.y, r1 = a2.r, x2 = b.x, y2 = b.y, r2 = b.r, x3 = c2.x, y3 = c2.y, r3 = c2.r, a22 = x12 - x2, a3 = x12 - x3, b2 = y12 - y2, b3 = y12 - y3, c22 = r2 - r1, c3 = r3 - r1, d1 = x12 * x12 + y12 * y12 - r1 * r1, d2 = d1 - x2 * x2 - y2 * y2 + r2 * r2, d3 = d1 - x3 * x3 - y3 * y3 + r3 * r3, ab = a3 * b2 - a22 * b3, xa = (b2 * d3 - b3 * d2) / (ab * 2) - x12, xb = (b3 * c22 - b2 * c3) / ab, ya = (a3 * d2 - a22 * d3) / (ab * 2) - y12, yb = (a22 * c3 - a3 * c22) / ab, A5 = xb * xb + yb * yb - 1, B2 = 2 * (r1 + xa * xb + ya * yb), C3 = xa * xa + ya * ya - r1 * r1, r = -(Math.abs(A5) > 1e-6 ? (B2 + Math.sqrt(B2 * B2 - 4 * A5 * C3)) / (2 * A5) : C3 / B2);
  return {
    x: x12 + xa + xb * r,
    y: y12 + ya + yb * r,
    r
  };
}
function place(b, a2, c2) {
  var dx = b.x - a2.x, x2, a22, dy = b.y - a2.y, y2, b2, d2 = dx * dx + dy * dy;
  if (d2) {
    a22 = a2.r + c2.r, a22 *= a22;
    b2 = b.r + c2.r, b2 *= b2;
    if (a22 > b2) {
      x2 = (d2 + b2 - a22) / (2 * d2);
      y2 = Math.sqrt(Math.max(0, b2 / d2 - x2 * x2));
      c2.x = b.x - x2 * dx - y2 * dy;
      c2.y = b.y - x2 * dy + y2 * dx;
    } else {
      x2 = (d2 + a22 - b2) / (2 * d2);
      y2 = Math.sqrt(Math.max(0, a22 / d2 - x2 * x2));
      c2.x = a2.x + x2 * dx - y2 * dy;
      c2.y = a2.y + x2 * dy + y2 * dx;
    }
  } else {
    c2.x = a2.x + c2.r;
    c2.y = a2.y;
  }
}
function intersects(a2, b) {
  var dr = a2.r + b.r - 1e-6, dx = b.x - a2.x, dy = b.y - a2.y;
  return dr > 0 && dr * dr > dx * dx + dy * dy;
}
function score(node) {
  var a2 = node._, b = node.next._, ab = a2.r + b.r, dx = (a2.x * b.r + b.x * a2.r) / ab, dy = (a2.y * b.r + b.y * a2.r) / ab;
  return dx * dx + dy * dy;
}
function Node(circle2) {
  this._ = circle2;
  this.next = null;
  this.previous = null;
}
function packSiblingsRandom(circles, random) {
  if (!(n = (circles = array(circles)).length)) return 0;
  var a2, b, c2, n, aa, ca, i, j, k, sj, sk;
  a2 = circles[0], a2.x = 0, a2.y = 0;
  if (!(n > 1)) return a2.r;
  b = circles[1], a2.x = -b.r, b.x = a2.r, b.y = 0;
  if (!(n > 2)) return a2.r + b.r;
  place(b, a2, c2 = circles[2]);
  a2 = new Node(a2), b = new Node(b), c2 = new Node(c2);
  a2.next = c2.previous = b;
  b.next = a2.previous = c2;
  c2.next = b.previous = a2;
  pack: for (i = 3; i < n; ++i) {
    place(a2._, b._, c2 = circles[i]), c2 = new Node(c2);
    j = b.next, k = a2.previous, sj = b._.r, sk = a2._.r;
    do {
      if (sj <= sk) {
        if (intersects(j._, c2._)) {
          b = j, a2.next = b, b.previous = a2, --i;
          continue pack;
        }
        sj += j._.r, j = j.next;
      } else {
        if (intersects(k._, c2._)) {
          a2 = k, a2.next = b, b.previous = a2, --i;
          continue pack;
        }
        sk += k._.r, k = k.previous;
      }
    } while (j !== k.next);
    c2.previous = a2, c2.next = b, a2.next = b.previous = b = c2;
    aa = score(a2);
    while ((c2 = c2.next) !== b) {
      if ((ca = score(c2)) < aa) {
        a2 = c2, aa = ca;
      }
    }
    b = a2.next;
  }
  a2 = [b._], c2 = b;
  while ((c2 = c2.next) !== b) a2.push(c2._);
  c2 = packEncloseRandom(a2, random);
  for (i = 0; i < n; ++i) a2 = circles[i], a2.x -= c2.x, a2.y -= c2.y;
  return c2.r;
}
function defaultRadius(d) {
  return Math.sqrt(d.value);
}
function pack() {
  var radius = null, dx = 1, dy = 1, padding = constantZero;
  function pack2(root) {
    const random = lcg();
    root.x = dx / 2, root.y = dy / 2;
    if (radius) {
      root.eachBefore(radiusLeaf(radius)).eachAfter(packChildrenRandom(padding, 0.5, random)).eachBefore(translateChild(1));
    } else {
      root.eachBefore(radiusLeaf(defaultRadius)).eachAfter(packChildrenRandom(constantZero, 1, random)).eachAfter(packChildrenRandom(padding, root.r / Math.min(dx, dy), random)).eachBefore(translateChild(Math.min(dx, dy) / (2 * root.r)));
    }
    return root;
  }
  pack2.radius = function(x2) {
    return arguments.length ? (radius = optional(x2), pack2) : radius;
  };
  pack2.size = function(x2) {
    return arguments.length ? (dx = +x2[0], dy = +x2[1], pack2) : [dx, dy];
  };
  pack2.padding = function(x2) {
    return arguments.length ? (padding = typeof x2 === "function" ? x2 : constant$1(+x2), pack2) : padding;
  };
  return pack2;
}
function radiusLeaf(radius) {
  return function(node) {
    if (!node.children) {
      node.r = Math.max(0, +radius(node) || 0);
    }
  };
}
function packChildrenRandom(padding, k, random) {
  return function(node) {
    if (children = node.children) {
      var children, i, n = children.length, r = padding(node) * k || 0, e;
      if (r) for (i = 0; i < n; ++i) children[i].r += r;
      e = packSiblingsRandom(children, random);
      if (r) for (i = 0; i < n; ++i) children[i].r -= r;
      node.r = e + r;
    }
  };
}
function translateChild(k) {
  return function(node) {
    var parent = node.parent;
    node.r *= k;
    if (parent) {
      node.x = parent.x + k * node.x;
      node.y = parent.y + k * node.y;
    }
  };
}
function partition() {
  var dx = 1, dy = 1, padding = 0, round = false;
  function partition2(root) {
    var n = root.height + 1;
    root.x0 = root.y0 = padding;
    root.x1 = dx;
    root.y1 = dy / n;
    root.eachBefore(positionNode(dy, n));
    if (round) root.eachBefore(roundNode);
    return root;
  }
  function positionNode(dy2, n) {
    return function(node) {
      if (node.children) {
        treemapDice(node, node.x0, dy2 * (node.depth + 1) / n, node.x1, dy2 * (node.depth + 2) / n);
      }
      var x02 = node.x0, y02 = node.y0, x12 = node.x1 - padding, y12 = node.y1 - padding;
      if (x12 < x02) x02 = x12 = (x02 + x12) / 2;
      if (y12 < y02) y02 = y12 = (y02 + y12) / 2;
      node.x0 = x02;
      node.y0 = y02;
      node.x1 = x12;
      node.y1 = y12;
    };
  }
  partition2.round = function(x2) {
    return arguments.length ? (round = !!x2, partition2) : round;
  };
  partition2.size = function(x2) {
    return arguments.length ? (dx = +x2[0], dy = +x2[1], partition2) : [dx, dy];
  };
  partition2.padding = function(x2) {
    return arguments.length ? (padding = +x2, partition2) : padding;
  };
  return partition2;
}
var preroot = { depth: -1 }, ambiguous = {}, imputed = {};
function defaultId(d) {
  return d.id;
}
function defaultParentId(d) {
  return d.parentId;
}
function stratify() {
  var id = defaultId, parentId = defaultParentId, path;
  function stratify2(data) {
    var nodes = Array.from(data), currentId = id, currentParentId = parentId, n, d, i, root, parent, node, nodeId, nodeKey, nodeByKey = /* @__PURE__ */ new Map();
    if (path != null) {
      const I = nodes.map((d2, i2) => normalize(path(d2, i2, data)));
      const P = I.map(parentof);
      const S = new Set(I).add("");
      for (const i2 of P) {
        if (!S.has(i2)) {
          S.add(i2);
          I.push(i2);
          P.push(parentof(i2));
          nodes.push(imputed);
        }
      }
      currentId = (_, i2) => I[i2];
      currentParentId = (_, i2) => P[i2];
    }
    for (i = 0, n = nodes.length; i < n; ++i) {
      d = nodes[i], node = nodes[i] = new Node$1(d);
      if ((nodeId = currentId(d, i, data)) != null && (nodeId += "")) {
        nodeKey = node.id = nodeId;
        nodeByKey.set(nodeKey, nodeByKey.has(nodeKey) ? ambiguous : node);
      }
      if ((nodeId = currentParentId(d, i, data)) != null && (nodeId += "")) {
        node.parent = nodeId;
      }
    }
    for (i = 0; i < n; ++i) {
      node = nodes[i];
      if (nodeId = node.parent) {
        parent = nodeByKey.get(nodeId);
        if (!parent) throw new Error("missing: " + nodeId);
        if (parent === ambiguous) throw new Error("ambiguous: " + nodeId);
        if (parent.children) parent.children.push(node);
        else parent.children = [node];
        node.parent = parent;
      } else {
        if (root) throw new Error("multiple roots");
        root = node;
      }
    }
    if (!root) throw new Error("no root");
    if (path != null) {
      while (root.data === imputed && root.children.length === 1) {
        root = root.children[0], --n;
      }
      for (let i2 = nodes.length - 1; i2 >= 0; --i2) {
        node = nodes[i2];
        if (node.data !== imputed) break;
        node.data = null;
      }
    }
    root.parent = preroot;
    root.eachBefore(function(node2) {
      node2.depth = node2.parent.depth + 1;
      --n;
    }).eachBefore(computeHeight);
    root.parent = null;
    if (n > 0) throw new Error("cycle");
    return root;
  }
  stratify2.id = function(x2) {
    return arguments.length ? (id = optional(x2), stratify2) : id;
  };
  stratify2.parentId = function(x2) {
    return arguments.length ? (parentId = optional(x2), stratify2) : parentId;
  };
  stratify2.path = function(x2) {
    return arguments.length ? (path = optional(x2), stratify2) : path;
  };
  return stratify2;
}
function normalize(path) {
  path = `${path}`;
  let i = path.length;
  if (slash(path, i - 1) && !slash(path, i - 2)) path = path.slice(0, -1);
  return path[0] === "/" ? path : `/${path}`;
}
function parentof(path) {
  let i = path.length;
  if (i < 2) return "";
  while (--i > 1) if (slash(path, i)) break;
  return path.slice(0, i);
}
function slash(path, i) {
  if (path[i] === "/") {
    let k = 0;
    while (i > 0 && path[--i] === "\\") ++k;
    if ((k & 1) === 0) return true;
  }
  return false;
}
function defaultSeparation(a2, b) {
  return a2.parent === b.parent ? 1 : 2;
}
function nextLeft(v) {
  var children = v.children;
  return children ? children[0] : v.t;
}
function nextRight(v) {
  var children = v.children;
  return children ? children[children.length - 1] : v.t;
}
function moveSubtree(wm, wp, shift) {
  var change = shift / (wp.i - wm.i);
  wp.c -= change;
  wp.s += shift;
  wm.c += change;
  wp.z += shift;
  wp.m += shift;
}
function executeShifts(v) {
  var shift = 0, change = 0, children = v.children, i = children.length, w;
  while (--i >= 0) {
    w = children[i];
    w.z += shift;
    w.m += shift;
    shift += w.s + (change += w.c);
  }
}
function nextAncestor(vim, v, ancestor) {
  return vim.a.parent === v.parent ? vim.a : ancestor;
}
function TreeNode(node, i) {
  this._ = node;
  this.parent = null;
  this.children = null;
  this.A = null;
  this.a = this;
  this.z = 0;
  this.m = 0;
  this.c = 0;
  this.s = 0;
  this.t = null;
  this.i = i;
}
TreeNode.prototype = Object.create(Node$1.prototype);
function treeRoot(root) {
  var tree2 = new TreeNode(root, 0), node, nodes = [tree2], child, children, i, n;
  while (node = nodes.pop()) {
    if (children = node._.children) {
      node.children = new Array(n = children.length);
      for (i = n - 1; i >= 0; --i) {
        nodes.push(child = node.children[i] = new TreeNode(children[i], i));
        child.parent = node;
      }
    }
  }
  (tree2.parent = new TreeNode(null, 0)).children = [tree2];
  return tree2;
}
function tree() {
  var separation = defaultSeparation, dx = 1, dy = 1, nodeSize = null;
  function tree2(root) {
    var t = treeRoot(root);
    t.eachAfter(firstWalk), t.parent.m = -t.z;
    t.eachBefore(secondWalk);
    if (nodeSize) root.eachBefore(sizeNode);
    else {
      var left = root, right = root, bottom = root;
      root.eachBefore(function(node) {
        if (node.x < left.x) left = node;
        if (node.x > right.x) right = node;
        if (node.depth > bottom.depth) bottom = node;
      });
      var s = left === right ? 1 : separation(left, right) / 2, tx = s - left.x, kx = dx / (right.x + s + tx), ky = dy / (bottom.depth || 1);
      root.eachBefore(function(node) {
        node.x = (node.x + tx) * kx;
        node.y = node.depth * ky;
      });
    }
    return root;
  }
  function firstWalk(v) {
    var children = v.children, siblings = v.parent.children, w = v.i ? siblings[v.i - 1] : null;
    if (children) {
      executeShifts(v);
      var midpoint = (children[0].z + children[children.length - 1].z) / 2;
      if (w) {
        v.z = w.z + separation(v._, w._);
        v.m = v.z - midpoint;
      } else {
        v.z = midpoint;
      }
    } else if (w) {
      v.z = w.z + separation(v._, w._);
    }
    v.parent.A = apportion(v, w, v.parent.A || siblings[0]);
  }
  function secondWalk(v) {
    v._.x = v.z + v.parent.m;
    v.m += v.parent.m;
  }
  function apportion(v, w, ancestor) {
    if (w) {
      var vip = v, vop = v, vim = w, vom = vip.parent.children[0], sip = vip.m, sop = vop.m, sim = vim.m, som = vom.m, shift;
      while (vim = nextRight(vim), vip = nextLeft(vip), vim && vip) {
        vom = nextLeft(vom);
        vop = nextRight(vop);
        vop.a = v;
        shift = vim.z + sim - vip.z - sip + separation(vim._, vip._);
        if (shift > 0) {
          moveSubtree(nextAncestor(vim, v, ancestor), v, shift);
          sip += shift;
          sop += shift;
        }
        sim += vim.m;
        sip += vip.m;
        som += vom.m;
        sop += vop.m;
      }
      if (vim && !nextRight(vop)) {
        vop.t = vim;
        vop.m += sim - sop;
      }
      if (vip && !nextLeft(vom)) {
        vom.t = vip;
        vom.m += sip - som;
        ancestor = v;
      }
    }
    return ancestor;
  }
  function sizeNode(node) {
    node.x *= dx;
    node.y = node.depth * dy;
  }
  tree2.separation = function(x2) {
    return arguments.length ? (separation = x2, tree2) : separation;
  };
  tree2.size = function(x2) {
    return arguments.length ? (nodeSize = false, dx = +x2[0], dy = +x2[1], tree2) : nodeSize ? null : [dx, dy];
  };
  tree2.nodeSize = function(x2) {
    return arguments.length ? (nodeSize = true, dx = +x2[0], dy = +x2[1], tree2) : nodeSize ? [dx, dy] : null;
  };
  return tree2;
}
function treemapBinary(parent, x02, y02, x12, y12) {
  var nodes = parent.children, i, n = nodes.length, sum2, sums = new Array(n + 1);
  for (sums[0] = sum2 = i = 0; i < n; ++i) {
    sums[i + 1] = sum2 += nodes[i].value;
  }
  partition2(0, n, parent.value, x02, y02, x12, y12);
  function partition2(i2, j, value, x03, y03, x13, y13) {
    if (i2 >= j - 1) {
      var node = nodes[i2];
      node.x0 = x03, node.y0 = y03;
      node.x1 = x13, node.y1 = y13;
      return;
    }
    var valueOffset = sums[i2], valueTarget = value / 2 + valueOffset, k = i2 + 1, hi = j - 1;
    while (k < hi) {
      var mid = k + hi >>> 1;
      if (sums[mid] < valueTarget) k = mid + 1;
      else hi = mid;
    }
    if (valueTarget - sums[k - 1] < sums[k] - valueTarget && i2 + 1 < k) --k;
    var valueLeft = sums[k] - valueOffset, valueRight = value - valueLeft;
    if (x13 - x03 > y13 - y03) {
      var xk = value ? (x03 * valueRight + x13 * valueLeft) / value : x13;
      partition2(i2, k, valueLeft, x03, y03, xk, y13);
      partition2(k, j, valueRight, xk, y03, x13, y13);
    } else {
      var yk = value ? (y03 * valueRight + y13 * valueLeft) / value : y13;
      partition2(i2, k, valueLeft, x03, y03, x13, yk);
      partition2(k, j, valueRight, x03, yk, x13, y13);
    }
  }
}
function treemapSliceDice(parent, x02, y02, x12, y12) {
  (parent.depth & 1 ? treemapSlice : treemapDice)(parent, x02, y02, x12, y12);
}
const treemapResquarify = (function custom(ratio) {
  function resquarify(parent, x02, y02, x12, y12) {
    if ((rows = parent._squarify) && rows.ratio === ratio) {
      var rows, row, nodes, i, j = -1, n, m2 = rows.length, value = parent.value;
      while (++j < m2) {
        row = rows[j], nodes = row.children;
        for (i = row.value = 0, n = nodes.length; i < n; ++i) row.value += nodes[i].value;
        if (row.dice) treemapDice(row, x02, y02, x12, value ? y02 += (y12 - y02) * row.value / value : y12);
        else treemapSlice(row, x02, y02, value ? x02 += (x12 - x02) * row.value / value : x12, y12);
        value -= row.value;
      }
    } else {
      parent._squarify = rows = squarifyRatio(ratio, parent, x02, y02, x12, y12);
      rows.ratio = ratio;
    }
  }
  resquarify.ratio = function(x2) {
    return custom((x2 = +x2) > 1 ? x2 : 1);
  };
  return resquarify;
})(phi);
function identity$1(domain) {
  var unknown;
  function scale(x2) {
    return x2 == null || isNaN(x2 = +x2) ? unknown : x2;
  }
  scale.invert = scale;
  scale.domain = scale.range = function(_) {
    return arguments.length ? (domain = Array.from(_, number$1), scale) : domain.slice();
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  scale.copy = function() {
    return identity$1(domain).unknown(unknown);
  };
  domain = arguments.length ? Array.from(domain, number$1) : [0, 1];
  return linearish(scale);
}
function transformLog(x2) {
  return Math.log(x2);
}
function transformExp(x2) {
  return Math.exp(x2);
}
function transformLogn(x2) {
  return -Math.log(-x2);
}
function transformExpn(x2) {
  return -Math.exp(-x2);
}
function pow10(x2) {
  return isFinite(x2) ? +("1e" + x2) : x2 < 0 ? 0 : x2;
}
function powp(base) {
  return base === 10 ? pow10 : base === Math.E ? Math.exp : (x2) => Math.pow(base, x2);
}
function logp(base) {
  return base === Math.E ? Math.log : base === 10 && Math.log10 || base === 2 && Math.log2 || (base = Math.log(base), (x2) => Math.log(x2) / base);
}
function reflect(f) {
  return (x2, k) => -f(-x2, k);
}
function loggish(transform2) {
  const scale = transform2(transformLog, transformExp);
  const domain = scale.domain;
  let base = 10;
  let logs;
  let pows;
  function rescale() {
    logs = logp(base), pows = powp(base);
    if (domain()[0] < 0) {
      logs = reflect(logs), pows = reflect(pows);
      transform2(transformLogn, transformExpn);
    } else {
      transform2(transformLog, transformExp);
    }
    return scale;
  }
  scale.base = function(_) {
    return arguments.length ? (base = +_, rescale()) : base;
  };
  scale.domain = function(_) {
    return arguments.length ? (domain(_), rescale()) : domain();
  };
  scale.ticks = (count) => {
    const d = domain();
    let u2 = d[0];
    let v = d[d.length - 1];
    const r = v < u2;
    if (r) [u2, v] = [v, u2];
    let i = logs(u2);
    let j = logs(v);
    let k;
    let t;
    const n = count == null ? 10 : +count;
    let z = [];
    if (!(base % 1) && j - i < n) {
      i = Math.floor(i), j = Math.ceil(j);
      if (u2 > 0) for (; i <= j; ++i) {
        for (k = 1; k < base; ++k) {
          t = i < 0 ? k / pows(-i) : k * pows(i);
          if (t < u2) continue;
          if (t > v) break;
          z.push(t);
        }
      }
      else for (; i <= j; ++i) {
        for (k = base - 1; k >= 1; --k) {
          t = i > 0 ? k / pows(-i) : k * pows(i);
          if (t < u2) continue;
          if (t > v) break;
          z.push(t);
        }
      }
      if (z.length * 2 < n) z = ticks(u2, v, n);
    } else {
      z = ticks(i, j, Math.min(j - i, n)).map(pows);
    }
    return r ? z.reverse() : z;
  };
  scale.tickFormat = (count, specifier) => {
    if (count == null) count = 10;
    if (specifier == null) specifier = base === 10 ? "s" : ",";
    if (typeof specifier !== "function") {
      if (!(base % 1) && (specifier = formatSpecifier(specifier)).precision == null) specifier.trim = true;
      specifier = format(specifier);
    }
    if (count === Infinity) return specifier;
    const k = Math.max(1, base * count / scale.ticks().length);
    return (d) => {
      let i = d / pows(Math.round(logs(d)));
      if (i * base < base - 0.5) i *= base;
      return i <= k ? specifier(d) : "";
    };
  };
  scale.nice = () => {
    return domain(nice(domain(), {
      floor: (x2) => pows(Math.floor(logs(x2))),
      ceil: (x2) => pows(Math.ceil(logs(x2)))
    }));
  };
  return scale;
}
function log() {
  const scale = loggish(transformer$3()).domain([1, 10]);
  scale.copy = () => copy$1(scale, log()).base(scale.base());
  initRange.apply(scale, arguments);
  return scale;
}
function transformSymlog(c2) {
  return function(x2) {
    return Math.sign(x2) * Math.log1p(Math.abs(x2 / c2));
  };
}
function transformSymexp(c2) {
  return function(x2) {
    return Math.sign(x2) * Math.expm1(Math.abs(x2)) * c2;
  };
}
function symlogish(transform2) {
  var c2 = 1, scale = transform2(transformSymlog(c2), transformSymexp(c2));
  scale.constant = function(_) {
    return arguments.length ? transform2(transformSymlog(c2 = +_), transformSymexp(c2)) : c2;
  };
  return linearish(scale);
}
function symlog() {
  var scale = symlogish(transformer$3());
  scale.copy = function() {
    return copy$1(scale, symlog()).constant(scale.constant());
  };
  return initRange.apply(scale, arguments);
}
function transformPow(exponent) {
  return function(x2) {
    return x2 < 0 ? -Math.pow(-x2, exponent) : Math.pow(x2, exponent);
  };
}
function transformSqrt(x2) {
  return x2 < 0 ? -Math.sqrt(-x2) : Math.sqrt(x2);
}
function transformSquare(x2) {
  return x2 < 0 ? -x2 * x2 : x2 * x2;
}
function powish(transform2) {
  var scale = transform2(identity$3, identity$3), exponent = 1;
  function rescale() {
    return exponent === 1 ? transform2(identity$3, identity$3) : exponent === 0.5 ? transform2(transformSqrt, transformSquare) : transform2(transformPow(exponent), transformPow(1 / exponent));
  }
  scale.exponent = function(_) {
    return arguments.length ? (exponent = +_, rescale()) : exponent;
  };
  return linearish(scale);
}
function pow() {
  var scale = powish(transformer$3());
  scale.copy = function() {
    return copy$1(scale, pow()).exponent(scale.exponent());
  };
  initRange.apply(scale, arguments);
  return scale;
}
function sqrt$1() {
  return pow.apply(null, arguments).exponent(0.5);
}
function quantile() {
  var domain = [], range2 = [], thresholds = [], unknown;
  function rescale() {
    var i = 0, n = Math.max(1, range2.length);
    thresholds = new Array(n - 1);
    while (++i < n) thresholds[i - 1] = quantileSorted(domain, i / n);
    return scale;
  }
  function scale(x2) {
    return x2 == null || isNaN(x2 = +x2) ? unknown : range2[bisectRight(thresholds, x2)];
  }
  scale.invertExtent = function(y2) {
    var i = range2.indexOf(y2);
    return i < 0 ? [NaN, NaN] : [
      i > 0 ? thresholds[i - 1] : domain[0],
      i < thresholds.length ? thresholds[i] : domain[domain.length - 1]
    ];
  };
  scale.domain = function(_) {
    if (!arguments.length) return domain.slice();
    domain = [];
    for (let d of _) if (d != null && !isNaN(d = +d)) domain.push(d);
    domain.sort(ascending);
    return rescale();
  };
  scale.range = function(_) {
    return arguments.length ? (range2 = Array.from(_), rescale()) : range2.slice();
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  scale.quantiles = function() {
    return thresholds.slice();
  };
  scale.copy = function() {
    return quantile().domain(domain).range(range2).unknown(unknown);
  };
  return initRange.apply(scale, arguments);
}
function quantize() {
  var x02 = 0, x12 = 1, n = 1, domain = [0.5], range2 = [0, 1], unknown;
  function scale(x2) {
    return x2 != null && x2 <= x2 ? range2[bisectRight(domain, x2, 0, n)] : unknown;
  }
  function rescale() {
    var i = -1;
    domain = new Array(n);
    while (++i < n) domain[i] = ((i + 1) * x12 - (i - n) * x02) / (n + 1);
    return scale;
  }
  scale.domain = function(_) {
    return arguments.length ? ([x02, x12] = _, x02 = +x02, x12 = +x12, rescale()) : [x02, x12];
  };
  scale.range = function(_) {
    return arguments.length ? (n = (range2 = Array.from(_)).length - 1, rescale()) : range2.slice();
  };
  scale.invertExtent = function(y2) {
    var i = range2.indexOf(y2);
    return i < 0 ? [NaN, NaN] : i < 1 ? [x02, domain[0]] : i >= n ? [domain[n - 1], x12] : [domain[i - 1], domain[i]];
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : scale;
  };
  scale.thresholds = function() {
    return domain.slice();
  };
  scale.copy = function() {
    return quantize().domain([x02, x12]).range(range2).unknown(unknown);
  };
  return initRange.apply(linearish(scale), arguments);
}
function threshold() {
  var domain = [0.5], range2 = [0, 1], unknown, n = 1;
  function scale(x2) {
    return x2 != null && x2 <= x2 ? range2[bisectRight(domain, x2, 0, n)] : unknown;
  }
  scale.domain = function(_) {
    return arguments.length ? (domain = Array.from(_), n = Math.min(domain.length, range2.length - 1), scale) : domain.slice();
  };
  scale.range = function(_) {
    return arguments.length ? (range2 = Array.from(_), n = Math.min(domain.length, range2.length - 1), scale) : range2.slice();
  };
  scale.invertExtent = function(y2) {
    var i = range2.indexOf(y2);
    return [domain[i - 1], domain[i]];
  };
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  scale.copy = function() {
    return threshold().domain(domain).range(range2).unknown(unknown);
  };
  return initRange.apply(scale, arguments);
}
function utcTime() {
  return initRange.apply(calendar(utcTicks, utcTickInterval, utcYear, utcMonth, utcSunday, utcDay, utcHour, utcMinute, second, utcFormat).domain([Date.UTC(2e3, 0, 1), Date.UTC(2e3, 0, 2)]), arguments);
}
function transformer$1() {
  var x02 = 0, x12 = 1, t0, t1, k10, transform2, interpolator = identity$3, clamp = false, unknown;
  function scale(x2) {
    return x2 == null || isNaN(x2 = +x2) ? unknown : interpolator(k10 === 0 ? 0.5 : (x2 = (transform2(x2) - t0) * k10, clamp ? Math.max(0, Math.min(1, x2)) : x2));
  }
  scale.domain = function(_) {
    return arguments.length ? ([x02, x12] = _, t0 = transform2(x02 = +x02), t1 = transform2(x12 = +x12), k10 = t0 === t1 ? 0 : 1 / (t1 - t0), scale) : [x02, x12];
  };
  scale.clamp = function(_) {
    return arguments.length ? (clamp = !!_, scale) : clamp;
  };
  scale.interpolator = function(_) {
    return arguments.length ? (interpolator = _, scale) : interpolator;
  };
  function range2(interpolate) {
    return function(_) {
      var r0, r1;
      return arguments.length ? ([r0, r1] = _, interpolator = interpolate(r0, r1), scale) : [interpolator(0), interpolator(1)];
    };
  }
  scale.range = range2(interpolate$1);
  scale.rangeRound = range2(interpolateRound);
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  return function(t) {
    transform2 = t, t0 = t(x02), t1 = t(x12), k10 = t0 === t1 ? 0 : 1 / (t1 - t0);
    return scale;
  };
}
function copy(source, target) {
  return target.domain(source.domain()).interpolator(source.interpolator()).clamp(source.clamp()).unknown(source.unknown());
}
function sequential() {
  var scale = linearish(transformer$1()(identity$3));
  scale.copy = function() {
    return copy(scale, sequential());
  };
  return initInterpolator.apply(scale, arguments);
}
function sequentialLog() {
  var scale = loggish(transformer$1()).domain([1, 10]);
  scale.copy = function() {
    return copy(scale, sequentialLog()).base(scale.base());
  };
  return initInterpolator.apply(scale, arguments);
}
function sequentialSymlog() {
  var scale = symlogish(transformer$1());
  scale.copy = function() {
    return copy(scale, sequentialSymlog()).constant(scale.constant());
  };
  return initInterpolator.apply(scale, arguments);
}
function sequentialPow() {
  var scale = powish(transformer$1());
  scale.copy = function() {
    return copy(scale, sequentialPow()).exponent(scale.exponent());
  };
  return initInterpolator.apply(scale, arguments);
}
function sequentialSqrt() {
  return sequentialPow.apply(null, arguments).exponent(0.5);
}
function transformer() {
  var x02 = 0, x12 = 0.5, x2 = 1, s = 1, t0, t1, t2, k10, k21, interpolator = identity$3, transform2, clamp = false, unknown;
  function scale(x3) {
    return isNaN(x3 = +x3) ? unknown : (x3 = 0.5 + ((x3 = +transform2(x3)) - t1) * (s * x3 < s * t1 ? k10 : k21), interpolator(clamp ? Math.max(0, Math.min(1, x3)) : x3));
  }
  scale.domain = function(_) {
    return arguments.length ? ([x02, x12, x2] = _, t0 = transform2(x02 = +x02), t1 = transform2(x12 = +x12), t2 = transform2(x2 = +x2), k10 = t0 === t1 ? 0 : 0.5 / (t1 - t0), k21 = t1 === t2 ? 0 : 0.5 / (t2 - t1), s = t1 < t0 ? -1 : 1, scale) : [x02, x12, x2];
  };
  scale.clamp = function(_) {
    return arguments.length ? (clamp = !!_, scale) : clamp;
  };
  scale.interpolator = function(_) {
    return arguments.length ? (interpolator = _, scale) : interpolator;
  };
  function range2(interpolate) {
    return function(_) {
      var r0, r1, r2;
      return arguments.length ? ([r0, r1, r2] = _, interpolator = piecewise(interpolate, [r0, r1, r2]), scale) : [interpolator(0), interpolator(0.5), interpolator(1)];
    };
  }
  scale.range = range2(interpolate$1);
  scale.rangeRound = range2(interpolateRound);
  scale.unknown = function(_) {
    return arguments.length ? (unknown = _, scale) : unknown;
  };
  return function(t) {
    transform2 = t, t0 = t(x02), t1 = t(x12), t2 = t(x2), k10 = t0 === t1 ? 0 : 0.5 / (t1 - t0), k21 = t1 === t2 ? 0 : 0.5 / (t2 - t1), s = t1 < t0 ? -1 : 1;
    return scale;
  };
}
function diverging() {
  var scale = linearish(transformer()(identity$3));
  scale.copy = function() {
    return copy(scale, diverging());
  };
  return initInterpolator.apply(scale, arguments);
}
function divergingLog() {
  var scale = loggish(transformer()).domain([0.1, 1, 10]);
  scale.copy = function() {
    return copy(scale, divergingLog()).base(scale.base());
  };
  return initInterpolator.apply(scale, arguments);
}
function divergingSymlog() {
  var scale = symlogish(transformer());
  scale.copy = function() {
    return copy(scale, divergingSymlog()).constant(scale.constant());
  };
  return initInterpolator.apply(scale, arguments);
}
function divergingPow() {
  var scale = powish(transformer());
  scale.copy = function() {
    return copy(scale, divergingPow()).exponent(scale.exponent());
  };
  return initInterpolator.apply(scale, arguments);
}
function divergingSqrt() {
  return divergingPow.apply(null, arguments).exponent(0.5);
}
const schemeCategory10 = colors("1f77b4ff7f0e2ca02cd627289467bd8c564be377c27f7f7fbcbd2217becf");
const schemeAccent = colors("7fc97fbeaed4fdc086ffff99386cb0f0027fbf5b17666666");
const schemeDark2 = colors("1b9e77d95f027570b3e7298a66a61ee6ab02a6761d666666");
const schemeObservable10 = colors("4269d0efb118ff725c6cc5b03ca951ff8ab7a463f297bbf59c6b4e9498a0");
const schemePaired = colors("a6cee31f78b4b2df8a33a02cfb9a99e31a1cfdbf6fff7f00cab2d66a3d9affff99b15928");
const schemePastel1 = colors("fbb4aeb3cde3ccebc5decbe4fed9a6ffffcce5d8bdfddaecf2f2f2");
const schemePastel2 = colors("b3e2cdfdcdaccbd5e8f4cae4e6f5c9fff2aef1e2cccccccc");
const schemeSet1 = colors("e41a1c377eb84daf4a984ea3ff7f00ffff33a65628f781bf999999");
const schemeSet2 = colors("66c2a5fc8d628da0cbe78ac3a6d854ffd92fe5c494b3b3b3");
const schemeSet3 = colors("8dd3c7ffffb3bebadafb807280b1d3fdb462b3de69fccde5d9d9d9bc80bdccebc5ffed6f");
function area$2(x02, y02, y12) {
  var x12 = null, defined = constant$2(true), context = null, curve = curveLinear, output = null, path = withPath(area);
  x02 = typeof x02 === "function" ? x02 : x02 === void 0 ? x$2 : constant$2(+x02);
  y02 = typeof y02 === "function" ? y02 : y02 === void 0 ? constant$2(0) : constant$2(+y02);
  y12 = typeof y12 === "function" ? y12 : y12 === void 0 ? y$2 : constant$2(+y12);
  function area(data) {
    var i, j, k, n = (data = array$2(data)).length, d, defined0 = false, buffer, x0z = new Array(n), y0z = new Array(n);
    if (context == null) output = curve(buffer = path());
    for (i = 0; i <= n; ++i) {
      if (!(i < n && defined(d = data[i], i, data)) === defined0) {
        if (defined0 = !defined0) {
          j = i;
          output.areaStart();
          output.lineStart();
        } else {
          output.lineEnd();
          output.lineStart();
          for (k = i - 1; k >= j; --k) {
            output.point(x0z[k], y0z[k]);
          }
          output.lineEnd();
          output.areaEnd();
        }
      }
      if (defined0) {
        x0z[i] = +x02(d, i, data), y0z[i] = +y02(d, i, data);
        output.point(x12 ? +x12(d, i, data) : x0z[i], y12 ? +y12(d, i, data) : y0z[i]);
      }
    }
    if (buffer) return output = null, buffer + "" || null;
  }
  function arealine() {
    return line().defined(defined).curve(curve).context(context);
  }
  area.x = function(_) {
    return arguments.length ? (x02 = typeof _ === "function" ? _ : constant$2(+_), x12 = null, area) : x02;
  };
  area.x0 = function(_) {
    return arguments.length ? (x02 = typeof _ === "function" ? _ : constant$2(+_), area) : x02;
  };
  area.x1 = function(_) {
    return arguments.length ? (x12 = _ == null ? null : typeof _ === "function" ? _ : constant$2(+_), area) : x12;
  };
  area.y = function(_) {
    return arguments.length ? (y02 = typeof _ === "function" ? _ : constant$2(+_), y12 = null, area) : y02;
  };
  area.y0 = function(_) {
    return arguments.length ? (y02 = typeof _ === "function" ? _ : constant$2(+_), area) : y02;
  };
  area.y1 = function(_) {
    return arguments.length ? (y12 = _ == null ? null : typeof _ === "function" ? _ : constant$2(+_), area) : y12;
  };
  area.lineX0 = area.lineY0 = function() {
    return arealine().x(x02).y(y02);
  };
  area.lineY1 = function() {
    return arealine().x(x02).y(y12);
  };
  area.lineX1 = function() {
    return arealine().x(x12).y(y02);
  };
  area.defined = function(_) {
    return arguments.length ? (defined = typeof _ === "function" ? _ : constant$2(!!_), area) : defined;
  };
  area.curve = function(_) {
    return arguments.length ? (curve = _, context != null && (output = curve(context)), area) : curve;
  };
  area.context = function(_) {
    return arguments.length ? (_ == null ? context = output = null : output = curve(context = _), area) : context;
  };
  return area;
}
const circle = {
  draw(context, size) {
    const r = sqrt$3(size / pi$2);
    context.moveTo(r, 0);
    context.arc(0, 0, r, 0, tau$2);
  }
};
function Symbol$1(type, size) {
  let context = null, path = withPath(symbol);
  type = typeof type === "function" ? type : constant$2(type || circle);
  size = typeof size === "function" ? size : constant$2(size === void 0 ? 64 : +size);
  function symbol() {
    let buffer;
    if (!context) context = buffer = path();
    type.apply(this, arguments).draw(context, +size.apply(this, arguments));
    if (buffer) return context = null, buffer + "" || null;
  }
  symbol.type = function(_) {
    return arguments.length ? (type = typeof _ === "function" ? _ : constant$2(_), symbol) : type;
  };
  symbol.size = function(_) {
    return arguments.length ? (size = typeof _ === "function" ? _ : constant$2(+_), symbol) : size;
  };
  symbol.context = function(_) {
    return arguments.length ? (context = _ == null ? null : _, symbol) : context;
  };
  return symbol;
}
const stringOrChar = /("(?:[^\\"]|\\.)*")|[:,]/g;
function stringify(passedObj, options = {}) {
  const indent = JSON.stringify(
    [1],
    void 0,
    options.indent === void 0 ? 2 : options.indent
  ).slice(2, -3);
  const maxLength = indent === "" ? Infinity : options.maxLength === void 0 ? 80 : options.maxLength;
  let { replacer } = options;
  return (function _stringify(obj, currentIndent, reserved) {
    if (obj && typeof obj.toJSON === "function") {
      obj = obj.toJSON();
    }
    const string = JSON.stringify(obj, replacer);
    if (string === void 0) {
      return string;
    }
    const length = maxLength - currentIndent.length - reserved;
    if (string.length <= length) {
      const prettified = string.replace(
        stringOrChar,
        (match, stringLiteral) => {
          return stringLiteral || `${match} `;
        }
      );
      if (prettified.length <= length) {
        return prettified;
      }
    }
    if (replacer != null) {
      obj = JSON.parse(string);
      replacer = void 0;
    }
    if (typeof obj === "object" && obj !== null) {
      const nextIndent = currentIndent + indent;
      const items = [];
      let index2 = 0;
      let start;
      let end;
      if (Array.isArray(obj)) {
        start = "[";
        end = "]";
        const { length: length2 } = obj;
        for (; index2 < length2; index2++) {
          items.push(
            _stringify(obj[index2], nextIndent, index2 === length2 - 1 ? 0 : 1) || "null"
          );
        }
      } else {
        start = "{";
        end = "}";
        const keys = Object.keys(obj);
        const { length: length2 } = keys;
        for (; index2 < length2; index2++) {
          const key = keys[index2];
          const keyPart = `${JSON.stringify(key)}: `;
          const value = _stringify(
            obj[key],
            nextIndent,
            keyPart.length + (index2 === length2 - 1 ? 0 : 1)
          );
          if (value !== void 0) {
            items.push(keyPart + value);
          }
        }
      }
      if (items.length > 0) {
        return [start, indent + items.join(`,
${nextIndent}`), end].join(
          `
${currentIndent}`
        );
      }
    }
    return string;
  })(passedObj, "", 0);
}
function identity(x2) {
  return x2;
}
function transform(transform2) {
  if (transform2 == null) return identity;
  var x02, y02, kx = transform2.scale[0], ky = transform2.scale[1], dx = transform2.translate[0], dy = transform2.translate[1];
  return function(input, i) {
    if (!i) x02 = y02 = 0;
    var j = 2, n = input.length, output = new Array(n);
    output[0] = (x02 += input[0]) * kx + dx;
    output[1] = (y02 += input[1]) * ky + dy;
    while (j < n) output[j] = input[j], ++j;
    return output;
  };
}
function reverse(array2, n) {
  var t, j = array2.length, i = j - n;
  while (i < --j) t = array2[i], array2[i++] = array2[j], array2[j] = t;
}
function feature(topology, o) {
  if (typeof o === "string") o = topology.objects[o];
  return o.type === "GeometryCollection" ? { type: "FeatureCollection", features: o.geometries.map(function(o2) {
    return feature$1(topology, o2);
  }) } : feature$1(topology, o);
}
function feature$1(topology, o) {
  var id = o.id, bbox = o.bbox, properties = o.properties == null ? {} : o.properties, geometry = object(topology, o);
  return id == null && bbox == null ? { type: "Feature", properties, geometry } : bbox == null ? { type: "Feature", id, properties, geometry } : { type: "Feature", id, bbox, properties, geometry };
}
function object(topology, o) {
  var transformPoint = transform(topology.transform), arcs = topology.arcs;
  function arc(i, points) {
    if (points.length) points.pop();
    for (var a2 = arcs[i < 0 ? ~i : i], k = 0, n = a2.length; k < n; ++k) {
      points.push(transformPoint(a2[k], k));
    }
    if (i < 0) reverse(points, n);
  }
  function point(p) {
    return transformPoint(p);
  }
  function line2(arcs2) {
    var points = [];
    for (var i = 0, n = arcs2.length; i < n; ++i) arc(arcs2[i], points);
    if (points.length < 2) points.push(points[0]);
    return points;
  }
  function ring(arcs2) {
    var points = line2(arcs2);
    while (points.length < 4) points.push(points[0]);
    return points;
  }
  function polygon(arcs2) {
    return arcs2.map(ring);
  }
  function geometry(o2) {
    var type = o2.type, coordinates;
    switch (type) {
      case "GeometryCollection":
        return { type, geometries: o2.geometries.map(geometry) };
      case "Point":
        coordinates = point(o2.coordinates);
        break;
      case "MultiPoint":
        coordinates = o2.coordinates.map(point);
        break;
      case "LineString":
        coordinates = line2(o2.arcs);
        break;
      case "MultiLineString":
        coordinates = o2.arcs.map(line2);
        break;
      case "Polygon":
        coordinates = polygon(o2.arcs);
        break;
      case "MultiPolygon":
        coordinates = o2.arcs.map(polygon);
        break;
      default:
        return null;
    }
    return { type, coordinates };
  }
  return geometry(o);
}
function stitch(topology, arcs) {
  var stitchedArcs = {}, fragmentByStart = {}, fragmentByEnd = {}, fragments = [], emptyIndex = -1;
  arcs.forEach(function(i, j) {
    var arc = topology.arcs[i < 0 ? ~i : i], t;
    if (arc.length < 3 && !arc[1][0] && !arc[1][1]) {
      t = arcs[++emptyIndex], arcs[emptyIndex] = i, arcs[j] = t;
    }
  });
  arcs.forEach(function(i) {
    var e = ends(i), start = e[0], end = e[1], f, g;
    if (f = fragmentByEnd[start]) {
      delete fragmentByEnd[f.end];
      f.push(i);
      f.end = end;
      if (g = fragmentByStart[end]) {
        delete fragmentByStart[g.start];
        var fg = g === f ? f : f.concat(g);
        fragmentByStart[fg.start = f.start] = fragmentByEnd[fg.end = g.end] = fg;
      } else {
        fragmentByStart[f.start] = fragmentByEnd[f.end] = f;
      }
    } else if (f = fragmentByStart[end]) {
      delete fragmentByStart[f.start];
      f.unshift(i);
      f.start = start;
      if (g = fragmentByEnd[start]) {
        delete fragmentByEnd[g.end];
        var gf = g === f ? f : g.concat(f);
        fragmentByStart[gf.start = g.start] = fragmentByEnd[gf.end = f.end] = gf;
      } else {
        fragmentByStart[f.start] = fragmentByEnd[f.end] = f;
      }
    } else {
      f = [i];
      fragmentByStart[f.start = start] = fragmentByEnd[f.end = end] = f;
    }
  });
  function ends(i) {
    var arc = topology.arcs[i < 0 ? ~i : i], p02 = arc[0], p1;
    if (topology.transform) p1 = [0, 0], arc.forEach(function(dp) {
      p1[0] += dp[0], p1[1] += dp[1];
    });
    else p1 = arc[arc.length - 1];
    return i < 0 ? [p1, p02] : [p02, p1];
  }
  function flush(fragmentByEnd2, fragmentByStart2) {
    for (var k in fragmentByEnd2) {
      var f = fragmentByEnd2[k];
      delete fragmentByStart2[f.start];
      delete f.start;
      delete f.end;
      f.forEach(function(i) {
        stitchedArcs[i < 0 ? ~i : i] = 1;
      });
      fragments.push(f);
    }
  }
  flush(fragmentByEnd, fragmentByStart);
  flush(fragmentByStart, fragmentByEnd);
  arcs.forEach(function(i) {
    if (!stitchedArcs[i < 0 ? ~i : i]) fragments.push([i]);
  });
  return fragments;
}
function mesh(topology) {
  return object(topology, meshArcs.apply(this, arguments));
}
function meshArcs(topology, object2, filter) {
  var arcs, i, n;
  if (arguments.length > 1) arcs = extractArcs(topology, object2, filter);
  else for (i = 0, arcs = new Array(n = topology.arcs.length); i < n; ++i) arcs[i] = i;
  return { type: "MultiLineString", arcs: stitch(topology, arcs) };
}
function extractArcs(topology, object2, filter) {
  var arcs = [], geomsByArc = [], geom;
  function extract0(i) {
    var j = i < 0 ? ~i : i;
    (geomsByArc[j] || (geomsByArc[j] = [])).push({ i, g: geom });
  }
  function extract1(arcs2) {
    arcs2.forEach(extract0);
  }
  function extract2(arcs2) {
    arcs2.forEach(extract1);
  }
  function extract3(arcs2) {
    arcs2.forEach(extract2);
  }
  function geometry(o) {
    switch (geom = o, o.type) {
      case "GeometryCollection":
        o.geometries.forEach(geometry);
        break;
      case "LineString":
        extract1(o.arcs);
        break;
      case "MultiLineString":
      case "Polygon":
        extract2(o.arcs);
        break;
      case "MultiPolygon":
        extract3(o.arcs);
        break;
    }
  }
  geometry(object2);
  geomsByArc.forEach(filter == null ? function(geoms) {
    arcs.push(geoms[0].i);
  } : function(geoms) {
    if (filter(geoms[0].g, geoms[geoms.length - 1].g)) arcs.push(geoms[0].i);
  });
  return arcs;
}
var abs = Math.abs;
var cos = Math.cos;
var sin = Math.sin;
var epsilon = 1e-6;
var pi = Math.PI;
var halfPi = pi / 2;
var sqrt2 = sqrt(2);
function asin(x2) {
  return x2 > 1 ? halfPi : x2 < -1 ? -halfPi : Math.asin(x2);
}
function sqrt(x2) {
  return x2 > 0 ? Math.sqrt(x2) : 0;
}
function mollweideBromleyTheta(cp, phi2) {
  var cpsinPhi = cp * sin(phi2), i = 30, delta;
  do
    phi2 -= delta = (phi2 + sin(phi2) - cpsinPhi) / (1 + cos(phi2));
  while (abs(delta) > epsilon && --i > 0);
  return phi2 / 2;
}
function mollweideBromleyRaw(cx, cy, cp) {
  function forward(lambda, phi2) {
    return [cx * lambda * cos(phi2 = mollweideBromleyTheta(cp, phi2)), cy * sin(phi2)];
  }
  forward.invert = function(x2, y2) {
    return y2 = asin(y2 / cy), [x2 / (cx * cos(y2)), asin((2 * y2 + sin(2 * y2)) / cp)];
  };
  return forward;
}
var mollweideRaw = mollweideBromleyRaw(sqrt2 / halfPi, sqrt2, pi);
function geoMollweide() {
  return projection(mollweideRaw).scale(169.529);
}
export {
  $$1 as $,
  threshold as A,
  schemeSet3 as B,
  schemeSet2 as C,
  schemeSet1 as D,
  schemePastel2 as E,
  schemePastel1 as F,
  schemePaired as G,
  schemeObservable10 as H,
  schemeDark2 as I,
  schemeCategory10 as J,
  schemeAccent as K,
  area$2 as L,
  sum$1 as M,
  geoTransverseMercator as N,
  geoStereographic as O,
  geoOrthographic as P,
  geoNaturalEarth1 as Q,
  geoMollweide as R,
  Symbol$1 as S,
  geoMercator as T,
  geoIdentity as U,
  geoGnomonic as V,
  geoEquirectangular as W,
  geoEqualEarth as X,
  geoConicEquidistant as Y,
  geoConicEqualArea as Z,
  geoConicConformal as _,
  quantileSorted as a,
  geoAzimuthalEquidistant as a0,
  geoAzimuthalEqualArea as a1,
  geoAlbersUsa as a2,
  geoAlbers as a3,
  geoPath as a4,
  graticule as a5,
  forceSimulation as a6,
  forceY as a7,
  forceX as a8,
  forceLink as a9,
  forceManyBody as aa,
  forceCollide as ab,
  forceCenter as ac,
  pack as ad,
  partition as ae,
  stratify as af,
  cluster as ag,
  tree as ah,
  treemapResquarify as ai,
  treemapSliceDice as aj,
  treemapBinary as ak,
  Delaunay as al,
  permute as am,
  intersection as an,
  union as ao,
  geoBounds$1 as ap,
  geoCentroid$1 as aq,
  geoArea$1 as ar,
  interval as as,
  stringify as at,
  median as b,
  mean as c,
  deviation as d,
  pow as e,
  feature as f,
  symlog as g,
  sequential as h,
  identity$1 as i,
  sequentialLog as j,
  sequentialPow as k,
  log as l,
  mesh as m,
  sequentialSqrt as n,
  sequentialSymlog as o,
  piecewise as p,
  quantile$1 as q,
  diverging as r,
  sqrt$1 as s,
  divergingLog as t,
  utcTime as u,
  divergingPow as v,
  divergingSqrt as w,
  divergingSymlog as x,
  quantile as y,
  quantize as z
};
//# sourceMappingURL=B5Kxxbk_.js.map
