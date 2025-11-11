import { i as Gt, a as me, r as Kt, Z as fe, g as qt, c as Q, b as Yt } from "./Index-BjPEl37B.js";
const _ = window.ms_globals.React, h = window.ms_globals.React, Nt = window.ms_globals.React.forwardRef, Xt = window.ms_globals.React.useRef, Vt = window.ms_globals.React.useState, Wt = window.ms_globals.React.useEffect, Ut = window.ms_globals.React.version, xt = window.ms_globals.React.useMemo, He = window.ms_globals.ReactDOM.createPortal, Qt = window.ms_globals.internalContext.useContextPropsContext, Zt = window.ms_globals.internalContext.ContextPropsProvider, Jt = window.ms_globals.antd.ConfigProvider, Ae = window.ms_globals.antd.theme, er = window.ms_globals.antd.Avatar, ie = window.ms_globals.antdCssinjs.unit, Ie = window.ms_globals.antdCssinjs.token2CSSVar, Qe = window.ms_globals.antdCssinjs.useStyleRegister, tr = window.ms_globals.antdCssinjs.useCSSVarRegister, rr = window.ms_globals.antdCssinjs.createTheme, nr = window.ms_globals.antdCssinjs.useCacheToken, Ct = window.ms_globals.antdCssinjs.Keyframes;
var or = /\s/;
function ir(t) {
  for (var e = t.length; e-- && or.test(t.charAt(e)); )
    ;
  return e;
}
var sr = /^\s+/;
function ar(t) {
  return t && t.slice(0, ir(t) + 1).replace(sr, "");
}
var Ze = NaN, cr = /^[-+]0x[0-9a-f]+$/i, lr = /^0b[01]+$/i, ur = /^0o[0-7]+$/i, fr = parseInt;
function Je(t) {
  if (typeof t == "number")
    return t;
  if (Gt(t))
    return Ze;
  if (me(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = me(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = ar(t);
  var r = lr.test(t);
  return r || ur.test(t) ? fr(t.slice(2), r ? 2 : 8) : cr.test(t) ? Ze : +t;
}
var ke = function() {
  return Kt.Date.now();
}, dr = "Expected a function", hr = Math.max, gr = Math.min;
function mr(t, e, r) {
  var o, n, i, s, a, c, l = 0, f = !1, u = !1, d = !0;
  if (typeof t != "function")
    throw new TypeError(dr);
  e = Je(e) || 0, me(r) && (f = !!r.leading, u = "maxWait" in r, i = u ? hr(Je(r.maxWait) || 0, e) : i, d = "trailing" in r ? !!r.trailing : d);
  function S(m) {
    var w = o, O = n;
    return o = n = void 0, l = m, s = t.apply(O, w), s;
  }
  function b(m) {
    return l = m, a = setTimeout(y, e), f ? S(m) : s;
  }
  function x(m) {
    var w = m - c, O = m - l, j = e - w;
    return u ? gr(j, i - O) : j;
  }
  function p(m) {
    var w = m - c, O = m - l;
    return c === void 0 || w >= e || w < 0 || u && O >= i;
  }
  function y() {
    var m = ke();
    if (p(m))
      return C(m);
    a = setTimeout(y, x(m));
  }
  function C(m) {
    return a = void 0, d && o ? S(m) : (o = n = void 0, s);
  }
  function I() {
    a !== void 0 && clearTimeout(a), l = 0, o = c = n = a = void 0;
  }
  function g() {
    return a === void 0 ? s : C(ke());
  }
  function v() {
    var m = ke(), w = p(m);
    if (o = arguments, n = this, c = m, w) {
      if (a === void 0)
        return b(c);
      if (u)
        return clearTimeout(a), a = setTimeout(y, e), S(c);
    }
    return a === void 0 && (a = setTimeout(y, e)), s;
  }
  return v.cancel = I, v.flush = g, v;
}
var wt = {
  exports: {}
}, ye = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var pr = h, br = Symbol.for("react.element"), yr = Symbol.for("react.fragment"), vr = Object.prototype.hasOwnProperty, Sr = pr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, xr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function _t(t, e, r) {
  var o, n = {}, i = null, s = null;
  r !== void 0 && (i = "" + r), e.key !== void 0 && (i = "" + e.key), e.ref !== void 0 && (s = e.ref);
  for (o in e) vr.call(e, o) && !xr.hasOwnProperty(o) && (n[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) n[o] === void 0 && (n[o] = e[o]);
  return {
    $$typeof: br,
    type: t,
    key: i,
    ref: s,
    props: n,
    _owner: Sr.current
  };
}
ye.Fragment = yr;
ye.jsx = _t;
ye.jsxs = _t;
wt.exports = ye;
var D = wt.exports;
const {
  SvelteComponent: Cr,
  assign: et,
  binding_callbacks: tt,
  check_outros: wr,
  children: Tt,
  claim_element: Pt,
  claim_space: _r,
  component_subscribe: rt,
  compute_slots: Tr,
  create_slot: Pr,
  detach: Z,
  element: Et,
  empty: nt,
  exclude_internal_props: ot,
  get_all_dirty_from_scope: Er,
  get_slot_changes: Or,
  group_outros: Mr,
  init: Rr,
  insert_hydration: de,
  safe_not_equal: jr,
  set_custom_element_data: Ot,
  space: Ir,
  transition_in: he,
  transition_out: ze,
  update_slot_base: kr
} = window.__gradio__svelte__internal, {
  beforeUpdate: Lr,
  getContext: $r,
  onDestroy: Dr,
  setContext: Br
} = window.__gradio__svelte__internal;
function it(t) {
  let e, r;
  const o = (
    /*#slots*/
    t[7].default
  ), n = Pr(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = Et("svelte-slot"), n && n.c(), this.h();
    },
    l(i) {
      e = Pt(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = Tt(e);
      n && n.l(s), s.forEach(Z), this.h();
    },
    h() {
      Ot(e, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      de(i, e, s), n && n.m(e, null), t[9](e), r = !0;
    },
    p(i, s) {
      n && n.p && (!r || s & /*$$scope*/
      64) && kr(
        n,
        o,
        i,
        /*$$scope*/
        i[6],
        r ? Or(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : Er(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      r || (he(n, i), r = !0);
    },
    o(i) {
      ze(n, i), r = !1;
    },
    d(i) {
      i && Z(e), n && n.d(i), t[9](null);
    }
  };
}
function Hr(t) {
  let e, r, o, n, i = (
    /*$$slots*/
    t[4].default && it(t)
  );
  return {
    c() {
      e = Et("react-portal-target"), r = Ir(), i && i.c(), o = nt(), this.h();
    },
    l(s) {
      e = Pt(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), Tt(e).forEach(Z), r = _r(s), i && i.l(s), o = nt(), this.h();
    },
    h() {
      Ot(e, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      de(s, e, a), t[8](e), de(s, r, a), i && i.m(s, a), de(s, o, a), n = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && he(i, 1)) : (i = it(s), i.c(), he(i, 1), i.m(o.parentNode, o)) : i && (Mr(), ze(i, 1, 1, () => {
        i = null;
      }), wr());
    },
    i(s) {
      n || (he(i), n = !0);
    },
    o(s) {
      ze(i), n = !1;
    },
    d(s) {
      s && (Z(e), Z(r), Z(o)), t[8](null), i && i.d(s);
    }
  };
}
function st(t) {
  const {
    svelteInit: e,
    ...r
  } = t;
  return r;
}
function Ar(t, e, r) {
  let o, n, {
    $$slots: i = {},
    $$scope: s
  } = e;
  const a = Tr(i);
  let {
    svelteInit: c
  } = e;
  const l = fe(st(e)), f = fe();
  rt(t, f, (g) => r(0, o = g));
  const u = fe();
  rt(t, u, (g) => r(1, n = g));
  const d = [], S = $r("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: x,
    subSlotIndex: p
  } = qt() || {}, y = c({
    parent: S,
    props: l,
    target: f,
    slot: u,
    slotKey: b,
    slotIndex: x,
    subSlotIndex: p,
    onDestroy(g) {
      d.push(g);
    }
  });
  Br("$$ms-gr-react-wrapper", y), Lr(() => {
    l.set(st(e));
  }), Dr(() => {
    d.forEach((g) => g());
  });
  function C(g) {
    tt[g ? "unshift" : "push"](() => {
      o = g, f.set(o);
    });
  }
  function I(g) {
    tt[g ? "unshift" : "push"](() => {
      n = g, u.set(n);
    });
  }
  return t.$$set = (g) => {
    r(17, e = et(et({}, e), ot(g))), "svelteInit" in g && r(5, c = g.svelteInit), "$$scope" in g && r(6, s = g.$$scope);
  }, e = ot(e), [o, n, f, u, a, c, s, i, C, I];
}
class zr extends Cr {
  constructor(e) {
    super(), Rr(this, e, Ar, Hr, jr, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: uo
} = window.__gradio__svelte__internal, at = window.ms_globals.rerender, Le = window.ms_globals.tree;
function Fr(t, e = {}) {
  function r(o) {
    const n = fe(), i = new zr({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: t,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: e.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, c = s.parent ?? Le;
          return c.nodes = [...c.nodes, a], at({
            createPortal: He,
            node: Le
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((l) => l.svelteInstance !== n), at({
              createPortal: He,
              node: Le
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
const Nr = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Xr(t) {
  return t ? Object.keys(t).reduce((e, r) => {
    const o = t[r];
    return e[r] = Vr(r, o), e;
  }, {}) : {};
}
function Vr(t, e) {
  return typeof e == "number" && !Nr.includes(t) ? e + "px" : e;
}
function Fe(t) {
  const e = [], r = t.cloneNode(!1);
  if (t._reactElement) {
    const n = h.Children.toArray(t._reactElement.props.children).map((i) => {
      if (h.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Fe(i.props.el);
        return h.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...h.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return n.originalChildren = t._reactElement.props.children, e.push(He(h.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: n
    }), r)), {
      clonedElement: r,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((n) => {
    t.getEventListeners(n).forEach(({
      listener: s,
      type: a,
      useCapture: c
    }) => {
      r.addEventListener(a, s, c);
    });
  });
  const o = Array.from(t.childNodes);
  for (let n = 0; n < o.length; n++) {
    const i = o[n];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Fe(i);
      e.push(...a), r.appendChild(s);
    } else i.nodeType === 3 && r.appendChild(i.cloneNode());
  }
  return {
    clonedElement: r,
    portals: e
  };
}
function Wr(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const U = Nt(({
  slot: t,
  clone: e,
  className: r,
  style: o,
  observeAttributes: n
}, i) => {
  const s = Xt(), [a, c] = Vt([]), {
    forceClone: l
  } = Qt(), f = l ? !0 : e;
  return Wt(() => {
    var x;
    if (!s.current || !t)
      return;
    let u = t;
    function d() {
      let p = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (p = u.children[0], p.tagName.toLowerCase() === "react-portal-target" && p.children[0] && (p = p.children[0])), Wr(i, p), r && p.classList.add(...r.split(" ")), o) {
        const y = Xr(o);
        Object.keys(y).forEach((C) => {
          p.style[C] = y[C];
        });
      }
    }
    let S = null, b = null;
    if (f && window.MutationObserver) {
      let p = function() {
        var g, v, m;
        (g = s.current) != null && g.contains(u) && ((v = s.current) == null || v.removeChild(u));
        const {
          portals: C,
          clonedElement: I
        } = Fe(t);
        u = I, c(C), u.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          d();
        }, 50), (m = s.current) == null || m.appendChild(u);
      };
      p();
      const y = mr(() => {
        p(), S == null || S.disconnect(), S == null || S.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: n
        });
      }, 50);
      S = new window.MutationObserver(y), S.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", d(), (x = s.current) == null || x.appendChild(u);
    return () => {
      var p, y;
      u.style.display = "", (p = s.current) != null && p.contains(u) && ((y = s.current) == null || y.removeChild(u)), S == null || S.disconnect();
    };
  }, [t, f, r, o, i, n, l]), h.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Ur = "1.6.1";
function J() {
  return J = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var r = arguments[e];
      for (var o in r) ({}).hasOwnProperty.call(r, o) && (t[o] = r[o]);
    }
    return t;
  }, J.apply(null, arguments);
}
function se(t) {
  "@babel/helpers - typeof";
  return se = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, se(t);
}
function Gr(t, e) {
  if (se(t) != "object" || !t) return t;
  var r = t[Symbol.toPrimitive];
  if (r !== void 0) {
    var o = r.call(t, e);
    if (se(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function Kr(t) {
  var e = Gr(t, "string");
  return se(e) == "symbol" ? e : e + "";
}
function qr(t, e, r) {
  return (e = Kr(e)) in t ? Object.defineProperty(t, e, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = r, t;
}
function ct(t, e) {
  var r = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(n) {
      return Object.getOwnPropertyDescriptor(t, n).enumerable;
    })), r.push.apply(r, o);
  }
  return r;
}
function Yr(t) {
  for (var e = 1; e < arguments.length; e++) {
    var r = arguments[e] != null ? arguments[e] : {};
    e % 2 ? ct(Object(r), !0).forEach(function(o) {
      qr(t, o, r[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(r)) : ct(Object(r)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(r, o));
    });
  }
  return t;
}
var Qr = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, Zr = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Jr = "".concat(Qr, " ").concat(Zr).split(/[\s\n]+/), en = "aria-", tn = "data-";
function lt(t, e) {
  return t.indexOf(e) === 0;
}
function rn(t) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, r;
  e === !1 ? r = {
    aria: !0,
    data: !0,
    attr: !0
  } : e === !0 ? r = {
    aria: !0
  } : r = Yr({}, e);
  var o = {};
  return Object.keys(t).forEach(function(n) {
    // Aria
    (r.aria && (n === "role" || lt(n, en)) || // Data
    r.data && lt(n, tn) || // Attr
    r.attr && Jr.includes(n)) && (o[n] = t[n]);
  }), o;
}
const nn = /* @__PURE__ */ h.createContext({}), on = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, sn = (t) => {
  const e = h.useContext(nn);
  return h.useMemo(() => ({
    ...on,
    ...e[t]
  }), [e[t]]);
};
function pe() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: r,
    iconPrefixCls: o,
    theme: n
  } = h.useContext(Jt.ConfigContext);
  return {
    theme: n,
    getPrefixCls: t,
    direction: e,
    csp: r,
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
function an(t) {
  if (Array.isArray(t)) return t;
}
function cn(t, e) {
  var r = t == null ? null : typeof Symbol < "u" && t[Symbol.iterator] || t["@@iterator"];
  if (r != null) {
    var o, n, i, s, a = [], c = !0, l = !1;
    try {
      if (i = (r = r.call(t)).next, e === 0) {
        if (Object(r) !== r) return;
        c = !1;
      } else for (; !(c = (o = i.call(r)).done) && (a.push(o.value), a.length !== e); c = !0) ;
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
function ut(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var r = 0, o = Array(e); r < e; r++) o[r] = t[r];
  return o;
}
function ln(t, e) {
  if (t) {
    if (typeof t == "string") return ut(t, e);
    var r = {}.toString.call(t).slice(8, -1);
    return r === "Object" && t.constructor && (r = t.constructor.name), r === "Map" || r === "Set" ? Array.from(t) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? ut(t, e) : void 0;
  }
}
function un() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function ge(t, e) {
  return an(t) || cn(t, e) || ln(t, e) || un();
}
function fn(t, e) {
  if (N(t) != "object" || !t) return t;
  var r = t[Symbol.toPrimitive];
  if (r !== void 0) {
    var o = r.call(t, e);
    if (N(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function Mt(t) {
  var e = fn(t, "string");
  return N(e) == "symbol" ? e : e + "";
}
function R(t, e, r) {
  return (e = Mt(e)) in t ? Object.defineProperty(t, e, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = r, t;
}
function ft(t, e) {
  var r = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(n) {
      return Object.getOwnPropertyDescriptor(t, n).enumerable;
    })), r.push.apply(r, o);
  }
  return r;
}
function A(t) {
  for (var e = 1; e < arguments.length; e++) {
    var r = arguments[e] != null ? arguments[e] : {};
    e % 2 ? ft(Object(r), !0).forEach(function(o) {
      R(t, o, r[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(r)) : ft(Object(r)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(r, o));
    });
  }
  return t;
}
function ve(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function dn(t, e) {
  for (var r = 0; r < e.length; r++) {
    var o = e[r];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, Mt(o.key), o);
  }
}
function Se(t, e, r) {
  return e && dn(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function oe(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function Ne(t, e) {
  return Ne = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, o) {
    return r.__proto__ = o, r;
  }, Ne(t, e);
}
function Rt(t, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  t.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: t,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(t, "prototype", {
    writable: !1
  }), e && Ne(t, e);
}
function be(t) {
  return be = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, be(t);
}
function jt() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (jt = function() {
    return !!t;
  })();
}
function hn(t, e) {
  if (e && (N(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return oe(t);
}
function It(t) {
  var e = jt();
  return function() {
    var r, o = be(t);
    if (e) {
      var n = be(this).constructor;
      r = Reflect.construct(o, arguments, n);
    } else r = o.apply(this, arguments);
    return hn(this, r);
  };
}
var kt = /* @__PURE__ */ Se(function t() {
  ve(this, t);
}), Lt = "CALC_UNIT", gn = new RegExp(Lt, "g");
function $e(t) {
  return typeof t == "number" ? "".concat(t).concat(Lt) : t;
}
var mn = /* @__PURE__ */ function(t) {
  Rt(r, t);
  var e = It(r);
  function r(o, n) {
    var i;
    ve(this, r), i = e.call(this), R(oe(i), "result", ""), R(oe(i), "unitlessCssVar", void 0), R(oe(i), "lowPriority", void 0);
    var s = N(o);
    return i.unitlessCssVar = n, o instanceof r ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = $e(o) : s === "string" && (i.result = o), i;
  }
  return Se(r, [{
    key: "add",
    value: function(n) {
      return n instanceof r ? this.result = "".concat(this.result, " + ").concat(n.getResult()) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " + ").concat($e(n))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(n) {
      return n instanceof r ? this.result = "".concat(this.result, " - ").concat(n.getResult()) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " - ").concat($e(n))), this.lowPriority = !0, this;
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
      }) && (c = !1), this.result = this.result.replace(gn, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), r;
}(kt), pn = /* @__PURE__ */ function(t) {
  Rt(r, t);
  var e = It(r);
  function r(o) {
    var n;
    return ve(this, r), n = e.call(this), R(oe(n), "result", 0), o instanceof r ? n.result = o.result : typeof o == "number" && (n.result = o), n;
  }
  return Se(r, [{
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
}(kt), bn = function(e, r) {
  var o = e === "css" ? mn : pn;
  return function(n) {
    return new o(n, r);
  };
}, dt = function(e, r) {
  return "".concat([r, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function yn(t) {
  var e = _.useRef();
  e.current = t;
  var r = _.useCallback(function() {
    for (var o, n = arguments.length, i = new Array(n), s = 0; s < n; s++)
      i[s] = arguments[s];
    return (o = e.current) === null || o === void 0 ? void 0 : o.call.apply(o, [e].concat(i));
  }, []);
  return r;
}
function vn() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var ht = vn() ? _.useLayoutEffect : _.useEffect, Sn = function(e, r) {
  var o = _.useRef(!0);
  ht(function() {
    return e(o.current);
  }, r), ht(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, T = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ve = Symbol.for("react.element"), We = Symbol.for("react.portal"), xe = Symbol.for("react.fragment"), Ce = Symbol.for("react.strict_mode"), we = Symbol.for("react.profiler"), _e = Symbol.for("react.provider"), Te = Symbol.for("react.context"), xn = Symbol.for("react.server_context"), Pe = Symbol.for("react.forward_ref"), Ee = Symbol.for("react.suspense"), Oe = Symbol.for("react.suspense_list"), Me = Symbol.for("react.memo"), Re = Symbol.for("react.lazy"), Cn = Symbol.for("react.offscreen"), $t;
$t = Symbol.for("react.module.reference");
function F(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case Ve:
        switch (t = t.type, t) {
          case xe:
          case we:
          case Ce:
          case Ee:
          case Oe:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case xn:
              case Te:
              case Pe:
              case Re:
              case Me:
              case _e:
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
T.ContextConsumer = Te;
T.ContextProvider = _e;
T.Element = Ve;
T.ForwardRef = Pe;
T.Fragment = xe;
T.Lazy = Re;
T.Memo = Me;
T.Portal = We;
T.Profiler = we;
T.StrictMode = Ce;
T.Suspense = Ee;
T.SuspenseList = Oe;
T.isAsyncMode = function() {
  return !1;
};
T.isConcurrentMode = function() {
  return !1;
};
T.isContextConsumer = function(t) {
  return F(t) === Te;
};
T.isContextProvider = function(t) {
  return F(t) === _e;
};
T.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === Ve;
};
T.isForwardRef = function(t) {
  return F(t) === Pe;
};
T.isFragment = function(t) {
  return F(t) === xe;
};
T.isLazy = function(t) {
  return F(t) === Re;
};
T.isMemo = function(t) {
  return F(t) === Me;
};
T.isPortal = function(t) {
  return F(t) === We;
};
T.isProfiler = function(t) {
  return F(t) === we;
};
T.isStrictMode = function(t) {
  return F(t) === Ce;
};
T.isSuspense = function(t) {
  return F(t) === Ee;
};
T.isSuspenseList = function(t) {
  return F(t) === Oe;
};
T.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === xe || t === we || t === Ce || t === Ee || t === Oe || t === Cn || typeof t == "object" && t !== null && (t.$$typeof === Re || t.$$typeof === Me || t.$$typeof === _e || t.$$typeof === Te || t.$$typeof === Pe || t.$$typeof === $t || t.getModuleId !== void 0);
};
T.typeOf = F;
Number(Ut.split(".")[0]);
function gt(t, e, r, o) {
  var n = A({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var c = ge(a, 2), l = c[0], f = c[1];
      if (n != null && n[l] || n != null && n[f]) {
        var u;
        (u = n[f]) !== null && u !== void 0 || (n[f] = n == null ? void 0 : n[l]);
      }
    });
  }
  var s = A(A({}, r), n);
  return Object.keys(s).forEach(function(a) {
    s[a] === e[a] && delete s[a];
  }), s;
}
var Dt = typeof CSSINJS_STATISTIC < "u", Xe = !0;
function Ue() {
  for (var t = arguments.length, e = new Array(t), r = 0; r < t; r++)
    e[r] = arguments[r];
  if (!Dt)
    return Object.assign.apply(Object, [{}].concat(e));
  Xe = !1;
  var o = {};
  return e.forEach(function(n) {
    if (N(n) === "object") {
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
  }), Xe = !0, o;
}
var mt = {};
function wn() {
}
var _n = function(e) {
  var r, o = e, n = wn;
  return Dt && typeof Proxy < "u" && (r = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(s, a) {
      if (Xe) {
        var c;
        (c = r) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), n = function(s, a) {
    var c;
    mt[s] = {
      global: Array.from(r),
      component: A(A({}, (c = mt[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: o,
    keys: r,
    flush: n
  };
};
function pt(t, e, r) {
  if (typeof r == "function") {
    var o;
    return r(Ue(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return r ?? {};
}
function Tn(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var r = arguments.length, o = new Array(r), n = 0; n < r; n++)
        o[n] = arguments[n];
      return "max(".concat(o.map(function(i) {
        return ie(i);
      }).join(","), ")");
    },
    min: function() {
      for (var r = arguments.length, o = new Array(r), n = 0; n < r; n++)
        o[n] = arguments[n];
      return "min(".concat(o.map(function(i) {
        return ie(i);
      }).join(","), ")");
    }
  };
}
var Pn = 1e3 * 60 * 10, En = /* @__PURE__ */ function() {
  function t() {
    ve(this, t), R(this, "map", /* @__PURE__ */ new Map()), R(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), R(this, "nextID", 0), R(this, "lastAccessBeat", /* @__PURE__ */ new Map()), R(this, "accessBeat", 0);
  }
  return Se(t, [{
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
        return i && N(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(N(i), "_").concat(i);
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
          o - n > Pn && (r.map.delete(i), r.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), bt = new En();
function On(t, e) {
  return h.useMemo(function() {
    var r = bt.get(e);
    if (r)
      return r;
    var o = t();
    return bt.set(e, o), o;
  }, e);
}
var Mn = function() {
  return {};
};
function Rn(t) {
  var e = t.useCSP, r = e === void 0 ? Mn : e, o = t.useToken, n = t.usePrefix, i = t.getResetStyles, s = t.getCommonStyle, a = t.getCompUnitless;
  function c(d, S, b, x) {
    var p = Array.isArray(d) ? d[0] : d;
    function y(O) {
      return "".concat(String(p)).concat(O.slice(0, 1).toUpperCase()).concat(O.slice(1));
    }
    var C = (x == null ? void 0 : x.unitless) || {}, I = typeof a == "function" ? a(d) : {}, g = A(A({}, I), {}, R({}, y("zIndexPopup"), !0));
    Object.keys(C).forEach(function(O) {
      g[y(O)] = C[O];
    });
    var v = A(A({}, x), {}, {
      unitless: g,
      prefixToken: y
    }), m = f(d, S, b, v), w = l(p, b, v);
    return function(O) {
      var j = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : O, P = m(O, j), k = ge(P, 2), L = k[1], M = w(j), E = ge(M, 2), $ = E[0], H = E[1];
      return [$, L, H];
    };
  }
  function l(d, S, b) {
    var x = b.unitless, p = b.injectStyle, y = p === void 0 ? !0 : p, C = b.prefixToken, I = b.ignore, g = function(w) {
      var O = w.rootCls, j = w.cssVar, P = j === void 0 ? {} : j, k = o(), L = k.realToken;
      return tr({
        path: [d],
        prefix: P.prefix,
        key: P.key,
        unitless: x,
        ignore: I,
        token: L,
        scope: O
      }, function() {
        var M = pt(d, L, S), E = gt(d, L, M, {
          deprecatedTokens: b == null ? void 0 : b.deprecatedTokens
        });
        return Object.keys(M).forEach(function($) {
          E[C($)] = E[$], delete E[$];
        }), E;
      }), null;
    }, v = function(w) {
      var O = o(), j = O.cssVar;
      return [function(P) {
        return y && j ? /* @__PURE__ */ h.createElement(h.Fragment, null, /* @__PURE__ */ h.createElement(g, {
          rootCls: w,
          cssVar: j,
          component: d
        }), P) : P;
      }, j == null ? void 0 : j.key];
    };
    return v;
  }
  function f(d, S, b) {
    var x = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = Array.isArray(d) ? d : [d, d], y = ge(p, 1), C = y[0], I = p.join("-"), g = t.layer || {
      name: "antd"
    };
    return function(v) {
      var m = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : v, w = o(), O = w.theme, j = w.realToken, P = w.hashId, k = w.token, L = w.cssVar, M = n(), E = M.rootPrefixCls, $ = M.iconPrefixCls, H = r(), z = L ? "css" : "js", V = On(function() {
        var W = /* @__PURE__ */ new Set();
        return L && Object.keys(x.unitless || {}).forEach(function(q) {
          W.add(Ie(q, L.prefix)), W.add(Ie(q, dt(C, L.prefix)));
        }), bn(z, W);
      }, [z, C, L == null ? void 0 : L.prefix]), K = Tn(z), ee = K.max, ae = K.min, Y = {
        theme: O,
        token: k,
        hashId: P,
        nonce: function() {
          return H.nonce;
        },
        clientOnly: x.clientOnly,
        layer: g,
        // antd is always at top of styles
        order: x.order || -999
      };
      typeof i == "function" && Qe(A(A({}, Y), {}, {
        clientOnly: !1,
        path: ["Shared", E]
      }), function() {
        return i(k, {
          prefix: {
            rootPrefixCls: E,
            iconPrefixCls: $
          },
          csp: H
        });
      });
      var je = Qe(A(A({}, Y), {}, {
        path: [I, v, $]
      }), function() {
        if (x.injectStyle === !1)
          return [];
        var W = _n(k), q = W.token, te = W.flush, X = pt(C, j, b), re = ".".concat(v), Ke = gt(C, j, X, {
          deprecatedTokens: x.deprecatedTokens
        });
        L && X && N(X) === "object" && Object.keys(X).forEach(function(Ye) {
          X[Ye] = "var(".concat(Ie(Ye, dt(C, L.prefix)), ")");
        });
        var qe = Ue(q, {
          componentCls: re,
          prefixCls: v,
          iconCls: ".".concat($),
          antCls: ".".concat(E),
          calc: V,
          // @ts-ignore
          max: ee,
          // @ts-ignore
          min: ae
        }, L ? X : Ke), zt = S(qe, {
          hashId: P,
          prefixCls: v,
          rootPrefixCls: E,
          iconPrefixCls: $
        });
        te(C, Ke);
        var Ft = typeof s == "function" ? s(qe, v, m, x.resetFont) : null;
        return [x.resetStyle === !1 ? null : Ft, zt];
      });
      return [je, P];
    };
  }
  function u(d, S, b) {
    var x = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = f(d, S, b, A({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, x)), y = function(I) {
      var g = I.prefixCls, v = I.rootCls, m = v === void 0 ? g : v;
      return p(g, m), null;
    };
    return y;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: u,
    genComponentStyleHook: f
  };
}
const jn = {
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
}, In = Object.assign(Object.assign({}, jn), {
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
}), B = Math.round;
function De(t, e) {
  const r = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = r.map((n) => parseFloat(n));
  for (let n = 0; n < 3; n += 1)
    o[n] = e(o[n] || 0, r[n] || "", n);
  return r[3] ? o[3] = r[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const yt = (t, e, r) => r === 0 ? t : t / 100;
function ne(t, e) {
  const r = e || 255;
  return t > r ? r : t < 0 ? 0 : t;
}
class G {
  constructor(e) {
    R(this, "isValid", !0), R(this, "r", 0), R(this, "g", 0), R(this, "b", 0), R(this, "a", 1), R(this, "_h", void 0), R(this, "_s", void 0), R(this, "_l", void 0), R(this, "_v", void 0), R(this, "_max", void 0), R(this, "_min", void 0), R(this, "_brightness", void 0);
    function r(o) {
      return o[0] in e && o[1] in e && o[2] in e;
    }
    if (e) if (typeof e == "string") {
      let n = function(i) {
        return o.startsWith(i);
      };
      const o = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : n("rgb") ? this.fromRgbString(o) : n("hsl") ? this.fromHslString(o) : (n("hsv") || n("hsb")) && this.fromHsvString(o);
    } else if (e instanceof G)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (r("rgb"))
      this.r = ne(e.r), this.g = ne(e.g), this.b = ne(e.b), this.a = typeof e.a == "number" ? ne(e.a, 1) : 1;
    else if (r("hsl"))
      this.fromHsl(e);
    else if (r("hsv"))
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
    const r = this.toHsv();
    return r.h = e, this._c(r);
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
    const r = e(this.r), o = e(this.g), n = e(this.b);
    return 0.2126 * r + 0.7152 * o + 0.0722 * n;
  }
  getHue() {
    if (typeof this._h > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._h = 0 : this._h = B(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
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
    const r = this.getHue(), o = this.getSaturation();
    let n = this.getLightness() - e / 100;
    return n < 0 && (n = 0), this._c({
      h: r,
      s: o,
      l: n,
      a: this.a
    });
  }
  lighten(e = 10) {
    const r = this.getHue(), o = this.getSaturation();
    let n = this.getLightness() + e / 100;
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
  mix(e, r = 50) {
    const o = this._c(e), n = r / 100, i = (a) => (o[a] - this[a]) * n + this[a], s = {
      r: B(i("r")),
      g: B(i("g")),
      b: B(i("b")),
      a: B(i("a") * 100) / 100
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
    const r = this._c(e), o = this.a + r.a * (1 - this.a), n = (i) => B((this[i] * this.a + r[i] * r.a * (1 - this.a)) / o);
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
  equals(e) {
    return this.r === e.r && this.g === e.g && this.b === e.b && this.a === e.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let e = "#";
    const r = (this.r || 0).toString(16);
    e += r.length === 2 ? r : "0" + r;
    const o = (this.g || 0).toString(16);
    e += o.length === 2 ? o : "0" + o;
    const n = (this.b || 0).toString(16);
    if (e += n.length === 2 ? n : "0" + n, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = B(this.a * 255).toString(16);
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
    const e = this.getHue(), r = B(this.getSaturation() * 100), o = B(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${e},${r}%,${o}%,${this.a})` : `hsl(${e},${r}%,${o}%)`;
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
  _sc(e, r, o) {
    const n = this.clone();
    return n[e] = ne(r, o), n;
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
    const r = e.replace("#", "");
    function o(n, i) {
      return parseInt(r[n] + r[i || n], 16);
    }
    r.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = r[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = r[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: e,
    s: r,
    l: o,
    a: n
  }) {
    if (this._h = e % 360, this._s = r, this._l = o, this.a = typeof n == "number" ? n : 1, r <= 0) {
      const d = B(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let i = 0, s = 0, a = 0;
    const c = e / 60, l = (1 - Math.abs(2 * o - 1)) * r, f = l * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (i = l, s = f) : c >= 1 && c < 2 ? (i = f, s = l) : c >= 2 && c < 3 ? (s = l, a = f) : c >= 3 && c < 4 ? (s = f, a = l) : c >= 4 && c < 5 ? (i = f, a = l) : c >= 5 && c < 6 && (i = l, a = f);
    const u = o - l / 2;
    this.r = B((i + u) * 255), this.g = B((s + u) * 255), this.b = B((a + u) * 255);
  }
  fromHsv({
    h: e,
    s: r,
    v: o,
    a: n
  }) {
    this._h = e % 360, this._s = r, this._v = o, this.a = typeof n == "number" ? n : 1;
    const i = B(o * 255);
    if (this.r = i, this.g = i, this.b = i, r <= 0)
      return;
    const s = e / 60, a = Math.floor(s), c = s - a, l = B(o * (1 - r) * 255), f = B(o * (1 - r * c) * 255), u = B(o * (1 - r * (1 - c)) * 255);
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
  fromHsvString(e) {
    const r = De(e, yt);
    this.fromHsv({
      h: r[0],
      s: r[1],
      v: r[2],
      a: r[3]
    });
  }
  fromHslString(e) {
    const r = De(e, yt);
    this.fromHsl({
      h: r[0],
      s: r[1],
      l: r[2],
      a: r[3]
    });
  }
  fromRgbString(e) {
    const r = De(e, (o, n) => (
      // Convert percentage to number. e.g. 50% -> 128
      n.includes("%") ? B(o / 100 * 255) : o
    ));
    this.r = r[0], this.g = r[1], this.b = r[2], this.a = r[3];
  }
}
function Be(t) {
  return t >= 0 && t <= 255;
}
function ce(t, e) {
  const {
    r,
    g: o,
    b: n,
    a: i
  } = new G(t).toRgb();
  if (i < 1)
    return t;
  const {
    r: s,
    g: a,
    b: c
  } = new G(e).toRgb();
  for (let l = 0.01; l <= 1; l += 0.01) {
    const f = Math.round((r - s * (1 - l)) / l), u = Math.round((o - a * (1 - l)) / l), d = Math.round((n - c * (1 - l)) / l);
    if (Be(f) && Be(u) && Be(d))
      return new G({
        r: f,
        g: u,
        b: d,
        a: Math.round(l * 100) / 100
      }).toRgbString();
  }
  return new G({
    r,
    g: o,
    b: n,
    a: 1
  }).toRgbString();
}
var kn = function(t, e) {
  var r = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (r[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var n = 0, o = Object.getOwnPropertySymbols(t); n < o.length; n++)
    e.indexOf(o[n]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[n]) && (r[o[n]] = t[o[n]]);
  return r;
};
function Ln(t) {
  const {
    override: e
  } = t, r = kn(t, ["override"]), o = Object.assign({}, e);
  Object.keys(In).forEach((d) => {
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
    colorSplit: ce(n.colorBorderSecondary, n.colorBgContainer),
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
    colorErrorOutline: ce(n.colorErrorBg, n.colorBgContainer),
    colorWarningOutline: ce(n.colorWarningBg, n.colorBgContainer),
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
    controlOutline: ce(n.colorPrimaryBg, n.colorBgContainer),
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
      0 1px 2px -2px ${new G("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new G("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new G("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const $n = {
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
}, Dn = {
  motionBase: !0,
  motionUnit: !0
}, Bn = rr(Ae.defaultAlgorithm), Hn = {
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
}, Bt = (t, e, r) => {
  const o = r.getDerivativeToken(t), {
    override: n,
    ...i
  } = e;
  let s = {
    ...o,
    override: n
  };
  return s = Ln(s), i && Object.entries(i).forEach(([a, c]) => {
    const {
      theme: l,
      ...f
    } = c;
    let u = f;
    l && (u = Bt({
      ...s,
      ...f
    }, {
      override: f
    }, l)), s[a] = u;
  }), s;
};
function An() {
  const {
    token: t,
    hashed: e,
    theme: r = Bn,
    override: o,
    cssVar: n
  } = h.useContext(Ae._internalContext), [i, s, a] = nr(r, [Ae.defaultSeed, t], {
    salt: `${Ur}-${e || ""}`,
    override: o,
    getComputedToken: Bt,
    cssVar: n && {
      prefix: n.prefix,
      key: n.key,
      unitless: $n,
      ignore: Dn,
      preserve: Hn
    }
  });
  return [r, a, e ? s : "", i, n];
}
const {
  genStyleHooks: zn
} = Rn({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = pe();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, r, o, n] = An();
    return {
      theme: t,
      realToken: e,
      hashId: r,
      token: o,
      cssVar: n
    };
  },
  useCSP: () => {
    const {
      csp: t
    } = pe();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
function le(t) {
  return typeof t == "string";
}
function Fn(t, e) {
  let r = 0;
  const o = Math.min(t.length, e.length);
  for (; r < o && t[r] === e[r]; )
    r++;
  return r;
}
const Nn = (t, e, r, o) => {
  const n = _.useRef(""), [i, s] = _.useState(1), a = e && le(t);
  return Sn(() => {
    if (!a && le(t))
      s(t.length);
    else if (le(t) && le(n.current) && t.indexOf(n.current) !== 0) {
      if (!t || !n.current) {
        s(1);
        return;
      }
      const l = Fn(t, n.current);
      s(l === 0 ? 1 : l + 1);
    }
    n.current = t;
  }, [t]), _.useEffect(() => {
    if (a && i < t.length) {
      const l = setTimeout(() => {
        s((f) => f + r);
      }, o);
      return () => {
        clearTimeout(l);
      };
    }
  }, [i, e, t]), [a ? t.slice(0, i) : t, a && i < t.length];
};
function Xn(t) {
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
const Vn = ({
  prefixCls: t
}) => /* @__PURE__ */ h.createElement("span", {
  className: `${t}-dot`
}, /* @__PURE__ */ h.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-1"
}), /* @__PURE__ */ h.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-2"
}), /* @__PURE__ */ h.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-3"
})), Wn = (t) => {
  const {
    componentCls: e,
    paddingSM: r,
    padding: o
  } = t;
  return {
    [e]: {
      [`${e}-content`]: {
        // Shared: filled, outlined, shadow
        "&-filled,&-outlined,&-shadow": {
          padding: `${ie(r)} ${ie(o)}`,
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
}, Un = (t) => {
  const {
    componentCls: e,
    fontSize: r,
    lineHeight: o,
    paddingSM: n,
    padding: i,
    calc: s
  } = t, a = s(r).mul(o).div(2).add(n).equal(), c = `${e}-content`;
  return {
    [e]: {
      [c]: {
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
      [`&-start ${c}-corner`]: {
        borderStartStartRadius: t.borderRadiusXS
      },
      [`&-end ${c}-corner`]: {
        borderStartEndRadius: t.borderRadiusXS
      }
    }
  };
}, Gn = (t) => {
  const {
    componentCls: e,
    padding: r
  } = t;
  return {
    [`${e}-list`]: {
      display: "flex",
      flexDirection: "column",
      gap: r,
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
}, Kn = new Ct("loadingMove", {
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
}), qn = new Ct("cursorBlink", {
  "0%": {
    opacity: 1
  },
  "50%": {
    opacity: 0
  },
  "100%": {
    opacity: 1
  }
}), Yn = (t) => {
  const {
    componentCls: e,
    fontSize: r,
    lineHeight: o,
    paddingSM: n,
    colorText: i,
    calc: s
  } = t;
  return {
    [e]: {
      display: "flex",
      columnGap: n,
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
        animationName: qn,
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
        fontSize: r,
        lineHeight: o,
        color: t.colorText
      },
      [`& ${e}-header`]: {
        marginBottom: t.paddingXXS
      },
      [`& ${e}-footer`]: {
        marginTop: n
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
        color: i,
        fontSize: t.fontSize,
        lineHeight: t.lineHeight,
        minHeight: s(n).mul(2).add(s(o).mul(r)).equal(),
        wordBreak: "break-word",
        [`& ${e}-dot`]: {
          position: "relative",
          height: "100%",
          display: "flex",
          alignItems: "center",
          columnGap: t.marginXS,
          padding: `0 ${ie(t.paddingXXS)}`,
          "&-item": {
            backgroundColor: t.colorPrimary,
            borderRadius: "100%",
            width: 4,
            height: 4,
            animationName: Kn,
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
}, Qn = () => ({}), Ht = zn("Bubble", (t) => {
  const e = Ue(t, {});
  return [Yn(e), Gn(e), Wn(e), Un(e)];
}, Qn), At = /* @__PURE__ */ h.createContext({}), Zn = (t, e) => {
  const {
    prefixCls: r,
    className: o,
    rootClassName: n,
    style: i,
    classNames: s = {},
    styles: a = {},
    avatar: c,
    placement: l = "start",
    loading: f = !1,
    loadingRender: u,
    typing: d,
    content: S = "",
    messageRender: b,
    variant: x = "filled",
    shape: p,
    onTypingComplete: y,
    header: C,
    footer: I,
    _key: g,
    ...v
  } = t, {
    onUpdate: m
  } = h.useContext(At), w = h.useRef(null);
  h.useImperativeHandle(e, () => ({
    nativeElement: w.current
  }));
  const {
    direction: O,
    getPrefixCls: j
  } = pe(), P = j("bubble", r), k = sn("bubble"), [L, M, E, $] = Xn(d), [H, z] = Nn(S, L, M, E);
  h.useEffect(() => {
    m == null || m();
  }, [H]);
  const V = h.useRef(!1);
  h.useEffect(() => {
    !z && !f ? V.current || (V.current = !0, y == null || y()) : V.current = !1;
  }, [z, f]);
  const [K, ee, ae] = Ht(P), Y = Q(P, n, k.className, o, ee, ae, `${P}-${l}`, {
    [`${P}-rtl`]: O === "rtl",
    [`${P}-typing`]: z && !f && !b && !$
  }), je = h.useMemo(() => /* @__PURE__ */ h.isValidElement(c) ? c : /* @__PURE__ */ h.createElement(er, c), [c]), W = h.useMemo(() => b ? b(H) : H, [H, b]), q = (re) => typeof re == "function" ? re(H, {
    key: g
  }) : re;
  let te;
  f ? te = u ? u() : /* @__PURE__ */ h.createElement(Vn, {
    prefixCls: P
  }) : te = /* @__PURE__ */ h.createElement(h.Fragment, null, W, z && $);
  let X = /* @__PURE__ */ h.createElement("div", {
    style: {
      ...k.styles.content,
      ...a.content
    },
    className: Q(`${P}-content`, `${P}-content-${x}`, p && `${P}-content-${p}`, k.classNames.content, s.content)
  }, te);
  return (C || I) && (X = /* @__PURE__ */ h.createElement("div", {
    className: `${P}-content-wrapper`
  }, C && /* @__PURE__ */ h.createElement("div", {
    className: Q(`${P}-header`, k.classNames.header, s.header),
    style: {
      ...k.styles.header,
      ...a.header
    }
  }, q(C)), X, I && /* @__PURE__ */ h.createElement("div", {
    className: Q(`${P}-footer`, k.classNames.footer, s.footer),
    style: {
      ...k.styles.footer,
      ...a.footer
    }
  }, q(I)))), K(/* @__PURE__ */ h.createElement("div", J({
    style: {
      ...k.style,
      ...i
    },
    className: Y
  }, v, {
    ref: w
  }), c && /* @__PURE__ */ h.createElement("div", {
    style: {
      ...k.styles.avatar,
      ...a.avatar
    },
    className: Q(`${P}-avatar`, k.classNames.avatar, s.avatar)
  }, je), X));
}, Ge = /* @__PURE__ */ h.forwardRef(Zn);
function Jn(t, e) {
  const r = _.useCallback((o, n) => typeof e == "function" ? e(o, n) : e ? e[o.role] || {} : {}, [e]);
  return _.useMemo(() => (t || []).map((o, n) => {
    const i = o.key ?? `preset_${n}`;
    return {
      ...r(o, n),
      ...o,
      key: i
    };
  }), [t, r]);
}
const eo = ({
  _key: t,
  ...e
}, r) => /* @__PURE__ */ _.createElement(Ge, J({}, e, {
  _key: t,
  ref: (o) => {
    var n;
    o ? r.current[t] = o : (n = r.current) == null || delete n[t];
  }
})), to = /* @__PURE__ */ _.memo(/* @__PURE__ */ _.forwardRef(eo)), ro = 1, no = (t, e) => {
  const {
    prefixCls: r,
    rootClassName: o,
    className: n,
    items: i,
    autoScroll: s = !0,
    roles: a,
    onScroll: c,
    ...l
  } = t, f = rn(l, {
    attr: !0,
    aria: !0
  }), u = _.useRef(null), d = _.useRef({}), {
    getPrefixCls: S
  } = pe(), b = S("bubble", r), x = `${b}-list`, [p, y, C] = Ht(b), [I, g] = _.useState(!1);
  _.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const v = Jn(i, a), [m, w] = _.useState(!0), [O, j] = _.useState(0), P = (M) => {
    const E = M.target;
    w(E.scrollHeight - Math.abs(E.scrollTop) - E.clientHeight <= ro), c == null || c(M);
  };
  _.useEffect(() => {
    s && u.current && m && u.current.scrollTo({
      top: u.current.scrollHeight
    });
  }, [O]), _.useEffect(() => {
    var M;
    if (s) {
      const E = (M = v[v.length - 2]) == null ? void 0 : M.key, $ = d.current[E];
      if ($) {
        const {
          nativeElement: H
        } = $, {
          top: z,
          bottom: V
        } = H.getBoundingClientRect(), {
          top: K,
          bottom: ee
        } = u.current.getBoundingClientRect();
        z < ee && V > K && (j((Y) => Y + 1), w(!0));
      }
    }
  }, [v.length]), _.useImperativeHandle(e, () => ({
    nativeElement: u.current,
    scrollTo: ({
      key: M,
      offset: E,
      behavior: $ = "smooth",
      block: H
    }) => {
      if (typeof E == "number")
        u.current.scrollTo({
          top: E,
          behavior: $
        });
      else if (M !== void 0) {
        const z = d.current[M];
        if (z) {
          const V = v.findIndex((K) => K.key === M);
          w(V === v.length - 1), z.nativeElement.scrollIntoView({
            behavior: $,
            block: H
          });
        }
      }
    }
  }));
  const k = yn(() => {
    s && j((M) => M + 1);
  }), L = _.useMemo(() => ({
    onUpdate: k
  }), []);
  return p(/* @__PURE__ */ _.createElement(At.Provider, {
    value: L
  }, /* @__PURE__ */ _.createElement("div", J({}, f, {
    className: Q(x, o, n, y, C, {
      [`${x}-reach-end`]: m
    }),
    ref: u,
    onScroll: P
  }), v.map(({
    key: M,
    ...E
  }) => /* @__PURE__ */ _.createElement(to, J({}, E, {
    key: M,
    _key: M,
    ref: d,
    typing: I ? E.typing : !1
  }))))));
}, oo = /* @__PURE__ */ _.forwardRef(no);
Ge.List = oo;
function io(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function so(t, e = !1) {
  try {
    if (Yt(t))
      return t;
    if (e && !io(t))
      return;
    if (typeof t == "string") {
      let r = t.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function ue(t, e) {
  return xt(() => so(t, e), [t, e]);
}
const ao = ({
  children: t,
  ...e
}) => /* @__PURE__ */ D.jsx(D.Fragment, {
  children: t(e)
});
function co(t) {
  return h.createElement(ao, {
    children: t
  });
}
function vt(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? co((r) => /* @__PURE__ */ D.jsx(Zt, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ D.jsx(U, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...r
    })
  })) : /* @__PURE__ */ D.jsx(U, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function St({
  key: t,
  slots: e,
  targets: r
}, o) {
  return e[t] ? (...n) => r ? r.map((i, s) => /* @__PURE__ */ D.jsx(h.Fragment, {
    children: vt(i, {
      clone: !0,
      params: n,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ D.jsx(D.Fragment, {
    children: vt(e[t], {
      clone: !0,
      params: n,
      forceClone: !0
    })
  }) : void 0;
}
const fo = Fr(({
  loadingRender: t,
  messageRender: e,
  slots: r,
  setSlotParams: o,
  children: n,
  ...i
}) => {
  const s = ue(t), a = ue(e), c = ue(i.header, !0), l = ue(i.footer, !0), f = xt(() => {
    var u, d;
    return r.avatar ? /* @__PURE__ */ D.jsx(U, {
      slot: r.avatar
    }) : r["avatar.icon"] || r["avatar.src"] ? {
      ...i.avatar || {},
      icon: r["avatar.icon"] ? /* @__PURE__ */ D.jsx(U, {
        slot: r["avatar.icon"]
      }) : (u = i.avatar) == null ? void 0 : u.icon,
      src: r["avatar.src"] ? /* @__PURE__ */ D.jsx(U, {
        slot: r["avatar.src"]
      }) : (d = i.avatar) == null ? void 0 : d.src
    } : i.avatar;
  }, [i.avatar, r]);
  return /* @__PURE__ */ D.jsxs(D.Fragment, {
    children: [/* @__PURE__ */ D.jsx("div", {
      style: {
        display: "none"
      },
      children: n
    }), /* @__PURE__ */ D.jsx(Ge, {
      ...i,
      avatar: f,
      typing: r["typing.suffix"] ? {
        ...me(i.typing) ? i.typing : {},
        suffix: /* @__PURE__ */ D.jsx(U, {
          slot: r["typing.suffix"]
        })
      } : i.typing,
      content: r.content ? /* @__PURE__ */ D.jsx(U, {
        slot: r.content
      }) : i.content,
      footer: r.footer ? /* @__PURE__ */ D.jsx(U, {
        slot: r.footer
      }) : l || i.footer,
      header: r.header ? /* @__PURE__ */ D.jsx(U, {
        slot: r.header
      }) : c || i.header,
      loadingRender: r.loadingRender ? St({
        slots: r,
        key: "loadingRender"
      }) : s,
      messageRender: r.messageRender ? St({
        slots: r,
        key: "messageRender"
      }) : a
    })]
  });
});
export {
  fo as Bubble,
  fo as default
};
