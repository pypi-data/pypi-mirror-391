var jr = (e) => {
  throw TypeError(e);
};
var Nr = (e, t, r) => t.has(e) || jr("Cannot " + r);
var De = (e, t, r) => (Nr(e, t, "read from private field"), r ? r.call(e) : t.get(e)), Fr = (e, t, r) => t.has(e) ? jr("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(e) : t.set(e, r), kr = (e, t, r, n) => (Nr(e, t, "write to private field"), n ? n.call(e, r) : t.set(e, r), r);
import { i as Ho, a as he, r as Bo, b as Wo, Z as pt, g as Vo, c as O, d as Sr, e as gt, o as zr } from "./Index-COss7Uox.js";
const M = window.ms_globals.React, u = window.ms_globals.React, Fo = window.ms_globals.React.isValidElement, ko = window.ms_globals.React.version, re = window.ms_globals.React.useRef, Ao = window.ms_globals.React.useLayoutEffect, _e = window.ms_globals.React.useEffect, zo = window.ms_globals.React.useCallback, ue = window.ms_globals.React.useMemo, Do = window.ms_globals.React.forwardRef, Ye = window.ms_globals.React.useState, Ar = window.ms_globals.ReactDOM, bt = window.ms_globals.ReactDOM.createPortal, An = window.ms_globals.antdIcons.FileTextFilled, Xo = window.ms_globals.antdIcons.CloseCircleFilled, Uo = window.ms_globals.antdIcons.FileExcelFilled, Go = window.ms_globals.antdIcons.FileImageFilled, Ko = window.ms_globals.antdIcons.FileMarkdownFilled, qo = window.ms_globals.antdIcons.FilePdfFilled, Yo = window.ms_globals.antdIcons.FilePptFilled, Zo = window.ms_globals.antdIcons.FileWordFilled, Qo = window.ms_globals.antdIcons.FileZipFilled, Jo = window.ms_globals.antdIcons.PlusOutlined, ei = window.ms_globals.antdIcons.LeftOutlined, ti = window.ms_globals.antdIcons.RightOutlined, ri = window.ms_globals.antdIcons.CloseOutlined, zn = window.ms_globals.antdIcons.CheckOutlined, ni = window.ms_globals.antdIcons.DeleteOutlined, oi = window.ms_globals.antdIcons.EditOutlined, ii = window.ms_globals.antdIcons.SyncOutlined, si = window.ms_globals.antdIcons.DislikeOutlined, ai = window.ms_globals.antdIcons.LikeOutlined, li = window.ms_globals.antdIcons.CopyOutlined, ci = window.ms_globals.antdIcons.EyeOutlined, ui = window.ms_globals.antdIcons.ArrowDownOutlined, fi = window.ms_globals.antd.ConfigProvider, Ze = window.ms_globals.antd.theme, Dn = window.ms_globals.antd.Upload, di = window.ms_globals.antd.Progress, mi = window.ms_globals.antd.Image, ie = window.ms_globals.antd.Button, Ee = window.ms_globals.antd.Flex, Te = window.ms_globals.antd.Typography, pi = window.ms_globals.antd.Avatar, gi = window.ms_globals.antd.Popconfirm, hi = window.ms_globals.antd.Tooltip, yi = window.ms_globals.antd.Collapse, vi = window.ms_globals.antd.Input, Hn = window.ms_globals.createItemsContext.createItemsContext, bi = window.ms_globals.internalContext.useContextPropsContext, Dr = window.ms_globals.internalContext.ContextPropsProvider, Ve = window.ms_globals.antdCssinjs.unit, Ut = window.ms_globals.antdCssinjs.token2CSSVar, Hr = window.ms_globals.antdCssinjs.useStyleRegister, Si = window.ms_globals.antdCssinjs.useCSSVarRegister, xi = window.ms_globals.antdCssinjs.createTheme, wi = window.ms_globals.antdCssinjs.useCacheToken, Bn = window.ms_globals.antdCssinjs.Keyframes, St = window.ms_globals.components.Markdown;
var _i = /\s/;
function Ei(e) {
  for (var t = e.length; t-- && _i.test(e.charAt(t)); )
    ;
  return t;
}
var Ci = /^\s+/;
function Ti(e) {
  return e && e.slice(0, Ei(e) + 1).replace(Ci, "");
}
var Br = NaN, $i = /^[-+]0x[0-9a-f]+$/i, Ii = /^0b[01]+$/i, Pi = /^0o[0-7]+$/i, Ri = parseInt;
function Wr(e) {
  if (typeof e == "number")
    return e;
  if (Ho(e))
    return Br;
  if (he(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = he(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Ti(e);
  var r = Ii.test(e);
  return r || Pi.test(e) ? Ri(e.slice(2), r ? 2 : 8) : $i.test(e) ? Br : +e;
}
var Gt = function() {
  return Bo.Date.now();
}, Mi = "Expected a function", Li = Math.max, Oi = Math.min;
function ji(e, t, r) {
  var n, o, i, s, a, l, c = 0, d = !1, m = !1, f = !0;
  if (typeof e != "function")
    throw new TypeError(Mi);
  t = Wr(t) || 0, he(r) && (d = !!r.leading, m = "maxWait" in r, i = m ? Li(Wr(r.maxWait) || 0, t) : i, f = "trailing" in r ? !!r.trailing : f);
  function p(v) {
    var R = n, P = o;
    return n = o = void 0, c = v, s = e.apply(P, R), s;
  }
  function y(v) {
    return c = v, a = setTimeout(x, t), d ? p(v) : s;
  }
  function h(v) {
    var R = v - l, P = v - c, j = t - R;
    return m ? Oi(j, i - P) : j;
  }
  function g(v) {
    var R = v - l, P = v - c;
    return l === void 0 || R >= t || R < 0 || m && P >= i;
  }
  function x() {
    var v = Gt();
    if (g(v))
      return _(v);
    a = setTimeout(x, h(v));
  }
  function _(v) {
    return a = void 0, f && n ? p(v) : (n = o = void 0, s);
  }
  function w() {
    a !== void 0 && clearTimeout(a), c = 0, n = l = o = a = void 0;
  }
  function $() {
    return a === void 0 ? s : _(Gt());
  }
  function I() {
    var v = Gt(), R = g(v);
    if (n = arguments, o = this, l = v, R) {
      if (a === void 0)
        return y(l);
      if (m)
        return clearTimeout(a), a = setTimeout(x, t), p(l);
    }
    return a === void 0 && (a = setTimeout(x, t)), s;
  }
  return I.cancel = w, I.flush = $, I;
}
function Ni(e, t) {
  return Wo(e, t);
}
var Wn = {
  exports: {}
}, Tt = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Fi = u, ki = Symbol.for("react.element"), Ai = Symbol.for("react.fragment"), zi = Object.prototype.hasOwnProperty, Di = Fi.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Hi = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Vn(e, t, r) {
  var n, o = {}, i = null, s = null;
  r !== void 0 && (i = "" + r), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) zi.call(t, n) && !Hi.hasOwnProperty(n) && (o[n] = t[n]);
  if (e && e.defaultProps) for (n in t = e.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: ki,
    type: e,
    key: i,
    ref: s,
    props: o,
    _owner: Di.current
  };
}
Tt.Fragment = Ai;
Tt.jsx = Vn;
Tt.jsxs = Vn;
Wn.exports = Tt;
var S = Wn.exports;
const {
  SvelteComponent: Bi,
  assign: Vr,
  binding_callbacks: Xr,
  check_outros: Wi,
  children: Xn,
  claim_element: Un,
  claim_space: Vi,
  component_subscribe: Ur,
  compute_slots: Xi,
  create_slot: Ui,
  detach: He,
  element: Gn,
  empty: Gr,
  exclude_internal_props: Kr,
  get_all_dirty_from_scope: Gi,
  get_slot_changes: Ki,
  group_outros: qi,
  init: Yi,
  insert_hydration: ht,
  safe_not_equal: Zi,
  set_custom_element_data: Kn,
  space: Qi,
  transition_in: yt,
  transition_out: or,
  update_slot_base: Ji
} = window.__gradio__svelte__internal, {
  beforeUpdate: es,
  getContext: ts,
  onDestroy: rs,
  setContext: ns
} = window.__gradio__svelte__internal;
function qr(e) {
  let t, r;
  const n = (
    /*#slots*/
    e[7].default
  ), o = Ui(
    n,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Gn("svelte-slot"), o && o.c(), this.h();
    },
    l(i) {
      t = Un(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = Xn(t);
      o && o.l(s), s.forEach(He), this.h();
    },
    h() {
      Kn(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      ht(i, t, s), o && o.m(t, null), e[9](t), r = !0;
    },
    p(i, s) {
      o && o.p && (!r || s & /*$$scope*/
      64) && Ji(
        o,
        n,
        i,
        /*$$scope*/
        i[6],
        r ? Ki(
          n,
          /*$$scope*/
          i[6],
          s,
          null
        ) : Gi(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      r || (yt(o, i), r = !0);
    },
    o(i) {
      or(o, i), r = !1;
    },
    d(i) {
      i && He(t), o && o.d(i), e[9](null);
    }
  };
}
function os(e) {
  let t, r, n, o, i = (
    /*$$slots*/
    e[4].default && qr(e)
  );
  return {
    c() {
      t = Gn("react-portal-target"), r = Qi(), i && i.c(), n = Gr(), this.h();
    },
    l(s) {
      t = Un(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), Xn(t).forEach(He), r = Vi(s), i && i.l(s), n = Gr(), this.h();
    },
    h() {
      Kn(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      ht(s, t, a), e[8](t), ht(s, r, a), i && i.m(s, a), ht(s, n, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && yt(i, 1)) : (i = qr(s), i.c(), yt(i, 1), i.m(n.parentNode, n)) : i && (qi(), or(i, 1, 1, () => {
        i = null;
      }), Wi());
    },
    i(s) {
      o || (yt(i), o = !0);
    },
    o(s) {
      or(i), o = !1;
    },
    d(s) {
      s && (He(t), He(r), He(n)), e[8](null), i && i.d(s);
    }
  };
}
function Yr(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function is(e, t, r) {
  let n, o, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = Xi(i);
  let {
    svelteInit: l
  } = t;
  const c = pt(Yr(t)), d = pt();
  Ur(e, d, ($) => r(0, n = $));
  const m = pt();
  Ur(e, m, ($) => r(1, o = $));
  const f = [], p = ts("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: h,
    subSlotIndex: g
  } = Vo() || {}, x = l({
    parent: p,
    props: c,
    target: d,
    slot: m,
    slotKey: y,
    slotIndex: h,
    subSlotIndex: g,
    onDestroy($) {
      f.push($);
    }
  });
  ns("$$ms-gr-react-wrapper", x), es(() => {
    c.set(Yr(t));
  }), rs(() => {
    f.forEach(($) => $());
  });
  function _($) {
    Xr[$ ? "unshift" : "push"](() => {
      n = $, d.set(n);
    });
  }
  function w($) {
    Xr[$ ? "unshift" : "push"](() => {
      o = $, m.set(o);
    });
  }
  return e.$$set = ($) => {
    r(17, t = Vr(Vr({}, t), Kr($))), "svelteInit" in $ && r(5, l = $.svelteInit), "$$scope" in $ && r(6, s = $.$$scope);
  }, t = Kr(t), [n, o, d, m, a, l, s, i, _, w];
}
class ss extends Bi {
  constructor(t) {
    super(), Yi(this, t, is, os, Zi, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Sc
} = window.__gradio__svelte__internal, Zr = window.ms_globals.rerender, Kt = window.ms_globals.tree;
function as(e, t = {}) {
  function r(n) {
    const o = pt(), i = new ss({
      ...n,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, l = s.parent ?? Kt;
          return l.nodes = [...l.nodes, a], Zr({
            createPortal: bt,
            node: Kt
          }), s.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== o), Zr({
              createPortal: bt,
              node: Kt
            });
          }), a;
        },
        ...n.props
      }
    });
    return o.set(i), i;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      n(r);
    });
  });
}
const ls = "1.6.1";
function ye() {
  return ye = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var r = arguments[t];
      for (var n in r) ({}).hasOwnProperty.call(r, n) && (e[n] = r[n]);
    }
    return e;
  }, ye.apply(null, arguments);
}
function $e(e) {
  "@babel/helpers - typeof";
  return $e = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, $e(e);
}
function cs(e, t) {
  if ($e(e) != "object" || !e) return e;
  var r = e[Symbol.toPrimitive];
  if (r !== void 0) {
    var n = r.call(e, t);
    if ($e(n) != "object") return n;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function us(e) {
  var t = cs(e, "string");
  return $e(t) == "symbol" ? t : t + "";
}
function fs(e, t, r) {
  return (t = us(t)) in e ? Object.defineProperty(e, t, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = r, e;
}
function Qr(e, t) {
  var r = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var n = Object.getOwnPropertySymbols(e);
    t && (n = n.filter(function(o) {
      return Object.getOwnPropertyDescriptor(e, o).enumerable;
    })), r.push.apply(r, n);
  }
  return r;
}
function ds(e) {
  for (var t = 1; t < arguments.length; t++) {
    var r = arguments[t] != null ? arguments[t] : {};
    t % 2 ? Qr(Object(r), !0).forEach(function(n) {
      fs(e, n, r[n]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : Qr(Object(r)).forEach(function(n) {
      Object.defineProperty(e, n, Object.getOwnPropertyDescriptor(r, n));
    });
  }
  return e;
}
var ms = `accept acceptCharset accessKey action allowFullScreen allowTransparency
    alt async autoComplete autoFocus autoPlay capture cellPadding cellSpacing challenge
    charSet checked classID className colSpan cols content contentEditable contextMenu
    controls coords crossOrigin data dateTime default defer dir disabled download draggable
    encType form formAction formEncType formMethod formNoValidate formTarget frameBorder
    headers height hidden high href hrefLang htmlFor httpEquiv icon id inputMode integrity
    is keyParams keyType kind label lang list loop low manifest marginHeight marginWidth max maxLength media
    mediaGroup method min minLength multiple muted name noValidate nonce open
    optimum pattern placeholder poster preload radioGroup readOnly rel required
    reversed role rowSpan rows sandbox scope scoped scrolling seamless selected
    shape size sizes span spellCheck src srcDoc srcLang srcSet start step style
    summary tabIndex target title type useMap value width wmode wrap`, ps = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, gs = "".concat(ms, " ").concat(ps).split(/[\s\n]+/), hs = "aria-", ys = "data-";
function Jr(e, t) {
  return e.indexOf(t) === 0;
}
function vs(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, r;
  t === !1 ? r = {
    aria: !0,
    data: !0,
    attr: !0
  } : t === !0 ? r = {
    aria: !0
  } : r = ds({}, t);
  var n = {};
  return Object.keys(e).forEach(function(o) {
    // Aria
    (r.aria && (o === "role" || Jr(o, hs)) || // Data
    r.data && Jr(o, ys) || // Attr
    r.attr && gs.includes(o)) && (n[o] = e[o]);
  }), n;
}
const bs = /* @__PURE__ */ u.createContext({}), Ss = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, $t = (e) => {
  const t = u.useContext(bs);
  return u.useMemo(() => ({
    ...Ss,
    ...t[e]
  }), [t[e]]);
};
function Ie() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: n,
    theme: o
  } = u.useContext(fi.ConfigContext);
  return {
    theme: o,
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: n
  };
}
function se(e) {
  "@babel/helpers - typeof";
  return se = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, se(e);
}
function xs(e) {
  if (Array.isArray(e)) return e;
}
function ws(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var n, o, i, s, a = [], l = !0, c = !1;
    try {
      if (i = (r = r.call(e)).next, t === 0) {
        if (Object(r) !== r) return;
        l = !1;
      } else for (; !(l = (n = i.call(r)).done) && (a.push(n.value), a.length !== t); l = !0) ;
    } catch (d) {
      c = !0, o = d;
    } finally {
      try {
        if (!l && r.return != null && (s = r.return(), Object(s) !== s)) return;
      } finally {
        if (c) throw o;
      }
    }
    return a;
  }
}
function en(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, n = Array(t); r < t; r++) n[r] = e[r];
  return n;
}
function _s(e, t) {
  if (e) {
    if (typeof e == "string") return en(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? en(e, t) : void 0;
  }
}
function Es() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function fe(e, t) {
  return xs(e) || ws(e, t) || _s(e, t) || Es();
}
function Cs(e, t) {
  if (se(e) != "object" || !e) return e;
  var r = e[Symbol.toPrimitive];
  if (r !== void 0) {
    var n = r.call(e, t);
    if (se(n) != "object") return n;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function qn(e) {
  var t = Cs(e, "string");
  return se(t) == "symbol" ? t : t + "";
}
function A(e, t, r) {
  return (t = qn(t)) in e ? Object.defineProperty(e, t, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = r, e;
}
function tn(e, t) {
  var r = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var n = Object.getOwnPropertySymbols(e);
    t && (n = n.filter(function(o) {
      return Object.getOwnPropertyDescriptor(e, o).enumerable;
    })), r.push.apply(r, n);
  }
  return r;
}
function k(e) {
  for (var t = 1; t < arguments.length; t++) {
    var r = arguments[t] != null ? arguments[t] : {};
    t % 2 ? tn(Object(r), !0).forEach(function(n) {
      A(e, n, r[n]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : tn(Object(r)).forEach(function(n) {
      Object.defineProperty(e, n, Object.getOwnPropertyDescriptor(r, n));
    });
  }
  return e;
}
function Ue(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function rn(e, t) {
  for (var r = 0; r < t.length; r++) {
    var n = t[r];
    n.enumerable = n.enumerable || !1, n.configurable = !0, "value" in n && (n.writable = !0), Object.defineProperty(e, qn(n.key), n);
  }
}
function Ge(e, t, r) {
  return t && rn(e.prototype, t), r && rn(e, r), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function Le(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function ir(e, t) {
  return ir = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
    return r.__proto__ = n, r;
  }, ir(e, t);
}
function It(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && ir(e, t);
}
function xt(e) {
  return xt = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, xt(e);
}
function Yn() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Yn = function() {
    return !!e;
  })();
}
function Ts(e, t) {
  if (t && (se(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Le(e);
}
function Pt(e) {
  var t = Yn();
  return function() {
    var r, n = xt(e);
    if (t) {
      var o = xt(this).constructor;
      r = Reflect.construct(n, arguments, o);
    } else r = n.apply(this, arguments);
    return Ts(this, r);
  };
}
var Zn = /* @__PURE__ */ Ge(function e() {
  Ue(this, e);
}), Qn = "CALC_UNIT", $s = new RegExp(Qn, "g");
function qt(e) {
  return typeof e == "number" ? "".concat(e).concat(Qn) : e;
}
var Is = /* @__PURE__ */ function(e) {
  It(r, e);
  var t = Pt(r);
  function r(n, o) {
    var i;
    Ue(this, r), i = t.call(this), A(Le(i), "result", ""), A(Le(i), "unitlessCssVar", void 0), A(Le(i), "lowPriority", void 0);
    var s = se(n);
    return i.unitlessCssVar = o, n instanceof r ? i.result = "(".concat(n.result, ")") : s === "number" ? i.result = qt(n) : s === "string" && (i.result = n), i;
  }
  return Ge(r, [{
    key: "add",
    value: function(o) {
      return o instanceof r ? this.result = "".concat(this.result, " + ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " + ").concat(qt(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof r ? this.result = "".concat(this.result, " - ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " - ").concat(qt(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(o) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), o instanceof r ? this.result = "".concat(this.result, " * ").concat(o.getResult(!0)) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " * ").concat(o)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(o) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), o instanceof r ? this.result = "".concat(this.result, " / ").concat(o.getResult(!0)) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " / ").concat(o)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(o) {
      return this.lowPriority || o ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(o) {
      var i = this, s = o || {}, a = s.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(c) {
        return i.result.includes(c);
      }) && (l = !1), this.result = this.result.replace($s, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), r;
}(Zn), Ps = /* @__PURE__ */ function(e) {
  It(r, e);
  var t = Pt(r);
  function r(n) {
    var o;
    return Ue(this, r), o = t.call(this), A(Le(o), "result", 0), n instanceof r ? o.result = n.result : typeof n == "number" && (o.result = n), o;
  }
  return Ge(r, [{
    key: "add",
    value: function(o) {
      return o instanceof r ? this.result += o.result : typeof o == "number" && (this.result += o), this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof r ? this.result -= o.result : typeof o == "number" && (this.result -= o), this;
    }
  }, {
    key: "mul",
    value: function(o) {
      return o instanceof r ? this.result *= o.result : typeof o == "number" && (this.result *= o), this;
    }
  }, {
    key: "div",
    value: function(o) {
      return o instanceof r ? this.result /= o.result : typeof o == "number" && (this.result /= o), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), r;
}(Zn), Rs = function(t, r) {
  var n = t === "css" ? Is : Ps;
  return function(o) {
    return new n(o, r);
  };
}, nn = function(t, r) {
  return "".concat([r, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function Oe(e) {
  var t = M.useRef();
  t.current = e;
  var r = M.useCallback(function() {
    for (var n, o = arguments.length, i = new Array(o), s = 0; s < o; s++)
      i[s] = arguments[s];
    return (n = t.current) === null || n === void 0 ? void 0 : n.call.apply(n, [t].concat(i));
  }, []);
  return r;
}
function Ms(e) {
  if (Array.isArray(e)) return e;
}
function Ls(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var n, o, i, s, a = [], l = !0, c = !1;
    try {
      if (i = (r = r.call(e)).next, t !== 0) for (; !(l = (n = i.call(r)).done) && (a.push(n.value), a.length !== t); l = !0) ;
    } catch (d) {
      c = !0, o = d;
    } finally {
      try {
        if (!l && r.return != null && (s = r.return(), Object(s) !== s)) return;
      } finally {
        if (c) throw o;
      }
    }
    return a;
  }
}
function on(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, n = Array(t); r < t; r++) n[r] = e[r];
  return n;
}
function Os(e, t) {
  if (e) {
    if (typeof e == "string") return on(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? on(e, t) : void 0;
  }
}
function js() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function wt(e, t) {
  return Ms(e) || Ls(e, t) || Os(e, t) || js();
}
function Rt() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var sn = Rt() ? M.useLayoutEffect : M.useEffect, Jn = function(t, r) {
  var n = M.useRef(!0);
  sn(function() {
    return t(n.current);
  }, r), sn(function() {
    return n.current = !1, function() {
      n.current = !0;
    };
  }, []);
}, an = function(t, r) {
  Jn(function(n) {
    if (!n)
      return t();
  }, r);
};
function Qe(e) {
  var t = M.useRef(!1), r = M.useState(e), n = wt(r, 2), o = n[0], i = n[1];
  M.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, l) {
    l && t.current || i(a);
  }
  return [o, s];
}
function Yt(e) {
  return e !== void 0;
}
function Ns(e, t) {
  var r = t || {}, n = r.defaultValue, o = r.value, i = r.onChange, s = r.postState, a = Qe(function() {
    return Yt(o) ? o : Yt(n) ? typeof n == "function" ? n() : n : typeof e == "function" ? e() : e;
  }), l = wt(a, 2), c = l[0], d = l[1], m = o !== void 0 ? o : c, f = s ? s(m) : m, p = Oe(i), y = Qe([m]), h = wt(y, 2), g = h[0], x = h[1];
  an(function() {
    var w = g[0];
    c !== w && p(c, w);
  }, [g]), an(function() {
    Yt(o) || d(o);
  }, [o]);
  var _ = Oe(function(w, $) {
    d(w, $), x([m], $);
  });
  return [f, _];
}
var eo = {
  exports: {}
}, H = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var xr = Symbol.for("react.element"), wr = Symbol.for("react.portal"), Mt = Symbol.for("react.fragment"), Lt = Symbol.for("react.strict_mode"), Ot = Symbol.for("react.profiler"), jt = Symbol.for("react.provider"), Nt = Symbol.for("react.context"), Fs = Symbol.for("react.server_context"), Ft = Symbol.for("react.forward_ref"), kt = Symbol.for("react.suspense"), At = Symbol.for("react.suspense_list"), zt = Symbol.for("react.memo"), Dt = Symbol.for("react.lazy"), ks = Symbol.for("react.offscreen"), to;
to = Symbol.for("react.module.reference");
function de(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case xr:
        switch (e = e.type, e) {
          case Mt:
          case Ot:
          case Lt:
          case kt:
          case At:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Fs:
              case Nt:
              case Ft:
              case Dt:
              case zt:
              case jt:
                return e;
              default:
                return t;
            }
        }
      case wr:
        return t;
    }
  }
}
H.ContextConsumer = Nt;
H.ContextProvider = jt;
H.Element = xr;
H.ForwardRef = Ft;
H.Fragment = Mt;
H.Lazy = Dt;
H.Memo = zt;
H.Portal = wr;
H.Profiler = Ot;
H.StrictMode = Lt;
H.Suspense = kt;
H.SuspenseList = At;
H.isAsyncMode = function() {
  return !1;
};
H.isConcurrentMode = function() {
  return !1;
};
H.isContextConsumer = function(e) {
  return de(e) === Nt;
};
H.isContextProvider = function(e) {
  return de(e) === jt;
};
H.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === xr;
};
H.isForwardRef = function(e) {
  return de(e) === Ft;
};
H.isFragment = function(e) {
  return de(e) === Mt;
};
H.isLazy = function(e) {
  return de(e) === Dt;
};
H.isMemo = function(e) {
  return de(e) === zt;
};
H.isPortal = function(e) {
  return de(e) === wr;
};
H.isProfiler = function(e) {
  return de(e) === Ot;
};
H.isStrictMode = function(e) {
  return de(e) === Lt;
};
H.isSuspense = function(e) {
  return de(e) === kt;
};
H.isSuspenseList = function(e) {
  return de(e) === At;
};
H.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === Mt || e === Ot || e === Lt || e === kt || e === At || e === ks || typeof e == "object" && e !== null && (e.$$typeof === Dt || e.$$typeof === zt || e.$$typeof === jt || e.$$typeof === Nt || e.$$typeof === Ft || e.$$typeof === to || e.getModuleId !== void 0);
};
H.typeOf = de;
eo.exports = H;
var Zt = eo.exports, As = Symbol.for("react.element"), zs = Symbol.for("react.transitional.element"), Ds = Symbol.for("react.fragment");
function Hs(e) {
  return (
    // Base object type
    e && $e(e) === "object" && // React Element type
    (e.$$typeof === As || e.$$typeof === zs) && // React Fragment type
    e.type === Ds
  );
}
var Bs = Number(ko.split(".")[0]), Ws = function(t, r) {
  typeof t == "function" ? t(r) : $e(t) === "object" && t && "current" in t && (t.current = r);
}, Vs = function(t) {
  var r, n;
  if (!t)
    return !1;
  if (ro(t) && Bs >= 19)
    return !0;
  var o = Zt.isMemo(t) ? t.type.type : t.type;
  return !(typeof o == "function" && !((r = o.prototype) !== null && r !== void 0 && r.render) && o.$$typeof !== Zt.ForwardRef || typeof t == "function" && !((n = t.prototype) !== null && n !== void 0 && n.render) && t.$$typeof !== Zt.ForwardRef);
};
function ro(e) {
  return /* @__PURE__ */ Fo(e) && !Hs(e);
}
var Xs = function(t) {
  if (t && ro(t)) {
    var r = t;
    return r.props.propertyIsEnumerable("ref") ? r.props.ref : r.ref;
  }
  return null;
};
function ln(e, t, r, n) {
  var o = k({}, t[e]);
  if (n != null && n.deprecatedTokens) {
    var i = n.deprecatedTokens;
    i.forEach(function(a) {
      var l = fe(a, 2), c = l[0], d = l[1];
      if (o != null && o[c] || o != null && o[d]) {
        var m;
        (m = o[d]) !== null && m !== void 0 || (o[d] = o == null ? void 0 : o[c]);
      }
    });
  }
  var s = k(k({}, r), o);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var no = typeof CSSINJS_STATISTIC < "u", sr = !0;
function Ke() {
  for (var e = arguments.length, t = new Array(e), r = 0; r < e; r++)
    t[r] = arguments[r];
  if (!no)
    return Object.assign.apply(Object, [{}].concat(t));
  sr = !1;
  var n = {};
  return t.forEach(function(o) {
    if (se(o) === "object") {
      var i = Object.keys(o);
      i.forEach(function(s) {
        Object.defineProperty(n, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return o[s];
          }
        });
      });
    }
  }), sr = !0, n;
}
var cn = {};
function Us() {
}
var Gs = function(t) {
  var r, n = t, o = Us;
  return no && typeof Proxy < "u" && (r = /* @__PURE__ */ new Set(), n = new Proxy(t, {
    get: function(s, a) {
      if (sr) {
        var l;
        (l = r) === null || l === void 0 || l.add(a);
      }
      return s[a];
    }
  }), o = function(s, a) {
    var l;
    cn[s] = {
      global: Array.from(r),
      component: k(k({}, (l = cn[s]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: n,
    keys: r,
    flush: o
  };
};
function un(e, t, r) {
  if (typeof r == "function") {
    var n;
    return r(Ke(t, (n = t[e]) !== null && n !== void 0 ? n : {}));
  }
  return r ?? {};
}
function Ks(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var r = arguments.length, n = new Array(r), o = 0; o < r; o++)
        n[o] = arguments[o];
      return "max(".concat(n.map(function(i) {
        return Ve(i);
      }).join(","), ")");
    },
    min: function() {
      for (var r = arguments.length, n = new Array(r), o = 0; o < r; o++)
        n[o] = arguments[o];
      return "min(".concat(n.map(function(i) {
        return Ve(i);
      }).join(","), ")");
    }
  };
}
var qs = 1e3 * 60 * 10, Ys = /* @__PURE__ */ function() {
  function e() {
    Ue(this, e), A(this, "map", /* @__PURE__ */ new Map()), A(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), A(this, "nextID", 0), A(this, "lastAccessBeat", /* @__PURE__ */ new Map()), A(this, "accessBeat", 0);
  }
  return Ge(e, [{
    key: "set",
    value: function(r, n) {
      this.clear();
      var o = this.getCompositeKey(r);
      this.map.set(o, n), this.lastAccessBeat.set(o, Date.now());
    }
  }, {
    key: "get",
    value: function(r) {
      var n = this.getCompositeKey(r), o = this.map.get(n);
      return this.lastAccessBeat.set(n, Date.now()), this.accessBeat += 1, o;
    }
  }, {
    key: "getCompositeKey",
    value: function(r) {
      var n = this, o = r.map(function(i) {
        return i && se(i) === "object" ? "obj_".concat(n.getObjectID(i)) : "".concat(se(i), "_").concat(i);
      });
      return o.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(r) {
      if (this.objectIDMap.has(r))
        return this.objectIDMap.get(r);
      var n = this.nextID;
      return this.objectIDMap.set(r, n), this.nextID += 1, n;
    }
  }, {
    key: "clear",
    value: function() {
      var r = this;
      if (this.accessBeat > 1e4) {
        var n = Date.now();
        this.lastAccessBeat.forEach(function(o, i) {
          n - o > qs && (r.map.delete(i), r.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), fn = new Ys();
function Zs(e, t) {
  return u.useMemo(function() {
    var r = fn.get(t);
    if (r)
      return r;
    var n = e();
    return fn.set(t, n), n;
  }, t);
}
var Qs = function() {
  return {};
};
function Js(e) {
  var t = e.useCSP, r = t === void 0 ? Qs : t, n = e.useToken, o = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function l(f, p, y, h) {
    var g = Array.isArray(f) ? f[0] : f;
    function x(P) {
      return "".concat(String(g)).concat(P.slice(0, 1).toUpperCase()).concat(P.slice(1));
    }
    var _ = (h == null ? void 0 : h.unitless) || {}, w = typeof a == "function" ? a(f) : {}, $ = k(k({}, w), {}, A({}, x("zIndexPopup"), !0));
    Object.keys(_).forEach(function(P) {
      $[x(P)] = _[P];
    });
    var I = k(k({}, h), {}, {
      unitless: $,
      prefixToken: x
    }), v = d(f, p, y, I), R = c(g, y, I);
    return function(P) {
      var j = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : P, T = v(P, j), L = fe(T, 2), N = L[1], b = R(j), E = fe(b, 2), F = E[0], D = E[1];
      return [F, N, D];
    };
  }
  function c(f, p, y) {
    var h = y.unitless, g = y.injectStyle, x = g === void 0 ? !0 : g, _ = y.prefixToken, w = y.ignore, $ = function(R) {
      var P = R.rootCls, j = R.cssVar, T = j === void 0 ? {} : j, L = n(), N = L.realToken;
      return Si({
        path: [f],
        prefix: T.prefix,
        key: T.key,
        unitless: h,
        ignore: w,
        token: N,
        scope: P
      }, function() {
        var b = un(f, N, p), E = ln(f, N, b, {
          deprecatedTokens: y == null ? void 0 : y.deprecatedTokens
        });
        return Object.keys(b).forEach(function(F) {
          E[_(F)] = E[F], delete E[F];
        }), E;
      }), null;
    }, I = function(R) {
      var P = n(), j = P.cssVar;
      return [function(T) {
        return x && j ? /* @__PURE__ */ u.createElement(u.Fragment, null, /* @__PURE__ */ u.createElement($, {
          rootCls: R,
          cssVar: j,
          component: f
        }), T) : T;
      }, j == null ? void 0 : j.key];
    };
    return I;
  }
  function d(f, p, y) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(f) ? f : [f, f], x = fe(g, 1), _ = x[0], w = g.join("-"), $ = e.layer || {
      name: "antd"
    };
    return function(I) {
      var v = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : I, R = n(), P = R.theme, j = R.realToken, T = R.hashId, L = R.token, N = R.cssVar, b = o(), E = b.rootPrefixCls, F = b.iconPrefixCls, D = r(), B = N ? "css" : "js", z = Zs(function() {
        var V = /* @__PURE__ */ new Set();
        return N && Object.keys(h.unitless || {}).forEach(function(q) {
          V.add(Ut(q, N.prefix)), V.add(Ut(q, nn(_, N.prefix)));
        }), Rs(B, V);
      }, [B, _, N == null ? void 0 : N.prefix]), W = Ks(B), oe = W.max, G = W.min, J = {
        theme: P,
        token: L,
        hashId: T,
        nonce: function() {
          return D.nonce;
        },
        clientOnly: h.clientOnly,
        layer: $,
        // antd is always at top of styles
        order: h.order || -999
      };
      typeof i == "function" && Hr(k(k({}, J), {}, {
        clientOnly: !1,
        path: ["Shared", E]
      }), function() {
        return i(L, {
          prefix: {
            rootPrefixCls: E,
            iconPrefixCls: F
          },
          csp: D
        });
      });
      var U = Hr(k(k({}, J), {}, {
        path: [w, I, F]
      }), function() {
        if (h.injectStyle === !1)
          return [];
        var V = Gs(L), q = V.token, ee = V.flush, Z = un(_, j, y), Se = ".".concat(I), Fe = ln(_, j, Z, {
          deprecatedTokens: h.deprecatedTokens
        });
        N && Z && se(Z) === "object" && Object.keys(Z).forEach(function(ze) {
          Z[ze] = "var(".concat(Ut(ze, nn(_, N.prefix)), ")");
        });
        var ke = Ke(q, {
          componentCls: Se,
          prefixCls: I,
          iconCls: ".".concat(F),
          antCls: ".".concat(E),
          calc: z,
          // @ts-ignore
          max: oe,
          // @ts-ignore
          min: G
        }, N ? Z : Fe), Ae = p(ke, {
          hashId: T,
          prefixCls: I,
          rootPrefixCls: E,
          iconPrefixCls: F
        });
        ee(_, Fe);
        var xe = typeof s == "function" ? s(ke, I, v, h.resetFont) : null;
        return [h.resetStyle === !1 ? null : xe, Ae];
      });
      return [U, T];
    };
  }
  function m(f, p, y) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = d(f, p, y, k({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, h)), x = function(w) {
      var $ = w.prefixCls, I = w.rootCls, v = I === void 0 ? $ : I;
      return g($, v), null;
    };
    return x;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: m,
    genComponentStyleHook: d
  };
}
const ea = {
  blue: "#1677FF",
  purple: "#722ED1",
  cyan: "#13C2C2",
  green: "#52C41A",
  magenta: "#EB2F96",
  /**
   * @deprecated Use magenta instead
   */
  pink: "#EB2F96",
  red: "#F5222D",
  orange: "#FA8C16",
  yellow: "#FADB14",
  volcano: "#FA541C",
  geekblue: "#2F54EB",
  gold: "#FAAD14",
  lime: "#A0D911"
}, ta = Object.assign(Object.assign({}, ea), {
  // Color
  colorPrimary: "#1677ff",
  colorSuccess: "#52c41a",
  colorWarning: "#faad14",
  colorError: "#ff4d4f",
  colorInfo: "#1677ff",
  colorLink: "",
  colorTextBase: "",
  colorBgBase: "",
  // Font
  fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
'Noto Color Emoji'`,
  fontFamilyCode: "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace",
  fontSize: 14,
  // Line
  lineWidth: 1,
  lineType: "solid",
  // Motion
  motionUnit: 0.1,
  motionBase: 0,
  motionEaseOutCirc: "cubic-bezier(0.08, 0.82, 0.17, 1)",
  motionEaseInOutCirc: "cubic-bezier(0.78, 0.14, 0.15, 0.86)",
  motionEaseOut: "cubic-bezier(0.215, 0.61, 0.355, 1)",
  motionEaseInOut: "cubic-bezier(0.645, 0.045, 0.355, 1)",
  motionEaseOutBack: "cubic-bezier(0.12, 0.4, 0.29, 1.46)",
  motionEaseInBack: "cubic-bezier(0.71, -0.46, 0.88, 0.6)",
  motionEaseInQuint: "cubic-bezier(0.755, 0.05, 0.855, 0.06)",
  motionEaseOutQuint: "cubic-bezier(0.23, 1, 0.32, 1)",
  // Radius
  borderRadius: 6,
  // Size
  sizeUnit: 4,
  sizeStep: 4,
  sizePopupArrow: 16,
  // Control Base
  controlHeight: 32,
  // zIndex
  zIndexBase: 0,
  zIndexPopupBase: 1e3,
  // Image
  opacityImage: 1,
  // Wireframe
  wireframe: !1,
  // Motion
  motion: !0
}), Q = Math.round;
function Qt(e, t) {
  const r = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], n = r.map((o) => parseFloat(o));
  for (let o = 0; o < 3; o += 1)
    n[o] = t(n[o] || 0, r[o] || "", o);
  return r[3] ? n[3] = r[3].includes("%") ? n[3] / 100 : n[3] : n[3] = 1, n;
}
const dn = (e, t, r) => r === 0 ? e : e / 100;
function qe(e, t) {
  const r = t || 255;
  return e > r ? r : e < 0 ? 0 : e;
}
class be {
  constructor(t) {
    A(this, "isValid", !0), A(this, "r", 0), A(this, "g", 0), A(this, "b", 0), A(this, "a", 1), A(this, "_h", void 0), A(this, "_s", void 0), A(this, "_l", void 0), A(this, "_v", void 0), A(this, "_max", void 0), A(this, "_min", void 0), A(this, "_brightness", void 0);
    function r(n) {
      return n[0] in t && n[1] in t && n[2] in t;
    }
    if (t) if (typeof t == "string") {
      let o = function(i) {
        return n.startsWith(i);
      };
      const n = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(n) ? this.fromHexString(n) : o("rgb") ? this.fromRgbString(n) : o("hsl") ? this.fromHslString(n) : (o("hsv") || o("hsb")) && this.fromHsvString(n);
    } else if (t instanceof be)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (r("rgb"))
      this.r = qe(t.r), this.g = qe(t.g), this.b = qe(t.b), this.a = typeof t.a == "number" ? qe(t.a, 1) : 1;
    else if (r("hsl"))
      this.fromHsl(t);
    else if (r("hsv"))
      this.fromHsv(t);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(t));
  }
  // ======================= Setter =======================
  setR(t) {
    return this._sc("r", t);
  }
  setG(t) {
    return this._sc("g", t);
  }
  setB(t) {
    return this._sc("b", t);
  }
  setA(t) {
    return this._sc("a", t, 1);
  }
  setHue(t) {
    const r = this.toHsv();
    return r.h = t, this._c(r);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function t(i) {
      const s = i / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    }
    const r = t(this.r), n = t(this.g), o = t(this.b);
    return 0.2126 * r + 0.7152 * n + 0.0722 * o;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = Q(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._s = 0 : this._s = t / this.getMax();
    }
    return this._s;
  }
  getLightness() {
    return typeof this._l > "u" && (this._l = (this.getMax() + this.getMin()) / 510), this._l;
  }
  getValue() {
    return typeof this._v > "u" && (this._v = this.getMax() / 255), this._v;
  }
  /**
   * Returns the perceived brightness of the color, from 0-255.
   * Note: this is not the b of HSB
   * @see http://www.w3.org/TR/AERT#color-contrast
   */
  getBrightness() {
    return typeof this._brightness > "u" && (this._brightness = (this.r * 299 + this.g * 587 + this.b * 114) / 1e3), this._brightness;
  }
  // ======================== Func ========================
  darken(t = 10) {
    const r = this.getHue(), n = this.getSaturation();
    let o = this.getLightness() - t / 100;
    return o < 0 && (o = 0), this._c({
      h: r,
      s: n,
      l: o,
      a: this.a
    });
  }
  lighten(t = 10) {
    const r = this.getHue(), n = this.getSaturation();
    let o = this.getLightness() + t / 100;
    return o > 1 && (o = 1), this._c({
      h: r,
      s: n,
      l: o,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(t, r = 50) {
    const n = this._c(t), o = r / 100, i = (a) => (n[a] - this[a]) * o + this[a], s = {
      r: Q(i("r")),
      g: Q(i("g")),
      b: Q(i("b")),
      a: Q(i("a") * 100) / 100
    };
    return this._c(s);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(t = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, t);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(t = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, t);
  }
  onBackground(t) {
    const r = this._c(t), n = this.a + r.a * (1 - this.a), o = (i) => Q((this[i] * this.a + r[i] * r.a * (1 - this.a)) / n);
    return this._c({
      r: o("r"),
      g: o("g"),
      b: o("b"),
      a: n
    });
  }
  // ======================= Status =======================
  isDark() {
    return this.getBrightness() < 128;
  }
  isLight() {
    return this.getBrightness() >= 128;
  }
  // ======================== MISC ========================
  equals(t) {
    return this.r === t.r && this.g === t.g && this.b === t.b && this.a === t.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let t = "#";
    const r = (this.r || 0).toString(16);
    t += r.length === 2 ? r : "0" + r;
    const n = (this.g || 0).toString(16);
    t += n.length === 2 ? n : "0" + n;
    const o = (this.b || 0).toString(16);
    if (t += o.length === 2 ? o : "0" + o, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = Q(this.a * 255).toString(16);
      t += i.length === 2 ? i : "0" + i;
    }
    return t;
  }
  /** CSS support color pattern */
  toHsl() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      l: this.getLightness(),
      a: this.a
    };
  }
  /** CSS support color pattern */
  toHslString() {
    const t = this.getHue(), r = Q(this.getSaturation() * 100), n = Q(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${r}%,${n}%,${this.a})` : `hsl(${t},${r}%,${n}%)`;
  }
  /** Same as toHsb */
  toHsv() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      v: this.getValue(),
      a: this.a
    };
  }
  toRgb() {
    return {
      r: this.r,
      g: this.g,
      b: this.b,
      a: this.a
    };
  }
  toRgbString() {
    return this.a !== 1 ? `rgba(${this.r},${this.g},${this.b},${this.a})` : `rgb(${this.r},${this.g},${this.b})`;
  }
  toString() {
    return this.toRgbString();
  }
  // ====================== Privates ======================
  /** Return a new FastColor object with one channel changed */
  _sc(t, r, n) {
    const o = this.clone();
    return o[t] = qe(r, n), o;
  }
  _c(t) {
    return new this.constructor(t);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(t) {
    const r = t.replace("#", "");
    function n(o, i) {
      return parseInt(r[o] + r[i || o], 16);
    }
    r.length < 6 ? (this.r = n(0), this.g = n(1), this.b = n(2), this.a = r[3] ? n(3) / 255 : 1) : (this.r = n(0, 1), this.g = n(2, 3), this.b = n(4, 5), this.a = r[6] ? n(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: r,
    l: n,
    a: o
  }) {
    if (this._h = t % 360, this._s = r, this._l = n, this.a = typeof o == "number" ? o : 1, r <= 0) {
      const f = Q(n * 255);
      this.r = f, this.g = f, this.b = f;
    }
    let i = 0, s = 0, a = 0;
    const l = t / 60, c = (1 - Math.abs(2 * n - 1)) * r, d = c * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (i = c, s = d) : l >= 1 && l < 2 ? (i = d, s = c) : l >= 2 && l < 3 ? (s = c, a = d) : l >= 3 && l < 4 ? (s = d, a = c) : l >= 4 && l < 5 ? (i = d, a = c) : l >= 5 && l < 6 && (i = c, a = d);
    const m = n - c / 2;
    this.r = Q((i + m) * 255), this.g = Q((s + m) * 255), this.b = Q((a + m) * 255);
  }
  fromHsv({
    h: t,
    s: r,
    v: n,
    a: o
  }) {
    this._h = t % 360, this._s = r, this._v = n, this.a = typeof o == "number" ? o : 1;
    const i = Q(n * 255);
    if (this.r = i, this.g = i, this.b = i, r <= 0)
      return;
    const s = t / 60, a = Math.floor(s), l = s - a, c = Q(n * (1 - r) * 255), d = Q(n * (1 - r * l) * 255), m = Q(n * (1 - r * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = m, this.b = c;
        break;
      case 1:
        this.r = d, this.b = c;
        break;
      case 2:
        this.r = c, this.b = m;
        break;
      case 3:
        this.r = c, this.g = d;
        break;
      case 4:
        this.r = m, this.g = c;
        break;
      case 5:
      default:
        this.g = c, this.b = d;
        break;
    }
  }
  fromHsvString(t) {
    const r = Qt(t, dn);
    this.fromHsv({
      h: r[0],
      s: r[1],
      v: r[2],
      a: r[3]
    });
  }
  fromHslString(t) {
    const r = Qt(t, dn);
    this.fromHsl({
      h: r[0],
      s: r[1],
      l: r[2],
      a: r[3]
    });
  }
  fromRgbString(t) {
    const r = Qt(t, (n, o) => (
      // Convert percentage to number. e.g. 50% -> 128
      o.includes("%") ? Q(n / 100 * 255) : n
    ));
    this.r = r[0], this.g = r[1], this.b = r[2], this.a = r[3];
  }
}
function Jt(e) {
  return e >= 0 && e <= 255;
}
function st(e, t) {
  const {
    r,
    g: n,
    b: o,
    a: i
  } = new be(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: l
  } = new be(t).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const d = Math.round((r - s * (1 - c)) / c), m = Math.round((n - a * (1 - c)) / c), f = Math.round((o - l * (1 - c)) / c);
    if (Jt(d) && Jt(m) && Jt(f))
      return new be({
        r: d,
        g: m,
        b: f,
        a: Math.round(c * 100) / 100
      }).toRgbString();
  }
  return new be({
    r,
    g: n,
    b: o,
    a: 1
  }).toRgbString();
}
var ra = function(e, t) {
  var r = {};
  for (var n in e) Object.prototype.hasOwnProperty.call(e, n) && t.indexOf(n) < 0 && (r[n] = e[n]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var o = 0, n = Object.getOwnPropertySymbols(e); o < n.length; o++)
    t.indexOf(n[o]) < 0 && Object.prototype.propertyIsEnumerable.call(e, n[o]) && (r[n[o]] = e[n[o]]);
  return r;
};
function na(e) {
  const {
    override: t
  } = e, r = ra(e, ["override"]), n = Object.assign({}, t);
  Object.keys(ta).forEach((f) => {
    delete n[f];
  });
  const o = Object.assign(Object.assign({}, r), n), i = 480, s = 576, a = 768, l = 992, c = 1200, d = 1600;
  if (o.motion === !1) {
    const f = "0s";
    o.motionDurationFast = f, o.motionDurationMid = f, o.motionDurationSlow = f;
  }
  return Object.assign(Object.assign(Object.assign({}, o), {
    // ============== Background ============== //
    colorFillContent: o.colorFillSecondary,
    colorFillContentHover: o.colorFill,
    colorFillAlter: o.colorFillQuaternary,
    colorBgContainerDisabled: o.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: o.colorBgContainer,
    colorSplit: st(o.colorBorderSecondary, o.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: o.colorTextQuaternary,
    colorTextDisabled: o.colorTextQuaternary,
    colorTextHeading: o.colorText,
    colorTextLabel: o.colorTextSecondary,
    colorTextDescription: o.colorTextTertiary,
    colorTextLightSolid: o.colorWhite,
    colorHighlight: o.colorError,
    colorBgTextHover: o.colorFillSecondary,
    colorBgTextActive: o.colorFill,
    colorIcon: o.colorTextTertiary,
    colorIconHover: o.colorText,
    colorErrorOutline: st(o.colorErrorBg, o.colorBgContainer),
    colorWarningOutline: st(o.colorWarningBg, o.colorBgContainer),
    // Font
    fontSizeIcon: o.fontSizeSM,
    // Line
    lineWidthFocus: o.lineWidth * 3,
    // Control
    lineWidth: o.lineWidth,
    controlOutlineWidth: o.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: o.controlHeight / 2,
    controlItemBgHover: o.colorFillTertiary,
    controlItemBgActive: o.colorPrimaryBg,
    controlItemBgActiveHover: o.colorPrimaryBgHover,
    controlItemBgActiveDisabled: o.colorFill,
    controlTmpOutline: o.colorFillQuaternary,
    controlOutline: st(o.colorPrimaryBg, o.colorBgContainer),
    lineType: o.lineType,
    borderRadius: o.borderRadius,
    borderRadiusXS: o.borderRadiusXS,
    borderRadiusSM: o.borderRadiusSM,
    borderRadiusLG: o.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: o.sizeXXS,
    paddingXS: o.sizeXS,
    paddingSM: o.sizeSM,
    padding: o.size,
    paddingMD: o.sizeMD,
    paddingLG: o.sizeLG,
    paddingXL: o.sizeXL,
    paddingContentHorizontalLG: o.sizeLG,
    paddingContentVerticalLG: o.sizeMS,
    paddingContentHorizontal: o.sizeMS,
    paddingContentVertical: o.sizeSM,
    paddingContentHorizontalSM: o.size,
    paddingContentVerticalSM: o.sizeXS,
    marginXXS: o.sizeXXS,
    marginXS: o.sizeXS,
    marginSM: o.sizeSM,
    margin: o.size,
    marginMD: o.sizeMD,
    marginLG: o.sizeLG,
    marginXL: o.sizeXL,
    marginXXL: o.sizeXXL,
    boxShadow: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowSecondary: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTertiary: `
      0 1px 2px 0 rgba(0, 0, 0, 0.03),
      0 1px 6px -1px rgba(0, 0, 0, 0.02),
      0 2px 4px 0 rgba(0, 0, 0, 0.02)
    `,
    screenXS: i,
    screenXSMin: i,
    screenXSMax: s - 1,
    screenSM: s,
    screenSMMin: s,
    screenSMMax: a - 1,
    screenMD: a,
    screenMDMin: a,
    screenMDMax: l - 1,
    screenLG: l,
    screenLGMin: l,
    screenLGMax: c - 1,
    screenXL: c,
    screenXLMin: c,
    screenXLMax: d - 1,
    screenXXL: d,
    screenXXLMin: d,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new be("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new be("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new be("rgba(0, 0, 0, 0.09)").toRgbString()}
    `,
    boxShadowDrawerRight: `
      -6px 0 16px 0 rgba(0, 0, 0, 0.08),
      -3px 0 6px -4px rgba(0, 0, 0, 0.12),
      -9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerLeft: `
      6px 0 16px 0 rgba(0, 0, 0, 0.08),
      3px 0 6px -4px rgba(0, 0, 0, 0.12),
      9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerUp: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerDown: `
      0 -6px 16px 0 rgba(0, 0, 0, 0.08),
      0 -3px 6px -4px rgba(0, 0, 0, 0.12),
      0 -9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTabsOverflowLeft: "inset 10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowRight: "inset -10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowTop: "inset 0 10px 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowBottom: "inset 0 -10px 8px -8px rgba(0, 0, 0, 0.08)"
  }), n);
}
const oa = {
  lineHeight: !0,
  lineHeightSM: !0,
  lineHeightLG: !0,
  lineHeightHeading1: !0,
  lineHeightHeading2: !0,
  lineHeightHeading3: !0,
  lineHeightHeading4: !0,
  lineHeightHeading5: !0,
  opacityLoading: !0,
  fontWeightStrong: !0,
  zIndexPopupBase: !0,
  zIndexBase: !0,
  opacityImage: !0
}, ia = {
  motionBase: !0,
  motionUnit: !0
}, sa = xi(Ze.defaultAlgorithm), aa = {
  screenXS: !0,
  screenXSMin: !0,
  screenXSMax: !0,
  screenSM: !0,
  screenSMMin: !0,
  screenSMMax: !0,
  screenMD: !0,
  screenMDMin: !0,
  screenMDMax: !0,
  screenLG: !0,
  screenLGMin: !0,
  screenLGMax: !0,
  screenXL: !0,
  screenXLMin: !0,
  screenXLMax: !0,
  screenXXL: !0,
  screenXXLMin: !0
}, oo = (e, t, r) => {
  const n = r.getDerivativeToken(e), {
    override: o,
    ...i
  } = t;
  let s = {
    ...n,
    override: o
  };
  return s = na(s), i && Object.entries(i).forEach(([a, l]) => {
    const {
      theme: c,
      ...d
    } = l;
    let m = d;
    c && (m = oo({
      ...s,
      ...d
    }, {
      override: d
    }, c)), s[a] = m;
  }), s;
};
function la() {
  const {
    token: e,
    hashed: t,
    theme: r = sa,
    override: n,
    cssVar: o
  } = u.useContext(Ze._internalContext), [i, s, a] = wi(r, [Ze.defaultSeed, e], {
    salt: `${ls}-${t || ""}`,
    override: n,
    getComputedToken: oo,
    cssVar: o && {
      prefix: o.prefix,
      key: o.key,
      unitless: oa,
      ignore: ia,
      preserve: aa
    }
  });
  return [r, a, t ? s : "", i, o];
}
const {
  genStyleHooks: Ht
} = Js({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Ie();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, r, n, o] = la();
    return {
      theme: e,
      realToken: t,
      hashId: r,
      token: n,
      cssVar: o
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = Ie();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), nt = /* @__PURE__ */ u.createContext(null);
function mn(e) {
  const {
    getDropContainer: t,
    className: r,
    prefixCls: n,
    children: o
  } = e, {
    disabled: i
  } = u.useContext(nt), [s, a] = u.useState(), [l, c] = u.useState(null);
  if (u.useEffect(() => {
    const f = t == null ? void 0 : t();
    s !== f && a(f);
  }, [t]), u.useEffect(() => {
    if (s) {
      const f = () => {
        c(!0);
      }, p = (g) => {
        g.preventDefault();
      }, y = (g) => {
        g.relatedTarget || c(!1);
      }, h = (g) => {
        c(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", f), document.addEventListener("dragover", p), document.addEventListener("dragleave", y), document.addEventListener("drop", h), () => {
        document.removeEventListener("dragenter", f), document.removeEventListener("dragover", p), document.removeEventListener("dragleave", y), document.removeEventListener("drop", h);
      };
    }
  }, [!!s]), !(t && s && !i))
    return null;
  const m = `${n}-drop-area`;
  return /* @__PURE__ */ bt(/* @__PURE__ */ u.createElement("div", {
    className: O(m, r, {
      [`${m}-on-body`]: s.tagName === "BODY"
    }),
    style: {
      display: l ? "block" : "none"
    }
  }, o), s);
}
function pn(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function ca(e) {
  return e && $e(e) === "object" && pn(e.nativeElement) ? e.nativeElement : pn(e) ? e : null;
}
function ua(e) {
  var t = ca(e);
  if (t)
    return t;
  if (e instanceof u.Component) {
    var r;
    return (r = Ar.findDOMNode) === null || r === void 0 ? void 0 : r.call(Ar, e);
  }
  return null;
}
function fa(e, t) {
  if (e == null) return {};
  var r = {};
  for (var n in e) if ({}.hasOwnProperty.call(e, n)) {
    if (t.indexOf(n) !== -1) continue;
    r[n] = e[n];
  }
  return r;
}
function gn(e, t) {
  if (e == null) return {};
  var r, n, o = fa(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (n = 0; n < i.length; n++) r = i[n], t.indexOf(r) === -1 && {}.propertyIsEnumerable.call(e, r) && (o[r] = e[r]);
  }
  return o;
}
var da = /* @__PURE__ */ M.createContext({}), ma = /* @__PURE__ */ function(e) {
  It(r, e);
  var t = Pt(r);
  function r() {
    return Ue(this, r), t.apply(this, arguments);
  }
  return Ge(r, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), r;
}(M.Component);
function pa(e) {
  var t = M.useReducer(function(a) {
    return a + 1;
  }, 0), r = wt(t, 2), n = r[1], o = M.useRef(e), i = Oe(function() {
    return o.current;
  }), s = Oe(function(a) {
    o.current = typeof a == "function" ? a(o.current) : a, n();
  });
  return [i, s];
}
var Ce = "none", at = "appear", lt = "enter", ct = "leave", hn = "none", pe = "prepare", Be = "start", We = "active", _r = "end", io = "prepared";
function yn(e, t) {
  var r = {};
  return r[e.toLowerCase()] = t.toLowerCase(), r["Webkit".concat(e)] = "webkit".concat(t), r["Moz".concat(e)] = "moz".concat(t), r["ms".concat(e)] = "MS".concat(t), r["O".concat(e)] = "o".concat(t.toLowerCase()), r;
}
function ga(e, t) {
  var r = {
    animationend: yn("Animation", "AnimationEnd"),
    transitionend: yn("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete r.animationend.animation, "TransitionEvent" in t || delete r.transitionend.transition), r;
}
var ha = ga(Rt(), typeof window < "u" ? window : {}), so = {};
if (Rt()) {
  var ya = document.createElement("div");
  so = ya.style;
}
var ut = {};
function ao(e) {
  if (ut[e])
    return ut[e];
  var t = ha[e];
  if (t)
    for (var r = Object.keys(t), n = r.length, o = 0; o < n; o += 1) {
      var i = r[o];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in so)
        return ut[e] = t[i], ut[e];
    }
  return "";
}
var lo = ao("animationend"), co = ao("transitionend"), uo = !!(lo && co), vn = lo || "animationend", bn = co || "transitionend";
function Sn(e, t) {
  if (!e) return null;
  if (se(e) === "object") {
    var r = t.replace(/-\w/g, function(n) {
      return n[1].toUpperCase();
    });
    return e[r];
  }
  return "".concat(e, "-").concat(t);
}
const va = function(e) {
  var t = re();
  function r(o) {
    o && (o.removeEventListener(bn, e), o.removeEventListener(vn, e));
  }
  function n(o) {
    t.current && t.current !== o && r(t.current), o && o !== t.current && (o.addEventListener(bn, e), o.addEventListener(vn, e), t.current = o);
  }
  return M.useEffect(function() {
    return function() {
      r(t.current);
    };
  }, []), [n, r];
};
var fo = Rt() ? Ao : _e, mo = function(t) {
  return +setTimeout(t, 16);
}, po = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (mo = function(t) {
  return window.requestAnimationFrame(t);
}, po = function(t) {
  return window.cancelAnimationFrame(t);
});
var xn = 0, Er = /* @__PURE__ */ new Map();
function go(e) {
  Er.delete(e);
}
var ar = function(t) {
  var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  xn += 1;
  var n = xn;
  function o(i) {
    if (i === 0)
      go(n), t();
    else {
      var s = mo(function() {
        o(i - 1);
      });
      Er.set(n, s);
    }
  }
  return o(r), n;
};
ar.cancel = function(e) {
  var t = Er.get(e);
  return go(e), po(t);
};
const ba = function() {
  var e = M.useRef(null);
  function t() {
    ar.cancel(e.current);
  }
  function r(n) {
    var o = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = ar(function() {
      o <= 1 ? n({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : r(n, o - 1);
    });
    e.current = i;
  }
  return M.useEffect(function() {
    return function() {
      t();
    };
  }, []), [r, t];
};
var Sa = [pe, Be, We, _r], xa = [pe, io], ho = !1, wa = !0;
function yo(e) {
  return e === We || e === _r;
}
const _a = function(e, t, r) {
  var n = Qe(hn), o = fe(n, 2), i = o[0], s = o[1], a = ba(), l = fe(a, 2), c = l[0], d = l[1];
  function m() {
    s(pe, !0);
  }
  var f = t ? xa : Sa;
  return fo(function() {
    if (i !== hn && i !== _r) {
      var p = f.indexOf(i), y = f[p + 1], h = r(i);
      h === ho ? s(y, !0) : y && c(function(g) {
        function x() {
          g.isCanceled() || s(y, !0);
        }
        h === !0 ? x() : Promise.resolve(h).then(x);
      });
    }
  }, [e, i]), M.useEffect(function() {
    return function() {
      d();
    };
  }, []), [m, i];
};
function Ea(e, t, r, n) {
  var o = n.motionEnter, i = o === void 0 ? !0 : o, s = n.motionAppear, a = s === void 0 ? !0 : s, l = n.motionLeave, c = l === void 0 ? !0 : l, d = n.motionDeadline, m = n.motionLeaveImmediately, f = n.onAppearPrepare, p = n.onEnterPrepare, y = n.onLeavePrepare, h = n.onAppearStart, g = n.onEnterStart, x = n.onLeaveStart, _ = n.onAppearActive, w = n.onEnterActive, $ = n.onLeaveActive, I = n.onAppearEnd, v = n.onEnterEnd, R = n.onLeaveEnd, P = n.onVisibleChanged, j = Qe(), T = fe(j, 2), L = T[0], N = T[1], b = pa(Ce), E = fe(b, 2), F = E[0], D = E[1], B = Qe(null), z = fe(B, 2), W = z[0], oe = z[1], G = F(), J = re(!1), U = re(null);
  function V() {
    return r();
  }
  var q = re(!1);
  function ee() {
    D(Ce), oe(null, !0);
  }
  var Z = Oe(function(te) {
    var Y = F();
    if (Y !== Ce) {
      var ae = V();
      if (!(te && !te.deadline && te.target !== ae)) {
        var Pe = q.current, Re;
        Y === at && Pe ? Re = I == null ? void 0 : I(ae, te) : Y === lt && Pe ? Re = v == null ? void 0 : v(ae, te) : Y === ct && Pe && (Re = R == null ? void 0 : R(ae, te)), Pe && Re !== !1 && ee();
      }
    }
  }), Se = va(Z), Fe = fe(Se, 1), ke = Fe[0], Ae = function(Y) {
    switch (Y) {
      case at:
        return A(A(A({}, pe, f), Be, h), We, _);
      case lt:
        return A(A(A({}, pe, p), Be, g), We, w);
      case ct:
        return A(A(A({}, pe, y), Be, x), We, $);
      default:
        return {};
    }
  }, xe = M.useMemo(function() {
    return Ae(G);
  }, [G]), ze = _a(G, !e, function(te) {
    if (te === pe) {
      var Y = xe[pe];
      return Y ? Y(V()) : ho;
    }
    if (C in xe) {
      var ae;
      oe(((ae = xe[C]) === null || ae === void 0 ? void 0 : ae.call(xe, V(), null)) || null);
    }
    return C === We && G !== Ce && (ke(V()), d > 0 && (clearTimeout(U.current), U.current = setTimeout(function() {
      Z({
        deadline: !0
      });
    }, d))), C === io && ee(), wa;
  }), it = fe(ze, 2), Xt = it[0], C = it[1], K = yo(C);
  q.current = K;
  var X = re(null);
  fo(function() {
    if (!(J.current && X.current === t)) {
      N(t);
      var te = J.current;
      J.current = !0;
      var Y;
      !te && t && a && (Y = at), te && t && i && (Y = lt), (te && !t && c || !te && m && !t && c) && (Y = ct);
      var ae = Ae(Y);
      Y && (e || ae[pe]) ? (D(Y), Xt()) : D(Ce), X.current = t;
    }
  }, [t]), _e(function() {
    // Cancel appear
    (G === at && !a || // Cancel enter
    G === lt && !i || // Cancel leave
    G === ct && !c) && D(Ce);
  }, [a, i, c]), _e(function() {
    return function() {
      J.current = !1, clearTimeout(U.current);
    };
  }, []);
  var me = M.useRef(!1);
  _e(function() {
    L && (me.current = !0), L !== void 0 && G === Ce && ((me.current || L) && (P == null || P(L)), me.current = !0);
  }, [L, G]);
  var ce = W;
  return xe[pe] && C === Be && (ce = k({
    transition: "none"
  }, ce)), [G, C, ce, L ?? t];
}
function Ca(e) {
  var t = e;
  se(e) === "object" && (t = e.transitionSupport);
  function r(o, i) {
    return !!(o.motionName && t && i !== !1);
  }
  var n = /* @__PURE__ */ M.forwardRef(function(o, i) {
    var s = o.visible, a = s === void 0 ? !0 : s, l = o.removeOnLeave, c = l === void 0 ? !0 : l, d = o.forceRender, m = o.children, f = o.motionName, p = o.leavedClassName, y = o.eventProps, h = M.useContext(da), g = h.motion, x = r(o, g), _ = re(), w = re();
    function $() {
      try {
        return _.current instanceof HTMLElement ? _.current : ua(w.current);
      } catch {
        return null;
      }
    }
    var I = Ea(x, a, $, o), v = fe(I, 4), R = v[0], P = v[1], j = v[2], T = v[3], L = M.useRef(T);
    T && (L.current = !0);
    var N = M.useCallback(function(z) {
      _.current = z, Ws(i, z);
    }, [i]), b, E = k(k({}, y), {}, {
      visible: a
    });
    if (!m)
      b = null;
    else if (R === Ce)
      T ? b = m(k({}, E), N) : !c && L.current && p ? b = m(k(k({}, E), {}, {
        className: p
      }), N) : d || !c && !p ? b = m(k(k({}, E), {}, {
        style: {
          display: "none"
        }
      }), N) : b = null;
    else {
      var F;
      P === pe ? F = "prepare" : yo(P) ? F = "active" : P === Be && (F = "start");
      var D = Sn(f, "".concat(R, "-").concat(F));
      b = m(k(k({}, E), {}, {
        className: O(Sn(f, R), A(A({}, D, D && F), f, typeof f == "string")),
        style: j
      }), N);
    }
    if (/* @__PURE__ */ M.isValidElement(b) && Vs(b)) {
      var B = Xs(b);
      B || (b = /* @__PURE__ */ M.cloneElement(b, {
        ref: N
      }));
    }
    return /* @__PURE__ */ M.createElement(ma, {
      ref: w
    }, b);
  });
  return n.displayName = "CSSMotion", n;
}
const Ta = Ca(uo);
var lr = "add", cr = "keep", ur = "remove", er = "removed";
function $a(e) {
  var t;
  return e && se(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, k(k({}, t), {}, {
    key: String(t.key)
  });
}
function fr() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map($a);
}
function Ia() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], r = [], n = 0, o = t.length, i = fr(e), s = fr(t);
  i.forEach(function(c) {
    for (var d = !1, m = n; m < o; m += 1) {
      var f = s[m];
      if (f.key === c.key) {
        n < m && (r = r.concat(s.slice(n, m).map(function(p) {
          return k(k({}, p), {}, {
            status: lr
          });
        })), n = m), r.push(k(k({}, f), {}, {
          status: cr
        })), n += 1, d = !0;
        break;
      }
    }
    d || r.push(k(k({}, c), {}, {
      status: ur
    }));
  }), n < o && (r = r.concat(s.slice(n).map(function(c) {
    return k(k({}, c), {}, {
      status: lr
    });
  })));
  var a = {};
  r.forEach(function(c) {
    var d = c.key;
    a[d] = (a[d] || 0) + 1;
  });
  var l = Object.keys(a).filter(function(c) {
    return a[c] > 1;
  });
  return l.forEach(function(c) {
    r = r.filter(function(d) {
      var m = d.key, f = d.status;
      return m !== c || f !== ur;
    }), r.forEach(function(d) {
      d.key === c && (d.status = cr);
    });
  }), r;
}
var Pa = ["component", "children", "onVisibleChanged", "onAllRemoved"], Ra = ["status"], Ma = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function La(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Ta, r = /* @__PURE__ */ function(n) {
    It(i, n);
    var o = Pt(i);
    function i() {
      var s;
      Ue(this, i);
      for (var a = arguments.length, l = new Array(a), c = 0; c < a; c++)
        l[c] = arguments[c];
      return s = o.call.apply(o, [this].concat(l)), A(Le(s), "state", {
        keyEntities: []
      }), A(Le(s), "removeKey", function(d) {
        s.setState(function(m) {
          var f = m.keyEntities.map(function(p) {
            return p.key !== d ? p : k(k({}, p), {}, {
              status: er
            });
          });
          return {
            keyEntities: f
          };
        }, function() {
          var m = s.state.keyEntities, f = m.filter(function(p) {
            var y = p.status;
            return y !== er;
          }).length;
          f === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return Ge(i, [{
      key: "render",
      value: function() {
        var a = this, l = this.state.keyEntities, c = this.props, d = c.component, m = c.children, f = c.onVisibleChanged;
        c.onAllRemoved;
        var p = gn(c, Pa), y = d || M.Fragment, h = {};
        return Ma.forEach(function(g) {
          h[g] = p[g], delete p[g];
        }), delete p.keys, /* @__PURE__ */ M.createElement(y, p, l.map(function(g, x) {
          var _ = g.status, w = gn(g, Ra), $ = _ === lr || _ === cr;
          return /* @__PURE__ */ M.createElement(t, ye({}, h, {
            key: w.key,
            visible: $,
            eventProps: w,
            onVisibleChanged: function(v) {
              f == null || f(v, {
                key: w.key
              }), v || a.removeKey(w.key);
            }
          }), function(I, v) {
            return m(k(k({}, I), {}, {
              index: x
            }), v);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, l) {
        var c = a.keys, d = l.keyEntities, m = fr(c), f = Ia(d, m);
        return {
          keyEntities: f.filter(function(p) {
            var y = d.find(function(h) {
              var g = h.key;
              return p.key === g;
            });
            return !(y && y.status === er && p.status === ur);
          })
        };
      }
    }]), i;
  }(M.Component);
  return A(r, "defaultProps", {
    component: "div"
  }), r;
}
const Oa = La(uo);
function ja(e, t) {
  const {
    children: r,
    upload: n,
    rootClassName: o
  } = e, i = u.useRef(null);
  return u.useImperativeHandle(t, () => i.current), /* @__PURE__ */ u.createElement(Dn, ye({}, n, {
    showUploadList: !1,
    rootClassName: o,
    ref: i
  }), r);
}
const vo = /* @__PURE__ */ u.forwardRef(ja), Na = (e) => {
  const {
    componentCls: t,
    antCls: r,
    calc: n
  } = e, o = `${t}-list-card`, i = n(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [o]: {
      borderRadius: e.borderRadius,
      position: "relative",
      background: e.colorFillContent,
      borderWidth: e.lineWidth,
      borderStyle: "solid",
      borderColor: "transparent",
      flex: "none",
      // =============================== Desc ================================
      [`${o}-name,${o}-desc`]: {
        display: "flex",
        flexWrap: "nowrap",
        maxWidth: "100%"
      },
      [`${o}-ellipsis-prefix`]: {
        flex: "0 1 auto",
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      },
      [`${o}-ellipsis-suffix`]: {
        flex: "none"
      },
      // ============================= Overview ==============================
      "&-type-overview": {
        padding: n(e.paddingSM).sub(e.lineWidth).equal(),
        paddingInlineStart: n(e.padding).add(e.lineWidth).equal(),
        display: "flex",
        flexWrap: "nowrap",
        gap: e.paddingXS,
        alignItems: "flex-start",
        width: 236,
        // Icon
        [`${o}-icon`]: {
          fontSize: n(e.fontSizeLG).mul(2).equal(),
          lineHeight: 1,
          paddingTop: n(e.paddingXXS).mul(1.5).equal(),
          flex: "none"
        },
        // Content
        [`${o}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch"
        },
        [`${o}-desc`]: {
          color: e.colorTextTertiary
        }
      },
      // ============================== Preview ==============================
      "&-type-preview": {
        width: i,
        height: i,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        [`&:not(${o}-status-error)`]: {
          border: 0
        },
        // Img
        [`${r}-image`]: {
          width: "100%",
          height: "100%",
          borderRadius: "inherit",
          position: "relative",
          overflow: "hidden",
          img: {
            height: "100%",
            objectFit: "cover",
            borderRadius: "inherit"
          }
        },
        // Mask
        [`${o}-img-mask`]: {
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "inherit",
          background: `rgba(0, 0, 0, ${e.opacityLoading})`
        },
        // Error
        [`&${o}-status-error`]: {
          borderRadius: "inherit",
          [`img, ${o}-img-mask`]: {
            borderRadius: n(e.borderRadius).sub(e.lineWidth).equal()
          },
          [`${o}-desc`]: {
            paddingInline: e.paddingXXS
          }
        },
        // Progress
        [`${o}-progress`]: {}
      },
      // ============================ Remove Icon ============================
      [`${o}-remove`]: {
        position: "absolute",
        top: 0,
        insetInlineEnd: 0,
        border: 0,
        padding: e.paddingXXS,
        background: "transparent",
        lineHeight: 1,
        transform: "translate(50%, -50%)",
        fontSize: e.fontSize,
        cursor: "pointer",
        opacity: e.opacityLoading,
        display: "none",
        "&:dir(rtl)": {
          transform: "translate(-50%, -50%)"
        },
        "&:hover": {
          opacity: 1
        },
        "&:active": {
          opacity: e.opacityLoading
        }
      },
      [`&:hover ${o}-remove`]: {
        display: "block"
      },
      // ============================== Status ===============================
      "&-status-error": {
        borderColor: e.colorError,
        [`${o}-desc`]: {
          color: e.colorError
        }
      },
      // ============================== Motion ===============================
      "&-motion": {
        transition: ["opacity", "width", "margin", "padding"].map((s) => `${s} ${e.motionDurationSlow}`).join(","),
        "&-appear-start": {
          width: 0,
          transition: "none"
        },
        "&-leave-active": {
          opacity: 0,
          width: 0,
          paddingInline: 0,
          borderInlineWidth: 0,
          marginInlineEnd: n(e.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, dr = {
  "&, *": {
    boxSizing: "border-box"
  }
}, Fa = (e) => {
  const {
    componentCls: t,
    calc: r,
    antCls: n
  } = e, o = `${t}-drop-area`, i = `${t}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [o]: {
      position: "absolute",
      inset: 0,
      zIndex: e.zIndexPopupBase,
      ...dr,
      "&-on-body": {
        position: "fixed",
        inset: 0
      },
      "&-hide-placement": {
        [`${i}-inner`]: {
          display: "none"
        }
      },
      [i]: {
        padding: 0
      }
    },
    "&": {
      // ============================= Placeholder =============================
      [i]: {
        height: "100%",
        borderRadius: e.borderRadius,
        borderWidth: e.lineWidthBold,
        borderStyle: "dashed",
        borderColor: "transparent",
        padding: e.padding,
        position: "relative",
        backdropFilter: "blur(10px)",
        background: e.colorBgPlaceholderHover,
        ...dr,
        [`${n}-upload-wrapper ${n}-upload${n}-upload-btn`]: {
          padding: 0
        },
        [`&${i}-drag-in`]: {
          borderColor: e.colorPrimaryHover
        },
        [`&${i}-disabled`]: {
          opacity: 0.25,
          pointerEvents: "none"
        },
        [`${i}-inner`]: {
          gap: r(e.paddingXXS).div(2).equal()
        },
        [`${i}-icon`]: {
          fontSize: e.fontSizeHeading2,
          lineHeight: 1
        },
        [`${i}-title${i}-title`]: {
          margin: 0,
          fontSize: e.fontSize,
          lineHeight: e.lineHeight
        },
        [`${i}-description`]: {}
      }
    }
  };
}, ka = (e) => {
  const {
    componentCls: t,
    calc: r
  } = e, n = `${t}-list`, o = r(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [t]: {
      position: "relative",
      width: "100%",
      ...dr,
      // =============================== File List ===============================
      [n]: {
        display: "flex",
        flexWrap: "wrap",
        gap: e.paddingSM,
        fontSize: e.fontSize,
        lineHeight: e.lineHeight,
        color: e.colorText,
        paddingBlock: e.paddingSM,
        paddingInline: e.padding,
        width: "100%",
        background: e.colorBgContainer,
        // Hide scrollbar
        scrollbarWidth: "none",
        "-ms-overflow-style": "none",
        "&::-webkit-scrollbar": {
          display: "none"
        },
        // Scroll
        "&-overflow-scrollX, &-overflow-scrollY": {
          "&:before, &:after": {
            content: '""',
            position: "absolute",
            opacity: 0,
            transition: `opacity ${e.motionDurationSlow}`,
            zIndex: 1
          }
        },
        "&-overflow-ping-start:before": {
          opacity: 1
        },
        "&-overflow-ping-end:after": {
          opacity: 1
        },
        "&-overflow-scrollX": {
          overflowX: "auto",
          overflowY: "hidden",
          flexWrap: "nowrap",
          "&:before, &:after": {
            insetBlock: 0,
            width: 8
          },
          "&:before": {
            insetInlineStart: 0,
            background: "linear-gradient(to right, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:after": {
            insetInlineEnd: 0,
            background: "linear-gradient(to left, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:dir(rtl)": {
            "&:before": {
              background: "linear-gradient(to left, rgba(0,0,0,0.06), rgba(0,0,0,0));"
            },
            "&:after": {
              background: "linear-gradient(to right, rgba(0,0,0,0.06), rgba(0,0,0,0));"
            }
          }
        },
        "&-overflow-scrollY": {
          overflowX: "hidden",
          overflowY: "auto",
          maxHeight: r(o).mul(3).equal(),
          "&:before, &:after": {
            insetInline: 0,
            height: 8
          },
          "&:before": {
            insetBlockStart: 0,
            background: "linear-gradient(to bottom, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:after": {
            insetBlockEnd: 0,
            background: "linear-gradient(to top, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          }
        },
        // ======================================================================
        // ==                              Upload                              ==
        // ======================================================================
        "&-upload-btn": {
          width: o,
          height: o,
          fontSize: e.fontSizeHeading2,
          color: "#999"
        },
        // ======================================================================
        // ==                             PrevNext                             ==
        // ======================================================================
        "&-prev-btn, &-next-btn": {
          position: "absolute",
          top: "50%",
          transform: "translateY(-50%)",
          boxShadow: e.boxShadowTertiary,
          opacity: 0,
          pointerEvents: "none"
        },
        "&-prev-btn": {
          left: {
            _skip_check_: !0,
            value: e.padding
          }
        },
        "&-next-btn": {
          right: {
            _skip_check_: !0,
            value: e.padding
          }
        },
        "&:dir(ltr)": {
          [`&${n}-overflow-ping-start ${n}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${n}-overflow-ping-end ${n}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        },
        "&:dir(rtl)": {
          [`&${n}-overflow-ping-end ${n}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${n}-overflow-ping-start ${n}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        }
      }
    }
  };
}, Aa = (e) => {
  const {
    colorBgContainer: t
  } = e;
  return {
    colorBgPlaceholderHover: new be(t).setA(0.85).toRgbString()
  };
}, bo = Ht("Attachments", (e) => {
  const t = Ke(e, {});
  return [Fa(t), ka(t), Na(t)];
}, Aa), za = (e) => e.indexOf("image/") === 0, ft = 200;
function Da(e) {
  return new Promise((t) => {
    if (!e || !e.type || !za(e.type)) {
      t("");
      return;
    }
    const r = new Image();
    if (r.onload = () => {
      const {
        width: n,
        height: o
      } = r, i = n / o, s = i > 1 ? ft : ft * i, a = i > 1 ? ft / i : ft, l = document.createElement("canvas");
      l.width = s, l.height = a, l.style.cssText = `position: fixed; left: 0; top: 0; width: ${s}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(l), l.getContext("2d").drawImage(r, 0, 0, s, a);
      const d = l.toDataURL();
      document.body.removeChild(l), window.URL.revokeObjectURL(r.src), t(d);
    }, r.crossOrigin = "anonymous", e.type.startsWith("image/svg+xml")) {
      const n = new FileReader();
      n.onload = () => {
        n.result && typeof n.result == "string" && (r.src = n.result);
      }, n.readAsDataURL(e);
    } else if (e.type.startsWith("image/gif")) {
      const n = new FileReader();
      n.onload = () => {
        n.result && t(n.result);
      }, n.readAsDataURL(e);
    } else
      r.src = window.URL.createObjectURL(e);
  });
}
function Ha() {
  return /* @__PURE__ */ u.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    //xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ u.createElement("title", null, "audio"), /* @__PURE__ */ u.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ u.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M10.7315824,7.11216117 C10.7428131,7.15148751 10.7485063,7.19218979 10.7485063,7.23309113 L10.7485063,8.07742614 C10.7484199,8.27364959 10.6183424,8.44607275 10.4296853,8.50003683 L8.32984514,9.09986306 L8.32984514,11.7071803 C8.32986605,12.5367078 7.67249692,13.217028 6.84345686,13.2454634 L6.79068592,13.2463395 C6.12766108,13.2463395 5.53916361,12.8217001 5.33010655,12.1924966 C5.1210495,11.563293 5.33842118,10.8709227 5.86959669,10.4741173 C6.40077221,10.0773119 7.12636292,10.0652587 7.67042486,10.4442027 L7.67020842,7.74937024 L7.68449368,7.74937024 C7.72405122,7.59919041 7.83988806,7.48101083 7.98924584,7.4384546 L10.1880418,6.81004755 C10.42156,6.74340323 10.6648954,6.87865515 10.7315824,7.11216117 Z M9.60714286,1.31785714 L12.9678571,4.67857143 L9.60714286,4.67857143 L9.60714286,1.31785714 Z",
    fill: "currentColor"
  })));
}
function Ba(e) {
  const {
    percent: t
  } = e, {
    token: r
  } = Ze.useToken();
  return /* @__PURE__ */ u.createElement(di, {
    type: "circle",
    percent: t,
    size: r.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (n) => /* @__PURE__ */ u.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (n || 0).toFixed(0), "%")
  });
}
function Wa() {
  return /* @__PURE__ */ u.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    // xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ u.createElement("title", null, "video"), /* @__PURE__ */ u.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ u.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M12.9678571,4.67857143 L9.60714286,1.31785714 L9.60714286,4.67857143 L12.9678571,4.67857143 Z M10.5379461,10.3101106 L6.68957555,13.0059749 C6.59910784,13.0693494 6.47439406,13.0473861 6.41101953,12.9569184 C6.3874624,12.9232903 6.37482581,12.8832269 6.37482581,12.8421686 L6.37482581,7.45043999 C6.37482581,7.33998304 6.46436886,7.25043999 6.57482581,7.25043999 C6.61588409,7.25043999 6.65594753,7.26307658 6.68957555,7.28663371 L10.5379461,9.98249803 C10.6284138,10.0458726 10.6503772,10.1705863 10.5870027,10.2610541 C10.5736331,10.2801392 10.5570312,10.2967411 10.5379461,10.3101106 Z",
    fill: "currentColor"
  })));
}
const tr = " ", vt = "#8c8c8c", So = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], wn = [{
  key: "default",
  icon: /* @__PURE__ */ u.createElement(An, null),
  color: vt,
  ext: []
}, {
  key: "excel",
  icon: /* @__PURE__ */ u.createElement(Uo, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  key: "image",
  icon: /* @__PURE__ */ u.createElement(Go, null),
  color: vt,
  ext: So
}, {
  key: "markdown",
  icon: /* @__PURE__ */ u.createElement(Ko, null),
  color: vt,
  ext: ["md", "mdx"]
}, {
  key: "pdf",
  icon: /* @__PURE__ */ u.createElement(qo, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  key: "ppt",
  icon: /* @__PURE__ */ u.createElement(Yo, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  key: "word",
  icon: /* @__PURE__ */ u.createElement(Zo, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  key: "zip",
  icon: /* @__PURE__ */ u.createElement(Qo, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  key: "video",
  icon: /* @__PURE__ */ u.createElement(Wa, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  key: "audio",
  icon: /* @__PURE__ */ u.createElement(Ha, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function _n(e, t) {
  return t.some((r) => e.toLowerCase() === `.${r}`);
}
function Va(e) {
  let t = e;
  const r = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let n = 0;
  for (; t >= 1024 && n < r.length - 1; )
    t /= 1024, n++;
  return `${t.toFixed(0)} ${r[n]}`;
}
function Xa(e, t) {
  const {
    prefixCls: r,
    item: n,
    onRemove: o,
    className: i,
    style: s,
    imageProps: a,
    type: l,
    icon: c
  } = e, d = u.useContext(nt), {
    disabled: m
  } = d || {}, {
    name: f,
    size: p,
    percent: y,
    status: h = "done",
    description: g
  } = n, {
    getPrefixCls: x
  } = Ie(), _ = x("attachment", r), w = `${_}-list-card`, [$, I, v] = bo(_), [R, P] = u.useMemo(() => {
    const z = f || "", W = z.match(/^(.*)\.[^.]+$/);
    return W ? [W[1], z.slice(W[1].length)] : [z, ""];
  }, [f]), j = u.useMemo(() => _n(P, So), [P]), T = u.useMemo(() => g || (h === "uploading" ? `${y || 0}%` : h === "error" ? n.response || tr : p ? Va(p) : tr), [h, y]), [L, N] = u.useMemo(() => {
    if (c)
      if (typeof c == "string") {
        const z = wn.find((W) => W.key === c);
        if (z)
          return [z.icon, z.color];
      } else
        return [c, void 0];
    for (const {
      ext: z,
      icon: W,
      color: oe
    } of wn)
      if (_n(P, z))
        return [W, oe];
    return [/* @__PURE__ */ u.createElement(An, {
      key: "defaultIcon"
    }), vt];
  }, [P, c]), [b, E] = u.useState();
  u.useEffect(() => {
    if (n.originFileObj) {
      let z = !0;
      return Da(n.originFileObj).then((W) => {
        z && E(W);
      }), () => {
        z = !1;
      };
    }
    E(void 0);
  }, [n.originFileObj]);
  let F = null;
  const D = n.thumbUrl || n.url || b, B = l === "image" || l !== "file" && j && (n.originFileObj || D);
  return B ? F = /* @__PURE__ */ u.createElement(u.Fragment, null, D && /* @__PURE__ */ u.createElement(mi, ye({
    alt: "preview",
    src: D
  }, a)), h !== "done" && /* @__PURE__ */ u.createElement("div", {
    className: `${w}-img-mask`
  }, h === "uploading" && y !== void 0 && /* @__PURE__ */ u.createElement(Ba, {
    percent: y,
    prefixCls: w
  }), h === "error" && /* @__PURE__ */ u.createElement("div", {
    className: `${w}-desc`
  }, /* @__PURE__ */ u.createElement("div", {
    className: `${w}-ellipsis-prefix`
  }, T)))) : F = /* @__PURE__ */ u.createElement(u.Fragment, null, /* @__PURE__ */ u.createElement("div", {
    className: `${w}-icon`,
    style: N ? {
      color: N
    } : void 0
  }, L), /* @__PURE__ */ u.createElement("div", {
    className: `${w}-content`
  }, /* @__PURE__ */ u.createElement("div", {
    className: `${w}-name`
  }, /* @__PURE__ */ u.createElement("div", {
    className: `${w}-ellipsis-prefix`
  }, R ?? tr), /* @__PURE__ */ u.createElement("div", {
    className: `${w}-ellipsis-suffix`
  }, P)), /* @__PURE__ */ u.createElement("div", {
    className: `${w}-desc`
  }, /* @__PURE__ */ u.createElement("div", {
    className: `${w}-ellipsis-prefix`
  }, T)))), $(/* @__PURE__ */ u.createElement("div", {
    className: O(w, {
      [`${w}-status-${h}`]: h,
      [`${w}-type-preview`]: B,
      [`${w}-type-overview`]: !B
    }, i, I, v),
    style: s,
    ref: t
  }, F, !m && o && /* @__PURE__ */ u.createElement("button", {
    type: "button",
    className: `${w}-remove`,
    onClick: () => {
      o(n);
    }
  }, /* @__PURE__ */ u.createElement(Xo, null))));
}
const xo = /* @__PURE__ */ u.forwardRef(Xa), En = 1;
function Ua(e) {
  const {
    prefixCls: t,
    items: r,
    onRemove: n,
    overflow: o,
    upload: i,
    listClassName: s,
    listStyle: a,
    itemClassName: l,
    uploadClassName: c,
    uploadStyle: d,
    itemStyle: m,
    imageProps: f
  } = e, p = `${t}-list`, y = u.useRef(null), [h, g] = u.useState(!1), {
    disabled: x
  } = u.useContext(nt);
  u.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [_, w] = u.useState(!1), [$, I] = u.useState(!1), v = () => {
    const T = y.current;
    T && (o === "scrollX" ? (w(Math.abs(T.scrollLeft) >= En), I(T.scrollWidth - T.clientWidth - Math.abs(T.scrollLeft) >= En)) : o === "scrollY" && (w(T.scrollTop !== 0), I(T.scrollHeight - T.clientHeight !== T.scrollTop)));
  };
  u.useEffect(() => {
    v();
  }, [o, r.length]);
  const R = (T) => {
    const L = y.current;
    L && L.scrollTo({
      left: L.scrollLeft + T * L.clientWidth,
      behavior: "smooth"
    });
  }, P = () => {
    R(-1);
  }, j = () => {
    R(1);
  };
  return /* @__PURE__ */ u.createElement("div", {
    className: O(p, {
      [`${p}-overflow-${e.overflow}`]: o,
      [`${p}-overflow-ping-start`]: _,
      [`${p}-overflow-ping-end`]: $
    }, s),
    ref: y,
    onScroll: v,
    style: a
  }, /* @__PURE__ */ u.createElement(Oa, {
    keys: r.map((T) => ({
      key: T.uid,
      item: T
    })),
    motionName: `${p}-card-motion`,
    component: !1,
    motionAppear: h,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: T,
    item: L,
    className: N,
    style: b
  }) => /* @__PURE__ */ u.createElement(xo, {
    key: T,
    prefixCls: t,
    item: L,
    onRemove: n,
    className: O(N, l),
    imageProps: f,
    style: {
      ...b,
      ...m
    }
  })), !x && /* @__PURE__ */ u.createElement(vo, {
    upload: i
  }, /* @__PURE__ */ u.createElement(ie, {
    className: O(c, `${p}-upload-btn`),
    style: d,
    type: "dashed"
  }, /* @__PURE__ */ u.createElement(Jo, {
    className: `${p}-upload-btn-icon`
  }))), o === "scrollX" && /* @__PURE__ */ u.createElement(u.Fragment, null, /* @__PURE__ */ u.createElement(ie, {
    size: "small",
    shape: "circle",
    className: `${p}-prev-btn`,
    icon: /* @__PURE__ */ u.createElement(ei, null),
    onClick: P
  }), /* @__PURE__ */ u.createElement(ie, {
    size: "small",
    shape: "circle",
    className: `${p}-next-btn`,
    icon: /* @__PURE__ */ u.createElement(ti, null),
    onClick: j
  })));
}
function Ga(e, t) {
  const {
    prefixCls: r,
    placeholder: n = {},
    upload: o,
    className: i,
    style: s
  } = e, a = `${r}-placeholder`, l = n || {}, {
    disabled: c
  } = u.useContext(nt), [d, m] = u.useState(!1), f = () => {
    m(!0);
  }, p = (g) => {
    g.currentTarget.contains(g.relatedTarget) || m(!1);
  }, y = () => {
    m(!1);
  }, h = /* @__PURE__ */ u.isValidElement(n) ? n : /* @__PURE__ */ u.createElement(Ee, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ u.createElement(Te.Text, {
    className: `${a}-icon`
  }, l.icon), /* @__PURE__ */ u.createElement(Te.Title, {
    className: `${a}-title`,
    level: 5
  }, l.title), /* @__PURE__ */ u.createElement(Te.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, l.description));
  return /* @__PURE__ */ u.createElement("div", {
    className: O(a, {
      [`${a}-drag-in`]: d,
      [`${a}-disabled`]: c
    }, i),
    onDragEnter: f,
    onDragLeave: p,
    onDrop: y,
    "aria-hidden": c,
    style: s
  }, /* @__PURE__ */ u.createElement(Dn.Dragger, ye({
    showUploadList: !1
  }, o, {
    ref: t,
    style: {
      padding: 0,
      border: 0,
      background: "transparent"
    }
  }), h));
}
const Ka = /* @__PURE__ */ u.forwardRef(Ga);
function qa(e, t) {
  const {
    prefixCls: r,
    rootClassName: n,
    rootStyle: o,
    className: i,
    style: s,
    items: a,
    children: l,
    getDropContainer: c,
    placeholder: d,
    onChange: m,
    onRemove: f,
    overflow: p,
    imageProps: y,
    disabled: h,
    maxCount: g,
    classNames: x = {},
    styles: _ = {},
    ...w
  } = e, {
    getPrefixCls: $,
    direction: I
  } = Ie(), v = $("attachment", r), R = $t("attachments"), {
    classNames: P,
    styles: j
  } = R, T = u.useRef(null), L = u.useRef(null);
  u.useImperativeHandle(t, () => ({
    nativeElement: T.current,
    upload: (U) => {
      var q, ee;
      const V = (ee = (q = L.current) == null ? void 0 : q.nativeElement) == null ? void 0 : ee.querySelector('input[type="file"]');
      if (V) {
        const Z = new DataTransfer();
        Z.items.add(U), V.files = Z.files, V.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [N, b, E] = bo(v), F = O(b, E), [D, B] = Ns([], {
    value: a
  }), z = Oe((U) => {
    B(U.fileList), m == null || m(U);
  }), W = {
    ...w,
    fileList: D,
    maxCount: g,
    onChange: z
  }, oe = (U) => Promise.resolve(typeof f == "function" ? f(U) : f).then((V) => {
    if (V === !1)
      return;
    const q = D.filter((ee) => ee.uid !== U.uid);
    z({
      file: {
        ...U,
        status: "removed"
      },
      fileList: q
    });
  });
  let G;
  const J = (U, V, q) => {
    const ee = typeof d == "function" ? d(U) : d;
    return /* @__PURE__ */ u.createElement(Ka, {
      placeholder: ee,
      upload: W,
      prefixCls: v,
      className: O(P.placeholder, x.placeholder),
      style: {
        ...j.placeholder,
        ..._.placeholder,
        ...V == null ? void 0 : V.style
      },
      ref: q
    });
  };
  if (l)
    G = /* @__PURE__ */ u.createElement(u.Fragment, null, /* @__PURE__ */ u.createElement(vo, {
      upload: W,
      rootClassName: n,
      ref: L
    }, l), /* @__PURE__ */ u.createElement(mn, {
      getDropContainer: c,
      prefixCls: v,
      className: O(F, n)
    }, J("drop")));
  else {
    const U = D.length > 0;
    G = /* @__PURE__ */ u.createElement("div", {
      className: O(v, F, {
        [`${v}-rtl`]: I === "rtl"
      }, i, n),
      style: {
        ...o,
        ...s
      },
      dir: I || "ltr",
      ref: T
    }, /* @__PURE__ */ u.createElement(Ua, {
      prefixCls: v,
      items: D,
      onRemove: oe,
      overflow: p,
      upload: W,
      listClassName: O(P.list, x.list),
      listStyle: {
        ...j.list,
        ..._.list,
        ...!U && {
          display: "none"
        }
      },
      uploadClassName: O(P.upload, x.upload),
      uploadStyle: {
        ...j.upload,
        ..._.upload
      },
      itemClassName: O(P.item, x.item),
      itemStyle: {
        ...j.item,
        ..._.item
      },
      imageProps: y
    }), J("inline", U ? {
      style: {
        display: "none"
      }
    } : {}, L), /* @__PURE__ */ u.createElement(mn, {
      getDropContainer: c || (() => T.current),
      prefixCls: v,
      className: F
    }, J("drop")));
  }
  return N(/* @__PURE__ */ u.createElement(nt.Provider, {
    value: {
      disabled: h
    }
  }, G));
}
const wo = /* @__PURE__ */ u.forwardRef(qa);
wo.FileCard = xo;
function dt(e) {
  return typeof e == "string";
}
function Ya(e, t) {
  let r = 0;
  const n = Math.min(e.length, t.length);
  for (; r < n && e[r] === t[r]; )
    r++;
  return r;
}
const Za = (e, t, r, n) => {
  const o = M.useRef(""), [i, s] = M.useState(1), a = t && dt(e);
  return Jn(() => {
    if (!a && dt(e))
      s(e.length);
    else if (dt(e) && dt(o.current) && e.indexOf(o.current) !== 0) {
      if (!e || !o.current) {
        s(1);
        return;
      }
      const c = Ya(e, o.current);
      s(c === 0 ? 1 : c + 1);
    }
    o.current = e;
  }, [e]), M.useEffect(() => {
    if (a && i < e.length) {
      const c = setTimeout(() => {
        s((d) => d + r);
      }, n);
      return () => {
        clearTimeout(c);
      };
    }
  }, [i, t, e]), [a ? e.slice(0, i) : e, a && i < e.length];
};
function Qa(e) {
  return M.useMemo(() => {
    if (!e)
      return [!1, 0, 0, null];
    let t = {
      step: 1,
      interval: 50,
      // set default suffix is empty
      suffix: null
    };
    return typeof e == "object" && (t = {
      ...t,
      ...e
    }), [!0, t.step, t.interval, t.suffix];
  }, [e]);
}
const Ja = ({
  prefixCls: e
}) => /* @__PURE__ */ u.createElement("span", {
  className: `${e}-dot`
}, /* @__PURE__ */ u.createElement("i", {
  className: `${e}-dot-item`,
  key: "item-1"
}), /* @__PURE__ */ u.createElement("i", {
  className: `${e}-dot-item`,
  key: "item-2"
}), /* @__PURE__ */ u.createElement("i", {
  className: `${e}-dot-item`,
  key: "item-3"
})), el = (e) => {
  const {
    componentCls: t,
    paddingSM: r,
    padding: n
  } = e;
  return {
    [t]: {
      [`${t}-content`]: {
        // Shared: filled, outlined, shadow
        "&-filled,&-outlined,&-shadow": {
          padding: `${Ve(r)} ${Ve(n)}`,
          borderRadius: e.borderRadiusLG
        },
        // Filled:
        "&-filled": {
          backgroundColor: e.colorFillContent
        },
        // Outlined:
        "&-outlined": {
          border: `1px solid ${e.colorBorderSecondary}`
        },
        // Shadow:
        "&-shadow": {
          boxShadow: e.boxShadowTertiary
        }
      }
    }
  };
}, tl = (e) => {
  const {
    componentCls: t,
    fontSize: r,
    lineHeight: n,
    paddingSM: o,
    padding: i,
    calc: s
  } = e, a = s(r).mul(n).div(2).add(o).equal(), l = `${t}-content`;
  return {
    [t]: {
      [l]: {
        // round:
        "&-round": {
          borderRadius: {
            _skip_check_: !0,
            value: a
          },
          paddingInline: s(i).mul(1.25).equal()
        }
      },
      // corner:
      [`&-start ${l}-corner`]: {
        borderStartStartRadius: e.borderRadiusXS
      },
      [`&-end ${l}-corner`]: {
        borderStartEndRadius: e.borderRadiusXS
      }
    }
  };
}, rl = (e) => {
  const {
    componentCls: t,
    padding: r
  } = e;
  return {
    [`${t}-list`]: {
      display: "flex",
      flexDirection: "column",
      gap: r,
      overflowY: "auto",
      "&::-webkit-scrollbar": {
        width: 8,
        backgroundColor: "transparent"
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: e.colorTextTertiary,
        borderRadius: e.borderRadiusSM
      },
      // For Firefox
      "&": {
        scrollbarWidth: "thin",
        scrollbarColor: `${e.colorTextTertiary} transparent`
      }
    }
  };
}, nl = new Bn("loadingMove", {
  "0%": {
    transform: "translateY(0)"
  },
  "10%": {
    transform: "translateY(4px)"
  },
  "20%": {
    transform: "translateY(0)"
  },
  "30%": {
    transform: "translateY(-4px)"
  },
  "40%": {
    transform: "translateY(0)"
  }
}), ol = new Bn("cursorBlink", {
  "0%": {
    opacity: 1
  },
  "50%": {
    opacity: 0
  },
  "100%": {
    opacity: 1
  }
}), il = (e) => {
  const {
    componentCls: t,
    fontSize: r,
    lineHeight: n,
    paddingSM: o,
    colorText: i,
    calc: s
  } = e;
  return {
    [t]: {
      display: "flex",
      columnGap: o,
      [`&${t}-end`]: {
        justifyContent: "end",
        flexDirection: "row-reverse",
        [`& ${t}-content-wrapper`]: {
          alignItems: "flex-end"
        }
      },
      [`&${t}-rtl`]: {
        direction: "rtl"
      },
      [`&${t}-typing ${t}-content:last-child::after`]: {
        content: '"|"',
        fontWeight: 900,
        userSelect: "none",
        opacity: 1,
        marginInlineStart: "0.1em",
        animationName: ol,
        animationDuration: "0.8s",
        animationIterationCount: "infinite",
        animationTimingFunction: "linear"
      },
      // ============================ Avatar =============================
      [`& ${t}-avatar`]: {
        display: "inline-flex",
        justifyContent: "center",
        alignSelf: "flex-start"
      },
      // ======================== Header & Footer ========================
      [`& ${t}-header, & ${t}-footer`]: {
        fontSize: r,
        lineHeight: n,
        color: e.colorText
      },
      [`& ${t}-header`]: {
        marginBottom: e.paddingXXS
      },
      [`& ${t}-footer`]: {
        marginTop: o
      },
      // =========================== Content =============================
      [`& ${t}-content-wrapper`]: {
        flex: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        minWidth: 0,
        maxWidth: "100%"
      },
      [`& ${t}-content`]: {
        position: "relative",
        boxSizing: "border-box",
        minWidth: 0,
        maxWidth: "100%",
        color: i,
        fontSize: e.fontSize,
        lineHeight: e.lineHeight,
        minHeight: s(o).mul(2).add(s(n).mul(r)).equal(),
        wordBreak: "break-word",
        [`& ${t}-dot`]: {
          position: "relative",
          height: "100%",
          display: "flex",
          alignItems: "center",
          columnGap: e.marginXS,
          padding: `0 ${Ve(e.paddingXXS)}`,
          "&-item": {
            backgroundColor: e.colorPrimary,
            borderRadius: "100%",
            width: 4,
            height: 4,
            animationName: nl,
            animationDuration: "2s",
            animationIterationCount: "infinite",
            animationTimingFunction: "linear",
            "&:nth-child(1)": {
              animationDelay: "0s"
            },
            "&:nth-child(2)": {
              animationDelay: "0.2s"
            },
            "&:nth-child(3)": {
              animationDelay: "0.4s"
            }
          }
        }
      }
    }
  };
}, sl = () => ({}), _o = Ht("Bubble", (e) => {
  const t = Ke(e, {});
  return [il(t), rl(t), el(t), tl(t)];
}, sl), Eo = /* @__PURE__ */ u.createContext({}), al = (e, t) => {
  const {
    prefixCls: r,
    className: n,
    rootClassName: o,
    style: i,
    classNames: s = {},
    styles: a = {},
    avatar: l,
    placement: c = "start",
    loading: d = !1,
    loadingRender: m,
    typing: f,
    content: p = "",
    messageRender: y,
    variant: h = "filled",
    shape: g,
    onTypingComplete: x,
    header: _,
    footer: w,
    _key: $,
    ...I
  } = e, {
    onUpdate: v
  } = u.useContext(Eo), R = u.useRef(null);
  u.useImperativeHandle(t, () => ({
    nativeElement: R.current
  }));
  const {
    direction: P,
    getPrefixCls: j
  } = Ie(), T = j("bubble", r), L = $t("bubble"), [N, b, E, F] = Qa(f), [D, B] = Za(p, N, b, E);
  u.useEffect(() => {
    v == null || v();
  }, [D]);
  const z = u.useRef(!1);
  u.useEffect(() => {
    !B && !d ? z.current || (z.current = !0, x == null || x()) : z.current = !1;
  }, [B, d]);
  const [W, oe, G] = _o(T), J = O(T, o, L.className, n, oe, G, `${T}-${c}`, {
    [`${T}-rtl`]: P === "rtl",
    [`${T}-typing`]: B && !d && !y && !F
  }), U = u.useMemo(() => /* @__PURE__ */ u.isValidElement(l) ? l : /* @__PURE__ */ u.createElement(pi, l), [l]), V = u.useMemo(() => y ? y(D) : D, [D, y]), q = (Se) => typeof Se == "function" ? Se(D, {
    key: $
  }) : Se;
  let ee;
  d ? ee = m ? m() : /* @__PURE__ */ u.createElement(Ja, {
    prefixCls: T
  }) : ee = /* @__PURE__ */ u.createElement(u.Fragment, null, V, B && F);
  let Z = /* @__PURE__ */ u.createElement("div", {
    style: {
      ...L.styles.content,
      ...a.content
    },
    className: O(`${T}-content`, `${T}-content-${h}`, g && `${T}-content-${g}`, L.classNames.content, s.content)
  }, ee);
  return (_ || w) && (Z = /* @__PURE__ */ u.createElement("div", {
    className: `${T}-content-wrapper`
  }, _ && /* @__PURE__ */ u.createElement("div", {
    className: O(`${T}-header`, L.classNames.header, s.header),
    style: {
      ...L.styles.header,
      ...a.header
    }
  }, q(_)), Z, w && /* @__PURE__ */ u.createElement("div", {
    className: O(`${T}-footer`, L.classNames.footer, s.footer),
    style: {
      ...L.styles.footer,
      ...a.footer
    }
  }, q(w)))), W(/* @__PURE__ */ u.createElement("div", ye({
    style: {
      ...L.style,
      ...i
    },
    className: J
  }, I, {
    ref: R
  }), l && /* @__PURE__ */ u.createElement("div", {
    style: {
      ...L.styles.avatar,
      ...a.avatar
    },
    className: O(`${T}-avatar`, L.classNames.avatar, s.avatar)
  }, U), Z));
}, Cr = /* @__PURE__ */ u.forwardRef(al);
function ll(e, t) {
  const r = M.useCallback((n, o) => typeof t == "function" ? t(n, o) : t ? t[n.role] || {} : {}, [t]);
  return M.useMemo(() => (e || []).map((n, o) => {
    const i = n.key ?? `preset_${o}`;
    return {
      ...r(n, o),
      ...n,
      key: i
    };
  }), [e, r]);
}
const cl = ({
  _key: e,
  ...t
}, r) => /* @__PURE__ */ M.createElement(Cr, ye({}, t, {
  _key: e,
  ref: (n) => {
    var o;
    n ? r.current[e] = n : (o = r.current) == null || delete o[e];
  }
})), ul = /* @__PURE__ */ M.memo(/* @__PURE__ */ M.forwardRef(cl)), fl = 1, dl = (e, t) => {
  const {
    prefixCls: r,
    rootClassName: n,
    className: o,
    items: i,
    autoScroll: s = !0,
    roles: a,
    onScroll: l,
    ...c
  } = e, d = vs(c, {
    attr: !0,
    aria: !0
  }), m = M.useRef(null), f = M.useRef({}), {
    getPrefixCls: p
  } = Ie(), y = p("bubble", r), h = `${y}-list`, [g, x, _] = _o(y), [w, $] = M.useState(!1);
  M.useEffect(() => ($(!0), () => {
    $(!1);
  }), []);
  const I = ll(i, a), [v, R] = M.useState(!0), [P, j] = M.useState(0), T = (b) => {
    const E = b.target;
    R(E.scrollHeight - Math.abs(E.scrollTop) - E.clientHeight <= fl), l == null || l(b);
  };
  M.useEffect(() => {
    s && m.current && v && m.current.scrollTo({
      top: m.current.scrollHeight
    });
  }, [P]), M.useEffect(() => {
    var b;
    if (s) {
      const E = (b = I[I.length - 2]) == null ? void 0 : b.key, F = f.current[E];
      if (F) {
        const {
          nativeElement: D
        } = F, {
          top: B,
          bottom: z
        } = D.getBoundingClientRect(), {
          top: W,
          bottom: oe
        } = m.current.getBoundingClientRect();
        B < oe && z > W && (j((J) => J + 1), R(!0));
      }
    }
  }, [I.length]), M.useImperativeHandle(t, () => ({
    nativeElement: m.current,
    scrollTo: ({
      key: b,
      offset: E,
      behavior: F = "smooth",
      block: D
    }) => {
      if (typeof E == "number")
        m.current.scrollTo({
          top: E,
          behavior: F
        });
      else if (b !== void 0) {
        const B = f.current[b];
        if (B) {
          const z = I.findIndex((W) => W.key === b);
          R(z === I.length - 1), B.nativeElement.scrollIntoView({
            behavior: F,
            block: D
          });
        }
      }
    }
  }));
  const L = Oe(() => {
    s && j((b) => b + 1);
  }), N = M.useMemo(() => ({
    onUpdate: L
  }), []);
  return g(/* @__PURE__ */ M.createElement(Eo.Provider, {
    value: N
  }, /* @__PURE__ */ M.createElement("div", ye({}, d, {
    className: O(h, n, o, x, _, {
      [`${h}-reach-end`]: v
    }),
    ref: m,
    onScroll: T
  }), I.map(({
    key: b,
    ...E
  }) => /* @__PURE__ */ M.createElement(ul, ye({}, E, {
    key: b,
    _key: b,
    ref: f,
    typing: w ? E.typing : !1
  }))))));
}, ml = /* @__PURE__ */ M.forwardRef(dl);
Cr.List = ml;
const pl = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      // ======================== Prompt ========================
      "&, & *": {
        boxSizing: "border-box"
      },
      maxWidth: "100%",
      [`&${t}-rtl`]: {
        direction: "rtl"
      },
      [`& ${t}-title`]: {
        marginBlockStart: 0,
        fontWeight: "normal",
        color: e.colorTextTertiary
      },
      [`& ${t}-list`]: {
        display: "flex",
        gap: e.paddingSM,
        overflowX: "auto",
        // Hide scrollbar
        scrollbarWidth: "none",
        "-ms-overflow-style": "none",
        "&::-webkit-scrollbar": {
          display: "none"
        },
        listStyle: "none",
        paddingInlineStart: 0,
        marginBlock: 0,
        alignItems: "stretch",
        "&-wrap": {
          flexWrap: "wrap"
        },
        "&-vertical": {
          flexDirection: "column",
          alignItems: "flex-start"
        }
      },
      // ========================= Item =========================
      [`${t}-item`]: {
        flex: "none",
        display: "flex",
        gap: e.paddingXS,
        height: "auto",
        paddingBlock: e.paddingSM,
        paddingInline: e.padding,
        alignItems: "flex-start",
        justifyContent: "flex-start",
        background: e.colorBgContainer,
        borderRadius: e.borderRadiusLG,
        transition: ["border", "background"].map((r) => `${r} ${e.motionDurationSlow}`).join(","),
        border: `${Ve(e.lineWidth)} ${e.lineType} ${e.colorBorderSecondary}`,
        [`&:not(${t}-item-has-nest)`]: {
          "&:hover": {
            cursor: "pointer",
            background: e.colorFillTertiary
          },
          "&:active": {
            background: e.colorFill
          }
        },
        [`${t}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          gap: e.paddingXXS,
          flexDirection: "column",
          alignItems: "flex-start"
        },
        [`${t}-icon, ${t}-label, ${t}-desc`]: {
          margin: 0,
          padding: 0,
          fontSize: e.fontSize,
          lineHeight: e.lineHeight,
          textAlign: "start",
          whiteSpace: "normal"
        },
        [`${t}-label`]: {
          color: e.colorTextHeading,
          fontWeight: 500
        },
        [`${t}-label + ${t}-desc`]: {
          color: e.colorTextTertiary
        },
        // Disabled
        [`&${t}-item-disabled`]: {
          pointerEvents: "none",
          background: e.colorBgContainerDisabled,
          [`${t}-label, ${t}-desc`]: {
            color: e.colorTextTertiary
          }
        }
      }
    }
  };
}, gl = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      // ========================= Parent =========================
      [`${t}-item-has-nest`]: {
        [`> ${t}-content`]: {
          // gap: token.paddingSM,
          [`> ${t}-label`]: {
            fontSize: e.fontSizeLG,
            lineHeight: e.lineHeightLG
          }
        }
      },
      // ========================= Nested =========================
      [`&${t}-nested`]: {
        marginTop: e.paddingXS,
        // ======================== Prompt ========================
        alignSelf: "stretch",
        [`${t}-list`]: {
          alignItems: "stretch"
        },
        // ========================= Item =========================
        [`${t}-item`]: {
          border: 0,
          background: e.colorFillQuaternary
        }
      }
    }
  };
}, hl = () => ({}), yl = Ht("Prompts", (e) => {
  const t = Ke(e, {});
  return [pl(t), gl(t)];
}, hl), Tr = (e) => {
  const {
    prefixCls: t,
    title: r,
    className: n,
    items: o,
    onItemClick: i,
    vertical: s,
    wrap: a,
    rootClassName: l,
    styles: c = {},
    classNames: d = {},
    style: m,
    ...f
  } = e, {
    getPrefixCls: p,
    direction: y
  } = Ie(), h = p("prompts", t), g = $t("prompts"), [x, _, w] = yl(h), $ = O(h, g.className, n, l, _, w, {
    [`${h}-rtl`]: y === "rtl"
  }), I = O(`${h}-list`, g.classNames.list, d.list, {
    [`${h}-list-wrap`]: a
  }, {
    [`${h}-list-vertical`]: s
  });
  return x(/* @__PURE__ */ u.createElement("div", ye({}, f, {
    className: $,
    style: {
      ...m,
      ...g.style
    }
  }), r && /* @__PURE__ */ u.createElement(Te.Title, {
    level: 5,
    className: O(`${h}-title`, g.classNames.title, d.title),
    style: {
      ...g.styles.title,
      ...c.title
    }
  }, r), /* @__PURE__ */ u.createElement("div", {
    className: I,
    style: {
      ...g.styles.list,
      ...c.list
    }
  }, o == null ? void 0 : o.map((v, R) => {
    const P = v.children && v.children.length > 0;
    return /* @__PURE__ */ u.createElement("div", {
      key: v.key || `key_${R}`,
      style: {
        ...g.styles.item,
        ...c.item
      },
      className: O(`${h}-item`, g.classNames.item, d.item, {
        [`${h}-item-disabled`]: v.disabled,
        [`${h}-item-has-nest`]: P
      }),
      onClick: () => {
        !P && i && i({
          data: v
        });
      }
    }, v.icon && /* @__PURE__ */ u.createElement("div", {
      className: `${h}-icon`
    }, v.icon), /* @__PURE__ */ u.createElement("div", {
      className: O(`${h}-content`, g.classNames.itemContent, d.itemContent),
      style: {
        ...g.styles.itemContent,
        ...c.itemContent
      }
    }, v.label && /* @__PURE__ */ u.createElement("h6", {
      className: `${h}-label`
    }, v.label), v.description && /* @__PURE__ */ u.createElement("p", {
      className: `${h}-desc`
    }, v.description), P && /* @__PURE__ */ u.createElement(Tr, {
      className: `${h}-nested`,
      items: v.children,
      vertical: !0,
      onItemClick: i,
      classNames: {
        list: d.subList,
        item: d.subItem
      },
      styles: {
        list: c.subList,
        item: c.subItem
      }
    })));
  }))));
}, vl = (e) => {
  const {
    componentCls: t,
    calc: r
  } = e, n = r(e.fontSizeHeading3).mul(e.lineHeightHeading3).equal(), o = r(e.fontSize).mul(e.lineHeight).equal();
  return {
    [t]: {
      gap: e.padding,
      // ======================== Icon ========================
      [`${t}-icon`]: {
        height: r(n).add(o).add(e.paddingXXS).equal(),
        display: "flex",
        img: {
          height: "100%"
        }
      },
      // ==================== Content Wrap ====================
      [`${t}-content-wrapper`]: {
        gap: e.paddingXS,
        flex: "auto",
        minWidth: 0,
        [`${t}-title-wrapper`]: {
          gap: e.paddingXS
        },
        [`${t}-title`]: {
          margin: 0
        },
        [`${t}-extra`]: {
          marginInlineStart: "auto"
        }
      }
    }
  };
}, bl = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      // ======================== Filled ========================
      "&-filled": {
        paddingInline: e.padding,
        paddingBlock: e.paddingSM,
        background: e.colorFillContent,
        borderRadius: e.borderRadiusLG
      },
      // ====================== Borderless ======================
      "&-borderless": {
        [`${t}-title`]: {
          fontSize: e.fontSizeHeading3,
          lineHeight: e.lineHeightHeading3
        }
      }
    }
  };
}, Sl = () => ({}), xl = Ht("Welcome", (e) => {
  const t = Ke(e, {});
  return [vl(t), bl(t)];
}, Sl);
function wl(e, t) {
  const {
    prefixCls: r,
    rootClassName: n,
    className: o,
    style: i,
    variant: s = "filled",
    // Semantic
    classNames: a = {},
    styles: l = {},
    // Layout
    icon: c,
    title: d,
    description: m,
    extra: f
  } = e, {
    direction: p,
    getPrefixCls: y
  } = Ie(), h = y("welcome", r), g = $t("welcome"), [x, _, w] = xl(h), $ = u.useMemo(() => {
    if (!c)
      return null;
    let R = c;
    return typeof c == "string" && c.startsWith("http") && (R = /* @__PURE__ */ u.createElement("img", {
      src: c,
      alt: "icon"
    })), /* @__PURE__ */ u.createElement("div", {
      className: O(`${h}-icon`, g.classNames.icon, a.icon),
      style: l.icon
    }, R);
  }, [c]), I = u.useMemo(() => d ? /* @__PURE__ */ u.createElement(Te.Title, {
    level: 4,
    className: O(`${h}-title`, g.classNames.title, a.title),
    style: l.title
  }, d) : null, [d]), v = u.useMemo(() => f ? /* @__PURE__ */ u.createElement("div", {
    className: O(`${h}-extra`, g.classNames.extra, a.extra),
    style: l.extra
  }, f) : null, [f]);
  return x(/* @__PURE__ */ u.createElement(Ee, {
    ref: t,
    className: O(h, g.className, o, n, _, w, `${h}-${s}`, {
      [`${h}-rtl`]: p === "rtl"
    }),
    style: i
  }, $, /* @__PURE__ */ u.createElement(Ee, {
    vertical: !0,
    className: `${h}-content-wrapper`
  }, f ? /* @__PURE__ */ u.createElement(Ee, {
    align: "flex-start",
    className: `${h}-title-wrapper`
  }, I, v) : I, m && /* @__PURE__ */ u.createElement(Te.Text, {
    className: O(`${h}-description`, g.classNames.description, a.description),
    style: l.description
  }, m))));
}
const _l = /* @__PURE__ */ u.forwardRef(wl);
function ne(e) {
  const t = re(e);
  return t.current = e, zo((...r) => {
    var n;
    return (n = t.current) == null ? void 0 : n.call(t, ...r);
  }, []);
}
function ve(e, t) {
  return Object.keys(e).reduce((r, n) => (e[n] !== void 0 && (!(t != null && t.omitNull) || e[n] !== null) && (r[n] = e[n]), r), {});
}
var Co = Symbol.for("immer-nothing"), Cn = Symbol.for("immer-draftable"), le = Symbol.for("immer-state");
function ge(e, ...t) {
  throw new Error(`[Immer] minified error nr: ${e}. Full error at: https://bit.ly/3cXEKWf`);
}
var Je = Object.getPrototypeOf;
function Xe(e) {
  return !!e && !!e[le];
}
function je(e) {
  var t;
  return e ? To(e) || Array.isArray(e) || !!e[Cn] || !!((t = e.constructor) != null && t[Cn]) || ot(e) || Wt(e) : !1;
}
var El = Object.prototype.constructor.toString(), Tn = /* @__PURE__ */ new WeakMap();
function To(e) {
  if (!e || typeof e != "object") return !1;
  const t = Object.getPrototypeOf(e);
  if (t === null || t === Object.prototype) return !0;
  const r = Object.hasOwnProperty.call(t, "constructor") && t.constructor;
  if (r === Object) return !0;
  if (typeof r != "function") return !1;
  let n = Tn.get(r);
  return n === void 0 && (n = Function.toString.call(r), Tn.set(r, n)), n === El;
}
function _t(e, t, r = !0) {
  Bt(e) === 0 ? (r ? Reflect.ownKeys(e) : Object.keys(e)).forEach((o) => {
    t(o, e[o], e);
  }) : e.forEach((n, o) => t(o, n, e));
}
function Bt(e) {
  const t = e[le];
  return t ? t.type_ : Array.isArray(e) ? 1 : ot(e) ? 2 : Wt(e) ? 3 : 0;
}
function mr(e, t) {
  return Bt(e) === 2 ? e.has(t) : Object.prototype.hasOwnProperty.call(e, t);
}
function $o(e, t, r) {
  const n = Bt(e);
  n === 2 ? e.set(t, r) : n === 3 ? e.add(r) : e[t] = r;
}
function Cl(e, t) {
  return e === t ? e !== 0 || 1 / e === 1 / t : e !== e && t !== t;
}
function ot(e) {
  return e instanceof Map;
}
function Wt(e) {
  return e instanceof Set;
}
function Me(e) {
  return e.copy_ || e.base_;
}
function pr(e, t) {
  if (ot(e))
    return new Map(e);
  if (Wt(e))
    return new Set(e);
  if (Array.isArray(e)) return Array.prototype.slice.call(e);
  const r = To(e);
  if (t === !0 || t === "class_only" && !r) {
    const n = Object.getOwnPropertyDescriptors(e);
    delete n[le];
    let o = Reflect.ownKeys(n);
    for (let i = 0; i < o.length; i++) {
      const s = o[i], a = n[s];
      a.writable === !1 && (a.writable = !0, a.configurable = !0), (a.get || a.set) && (n[s] = {
        configurable: !0,
        writable: !0,
        // could live with !!desc.set as well here...
        enumerable: a.enumerable,
        value: e[s]
      });
    }
    return Object.create(Je(e), n);
  } else {
    const n = Je(e);
    if (n !== null && r)
      return {
        ...e
      };
    const o = Object.create(n);
    return Object.assign(o, e);
  }
}
function $r(e, t = !1) {
  return Vt(e) || Xe(e) || !je(e) || (Bt(e) > 1 && Object.defineProperties(e, {
    set: mt,
    add: mt,
    clear: mt,
    delete: mt
  }), Object.freeze(e), t && Object.values(e).forEach((r) => $r(r, !0))), e;
}
function Tl() {
  ge(2);
}
var mt = {
  value: Tl
};
function Vt(e) {
  return e === null || typeof e != "object" ? !0 : Object.isFrozen(e);
}
var $l = {};
function Ne(e) {
  const t = $l[e];
  return t || ge(0, e), t;
}
var et;
function Io() {
  return et;
}
function Il(e, t) {
  return {
    drafts_: [],
    parent_: e,
    immer_: t,
    // Whenever the modified draft contains a draft from another scope, we
    // need to prevent auto-freezing so the unowned draft can be finalized.
    canAutoFreeze_: !0,
    unfinalizedDrafts_: 0
  };
}
function $n(e, t) {
  t && (Ne("Patches"), e.patches_ = [], e.inversePatches_ = [], e.patchListener_ = t);
}
function gr(e) {
  hr(e), e.drafts_.forEach(Pl), e.drafts_ = null;
}
function hr(e) {
  e === et && (et = e.parent_);
}
function In(e) {
  return et = Il(et, e);
}
function Pl(e) {
  const t = e[le];
  t.type_ === 0 || t.type_ === 1 ? t.revoke_() : t.revoked_ = !0;
}
function Pn(e, t) {
  t.unfinalizedDrafts_ = t.drafts_.length;
  const r = t.drafts_[0];
  return e !== void 0 && e !== r ? (r[le].modified_ && (gr(t), ge(4)), je(e) && (e = Et(t, e), t.parent_ || Ct(t, e)), t.patches_ && Ne("Patches").generateReplacementPatches_(r[le].base_, e, t.patches_, t.inversePatches_)) : e = Et(t, r, []), gr(t), t.patches_ && t.patchListener_(t.patches_, t.inversePatches_), e !== Co ? e : void 0;
}
function Et(e, t, r) {
  if (Vt(t)) return t;
  const n = e.immer_.shouldUseStrictIteration(), o = t[le];
  if (!o)
    return _t(t, (i, s) => Rn(e, o, t, i, s, r), n), t;
  if (o.scope_ !== e) return t;
  if (!o.modified_)
    return Ct(e, o.base_, !0), o.base_;
  if (!o.finalized_) {
    o.finalized_ = !0, o.scope_.unfinalizedDrafts_--;
    const i = o.copy_;
    let s = i, a = !1;
    o.type_ === 3 && (s = new Set(i), i.clear(), a = !0), _t(s, (l, c) => Rn(e, o, i, l, c, r, a), n), Ct(e, i, !1), r && e.patches_ && Ne("Patches").generatePatches_(o, r, e.patches_, e.inversePatches_);
  }
  return o.copy_;
}
function Rn(e, t, r, n, o, i, s) {
  if (o == null || typeof o != "object" && !s)
    return;
  const a = Vt(o);
  if (!(a && !s)) {
    if (Xe(o)) {
      const l = i && t && t.type_ !== 3 && // Set objects are atomic since they have no keys.
      !mr(t.assigned_, n) ? i.concat(n) : void 0, c = Et(e, o, l);
      if ($o(r, n, c), Xe(c))
        e.canAutoFreeze_ = !1;
      else return;
    } else s && r.add(o);
    if (je(o) && !a) {
      if (!e.immer_.autoFreeze_ && e.unfinalizedDrafts_ < 1 || t && t.base_ && t.base_[n] === o && a)
        return;
      Et(e, o), (!t || !t.scope_.parent_) && typeof n != "symbol" && (ot(r) ? r.has(n) : Object.prototype.propertyIsEnumerable.call(r, n)) && Ct(e, o);
    }
  }
}
function Ct(e, t, r = !1) {
  !e.parent_ && e.immer_.autoFreeze_ && e.canAutoFreeze_ && $r(t, r);
}
function Rl(e, t) {
  const r = Array.isArray(e), n = {
    type_: r ? 1 : 0,
    // Track which produce call this is associated with.
    scope_: t ? t.scope_ : Io(),
    // True for both shallow and deep changes.
    modified_: !1,
    // Used during finalization.
    finalized_: !1,
    // Track which properties have been assigned (true) or deleted (false).
    assigned_: {},
    // The parent draft state.
    parent_: t,
    // The base state.
    base_: e,
    // The base proxy.
    draft_: null,
    // set below
    // The base copy with any updated values.
    copy_: null,
    // Called by the `produce` function.
    revoke_: null,
    isManual_: !1
  };
  let o = n, i = Ir;
  r && (o = [n], i = tt);
  const {
    revoke: s,
    proxy: a
  } = Proxy.revocable(o, i);
  return n.draft_ = a, n.revoke_ = s, a;
}
var Ir = {
  get(e, t) {
    if (t === le) return e;
    const r = Me(e);
    if (!mr(r, t))
      return Ml(e, r, t);
    const n = r[t];
    return e.finalized_ || !je(n) ? n : n === rr(e.base_, t) ? (nr(e), e.copy_[t] = vr(n, e)) : n;
  },
  has(e, t) {
    return t in Me(e);
  },
  ownKeys(e) {
    return Reflect.ownKeys(Me(e));
  },
  set(e, t, r) {
    const n = Po(Me(e), t);
    if (n != null && n.set)
      return n.set.call(e.draft_, r), !0;
    if (!e.modified_) {
      const o = rr(Me(e), t), i = o == null ? void 0 : o[le];
      if (i && i.base_ === r)
        return e.copy_[t] = r, e.assigned_[t] = !1, !0;
      if (Cl(r, o) && (r !== void 0 || mr(e.base_, t))) return !0;
      nr(e), yr(e);
    }
    return e.copy_[t] === r && // special case: handle new props with value 'undefined'
    (r !== void 0 || t in e.copy_) || // special case: NaN
    Number.isNaN(r) && Number.isNaN(e.copy_[t]) || (e.copy_[t] = r, e.assigned_[t] = !0), !0;
  },
  deleteProperty(e, t) {
    return rr(e.base_, t) !== void 0 || t in e.base_ ? (e.assigned_[t] = !1, nr(e), yr(e)) : delete e.assigned_[t], e.copy_ && delete e.copy_[t], !0;
  },
  // Note: We never coerce `desc.value` into an Immer draft, because we can't make
  // the same guarantee in ES5 mode.
  getOwnPropertyDescriptor(e, t) {
    const r = Me(e), n = Reflect.getOwnPropertyDescriptor(r, t);
    return n && {
      writable: !0,
      configurable: e.type_ !== 1 || t !== "length",
      enumerable: n.enumerable,
      value: r[t]
    };
  },
  defineProperty() {
    ge(11);
  },
  getPrototypeOf(e) {
    return Je(e.base_);
  },
  setPrototypeOf() {
    ge(12);
  }
}, tt = {};
_t(Ir, (e, t) => {
  tt[e] = function() {
    return arguments[0] = arguments[0][0], t.apply(this, arguments);
  };
});
tt.deleteProperty = function(e, t) {
  return tt.set.call(this, e, t, void 0);
};
tt.set = function(e, t, r) {
  return Ir.set.call(this, e[0], t, r, e[0]);
};
function rr(e, t) {
  const r = e[le];
  return (r ? Me(r) : e)[t];
}
function Ml(e, t, r) {
  var o;
  const n = Po(t, r);
  return n ? "value" in n ? n.value : (
    // This is a very special case, if the prop is a getter defined by the
    // prototype, we should invoke it with the draft as context!
    (o = n.get) == null ? void 0 : o.call(e.draft_)
  ) : void 0;
}
function Po(e, t) {
  if (!(t in e)) return;
  let r = Je(e);
  for (; r; ) {
    const n = Object.getOwnPropertyDescriptor(r, t);
    if (n) return n;
    r = Je(r);
  }
}
function yr(e) {
  e.modified_ || (e.modified_ = !0, e.parent_ && yr(e.parent_));
}
function nr(e) {
  e.copy_ || (e.copy_ = pr(e.base_, e.scope_.immer_.useStrictShallowCopy_));
}
var Ll = class {
  constructor(e) {
    this.autoFreeze_ = !0, this.useStrictShallowCopy_ = !1, this.useStrictIteration_ = !0, this.produce = (t, r, n) => {
      if (typeof t == "function" && typeof r != "function") {
        const i = r;
        r = t;
        const s = this;
        return function(l = i, ...c) {
          return s.produce(l, (d) => r.call(this, d, ...c));
        };
      }
      typeof r != "function" && ge(6), n !== void 0 && typeof n != "function" && ge(7);
      let o;
      if (je(t)) {
        const i = In(this), s = vr(t, void 0);
        let a = !0;
        try {
          o = r(s), a = !1;
        } finally {
          a ? gr(i) : hr(i);
        }
        return $n(i, n), Pn(o, i);
      } else if (!t || typeof t != "object") {
        if (o = r(t), o === void 0 && (o = t), o === Co && (o = void 0), this.autoFreeze_ && $r(o, !0), n) {
          const i = [], s = [];
          Ne("Patches").generateReplacementPatches_(t, o, i, s), n(i, s);
        }
        return o;
      } else ge(1, t);
    }, this.produceWithPatches = (t, r) => {
      if (typeof t == "function")
        return (s, ...a) => this.produceWithPatches(s, (l) => t(l, ...a));
      let n, o;
      return [this.produce(t, r, (s, a) => {
        n = s, o = a;
      }), n, o];
    }, typeof (e == null ? void 0 : e.autoFreeze) == "boolean" && this.setAutoFreeze(e.autoFreeze), typeof (e == null ? void 0 : e.useStrictShallowCopy) == "boolean" && this.setUseStrictShallowCopy(e.useStrictShallowCopy), typeof (e == null ? void 0 : e.useStrictIteration) == "boolean" && this.setUseStrictIteration(e.useStrictIteration);
  }
  createDraft(e) {
    je(e) || ge(8), Xe(e) && (e = Ol(e));
    const t = In(this), r = vr(e, void 0);
    return r[le].isManual_ = !0, hr(t), r;
  }
  finishDraft(e, t) {
    const r = e && e[le];
    (!r || !r.isManual_) && ge(9);
    const {
      scope_: n
    } = r;
    return $n(n, t), Pn(void 0, n);
  }
  /**
   * Pass true to automatically freeze all copies created by Immer.
   *
   * By default, auto-freezing is enabled.
   */
  setAutoFreeze(e) {
    this.autoFreeze_ = e;
  }
  /**
   * Pass true to enable strict shallow copy.
   *
   * By default, immer does not copy the object descriptors such as getter, setter and non-enumrable properties.
   */
  setUseStrictShallowCopy(e) {
    this.useStrictShallowCopy_ = e;
  }
  /**
   * Pass false to use faster iteration that skips non-enumerable properties
   * but still handles symbols for compatibility.
   *
   * By default, strict iteration is enabled (includes all own properties).
   */
  setUseStrictIteration(e) {
    this.useStrictIteration_ = e;
  }
  shouldUseStrictIteration() {
    return this.useStrictIteration_;
  }
  applyPatches(e, t) {
    let r;
    for (r = t.length - 1; r >= 0; r--) {
      const o = t[r];
      if (o.path.length === 0 && o.op === "replace") {
        e = o.value;
        break;
      }
    }
    r > -1 && (t = t.slice(r + 1));
    const n = Ne("Patches").applyPatches_;
    return Xe(e) ? n(e, t) : this.produce(e, (o) => n(o, t));
  }
};
function vr(e, t) {
  const r = ot(e) ? Ne("MapSet").proxyMap_(e, t) : Wt(e) ? Ne("MapSet").proxySet_(e, t) : Rl(e, t);
  return (t ? t.scope_ : Io()).drafts_.push(r), r;
}
function Ol(e) {
  return Xe(e) || ge(10, e), Ro(e);
}
function Ro(e) {
  if (!je(e) || Vt(e)) return e;
  const t = e[le];
  let r, n = !0;
  if (t) {
    if (!t.modified_) return t.base_;
    t.finalized_ = !0, r = pr(e, t.scope_.immer_.useStrictShallowCopy_), n = t.scope_.immer_.shouldUseStrictIteration();
  } else
    r = pr(e, !0);
  return _t(r, (o, i) => {
    $o(r, o, Ro(i));
  }, n), t && (t.finalized_ = !1), r;
}
var jl = new Ll(), Mn = jl.produce;
const {
  useItems: xc,
  withItemsContextProvider: wc,
  ItemHandler: _c
} = Hn("antdx-bubble.list-items"), {
  useItems: Nl,
  withItemsContextProvider: Fl,
  ItemHandler: Ec
} = Hn("antdx-bubble.list-roles");
function kl(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function Al(e, t = !1) {
  try {
    if (Sr(e))
      return e;
    if (t && !kl(e))
      return;
    if (typeof e == "string") {
      let r = e.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function zl(e, t) {
  return ue(() => Al(e, t), [e, t]);
}
function Dl(e, t) {
  return t((n, o) => Sr(n) ? o ? (...i) => he(o) && o.unshift ? n(...e, ...i) : n(...i, ...e) : n(...e) : n);
}
const Hl = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Bl(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const n = e[r];
    return t[r] = Wl(r, n), t;
  }, {}) : {};
}
function Wl(e, t) {
  return typeof t == "number" && !Hl.includes(e) ? t + "px" : t;
}
function br(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const o = u.Children.toArray(e._reactElement.props.children).map((i) => {
      if (u.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = br(i.props.el);
        return u.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...u.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(bt(u.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: s,
      type: a,
      useCapture: l
    }) => {
      r.addEventListener(a, s, l);
    });
  });
  const n = Array.from(e.childNodes);
  for (let o = 0; o < n.length; o++) {
    const i = n[o];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = br(i);
      t.push(...a), r.appendChild(s);
    } else i.nodeType === 3 && r.appendChild(i.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function Vl(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Ln = Do(({
  slot: e,
  clone: t,
  className: r,
  style: n,
  observeAttributes: o
}, i) => {
  const s = re(), [a, l] = Ye([]), {
    forceClone: c
  } = bi(), d = c ? !0 : t;
  return _e(() => {
    var h;
    if (!s.current || !e)
      return;
    let m = e;
    function f() {
      let g = m;
      if (m.tagName.toLowerCase() === "svelte-slot" && m.children.length === 1 && m.children[0] && (g = m.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), Vl(i, g), r && g.classList.add(...r.split(" ")), n) {
        const x = Bl(n);
        Object.keys(x).forEach((_) => {
          g.style[_] = x[_];
        });
      }
    }
    let p = null, y = null;
    if (d && window.MutationObserver) {
      let g = function() {
        var $, I, v;
        ($ = s.current) != null && $.contains(m) && ((I = s.current) == null || I.removeChild(m));
        const {
          portals: _,
          clonedElement: w
        } = br(e);
        m = w, l(_), m.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          f();
        }, 50), (v = s.current) == null || v.appendChild(m);
      };
      g();
      const x = ji(() => {
        g(), p == null || p.disconnect(), p == null || p.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      p = new window.MutationObserver(x), p.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      m.style.display = "contents", f(), (h = s.current) == null || h.appendChild(m);
    return () => {
      var g, x;
      m.style.display = "", (g = s.current) != null && g.contains(m) && ((x = s.current) == null || x.removeChild(m)), p == null || p.disconnect();
    };
  }, [e, d, r, n, i, o, c]), u.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Xl = ({
  children: e,
  ...t
}) => /* @__PURE__ */ S.jsx(S.Fragment, {
  children: e(t)
});
function Ul(e) {
  return u.createElement(Xl, {
    children: e
  });
}
function Mo(e, t, r) {
  const n = e.filter(Boolean);
  if (n.length !== 0)
    return n.map((o, i) => {
      var c, d;
      if (typeof o != "object")
        return t != null && t.fallback ? t.fallback(o) : o;
      const s = t != null && t.itemPropsTransformer ? t == null ? void 0 : t.itemPropsTransformer({
        ...o.props,
        key: ((c = o.props) == null ? void 0 : c.key) ?? (r ? `${r}-${i}` : `${i}`)
      }) : {
        ...o.props,
        key: ((d = o.props) == null ? void 0 : d.key) ?? (r ? `${r}-${i}` : `${i}`)
      };
      let a = s;
      Object.keys(o.slots).forEach((m) => {
        if (!o.slots[m] || !(o.slots[m] instanceof Element) && !o.slots[m].el)
          return;
        const f = m.split(".");
        f.forEach((_, w) => {
          a[_] || (a[_] = {}), w !== f.length - 1 && (a = s[_]);
        });
        const p = o.slots[m];
        let y, h, g = (t == null ? void 0 : t.clone) ?? !1, x = t == null ? void 0 : t.forceClone;
        p instanceof Element ? y = p : (y = p.el, h = p.callback, g = p.clone ?? g, x = p.forceClone ?? x), x = x ?? !!h, a[f[f.length - 1]] = y ? h ? (..._) => (h(f[f.length - 1], _), /* @__PURE__ */ S.jsx(Dr, {
          ...o.ctx,
          params: _,
          forceClone: x,
          children: /* @__PURE__ */ S.jsx(Ln, {
            slot: y,
            clone: g
          })
        })) : Ul((_) => /* @__PURE__ */ S.jsx(Dr, {
          ...o.ctx,
          forceClone: x,
          children: /* @__PURE__ */ S.jsx(Ln, {
            ..._,
            slot: y,
            clone: g
          })
        })) : a[f[f.length - 1]], a = s;
      });
      const l = (t == null ? void 0 : t.children) || "children";
      return o[l] ? s[l] = Mo(o[l], t, `${i}`) : t != null && t.children && (s[l] = void 0, Reflect.deleteProperty(s, l)), s;
    });
}
const Lo = Symbol();
function Gl(e, t) {
  return Dl(t, (r) => {
    var n, o;
    return {
      ...e,
      avatar: Sr(e.avatar) ? r(e.avatar) : he(e.avatar) ? {
        ...e.avatar,
        icon: r((n = e.avatar) == null ? void 0 : n.icon),
        src: r((o = e.avatar) == null ? void 0 : o.src)
      } : e.avatar,
      footer: r(e.footer, {
        unshift: !0
      }),
      header: r(e.header, {
        unshift: !0
      }),
      loadingRender: r(e.loadingRender, !0),
      messageRender: r(e.messageRender, !0)
    };
  });
}
function Kl({
  roles: e,
  preProcess: t,
  postProcess: r
}, n = []) {
  const o = zl(e), i = ne(t), s = ne(r), {
    items: {
      roles: a
    }
  } = Nl(), l = ue(() => {
    var d;
    return e || ((d = Mo(a, {
      clone: !0,
      forceClone: !0
    })) == null ? void 0 : d.reduce((m, f) => (f.role !== void 0 && (m[f.role] = f), m), {}));
  }, [a, e]), c = ue(() => (d, m) => {
    const f = m ?? d[Lo], p = i(d, f) || d;
    if (p.role && (l || {})[p.role])
      return Gl((l || {})[p.role], [p, f]);
    let y;
    return y = s(p, f), y || {
      messageRender(h) {
        return /* @__PURE__ */ S.jsx(S.Fragment, {
          children: he(h) ? JSON.stringify(h) : h
        });
      }
    };
  }, [l, s, i, ...n]);
  return o || c;
}
function ql(e) {
  const [t, r] = Ye(!1), n = re(0), o = re(!0), i = re(!0), {
    autoScroll: s,
    scrollButtonOffset: a,
    ref: l,
    value: c
  } = e, d = ne((f = "instant") => {
    l.current && (i.current = !0, requestAnimationFrame(() => {
      var p;
      (p = l.current) == null || p.scrollTo({
        offset: l.current.nativeElement.scrollHeight,
        behavior: f
      });
    }), r(!1));
  }), m = ne((f = 100) => {
    if (!l.current)
      return !1;
    const p = l.current.nativeElement, y = p.scrollHeight, {
      scrollTop: h,
      clientHeight: g
    } = p;
    return y - (h + g) < f;
  });
  return _e(() => {
    l.current && s && (c.length !== n.current && (o.current = !0), o.current && requestAnimationFrame(() => {
      d();
    }), n.current = c.length);
  }, [c, l, s, d, m]), _e(() => {
    if (l.current && s) {
      const f = l.current.nativeElement;
      let p = 0, y = 0;
      const h = (g) => {
        const x = g.target;
        i.current ? i.current = !1 : x.scrollTop < p && x.scrollHeight >= y ? o.current = !1 : m() && (o.current = !0), p = x.scrollTop, y = x.scrollHeight, r(!m(a));
      };
      return f.addEventListener("scroll", h), () => {
        f.removeEventListener("scroll", h);
      };
    }
  }, [s, m, a]), {
    showScrollButton: t,
    scrollToBottom: d
  };
}
new Intl.Collator(0, {
  numeric: 1
}).compare;
typeof process < "u" && process.versions && process.versions.node;
var we;
class Cc extends TransformStream {
  /** Constructs a new instance. */
  constructor(r = {
    allowCR: !1
  }) {
    super({
      transform: (n, o) => {
        for (n = De(this, we) + n; ; ) {
          const i = n.indexOf(`
`), s = r.allowCR ? n.indexOf("\r") : -1;
          if (s !== -1 && s !== n.length - 1 && (i === -1 || i - 1 > s)) {
            o.enqueue(n.slice(0, s)), n = n.slice(s + 1);
            continue;
          }
          if (i === -1) break;
          const a = n[i - 1] === "\r" ? i - 1 : i;
          o.enqueue(n.slice(0, a)), n = n.slice(i + 1);
        }
        kr(this, we, n);
      },
      flush: (n) => {
        if (De(this, we) === "") return;
        const o = r.allowCR && De(this, we).endsWith("\r") ? De(this, we).slice(0, -1) : De(this, we);
        n.enqueue(o);
      }
    });
    Fr(this, we, "");
  }
}
we = new WeakMap();
function Yl(e) {
  try {
    const t = new URL(e);
    return t.protocol === "http:" || t.protocol === "https:";
  } catch {
    return !1;
  }
}
function Zl() {
  const e = document.querySelector(".gradio-container");
  if (!e)
    return "";
  const t = e.className.match(/gradio-container-(.+)/);
  return t ? t[1] : "";
}
const Ql = +Zl()[0];
function rt(e, t, r) {
  const n = Ql >= 5 ? "gradio_api/" : "";
  return e == null ? r ? `/proxy=${r}${n}file=` : `${t}${n}file=` : Yl(e) ? e : r ? `/proxy=${r}${n}file=${e}` : `${t}/${n}file=${e}`;
}
const Jl = (e) => !!e.url;
function Oo(e, t, r) {
  if (e)
    return Jl(e) ? e.url : typeof e == "string" ? e.startsWith("http") ? e : rt(e, t, r) : e;
}
const ec = ({
  options: e,
  urlProxyUrl: t,
  urlRoot: r,
  onWelcomePromptSelect: n
}) => {
  var a;
  const {
    prompts: o,
    ...i
  } = e, s = ue(() => ve(o || {}, {
    omitNull: !0
  }), [o]);
  return /* @__PURE__ */ S.jsxs(Ee, {
    vertical: !0,
    gap: "middle",
    children: [/* @__PURE__ */ S.jsx(_l, {
      ...i,
      icon: Oo(i.icon, r, t),
      styles: {
        ...i == null ? void 0 : i.styles,
        icon: {
          flexShrink: 0,
          ...(a = i == null ? void 0 : i.styles) == null ? void 0 : a.icon
        }
      },
      classNames: i.class_names,
      className: O(i.elem_classes),
      style: i.elem_style
    }), /* @__PURE__ */ S.jsx(Tr, {
      ...s,
      classNames: s == null ? void 0 : s.class_names,
      className: O(s == null ? void 0 : s.elem_classes),
      style: s == null ? void 0 : s.elem_style,
      onItemClick: ({
        data: l
      }) => {
        n({
          value: l
        });
      }
    })]
  });
}, On = Symbol(), jn = Symbol(), Nn = Symbol(), Fn = Symbol(), tc = (e) => e ? typeof e == "string" ? {
  src: e
} : ((r) => !!r.url)(e) ? {
  src: e.url
} : e.src ? {
  ...e,
  src: typeof e.src == "string" ? e.src : e.src.url
} : e : void 0, rc = (e) => typeof e == "string" ? [{
  type: "text",
  content: e
}] : Array.isArray(e) ? e.map((t) => typeof t == "string" ? {
  type: "text",
  content: t
} : t) : he(e) ? [e] : [], nc = (e, t) => {
  if (typeof e == "string")
    return t[0];
  if (Array.isArray(e)) {
    const r = [...e];
    return Object.keys(t).forEach((n) => {
      const o = r[n];
      typeof o == "string" ? r[n] = t[n] : r[n] = {
        ...o,
        content: t[n]
      };
    }), r;
  }
  return he(e) ? {
    ...e,
    content: t[0]
  } : e;
}, jo = (e, t, r) => typeof e == "string" ? e : Array.isArray(e) ? e.map((n) => jo(n, t, r)).filter(Boolean).join(`
`) : he(e) ? e.copyable ?? !0 ? typeof e.content == "string" ? e.content : e.type === "file" ? JSON.stringify(e.content.map((n) => Oo(n, t, r))) : JSON.stringify(e.content) : "" : JSON.stringify(e), No = (e, t) => (e || []).map((r) => ({
  ...t(r),
  children: Array.isArray(r.children) ? No(r.children, t) : void 0
})), oc = ({
  content: e,
  className: t,
  style: r,
  disabled: n,
  urlRoot: o,
  urlProxyUrl: i,
  onCopy: s
}) => {
  const a = ue(() => jo(e, o, i), [e, i, o]), l = re(null);
  return /* @__PURE__ */ S.jsx(Te.Text, {
    copyable: {
      tooltips: !1,
      onCopy() {
        s == null || s(a);
      },
      text: a,
      icon: [/* @__PURE__ */ S.jsx(ie, {
        ref: l,
        variant: "text",
        color: "default",
        disabled: n,
        size: "small",
        className: t,
        style: r,
        icon: /* @__PURE__ */ S.jsx(li, {})
      }, "copy"), /* @__PURE__ */ S.jsx(ie, {
        variant: "text",
        color: "default",
        size: "small",
        disabled: n,
        className: t,
        style: r,
        icon: /* @__PURE__ */ S.jsx(zn, {})
      }, "copied")]
    }
  });
}, ic = ({
  action: e,
  disabledActions: t,
  message: r,
  onCopy: n,
  onDelete: o,
  onEdit: i,
  onLike: s,
  onRetry: a,
  urlRoot: l,
  urlProxyUrl: c
}) => {
  var x;
  const d = re(), m = () => he(e) ? {
    action: e.action,
    disabled: (t == null ? void 0 : t.includes(e.action)) || !!e.disabled,
    disableHandler: !!e.popconfirm
  } : {
    action: e,
    disabled: (t == null ? void 0 : t.includes(e)) || !1,
    disableHandler: !1
  }, {
    action: f,
    disabled: p,
    disableHandler: y
  } = m(), g = (() => {
    var _, w;
    switch (f) {
      case "copy":
        return /* @__PURE__ */ S.jsx(oc, {
          disabled: p,
          content: r.content,
          onCopy: n,
          urlRoot: l,
          urlProxyUrl: c
        });
      case "like":
        return d.current = () => s(!0), /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: ((_ = r.meta) == null ? void 0 : _.feedback) === "like" ? "primary" : "default",
          disabled: p,
          size: "small",
          icon: /* @__PURE__ */ S.jsx(ai, {}),
          onClick: () => {
            !y && s(!0);
          }
        });
      case "dislike":
        return d.current = () => s(!1), /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: ((w = r.meta) == null ? void 0 : w.feedback) === "dislike" ? "primary" : "default",
          size: "small",
          icon: /* @__PURE__ */ S.jsx(si, {}),
          disabled: p,
          onClick: () => !y && s(!1)
        });
      case "retry":
        return d.current = a, /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: "default",
          size: "small",
          disabled: p,
          icon: /* @__PURE__ */ S.jsx(ii, {}),
          onClick: () => !y && a()
        });
      case "edit":
        return d.current = i, /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: "default",
          size: "small",
          disabled: p,
          icon: /* @__PURE__ */ S.jsx(oi, {}),
          onClick: () => !y && i()
        });
      case "delete":
        return d.current = o, /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: "default",
          size: "small",
          disabled: p,
          icon: /* @__PURE__ */ S.jsx(ni, {}),
          onClick: () => !y && o()
        });
      default:
        return null;
    }
  })();
  if (he(e)) {
    const _ = {
      ...typeof e.popconfirm == "string" ? {
        title: e.popconfirm
      } : {
        ...e.popconfirm,
        title: (x = e.popconfirm) == null ? void 0 : x.title
      },
      disabled: p,
      onConfirm() {
        var w;
        (w = d.current) == null || w.call(d);
      }
    };
    return u.createElement(e.popconfirm ? gi : u.Fragment, e.popconfirm ? _ : void 0, u.createElement(e.tooltip ? hi : u.Fragment, e.tooltip ? typeof e.tooltip == "string" ? {
      title: e.tooltip
    } : e.tooltip : void 0, g));
  }
  return g;
}, sc = ({
  isEditing: e,
  onEditCancel: t,
  onEditConfirm: r,
  onCopy: n,
  onEdit: o,
  onLike: i,
  onDelete: s,
  onRetry: a,
  editValues: l,
  message: c,
  extra: d,
  index: m,
  actions: f,
  disabledActions: p,
  urlRoot: y,
  urlProxyUrl: h
}) => e ? /* @__PURE__ */ S.jsxs(Ee, {
  justify: "end",
  children: [/* @__PURE__ */ S.jsx(ie, {
    variant: "text",
    color: "default",
    size: "small",
    icon: /* @__PURE__ */ S.jsx(ri, {}),
    onClick: () => {
      t == null || t();
    }
  }), /* @__PURE__ */ S.jsx(ie, {
    variant: "text",
    color: "default",
    size: "small",
    icon: /* @__PURE__ */ S.jsx(zn, {}),
    onClick: () => {
      const g = nc(c.content, l);
      r == null || r({
        index: m,
        value: g,
        previous_value: c.content
      });
    }
  })]
}) : /* @__PURE__ */ S.jsx(Ee, {
  justify: "space-between",
  align: "center",
  gap: d && (f != null && f.length) ? "small" : void 0,
  children: (c.role === "user" ? ["extra", "actions"] : ["actions", "extra"]).map((g) => {
    switch (g) {
      case "extra":
        return /* @__PURE__ */ S.jsx(Te.Text, {
          type: "secondary",
          children: d
        }, "extra");
      case "actions":
        return /* @__PURE__ */ S.jsx("div", {
          children: (f || []).map((x, _) => /* @__PURE__ */ S.jsx(ic, {
            urlRoot: y,
            urlProxyUrl: h,
            action: x,
            disabledActions: p,
            message: c,
            onCopy: (w) => n({
              value: w,
              index: m
            }),
            onDelete: () => s({
              index: m,
              value: c.content
            }),
            onEdit: () => o(m),
            onLike: (w) => i == null ? void 0 : i({
              value: c.content,
              liked: w,
              index: m
            }),
            onRetry: () => a == null ? void 0 : a({
              index: m,
              value: c.content
            })
          }, `${x}-${_}`))
        }, "actions");
    }
  })
}), ac = ({
  markdownConfig: e,
  title: t
}) => t ? e.renderMarkdown ? /* @__PURE__ */ S.jsx(St, {
  ...e,
  value: t
}) : /* @__PURE__ */ S.jsx(S.Fragment, {
  children: t
}) : null, lc = ({
  item: e,
  urlRoot: t,
  urlProxyUrl: r,
  ...n
}) => {
  const o = ue(() => e ? typeof e == "string" ? {
    url: e.startsWith("http") ? e : rt(e, t, r),
    uid: e,
    name: e.split("/").pop()
  } : {
    ...e,
    uid: e.uid || e.path || e.url,
    name: e.name || e.orig_name || (e.url || e.path).split("/").pop(),
    url: e.url || rt(e.path, t, r)
  } : {}, [e, r, t]);
  return /* @__PURE__ */ S.jsx(wo.FileCard, {
    ...n,
    imageProps: {
      ...n.imageProps
      // fixed in @ant-design/x@1.2.0
      // wrapperStyle: {
      //   width: '100%',
      //   height: '100%',
      //   ...props.imageProps?.wrapperStyle,
      // },
      // style: {
      //   width: '100%',
      //   height: '100%',
      //   objectFit: 'contain',
      //   borderRadius: token.borderRadius,
      //   ...props.imageProps?.style,
      // },
    },
    item: o
  });
}, cc = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"];
function uc(e, t) {
  return t.some((r) => e.toLowerCase() === `.${r}`);
}
const fc = (e, t, r) => e ? typeof e == "string" ? {
  url: e.startsWith("http") ? e : rt(e, t, r),
  uid: e,
  name: e.split("/").pop()
} : {
  ...e,
  uid: e.uid || e.path || e.url,
  name: e.name || e.orig_name || (e.url || e.path).split("/").pop(),
  url: e.url || rt(e.path, t, r)
} : {}, dc = ({
  children: e,
  item: t
}) => {
  const {
    token: r
  } = Ze.useToken(), n = ue(() => {
    const o = t.name || "", i = o.match(/^(.*)\.[^.]+$/), s = i ? o.slice(i[1].length) : "";
    return uc(s, cc);
  }, [t.name]);
  return /* @__PURE__ */ S.jsx("div", {
    className: "ms-gr-pro-chatbot-message-file-message-container",
    style: {
      borderRadius: r.borderRadius
    },
    children: n ? /* @__PURE__ */ S.jsxs(S.Fragment, {
      children: [" ", e]
    }) : /* @__PURE__ */ S.jsxs(S.Fragment, {
      children: [e, /* @__PURE__ */ S.jsx("div", {
        className: "ms-gr-pro-chatbot-message-file-message-toolbar",
        style: {
          backgroundColor: r.colorBgMask,
          zIndex: r.zIndexPopupBase,
          borderRadius: r.borderRadius
        },
        children: /* @__PURE__ */ S.jsx(ie, {
          icon: /* @__PURE__ */ S.jsx(ci, {
            style: {
              color: r.colorWhite
            }
          }),
          variant: "link",
          color: "default",
          size: "small",
          href: t.url,
          target: "_blank",
          rel: "noopener noreferrer"
        })
      })]
    })
  });
}, mc = ({
  value: e,
  urlProxyUrl: t,
  urlRoot: r,
  options: n
}) => {
  const {
    imageProps: o
  } = n;
  return /* @__PURE__ */ S.jsx(Ee, {
    gap: "small",
    wrap: !0,
    ...n,
    className: "ms-gr-pro-chatbot-message-file-message",
    children: e == null ? void 0 : e.map((i, s) => {
      const a = fc(i, r, t);
      return /* @__PURE__ */ S.jsx(dc, {
        item: a,
        children: /* @__PURE__ */ S.jsx(lc, {
          item: a,
          urlRoot: r,
          urlProxyUrl: t,
          imageProps: o
        })
      }, `${a.uid}-${s}`);
    })
  });
}, pc = ({
  value: e,
  options: t,
  onItemClick: r
}) => {
  const {
    elem_style: n,
    elem_classes: o,
    class_names: i,
    styles: s,
    ...a
  } = t;
  return /* @__PURE__ */ S.jsx(Tr, {
    ...a,
    classNames: i,
    className: O(o),
    style: n,
    styles: s,
    items: e,
    onItemClick: ({
      data: l
    }) => {
      r(l);
    }
  });
}, kn = ({
  value: e,
  options: t
}) => {
  const {
    renderMarkdown: r,
    ...n
  } = t;
  return /* @__PURE__ */ S.jsx(S.Fragment, {
    children: r ? /* @__PURE__ */ S.jsx(St, {
      ...n,
      value: e
    }) : e
  });
}, gc = ({
  value: e,
  options: t
}) => {
  const {
    renderMarkdown: r,
    status: n,
    title: o,
    ...i
  } = t, [s, a] = Ye(() => n !== "done");
  return _e(() => {
    a(n !== "done");
  }, [n]), /* @__PURE__ */ S.jsx(S.Fragment, {
    children: /* @__PURE__ */ S.jsx(yi, {
      activeKey: s ? ["tool"] : [],
      onChange: () => {
        a(!s);
      },
      items: [{
        key: "tool",
        label: r ? /* @__PURE__ */ S.jsx(St, {
          ...i,
          value: o
        }) : o,
        children: r ? /* @__PURE__ */ S.jsx(St, {
          ...i,
          value: e
        }) : e
      }]
    })
  });
}, hc = ["text", "tool"], yc = ({
  isEditing: e,
  index: t,
  message: r,
  isLastMessage: n,
  markdownConfig: o,
  onEdit: i,
  onSuggestionSelect: s,
  urlProxyUrl: a,
  urlRoot: l
}) => {
  const c = re(null), d = () => rc(r.content).map((f, p) => {
    const y = () => {
      var h;
      if (e && (f.editable ?? !0) && hc.includes(f.type)) {
        const g = f.content, x = (h = c.current) == null ? void 0 : h.getBoundingClientRect().width;
        return /* @__PURE__ */ S.jsx("div", {
          style: {
            width: x,
            minWidth: 200,
            maxWidth: "100%"
          },
          children: /* @__PURE__ */ S.jsx(vi.TextArea, {
            autoSize: {
              minRows: 1,
              maxRows: 10
            },
            defaultValue: g,
            onChange: (_) => {
              i(p, _.target.value);
            }
          })
        });
      }
      switch (f.type) {
        case "text":
          return /* @__PURE__ */ S.jsx(kn, {
            value: f.content,
            options: ve({
              ...o,
              ...gt(f.options)
            }, {
              omitNull: !0
            })
          });
        case "tool":
          return /* @__PURE__ */ S.jsx(gc, {
            value: f.content,
            options: ve({
              ...o,
              ...gt(f.options)
            }, {
              omitNull: !0
            })
          });
        case "file":
          return /* @__PURE__ */ S.jsx(mc, {
            value: f.content,
            urlRoot: l,
            urlProxyUrl: a,
            options: ve(f.options || {}, {
              omitNull: !0
            })
          });
        case "suggestion":
          return /* @__PURE__ */ S.jsx(pc, {
            value: n ? f.content : No(f.content, (g) => ({
              ...g,
              disabled: g.disabled ?? !0
            })),
            options: ve(f.options || {}, {
              omitNull: !0
            }),
            onItemClick: (g) => {
              s({
                index: t,
                value: g
              });
            }
          });
        default:
          return typeof f.content != "string" ? null : /* @__PURE__ */ S.jsx(kn, {
            value: f.content,
            options: ve({
              ...o,
              ...gt(f.options)
            }, {
              omitNull: !0
            })
          });
      }
    };
    return /* @__PURE__ */ S.jsx(u.Fragment, {
      children: y()
    }, p);
  });
  return /* @__PURE__ */ S.jsx("div", {
    ref: c,
    children: /* @__PURE__ */ S.jsx(Ee, {
      vertical: !0,
      gap: "small",
      children: d()
    })
  });
}, Tc = as(Fl(["roles"], ({
  id: e,
  className: t,
  style: r,
  height: n,
  minHeight: o,
  maxHeight: i,
  value: s,
  roles: a,
  urlRoot: l,
  urlProxyUrl: c,
  themeMode: d,
  autoScroll: m = !0,
  showScrollToBottomButton: f = !0,
  scrollToBottomButtonOffset: p = 200,
  markdownConfig: y,
  welcomeConfig: h,
  userConfig: g,
  botConfig: x,
  onValueChange: _,
  onCopy: w,
  onChange: $,
  onEdit: I,
  onRetry: v,
  onDelete: R,
  onLike: P,
  onSuggestionSelect: j,
  onWelcomePromptSelect: T
}) => {
  const L = ue(() => ({
    variant: "borderless",
    ...h ? ve(h, {
      omitNull: !0
    }) : {}
  }), [h]), N = ue(() => ({
    lineBreaks: !0,
    renderMarkdown: !0,
    ...gt(y),
    urlRoot: l,
    themeMode: d
  }), [y, d, l]), b = ue(() => g ? ve(g, {
    omitNull: !0
  }) : {}, [g]), E = ue(() => x ? ve(x, {
    omitNull: !0
  }) : {}, [x]), F = ue(() => {
    const C = (s || []).map((K, X) => {
      const me = X === s.length - 1, ce = ve(K, {
        omitNull: !0
      });
      return {
        ...zr(ce, ["header", "footer", "avatar"]),
        [Lo]: X,
        [On]: ce.header,
        [jn]: ce.footer,
        [Nn]: ce.avatar,
        [Fn]: me,
        key: ce.key ?? `${X}`
      };
    }).filter((K) => K.role !== "system");
    return C.length > 0 ? C : [{
      role: "chatbot-internal-welcome"
    }];
  }, [s]), D = re(null), [B, z] = Ye(-1), [W, oe] = Ye({}), G = re(), J = ne((C, K) => {
    oe((X) => ({
      ...X,
      [C]: K
    }));
  }), U = ne($);
  _e(() => {
    Ni(G.current, s) || (U(), G.current = s);
  }, [s, U]);
  const V = ne((C) => {
    j == null || j(C);
  }), q = ne((C) => {
    T == null || T(C);
  }), ee = ne((C) => {
    v == null || v(C);
  }), Z = ne((C) => {
    z(C);
  }), Se = ne(() => {
    z(-1);
  }), Fe = ne((C) => {
    z(-1), _([...s.slice(0, C.index), {
      ...s[C.index],
      content: C.value
    }, ...s.slice(C.index + 1)]), I == null || I(C);
  }), ke = ne((C) => {
    w == null || w(C);
  }), Ae = ne((C) => {
    P == null || P(C), _(Mn(s, (K) => {
      const X = K[C.index].meta || {}, me = C.liked ? "like" : "dislike";
      K[C.index] = {
        ...K[C.index],
        meta: {
          ...X,
          feedback: X.feedback === me ? null : me
        }
      };
    }));
  }), xe = ne((C) => {
    _(Mn(s, (K) => {
      K.splice(C.index, 1);
    })), R == null || R(C);
  }), ze = Kl({
    roles: a,
    preProcess(C, K) {
      var me, ce, te, Y, ae, Pe, Re, Pr, Rr, Mr, Lr, Or;
      const X = C.role === "user";
      return {
        ...C,
        style: C.elem_style,
        className: O(C.elem_classes, "ms-gr-pro-chatbot-message"),
        classNames: {
          ...C.class_names,
          avatar: O(X ? (me = b == null ? void 0 : b.class_names) == null ? void 0 : me.avatar : (ce = E == null ? void 0 : E.class_names) == null ? void 0 : ce.avatar, (te = C.class_names) == null ? void 0 : te.avatar, "ms-gr-pro-chatbot-message-avatar"),
          header: O(X ? (Y = b == null ? void 0 : b.class_names) == null ? void 0 : Y.header : (ae = E == null ? void 0 : E.class_names) == null ? void 0 : ae.header, (Pe = C.class_names) == null ? void 0 : Pe.header, "ms-gr-pro-chatbot-message-header"),
          footer: O(X ? (Re = b == null ? void 0 : b.class_names) == null ? void 0 : Re.footer : (Pr = E == null ? void 0 : E.class_names) == null ? void 0 : Pr.footer, (Rr = C.class_names) == null ? void 0 : Rr.footer, "ms-gr-pro-chatbot-message-footer", K === B ? "ms-gr-pro-chatbot-message-footer-editing" : void 0),
          content: O(X ? (Mr = b == null ? void 0 : b.class_names) == null ? void 0 : Mr.content : (Lr = E == null ? void 0 : E.class_names) == null ? void 0 : Lr.content, (Or = C.class_names) == null ? void 0 : Or.content, "ms-gr-pro-chatbot-message-content")
        }
      };
    },
    postProcess(C, K) {
      const X = C.role === "user";
      switch (C.role) {
        case "chatbot-internal-welcome":
          return {
            variant: "borderless",
            styles: {
              content: {
                width: "100%"
              }
            },
            messageRender() {
              return /* @__PURE__ */ S.jsx(ec, {
                urlRoot: l,
                urlProxyUrl: c,
                options: L || {},
                onWelcomePromptSelect: q
              });
            }
          };
        case "user":
        case "assistant":
          return {
            ...zr(X ? b : E, ["actions", "avatar", "header"]),
            ...C,
            style: {
              ...X ? b == null ? void 0 : b.style : E == null ? void 0 : E.style,
              ...C.style
            },
            className: O(C.className, X ? b == null ? void 0 : b.elem_classes : E == null ? void 0 : E.elem_classes),
            header: /* @__PURE__ */ S.jsx(ac, {
              title: C[On] ?? (X ? b == null ? void 0 : b.header : E == null ? void 0 : E.header),
              markdownConfig: N
            }),
            avatar: tc(C[Nn] ?? (X ? b == null ? void 0 : b.avatar : E == null ? void 0 : E.avatar)),
            footer: (
              // bubbleProps[lastMessageSymbol] &&
              C.loading || C.status === "pending" ? null : /* @__PURE__ */ S.jsx(sc, {
                isEditing: B === K,
                message: C,
                extra: C[jn] ?? (X ? b == null ? void 0 : b.footer : E == null ? void 0 : E.footer),
                urlRoot: l,
                urlProxyUrl: c,
                editValues: W,
                index: K,
                actions: C.actions ?? (X ? (b == null ? void 0 : b.actions) || [] : (E == null ? void 0 : E.actions) || []),
                disabledActions: C.disabled_actions ?? (X ? (b == null ? void 0 : b.disabled_actions) || [] : (E == null ? void 0 : E.disabled_actions) || []),
                onEditCancel: Se,
                onEditConfirm: Fe,
                onCopy: ke,
                onEdit: Z,
                onDelete: xe,
                onRetry: ee,
                onLike: Ae
              })
            ),
            messageRender() {
              return /* @__PURE__ */ S.jsx(yc, {
                index: K,
                urlProxyUrl: c,
                urlRoot: l,
                isEditing: B === K,
                message: C,
                isLastMessage: C[Fn] || !1,
                markdownConfig: N,
                onEdit: J,
                onSuggestionSelect: V
              });
            }
          };
        default:
          return;
      }
    }
  }, [B, b, L, E, N, W]), {
    scrollToBottom: it,
    showScrollButton: Xt
  } = ql({
    ref: D,
    value: s,
    autoScroll: m,
    scrollButtonOffset: p
  });
  return /* @__PURE__ */ S.jsxs("div", {
    id: e,
    className: O(t, "ms-gr-pro-chatbot"),
    style: {
      height: n,
      minHeight: o,
      maxHeight: i,
      ...r
    },
    children: [/* @__PURE__ */ S.jsx(Cr.List, {
      ref: D,
      className: "ms-gr-pro-chatbot-messages",
      autoScroll: !1,
      roles: ze,
      items: F
    }), f && Xt && /* @__PURE__ */ S.jsx("div", {
      className: "ms-gr-pro-chatbot-scroll-to-bottom-button",
      children: /* @__PURE__ */ S.jsx(ie, {
        icon: /* @__PURE__ */ S.jsx(ui, {}),
        shape: "circle",
        variant: "outlined",
        color: "primary",
        onClick: () => it("smooth")
      })
    })]
  });
}));
export {
  Tc as Chatbot,
  Tc as default
};
