import { i as Yt, a as J, r as Qt, Z as ue, g as Jt, c as Y, b as Xe } from "./Index-BXcb6D5Z.js";
const _ = window.ms_globals.React, g = window.ms_globals.React, Wt = window.ms_globals.React.version, Ut = window.ms_globals.React.forwardRef, wt = window.ms_globals.React.useRef, Gt = window.ms_globals.React.useState, Kt = window.ms_globals.React.useEffect, qt = window.ms_globals.React.useCallback, ge = window.ms_globals.React.useMemo, Be = window.ms_globals.ReactDOM.createPortal, Zt = window.ms_globals.internalContext.useContextPropsContext, Je = window.ms_globals.internalContext.ContextPropsProvider, _t = window.ms_globals.createItemsContext.createItemsContext, er = window.ms_globals.antd.ConfigProvider, He = window.ms_globals.antd.theme, tr = window.ms_globals.antd.Avatar, se = window.ms_globals.antdCssinjs.unit, Re = window.ms_globals.antdCssinjs.token2CSSVar, Ze = window.ms_globals.antdCssinjs.useStyleRegister, rr = window.ms_globals.antdCssinjs.useCSSVarRegister, nr = window.ms_globals.antdCssinjs.createTheme, or = window.ms_globals.antdCssinjs.useCacheToken, Pt = window.ms_globals.antdCssinjs.Keyframes;
var sr = /\s/;
function ir(t) {
  for (var e = t.length; e-- && sr.test(t.charAt(e)); )
    ;
  return e;
}
var ar = /^\s+/;
function lr(t) {
  return t && t.slice(0, ir(t) + 1).replace(ar, "");
}
var et = NaN, cr = /^[-+]0x[0-9a-f]+$/i, ur = /^0b[01]+$/i, fr = /^0o[0-7]+$/i, dr = parseInt;
function tt(t) {
  if (typeof t == "number")
    return t;
  if (Yt(t))
    return et;
  if (J(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = J(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = lr(t);
  var n = ur.test(t);
  return n || fr.test(t) ? dr(t.slice(2), n ? 2 : 8) : cr.test(t) ? et : +t;
}
var je = function() {
  return Qt.Date.now();
}, hr = "Expected a function", gr = Math.max, mr = Math.min;
function pr(t, e, n) {
  var o, r, s, i, a, l, c = 0, d = !1, u = !1, f = !0;
  if (typeof t != "function")
    throw new TypeError(hr);
  e = tt(e) || 0, J(n) && (d = !!n.leading, u = "maxWait" in n, s = u ? gr(tt(n.maxWait) || 0, e) : s, f = "trailing" in n ? !!n.trailing : f);
  function h(S) {
    var w = o, O = r;
    return o = r = void 0, c = S, i = t.apply(O, w), i;
  }
  function m(S) {
    return c = S, a = setTimeout(v, e), d ? h(S) : i;
  }
  function y(S) {
    var w = S - l, O = S - c, j = e - w;
    return u ? mr(j, s - O) : j;
  }
  function p(S) {
    var w = S - l, O = S - c;
    return l === void 0 || w >= e || w < 0 || u && O >= s;
  }
  function v() {
    var S = je();
    if (p(S))
      return x(S);
    a = setTimeout(v, y(S));
  }
  function x(S) {
    return a = void 0, f && o ? h(S) : (o = r = void 0, i);
  }
  function R() {
    a !== void 0 && clearTimeout(a), c = 0, o = l = r = a = void 0;
  }
  function b() {
    return a === void 0 ? i : x(je());
  }
  function C() {
    var S = je(), w = p(S);
    if (o = arguments, r = this, l = S, w) {
      if (a === void 0)
        return m(l);
      if (u)
        return clearTimeout(a), a = setTimeout(v, e), h(l);
    }
    return a === void 0 && (a = setTimeout(v, e)), i;
  }
  return C.cancel = R, C.flush = b, C;
}
var Tt = {
  exports: {}
}, be = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var br = g, yr = Symbol.for("react.element"), vr = Symbol.for("react.fragment"), xr = Object.prototype.hasOwnProperty, Sr = br.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Cr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Et(t, e, n) {
  var o, r = {}, s = null, i = null;
  n !== void 0 && (s = "" + n), e.key !== void 0 && (s = "" + e.key), e.ref !== void 0 && (i = e.ref);
  for (o in e) xr.call(e, o) && !Cr.hasOwnProperty(o) && (r[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) r[o] === void 0 && (r[o] = e[o]);
  return {
    $$typeof: yr,
    type: t,
    key: s,
    ref: i,
    props: r,
    _owner: Sr.current
  };
}
be.Fragment = vr;
be.jsx = Et;
be.jsxs = Et;
Tt.exports = be;
var z = Tt.exports;
const {
  SvelteComponent: wr,
  assign: rt,
  binding_callbacks: nt,
  check_outros: _r,
  children: Ot,
  claim_element: Mt,
  claim_space: Pr,
  component_subscribe: ot,
  compute_slots: Tr,
  create_slot: Er,
  detach: Q,
  element: It,
  empty: st,
  exclude_internal_props: it,
  get_all_dirty_from_scope: Or,
  get_slot_changes: Mr,
  group_outros: Ir,
  init: Rr,
  insert_hydration: fe,
  safe_not_equal: jr,
  set_custom_element_data: Rt,
  space: kr,
  transition_in: de,
  transition_out: Ae,
  update_slot_base: Lr
} = window.__gradio__svelte__internal, {
  beforeUpdate: $r,
  getContext: Dr,
  onDestroy: Br,
  setContext: Hr
} = window.__gradio__svelte__internal;
function at(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), r = Er(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = It("svelte-slot"), r && r.c(), this.h();
    },
    l(s) {
      e = Mt(s, "SVELTE-SLOT", {
        class: !0
      });
      var i = Ot(e);
      r && r.l(i), i.forEach(Q), this.h();
    },
    h() {
      Rt(e, "class", "svelte-1rt0kpf");
    },
    m(s, i) {
      fe(s, e, i), r && r.m(e, null), t[9](e), n = !0;
    },
    p(s, i) {
      r && r.p && (!n || i & /*$$scope*/
      64) && Lr(
        r,
        o,
        s,
        /*$$scope*/
        s[6],
        n ? Mr(
          o,
          /*$$scope*/
          s[6],
          i,
          null
        ) : Or(
          /*$$scope*/
          s[6]
        ),
        null
      );
    },
    i(s) {
      n || (de(r, s), n = !0);
    },
    o(s) {
      Ae(r, s), n = !1;
    },
    d(s) {
      s && Q(e), r && r.d(s), t[9](null);
    }
  };
}
function Ar(t) {
  let e, n, o, r, s = (
    /*$$slots*/
    t[4].default && at(t)
  );
  return {
    c() {
      e = It("react-portal-target"), n = kr(), s && s.c(), o = st(), this.h();
    },
    l(i) {
      e = Mt(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), Ot(e).forEach(Q), n = Pr(i), s && s.l(i), o = st(), this.h();
    },
    h() {
      Rt(e, "class", "svelte-1rt0kpf");
    },
    m(i, a) {
      fe(i, e, a), t[8](e), fe(i, n, a), s && s.m(i, a), fe(i, o, a), r = !0;
    },
    p(i, [a]) {
      /*$$slots*/
      i[4].default ? s ? (s.p(i, a), a & /*$$slots*/
      16 && de(s, 1)) : (s = at(i), s.c(), de(s, 1), s.m(o.parentNode, o)) : s && (Ir(), Ae(s, 1, 1, () => {
        s = null;
      }), _r());
    },
    i(i) {
      r || (de(s), r = !0);
    },
    o(i) {
      Ae(s), r = !1;
    },
    d(i) {
      i && (Q(e), Q(n), Q(o)), t[8](null), s && s.d(i);
    }
  };
}
function lt(t) {
  const {
    svelteInit: e,
    ...n
  } = t;
  return n;
}
function zr(t, e, n) {
  let o, r, {
    $$slots: s = {},
    $$scope: i
  } = e;
  const a = Tr(s);
  let {
    svelteInit: l
  } = e;
  const c = ue(lt(e)), d = ue();
  ot(t, d, (b) => n(0, o = b));
  const u = ue();
  ot(t, u, (b) => n(1, r = b));
  const f = [], h = Dr("$$ms-gr-react-wrapper"), {
    slotKey: m,
    slotIndex: y,
    subSlotIndex: p
  } = Jt() || {}, v = l({
    parent: h,
    props: c,
    target: d,
    slot: u,
    slotKey: m,
    slotIndex: y,
    subSlotIndex: p,
    onDestroy(b) {
      f.push(b);
    }
  });
  Hr("$$ms-gr-react-wrapper", v), $r(() => {
    c.set(lt(e));
  }), Br(() => {
    f.forEach((b) => b());
  });
  function x(b) {
    nt[b ? "unshift" : "push"](() => {
      o = b, d.set(o);
    });
  }
  function R(b) {
    nt[b ? "unshift" : "push"](() => {
      r = b, u.set(r);
    });
  }
  return t.$$set = (b) => {
    n(17, e = rt(rt({}, e), it(b))), "svelteInit" in b && n(5, l = b.svelteInit), "$$scope" in b && n(6, i = b.$$scope);
  }, e = it(e), [o, r, d, u, a, l, i, s, x, R];
}
class Fr extends wr {
  constructor(e) {
    super(), Rr(this, e, zr, Ar, jr, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: So
} = window.__gradio__svelte__internal, ct = window.ms_globals.rerender, ke = window.ms_globals.tree;
function Nr(t, e = {}) {
  function n(o) {
    const r = ue(), s = new Fr({
      ...o,
      props: {
        svelteInit(i) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: t,
            props: i.props,
            slot: i.slot,
            target: i.target,
            slotIndex: i.slotIndex,
            subSlotIndex: i.subSlotIndex,
            ignore: e.ignore,
            slotKey: i.slotKey,
            nodes: []
          }, l = i.parent ?? ke;
          return l.nodes = [...l.nodes, a], ct({
            createPortal: Be,
            node: ke
          }), i.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== r), ct({
              createPortal: Be,
              node: ke
            });
          }), a;
        },
        ...o.props
      }
    });
    return r.set(s), s;
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
const Xr = "1.6.1";
function Z() {
  return Z = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, Z.apply(null, arguments);
}
function ie(t) {
  "@babel/helpers - typeof";
  return ie = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, ie(t);
}
function Vr(t, e) {
  if (ie(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (ie(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function Wr(t) {
  var e = Vr(t, "string");
  return ie(e) == "symbol" ? e : e + "";
}
function Ur(t, e, n) {
  return (e = Wr(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function ut(t, e) {
  var n = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(t, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function Gr(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? ut(Object(n), !0).forEach(function(o) {
      Ur(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : ut(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
var Kr = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, qr = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Yr = "".concat(Kr, " ").concat(qr).split(/[\s\n]+/), Qr = "aria-", Jr = "data-";
function ft(t, e) {
  return t.indexOf(e) === 0;
}
function Zr(t) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  e === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : e === !0 ? n = {
    aria: !0
  } : n = Gr({}, e);
  var o = {};
  return Object.keys(t).forEach(function(r) {
    // Aria
    (n.aria && (r === "role" || ft(r, Qr)) || // Data
    n.data && ft(r, Jr) || // Attr
    n.attr && Yr.includes(r)) && (o[r] = t[r]);
  }), o;
}
const en = /* @__PURE__ */ g.createContext({}), tn = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, rn = (t) => {
  const e = g.useContext(en);
  return g.useMemo(() => ({
    ...tn,
    ...e[t]
  }), [e[t]]);
};
function me() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = g.useContext(er.ConfigContext);
  return {
    theme: r,
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o
  };
}
function N(t) {
  "@babel/helpers - typeof";
  return N = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, N(t);
}
function nn(t) {
  if (Array.isArray(t)) return t;
}
function on(t, e) {
  var n = t == null ? null : typeof Symbol < "u" && t[Symbol.iterator] || t["@@iterator"];
  if (n != null) {
    var o, r, s, i, a = [], l = !0, c = !1;
    try {
      if (s = (n = n.call(t)).next, e === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = s.call(n)).done) && (a.push(o.value), a.length !== e); l = !0) ;
    } catch (d) {
      c = !0, r = d;
    } finally {
      try {
        if (!l && n.return != null && (i = n.return(), Object(i) !== i)) return;
      } finally {
        if (c) throw r;
      }
    }
    return a;
  }
}
function dt(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var n = 0, o = Array(e); n < e; n++) o[n] = t[n];
  return o;
}
function sn(t, e) {
  if (t) {
    if (typeof t == "string") return dt(t, e);
    var n = {}.toString.call(t).slice(8, -1);
    return n === "Object" && t.constructor && (n = t.constructor.name), n === "Map" || n === "Set" ? Array.from(t) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? dt(t, e) : void 0;
  }
}
function an() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function he(t, e) {
  return nn(t) || on(t, e) || sn(t, e) || an();
}
function ln(t, e) {
  if (N(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (N(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function jt(t) {
  var e = ln(t, "string");
  return N(e) == "symbol" ? e : e + "";
}
function I(t, e, n) {
  return (e = jt(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function ht(t, e) {
  var n = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(t, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function H(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? ht(Object(n), !0).forEach(function(o) {
      I(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : ht(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
function ye(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function cn(t, e) {
  for (var n = 0; n < e.length; n++) {
    var o = e[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, jt(o.key), o);
  }
}
function ve(t, e, n) {
  return e && cn(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function oe(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function ze(t, e) {
  return ze = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, ze(t, e);
}
function kt(t, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  t.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: t,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(t, "prototype", {
    writable: !1
  }), e && ze(t, e);
}
function pe(t) {
  return pe = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, pe(t);
}
function Lt() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Lt = function() {
    return !!t;
  })();
}
function un(t, e) {
  if (e && (N(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return oe(t);
}
function $t(t) {
  var e = Lt();
  return function() {
    var n, o = pe(t);
    if (e) {
      var r = pe(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return un(this, n);
  };
}
var Dt = /* @__PURE__ */ ve(function t() {
  ye(this, t);
}), Bt = "CALC_UNIT", fn = new RegExp(Bt, "g");
function Le(t) {
  return typeof t == "number" ? "".concat(t).concat(Bt) : t;
}
var dn = /* @__PURE__ */ function(t) {
  kt(n, t);
  var e = $t(n);
  function n(o, r) {
    var s;
    ye(this, n), s = e.call(this), I(oe(s), "result", ""), I(oe(s), "unitlessCssVar", void 0), I(oe(s), "lowPriority", void 0);
    var i = N(o);
    return s.unitlessCssVar = r, o instanceof n ? s.result = "(".concat(o.result, ")") : i === "number" ? s.result = Le(o) : i === "string" && (s.result = o), s;
  }
  return ve(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(Le(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(Le(r))), this.lowPriority = !0, this;
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
      var s = this, i = r || {}, a = i.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(c) {
        return s.result.includes(c);
      }) && (l = !1), this.result = this.result.replace(fn, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(Dt), hn = /* @__PURE__ */ function(t) {
  kt(n, t);
  var e = $t(n);
  function n(o) {
    var r;
    return ye(this, n), r = e.call(this), I(oe(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return ve(n, [{
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
}(Dt), gn = function(e, n) {
  var o = e === "css" ? dn : hn;
  return function(r) {
    return new o(r, n);
  };
}, gt = function(e, n) {
  return "".concat([n, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function mn(t) {
  var e = _.useRef();
  e.current = t;
  var n = _.useCallback(function() {
    for (var o, r = arguments.length, s = new Array(r), i = 0; i < r; i++)
      s[i] = arguments[i];
    return (o = e.current) === null || o === void 0 ? void 0 : o.call.apply(o, [e].concat(s));
  }, []);
  return n;
}
function pn() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var mt = pn() ? _.useLayoutEffect : _.useEffect, bn = function(e, n) {
  var o = _.useRef(!0);
  mt(function() {
    return e(o.current);
  }, n), mt(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, P = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ve = Symbol.for("react.element"), We = Symbol.for("react.portal"), xe = Symbol.for("react.fragment"), Se = Symbol.for("react.strict_mode"), Ce = Symbol.for("react.profiler"), we = Symbol.for("react.provider"), _e = Symbol.for("react.context"), yn = Symbol.for("react.server_context"), Pe = Symbol.for("react.forward_ref"), Te = Symbol.for("react.suspense"), Ee = Symbol.for("react.suspense_list"), Oe = Symbol.for("react.memo"), Me = Symbol.for("react.lazy"), vn = Symbol.for("react.offscreen"), Ht;
Ht = Symbol.for("react.module.reference");
function F(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case Ve:
        switch (t = t.type, t) {
          case xe:
          case Ce:
          case Se:
          case Te:
          case Ee:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case yn:
              case _e:
              case Pe:
              case Me:
              case Oe:
              case we:
                return t;
              default:
                return e;
            }
        }
      case We:
        return e;
    }
  }
}
P.ContextConsumer = _e;
P.ContextProvider = we;
P.Element = Ve;
P.ForwardRef = Pe;
P.Fragment = xe;
P.Lazy = Me;
P.Memo = Oe;
P.Portal = We;
P.Profiler = Ce;
P.StrictMode = Se;
P.Suspense = Te;
P.SuspenseList = Ee;
P.isAsyncMode = function() {
  return !1;
};
P.isConcurrentMode = function() {
  return !1;
};
P.isContextConsumer = function(t) {
  return F(t) === _e;
};
P.isContextProvider = function(t) {
  return F(t) === we;
};
P.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === Ve;
};
P.isForwardRef = function(t) {
  return F(t) === Pe;
};
P.isFragment = function(t) {
  return F(t) === xe;
};
P.isLazy = function(t) {
  return F(t) === Me;
};
P.isMemo = function(t) {
  return F(t) === Oe;
};
P.isPortal = function(t) {
  return F(t) === We;
};
P.isProfiler = function(t) {
  return F(t) === Ce;
};
P.isStrictMode = function(t) {
  return F(t) === Se;
};
P.isSuspense = function(t) {
  return F(t) === Te;
};
P.isSuspenseList = function(t) {
  return F(t) === Ee;
};
P.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === xe || t === Ce || t === Se || t === Te || t === Ee || t === vn || typeof t == "object" && t !== null && (t.$$typeof === Me || t.$$typeof === Oe || t.$$typeof === we || t.$$typeof === _e || t.$$typeof === Pe || t.$$typeof === Ht || t.getModuleId !== void 0);
};
P.typeOf = F;
Number(Wt.split(".")[0]);
function pt(t, e, n, o) {
  var r = H({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var s = o.deprecatedTokens;
    s.forEach(function(a) {
      var l = he(a, 2), c = l[0], d = l[1];
      if (r != null && r[c] || r != null && r[d]) {
        var u;
        (u = r[d]) !== null && u !== void 0 || (r[d] = r == null ? void 0 : r[c]);
      }
    });
  }
  var i = H(H({}, n), r);
  return Object.keys(i).forEach(function(a) {
    i[a] === e[a] && delete i[a];
  }), i;
}
var At = typeof CSSINJS_STATISTIC < "u", Fe = !0;
function Ue() {
  for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
    e[n] = arguments[n];
  if (!At)
    return Object.assign.apply(Object, [{}].concat(e));
  Fe = !1;
  var o = {};
  return e.forEach(function(r) {
    if (N(r) === "object") {
      var s = Object.keys(r);
      s.forEach(function(i) {
        Object.defineProperty(o, i, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return r[i];
          }
        });
      });
    }
  }), Fe = !0, o;
}
var bt = {};
function xn() {
}
var Sn = function(e) {
  var n, o = e, r = xn;
  return At && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(i, a) {
      if (Fe) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return i[a];
    }
  }), r = function(i, a) {
    var l;
    bt[i] = {
      global: Array.from(n),
      component: H(H({}, (l = bt[i]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function yt(t, e, n) {
  if (typeof n == "function") {
    var o;
    return n(Ue(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function Cn(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(s) {
        return se(s);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(s) {
        return se(s);
      }).join(","), ")");
    }
  };
}
var wn = 1e3 * 60 * 10, _n = /* @__PURE__ */ function() {
  function t() {
    ye(this, t), I(this, "map", /* @__PURE__ */ new Map()), I(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), I(this, "nextID", 0), I(this, "lastAccessBeat", /* @__PURE__ */ new Map()), I(this, "accessBeat", 0);
  }
  return ve(t, [{
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
      var o = this, r = n.map(function(s) {
        return s && N(s) === "object" ? "obj_".concat(o.getObjectID(s)) : "".concat(N(s), "_").concat(s);
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
        this.lastAccessBeat.forEach(function(r, s) {
          o - r > wn && (n.map.delete(s), n.lastAccessBeat.delete(s));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), vt = new _n();
function Pn(t, e) {
  return g.useMemo(function() {
    var n = vt.get(e);
    if (n)
      return n;
    var o = t();
    return vt.set(e, o), o;
  }, e);
}
var Tn = function() {
  return {};
};
function En(t) {
  var e = t.useCSP, n = e === void 0 ? Tn : e, o = t.useToken, r = t.usePrefix, s = t.getResetStyles, i = t.getCommonStyle, a = t.getCompUnitless;
  function l(f, h, m, y) {
    var p = Array.isArray(f) ? f[0] : f;
    function v(O) {
      return "".concat(String(p)).concat(O.slice(0, 1).toUpperCase()).concat(O.slice(1));
    }
    var x = (y == null ? void 0 : y.unitless) || {}, R = typeof a == "function" ? a(f) : {}, b = H(H({}, R), {}, I({}, v("zIndexPopup"), !0));
    Object.keys(x).forEach(function(O) {
      b[v(O)] = x[O];
    });
    var C = H(H({}, y), {}, {
      unitless: b,
      prefixToken: v
    }), S = d(f, h, m, C), w = c(p, m, C);
    return function(O) {
      var j = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : O, T = S(O, j), k = he(T, 2), L = k[1], M = w(j), E = he(M, 2), $ = E[0], B = E[1];
      return [$, L, B];
    };
  }
  function c(f, h, m) {
    var y = m.unitless, p = m.injectStyle, v = p === void 0 ? !0 : p, x = m.prefixToken, R = m.ignore, b = function(w) {
      var O = w.rootCls, j = w.cssVar, T = j === void 0 ? {} : j, k = o(), L = k.realToken;
      return rr({
        path: [f],
        prefix: T.prefix,
        key: T.key,
        unitless: y,
        ignore: R,
        token: L,
        scope: O
      }, function() {
        var M = yt(f, L, h), E = pt(f, L, M, {
          deprecatedTokens: m == null ? void 0 : m.deprecatedTokens
        });
        return Object.keys(M).forEach(function($) {
          E[x($)] = E[$], delete E[$];
        }), E;
      }), null;
    }, C = function(w) {
      var O = o(), j = O.cssVar;
      return [function(T) {
        return v && j ? /* @__PURE__ */ g.createElement(g.Fragment, null, /* @__PURE__ */ g.createElement(b, {
          rootCls: w,
          cssVar: j,
          component: f
        }), T) : T;
      }, j == null ? void 0 : j.key];
    };
    return C;
  }
  function d(f, h, m) {
    var y = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = Array.isArray(f) ? f : [f, f], v = he(p, 1), x = v[0], R = p.join("-"), b = t.layer || {
      name: "antd"
    };
    return function(C) {
      var S = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : C, w = o(), O = w.theme, j = w.realToken, T = w.hashId, k = w.token, L = w.cssVar, M = r(), E = M.rootPrefixCls, $ = M.iconPrefixCls, B = n(), A = L ? "css" : "js", V = Pn(function() {
        var W = /* @__PURE__ */ new Set();
        return L && Object.keys(y.unitless || {}).forEach(function(K) {
          W.add(Re(K, L.prefix)), W.add(Re(K, gt(x, L.prefix)));
        }), gn(A, W);
      }, [A, x, L == null ? void 0 : L.prefix]), G = Cn(A), ee = G.max, ae = G.min, q = {
        theme: O,
        token: k,
        hashId: T,
        nonce: function() {
          return B.nonce;
        },
        clientOnly: y.clientOnly,
        layer: b,
        // antd is always at top of styles
        order: y.order || -999
      };
      typeof s == "function" && Ze(H(H({}, q), {}, {
        clientOnly: !1,
        path: ["Shared", E]
      }), function() {
        return s(k, {
          prefix: {
            rootPrefixCls: E,
            iconPrefixCls: $
          },
          csp: B
        });
      });
      var Ie = Ze(H(H({}, q), {}, {
        path: [R, C, $]
      }), function() {
        if (y.injectStyle === !1)
          return [];
        var W = Sn(k), K = W.token, te = W.flush, X = yt(x, j, m), re = ".".concat(C), qe = pt(x, j, X, {
          deprecatedTokens: y.deprecatedTokens
        });
        L && X && N(X) === "object" && Object.keys(X).forEach(function(Qe) {
          X[Qe] = "var(".concat(Re(Qe, gt(x, L.prefix)), ")");
        });
        var Ye = Ue(K, {
          componentCls: re,
          prefixCls: C,
          iconCls: ".".concat($),
          antCls: ".".concat(E),
          calc: V,
          // @ts-ignore
          max: ee,
          // @ts-ignore
          min: ae
        }, L ? X : qe), Xt = h(Ye, {
          hashId: T,
          prefixCls: C,
          rootPrefixCls: E,
          iconPrefixCls: $
        });
        te(x, qe);
        var Vt = typeof i == "function" ? i(Ye, C, S, y.resetFont) : null;
        return [y.resetStyle === !1 ? null : Vt, Xt];
      });
      return [Ie, T];
    };
  }
  function u(f, h, m) {
    var y = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = d(f, h, m, H({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, y)), v = function(R) {
      var b = R.prefixCls, C = R.rootCls, S = C === void 0 ? b : C;
      return p(b, S), null;
    };
    return v;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: u,
    genComponentStyleHook: d
  };
}
const On = {
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
}, Mn = Object.assign(Object.assign({}, On), {
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
function $e(t, e) {
  const n = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = e(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const xt = (t, e, n) => n === 0 ? t : t / 100;
function ne(t, e) {
  const n = e || 255;
  return t > n ? n : t < 0 ? 0 : t;
}
class U {
  constructor(e) {
    I(this, "isValid", !0), I(this, "r", 0), I(this, "g", 0), I(this, "b", 0), I(this, "a", 1), I(this, "_h", void 0), I(this, "_s", void 0), I(this, "_l", void 0), I(this, "_v", void 0), I(this, "_max", void 0), I(this, "_min", void 0), I(this, "_brightness", void 0);
    function n(o) {
      return o[0] in e && o[1] in e && o[2] in e;
    }
    if (e) if (typeof e == "string") {
      let r = function(s) {
        return o.startsWith(s);
      };
      const o = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (e instanceof U)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (n("rgb"))
      this.r = ne(e.r), this.g = ne(e.g), this.b = ne(e.b), this.a = typeof e.a == "number" ? ne(e.a, 1) : 1;
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
    function e(s) {
      const i = s / 255;
      return i <= 0.03928 ? i / 12.92 : Math.pow((i + 0.055) / 1.055, 2.4);
    }
    const n = e(this.r), o = e(this.g), r = e(this.b);
    return 0.2126 * n + 0.7152 * o + 0.0722 * r;
  }
  getHue() {
    if (typeof this._h > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._h = 0 : this._h = D(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
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
    const o = this._c(e), r = n / 100, s = (a) => (o[a] - this[a]) * r + this[a], i = {
      r: D(s("r")),
      g: D(s("g")),
      b: D(s("b")),
      a: D(s("a") * 100) / 100
    };
    return this._c(i);
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
    const n = this._c(e), o = this.a + n.a * (1 - this.a), r = (s) => D((this[s] * this.a + n[s] * n.a * (1 - this.a)) / o);
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
      const s = D(this.a * 255).toString(16);
      e += s.length === 2 ? s : "0" + s;
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
    const e = this.getHue(), n = D(this.getSaturation() * 100), o = D(this.getLightness() * 100);
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
    return r[e] = ne(n, o), r;
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
    function o(r, s) {
      return parseInt(n[r] + n[s || r], 16);
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
      const f = D(o * 255);
      this.r = f, this.g = f, this.b = f;
    }
    let s = 0, i = 0, a = 0;
    const l = e / 60, c = (1 - Math.abs(2 * o - 1)) * n, d = c * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (s = c, i = d) : l >= 1 && l < 2 ? (s = d, i = c) : l >= 2 && l < 3 ? (i = c, a = d) : l >= 3 && l < 4 ? (i = d, a = c) : l >= 4 && l < 5 ? (s = d, a = c) : l >= 5 && l < 6 && (s = c, a = d);
    const u = o - c / 2;
    this.r = D((s + u) * 255), this.g = D((i + u) * 255), this.b = D((a + u) * 255);
  }
  fromHsv({
    h: e,
    s: n,
    v: o,
    a: r
  }) {
    this._h = e % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const s = D(o * 255);
    if (this.r = s, this.g = s, this.b = s, n <= 0)
      return;
    const i = e / 60, a = Math.floor(i), l = i - a, c = D(o * (1 - n) * 255), d = D(o * (1 - n * l) * 255), u = D(o * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = u, this.b = c;
        break;
      case 1:
        this.r = d, this.b = c;
        break;
      case 2:
        this.r = c, this.b = u;
        break;
      case 3:
        this.r = c, this.g = d;
        break;
      case 4:
        this.r = u, this.g = c;
        break;
      case 5:
      default:
        this.g = c, this.b = d;
        break;
    }
  }
  fromHsvString(e) {
    const n = $e(e, xt);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(e) {
    const n = $e(e, xt);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(e) {
    const n = $e(e, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? D(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function De(t) {
  return t >= 0 && t <= 255;
}
function le(t, e) {
  const {
    r: n,
    g: o,
    b: r,
    a: s
  } = new U(t).toRgb();
  if (s < 1)
    return t;
  const {
    r: i,
    g: a,
    b: l
  } = new U(e).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const d = Math.round((n - i * (1 - c)) / c), u = Math.round((o - a * (1 - c)) / c), f = Math.round((r - l * (1 - c)) / c);
    if (De(d) && De(u) && De(f))
      return new U({
        r: d,
        g: u,
        b: f,
        a: Math.round(c * 100) / 100
      }).toRgbString();
  }
  return new U({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var In = function(t, e) {
  var n = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (n[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(t); r < o.length; r++)
    e.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[r]) && (n[o[r]] = t[o[r]]);
  return n;
};
function Rn(t) {
  const {
    override: e
  } = t, n = In(t, ["override"]), o = Object.assign({}, e);
  Object.keys(Mn).forEach((f) => {
    delete o[f];
  });
  const r = Object.assign(Object.assign({}, n), o), s = 480, i = 576, a = 768, l = 992, c = 1200, d = 1600;
  if (r.motion === !1) {
    const f = "0s";
    r.motionDurationFast = f, r.motionDurationMid = f, r.motionDurationSlow = f;
  }
  return Object.assign(Object.assign(Object.assign({}, r), {
    // ============== Background ============== //
    colorFillContent: r.colorFillSecondary,
    colorFillContentHover: r.colorFill,
    colorFillAlter: r.colorFillQuaternary,
    colorBgContainerDisabled: r.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: r.colorBgContainer,
    colorSplit: le(r.colorBorderSecondary, r.colorBgContainer),
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
    colorErrorOutline: le(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: le(r.colorWarningBg, r.colorBgContainer),
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
    controlOutline: le(r.colorPrimaryBg, r.colorBgContainer),
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
    screenXS: s,
    screenXSMin: s,
    screenXSMax: i - 1,
    screenSM: i,
    screenSMMin: i,
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
      0 1px 2px -2px ${new U("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new U("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new U("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const jn = {
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
}, kn = {
  motionBase: !0,
  motionUnit: !0
}, Ln = nr(He.defaultAlgorithm), $n = {
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
}, zt = (t, e, n) => {
  const o = n.getDerivativeToken(t), {
    override: r,
    ...s
  } = e;
  let i = {
    ...o,
    override: r
  };
  return i = Rn(i), s && Object.entries(s).forEach(([a, l]) => {
    const {
      theme: c,
      ...d
    } = l;
    let u = d;
    c && (u = zt({
      ...i,
      ...d
    }, {
      override: d
    }, c)), i[a] = u;
  }), i;
};
function Dn() {
  const {
    token: t,
    hashed: e,
    theme: n = Ln,
    override: o,
    cssVar: r
  } = g.useContext(He._internalContext), [s, i, a] = or(n, [He.defaultSeed, t], {
    salt: `${Xr}-${e || ""}`,
    override: o,
    getComputedToken: zt,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: jn,
      ignore: kn,
      preserve: $n
    }
  });
  return [n, a, e ? i : "", s, r];
}
const {
  genStyleHooks: Bn
} = En({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = me();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, n, o, r] = Dn();
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
    } = me();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
function ce(t) {
  return typeof t == "string";
}
function Hn(t, e) {
  let n = 0;
  const o = Math.min(t.length, e.length);
  for (; n < o && t[n] === e[n]; )
    n++;
  return n;
}
const An = (t, e, n, o) => {
  const r = _.useRef(""), [s, i] = _.useState(1), a = e && ce(t);
  return bn(() => {
    if (!a && ce(t))
      i(t.length);
    else if (ce(t) && ce(r.current) && t.indexOf(r.current) !== 0) {
      if (!t || !r.current) {
        i(1);
        return;
      }
      const c = Hn(t, r.current);
      i(c === 0 ? 1 : c + 1);
    }
    r.current = t;
  }, [t]), _.useEffect(() => {
    if (a && s < t.length) {
      const c = setTimeout(() => {
        i((d) => d + n);
      }, o);
      return () => {
        clearTimeout(c);
      };
    }
  }, [s, e, t]), [a ? t.slice(0, s) : t, a && s < t.length];
};
function zn(t) {
  return _.useMemo(() => {
    if (!t)
      return [!1, 0, 0, null];
    let e = {
      step: 1,
      interval: 50,
      // set default suffix is empty
      suffix: null
    };
    return typeof t == "object" && (e = {
      ...e,
      ...t
    }), [!0, e.step, e.interval, e.suffix];
  }, [t]);
}
const Fn = ({
  prefixCls: t
}) => /* @__PURE__ */ g.createElement("span", {
  className: `${t}-dot`
}, /* @__PURE__ */ g.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-1"
}), /* @__PURE__ */ g.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-2"
}), /* @__PURE__ */ g.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-3"
})), Nn = (t) => {
  const {
    componentCls: e,
    paddingSM: n,
    padding: o
  } = t;
  return {
    [e]: {
      [`${e}-content`]: {
        // Shared: filled, outlined, shadow
        "&-filled,&-outlined,&-shadow": {
          padding: `${se(n)} ${se(o)}`,
          borderRadius: t.borderRadiusLG
        },
        // Filled:
        "&-filled": {
          backgroundColor: t.colorFillContent
        },
        // Outlined:
        "&-outlined": {
          border: `1px solid ${t.colorBorderSecondary}`
        },
        // Shadow:
        "&-shadow": {
          boxShadow: t.boxShadowTertiary
        }
      }
    }
  };
}, Xn = (t) => {
  const {
    componentCls: e,
    fontSize: n,
    lineHeight: o,
    paddingSM: r,
    padding: s,
    calc: i
  } = t, a = i(n).mul(o).div(2).add(r).equal(), l = `${e}-content`;
  return {
    [e]: {
      [l]: {
        // round:
        "&-round": {
          borderRadius: {
            _skip_check_: !0,
            value: a
          },
          paddingInline: i(s).mul(1.25).equal()
        }
      },
      // corner:
      [`&-start ${l}-corner`]: {
        borderStartStartRadius: t.borderRadiusXS
      },
      [`&-end ${l}-corner`]: {
        borderStartEndRadius: t.borderRadiusXS
      }
    }
  };
}, Vn = (t) => {
  const {
    componentCls: e,
    padding: n
  } = t;
  return {
    [`${e}-list`]: {
      display: "flex",
      flexDirection: "column",
      gap: n,
      overflowY: "auto",
      "&::-webkit-scrollbar": {
        width: 8,
        backgroundColor: "transparent"
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: t.colorTextTertiary,
        borderRadius: t.borderRadiusSM
      },
      // For Firefox
      "&": {
        scrollbarWidth: "thin",
        scrollbarColor: `${t.colorTextTertiary} transparent`
      }
    }
  };
}, Wn = new Pt("loadingMove", {
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
}), Un = new Pt("cursorBlink", {
  "0%": {
    opacity: 1
  },
  "50%": {
    opacity: 0
  },
  "100%": {
    opacity: 1
  }
}), Gn = (t) => {
  const {
    componentCls: e,
    fontSize: n,
    lineHeight: o,
    paddingSM: r,
    colorText: s,
    calc: i
  } = t;
  return {
    [e]: {
      display: "flex",
      columnGap: r,
      [`&${e}-end`]: {
        justifyContent: "end",
        flexDirection: "row-reverse",
        [`& ${e}-content-wrapper`]: {
          alignItems: "flex-end"
        }
      },
      [`&${e}-rtl`]: {
        direction: "rtl"
      },
      [`&${e}-typing ${e}-content:last-child::after`]: {
        content: '"|"',
        fontWeight: 900,
        userSelect: "none",
        opacity: 1,
        marginInlineStart: "0.1em",
        animationName: Un,
        animationDuration: "0.8s",
        animationIterationCount: "infinite",
        animationTimingFunction: "linear"
      },
      // ============================ Avatar =============================
      [`& ${e}-avatar`]: {
        display: "inline-flex",
        justifyContent: "center",
        alignSelf: "flex-start"
      },
      // ======================== Header & Footer ========================
      [`& ${e}-header, & ${e}-footer`]: {
        fontSize: n,
        lineHeight: o,
        color: t.colorText
      },
      [`& ${e}-header`]: {
        marginBottom: t.paddingXXS
      },
      [`& ${e}-footer`]: {
        marginTop: r
      },
      // =========================== Content =============================
      [`& ${e}-content-wrapper`]: {
        flex: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        minWidth: 0,
        maxWidth: "100%"
      },
      [`& ${e}-content`]: {
        position: "relative",
        boxSizing: "border-box",
        minWidth: 0,
        maxWidth: "100%",
        color: s,
        fontSize: t.fontSize,
        lineHeight: t.lineHeight,
        minHeight: i(r).mul(2).add(i(o).mul(n)).equal(),
        wordBreak: "break-word",
        [`& ${e}-dot`]: {
          position: "relative",
          height: "100%",
          display: "flex",
          alignItems: "center",
          columnGap: t.marginXS,
          padding: `0 ${se(t.paddingXXS)}`,
          "&-item": {
            backgroundColor: t.colorPrimary,
            borderRadius: "100%",
            width: 4,
            height: 4,
            animationName: Wn,
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
}, Kn = () => ({}), Ft = Bn("Bubble", (t) => {
  const e = Ue(t, {});
  return [Gn(e), Vn(e), Nn(e), Xn(e)];
}, Kn), Nt = /* @__PURE__ */ g.createContext({}), qn = (t, e) => {
  const {
    prefixCls: n,
    className: o,
    rootClassName: r,
    style: s,
    classNames: i = {},
    styles: a = {},
    avatar: l,
    placement: c = "start",
    loading: d = !1,
    loadingRender: u,
    typing: f,
    content: h = "",
    messageRender: m,
    variant: y = "filled",
    shape: p,
    onTypingComplete: v,
    header: x,
    footer: R,
    _key: b,
    ...C
  } = t, {
    onUpdate: S
  } = g.useContext(Nt), w = g.useRef(null);
  g.useImperativeHandle(e, () => ({
    nativeElement: w.current
  }));
  const {
    direction: O,
    getPrefixCls: j
  } = me(), T = j("bubble", n), k = rn("bubble"), [L, M, E, $] = zn(f), [B, A] = An(h, L, M, E);
  g.useEffect(() => {
    S == null || S();
  }, [B]);
  const V = g.useRef(!1);
  g.useEffect(() => {
    !A && !d ? V.current || (V.current = !0, v == null || v()) : V.current = !1;
  }, [A, d]);
  const [G, ee, ae] = Ft(T), q = Y(T, r, k.className, o, ee, ae, `${T}-${c}`, {
    [`${T}-rtl`]: O === "rtl",
    [`${T}-typing`]: A && !d && !m && !$
  }), Ie = g.useMemo(() => /* @__PURE__ */ g.isValidElement(l) ? l : /* @__PURE__ */ g.createElement(tr, l), [l]), W = g.useMemo(() => m ? m(B) : B, [B, m]), K = (re) => typeof re == "function" ? re(B, {
    key: b
  }) : re;
  let te;
  d ? te = u ? u() : /* @__PURE__ */ g.createElement(Fn, {
    prefixCls: T
  }) : te = /* @__PURE__ */ g.createElement(g.Fragment, null, W, A && $);
  let X = /* @__PURE__ */ g.createElement("div", {
    style: {
      ...k.styles.content,
      ...a.content
    },
    className: Y(`${T}-content`, `${T}-content-${y}`, p && `${T}-content-${p}`, k.classNames.content, i.content)
  }, te);
  return (x || R) && (X = /* @__PURE__ */ g.createElement("div", {
    className: `${T}-content-wrapper`
  }, x && /* @__PURE__ */ g.createElement("div", {
    className: Y(`${T}-header`, k.classNames.header, i.header),
    style: {
      ...k.styles.header,
      ...a.header
    }
  }, K(x)), X, R && /* @__PURE__ */ g.createElement("div", {
    className: Y(`${T}-footer`, k.classNames.footer, i.footer),
    style: {
      ...k.styles.footer,
      ...a.footer
    }
  }, K(R)))), G(/* @__PURE__ */ g.createElement("div", Z({
    style: {
      ...k.style,
      ...s
    },
    className: q
  }, C, {
    ref: w
  }), l && /* @__PURE__ */ g.createElement("div", {
    style: {
      ...k.styles.avatar,
      ...a.avatar
    },
    className: Y(`${T}-avatar`, k.classNames.avatar, i.avatar)
  }, Ie), X));
}, Ge = /* @__PURE__ */ g.forwardRef(qn);
function Yn(t, e) {
  const n = _.useCallback((o, r) => typeof e == "function" ? e(o, r) : e ? e[o.role] || {} : {}, [e]);
  return _.useMemo(() => (t || []).map((o, r) => {
    const s = o.key ?? `preset_${r}`;
    return {
      ...n(o, r),
      ...o,
      key: s
    };
  }), [t, n]);
}
const Qn = ({
  _key: t,
  ...e
}, n) => /* @__PURE__ */ _.createElement(Ge, Z({}, e, {
  _key: t,
  ref: (o) => {
    var r;
    o ? n.current[t] = o : (r = n.current) == null || delete r[t];
  }
})), Jn = /* @__PURE__ */ _.memo(/* @__PURE__ */ _.forwardRef(Qn)), Zn = 1, eo = (t, e) => {
  const {
    prefixCls: n,
    rootClassName: o,
    className: r,
    items: s,
    autoScroll: i = !0,
    roles: a,
    onScroll: l,
    ...c
  } = t, d = Zr(c, {
    attr: !0,
    aria: !0
  }), u = _.useRef(null), f = _.useRef({}), {
    getPrefixCls: h
  } = me(), m = h("bubble", n), y = `${m}-list`, [p, v, x] = Ft(m), [R, b] = _.useState(!1);
  _.useEffect(() => (b(!0), () => {
    b(!1);
  }), []);
  const C = Yn(s, a), [S, w] = _.useState(!0), [O, j] = _.useState(0), T = (M) => {
    const E = M.target;
    w(E.scrollHeight - Math.abs(E.scrollTop) - E.clientHeight <= Zn), l == null || l(M);
  };
  _.useEffect(() => {
    i && u.current && S && u.current.scrollTo({
      top: u.current.scrollHeight
    });
  }, [O]), _.useEffect(() => {
    var M;
    if (i) {
      const E = (M = C[C.length - 2]) == null ? void 0 : M.key, $ = f.current[E];
      if ($) {
        const {
          nativeElement: B
        } = $, {
          top: A,
          bottom: V
        } = B.getBoundingClientRect(), {
          top: G,
          bottom: ee
        } = u.current.getBoundingClientRect();
        A < ee && V > G && (j((q) => q + 1), w(!0));
      }
    }
  }, [C.length]), _.useImperativeHandle(e, () => ({
    nativeElement: u.current,
    scrollTo: ({
      key: M,
      offset: E,
      behavior: $ = "smooth",
      block: B
    }) => {
      if (typeof E == "number")
        u.current.scrollTo({
          top: E,
          behavior: $
        });
      else if (M !== void 0) {
        const A = f.current[M];
        if (A) {
          const V = C.findIndex((G) => G.key === M);
          w(V === C.length - 1), A.nativeElement.scrollIntoView({
            behavior: $,
            block: B
          });
        }
      }
    }
  }));
  const k = mn(() => {
    i && j((M) => M + 1);
  }), L = _.useMemo(() => ({
    onUpdate: k
  }), []);
  return p(/* @__PURE__ */ _.createElement(Nt.Provider, {
    value: L
  }, /* @__PURE__ */ _.createElement("div", Z({}, d, {
    className: Y(y, o, r, v, x, {
      [`${y}-reach-end`]: S
    }),
    ref: u,
    onScroll: T
  }), C.map(({
    key: M,
    ...E
  }) => /* @__PURE__ */ _.createElement(Jn, Z({}, E, {
    key: M,
    _key: M,
    ref: f,
    typing: R ? E.typing : !1
  }))))));
}, to = /* @__PURE__ */ _.forwardRef(eo);
Ge.List = to;
const ro = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function no(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = oo(n, o), e;
  }, {}) : {};
}
function oo(t, e) {
  return typeof e == "number" && !ro.includes(t) ? e + "px" : e;
}
function Ne(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const r = g.Children.toArray(t._reactElement.props.children).map((s) => {
      if (g.isValidElement(s) && s.props.__slot__) {
        const {
          portals: i,
          clonedElement: a
        } = Ne(s.props.el);
        return g.cloneElement(s, {
          ...s.props,
          el: a,
          children: [...g.Children.toArray(s.props.children), ...i]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(Be(g.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: r
    }), n)), {
      clonedElement: n,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((r) => {
    t.getEventListeners(r).forEach(({
      listener: i,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, i, l);
    });
  });
  const o = Array.from(t.childNodes);
  for (let r = 0; r < o.length; r++) {
    const s = o[r];
    if (s.nodeType === 1) {
      const {
        clonedElement: i,
        portals: a
      } = Ne(s);
      e.push(...a), n.appendChild(i);
    } else s.nodeType === 3 && n.appendChild(s.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function so(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const St = Ut(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: r
}, s) => {
  const i = wt(), [a, l] = Gt([]), {
    forceClone: c
  } = Zt(), d = c ? !0 : e;
  return Kt(() => {
    var y;
    if (!i.current || !t)
      return;
    let u = t;
    function f() {
      let p = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (p = u.children[0], p.tagName.toLowerCase() === "react-portal-target" && p.children[0] && (p = p.children[0])), so(s, p), n && p.classList.add(...n.split(" ")), o) {
        const v = no(o);
        Object.keys(v).forEach((x) => {
          p.style[x] = v[x];
        });
      }
    }
    let h = null, m = null;
    if (d && window.MutationObserver) {
      let p = function() {
        var b, C, S;
        (b = i.current) != null && b.contains(u) && ((C = i.current) == null || C.removeChild(u));
        const {
          portals: x,
          clonedElement: R
        } = Ne(t);
        u = R, l(x), u.style.display = "contents", m && clearTimeout(m), m = setTimeout(() => {
          f();
        }, 50), (S = i.current) == null || S.appendChild(u);
      };
      p();
      const v = pr(() => {
        p(), h == null || h.disconnect(), h == null || h.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      h = new window.MutationObserver(v), h.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", f(), (y = i.current) == null || y.appendChild(u);
    return () => {
      var p, v;
      u.style.display = "", (p = i.current) != null && p.contains(u) && ((v = i.current) == null || v.removeChild(u)), h == null || h.disconnect();
    };
  }, [t, d, n, o, s, r, c]), g.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...a);
});
function Ct(t) {
  const e = wt(t);
  return e.current = t, qt((...n) => {
    var o;
    return (o = e.current) == null ? void 0 : o.call(e, ...n);
  }, []);
}
const io = ({
  children: t,
  ...e
}) => /* @__PURE__ */ z.jsx(z.Fragment, {
  children: t(e)
});
function ao(t) {
  return g.createElement(io, {
    children: t
  });
}
function Ke(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((r, s) => {
      var c, d;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const i = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((c = r.props) == null ? void 0 : c.key) ?? (n ? `${n}-${s}` : `${s}`)
      }) : {
        ...r.props,
        key: ((d = r.props) == null ? void 0 : d.key) ?? (n ? `${n}-${s}` : `${s}`)
      };
      let a = i;
      Object.keys(r.slots).forEach((u) => {
        if (!r.slots[u] || !(r.slots[u] instanceof Element) && !r.slots[u].el)
          return;
        const f = u.split(".");
        f.forEach((x, R) => {
          a[x] || (a[x] = {}), R !== f.length - 1 && (a = i[x]);
        });
        const h = r.slots[u];
        let m, y, p = (e == null ? void 0 : e.clone) ?? !1, v = e == null ? void 0 : e.forceClone;
        h instanceof Element ? m = h : (m = h.el, y = h.callback, p = h.clone ?? p, v = h.forceClone ?? v), v = v ?? !!y, a[f[f.length - 1]] = m ? y ? (...x) => (y(f[f.length - 1], x), /* @__PURE__ */ z.jsx(Je, {
          ...r.ctx,
          params: x,
          forceClone: v,
          children: /* @__PURE__ */ z.jsx(St, {
            slot: m,
            clone: p
          })
        })) : ao((x) => /* @__PURE__ */ z.jsx(Je, {
          ...r.ctx,
          forceClone: v,
          children: /* @__PURE__ */ z.jsx(St, {
            ...x,
            slot: m,
            clone: p
          })
        })) : a[f[f.length - 1]], a = i;
      });
      const l = (e == null ? void 0 : e.children) || "children";
      return r[l] ? i[l] = Ke(r[l], e, `${s}`) : e != null && e.children && (i[l] = void 0, Reflect.deleteProperty(i, l)), i;
    });
}
const {
  useItems: lo,
  withItemsContextProvider: co,
  ItemHandler: Co
} = _t("antdx-bubble.list-items"), {
  useItems: uo,
  withItemsContextProvider: fo,
  ItemHandler: wo
} = _t("antdx-bubble.list-roles");
function ho(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function go(t, e = !1) {
  try {
    if (Xe(t))
      return t;
    if (e && !ho(t))
      return;
    if (typeof t == "string") {
      let n = t.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function mo(t, e) {
  return ge(() => go(t, e), [t, e]);
}
function po(t, e) {
  return e((o, r) => Xe(o) ? r ? (...s) => J(r) && r.unshift ? o(...t, ...s) : o(...s, ...t) : o(...t) : o);
}
const bo = Symbol();
function yo(t, e) {
  return po(e, (n) => {
    var o, r;
    return {
      ...t,
      avatar: Xe(t.avatar) ? n(t.avatar) : J(t.avatar) ? {
        ...t.avatar,
        icon: n((o = t.avatar) == null ? void 0 : o.icon),
        src: n((r = t.avatar) == null ? void 0 : r.src)
      } : t.avatar,
      footer: n(t.footer, {
        unshift: !0
      }),
      header: n(t.header, {
        unshift: !0
      }),
      loadingRender: n(t.loadingRender, !0),
      messageRender: n(t.messageRender, !0)
    };
  });
}
function vo({
  roles: t,
  preProcess: e,
  postProcess: n
}, o = []) {
  const r = mo(t), s = Ct(e), i = Ct(n), {
    items: {
      roles: a
    }
  } = uo(), l = ge(() => {
    var d;
    return t || ((d = Ke(a, {
      clone: !0,
      forceClone: !0
    })) == null ? void 0 : d.reduce((u, f) => (f.role !== void 0 && (u[f.role] = f), u), {}));
  }, [a, t]), c = ge(() => (d, u) => {
    const f = u ?? d[bo], h = s(d, f) || d;
    if (h.role && (l || {})[h.role])
      return yo((l || {})[h.role], [h, f]);
    let m;
    return m = i(h, f), m || {
      messageRender(y) {
        return /* @__PURE__ */ z.jsx(z.Fragment, {
          children: J(y) ? JSON.stringify(y) : y
        });
      }
    };
  }, [l, i, s, ...o]);
  return r || c;
}
const _o = Nr(fo(["roles"], co(["items", "default"], ({
  items: t,
  roles: e,
  children: n,
  ...o
}) => {
  const {
    items: r
  } = lo(), s = vo({
    roles: e
  }), i = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ z.jsxs(z.Fragment, {
    children: [/* @__PURE__ */ z.jsx("div", {
      style: {
        display: "none"
      },
      children: n
    }), /* @__PURE__ */ z.jsx(Ge.List, {
      ...o,
      items: ge(() => t || Ke(i), [t, i]),
      roles: s
    })]
  });
})));
export {
  _o as BubbleList,
  _o as default
};
