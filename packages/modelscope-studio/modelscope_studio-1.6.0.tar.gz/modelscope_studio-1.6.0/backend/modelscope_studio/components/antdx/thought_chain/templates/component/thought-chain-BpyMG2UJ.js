import { i as nn, a as gt, r as on, Z as Ae, g as sn, c as G } from "./Index-DCKtMKdK.js";
const R = window.ms_globals.React, x = window.ms_globals.React, Yr = window.ms_globals.React.isValidElement, Zr = window.ms_globals.React.version, ee = window.ms_globals.React.useRef, Jr = window.ms_globals.React.useLayoutEffect, ge = window.ms_globals.React.useEffect, en = window.ms_globals.React.forwardRef, tn = window.ms_globals.React.useState, rn = window.ms_globals.React.useMemo, jt = window.ms_globals.ReactDOM, pt = window.ms_globals.ReactDOM.createPortal, an = window.ms_globals.internalContext.useContextPropsContext, zt = window.ms_globals.internalContext.ContextPropsProvider, cn = window.ms_globals.createItemsContext.createItemsContext, ln = window.ms_globals.antd.ConfigProvider, vt = window.ms_globals.antd.theme, un = window.ms_globals.antd.Avatar, fn = window.ms_globals.antd.Tooltip, dn = window.ms_globals.antd.Typography, ze = window.ms_globals.antdCssinjs.unit, rt = window.ms_globals.antdCssinjs.token2CSSVar, Dt = window.ms_globals.antdCssinjs.useStyleRegister, mn = window.ms_globals.antdCssinjs.useCSSVarRegister, hn = window.ms_globals.antdCssinjs.createTheme, pn = window.ms_globals.antdCssinjs.useCacheToken, gn = window.ms_globals.antdIcons.LeftOutlined, vn = window.ms_globals.antdIcons.RightOutlined;
var yn = /\s/;
function bn(e) {
  for (var t = e.length; t-- && yn.test(e.charAt(t)); )
    ;
  return t;
}
var Sn = /^\s+/;
function xn(e) {
  return e && e.slice(0, bn(e) + 1).replace(Sn, "");
}
var kt = NaN, Cn = /^[-+]0x[0-9a-f]+$/i, En = /^0b[01]+$/i, _n = /^0o[0-7]+$/i, wn = parseInt;
function Nt(e) {
  if (typeof e == "number")
    return e;
  if (nn(e))
    return kt;
  if (gt(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = gt(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = xn(e);
  var r = En.test(e);
  return r || _n.test(e) ? wn(e.slice(2), r ? 2 : 8) : Cn.test(e) ? kt : +e;
}
var nt = function() {
  return on.Date.now();
}, Tn = "Expected a function", Pn = Math.max, On = Math.min;
function Mn(e, t, r) {
  var o, n, i, s, a, c, l = 0, f = !1, u = !1, d = !0;
  if (typeof e != "function")
    throw new TypeError(Tn);
  t = Nt(t) || 0, gt(r) && (f = !!r.leading, u = "maxWait" in r, i = u ? Pn(Nt(r.maxWait) || 0, t) : i, d = "trailing" in r ? !!r.trailing : d);
  function h(b) {
    var O = o, _ = n;
    return o = n = void 0, l = b, s = e.apply(_, O), s;
  }
  function g(b) {
    return l = b, a = setTimeout(S, t), f ? h(b) : s;
  }
  function p(b) {
    var O = b - c, _ = b - l, C = t - O;
    return u ? On(C, i - _) : C;
  }
  function m(b) {
    var O = b - c, _ = b - l;
    return c === void 0 || O >= t || O < 0 || u && _ >= i;
  }
  function S() {
    var b = nt();
    if (m(b))
      return v(b);
    a = setTimeout(S, p(b));
  }
  function v(b) {
    return a = void 0, d && o ? h(b) : (o = n = void 0, s);
  }
  function T() {
    a !== void 0 && clearTimeout(a), l = 0, o = c = n = a = void 0;
  }
  function y() {
    return a === void 0 ? s : v(nt());
  }
  function P() {
    var b = nt(), O = m(b);
    if (o = arguments, n = this, c = b, O) {
      if (a === void 0)
        return g(c);
      if (u)
        return clearTimeout(a), a = setTimeout(S, t), h(c);
    }
    return a === void 0 && (a = setTimeout(S, t)), s;
  }
  return P.cancel = T, P.flush = y, P;
}
var yr = {
  exports: {}
}, Ne = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Rn = x, Ln = Symbol.for("react.element"), $n = Symbol.for("react.fragment"), An = Object.prototype.hasOwnProperty, In = Rn.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, jn = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function br(e, t, r) {
  var o, n = {}, i = null, s = null;
  r !== void 0 && (i = "" + r), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (o in t) An.call(t, o) && !jn.hasOwnProperty(o) && (n[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) n[o] === void 0 && (n[o] = t[o]);
  return {
    $$typeof: Ln,
    type: e,
    key: i,
    ref: s,
    props: n,
    _owner: In.current
  };
}
Ne.Fragment = $n;
Ne.jsx = br;
Ne.jsxs = br;
yr.exports = Ne;
var q = yr.exports;
const {
  SvelteComponent: zn,
  assign: Ft,
  binding_callbacks: Ht,
  check_outros: Dn,
  children: Sr,
  claim_element: xr,
  claim_space: kn,
  component_subscribe: Vt,
  compute_slots: Nn,
  create_slot: Fn,
  detach: ce,
  element: Cr,
  empty: Bt,
  exclude_internal_props: Gt,
  get_all_dirty_from_scope: Hn,
  get_slot_changes: Vn,
  group_outros: Bn,
  init: Gn,
  insert_hydration: Ie,
  safe_not_equal: Un,
  set_custom_element_data: Er,
  space: Xn,
  transition_in: je,
  transition_out: yt,
  update_slot_base: Wn
} = window.__gradio__svelte__internal, {
  beforeUpdate: Kn,
  getContext: qn,
  onDestroy: Qn,
  setContext: Yn
} = window.__gradio__svelte__internal;
function Ut(e) {
  let t, r;
  const o = (
    /*#slots*/
    e[7].default
  ), n = Fn(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Cr("svelte-slot"), n && n.c(), this.h();
    },
    l(i) {
      t = xr(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = Sr(t);
      n && n.l(s), s.forEach(ce), this.h();
    },
    h() {
      Er(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      Ie(i, t, s), n && n.m(t, null), e[9](t), r = !0;
    },
    p(i, s) {
      n && n.p && (!r || s & /*$$scope*/
      64) && Wn(
        n,
        o,
        i,
        /*$$scope*/
        i[6],
        r ? Vn(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : Hn(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      r || (je(n, i), r = !0);
    },
    o(i) {
      yt(n, i), r = !1;
    },
    d(i) {
      i && ce(t), n && n.d(i), e[9](null);
    }
  };
}
function Zn(e) {
  let t, r, o, n, i = (
    /*$$slots*/
    e[4].default && Ut(e)
  );
  return {
    c() {
      t = Cr("react-portal-target"), r = Xn(), i && i.c(), o = Bt(), this.h();
    },
    l(s) {
      t = xr(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), Sr(t).forEach(ce), r = kn(s), i && i.l(s), o = Bt(), this.h();
    },
    h() {
      Er(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      Ie(s, t, a), e[8](t), Ie(s, r, a), i && i.m(s, a), Ie(s, o, a), n = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && je(i, 1)) : (i = Ut(s), i.c(), je(i, 1), i.m(o.parentNode, o)) : i && (Bn(), yt(i, 1, 1, () => {
        i = null;
      }), Dn());
    },
    i(s) {
      n || (je(i), n = !0);
    },
    o(s) {
      yt(i), n = !1;
    },
    d(s) {
      s && (ce(t), ce(r), ce(o)), e[8](null), i && i.d(s);
    }
  };
}
function Xt(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function Jn(e, t, r) {
  let o, n, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = Nn(i);
  let {
    svelteInit: c
  } = t;
  const l = Ae(Xt(t)), f = Ae();
  Vt(e, f, (y) => r(0, o = y));
  const u = Ae();
  Vt(e, u, (y) => r(1, n = y));
  const d = [], h = qn("$$ms-gr-react-wrapper"), {
    slotKey: g,
    slotIndex: p,
    subSlotIndex: m
  } = sn() || {}, S = c({
    parent: h,
    props: l,
    target: f,
    slot: u,
    slotKey: g,
    slotIndex: p,
    subSlotIndex: m,
    onDestroy(y) {
      d.push(y);
    }
  });
  Yn("$$ms-gr-react-wrapper", S), Kn(() => {
    l.set(Xt(t));
  }), Qn(() => {
    d.forEach((y) => y());
  });
  function v(y) {
    Ht[y ? "unshift" : "push"](() => {
      o = y, f.set(o);
    });
  }
  function T(y) {
    Ht[y ? "unshift" : "push"](() => {
      n = y, u.set(n);
    });
  }
  return e.$$set = (y) => {
    r(17, t = Ft(Ft({}, t), Gt(y))), "svelteInit" in y && r(5, c = y.svelteInit), "$$scope" in y && r(6, s = y.$$scope);
  }, t = Gt(t), [o, n, f, u, a, c, s, i, v, T];
}
class eo extends zn {
  constructor(t) {
    super(), Gn(this, t, Jn, Zn, Un, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Qi
} = window.__gradio__svelte__internal, Wt = window.ms_globals.rerender, ot = window.ms_globals.tree;
function to(e, t = {}) {
  function r(o) {
    const n = Ae(), i = new eo({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, c = s.parent ?? ot;
          return c.nodes = [...c.nodes, a], Wt({
            createPortal: pt,
            node: ot
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((l) => l.svelteInstance !== n), Wt({
              createPortal: pt,
              node: ot
            });
          }), a;
        },
        ...o.props
      }
    });
    return n.set(i), i;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((n) => {
      window.ms_globals.initialize = () => {
        n();
      };
    })), window.ms_globals.initializePromise.then(() => {
      o(r);
    });
  });
}
const ro = "1.6.1";
function fe() {
  return fe = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var r = arguments[t];
      for (var o in r) ({}).hasOwnProperty.call(r, o) && (e[o] = r[o]);
    }
    return e;
  }, fe.apply(null, arguments);
}
function te(e) {
  "@babel/helpers - typeof";
  return te = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, te(e);
}
function no(e, t) {
  if (te(e) != "object" || !e) return e;
  var r = e[Symbol.toPrimitive];
  if (r !== void 0) {
    var o = r.call(e, t);
    if (te(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function oo(e) {
  var t = no(e, "string");
  return te(t) == "symbol" ? t : t + "";
}
function io(e, t, r) {
  return (t = oo(t)) in e ? Object.defineProperty(e, t, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = r, e;
}
function Kt(e, t) {
  var r = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(n) {
      return Object.getOwnPropertyDescriptor(e, n).enumerable;
    })), r.push.apply(r, o);
  }
  return r;
}
function so(e) {
  for (var t = 1; t < arguments.length; t++) {
    var r = arguments[t] != null ? arguments[t] : {};
    t % 2 ? Kt(Object(r), !0).forEach(function(o) {
      io(e, o, r[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : Kt(Object(r)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(r, o));
    });
  }
  return e;
}
var ao = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, co = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, lo = "".concat(ao, " ").concat(co).split(/[\s\n]+/), uo = "aria-", fo = "data-";
function qt(e, t) {
  return e.indexOf(t) === 0;
}
function _r(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, r;
  t === !1 ? r = {
    aria: !0,
    data: !0,
    attr: !0
  } : t === !0 ? r = {
    aria: !0
  } : r = so({}, t);
  var o = {};
  return Object.keys(e).forEach(function(n) {
    // Aria
    (r.aria && (n === "role" || qt(n, uo)) || // Data
    r.data && qt(n, fo) || // Attr
    r.attr && lo.includes(n)) && (o[n] = e[n]);
  }), o;
}
const mo = /* @__PURE__ */ x.createContext({}), ho = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, po = (e) => {
  const t = x.useContext(mo);
  return x.useMemo(() => ({
    ...ho,
    ...t[e]
  }), [t[e]]);
}, go = "ant";
function bt() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: o,
    theme: n
  } = x.useContext(ln.ConfigContext);
  return {
    theme: n,
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: o
  };
}
function F(e) {
  "@babel/helpers - typeof";
  return F = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, F(e);
}
function vo(e) {
  if (Array.isArray(e)) return e;
}
function yo(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var o, n, i, s, a = [], c = !0, l = !1;
    try {
      if (i = (r = r.call(e)).next, t === 0) {
        if (Object(r) !== r) return;
        c = !1;
      } else for (; !(c = (o = i.call(r)).done) && (a.push(o.value), a.length !== t); c = !0) ;
    } catch (f) {
      l = !0, n = f;
    } finally {
      try {
        if (!c && r.return != null && (s = r.return(), Object(s) !== s)) return;
      } finally {
        if (l) throw n;
      }
    }
    return a;
  }
}
function Qt(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, o = Array(t); r < t; r++) o[r] = e[r];
  return o;
}
function bo(e, t) {
  if (e) {
    if (typeof e == "string") return Qt(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? Qt(e, t) : void 0;
  }
}
function So() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function U(e, t) {
  return vo(e) || yo(e, t) || bo(e, t) || So();
}
function xo(e, t) {
  if (F(e) != "object" || !e) return e;
  var r = e[Symbol.toPrimitive];
  if (r !== void 0) {
    var o = r.call(e, t);
    if (F(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function wr(e) {
  var t = xo(e, "string");
  return F(t) == "symbol" ? t : t + "";
}
function w(e, t, r) {
  return (t = wr(t)) in e ? Object.defineProperty(e, t, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = r, e;
}
function Yt(e, t) {
  var r = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(n) {
      return Object.getOwnPropertyDescriptor(e, n).enumerable;
    })), r.push.apply(r, o);
  }
  return r;
}
function E(e) {
  for (var t = 1; t < arguments.length; t++) {
    var r = arguments[t] != null ? arguments[t] : {};
    t % 2 ? Yt(Object(r), !0).forEach(function(o) {
      w(e, o, r[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : Yt(Object(r)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(r, o));
    });
  }
  return e;
}
function de(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function Zt(e, t) {
  for (var r = 0; r < t.length; r++) {
    var o = t[r];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, wr(o.key), o);
  }
}
function me(e, t, r) {
  return t && Zt(e.prototype, t), r && Zt(e, r), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function ae(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function St(e, t) {
  return St = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, o) {
    return r.__proto__ = o, r;
  }, St(e, t);
}
function Fe(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && St(e, t);
}
function De(e) {
  return De = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, De(e);
}
function Tr() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Tr = function() {
    return !!e;
  })();
}
function Co(e, t) {
  if (t && (F(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return ae(e);
}
function He(e) {
  var t = Tr();
  return function() {
    var r, o = De(e);
    if (t) {
      var n = De(this).constructor;
      r = Reflect.construct(o, arguments, n);
    } else r = o.apply(this, arguments);
    return Co(this, r);
  };
}
var Pr = /* @__PURE__ */ me(function e() {
  de(this, e);
}), Or = "CALC_UNIT", Eo = new RegExp(Or, "g");
function it(e) {
  return typeof e == "number" ? "".concat(e).concat(Or) : e;
}
var _o = /* @__PURE__ */ function(e) {
  Fe(r, e);
  var t = He(r);
  function r(o, n) {
    var i;
    de(this, r), i = t.call(this), w(ae(i), "result", ""), w(ae(i), "unitlessCssVar", void 0), w(ae(i), "lowPriority", void 0);
    var s = F(o);
    return i.unitlessCssVar = n, o instanceof r ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = it(o) : s === "string" && (i.result = o), i;
  }
  return me(r, [{
    key: "add",
    value: function(n) {
      return n instanceof r ? this.result = "".concat(this.result, " + ").concat(n.getResult()) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " + ").concat(it(n))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(n) {
      return n instanceof r ? this.result = "".concat(this.result, " - ").concat(n.getResult()) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " - ").concat(it(n))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(n) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), n instanceof r ? this.result = "".concat(this.result, " * ").concat(n.getResult(!0)) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " * ").concat(n)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(n) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), n instanceof r ? this.result = "".concat(this.result, " / ").concat(n.getResult(!0)) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " / ").concat(n)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(n) {
      return this.lowPriority || n ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(n) {
      var i = this, s = n || {}, a = s.unit, c = !0;
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(l) {
        return i.result.includes(l);
      }) && (c = !1), this.result = this.result.replace(Eo, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), r;
}(Pr), wo = /* @__PURE__ */ function(e) {
  Fe(r, e);
  var t = He(r);
  function r(o) {
    var n;
    return de(this, r), n = t.call(this), w(ae(n), "result", 0), o instanceof r ? n.result = o.result : typeof o == "number" && (n.result = o), n;
  }
  return me(r, [{
    key: "add",
    value: function(n) {
      return n instanceof r ? this.result += n.result : typeof n == "number" && (this.result += n), this;
    }
  }, {
    key: "sub",
    value: function(n) {
      return n instanceof r ? this.result -= n.result : typeof n == "number" && (this.result -= n), this;
    }
  }, {
    key: "mul",
    value: function(n) {
      return n instanceof r ? this.result *= n.result : typeof n == "number" && (this.result *= n), this;
    }
  }, {
    key: "div",
    value: function(n) {
      return n instanceof r ? this.result /= n.result : typeof n == "number" && (this.result /= n), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), r;
}(Pr), To = function(t, r) {
  var o = t === "css" ? _o : wo;
  return function(n) {
    return new o(n, r);
  };
}, Jt = function(t, r) {
  return "".concat([r, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function ve(e) {
  var t = R.useRef();
  t.current = e;
  var r = R.useCallback(function() {
    for (var o, n = arguments.length, i = new Array(n), s = 0; s < n; s++)
      i[s] = arguments[s];
    return (o = t.current) === null || o === void 0 ? void 0 : o.call.apply(o, [t].concat(i));
  }, []);
  return r;
}
function Po(e) {
  if (Array.isArray(e)) return e;
}
function Oo(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var o, n, i, s, a = [], c = !0, l = !1;
    try {
      if (i = (r = r.call(e)).next, t !== 0) for (; !(c = (o = i.call(r)).done) && (a.push(o.value), a.length !== t); c = !0) ;
    } catch (f) {
      l = !0, n = f;
    } finally {
      try {
        if (!c && r.return != null && (s = r.return(), Object(s) !== s)) return;
      } finally {
        if (l) throw n;
      }
    }
    return a;
  }
}
function er(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, o = Array(t); r < t; r++) o[r] = e[r];
  return o;
}
function Mo(e, t) {
  if (e) {
    if (typeof e == "string") return er(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? er(e, t) : void 0;
  }
}
function Ro() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function ke(e, t) {
  return Po(e) || Oo(e, t) || Mo(e, t) || Ro();
}
function Ve() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var tr = Ve() ? R.useLayoutEffect : R.useEffect, Lo = function(t, r) {
  var o = R.useRef(!0);
  tr(function() {
    return t(o.current);
  }, r), tr(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, rr = function(t, r) {
  Lo(function(o) {
    if (!o)
      return t();
  }, r);
};
function ye(e) {
  var t = R.useRef(!1), r = R.useState(e), o = ke(r, 2), n = o[0], i = o[1];
  R.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, c) {
    c && t.current || i(a);
  }
  return [n, s];
}
function st(e) {
  return e !== void 0;
}
function $o(e, t) {
  var r = t || {}, o = r.defaultValue, n = r.value, i = r.onChange, s = r.postState, a = ye(function() {
    return st(n) ? n : st(o) ? typeof o == "function" ? o() : o : typeof e == "function" ? e() : e;
  }), c = ke(a, 2), l = c[0], f = c[1], u = n !== void 0 ? n : l, d = s ? s(u) : u, h = ve(i), g = ye([u]), p = ke(g, 2), m = p[0], S = p[1];
  rr(function() {
    var T = m[0];
    l !== T && h(l, T);
  }, [m]), rr(function() {
    st(n) || f(n);
  }, [n]);
  var v = ve(function(T, y) {
    f(T, y), S([u], y);
  });
  return [d, v];
}
var Mr = {
  exports: {}
}, L = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ot = Symbol.for("react.element"), Mt = Symbol.for("react.portal"), Be = Symbol.for("react.fragment"), Ge = Symbol.for("react.strict_mode"), Ue = Symbol.for("react.profiler"), Xe = Symbol.for("react.provider"), We = Symbol.for("react.context"), Ao = Symbol.for("react.server_context"), Ke = Symbol.for("react.forward_ref"), qe = Symbol.for("react.suspense"), Qe = Symbol.for("react.suspense_list"), Ye = Symbol.for("react.memo"), Ze = Symbol.for("react.lazy"), Io = Symbol.for("react.offscreen"), Rr;
Rr = Symbol.for("react.module.reference");
function X(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Ot:
        switch (e = e.type, e) {
          case Be:
          case Ue:
          case Ge:
          case qe:
          case Qe:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Ao:
              case We:
              case Ke:
              case Ze:
              case Ye:
              case Xe:
                return e;
              default:
                return t;
            }
        }
      case Mt:
        return t;
    }
  }
}
L.ContextConsumer = We;
L.ContextProvider = Xe;
L.Element = Ot;
L.ForwardRef = Ke;
L.Fragment = Be;
L.Lazy = Ze;
L.Memo = Ye;
L.Portal = Mt;
L.Profiler = Ue;
L.StrictMode = Ge;
L.Suspense = qe;
L.SuspenseList = Qe;
L.isAsyncMode = function() {
  return !1;
};
L.isConcurrentMode = function() {
  return !1;
};
L.isContextConsumer = function(e) {
  return X(e) === We;
};
L.isContextProvider = function(e) {
  return X(e) === Xe;
};
L.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Ot;
};
L.isForwardRef = function(e) {
  return X(e) === Ke;
};
L.isFragment = function(e) {
  return X(e) === Be;
};
L.isLazy = function(e) {
  return X(e) === Ze;
};
L.isMemo = function(e) {
  return X(e) === Ye;
};
L.isPortal = function(e) {
  return X(e) === Mt;
};
L.isProfiler = function(e) {
  return X(e) === Ue;
};
L.isStrictMode = function(e) {
  return X(e) === Ge;
};
L.isSuspense = function(e) {
  return X(e) === qe;
};
L.isSuspenseList = function(e) {
  return X(e) === Qe;
};
L.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === Be || e === Ue || e === Ge || e === qe || e === Qe || e === Io || typeof e == "object" && e !== null && (e.$$typeof === Ze || e.$$typeof === Ye || e.$$typeof === Xe || e.$$typeof === We || e.$$typeof === Ke || e.$$typeof === Rr || e.getModuleId !== void 0);
};
L.typeOf = X;
Mr.exports = L;
var at = Mr.exports, jo = Symbol.for("react.element"), zo = Symbol.for("react.transitional.element"), Do = Symbol.for("react.fragment");
function ko(e) {
  return (
    // Base object type
    e && te(e) === "object" && // React Element type
    (e.$$typeof === jo || e.$$typeof === zo) && // React Fragment type
    e.type === Do
  );
}
var No = Number(Zr.split(".")[0]), Fo = function(t, r) {
  typeof t == "function" ? t(r) : te(t) === "object" && t && "current" in t && (t.current = r);
}, Ho = function(t) {
  var r, o;
  if (!t)
    return !1;
  if (Lr(t) && No >= 19)
    return !0;
  var n = at.isMemo(t) ? t.type.type : t.type;
  return !(typeof n == "function" && !((r = n.prototype) !== null && r !== void 0 && r.render) && n.$$typeof !== at.ForwardRef || typeof t == "function" && !((o = t.prototype) !== null && o !== void 0 && o.render) && t.$$typeof !== at.ForwardRef);
};
function Lr(e) {
  return /* @__PURE__ */ Yr(e) && !ko(e);
}
var Vo = function(t) {
  if (t && Lr(t)) {
    var r = t;
    return r.props.propertyIsEnumerable("ref") ? r.props.ref : r.ref;
  }
  return null;
};
function nr(e, t, r, o) {
  var n = E({}, t[e]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var c = U(a, 2), l = c[0], f = c[1];
      if (n != null && n[l] || n != null && n[f]) {
        var u;
        (u = n[f]) !== null && u !== void 0 || (n[f] = n == null ? void 0 : n[l]);
      }
    });
  }
  var s = E(E({}, r), n);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var $r = typeof CSSINJS_STATISTIC < "u", xt = !0;
function Rt() {
  for (var e = arguments.length, t = new Array(e), r = 0; r < e; r++)
    t[r] = arguments[r];
  if (!$r)
    return Object.assign.apply(Object, [{}].concat(t));
  xt = !1;
  var o = {};
  return t.forEach(function(n) {
    if (F(n) === "object") {
      var i = Object.keys(n);
      i.forEach(function(s) {
        Object.defineProperty(o, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return n[s];
          }
        });
      });
    }
  }), xt = !0, o;
}
var or = {};
function Bo() {
}
var Go = function(t) {
  var r, o = t, n = Bo;
  return $r && typeof Proxy < "u" && (r = /* @__PURE__ */ new Set(), o = new Proxy(t, {
    get: function(s, a) {
      if (xt) {
        var c;
        (c = r) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), n = function(s, a) {
    var c;
    or[s] = {
      global: Array.from(r),
      component: E(E({}, (c = or[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: o,
    keys: r,
    flush: n
  };
};
function ir(e, t, r) {
  if (typeof r == "function") {
    var o;
    return r(Rt(t, (o = t[e]) !== null && o !== void 0 ? o : {}));
  }
  return r ?? {};
}
function Uo(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var r = arguments.length, o = new Array(r), n = 0; n < r; n++)
        o[n] = arguments[n];
      return "max(".concat(o.map(function(i) {
        return ze(i);
      }).join(","), ")");
    },
    min: function() {
      for (var r = arguments.length, o = new Array(r), n = 0; n < r; n++)
        o[n] = arguments[n];
      return "min(".concat(o.map(function(i) {
        return ze(i);
      }).join(","), ")");
    }
  };
}
var Xo = 1e3 * 60 * 10, Wo = /* @__PURE__ */ function() {
  function e() {
    de(this, e), w(this, "map", /* @__PURE__ */ new Map()), w(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), w(this, "nextID", 0), w(this, "lastAccessBeat", /* @__PURE__ */ new Map()), w(this, "accessBeat", 0);
  }
  return me(e, [{
    key: "set",
    value: function(r, o) {
      this.clear();
      var n = this.getCompositeKey(r);
      this.map.set(n, o), this.lastAccessBeat.set(n, Date.now());
    }
  }, {
    key: "get",
    value: function(r) {
      var o = this.getCompositeKey(r), n = this.map.get(o);
      return this.lastAccessBeat.set(o, Date.now()), this.accessBeat += 1, n;
    }
  }, {
    key: "getCompositeKey",
    value: function(r) {
      var o = this, n = r.map(function(i) {
        return i && F(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(F(i), "_").concat(i);
      });
      return n.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(r) {
      if (this.objectIDMap.has(r))
        return this.objectIDMap.get(r);
      var o = this.nextID;
      return this.objectIDMap.set(r, o), this.nextID += 1, o;
    }
  }, {
    key: "clear",
    value: function() {
      var r = this;
      if (this.accessBeat > 1e4) {
        var o = Date.now();
        this.lastAccessBeat.forEach(function(n, i) {
          o - n > Xo && (r.map.delete(i), r.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), sr = new Wo();
function Ko(e, t) {
  return x.useMemo(function() {
    var r = sr.get(t);
    if (r)
      return r;
    var o = e();
    return sr.set(t, o), o;
  }, t);
}
var qo = function() {
  return {};
};
function Qo(e) {
  var t = e.useCSP, r = t === void 0 ? qo : t, o = e.useToken, n = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function c(d, h, g, p) {
    var m = Array.isArray(d) ? d[0] : d;
    function S(_) {
      return "".concat(String(m)).concat(_.slice(0, 1).toUpperCase()).concat(_.slice(1));
    }
    var v = (p == null ? void 0 : p.unitless) || {}, T = typeof a == "function" ? a(d) : {}, y = E(E({}, T), {}, w({}, S("zIndexPopup"), !0));
    Object.keys(v).forEach(function(_) {
      y[S(_)] = v[_];
    });
    var P = E(E({}, p), {}, {
      unitless: y,
      prefixToken: S
    }), b = f(d, h, g, P), O = l(m, g, P);
    return function(_) {
      var C = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : _, I = b(_, C), A = U(I, 2), M = A[1], $ = O(C), j = U($, 2), z = j[0], H = j[1];
      return [z, M, H];
    };
  }
  function l(d, h, g) {
    var p = g.unitless, m = g.injectStyle, S = m === void 0 ? !0 : m, v = g.prefixToken, T = g.ignore, y = function(O) {
      var _ = O.rootCls, C = O.cssVar, I = C === void 0 ? {} : C, A = o(), M = A.realToken;
      return mn({
        path: [d],
        prefix: I.prefix,
        key: I.key,
        unitless: p,
        ignore: T,
        token: M,
        scope: _
      }, function() {
        var $ = ir(d, M, h), j = nr(d, M, $, {
          deprecatedTokens: g == null ? void 0 : g.deprecatedTokens
        });
        return Object.keys($).forEach(function(z) {
          j[v(z)] = j[z], delete j[z];
        }), j;
      }), null;
    }, P = function(O) {
      var _ = o(), C = _.cssVar;
      return [function(I) {
        return S && C ? /* @__PURE__ */ x.createElement(x.Fragment, null, /* @__PURE__ */ x.createElement(y, {
          rootCls: O,
          cssVar: C,
          component: d
        }), I) : I;
      }, C == null ? void 0 : C.key];
    };
    return P;
  }
  function f(d, h, g) {
    var p = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, m = Array.isArray(d) ? d : [d, d], S = U(m, 1), v = S[0], T = m.join("-"), y = e.layer || {
      name: "antd"
    };
    return function(P) {
      var b = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : P, O = o(), _ = O.theme, C = O.realToken, I = O.hashId, A = O.token, M = O.cssVar, $ = n(), j = $.rootPrefixCls, z = $.iconPrefixCls, H = r(), re = M ? "css" : "js", Z = Ko(function() {
        var B = /* @__PURE__ */ new Set();
        return M && Object.keys(p.unitless || {}).forEach(function(oe) {
          B.add(rt(oe, M.prefix)), B.add(rt(oe, Jt(v, M.prefix)));
        }), To(re, B);
      }, [re, v, M == null ? void 0 : M.prefix]), be = Uo(re), Se = be.max, V = be.min, ne = {
        theme: _,
        token: A,
        hashId: I,
        nonce: function() {
          return H.nonce;
        },
        clientOnly: p.clientOnly,
        layer: y,
        // antd is always at top of styles
        order: p.order || -999
      };
      typeof i == "function" && Dt(E(E({}, ne), {}, {
        clientOnly: !1,
        path: ["Shared", j]
      }), function() {
        return i(A, {
          prefix: {
            rootPrefixCls: j,
            iconPrefixCls: z
          },
          csp: H
        });
      });
      var he = Dt(E(E({}, ne), {}, {
        path: [T, P, z]
      }), function() {
        if (p.injectStyle === !1)
          return [];
        var B = Go(A), oe = B.token, xe = B.flush, Q = ir(v, C, g), Je = ".".concat(P), Ce = nr(v, C, Q, {
          deprecatedTokens: p.deprecatedTokens
        });
        M && Q && F(Q) === "object" && Object.keys(Q).forEach(function(we) {
          Q[we] = "var(".concat(rt(we, Jt(v, M.prefix)), ")");
        });
        var Ee = Rt(oe, {
          componentCls: Je,
          prefixCls: P,
          iconCls: ".".concat(z),
          antCls: ".".concat(j),
          calc: Z,
          // @ts-ignore
          max: Se,
          // @ts-ignore
          min: V
        }, M ? Q : Ce), _e = h(Ee, {
          hashId: I,
          prefixCls: P,
          rootPrefixCls: j,
          iconPrefixCls: z
        });
        xe(v, Ce);
        var ie = typeof s == "function" ? s(Ee, P, b, p.resetFont) : null;
        return [p.resetStyle === !1 ? null : ie, _e];
      });
      return [he, I];
    };
  }
  function u(d, h, g) {
    var p = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, m = f(d, h, g, E({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, p)), S = function(T) {
      var y = T.prefixCls, P = T.rootCls, b = P === void 0 ? y : P;
      return m(y, b), null;
    };
    return S;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: u,
    genComponentStyleHook: f
  };
}
const Yo = {
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
}, Zo = Object.assign(Object.assign({}, Yo), {
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
}), D = Math.round;
function ct(e, t) {
  const r = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = r.map((n) => parseFloat(n));
  for (let n = 0; n < 3; n += 1)
    o[n] = t(o[n] || 0, r[n] || "", n);
  return r[3] ? o[3] = r[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const ar = (e, t, r) => r === 0 ? e : e / 100;
function pe(e, t) {
  const r = t || 255;
  return e > r ? r : e < 0 ? 0 : e;
}
class Y {
  constructor(t) {
    w(this, "isValid", !0), w(this, "r", 0), w(this, "g", 0), w(this, "b", 0), w(this, "a", 1), w(this, "_h", void 0), w(this, "_s", void 0), w(this, "_l", void 0), w(this, "_v", void 0), w(this, "_max", void 0), w(this, "_min", void 0), w(this, "_brightness", void 0);
    function r(o) {
      return o[0] in t && o[1] in t && o[2] in t;
    }
    if (t) if (typeof t == "string") {
      let n = function(i) {
        return o.startsWith(i);
      };
      const o = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : n("rgb") ? this.fromRgbString(o) : n("hsl") ? this.fromHslString(o) : (n("hsv") || n("hsb")) && this.fromHsvString(o);
    } else if (t instanceof Y)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (r("rgb"))
      this.r = pe(t.r), this.g = pe(t.g), this.b = pe(t.b), this.a = typeof t.a == "number" ? pe(t.a, 1) : 1;
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
    const r = t(this.r), o = t(this.g), n = t(this.b);
    return 0.2126 * r + 0.7152 * o + 0.0722 * n;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = D(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
    const r = this.getHue(), o = this.getSaturation();
    let n = this.getLightness() - t / 100;
    return n < 0 && (n = 0), this._c({
      h: r,
      s: o,
      l: n,
      a: this.a
    });
  }
  lighten(t = 10) {
    const r = this.getHue(), o = this.getSaturation();
    let n = this.getLightness() + t / 100;
    return n > 1 && (n = 1), this._c({
      h: r,
      s: o,
      l: n,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(t, r = 50) {
    const o = this._c(t), n = r / 100, i = (a) => (o[a] - this[a]) * n + this[a], s = {
      r: D(i("r")),
      g: D(i("g")),
      b: D(i("b")),
      a: D(i("a") * 100) / 100
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
    const r = this._c(t), o = this.a + r.a * (1 - this.a), n = (i) => D((this[i] * this.a + r[i] * r.a * (1 - this.a)) / o);
    return this._c({
      r: n("r"),
      g: n("g"),
      b: n("b"),
      a: o
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
    const o = (this.g || 0).toString(16);
    t += o.length === 2 ? o : "0" + o;
    const n = (this.b || 0).toString(16);
    if (t += n.length === 2 ? n : "0" + n, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = D(this.a * 255).toString(16);
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
    const t = this.getHue(), r = D(this.getSaturation() * 100), o = D(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${r}%,${o}%,${this.a})` : `hsl(${t},${r}%,${o}%)`;
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
  _sc(t, r, o) {
    const n = this.clone();
    return n[t] = pe(r, o), n;
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
    function o(n, i) {
      return parseInt(r[n] + r[i || n], 16);
    }
    r.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = r[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = r[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: r,
    l: o,
    a: n
  }) {
    if (this._h = t % 360, this._s = r, this._l = o, this.a = typeof n == "number" ? n : 1, r <= 0) {
      const d = D(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let i = 0, s = 0, a = 0;
    const c = t / 60, l = (1 - Math.abs(2 * o - 1)) * r, f = l * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (i = l, s = f) : c >= 1 && c < 2 ? (i = f, s = l) : c >= 2 && c < 3 ? (s = l, a = f) : c >= 3 && c < 4 ? (s = f, a = l) : c >= 4 && c < 5 ? (i = f, a = l) : c >= 5 && c < 6 && (i = l, a = f);
    const u = o - l / 2;
    this.r = D((i + u) * 255), this.g = D((s + u) * 255), this.b = D((a + u) * 255);
  }
  fromHsv({
    h: t,
    s: r,
    v: o,
    a: n
  }) {
    this._h = t % 360, this._s = r, this._v = o, this.a = typeof n == "number" ? n : 1;
    const i = D(o * 255);
    if (this.r = i, this.g = i, this.b = i, r <= 0)
      return;
    const s = t / 60, a = Math.floor(s), c = s - a, l = D(o * (1 - r) * 255), f = D(o * (1 - r * c) * 255), u = D(o * (1 - r * (1 - c)) * 255);
    switch (a) {
      case 0:
        this.g = u, this.b = l;
        break;
      case 1:
        this.r = f, this.b = l;
        break;
      case 2:
        this.r = l, this.b = u;
        break;
      case 3:
        this.r = l, this.g = f;
        break;
      case 4:
        this.r = u, this.g = l;
        break;
      case 5:
      default:
        this.g = l, this.b = f;
        break;
    }
  }
  fromHsvString(t) {
    const r = ct(t, ar);
    this.fromHsv({
      h: r[0],
      s: r[1],
      v: r[2],
      a: r[3]
    });
  }
  fromHslString(t) {
    const r = ct(t, ar);
    this.fromHsl({
      h: r[0],
      s: r[1],
      l: r[2],
      a: r[3]
    });
  }
  fromRgbString(t) {
    const r = ct(t, (o, n) => (
      // Convert percentage to number. e.g. 50% -> 128
      n.includes("%") ? D(o / 100 * 255) : o
    ));
    this.r = r[0], this.g = r[1], this.b = r[2], this.a = r[3];
  }
}
function lt(e) {
  return e >= 0 && e <= 255;
}
function Oe(e, t) {
  const {
    r,
    g: o,
    b: n,
    a: i
  } = new Y(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: c
  } = new Y(t).toRgb();
  for (let l = 0.01; l <= 1; l += 0.01) {
    const f = Math.round((r - s * (1 - l)) / l), u = Math.round((o - a * (1 - l)) / l), d = Math.round((n - c * (1 - l)) / l);
    if (lt(f) && lt(u) && lt(d))
      return new Y({
        r: f,
        g: u,
        b: d,
        a: Math.round(l * 100) / 100
      }).toRgbString();
  }
  return new Y({
    r,
    g: o,
    b: n,
    a: 1
  }).toRgbString();
}
var Jo = function(e, t) {
  var r = {};
  for (var o in e) Object.prototype.hasOwnProperty.call(e, o) && t.indexOf(o) < 0 && (r[o] = e[o]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var n = 0, o = Object.getOwnPropertySymbols(e); n < o.length; n++)
    t.indexOf(o[n]) < 0 && Object.prototype.propertyIsEnumerable.call(e, o[n]) && (r[o[n]] = e[o[n]]);
  return r;
};
function ei(e) {
  const {
    override: t
  } = e, r = Jo(e, ["override"]), o = Object.assign({}, t);
  Object.keys(Zo).forEach((d) => {
    delete o[d];
  });
  const n = Object.assign(Object.assign({}, r), o), i = 480, s = 576, a = 768, c = 992, l = 1200, f = 1600;
  if (n.motion === !1) {
    const d = "0s";
    n.motionDurationFast = d, n.motionDurationMid = d, n.motionDurationSlow = d;
  }
  return Object.assign(Object.assign(Object.assign({}, n), {
    // ============== Background ============== //
    colorFillContent: n.colorFillSecondary,
    colorFillContentHover: n.colorFill,
    colorFillAlter: n.colorFillQuaternary,
    colorBgContainerDisabled: n.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: n.colorBgContainer,
    colorSplit: Oe(n.colorBorderSecondary, n.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: n.colorTextQuaternary,
    colorTextDisabled: n.colorTextQuaternary,
    colorTextHeading: n.colorText,
    colorTextLabel: n.colorTextSecondary,
    colorTextDescription: n.colorTextTertiary,
    colorTextLightSolid: n.colorWhite,
    colorHighlight: n.colorError,
    colorBgTextHover: n.colorFillSecondary,
    colorBgTextActive: n.colorFill,
    colorIcon: n.colorTextTertiary,
    colorIconHover: n.colorText,
    colorErrorOutline: Oe(n.colorErrorBg, n.colorBgContainer),
    colorWarningOutline: Oe(n.colorWarningBg, n.colorBgContainer),
    // Font
    fontSizeIcon: n.fontSizeSM,
    // Line
    lineWidthFocus: n.lineWidth * 3,
    // Control
    lineWidth: n.lineWidth,
    controlOutlineWidth: n.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: n.controlHeight / 2,
    controlItemBgHover: n.colorFillTertiary,
    controlItemBgActive: n.colorPrimaryBg,
    controlItemBgActiveHover: n.colorPrimaryBgHover,
    controlItemBgActiveDisabled: n.colorFill,
    controlTmpOutline: n.colorFillQuaternary,
    controlOutline: Oe(n.colorPrimaryBg, n.colorBgContainer),
    lineType: n.lineType,
    borderRadius: n.borderRadius,
    borderRadiusXS: n.borderRadiusXS,
    borderRadiusSM: n.borderRadiusSM,
    borderRadiusLG: n.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: n.sizeXXS,
    paddingXS: n.sizeXS,
    paddingSM: n.sizeSM,
    padding: n.size,
    paddingMD: n.sizeMD,
    paddingLG: n.sizeLG,
    paddingXL: n.sizeXL,
    paddingContentHorizontalLG: n.sizeLG,
    paddingContentVerticalLG: n.sizeMS,
    paddingContentHorizontal: n.sizeMS,
    paddingContentVertical: n.sizeSM,
    paddingContentHorizontalSM: n.size,
    paddingContentVerticalSM: n.sizeXS,
    marginXXS: n.sizeXXS,
    marginXS: n.sizeXS,
    marginSM: n.sizeSM,
    margin: n.size,
    marginMD: n.sizeMD,
    marginLG: n.sizeLG,
    marginXL: n.sizeXL,
    marginXXL: n.sizeXXL,
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
    screenMDMax: c - 1,
    screenLG: c,
    screenLGMin: c,
    screenLGMax: l - 1,
    screenXL: l,
    screenXLMin: l,
    screenXLMax: f - 1,
    screenXXL: f,
    screenXXLMin: f,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new Y("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new Y("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new Y("rgba(0, 0, 0, 0.09)").toRgbString()}
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
  }), o);
}
const ti = {
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
}, ri = {
  motionBase: !0,
  motionUnit: !0
}, ni = hn(vt.defaultAlgorithm), oi = {
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
}, Ar = (e, t, r) => {
  const o = r.getDerivativeToken(e), {
    override: n,
    ...i
  } = t;
  let s = {
    ...o,
    override: n
  };
  return s = ei(s), i && Object.entries(i).forEach(([a, c]) => {
    const {
      theme: l,
      ...f
    } = c;
    let u = f;
    l && (u = Ar({
      ...s,
      ...f
    }, {
      override: f
    }, l)), s[a] = u;
  }), s;
};
function ii() {
  const {
    token: e,
    hashed: t,
    theme: r = ni,
    override: o,
    cssVar: n
  } = x.useContext(vt._internalContext), [i, s, a] = pn(r, [vt.defaultSeed, e], {
    salt: `${ro}-${t || ""}`,
    override: o,
    getComputedToken: Ar,
    cssVar: n && {
      prefix: n.prefix,
      key: n.key,
      unitless: ti,
      ignore: ri,
      preserve: oi
    }
  });
  return [r, a, t ? s : "", i, n];
}
const {
  genStyleHooks: si
} = Qo({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = bt();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, r, o, n] = ii();
    return {
      theme: e,
      realToken: t,
      hashId: r,
      token: o,
      cssVar: n
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = bt();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
function cr(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function ai(e) {
  return e && te(e) === "object" && cr(e.nativeElement) ? e.nativeElement : cr(e) ? e : null;
}
function ci(e) {
  var t = ai(e);
  if (t)
    return t;
  if (e instanceof x.Component) {
    var r;
    return (r = jt.findDOMNode) === null || r === void 0 ? void 0 : r.call(jt, e);
  }
  return null;
}
function li(e, t) {
  if (e == null) return {};
  var r = {};
  for (var o in e) if ({}.hasOwnProperty.call(e, o)) {
    if (t.indexOf(o) !== -1) continue;
    r[o] = e[o];
  }
  return r;
}
function lr(e, t) {
  if (e == null) return {};
  var r, o, n = li(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (o = 0; o < i.length; o++) r = i[o], t.indexOf(r) === -1 && {}.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
  }
  return n;
}
var ui = /* @__PURE__ */ R.createContext({}), fi = /* @__PURE__ */ function(e) {
  Fe(r, e);
  var t = He(r);
  function r() {
    return de(this, r), t.apply(this, arguments);
  }
  return me(r, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), r;
}(R.Component);
function di(e) {
  var t = R.useReducer(function(a) {
    return a + 1;
  }, 0), r = ke(t, 2), o = r[1], n = R.useRef(e), i = ve(function() {
    return n.current;
  }), s = ve(function(a) {
    n.current = typeof a == "function" ? a(n.current) : a, o();
  });
  return [i, s];
}
var J = "none", Me = "appear", Re = "enter", Le = "leave", ur = "none", W = "prepare", le = "start", ue = "active", Lt = "end", Ir = "prepared";
function fr(e, t) {
  var r = {};
  return r[e.toLowerCase()] = t.toLowerCase(), r["Webkit".concat(e)] = "webkit".concat(t), r["Moz".concat(e)] = "moz".concat(t), r["ms".concat(e)] = "MS".concat(t), r["O".concat(e)] = "o".concat(t.toLowerCase()), r;
}
function mi(e, t) {
  var r = {
    animationend: fr("Animation", "AnimationEnd"),
    transitionend: fr("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete r.animationend.animation, "TransitionEvent" in t || delete r.transitionend.transition), r;
}
var hi = mi(Ve(), typeof window < "u" ? window : {}), jr = {};
if (Ve()) {
  var pi = document.createElement("div");
  jr = pi.style;
}
var $e = {};
function zr(e) {
  if ($e[e])
    return $e[e];
  var t = hi[e];
  if (t)
    for (var r = Object.keys(t), o = r.length, n = 0; n < o; n += 1) {
      var i = r[n];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in jr)
        return $e[e] = t[i], $e[e];
    }
  return "";
}
var Dr = zr("animationend"), kr = zr("transitionend"), Nr = !!(Dr && kr), dr = Dr || "animationend", mr = kr || "transitionend";
function hr(e, t) {
  if (!e) return null;
  if (F(e) === "object") {
    var r = t.replace(/-\w/g, function(o) {
      return o[1].toUpperCase();
    });
    return e[r];
  }
  return "".concat(e, "-").concat(t);
}
const gi = function(e) {
  var t = ee();
  function r(n) {
    n && (n.removeEventListener(mr, e), n.removeEventListener(dr, e));
  }
  function o(n) {
    t.current && t.current !== n && r(t.current), n && n !== t.current && (n.addEventListener(mr, e), n.addEventListener(dr, e), t.current = n);
  }
  return R.useEffect(function() {
    return function() {
      r(t.current);
    };
  }, []), [o, r];
};
var Fr = Ve() ? Jr : ge, Hr = function(t) {
  return +setTimeout(t, 16);
}, Vr = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (Hr = function(t) {
  return window.requestAnimationFrame(t);
}, Vr = function(t) {
  return window.cancelAnimationFrame(t);
});
var pr = 0, $t = /* @__PURE__ */ new Map();
function Br(e) {
  $t.delete(e);
}
var Ct = function(t) {
  var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  pr += 1;
  var o = pr;
  function n(i) {
    if (i === 0)
      Br(o), t();
    else {
      var s = Hr(function() {
        n(i - 1);
      });
      $t.set(o, s);
    }
  }
  return n(r), o;
};
Ct.cancel = function(e) {
  var t = $t.get(e);
  return Br(e), Vr(t);
};
const vi = function() {
  var e = R.useRef(null);
  function t() {
    Ct.cancel(e.current);
  }
  function r(o) {
    var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = Ct(function() {
      n <= 1 ? o({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : r(o, n - 1);
    });
    e.current = i;
  }
  return R.useEffect(function() {
    return function() {
      t();
    };
  }, []), [r, t];
};
var yi = [W, le, ue, Lt], bi = [W, Ir], Gr = !1, Si = !0;
function Ur(e) {
  return e === ue || e === Lt;
}
const xi = function(e, t, r) {
  var o = ye(ur), n = U(o, 2), i = n[0], s = n[1], a = vi(), c = U(a, 2), l = c[0], f = c[1];
  function u() {
    s(W, !0);
  }
  var d = t ? bi : yi;
  return Fr(function() {
    if (i !== ur && i !== Lt) {
      var h = d.indexOf(i), g = d[h + 1], p = r(i);
      p === Gr ? s(g, !0) : g && l(function(m) {
        function S() {
          m.isCanceled() || s(g, !0);
        }
        p === !0 ? S() : Promise.resolve(p).then(S);
      });
    }
  }, [e, i]), R.useEffect(function() {
    return function() {
      f();
    };
  }, []), [u, i];
};
function Ci(e, t, r, o) {
  var n = o.motionEnter, i = n === void 0 ? !0 : n, s = o.motionAppear, a = s === void 0 ? !0 : s, c = o.motionLeave, l = c === void 0 ? !0 : c, f = o.motionDeadline, u = o.motionLeaveImmediately, d = o.onAppearPrepare, h = o.onEnterPrepare, g = o.onLeavePrepare, p = o.onAppearStart, m = o.onEnterStart, S = o.onLeaveStart, v = o.onAppearActive, T = o.onEnterActive, y = o.onLeaveActive, P = o.onAppearEnd, b = o.onEnterEnd, O = o.onLeaveEnd, _ = o.onVisibleChanged, C = ye(), I = U(C, 2), A = I[0], M = I[1], $ = di(J), j = U($, 2), z = j[0], H = j[1], re = ye(null), Z = U(re, 2), be = Z[0], Se = Z[1], V = z(), ne = ee(!1), he = ee(null);
  function B() {
    return r();
  }
  var oe = ee(!1);
  function xe() {
    H(J), Se(null, !0);
  }
  var Q = ve(function(N) {
    var k = z();
    if (k !== J) {
      var K = B();
      if (!(N && !N.deadline && N.target !== K)) {
        var Te = oe.current, Pe;
        k === Me && Te ? Pe = P == null ? void 0 : P(K, N) : k === Re && Te ? Pe = b == null ? void 0 : b(K, N) : k === Le && Te && (Pe = O == null ? void 0 : O(K, N)), Te && Pe !== !1 && xe();
      }
    }
  }), Je = gi(Q), Ce = U(Je, 1), Ee = Ce[0], _e = function(k) {
    switch (k) {
      case Me:
        return w(w(w({}, W, d), le, p), ue, v);
      case Re:
        return w(w(w({}, W, h), le, m), ue, T);
      case Le:
        return w(w(w({}, W, g), le, S), ue, y);
      default:
        return {};
    }
  }, ie = R.useMemo(function() {
    return _e(V);
  }, [V]), we = xi(V, !e, function(N) {
    if (N === W) {
      var k = ie[W];
      return k ? k(B()) : Gr;
    }
    if (se in ie) {
      var K;
      Se(((K = ie[se]) === null || K === void 0 ? void 0 : K.call(ie, B(), null)) || null);
    }
    return se === ue && V !== J && (Ee(B()), f > 0 && (clearTimeout(he.current), he.current = setTimeout(function() {
      Q({
        deadline: !0
      });
    }, f))), se === Ir && xe(), Si;
  }), At = U(we, 2), qr = At[0], se = At[1], Qr = Ur(se);
  oe.current = Qr;
  var It = ee(null);
  Fr(function() {
    if (!(ne.current && It.current === t)) {
      M(t);
      var N = ne.current;
      ne.current = !0;
      var k;
      !N && t && a && (k = Me), N && t && i && (k = Re), (N && !t && l || !N && u && !t && l) && (k = Le);
      var K = _e(k);
      k && (e || K[W]) ? (H(k), qr()) : H(J), It.current = t;
    }
  }, [t]), ge(function() {
    // Cancel appear
    (V === Me && !a || // Cancel enter
    V === Re && !i || // Cancel leave
    V === Le && !l) && H(J);
  }, [a, i, l]), ge(function() {
    return function() {
      ne.current = !1, clearTimeout(he.current);
    };
  }, []);
  var et = R.useRef(!1);
  ge(function() {
    A && (et.current = !0), A !== void 0 && V === J && ((et.current || A) && (_ == null || _(A)), et.current = !0);
  }, [A, V]);
  var tt = be;
  return ie[W] && se === le && (tt = E({
    transition: "none"
  }, tt)), [V, se, tt, A ?? t];
}
function Ei(e) {
  var t = e;
  F(e) === "object" && (t = e.transitionSupport);
  function r(n, i) {
    return !!(n.motionName && t && i !== !1);
  }
  var o = /* @__PURE__ */ R.forwardRef(function(n, i) {
    var s = n.visible, a = s === void 0 ? !0 : s, c = n.removeOnLeave, l = c === void 0 ? !0 : c, f = n.forceRender, u = n.children, d = n.motionName, h = n.leavedClassName, g = n.eventProps, p = R.useContext(ui), m = p.motion, S = r(n, m), v = ee(), T = ee();
    function y() {
      try {
        return v.current instanceof HTMLElement ? v.current : ci(T.current);
      } catch {
        return null;
      }
    }
    var P = Ci(S, a, y, n), b = U(P, 4), O = b[0], _ = b[1], C = b[2], I = b[3], A = R.useRef(I);
    I && (A.current = !0);
    var M = R.useCallback(function(Z) {
      v.current = Z, Fo(i, Z);
    }, [i]), $, j = E(E({}, g), {}, {
      visible: a
    });
    if (!u)
      $ = null;
    else if (O === J)
      I ? $ = u(E({}, j), M) : !l && A.current && h ? $ = u(E(E({}, j), {}, {
        className: h
      }), M) : f || !l && !h ? $ = u(E(E({}, j), {}, {
        style: {
          display: "none"
        }
      }), M) : $ = null;
    else {
      var z;
      _ === W ? z = "prepare" : Ur(_) ? z = "active" : _ === le && (z = "start");
      var H = hr(d, "".concat(O, "-").concat(z));
      $ = u(E(E({}, j), {}, {
        className: G(hr(d, O), w(w({}, H, H && z), d, typeof d == "string")),
        style: C
      }), M);
    }
    if (/* @__PURE__ */ R.isValidElement($) && Ho($)) {
      var re = Vo($);
      re || ($ = /* @__PURE__ */ R.cloneElement($, {
        ref: M
      }));
    }
    return /* @__PURE__ */ R.createElement(fi, {
      ref: T
    }, $);
  });
  return o.displayName = "CSSMotion", o;
}
const Xr = Ei(Nr);
var Et = "add", _t = "keep", wt = "remove", ut = "removed";
function _i(e) {
  var t;
  return e && F(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, E(E({}, t), {}, {
    key: String(t.key)
  });
}
function Tt() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(_i);
}
function wi() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], r = [], o = 0, n = t.length, i = Tt(e), s = Tt(t);
  i.forEach(function(l) {
    for (var f = !1, u = o; u < n; u += 1) {
      var d = s[u];
      if (d.key === l.key) {
        o < u && (r = r.concat(s.slice(o, u).map(function(h) {
          return E(E({}, h), {}, {
            status: Et
          });
        })), o = u), r.push(E(E({}, d), {}, {
          status: _t
        })), o += 1, f = !0;
        break;
      }
    }
    f || r.push(E(E({}, l), {}, {
      status: wt
    }));
  }), o < n && (r = r.concat(s.slice(o).map(function(l) {
    return E(E({}, l), {}, {
      status: Et
    });
  })));
  var a = {};
  r.forEach(function(l) {
    var f = l.key;
    a[f] = (a[f] || 0) + 1;
  });
  var c = Object.keys(a).filter(function(l) {
    return a[l] > 1;
  });
  return c.forEach(function(l) {
    r = r.filter(function(f) {
      var u = f.key, d = f.status;
      return u !== l || d !== wt;
    }), r.forEach(function(f) {
      f.key === l && (f.status = _t);
    });
  }), r;
}
var Ti = ["component", "children", "onVisibleChanged", "onAllRemoved"], Pi = ["status"], Oi = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function Mi(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Xr, r = /* @__PURE__ */ function(o) {
    Fe(i, o);
    var n = He(i);
    function i() {
      var s;
      de(this, i);
      for (var a = arguments.length, c = new Array(a), l = 0; l < a; l++)
        c[l] = arguments[l];
      return s = n.call.apply(n, [this].concat(c)), w(ae(s), "state", {
        keyEntities: []
      }), w(ae(s), "removeKey", function(f) {
        s.setState(function(u) {
          var d = u.keyEntities.map(function(h) {
            return h.key !== f ? h : E(E({}, h), {}, {
              status: ut
            });
          });
          return {
            keyEntities: d
          };
        }, function() {
          var u = s.state.keyEntities, d = u.filter(function(h) {
            var g = h.status;
            return g !== ut;
          }).length;
          d === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return me(i, [{
      key: "render",
      value: function() {
        var a = this, c = this.state.keyEntities, l = this.props, f = l.component, u = l.children, d = l.onVisibleChanged;
        l.onAllRemoved;
        var h = lr(l, Ti), g = f || R.Fragment, p = {};
        return Oi.forEach(function(m) {
          p[m] = h[m], delete h[m];
        }), delete h.keys, /* @__PURE__ */ R.createElement(g, h, c.map(function(m, S) {
          var v = m.status, T = lr(m, Pi), y = v === Et || v === _t;
          return /* @__PURE__ */ R.createElement(t, fe({}, p, {
            key: T.key,
            visible: y,
            eventProps: T,
            onVisibleChanged: function(b) {
              d == null || d(b, {
                key: T.key
              }), b || a.removeKey(T.key);
            }
          }), function(P, b) {
            return u(E(E({}, P), {}, {
              index: S
            }), b);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, c) {
        var l = a.keys, f = c.keyEntities, u = Tt(l), d = wi(f, u);
        return {
          keyEntities: d.filter(function(h) {
            var g = f.find(function(p) {
              var m = p.key;
              return h.key === m;
            });
            return !(g && g.status === ut && h.status === wt);
          })
        };
      }
    }]), i;
  }(R.Component);
  return w(r, "defaultProps", {
    component: "div"
  }), r;
}
Mi(Nr);
const ft = () => ({
  height: 0,
  opacity: 0
}), gr = (e) => {
  const {
    scrollHeight: t
  } = e;
  return {
    height: t,
    opacity: 1
  };
}, Ri = (e) => ({
  height: e ? e.offsetHeight : 0
}), dt = (e, t) => (t == null ? void 0 : t.deadline) === !0 || t.propertyName === "height", Li = (e = go) => ({
  motionName: `${e}-motion-collapse`,
  onAppearStart: ft,
  onEnterStart: ft,
  onAppearActive: gr,
  onEnterActive: gr,
  onLeaveStart: Ri,
  onLeaveActive: ft,
  onAppearEnd: dt,
  onEnterEnd: dt,
  onLeaveEnd: dt,
  motionDeadline: 500
}), $i = (e, t, r) => {
  const o = typeof e == "boolean" || (e == null ? void 0 : e.expandedKeys) === void 0, [n, i, s] = x.useMemo(() => {
    let u = {
      expandedKeys: [],
      onExpand: () => {
      }
    };
    return e ? (typeof e == "object" && (u = {
      ...u,
      ...e
    }), [!0, u.expandedKeys, u.onExpand]) : [!1, u.expandedKeys, u.onExpand];
  }, [e]), [a, c] = $o(i, {
    value: o ? void 0 : i,
    onChange: s
  }), l = (u) => {
    c((d) => {
      const h = o ? d : i, g = h.includes(u) ? h.filter((p) => p !== u) : [...h, u];
      return s == null || s(g), g;
    });
  }, f = x.useMemo(() => n ? {
    ...Li(r),
    motionAppear: !1,
    leavedClassName: `${t}-content-hidden`
  } : {}, [r, t, n]);
  return [n, a, n ? l : void 0, f];
}, Ai = (e) => ({
  [e.componentCls]: {
    // For common/openAnimation
    [`${e.antCls}-motion-collapse-legacy`]: {
      overflow: "hidden",
      "&-active": {
        transition: `height ${e.motionDurationMid} ${e.motionEaseInOut},
        opacity ${e.motionDurationMid} ${e.motionEaseInOut} !important`
      }
    },
    [`${e.antCls}-motion-collapse`]: {
      overflow: "hidden",
      transition: `height ${e.motionDurationMid} ${e.motionEaseInOut},
        opacity ${e.motionDurationMid} ${e.motionEaseInOut} !important`
    }
  }
});
let mt = /* @__PURE__ */ function(e) {
  return e.PENDING = "pending", e.SUCCESS = "success", e.ERROR = "error", e;
}({});
const Wr = /* @__PURE__ */ x.createContext(null), Ii = (e) => {
  const {
    info: t = {},
    nextStatus: r,
    onClick: o,
    ...n
  } = e, i = _r(n, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    prefixCls: s,
    collapseMotion: a,
    enableCollapse: c,
    expandedKeys: l,
    direction: f,
    classNames: u = {},
    styles: d = {}
  } = x.useContext(Wr), h = x.useId(), {
    key: g = h,
    icon: p,
    title: m,
    extra: S,
    content: v,
    footer: T,
    status: y,
    description: P
  } = t, [b, O] = x.useState(!1), _ = x.useRef(null);
  x.useEffect(() => {
    const M = () => {
      _.current && O(_.current.scrollWidth > _.current.clientWidth);
    };
    M();
    const $ = new ResizeObserver(M);
    return _.current && $.observe(_.current), () => {
      $.disconnect();
    };
  }, [m]);
  const C = `${s}-item`, I = () => o == null ? void 0 : o(g), A = l == null ? void 0 : l.includes(g);
  return /* @__PURE__ */ x.createElement("div", fe({}, i, {
    className: G(C, {
      [`${C}-${y}${r ? `-${r}` : ""}`]: y
    }, e.className),
    style: e.style
  }), /* @__PURE__ */ x.createElement("div", {
    className: G(`${C}-header`, u.itemHeader),
    style: d.itemHeader,
    onClick: I
  }, /* @__PURE__ */ x.createElement(un, {
    icon: p,
    className: `${C}-icon`
  }), /* @__PURE__ */ x.createElement("div", {
    className: G(`${C}-header-box`, {
      [`${C}-collapsible`]: c && v
    })
  }, /* @__PURE__ */ x.createElement(fn, {
    title: b ? m : void 0,
    placement: f === "rtl" ? "topRight" : "topLeft"
  }, /* @__PURE__ */ x.createElement("div", {
    className: `${C}-title`
  }, c && v && (f === "rtl" ? /* @__PURE__ */ x.createElement(gn, {
    className: `${C}-collapse-icon`,
    rotate: A ? -90 : 0
  }) : /* @__PURE__ */ x.createElement(vn, {
    className: `${C}-collapse-icon`,
    rotate: A ? 90 : 0
  })), /* @__PURE__ */ x.createElement("div", {
    ref: _,
    className: `${C}-title-content`
  }, m))), P && /* @__PURE__ */ x.createElement(dn.Text, {
    className: `${C}-desc`,
    ellipsis: {
      tooltip: {
        placement: f === "rtl" ? "topRight" : "topLeft",
        title: P
      }
    },
    type: "secondary"
  }, P)), S && /* @__PURE__ */ x.createElement("div", {
    className: `${C}-extra`
  }, S)), v && /* @__PURE__ */ x.createElement(Xr, fe({}, a, {
    visible: c ? A : !0
  }), ({
    className: M,
    style: $
  }, j) => /* @__PURE__ */ x.createElement("div", {
    className: G(`${C}-content`, M),
    ref: j,
    style: $
  }, /* @__PURE__ */ x.createElement("div", {
    className: G(`${C}-content-box`, u.itemContent),
    style: d.itemContent
  }, v))), T && /* @__PURE__ */ x.createElement("div", {
    className: G(`${C}-footer`, u.itemFooter),
    style: d.itemFooter
  }, T));
}, ji = (e) => {
  const {
    componentCls: t
  } = e, r = `${t}-item`, o = {
    [mt.PENDING]: e.colorPrimaryText,
    [mt.SUCCESS]: e.colorSuccessText,
    [mt.ERROR]: e.colorErrorText
  }, n = Object.keys(o);
  return n.reduce((i, s) => {
    const a = o[s];
    return n.forEach((c) => {
      const l = `& ${r}-${s}-${c}`, f = s === c ? {} : {
        backgroundColor: "none !important",
        backgroundImage: `linear-gradient(${a}, ${o[c]})`
      };
      i[l] = {
        [`& ${r}-icon, & > *::before`]: {
          backgroundColor: `${a} !important`
        },
        "& > :last-child::before": f
      };
    }), i;
  }, {});
}, zi = (e) => {
  const {
    calc: t,
    componentCls: r
  } = e, o = `${r}-item`, n = {
    content: '""',
    width: t(e.lineWidth).mul(2).equal(),
    display: "block",
    position: "absolute",
    insetInlineEnd: "none",
    backgroundColor: e.colorTextPlaceholder
  };
  return {
    "& > :last-child > :last-child": {
      "&::before": {
        display: "none !important"
      },
      [`&${o}-footer`]: {
        "&::before": {
          display: "block !important",
          bottom: 0
        }
      }
    },
    [`& > ${o}`]: {
      [`& ${o}-header, & ${o}-content, & ${o}-footer`]: {
        position: "relative",
        "&::before": {
          bottom: t(e.itemGap).mul(-1).equal()
        }
      },
      [`& ${o}-header, & ${o}-content`]: {
        marginInlineStart: t(e.itemSize).mul(-1).equal(),
        "&::before": {
          ...n,
          insetInlineStart: t(e.itemSize).div(2).sub(e.lineWidth).equal()
        }
      },
      [`& ${o}-header::before`]: {
        top: e.itemSize,
        bottom: t(e.itemGap).mul(-2).equal()
      },
      [`& ${o}-content::before`]: {
        top: "100%"
      },
      [`& ${o}-footer::before`]: {
        ...n,
        top: 0,
        insetInlineStart: t(e.itemSize).div(-2).sub(e.lineWidth).equal()
      }
    }
  };
}, Di = (e) => {
  const {
    componentCls: t
  } = e, r = `${t}-item`;
  return {
    [r]: {
      display: "flex",
      flexDirection: "column",
      [`& ${r}-collapsible`]: {
        cursor: "pointer"
      },
      [`& ${r}-header`]: {
        display: "flex",
        marginBottom: e.itemGap,
        gap: e.itemGap,
        alignItems: "flex-start",
        [`& ${r}-icon`]: {
          height: e.itemSize,
          width: e.itemSize,
          fontSize: e.itemFontSize
        },
        [`& ${r}-extra`]: {
          height: e.itemSize,
          maxHeight: e.itemSize
        },
        [`& ${r}-header-box`]: {
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          [`& ${r}-title`]: {
            height: e.itemSize,
            lineHeight: `${ze(e.itemSize)}`,
            maxHeight: e.itemSize,
            fontSize: e.itemFontSize,
            display: "flex",
            alignItems: "center",
            [`& ${r}-collapse-icon`]: {
              marginInlineEnd: e.marginXS,
              flexShrink: 0
            },
            [`& ${r}-title-content`]: {
              flex: 1,
              minWidth: 0,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              fontWeight: e.fontWeightStrong
            }
          },
          [`& ${r}-desc`]: {
            fontSize: e.itemFontSize
          }
        }
      },
      [`& ${r}-content`]: {
        [`& ${r}-content-hidden`]: {
          display: "none"
        },
        [`& ${r}-content-box`]: {
          padding: e.itemGap,
          display: "inline-block",
          maxWidth: `calc(100% - ${e.itemSize})`,
          borderRadius: e.borderRadiusLG,
          backgroundColor: e.colorBgContainer,
          border: `${ze(e.lineWidth)} ${e.lineType} ${e.colorBorderSecondary}`
        }
      },
      [`& ${r}-footer`]: {
        marginTop: e.itemGap,
        display: "inline-flex"
      }
    }
  };
}, ht = (e, t = "middle") => {
  const {
    componentCls: r
  } = e, o = {
    large: {
      itemSize: e.itemSizeLG,
      itemGap: e.itemGapLG,
      itemFontSize: e.itemFontSizeLG
    },
    middle: {
      itemSize: e.itemSize,
      itemGap: e.itemGap,
      itemFontSize: e.itemFontSize
    },
    small: {
      itemSize: e.itemSizeSM,
      itemGap: e.itemGapSM,
      itemFontSize: e.itemFontSizeSM
    }
  }[t];
  return {
    [`&${r}-${t}`]: {
      paddingInlineStart: o.itemSize,
      gap: o.itemGap,
      ...Di({
        ...e,
        ...o
      }),
      ...zi({
        ...e,
        ...o
      })
    }
  };
}, ki = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      display: "flex",
      flexDirection: "column",
      ...ji(e),
      ...ht(e),
      ...ht(e, "large"),
      ...ht(e, "small"),
      [`&${t}-rtl`]: {
        direction: "rtl"
      }
    }
  };
}, Ni = si("ThoughtChain", (e) => {
  const t = Rt(e, {
    // small size tokens
    itemFontSizeSM: e.fontSizeSM,
    itemSizeSM: e.calc(e.controlHeightXS).add(e.controlHeightSM).div(2).equal(),
    itemGapSM: e.marginSM,
    // default size tokens
    itemFontSize: e.fontSize,
    itemSize: e.calc(e.controlHeightSM).add(e.controlHeight).div(2).equal(),
    itemGap: e.margin,
    // large size tokens
    itemFontSizeLG: e.fontSizeLG,
    itemSizeLG: e.calc(e.controlHeight).add(e.controlHeightLG).div(2).equal(),
    itemGapLG: e.marginLG
  });
  return [ki(t), Ai(t)];
}), Fi = (e) => {
  const {
    prefixCls: t,
    rootClassName: r,
    className: o,
    items: n,
    collapsible: i,
    styles: s = {},
    style: a,
    classNames: c = {},
    size: l = "middle",
    ...f
  } = e, u = _r(f, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    getPrefixCls: d,
    direction: h
  } = bt(), g = d(), p = d("thought-chain", t), m = po("thoughtChain"), [S, v, T, y] = $i(i, p, g), [P, b, O] = Ni(p), _ = G(o, r, p, m.className, b, O, {
    [`${p}-rtl`]: h === "rtl"
  }, `${p}-${l}`);
  return P(/* @__PURE__ */ x.createElement("div", fe({}, u, {
    className: _,
    style: {
      ...m.style,
      ...a
    }
  }), /* @__PURE__ */ x.createElement(Wr.Provider, {
    value: {
      prefixCls: p,
      enableCollapse: S,
      collapseMotion: y,
      expandedKeys: v,
      direction: h,
      classNames: {
        itemHeader: G(m.classNames.itemHeader, c.itemHeader),
        itemContent: G(m.classNames.itemContent, c.itemContent),
        itemFooter: G(m.classNames.itemFooter, c.itemFooter)
      },
      styles: {
        itemHeader: {
          ...m.styles.itemHeader,
          ...s.itemHeader
        },
        itemContent: {
          ...m.styles.itemContent,
          ...s.itemContent
        },
        itemFooter: {
          ...m.styles.itemFooter,
          ...s.itemFooter
        }
      }
    }
  }, n == null ? void 0 : n.map((C, I) => {
    var A;
    return /* @__PURE__ */ x.createElement(Ii, {
      key: C.key || `key_${I}`,
      className: G(m.classNames.item, c.item),
      style: {
        ...m.styles.item,
        ...s.item
      },
      info: {
        ...C,
        icon: C.icon || I + 1
      },
      onClick: T,
      nextStatus: ((A = n[I + 1]) == null ? void 0 : A.status) || C.status
    });
  }))));
}, Hi = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Vi(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const o = e[r];
    return t[r] = Bi(r, o), t;
  }, {}) : {};
}
function Bi(e, t) {
  return typeof t == "number" && !Hi.includes(e) ? t + "px" : t;
}
function Pt(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const n = x.Children.toArray(e._reactElement.props.children).map((i) => {
      if (x.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Pt(i.props.el);
        return x.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...x.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return n.originalChildren = e._reactElement.props.children, t.push(pt(x.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: n
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((n) => {
    e.getEventListeners(n).forEach(({
      listener: s,
      type: a,
      useCapture: c
    }) => {
      r.addEventListener(a, s, c);
    });
  });
  const o = Array.from(e.childNodes);
  for (let n = 0; n < o.length; n++) {
    const i = o[n];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Pt(i);
      t.push(...a), r.appendChild(s);
    } else i.nodeType === 3 && r.appendChild(i.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function Gi(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const vr = en(({
  slot: e,
  clone: t,
  className: r,
  style: o,
  observeAttributes: n
}, i) => {
  const s = ee(), [a, c] = tn([]), {
    forceClone: l
  } = an(), f = l ? !0 : t;
  return ge(() => {
    var p;
    if (!s.current || !e)
      return;
    let u = e;
    function d() {
      let m = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (m = u.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), Gi(i, m), r && m.classList.add(...r.split(" ")), o) {
        const S = Vi(o);
        Object.keys(S).forEach((v) => {
          m.style[v] = S[v];
        });
      }
    }
    let h = null, g = null;
    if (f && window.MutationObserver) {
      let m = function() {
        var y, P, b;
        (y = s.current) != null && y.contains(u) && ((P = s.current) == null || P.removeChild(u));
        const {
          portals: v,
          clonedElement: T
        } = Pt(e);
        u = T, c(v), u.style.display = "contents", g && clearTimeout(g), g = setTimeout(() => {
          d();
        }, 50), (b = s.current) == null || b.appendChild(u);
      };
      m();
      const S = Mn(() => {
        m(), h == null || h.disconnect(), h == null || h.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: n
        });
      }, 50);
      h = new window.MutationObserver(S), h.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", d(), (p = s.current) == null || p.appendChild(u);
    return () => {
      var m, S;
      u.style.display = "", (m = s.current) != null && m.contains(u) && ((S = s.current) == null || S.removeChild(u)), h == null || h.disconnect();
    };
  }, [e, f, r, o, i, n, l]), x.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Ui = ({
  children: e,
  ...t
}) => /* @__PURE__ */ q.jsx(q.Fragment, {
  children: e(t)
});
function Xi(e) {
  return x.createElement(Ui, {
    children: e
  });
}
function Kr(e, t, r) {
  const o = e.filter(Boolean);
  if (o.length !== 0)
    return o.map((n, i) => {
      var l, f;
      if (typeof n != "object")
        return t != null && t.fallback ? t.fallback(n) : n;
      const s = t != null && t.itemPropsTransformer ? t == null ? void 0 : t.itemPropsTransformer({
        ...n.props,
        key: ((l = n.props) == null ? void 0 : l.key) ?? (r ? `${r}-${i}` : `${i}`)
      }) : {
        ...n.props,
        key: ((f = n.props) == null ? void 0 : f.key) ?? (r ? `${r}-${i}` : `${i}`)
      };
      let a = s;
      Object.keys(n.slots).forEach((u) => {
        if (!n.slots[u] || !(n.slots[u] instanceof Element) && !n.slots[u].el)
          return;
        const d = u.split(".");
        d.forEach((v, T) => {
          a[v] || (a[v] = {}), T !== d.length - 1 && (a = s[v]);
        });
        const h = n.slots[u];
        let g, p, m = (t == null ? void 0 : t.clone) ?? !1, S = t == null ? void 0 : t.forceClone;
        h instanceof Element ? g = h : (g = h.el, p = h.callback, m = h.clone ?? m, S = h.forceClone ?? S), S = S ?? !!p, a[d[d.length - 1]] = g ? p ? (...v) => (p(d[d.length - 1], v), /* @__PURE__ */ q.jsx(zt, {
          ...n.ctx,
          params: v,
          forceClone: S,
          children: /* @__PURE__ */ q.jsx(vr, {
            slot: g,
            clone: m
          })
        })) : Xi((v) => /* @__PURE__ */ q.jsx(zt, {
          ...n.ctx,
          forceClone: S,
          children: /* @__PURE__ */ q.jsx(vr, {
            ...v,
            slot: g,
            clone: m
          })
        })) : a[d[d.length - 1]], a = s;
      });
      const c = (t == null ? void 0 : t.children) || "children";
      return n[c] ? s[c] = Kr(n[c], t, `${i}`) : t != null && t.children && (s[c] = void 0, Reflect.deleteProperty(s, c)), s;
    });
}
const {
  useItems: Wi,
  withItemsContextProvider: Ki,
  ItemHandler: Yi
} = cn("antdx-thought-chain-items"), Zi = to(Ki(["default", "items"], ({
  children: e,
  items: t,
  ...r
}) => {
  const {
    items: o
  } = Wi(), n = o.items.length > 0 ? o.items : o.default;
  return /* @__PURE__ */ q.jsxs(q.Fragment, {
    children: [/* @__PURE__ */ q.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ q.jsx(Fi, {
      ...r,
      items: rn(() => t || Kr(n, {
        clone: !0
      }), [t, n])
    })]
  });
}));
export {
  Zi as ThoughtChain,
  Zi as default
};
