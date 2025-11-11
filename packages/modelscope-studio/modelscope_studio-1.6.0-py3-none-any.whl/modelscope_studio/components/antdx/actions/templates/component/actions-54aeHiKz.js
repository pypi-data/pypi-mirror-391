import { i as Bt, a as Pe, r as Xt, Z, g as Ft, c as J } from "./Index-CVYNHp-C.js";
const _ = window.ms_globals.React, Lt = window.ms_globals.React.version, Dt = window.ms_globals.React.forwardRef, At = window.ms_globals.React.useRef, Ht = window.ms_globals.React.useState, $t = window.ms_globals.React.useEffect, zt = window.ms_globals.React.useMemo, Oe = window.ms_globals.ReactDOM.createPortal, Vt = window.ms_globals.internalContext.useContextPropsContext, Be = window.ms_globals.internalContext.ContextPropsProvider, Nt = window.ms_globals.createItemsContext.createItemsContext, Ut = window.ms_globals.antd.ConfigProvider, Wt = window.ms_globals.antd.Dropdown, Te = window.ms_globals.antd.theme, Gt = window.ms_globals.antd.Tooltip, Kt = window.ms_globals.antdIcons.EllipsisOutlined, Xe = window.ms_globals.antdCssinjs.unit, ve = window.ms_globals.antdCssinjs.token2CSSVar, Fe = window.ms_globals.antdCssinjs.useStyleRegister, qt = window.ms_globals.antdCssinjs.useCSSVarRegister, Qt = window.ms_globals.antdCssinjs.createTheme, Zt = window.ms_globals.antdCssinjs.useCacheToken;
var Jt = /\s/;
function Yt(t) {
  for (var e = t.length; e-- && Jt.test(t.charAt(e)); )
    ;
  return e;
}
var er = /^\s+/;
function tr(t) {
  return t && t.slice(0, Yt(t) + 1).replace(er, "");
}
var Ve = NaN, rr = /^[-+]0x[0-9a-f]+$/i, nr = /^0b[01]+$/i, or = /^0o[0-7]+$/i, ir = parseInt;
function Ne(t) {
  if (typeof t == "number")
    return t;
  if (Bt(t))
    return Ve;
  if (Pe(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = Pe(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = tr(t);
  var n = nr.test(t);
  return n || or.test(t) ? ir(t.slice(2), n ? 2 : 8) : rr.test(t) ? Ve : +t;
}
var Se = function() {
  return Xt.Date.now();
}, sr = "Expected a function", ar = Math.max, lr = Math.min;
function cr(t, e, n) {
  var o, r, i, s, a, l, c = 0, d = !1, f = !1, u = !0;
  if (typeof t != "function")
    throw new TypeError(sr);
  e = Ne(e) || 0, Pe(n) && (d = !!n.leading, f = "maxWait" in n, i = f ? ar(Ne(n.maxWait) || 0, e) : i, u = "trailing" in n ? !!n.trailing : u);
  function g(h) {
    var S = o, w = r;
    return o = r = void 0, c = h, s = t.apply(w, S), s;
  }
  function b(h) {
    return c = h, a = setTimeout(y, e), d ? g(h) : s;
  }
  function x(h) {
    var S = h - l, w = h - c, T = e - S;
    return f ? lr(T, i - w) : T;
  }
  function p(h) {
    var S = h - l, w = h - c;
    return l === void 0 || S >= e || S < 0 || f && w >= i;
  }
  function y() {
    var h = Se();
    if (p(h))
      return v(h);
    a = setTimeout(y, x(h));
  }
  function v(h) {
    return a = void 0, u && o ? g(h) : (o = r = void 0, s);
  }
  function M() {
    a !== void 0 && clearTimeout(a), c = 0, o = l = r = a = void 0;
  }
  function m() {
    return a === void 0 ? s : v(Se());
  }
  function O() {
    var h = Se(), S = p(h);
    if (o = arguments, r = this, l = h, S) {
      if (a === void 0)
        return b(l);
      if (f)
        return clearTimeout(a), a = setTimeout(y, e), g(l);
    }
    return a === void 0 && (a = setTimeout(y, e)), s;
  }
  return O.cancel = M, O.flush = m, O;
}
var ut = {
  exports: {}
}, ie = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ur = _, fr = Symbol.for("react.element"), dr = Symbol.for("react.fragment"), hr = Object.prototype.hasOwnProperty, gr = ur.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, pr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ft(t, e, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), e.key !== void 0 && (i = "" + e.key), e.ref !== void 0 && (s = e.ref);
  for (o in e) hr.call(e, o) && !pr.hasOwnProperty(o) && (r[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) r[o] === void 0 && (r[o] = e[o]);
  return {
    $$typeof: fr,
    type: t,
    key: i,
    ref: s,
    props: r,
    _owner: gr.current
  };
}
ie.Fragment = dr;
ie.jsx = ft;
ie.jsxs = ft;
ut.exports = ie;
var H = ut.exports;
const {
  SvelteComponent: mr,
  assign: Ue,
  binding_callbacks: We,
  check_outros: br,
  children: dt,
  claim_element: ht,
  claim_space: yr,
  component_subscribe: Ge,
  compute_slots: vr,
  create_slot: Sr,
  detach: V,
  element: gt,
  empty: Ke,
  exclude_internal_props: qe,
  get_all_dirty_from_scope: xr,
  get_slot_changes: Cr,
  group_outros: _r,
  init: wr,
  insert_hydration: Y,
  safe_not_equal: Or,
  set_custom_element_data: pt,
  space: Pr,
  transition_in: ee,
  transition_out: Me,
  update_slot_base: Tr
} = window.__gradio__svelte__internal, {
  beforeUpdate: Mr,
  getContext: Er,
  onDestroy: jr,
  setContext: Ir
} = window.__gradio__svelte__internal;
function Qe(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), r = Sr(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = gt("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      e = ht(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = dt(e);
      r && r.l(s), s.forEach(V), this.h();
    },
    h() {
      pt(e, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      Y(i, e, s), r && r.m(e, null), t[9](e), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && Tr(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? Cr(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : xr(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (ee(r, i), n = !0);
    },
    o(i) {
      Me(r, i), n = !1;
    },
    d(i) {
      i && V(e), r && r.d(i), t[9](null);
    }
  };
}
function kr(t) {
  let e, n, o, r, i = (
    /*$$slots*/
    t[4].default && Qe(t)
  );
  return {
    c() {
      e = gt("react-portal-target"), n = Pr(), i && i.c(), o = Ke(), this.h();
    },
    l(s) {
      e = ht(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), dt(e).forEach(V), n = yr(s), i && i.l(s), o = Ke(), this.h();
    },
    h() {
      pt(e, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      Y(s, e, a), t[8](e), Y(s, n, a), i && i.m(s, a), Y(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && ee(i, 1)) : (i = Qe(s), i.c(), ee(i, 1), i.m(o.parentNode, o)) : i && (_r(), Me(i, 1, 1, () => {
        i = null;
      }), br());
    },
    i(s) {
      r || (ee(i), r = !0);
    },
    o(s) {
      Me(i), r = !1;
    },
    d(s) {
      s && (V(e), V(n), V(o)), t[8](null), i && i.d(s);
    }
  };
}
function Ze(t) {
  const {
    svelteInit: e,
    ...n
  } = t;
  return n;
}
function Rr(t, e, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = e;
  const a = vr(i);
  let {
    svelteInit: l
  } = e;
  const c = Z(Ze(e)), d = Z();
  Ge(t, d, (m) => n(0, o = m));
  const f = Z();
  Ge(t, f, (m) => n(1, r = m));
  const u = [], g = Er("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: x,
    subSlotIndex: p
  } = Ft() || {}, y = l({
    parent: g,
    props: c,
    target: d,
    slot: f,
    slotKey: b,
    slotIndex: x,
    subSlotIndex: p,
    onDestroy(m) {
      u.push(m);
    }
  });
  Ir("$$ms-gr-react-wrapper", y), Mr(() => {
    c.set(Ze(e));
  }), jr(() => {
    u.forEach((m) => m());
  });
  function v(m) {
    We[m ? "unshift" : "push"](() => {
      o = m, d.set(o);
    });
  }
  function M(m) {
    We[m ? "unshift" : "push"](() => {
      r = m, f.set(r);
    });
  }
  return t.$$set = (m) => {
    n(17, e = Ue(Ue({}, e), qe(m))), "svelteInit" in m && n(5, l = m.svelteInit), "$$scope" in m && n(6, s = m.$$scope);
  }, e = qe(e), [o, r, d, f, a, l, s, i, v, M];
}
class Lr extends mr {
  constructor(e) {
    super(), wr(this, e, Rr, kr, Or, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Fn
} = window.__gradio__svelte__internal, Je = window.ms_globals.rerender, xe = window.ms_globals.tree;
function Dr(t, e = {}) {
  function n(o) {
    const r = Z(), i = new Lr({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: t,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: e.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, l = s.parent ?? xe;
          return l.nodes = [...l.nodes, a], Je({
            createPortal: Oe,
            node: xe
          }), s.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== r), Je({
              createPortal: Oe,
              node: xe
            });
          }), a;
        },
        ...o.props
      }
    });
    return r.set(i), i;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((r) => {
      window.ms_globals.initialize = () => {
        r();
      };
    })), window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
const Ar = "1.6.1";
function re() {
  return re = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, re.apply(null, arguments);
}
function G(t) {
  "@babel/helpers - typeof";
  return G = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, G(t);
}
function Hr(t, e) {
  if (G(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (G(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function $r(t) {
  var e = Hr(t, "string");
  return G(e) == "symbol" ? e : e + "";
}
function zr(t, e, n) {
  return (e = $r(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function Ye(t, e) {
  var n = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(t, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function Br(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? Ye(Object(n), !0).forEach(function(o) {
      zr(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : Ye(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
var Xr = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, Fr = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Vr = "".concat(Xr, " ").concat(Fr).split(/[\s\n]+/), Nr = "aria-", Ur = "data-";
function et(t, e) {
  return t.indexOf(e) === 0;
}
function Wr(t) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  e === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : e === !0 ? n = {
    aria: !0
  } : n = Br({}, e);
  var o = {};
  return Object.keys(t).forEach(function(r) {
    // Aria
    (n.aria && (r === "role" || et(r, Nr)) || // Data
    n.data && et(r, Ur) || // Attr
    n.attr && Vr.includes(r)) && (o[r] = t[r]);
  }), o;
}
const Gr = /* @__PURE__ */ _.createContext({}), Kr = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, qr = (t) => {
  const e = _.useContext(Gr);
  return _.useMemo(() => ({
    ...Kr,
    ...e[t]
  }), [e[t]]);
};
function ne() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = _.useContext(Ut.ConfigContext);
  return {
    theme: r,
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o
  };
}
const U = (t, e) => {
  const n = t[0];
  for (const o of e)
    if (o.key === n) {
      if (t.length === 1) return o;
      if ("children" in o)
        return U(t.slice(1), o.children);
    }
  return null;
}, Qr = (t) => {
  const {
    onClick: e,
    item: n
  } = t, {
    children: o = [],
    triggerSubMenuAction: r = "hover"
  } = n, {
    getPrefixCls: i
  } = ne(), s = i("actions", t.prefixCls), a = (n == null ? void 0 : n.icon) ?? /* @__PURE__ */ _.createElement(Kt, null), l = {
    items: o,
    onClick: ({
      key: c,
      keyPath: d,
      domEvent: f
    }) => {
      var u, g, b;
      if ((u = U(d, o)) != null && u.onItemClick) {
        (b = (g = U(d, o)) == null ? void 0 : g.onItemClick) == null || b.call(g, U(d, o));
        return;
      }
      e == null || e({
        key: c,
        keyPath: [...d, n.key],
        domEvent: f,
        item: U(d, o)
      });
    }
  };
  return /* @__PURE__ */ _.createElement(Wt, {
    menu: l,
    overlayClassName: `${s}-sub-item`,
    arrow: !0,
    trigger: [r]
  }, /* @__PURE__ */ _.createElement("div", {
    className: `${s}-list-item`
  }, /* @__PURE__ */ _.createElement("div", {
    className: `${s}-list-item-icon`
  }, a)));
};
function D(t) {
  "@babel/helpers - typeof";
  return D = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, D(t);
}
function Zr(t) {
  if (Array.isArray(t)) return t;
}
function Jr(t, e) {
  var n = t == null ? null : typeof Symbol < "u" && t[Symbol.iterator] || t["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], l = !0, c = !1;
    try {
      if (i = (n = n.call(t)).next, e === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = i.call(n)).done) && (a.push(o.value), a.length !== e); l = !0) ;
    } catch (d) {
      c = !0, r = d;
    } finally {
      try {
        if (!l && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (c) throw r;
      }
    }
    return a;
  }
}
function tt(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var n = 0, o = Array(e); n < e; n++) o[n] = t[n];
  return o;
}
function Yr(t, e) {
  if (t) {
    if (typeof t == "string") return tt(t, e);
    var n = {}.toString.call(t).slice(8, -1);
    return n === "Object" && t.constructor && (n = t.constructor.name), n === "Map" || n === "Set" ? Array.from(t) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? tt(t, e) : void 0;
  }
}
function en() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function te(t, e) {
  return Zr(t) || Jr(t, e) || Yr(t, e) || en();
}
function tn(t, e) {
  if (D(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (D(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function mt(t) {
  var e = tn(t, "string");
  return D(e) == "symbol" ? e : e + "";
}
function P(t, e, n) {
  return (e = mt(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function rt(t, e) {
  var n = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(t, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function I(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? rt(Object(n), !0).forEach(function(o) {
      P(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : rt(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
function se(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function rn(t, e) {
  for (var n = 0; n < e.length; n++) {
    var o = e[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, mt(o.key), o);
  }
}
function ae(t, e, n) {
  return e && rn(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function W(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function Ee(t, e) {
  return Ee = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Ee(t, e);
}
function bt(t, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  t.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: t,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(t, "prototype", {
    writable: !1
  }), e && Ee(t, e);
}
function oe(t) {
  return oe = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, oe(t);
}
function yt() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (yt = function() {
    return !!t;
  })();
}
function nn(t, e) {
  if (e && (D(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return W(t);
}
function vt(t) {
  var e = yt();
  return function() {
    var n, o = oe(t);
    if (e) {
      var r = oe(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return nn(this, n);
  };
}
var St = /* @__PURE__ */ ae(function t() {
  se(this, t);
}), xt = "CALC_UNIT", on = new RegExp(xt, "g");
function Ce(t) {
  return typeof t == "number" ? "".concat(t).concat(xt) : t;
}
var sn = /* @__PURE__ */ function(t) {
  bt(n, t);
  var e = vt(n);
  function n(o, r) {
    var i;
    se(this, n), i = e.call(this), P(W(i), "result", ""), P(W(i), "unitlessCssVar", void 0), P(W(i), "lowPriority", void 0);
    var s = D(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = Ce(o) : s === "string" && (i.result = o), i;
  }
  return ae(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(Ce(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(Ce(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " * ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " * ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " / ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " / ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(r) {
      return this.lowPriority || r ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(r) {
      var i = this, s = r || {}, a = s.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(c) {
        return i.result.includes(c);
      }) && (l = !1), this.result = this.result.replace(on, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(St), an = /* @__PURE__ */ function(t) {
  bt(n, t);
  var e = vt(n);
  function n(o) {
    var r;
    return se(this, n), r = e.call(this), P(W(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return ae(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result += r.result : typeof r == "number" && (this.result += r), this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result -= r.result : typeof r == "number" && (this.result -= r), this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return r instanceof n ? this.result *= r.result : typeof r == "number" && (this.result *= r), this;
    }
  }, {
    key: "div",
    value: function(r) {
      return r instanceof n ? this.result /= r.result : typeof r == "number" && (this.result /= r), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), n;
}(St), ln = function(e, n) {
  var o = e === "css" ? sn : an;
  return function(r) {
    return new o(r, n);
  };
}, nt = function(e, n) {
  return "".concat([n, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
}, C = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ke = Symbol.for("react.element"), Re = Symbol.for("react.portal"), le = Symbol.for("react.fragment"), ce = Symbol.for("react.strict_mode"), ue = Symbol.for("react.profiler"), fe = Symbol.for("react.provider"), de = Symbol.for("react.context"), cn = Symbol.for("react.server_context"), he = Symbol.for("react.forward_ref"), ge = Symbol.for("react.suspense"), pe = Symbol.for("react.suspense_list"), me = Symbol.for("react.memo"), be = Symbol.for("react.lazy"), un = Symbol.for("react.offscreen"), Ct;
Ct = Symbol.for("react.module.reference");
function L(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case ke:
        switch (t = t.type, t) {
          case le:
          case ue:
          case ce:
          case ge:
          case pe:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case cn:
              case de:
              case he:
              case be:
              case me:
              case fe:
                return t;
              default:
                return e;
            }
        }
      case Re:
        return e;
    }
  }
}
C.ContextConsumer = de;
C.ContextProvider = fe;
C.Element = ke;
C.ForwardRef = he;
C.Fragment = le;
C.Lazy = be;
C.Memo = me;
C.Portal = Re;
C.Profiler = ue;
C.StrictMode = ce;
C.Suspense = ge;
C.SuspenseList = pe;
C.isAsyncMode = function() {
  return !1;
};
C.isConcurrentMode = function() {
  return !1;
};
C.isContextConsumer = function(t) {
  return L(t) === de;
};
C.isContextProvider = function(t) {
  return L(t) === fe;
};
C.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === ke;
};
C.isForwardRef = function(t) {
  return L(t) === he;
};
C.isFragment = function(t) {
  return L(t) === le;
};
C.isLazy = function(t) {
  return L(t) === be;
};
C.isMemo = function(t) {
  return L(t) === me;
};
C.isPortal = function(t) {
  return L(t) === Re;
};
C.isProfiler = function(t) {
  return L(t) === ue;
};
C.isStrictMode = function(t) {
  return L(t) === ce;
};
C.isSuspense = function(t) {
  return L(t) === ge;
};
C.isSuspenseList = function(t) {
  return L(t) === pe;
};
C.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === le || t === ue || t === ce || t === ge || t === pe || t === un || typeof t == "object" && t !== null && (t.$$typeof === be || t.$$typeof === me || t.$$typeof === fe || t.$$typeof === de || t.$$typeof === he || t.$$typeof === Ct || t.getModuleId !== void 0);
};
C.typeOf = L;
Number(Lt.split(".")[0]);
function ot(t, e, n, o) {
  var r = I({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var l = te(a, 2), c = l[0], d = l[1];
      if (r != null && r[c] || r != null && r[d]) {
        var f;
        (f = r[d]) !== null && f !== void 0 || (r[d] = r == null ? void 0 : r[c]);
      }
    });
  }
  var s = I(I({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === e[a] && delete s[a];
  }), s;
}
var _t = typeof CSSINJS_STATISTIC < "u", je = !0;
function Le() {
  for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
    e[n] = arguments[n];
  if (!_t)
    return Object.assign.apply(Object, [{}].concat(e));
  je = !1;
  var o = {};
  return e.forEach(function(r) {
    if (D(r) === "object") {
      var i = Object.keys(r);
      i.forEach(function(s) {
        Object.defineProperty(o, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return r[s];
          }
        });
      });
    }
  }), je = !0, o;
}
var it = {};
function fn() {
}
var dn = function(e) {
  var n, o = e, r = fn;
  return _t && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(s, a) {
      if (je) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var l;
    it[s] = {
      global: Array.from(n),
      component: I(I({}, (l = it[s]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function st(t, e, n) {
  if (typeof n == "function") {
    var o;
    return n(Le(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function hn(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return Xe(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return Xe(i);
      }).join(","), ")");
    }
  };
}
var gn = 1e3 * 60 * 10, pn = /* @__PURE__ */ function() {
  function t() {
    se(this, t), P(this, "map", /* @__PURE__ */ new Map()), P(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), P(this, "nextID", 0), P(this, "lastAccessBeat", /* @__PURE__ */ new Map()), P(this, "accessBeat", 0);
  }
  return ae(t, [{
    key: "set",
    value: function(n, o) {
      this.clear();
      var r = this.getCompositeKey(n);
      this.map.set(r, o), this.lastAccessBeat.set(r, Date.now());
    }
  }, {
    key: "get",
    value: function(n) {
      var o = this.getCompositeKey(n), r = this.map.get(o);
      return this.lastAccessBeat.set(o, Date.now()), this.accessBeat += 1, r;
    }
  }, {
    key: "getCompositeKey",
    value: function(n) {
      var o = this, r = n.map(function(i) {
        return i && D(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(D(i), "_").concat(i);
      });
      return r.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(n) {
      if (this.objectIDMap.has(n))
        return this.objectIDMap.get(n);
      var o = this.nextID;
      return this.objectIDMap.set(n, o), this.nextID += 1, o;
    }
  }, {
    key: "clear",
    value: function() {
      var n = this;
      if (this.accessBeat > 1e4) {
        var o = Date.now();
        this.lastAccessBeat.forEach(function(r, i) {
          o - r > gn && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), at = new pn();
function mn(t, e) {
  return _.useMemo(function() {
    var n = at.get(e);
    if (n)
      return n;
    var o = t();
    return at.set(e, o), o;
  }, e);
}
var bn = function() {
  return {};
};
function yn(t) {
  var e = t.useCSP, n = e === void 0 ? bn : e, o = t.useToken, r = t.usePrefix, i = t.getResetStyles, s = t.getCommonStyle, a = t.getCompUnitless;
  function l(u, g, b, x) {
    var p = Array.isArray(u) ? u[0] : u;
    function y(w) {
      return "".concat(String(p)).concat(w.slice(0, 1).toUpperCase()).concat(w.slice(1));
    }
    var v = (x == null ? void 0 : x.unitless) || {}, M = typeof a == "function" ? a(u) : {}, m = I(I({}, M), {}, P({}, y("zIndexPopup"), !0));
    Object.keys(v).forEach(function(w) {
      m[y(w)] = v[w];
    });
    var O = I(I({}, x), {}, {
      unitless: m,
      prefixToken: y
    }), h = d(u, g, b, O), S = c(p, b, O);
    return function(w) {
      var T = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : w, k = h(w, T), z = te(k, 2), j = z[1], B = S(T), R = te(B, 2), A = R[0], K = R[1];
      return [A, j, K];
    };
  }
  function c(u, g, b) {
    var x = b.unitless, p = b.injectStyle, y = p === void 0 ? !0 : p, v = b.prefixToken, M = b.ignore, m = function(S) {
      var w = S.rootCls, T = S.cssVar, k = T === void 0 ? {} : T, z = o(), j = z.realToken;
      return qt({
        path: [u],
        prefix: k.prefix,
        key: k.key,
        unitless: x,
        ignore: M,
        token: j,
        scope: w
      }, function() {
        var B = st(u, j, g), R = ot(u, j, B, {
          deprecatedTokens: b == null ? void 0 : b.deprecatedTokens
        });
        return Object.keys(B).forEach(function(A) {
          R[v(A)] = R[A], delete R[A];
        }), R;
      }), null;
    }, O = function(S) {
      var w = o(), T = w.cssVar;
      return [function(k) {
        return y && T ? /* @__PURE__ */ _.createElement(_.Fragment, null, /* @__PURE__ */ _.createElement(m, {
          rootCls: S,
          cssVar: T,
          component: u
        }), k) : k;
      }, T == null ? void 0 : T.key];
    };
    return O;
  }
  function d(u, g, b) {
    var x = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = Array.isArray(u) ? u : [u, u], y = te(p, 1), v = y[0], M = p.join("-"), m = t.layer || {
      name: "antd"
    };
    return function(O) {
      var h = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : O, S = o(), w = S.theme, T = S.realToken, k = S.hashId, z = S.token, j = S.cssVar, B = r(), R = B.rootPrefixCls, A = B.iconPrefixCls, K = n(), ye = j ? "css" : "js", Pt = mn(function() {
        var X = /* @__PURE__ */ new Set();
        return j && Object.keys(x.unitless || {}).forEach(function(q) {
          X.add(ve(q, j.prefix)), X.add(ve(q, nt(v, j.prefix)));
        }), ln(ye, X);
      }, [ye, v, j == null ? void 0 : j.prefix]), De = hn(ye), Tt = De.max, Mt = De.min, Ae = {
        theme: w,
        token: z,
        hashId: k,
        nonce: function() {
          return K.nonce;
        },
        clientOnly: x.clientOnly,
        layer: m,
        // antd is always at top of styles
        order: x.order || -999
      };
      typeof i == "function" && Fe(I(I({}, Ae), {}, {
        clientOnly: !1,
        path: ["Shared", R]
      }), function() {
        return i(z, {
          prefix: {
            rootPrefixCls: R,
            iconPrefixCls: A
          },
          csp: K
        });
      });
      var Et = Fe(I(I({}, Ae), {}, {
        path: [M, O, A]
      }), function() {
        if (x.injectStyle === !1)
          return [];
        var X = dn(z), q = X.token, jt = X.flush, F = st(v, T, b), It = ".".concat(O), He = ot(v, T, F, {
          deprecatedTokens: x.deprecatedTokens
        });
        j && F && D(F) === "object" && Object.keys(F).forEach(function(ze) {
          F[ze] = "var(".concat(ve(ze, nt(v, j.prefix)), ")");
        });
        var $e = Le(q, {
          componentCls: It,
          prefixCls: O,
          iconCls: ".".concat(A),
          antCls: ".".concat(R),
          calc: Pt,
          // @ts-ignore
          max: Tt,
          // @ts-ignore
          min: Mt
        }, j ? F : He), kt = g($e, {
          hashId: k,
          prefixCls: O,
          rootPrefixCls: R,
          iconPrefixCls: A
        });
        jt(v, He);
        var Rt = typeof s == "function" ? s($e, O, h, x.resetFont) : null;
        return [x.resetStyle === !1 ? null : Rt, kt];
      });
      return [Et, k];
    };
  }
  function f(u, g, b) {
    var x = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = d(u, g, b, I({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, x)), y = function(M) {
      var m = M.prefixCls, O = M.rootCls, h = O === void 0 ? m : O;
      return p(m, h), null;
    };
    return y;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: f,
    genComponentStyleHook: d
  };
}
const vn = {
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
}, Sn = Object.assign(Object.assign({}, vn), {
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
}), E = Math.round;
function _e(t, e) {
  const n = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = e(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const lt = (t, e, n) => n === 0 ? t : t / 100;
function N(t, e) {
  const n = e || 255;
  return t > n ? n : t < 0 ? 0 : t;
}
class $ {
  constructor(e) {
    P(this, "isValid", !0), P(this, "r", 0), P(this, "g", 0), P(this, "b", 0), P(this, "a", 1), P(this, "_h", void 0), P(this, "_s", void 0), P(this, "_l", void 0), P(this, "_v", void 0), P(this, "_max", void 0), P(this, "_min", void 0), P(this, "_brightness", void 0);
    function n(o) {
      return o[0] in e && o[1] in e && o[2] in e;
    }
    if (e) if (typeof e == "string") {
      let r = function(i) {
        return o.startsWith(i);
      };
      const o = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (e instanceof $)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (n("rgb"))
      this.r = N(e.r), this.g = N(e.g), this.b = N(e.b), this.a = typeof e.a == "number" ? N(e.a, 1) : 1;
    else if (n("hsl"))
      this.fromHsl(e);
    else if (n("hsv"))
      this.fromHsv(e);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(e));
  }
  // ======================= Setter =======================
  setR(e) {
    return this._sc("r", e);
  }
  setG(e) {
    return this._sc("g", e);
  }
  setB(e) {
    return this._sc("b", e);
  }
  setA(e) {
    return this._sc("a", e, 1);
  }
  setHue(e) {
    const n = this.toHsv();
    return n.h = e, this._c(n);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function e(i) {
      const s = i / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    }
    const n = e(this.r), o = e(this.g), r = e(this.b);
    return 0.2126 * n + 0.7152 * o + 0.0722 * r;
  }
  getHue() {
    if (typeof this._h > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._h = 0 : this._h = E(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._s = 0 : this._s = e / this.getMax();
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
  darken(e = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() - e / 100;
    return r < 0 && (r = 0), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  lighten(e = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() + e / 100;
    return r > 1 && (r = 1), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(e, n = 50) {
    const o = this._c(e), r = n / 100, i = (a) => (o[a] - this[a]) * r + this[a], s = {
      r: E(i("r")),
      g: E(i("g")),
      b: E(i("b")),
      a: E(i("a") * 100) / 100
    };
    return this._c(s);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(e = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, e);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(e = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, e);
  }
  onBackground(e) {
    const n = this._c(e), o = this.a + n.a * (1 - this.a), r = (i) => E((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
    return this._c({
      r: r("r"),
      g: r("g"),
      b: r("b"),
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
  equals(e) {
    return this.r === e.r && this.g === e.g && this.b === e.b && this.a === e.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let e = "#";
    const n = (this.r || 0).toString(16);
    e += n.length === 2 ? n : "0" + n;
    const o = (this.g || 0).toString(16);
    e += o.length === 2 ? o : "0" + o;
    const r = (this.b || 0).toString(16);
    if (e += r.length === 2 ? r : "0" + r, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = E(this.a * 255).toString(16);
      e += i.length === 2 ? i : "0" + i;
    }
    return e;
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
    const e = this.getHue(), n = E(this.getSaturation() * 100), o = E(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${e},${n}%,${o}%,${this.a})` : `hsl(${e},${n}%,${o}%)`;
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
  _sc(e, n, o) {
    const r = this.clone();
    return r[e] = N(n, o), r;
  }
  _c(e) {
    return new this.constructor(e);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(e) {
    const n = e.replace("#", "");
    function o(r, i) {
      return parseInt(n[r] + n[i || r], 16);
    }
    n.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = n[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = n[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: e,
    s: n,
    l: o,
    a: r
  }) {
    if (this._h = e % 360, this._s = n, this._l = o, this.a = typeof r == "number" ? r : 1, n <= 0) {
      const u = E(o * 255);
      this.r = u, this.g = u, this.b = u;
    }
    let i = 0, s = 0, a = 0;
    const l = e / 60, c = (1 - Math.abs(2 * o - 1)) * n, d = c * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (i = c, s = d) : l >= 1 && l < 2 ? (i = d, s = c) : l >= 2 && l < 3 ? (s = c, a = d) : l >= 3 && l < 4 ? (s = d, a = c) : l >= 4 && l < 5 ? (i = d, a = c) : l >= 5 && l < 6 && (i = c, a = d);
    const f = o - c / 2;
    this.r = E((i + f) * 255), this.g = E((s + f) * 255), this.b = E((a + f) * 255);
  }
  fromHsv({
    h: e,
    s: n,
    v: o,
    a: r
  }) {
    this._h = e % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = E(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = e / 60, a = Math.floor(s), l = s - a, c = E(o * (1 - n) * 255), d = E(o * (1 - n * l) * 255), f = E(o * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = f, this.b = c;
        break;
      case 1:
        this.r = d, this.b = c;
        break;
      case 2:
        this.r = c, this.b = f;
        break;
      case 3:
        this.r = c, this.g = d;
        break;
      case 4:
        this.r = f, this.g = c;
        break;
      case 5:
      default:
        this.g = c, this.b = d;
        break;
    }
  }
  fromHsvString(e) {
    const n = _e(e, lt);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(e) {
    const n = _e(e, lt);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(e) {
    const n = _e(e, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? E(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function we(t) {
  return t >= 0 && t <= 255;
}
function Q(t, e) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new $(t).toRgb();
  if (i < 1)
    return t;
  const {
    r: s,
    g: a,
    b: l
  } = new $(e).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const d = Math.round((n - s * (1 - c)) / c), f = Math.round((o - a * (1 - c)) / c), u = Math.round((r - l * (1 - c)) / c);
    if (we(d) && we(f) && we(u))
      return new $({
        r: d,
        g: f,
        b: u,
        a: Math.round(c * 100) / 100
      }).toRgbString();
  }
  return new $({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var xn = function(t, e) {
  var n = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (n[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(t); r < o.length; r++)
    e.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[r]) && (n[o[r]] = t[o[r]]);
  return n;
};
function Cn(t) {
  const {
    override: e
  } = t, n = xn(t, ["override"]), o = Object.assign({}, e);
  Object.keys(Sn).forEach((u) => {
    delete o[u];
  });
  const r = Object.assign(Object.assign({}, n), o), i = 480, s = 576, a = 768, l = 992, c = 1200, d = 1600;
  if (r.motion === !1) {
    const u = "0s";
    r.motionDurationFast = u, r.motionDurationMid = u, r.motionDurationSlow = u;
  }
  return Object.assign(Object.assign(Object.assign({}, r), {
    // ============== Background ============== //
    colorFillContent: r.colorFillSecondary,
    colorFillContentHover: r.colorFill,
    colorFillAlter: r.colorFillQuaternary,
    colorBgContainerDisabled: r.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: r.colorBgContainer,
    colorSplit: Q(r.colorBorderSecondary, r.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: r.colorTextQuaternary,
    colorTextDisabled: r.colorTextQuaternary,
    colorTextHeading: r.colorText,
    colorTextLabel: r.colorTextSecondary,
    colorTextDescription: r.colorTextTertiary,
    colorTextLightSolid: r.colorWhite,
    colorHighlight: r.colorError,
    colorBgTextHover: r.colorFillSecondary,
    colorBgTextActive: r.colorFill,
    colorIcon: r.colorTextTertiary,
    colorIconHover: r.colorText,
    colorErrorOutline: Q(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: Q(r.colorWarningBg, r.colorBgContainer),
    // Font
    fontSizeIcon: r.fontSizeSM,
    // Line
    lineWidthFocus: r.lineWidth * 3,
    // Control
    lineWidth: r.lineWidth,
    controlOutlineWidth: r.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: r.controlHeight / 2,
    controlItemBgHover: r.colorFillTertiary,
    controlItemBgActive: r.colorPrimaryBg,
    controlItemBgActiveHover: r.colorPrimaryBgHover,
    controlItemBgActiveDisabled: r.colorFill,
    controlTmpOutline: r.colorFillQuaternary,
    controlOutline: Q(r.colorPrimaryBg, r.colorBgContainer),
    lineType: r.lineType,
    borderRadius: r.borderRadius,
    borderRadiusXS: r.borderRadiusXS,
    borderRadiusSM: r.borderRadiusSM,
    borderRadiusLG: r.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: r.sizeXXS,
    paddingXS: r.sizeXS,
    paddingSM: r.sizeSM,
    padding: r.size,
    paddingMD: r.sizeMD,
    paddingLG: r.sizeLG,
    paddingXL: r.sizeXL,
    paddingContentHorizontalLG: r.sizeLG,
    paddingContentVerticalLG: r.sizeMS,
    paddingContentHorizontal: r.sizeMS,
    paddingContentVertical: r.sizeSM,
    paddingContentHorizontalSM: r.size,
    paddingContentVerticalSM: r.sizeXS,
    marginXXS: r.sizeXXS,
    marginXS: r.sizeXS,
    marginSM: r.sizeSM,
    margin: r.size,
    marginMD: r.sizeMD,
    marginLG: r.sizeLG,
    marginXL: r.sizeXL,
    marginXXL: r.sizeXXL,
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
      0 1px 2px -2px ${new $("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new $("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new $("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const _n = {
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
}, wn = {
  motionBase: !0,
  motionUnit: !0
}, On = Qt(Te.defaultAlgorithm), Pn = {
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
}, wt = (t, e, n) => {
  const o = n.getDerivativeToken(t), {
    override: r,
    ...i
  } = e;
  let s = {
    ...o,
    override: r
  };
  return s = Cn(s), i && Object.entries(i).forEach(([a, l]) => {
    const {
      theme: c,
      ...d
    } = l;
    let f = d;
    c && (f = wt({
      ...s,
      ...d
    }, {
      override: d
    }, c)), s[a] = f;
  }), s;
};
function Tn() {
  const {
    token: t,
    hashed: e,
    theme: n = On,
    override: o,
    cssVar: r
  } = _.useContext(Te._internalContext), [i, s, a] = Zt(n, [Te.defaultSeed, t], {
    salt: `${Ar}-${e || ""}`,
    override: o,
    getComputedToken: wt,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: _n,
      ignore: wn,
      preserve: Pn
    }
  });
  return [n, a, e ? s : "", i, r];
}
const {
  genStyleHooks: Mn
} = yn({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = ne();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, n, o, r] = Tn();
    return {
      theme: t,
      realToken: e,
      hashId: n,
      token: o,
      cssVar: r
    };
  },
  useCSP: () => {
    const {
      csp: t
    } = ne();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), En = (t) => {
  const {
    componentCls: e,
    calc: n
  } = t;
  return {
    [e]: {
      [`&${e}-rtl`]: {
        direction: "rtl"
      },
      [`${e}-list`]: {
        display: "inline-flex",
        flexDirection: "row",
        gap: t.paddingXS,
        color: t.colorTextDescription,
        "&-item, &-sub-item": {
          cursor: "pointer",
          padding: t.paddingXXS,
          borderRadius: t.borderRadius,
          height: t.controlHeightSM,
          width: t.controlHeightSM,
          boxSizing: "border-box",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          "&-icon": {
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: t.fontSize,
            width: "100%",
            height: "100%"
          },
          "&:hover": {
            background: t.colorBgTextHover
          }
        }
      },
      "& .border": {
        padding: `${t.paddingXS} ${t.paddingSM}`,
        gap: t.paddingSM,
        borderRadius: n(t.borderRadiusLG).mul(1.5).equal(),
        backgroundColor: t.colorBorderSecondary,
        color: t.colorTextSecondary,
        [`${e}-list-item, ${e}-list-sub-item`]: {
          padding: 0,
          lineHeight: t.lineHeight,
          "&-icon": {
            fontSize: t.fontSizeLG
          },
          "&:hover": {
            opacity: 0.8
          }
        }
      },
      "& .block": {
        display: "flex"
      }
    }
  };
}, jn = () => ({}), In = Mn("Actions", (t) => {
  const e = Le(t, {});
  return [En(e)];
}, jn), kn = (t) => {
  const {
    prefixCls: e,
    rootClassName: n = {},
    style: o = {},
    variant: r = "borderless",
    block: i = !1,
    onClick: s,
    items: a = [],
    ...l
  } = t, c = Wr(l, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    getPrefixCls: d,
    direction: f
  } = ne(), u = d("actions", e), g = qr("actions"), [b, x, p] = In(u), y = J(u, g.className, n, p, x, {
    [`${u}-rtl`]: f === "rtl"
  }), v = {
    ...g.style,
    ...o
  }, M = (h, S, w) => S ? /* @__PURE__ */ _.createElement(Gt, re({}, w, {
    title: S
  }), h) : h, m = (h, S, w) => {
    if (S.onItemClick) {
      S.onItemClick(S);
      return;
    }
    s == null || s({
      key: h,
      item: S,
      keyPath: [h],
      domEvent: w
    });
  }, O = (h) => {
    const {
      icon: S,
      label: w,
      key: T
    } = h;
    return /* @__PURE__ */ _.createElement("div", {
      className: J(`${u}-list-item`),
      onClick: (k) => m(T, h, k),
      key: T
    }, M(/* @__PURE__ */ _.createElement("div", {
      className: `${u}-list-item-icon`
    }, S), w));
  };
  return b(/* @__PURE__ */ _.createElement("div", re({
    className: y
  }, c, {
    style: v
  }), /* @__PURE__ */ _.createElement("div", {
    className: J(`${u}-list`, r, i)
  }, a.map((h) => "children" in h ? /* @__PURE__ */ _.createElement(Qr, {
    key: h.key,
    item: h,
    prefixCls: u,
    onClick: s
  }) : O(h)))));
}, Rn = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ln(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = Dn(n, o), e;
  }, {}) : {};
}
function Dn(t, e) {
  return typeof e == "number" && !Rn.includes(t) ? e + "px" : e;
}
function Ie(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const r = _.Children.toArray(t._reactElement.props.children).map((i) => {
      if (_.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Ie(i.props.el);
        return _.cloneElement(i, {
          ...i.props,
          el: a,
          children: [..._.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(Oe(_.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: r
    }), n)), {
      clonedElement: n,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((r) => {
    t.getEventListeners(r).forEach(({
      listener: s,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, s, l);
    });
  });
  const o = Array.from(t.childNodes);
  for (let r = 0; r < o.length; r++) {
    const i = o[r];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Ie(i);
      e.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function An(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const ct = Dt(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = At(), [a, l] = Ht([]), {
    forceClone: c
  } = Vt(), d = c ? !0 : e;
  return $t(() => {
    var x;
    if (!s.current || !t)
      return;
    let f = t;
    function u() {
      let p = f;
      if (f.tagName.toLowerCase() === "svelte-slot" && f.children.length === 1 && f.children[0] && (p = f.children[0], p.tagName.toLowerCase() === "react-portal-target" && p.children[0] && (p = p.children[0])), An(i, p), n && p.classList.add(...n.split(" ")), o) {
        const y = Ln(o);
        Object.keys(y).forEach((v) => {
          p.style[v] = y[v];
        });
      }
    }
    let g = null, b = null;
    if (d && window.MutationObserver) {
      let p = function() {
        var m, O, h;
        (m = s.current) != null && m.contains(f) && ((O = s.current) == null || O.removeChild(f));
        const {
          portals: v,
          clonedElement: M
        } = Ie(t);
        f = M, l(v), f.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          u();
        }, 50), (h = s.current) == null || h.appendChild(f);
      };
      p();
      const y = cr(() => {
        p(), g == null || g.disconnect(), g == null || g.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      g = new window.MutationObserver(y), g.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      f.style.display = "contents", u(), (x = s.current) == null || x.appendChild(f);
    return () => {
      var p, y;
      f.style.display = "", (p = s.current) != null && p.contains(f) && ((y = s.current) == null || y.removeChild(f)), g == null || g.disconnect();
    };
  }, [t, d, n, o, i, r, c]), _.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Hn = ({
  children: t,
  ...e
}) => /* @__PURE__ */ H.jsx(H.Fragment, {
  children: t(e)
});
function $n(t) {
  return _.createElement(Hn, {
    children: t
  });
}
function Ot(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((r, i) => {
      var c, d;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const s = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((c = r.props) == null ? void 0 : c.key) ?? (n ? `${n}-${i}` : `${i}`)
      }) : {
        ...r.props,
        key: ((d = r.props) == null ? void 0 : d.key) ?? (n ? `${n}-${i}` : `${i}`)
      };
      let a = s;
      Object.keys(r.slots).forEach((f) => {
        if (!r.slots[f] || !(r.slots[f] instanceof Element) && !r.slots[f].el)
          return;
        const u = f.split(".");
        u.forEach((v, M) => {
          a[v] || (a[v] = {}), M !== u.length - 1 && (a = s[v]);
        });
        const g = r.slots[f];
        let b, x, p = (e == null ? void 0 : e.clone) ?? !1, y = e == null ? void 0 : e.forceClone;
        g instanceof Element ? b = g : (b = g.el, x = g.callback, p = g.clone ?? p, y = g.forceClone ?? y), y = y ?? !!x, a[u[u.length - 1]] = b ? x ? (...v) => (x(u[u.length - 1], v), /* @__PURE__ */ H.jsx(Be, {
          ...r.ctx,
          params: v,
          forceClone: y,
          children: /* @__PURE__ */ H.jsx(ct, {
            slot: b,
            clone: p
          })
        })) : $n((v) => /* @__PURE__ */ H.jsx(Be, {
          ...r.ctx,
          forceClone: y,
          children: /* @__PURE__ */ H.jsx(ct, {
            ...v,
            slot: b,
            clone: p
          })
        })) : a[u[u.length - 1]], a = s;
      });
      const l = (e == null ? void 0 : e.children) || "children";
      return r[l] ? s[l] = Ot(r[l], e, `${i}`) : e != null && e.children && (s[l] = void 0, Reflect.deleteProperty(s, l)), s;
    });
}
const {
  useItems: zn,
  withItemsContextProvider: Bn,
  ItemHandler: Vn
} = Nt("antdx-actions-items"), Nn = Dr(Bn(["default", "items"], ({
  children: t,
  items: e,
  className: n,
  ...o
}) => {
  const {
    items: r
  } = zn(), i = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ H.jsxs(H.Fragment, {
    children: [/* @__PURE__ */ H.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ H.jsx(kn, {
      ...o,
      rootClassName: J(n, o.rootClassName),
      items: zt(() => e || Ot(i, {
        clone: !0
      }) || [], [e, i])
    })]
  });
}));
export {
  Nn as Actions,
  Nn as default
};
