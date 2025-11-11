import { i as gr, a as Pt, r as hr, Z as We, g as vr, t as yr, s as ke, c as te, b as br } from "./Index-BRYZJUOL.js";
const k = window.ms_globals.React, c = window.ms_globals.React, nt = window.ms_globals.React.useMemo, Ze = window.ms_globals.React.useState, xe = window.ms_globals.React.useEffect, fr = window.ms_globals.React.forwardRef, be = window.ms_globals.React.useRef, dr = window.ms_globals.React.version, pr = window.ms_globals.React.isValidElement, mr = window.ms_globals.React.useLayoutEffect, Wt = window.ms_globals.ReactDOM, Qe = window.ms_globals.ReactDOM.createPortal, Sr = window.ms_globals.internalContext.useContextPropsContext, wr = window.ms_globals.internalContext.ContextPropsProvider, xr = window.ms_globals.antd.ConfigProvider, Ye = window.ms_globals.antd.theme, Mn = window.ms_globals.antd.Upload, Er = window.ms_globals.antd.Progress, Cr = window.ms_globals.antd.Image, vt = window.ms_globals.antd.Button, _r = window.ms_globals.antd.Flex, yt = window.ms_globals.antd.Typography, On = window.ms_globals.antdIcons.FileTextFilled, Rr = window.ms_globals.antdIcons.CloseCircleFilled, Lr = window.ms_globals.antdIcons.FileExcelFilled, Ir = window.ms_globals.antdIcons.FileImageFilled, Tr = window.ms_globals.antdIcons.FileMarkdownFilled, Pr = window.ms_globals.antdIcons.FilePdfFilled, Mr = window.ms_globals.antdIcons.FilePptFilled, Or = window.ms_globals.antdIcons.FileWordFilled, Fr = window.ms_globals.antdIcons.FileZipFilled, Ar = window.ms_globals.antdIcons.PlusOutlined, kr = window.ms_globals.antdIcons.LeftOutlined, $r = window.ms_globals.antdIcons.RightOutlined, Gt = window.ms_globals.antdCssinjs.unit, bt = window.ms_globals.antdCssinjs.token2CSSVar, Kt = window.ms_globals.antdCssinjs.useStyleRegister, jr = window.ms_globals.antdCssinjs.useCSSVarRegister, Dr = window.ms_globals.antdCssinjs.createTheme, Nr = window.ms_globals.antdCssinjs.useCacheToken;
var Hr = /\s/;
function zr(e) {
  for (var t = e.length; t-- && Hr.test(e.charAt(t)); )
    ;
  return t;
}
var Ur = /^\s+/;
function Br(e) {
  return e && e.slice(0, zr(e) + 1).replace(Ur, "");
}
var qt = NaN, Vr = /^[-+]0x[0-9a-f]+$/i, Xr = /^0b[01]+$/i, Wr = /^0o[0-7]+$/i, Gr = parseInt;
function Zt(e) {
  if (typeof e == "number")
    return e;
  if (gr(e))
    return qt;
  if (Pt(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = Pt(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Br(e);
  var n = Xr.test(e);
  return n || Wr.test(e) ? Gr(e.slice(2), n ? 2 : 8) : Vr.test(e) ? qt : +e;
}
function Kr() {
}
var St = function() {
  return hr.Date.now();
}, qr = "Expected a function", Zr = Math.max, Qr = Math.min;
function Yr(e, t, n) {
  var o, r, i, s, a, l, u = 0, p = !1, f = !1, d = !0;
  if (typeof e != "function")
    throw new TypeError(qr);
  t = Zt(t) || 0, Pt(n) && (p = !!n.leading, f = "maxWait" in n, i = f ? Zr(Zt(n.maxWait) || 0, t) : i, d = "trailing" in n ? !!n.trailing : d);
  function m(h) {
    var L = o, C = r;
    return o = r = void 0, u = h, s = e.apply(C, L), s;
  }
  function y(h) {
    return u = h, a = setTimeout(x, t), p ? m(h) : s;
  }
  function b(h) {
    var L = h - l, C = h - u, M = t - L;
    return f ? Qr(M, i - C) : M;
  }
  function g(h) {
    var L = h - l, C = h - u;
    return l === void 0 || L >= t || L < 0 || f && C >= i;
  }
  function x() {
    var h = St();
    if (g(h))
      return w(h);
    a = setTimeout(x, b(h));
  }
  function w(h) {
    return a = void 0, d && o ? m(h) : (o = r = void 0, s);
  }
  function S() {
    a !== void 0 && clearTimeout(a), u = 0, o = l = r = a = void 0;
  }
  function v() {
    return a === void 0 ? s : w(St());
  }
  function R() {
    var h = St(), L = g(h);
    if (o = arguments, r = this, l = h, L) {
      if (a === void 0)
        return y(l);
      if (f)
        return clearTimeout(a), a = setTimeout(x, t), m(l);
    }
    return a === void 0 && (a = setTimeout(x, t)), s;
  }
  return R.cancel = S, R.flush = v, R;
}
var Fn = {
  exports: {}
}, rt = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Jr = c, eo = Symbol.for("react.element"), to = Symbol.for("react.fragment"), no = Object.prototype.hasOwnProperty, ro = Jr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, oo = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function An(e, t, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (o in t) no.call(t, o) && !oo.hasOwnProperty(o) && (r[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) r[o] === void 0 && (r[o] = t[o]);
  return {
    $$typeof: eo,
    type: e,
    key: i,
    ref: s,
    props: r,
    _owner: ro.current
  };
}
rt.Fragment = to;
rt.jsx = An;
rt.jsxs = An;
Fn.exports = rt;
var Y = Fn.exports;
const {
  SvelteComponent: io,
  assign: Qt,
  binding_callbacks: Yt,
  check_outros: so,
  children: kn,
  claim_element: $n,
  claim_space: ao,
  component_subscribe: Jt,
  compute_slots: lo,
  create_slot: co,
  detach: Re,
  element: jn,
  empty: en,
  exclude_internal_props: tn,
  get_all_dirty_from_scope: uo,
  get_slot_changes: fo,
  group_outros: po,
  init: mo,
  insert_hydration: Ge,
  safe_not_equal: go,
  set_custom_element_data: Dn,
  space: ho,
  transition_in: Ke,
  transition_out: Mt,
  update_slot_base: vo
} = window.__gradio__svelte__internal, {
  beforeUpdate: yo,
  getContext: bo,
  onDestroy: So,
  setContext: wo
} = window.__gradio__svelte__internal;
function nn(e) {
  let t, n;
  const o = (
    /*#slots*/
    e[7].default
  ), r = co(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = jn("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      t = $n(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = kn(t);
      r && r.l(s), s.forEach(Re), this.h();
    },
    h() {
      Dn(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      Ge(i, t, s), r && r.m(t, null), e[9](t), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && vo(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? fo(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : uo(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (Ke(r, i), n = !0);
    },
    o(i) {
      Mt(r, i), n = !1;
    },
    d(i) {
      i && Re(t), r && r.d(i), e[9](null);
    }
  };
}
function xo(e) {
  let t, n, o, r, i = (
    /*$$slots*/
    e[4].default && nn(e)
  );
  return {
    c() {
      t = jn("react-portal-target"), n = ho(), i && i.c(), o = en(), this.h();
    },
    l(s) {
      t = $n(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), kn(t).forEach(Re), n = ao(s), i && i.l(s), o = en(), this.h();
    },
    h() {
      Dn(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      Ge(s, t, a), e[8](t), Ge(s, n, a), i && i.m(s, a), Ge(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && Ke(i, 1)) : (i = nn(s), i.c(), Ke(i, 1), i.m(o.parentNode, o)) : i && (po(), Mt(i, 1, 1, () => {
        i = null;
      }), so());
    },
    i(s) {
      r || (Ke(i), r = !0);
    },
    o(s) {
      Mt(i), r = !1;
    },
    d(s) {
      s && (Re(t), Re(n), Re(o)), e[8](null), i && i.d(s);
    }
  };
}
function rn(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function Eo(e, t, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = lo(i);
  let {
    svelteInit: l
  } = t;
  const u = We(rn(t)), p = We();
  Jt(e, p, (v) => n(0, o = v));
  const f = We();
  Jt(e, f, (v) => n(1, r = v));
  const d = [], m = bo("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: b,
    subSlotIndex: g
  } = vr() || {}, x = l({
    parent: m,
    props: u,
    target: p,
    slot: f,
    slotKey: y,
    slotIndex: b,
    subSlotIndex: g,
    onDestroy(v) {
      d.push(v);
    }
  });
  wo("$$ms-gr-react-wrapper", x), yo(() => {
    u.set(rn(t));
  }), So(() => {
    d.forEach((v) => v());
  });
  function w(v) {
    Yt[v ? "unshift" : "push"](() => {
      o = v, p.set(o);
    });
  }
  function S(v) {
    Yt[v ? "unshift" : "push"](() => {
      r = v, f.set(r);
    });
  }
  return e.$$set = (v) => {
    n(17, t = Qt(Qt({}, t), tn(v))), "svelteInit" in v && n(5, l = v.svelteInit), "$$scope" in v && n(6, s = v.$$scope);
  }, t = tn(t), [o, r, p, f, a, l, s, i, w, S];
}
class Co extends io {
  constructor(t) {
    super(), mo(this, t, Eo, xo, go, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ws
} = window.__gradio__svelte__internal, on = window.ms_globals.rerender, wt = window.ms_globals.tree;
function _o(e, t = {}) {
  function n(o) {
    const r = We(), i = new Co({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, l = s.parent ?? wt;
          return l.nodes = [...l.nodes, a], on({
            createPortal: Qe,
            node: wt
          }), s.onDestroy(() => {
            l.nodes = l.nodes.filter((u) => u.svelteInstance !== r), on({
              createPortal: Qe,
              node: wt
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
function Ro(e) {
  const [t, n] = Ze(() => ke(e));
  return xe(() => {
    let o = !0;
    return e.subscribe((i) => {
      o && (o = !1, i === t) || n(i);
    });
  }, [e]), t;
}
function Lo(e) {
  const t = nt(() => yr(e, (n) => n), [e]);
  return Ro(t);
}
const Io = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function To(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const o = e[n];
    return t[n] = Po(n, o), t;
  }, {}) : {};
}
function Po(e, t) {
  return typeof t == "number" && !Io.includes(e) ? t + "px" : t;
}
function Ot(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const r = c.Children.toArray(e._reactElement.props.children).map((i) => {
      if (c.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Ot(i.props.el);
        return c.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...c.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(Qe(c.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: r
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((r) => {
    e.getEventListeners(r).forEach(({
      listener: s,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, s, l);
    });
  });
  const o = Array.from(e.childNodes);
  for (let r = 0; r < o.length; r++) {
    const i = o[r];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Ot(i);
      t.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function Mo(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const $e = fr(({
  slot: e,
  clone: t,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = be(), [a, l] = Ze([]), {
    forceClone: u
  } = Sr(), p = u ? !0 : t;
  return xe(() => {
    var b;
    if (!s.current || !e)
      return;
    let f = e;
    function d() {
      let g = f;
      if (f.tagName.toLowerCase() === "svelte-slot" && f.children.length === 1 && f.children[0] && (g = f.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), Mo(i, g), n && g.classList.add(...n.split(" ")), o) {
        const x = To(o);
        Object.keys(x).forEach((w) => {
          g.style[w] = x[w];
        });
      }
    }
    let m = null, y = null;
    if (p && window.MutationObserver) {
      let g = function() {
        var v, R, h;
        (v = s.current) != null && v.contains(f) && ((R = s.current) == null || R.removeChild(f));
        const {
          portals: w,
          clonedElement: S
        } = Ot(e);
        f = S, l(w), f.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          d();
        }, 50), (h = s.current) == null || h.appendChild(f);
      };
      g();
      const x = Yr(() => {
        g(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      m = new window.MutationObserver(x), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      f.style.display = "contents", d(), (b = s.current) == null || b.appendChild(f);
    return () => {
      var g, x;
      f.style.display = "", (g = s.current) != null && g.contains(f) && ((x = s.current) == null || x.removeChild(f)), m == null || m.disconnect();
    };
  }, [e, p, n, o, i, r, u]), c.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Oo = "1.6.1";
function Te() {
  return Te = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = arguments[t];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (e[o] = n[o]);
    }
    return e;
  }, Te.apply(null, arguments);
}
function je(e) {
  "@babel/helpers - typeof";
  return je = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, je(e);
}
const Fo = /* @__PURE__ */ c.createContext({}), Ao = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, ko = (e) => {
  const t = c.useContext(Fo);
  return c.useMemo(() => ({
    ...Ao,
    ...t[e]
  }), [t[e]]);
};
function Je() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = c.useContext(xr.ConfigContext);
  return {
    theme: r,
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o
  };
}
function ne(e) {
  "@babel/helpers - typeof";
  return ne = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, ne(e);
}
function $o(e) {
  if (Array.isArray(e)) return e;
}
function jo(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], l = !0, u = !1;
    try {
      if (i = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = i.call(n)).done) && (a.push(o.value), a.length !== t); l = !0) ;
    } catch (p) {
      u = !0, r = p;
    } finally {
      try {
        if (!l && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (u) throw r;
      }
    }
    return a;
  }
}
function sn(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, o = Array(t); n < t; n++) o[n] = e[n];
  return o;
}
function Do(e, t) {
  if (e) {
    if (typeof e == "string") return sn(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? sn(e, t) : void 0;
  }
}
function No() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function le(e, t) {
  return $o(e) || jo(e, t) || Do(e, t) || No();
}
function Ho(e, t) {
  if (ne(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(e, t);
    if (ne(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function Nn(e) {
  var t = Ho(e, "string");
  return ne(t) == "symbol" ? t : t + "";
}
function T(e, t, n) {
  return (t = Nn(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function an(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(e, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function I(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? an(Object(n), !0).forEach(function(o) {
      T(e, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : an(Object(n)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return e;
}
function Me(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function ln(e, t) {
  for (var n = 0; n < t.length; n++) {
    var o = t[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, Nn(o.key), o);
  }
}
function Oe(e, t, n) {
  return t && ln(e.prototype, t), n && ln(e, n), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function Ee(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function Ft(e, t) {
  return Ft = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Ft(e, t);
}
function ot(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && Ft(e, t);
}
function et(e) {
  return et = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, et(e);
}
function Hn() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Hn = function() {
    return !!e;
  })();
}
function zo(e, t) {
  if (t && (ne(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Ee(e);
}
function it(e) {
  var t = Hn();
  return function() {
    var n, o = et(e);
    if (t) {
      var r = et(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return zo(this, n);
  };
}
var zn = /* @__PURE__ */ Oe(function e() {
  Me(this, e);
}), Un = "CALC_UNIT", Uo = new RegExp(Un, "g");
function xt(e) {
  return typeof e == "number" ? "".concat(e).concat(Un) : e;
}
var Bo = /* @__PURE__ */ function(e) {
  ot(n, e);
  var t = it(n);
  function n(o, r) {
    var i;
    Me(this, n), i = t.call(this), T(Ee(i), "result", ""), T(Ee(i), "unitlessCssVar", void 0), T(Ee(i), "lowPriority", void 0);
    var s = ne(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = xt(o) : s === "string" && (i.result = o), i;
  }
  return Oe(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(xt(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(xt(r))), this.lowPriority = !0, this;
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
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(u) {
        return i.result.includes(u);
      }) && (l = !1), this.result = this.result.replace(Uo, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(zn), Vo = /* @__PURE__ */ function(e) {
  ot(n, e);
  var t = it(n);
  function n(o) {
    var r;
    return Me(this, n), r = t.call(this), T(Ee(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return Oe(n, [{
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
}(zn), Xo = function(t, n) {
  var o = t === "css" ? Bo : Vo;
  return function(r) {
    return new o(r, n);
  };
}, cn = function(t, n) {
  return "".concat([n, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function Pe(e) {
  var t = k.useRef();
  t.current = e;
  var n = k.useCallback(function() {
    for (var o, r = arguments.length, i = new Array(r), s = 0; s < r; s++)
      i[s] = arguments[s];
    return (o = t.current) === null || o === void 0 ? void 0 : o.call.apply(o, [t].concat(i));
  }, []);
  return n;
}
function Wo(e) {
  if (Array.isArray(e)) return e;
}
function Go(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], l = !0, u = !1;
    try {
      if (i = (n = n.call(e)).next, t !== 0) for (; !(l = (o = i.call(n)).done) && (a.push(o.value), a.length !== t); l = !0) ;
    } catch (p) {
      u = !0, r = p;
    } finally {
      try {
        if (!l && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (u) throw r;
      }
    }
    return a;
  }
}
function un(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, o = Array(t); n < t; n++) o[n] = e[n];
  return o;
}
function Ko(e, t) {
  if (e) {
    if (typeof e == "string") return un(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? un(e, t) : void 0;
  }
}
function qo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function tt(e, t) {
  return Wo(e) || Go(e, t) || Ko(e, t) || qo();
}
function st() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var fn = st() ? k.useLayoutEffect : k.useEffect, Zo = function(t, n) {
  var o = k.useRef(!0);
  fn(function() {
    return t(o.current);
  }, n), fn(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, dn = function(t, n) {
  Zo(function(o) {
    if (!o)
      return t();
  }, n);
};
function De(e) {
  var t = k.useRef(!1), n = k.useState(e), o = tt(n, 2), r = o[0], i = o[1];
  k.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, l) {
    l && t.current || i(a);
  }
  return [r, s];
}
function Et(e) {
  return e !== void 0;
}
function Qo(e, t) {
  var n = t || {}, o = n.defaultValue, r = n.value, i = n.onChange, s = n.postState, a = De(function() {
    return Et(r) ? r : Et(o) ? typeof o == "function" ? o() : o : typeof e == "function" ? e() : e;
  }), l = tt(a, 2), u = l[0], p = l[1], f = r !== void 0 ? r : u, d = s ? s(f) : f, m = Pe(i), y = De([f]), b = tt(y, 2), g = b[0], x = b[1];
  dn(function() {
    var S = g[0];
    u !== S && m(u, S);
  }, [g]), dn(function() {
    Et(r) || p(r);
  }, [r]);
  var w = Pe(function(S, v) {
    p(S, v), x([f], v);
  });
  return [d, w];
}
var Bn = {
  exports: {}
}, $ = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var zt = Symbol.for("react.element"), Ut = Symbol.for("react.portal"), at = Symbol.for("react.fragment"), lt = Symbol.for("react.strict_mode"), ct = Symbol.for("react.profiler"), ut = Symbol.for("react.provider"), ft = Symbol.for("react.context"), Yo = Symbol.for("react.server_context"), dt = Symbol.for("react.forward_ref"), pt = Symbol.for("react.suspense"), mt = Symbol.for("react.suspense_list"), gt = Symbol.for("react.memo"), ht = Symbol.for("react.lazy"), Jo = Symbol.for("react.offscreen"), Vn;
Vn = Symbol.for("react.module.reference");
function ce(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case zt:
        switch (e = e.type, e) {
          case at:
          case ct:
          case lt:
          case pt:
          case mt:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Yo:
              case ft:
              case dt:
              case ht:
              case gt:
              case ut:
                return e;
              default:
                return t;
            }
        }
      case Ut:
        return t;
    }
  }
}
$.ContextConsumer = ft;
$.ContextProvider = ut;
$.Element = zt;
$.ForwardRef = dt;
$.Fragment = at;
$.Lazy = ht;
$.Memo = gt;
$.Portal = Ut;
$.Profiler = ct;
$.StrictMode = lt;
$.Suspense = pt;
$.SuspenseList = mt;
$.isAsyncMode = function() {
  return !1;
};
$.isConcurrentMode = function() {
  return !1;
};
$.isContextConsumer = function(e) {
  return ce(e) === ft;
};
$.isContextProvider = function(e) {
  return ce(e) === ut;
};
$.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === zt;
};
$.isForwardRef = function(e) {
  return ce(e) === dt;
};
$.isFragment = function(e) {
  return ce(e) === at;
};
$.isLazy = function(e) {
  return ce(e) === ht;
};
$.isMemo = function(e) {
  return ce(e) === gt;
};
$.isPortal = function(e) {
  return ce(e) === Ut;
};
$.isProfiler = function(e) {
  return ce(e) === ct;
};
$.isStrictMode = function(e) {
  return ce(e) === lt;
};
$.isSuspense = function(e) {
  return ce(e) === pt;
};
$.isSuspenseList = function(e) {
  return ce(e) === mt;
};
$.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === at || e === ct || e === lt || e === pt || e === mt || e === Jo || typeof e == "object" && e !== null && (e.$$typeof === ht || e.$$typeof === gt || e.$$typeof === ut || e.$$typeof === ft || e.$$typeof === dt || e.$$typeof === Vn || e.getModuleId !== void 0);
};
$.typeOf = ce;
Bn.exports = $;
var Ct = Bn.exports, ei = Symbol.for("react.element"), ti = Symbol.for("react.transitional.element"), ni = Symbol.for("react.fragment");
function ri(e) {
  return (
    // Base object type
    e && je(e) === "object" && // React Element type
    (e.$$typeof === ei || e.$$typeof === ti) && // React Fragment type
    e.type === ni
  );
}
var oi = Number(dr.split(".")[0]), ii = function(t, n) {
  typeof t == "function" ? t(n) : je(t) === "object" && t && "current" in t && (t.current = n);
}, si = function(t) {
  var n, o;
  if (!t)
    return !1;
  if (Xn(t) && oi >= 19)
    return !0;
  var r = Ct.isMemo(t) ? t.type.type : t.type;
  return !(typeof r == "function" && !((n = r.prototype) !== null && n !== void 0 && n.render) && r.$$typeof !== Ct.ForwardRef || typeof t == "function" && !((o = t.prototype) !== null && o !== void 0 && o.render) && t.$$typeof !== Ct.ForwardRef);
};
function Xn(e) {
  return /* @__PURE__ */ pr(e) && !ri(e);
}
var ai = function(t) {
  if (t && Xn(t)) {
    var n = t;
    return n.props.propertyIsEnumerable("ref") ? n.props.ref : n.ref;
  }
  return null;
};
function pn(e, t, n, o) {
  var r = I({}, t[e]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var l = le(a, 2), u = l[0], p = l[1];
      if (r != null && r[u] || r != null && r[p]) {
        var f;
        (f = r[p]) !== null && f !== void 0 || (r[p] = r == null ? void 0 : r[u]);
      }
    });
  }
  var s = I(I({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Wn = typeof CSSINJS_STATISTIC < "u", At = !0;
function Bt() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
    t[n] = arguments[n];
  if (!Wn)
    return Object.assign.apply(Object, [{}].concat(t));
  At = !1;
  var o = {};
  return t.forEach(function(r) {
    if (ne(r) === "object") {
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
  }), At = !0, o;
}
var mn = {};
function li() {
}
var ci = function(t) {
  var n, o = t, r = li;
  return Wn && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(t, {
    get: function(s, a) {
      if (At) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var l;
    mn[s] = {
      global: Array.from(n),
      component: I(I({}, (l = mn[s]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function gn(e, t, n) {
  if (typeof n == "function") {
    var o;
    return n(Bt(t, (o = t[e]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function ui(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return Gt(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return Gt(i);
      }).join(","), ")");
    }
  };
}
var fi = 1e3 * 60 * 10, di = /* @__PURE__ */ function() {
  function e() {
    Me(this, e), T(this, "map", /* @__PURE__ */ new Map()), T(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), T(this, "nextID", 0), T(this, "lastAccessBeat", /* @__PURE__ */ new Map()), T(this, "accessBeat", 0);
  }
  return Oe(e, [{
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
        return i && ne(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(ne(i), "_").concat(i);
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
          o - r > fi && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), hn = new di();
function pi(e, t) {
  return c.useMemo(function() {
    var n = hn.get(t);
    if (n)
      return n;
    var o = e();
    return hn.set(t, o), o;
  }, t);
}
var mi = function() {
  return {};
};
function gi(e) {
  var t = e.useCSP, n = t === void 0 ? mi : t, o = e.useToken, r = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function l(d, m, y, b) {
    var g = Array.isArray(d) ? d[0] : d;
    function x(C) {
      return "".concat(String(g)).concat(C.slice(0, 1).toUpperCase()).concat(C.slice(1));
    }
    var w = (b == null ? void 0 : b.unitless) || {}, S = typeof a == "function" ? a(d) : {}, v = I(I({}, S), {}, T({}, x("zIndexPopup"), !0));
    Object.keys(w).forEach(function(C) {
      v[x(C)] = w[C];
    });
    var R = I(I({}, b), {}, {
      unitless: v,
      prefixToken: x
    }), h = p(d, m, y, R), L = u(g, y, R);
    return function(C) {
      var M = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : C, E = h(C, M), P = le(E, 2), _ = P[1], O = L(M), F = le(O, 2), A = F[0], H = F[1];
      return [A, _, H];
    };
  }
  function u(d, m, y) {
    var b = y.unitless, g = y.injectStyle, x = g === void 0 ? !0 : g, w = y.prefixToken, S = y.ignore, v = function(L) {
      var C = L.rootCls, M = L.cssVar, E = M === void 0 ? {} : M, P = o(), _ = P.realToken;
      return jr({
        path: [d],
        prefix: E.prefix,
        key: E.key,
        unitless: b,
        ignore: S,
        token: _,
        scope: C
      }, function() {
        var O = gn(d, _, m), F = pn(d, _, O, {
          deprecatedTokens: y == null ? void 0 : y.deprecatedTokens
        });
        return Object.keys(O).forEach(function(A) {
          F[w(A)] = F[A], delete F[A];
        }), F;
      }), null;
    }, R = function(L) {
      var C = o(), M = C.cssVar;
      return [function(E) {
        return x && M ? /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement(v, {
          rootCls: L,
          cssVar: M,
          component: d
        }), E) : E;
      }, M == null ? void 0 : M.key];
    };
    return R;
  }
  function p(d, m, y) {
    var b = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(d) ? d : [d, d], x = le(g, 1), w = x[0], S = g.join("-"), v = e.layer || {
      name: "antd"
    };
    return function(R) {
      var h = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : R, L = o(), C = L.theme, M = L.realToken, E = L.hashId, P = L.token, _ = L.cssVar, O = r(), F = O.rootPrefixCls, A = O.iconPrefixCls, H = n(), Q = _ ? "css" : "js", j = pi(function() {
        var N = /* @__PURE__ */ new Set();
        return _ && Object.keys(b.unitless || {}).forEach(function(q) {
          N.add(bt(q, _.prefix)), N.add(bt(q, cn(w, _.prefix)));
        }), Xo(Q, N);
      }, [Q, w, _ == null ? void 0 : _.prefix]), B = ui(Q), fe = B.max, X = B.min, re = {
        theme: C,
        token: P,
        hashId: E,
        nonce: function() {
          return H.nonce;
        },
        clientOnly: b.clientOnly,
        layer: v,
        // antd is always at top of styles
        order: b.order || -999
      };
      typeof i == "function" && Kt(I(I({}, re), {}, {
        clientOnly: !1,
        path: ["Shared", F]
      }), function() {
        return i(P, {
          prefix: {
            rootPrefixCls: F,
            iconPrefixCls: A
          },
          csp: H
        });
      });
      var U = Kt(I(I({}, re), {}, {
        path: [S, R, A]
      }), function() {
        if (b.injectStyle === !1)
          return [];
        var N = ci(P), q = N.token, oe = N.flush, J = gn(w, M, y), Fe = ".".concat(R), ge = pn(w, M, J, {
          deprecatedTokens: b.deprecatedTokens
        });
        _ && J && ne(J) === "object" && Object.keys(J).forEach(function(Se) {
          J[Se] = "var(".concat(bt(Se, cn(w, _.prefix)), ")");
        });
        var de = Bt(q, {
          componentCls: Fe,
          prefixCls: R,
          iconCls: ".".concat(A),
          antCls: ".".concat(F),
          calc: j,
          // @ts-ignore
          max: fe,
          // @ts-ignore
          min: X
        }, _ ? J : ge), he = m(de, {
          hashId: E,
          prefixCls: R,
          rootPrefixCls: F,
          iconPrefixCls: A
        });
        oe(w, ge);
        var pe = typeof s == "function" ? s(de, R, h, b.resetFont) : null;
        return [b.resetStyle === !1 ? null : pe, he];
      });
      return [U, E];
    };
  }
  function f(d, m, y) {
    var b = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = p(d, m, y, I({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, b)), x = function(S) {
      var v = S.prefixCls, R = S.rootCls, h = R === void 0 ? v : R;
      return g(v, h), null;
    };
    return x;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: f,
    genComponentStyleHook: p
  };
}
const hi = {
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
}, vi = Object.assign(Object.assign({}, hi), {
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
}), W = Math.round;
function _t(e, t) {
  const n = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = t(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const vn = (e, t, n) => n === 0 ? e : e / 100;
function Ae(e, t) {
  const n = t || 255;
  return e > n ? n : e < 0 ? 0 : e;
}
class me {
  constructor(t) {
    T(this, "isValid", !0), T(this, "r", 0), T(this, "g", 0), T(this, "b", 0), T(this, "a", 1), T(this, "_h", void 0), T(this, "_s", void 0), T(this, "_l", void 0), T(this, "_v", void 0), T(this, "_max", void 0), T(this, "_min", void 0), T(this, "_brightness", void 0);
    function n(o) {
      return o[0] in t && o[1] in t && o[2] in t;
    }
    if (t) if (typeof t == "string") {
      let r = function(i) {
        return o.startsWith(i);
      };
      const o = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (t instanceof me)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (n("rgb"))
      this.r = Ae(t.r), this.g = Ae(t.g), this.b = Ae(t.b), this.a = typeof t.a == "number" ? Ae(t.a, 1) : 1;
    else if (n("hsl"))
      this.fromHsl(t);
    else if (n("hsv"))
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
    const n = this.toHsv();
    return n.h = t, this._c(n);
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
    const n = t(this.r), o = t(this.g), r = t(this.b);
    return 0.2126 * n + 0.7152 * o + 0.0722 * r;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = W(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() - t / 100;
    return r < 0 && (r = 0), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  lighten(t = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() + t / 100;
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
  mix(t, n = 50) {
    const o = this._c(t), r = n / 100, i = (a) => (o[a] - this[a]) * r + this[a], s = {
      r: W(i("r")),
      g: W(i("g")),
      b: W(i("b")),
      a: W(i("a") * 100) / 100
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
    const n = this._c(t), o = this.a + n.a * (1 - this.a), r = (i) => W((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
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
  equals(t) {
    return this.r === t.r && this.g === t.g && this.b === t.b && this.a === t.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let t = "#";
    const n = (this.r || 0).toString(16);
    t += n.length === 2 ? n : "0" + n;
    const o = (this.g || 0).toString(16);
    t += o.length === 2 ? o : "0" + o;
    const r = (this.b || 0).toString(16);
    if (t += r.length === 2 ? r : "0" + r, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = W(this.a * 255).toString(16);
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
    const t = this.getHue(), n = W(this.getSaturation() * 100), o = W(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${n}%,${o}%,${this.a})` : `hsl(${t},${n}%,${o}%)`;
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
  _sc(t, n, o) {
    const r = this.clone();
    return r[t] = Ae(n, o), r;
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
    const n = t.replace("#", "");
    function o(r, i) {
      return parseInt(n[r] + n[i || r], 16);
    }
    n.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = n[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = n[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: n,
    l: o,
    a: r
  }) {
    if (this._h = t % 360, this._s = n, this._l = o, this.a = typeof r == "number" ? r : 1, n <= 0) {
      const d = W(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let i = 0, s = 0, a = 0;
    const l = t / 60, u = (1 - Math.abs(2 * o - 1)) * n, p = u * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (i = u, s = p) : l >= 1 && l < 2 ? (i = p, s = u) : l >= 2 && l < 3 ? (s = u, a = p) : l >= 3 && l < 4 ? (s = p, a = u) : l >= 4 && l < 5 ? (i = p, a = u) : l >= 5 && l < 6 && (i = u, a = p);
    const f = o - u / 2;
    this.r = W((i + f) * 255), this.g = W((s + f) * 255), this.b = W((a + f) * 255);
  }
  fromHsv({
    h: t,
    s: n,
    v: o,
    a: r
  }) {
    this._h = t % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = W(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = t / 60, a = Math.floor(s), l = s - a, u = W(o * (1 - n) * 255), p = W(o * (1 - n * l) * 255), f = W(o * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = f, this.b = u;
        break;
      case 1:
        this.r = p, this.b = u;
        break;
      case 2:
        this.r = u, this.b = f;
        break;
      case 3:
        this.r = u, this.g = p;
        break;
      case 4:
        this.r = f, this.g = u;
        break;
      case 5:
      default:
        this.g = u, this.b = p;
        break;
    }
  }
  fromHsvString(t) {
    const n = _t(t, vn);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(t) {
    const n = _t(t, vn);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(t) {
    const n = _t(t, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? W(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function Rt(e) {
  return e >= 0 && e <= 255;
}
function He(e, t) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new me(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: l
  } = new me(t).toRgb();
  for (let u = 0.01; u <= 1; u += 0.01) {
    const p = Math.round((n - s * (1 - u)) / u), f = Math.round((o - a * (1 - u)) / u), d = Math.round((r - l * (1 - u)) / u);
    if (Rt(p) && Rt(f) && Rt(d))
      return new me({
        r: p,
        g: f,
        b: d,
        a: Math.round(u * 100) / 100
      }).toRgbString();
  }
  return new me({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var yi = function(e, t) {
  var n = {};
  for (var o in e) Object.prototype.hasOwnProperty.call(e, o) && t.indexOf(o) < 0 && (n[o] = e[o]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(e); r < o.length; r++)
    t.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(e, o[r]) && (n[o[r]] = e[o[r]]);
  return n;
};
function bi(e) {
  const {
    override: t
  } = e, n = yi(e, ["override"]), o = Object.assign({}, t);
  Object.keys(vi).forEach((d) => {
    delete o[d];
  });
  const r = Object.assign(Object.assign({}, n), o), i = 480, s = 576, a = 768, l = 992, u = 1200, p = 1600;
  if (r.motion === !1) {
    const d = "0s";
    r.motionDurationFast = d, r.motionDurationMid = d, r.motionDurationSlow = d;
  }
  return Object.assign(Object.assign(Object.assign({}, r), {
    // ============== Background ============== //
    colorFillContent: r.colorFillSecondary,
    colorFillContentHover: r.colorFill,
    colorFillAlter: r.colorFillQuaternary,
    colorBgContainerDisabled: r.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: r.colorBgContainer,
    colorSplit: He(r.colorBorderSecondary, r.colorBgContainer),
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
    colorErrorOutline: He(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: He(r.colorWarningBg, r.colorBgContainer),
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
    controlOutline: He(r.colorPrimaryBg, r.colorBgContainer),
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
    screenLGMax: u - 1,
    screenXL: u,
    screenXLMin: u,
    screenXLMax: p - 1,
    screenXXL: p,
    screenXXLMin: p,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new me("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new me("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new me("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const Si = {
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
}, wi = {
  motionBase: !0,
  motionUnit: !0
}, xi = Dr(Ye.defaultAlgorithm), Ei = {
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
}, Gn = (e, t, n) => {
  const o = n.getDerivativeToken(e), {
    override: r,
    ...i
  } = t;
  let s = {
    ...o,
    override: r
  };
  return s = bi(s), i && Object.entries(i).forEach(([a, l]) => {
    const {
      theme: u,
      ...p
    } = l;
    let f = p;
    u && (f = Gn({
      ...s,
      ...p
    }, {
      override: p
    }, u)), s[a] = f;
  }), s;
};
function Ci() {
  const {
    token: e,
    hashed: t,
    theme: n = xi,
    override: o,
    cssVar: r
  } = c.useContext(Ye._internalContext), [i, s, a] = Nr(n, [Ye.defaultSeed, e], {
    salt: `${Oo}-${t || ""}`,
    override: o,
    getComputedToken: Gn,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: Si,
      ignore: wi,
      preserve: Ei
    }
  });
  return [n, a, t ? s : "", i, r];
}
const {
  genStyleHooks: _i
} = gi({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Je();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, n, o, r] = Ci();
    return {
      theme: e,
      realToken: t,
      hashId: n,
      token: o,
      cssVar: r
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = Je();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), Ne = /* @__PURE__ */ c.createContext(null);
function yn(e) {
  const {
    getDropContainer: t,
    className: n,
    prefixCls: o,
    children: r
  } = e, {
    disabled: i
  } = c.useContext(Ne), [s, a] = c.useState(), [l, u] = c.useState(null);
  if (c.useEffect(() => {
    const d = t == null ? void 0 : t();
    s !== d && a(d);
  }, [t]), c.useEffect(() => {
    if (s) {
      const d = () => {
        u(!0);
      }, m = (g) => {
        g.preventDefault();
      }, y = (g) => {
        g.relatedTarget || u(!1);
      }, b = (g) => {
        u(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", d), document.addEventListener("dragover", m), document.addEventListener("dragleave", y), document.addEventListener("drop", b), () => {
        document.removeEventListener("dragenter", d), document.removeEventListener("dragover", m), document.removeEventListener("dragleave", y), document.removeEventListener("drop", b);
      };
    }
  }, [!!s]), !(t && s && !i))
    return null;
  const f = `${o}-drop-area`;
  return /* @__PURE__ */ Qe(/* @__PURE__ */ c.createElement("div", {
    className: te(f, n, {
      [`${f}-on-body`]: s.tagName === "BODY"
    }),
    style: {
      display: l ? "block" : "none"
    }
  }, r), s);
}
function bn(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function Ri(e) {
  return e && je(e) === "object" && bn(e.nativeElement) ? e.nativeElement : bn(e) ? e : null;
}
function Li(e) {
  var t = Ri(e);
  if (t)
    return t;
  if (e instanceof c.Component) {
    var n;
    return (n = Wt.findDOMNode) === null || n === void 0 ? void 0 : n.call(Wt, e);
  }
  return null;
}
function Ii(e, t) {
  if (e == null) return {};
  var n = {};
  for (var o in e) if ({}.hasOwnProperty.call(e, o)) {
    if (t.indexOf(o) !== -1) continue;
    n[o] = e[o];
  }
  return n;
}
function Sn(e, t) {
  if (e == null) return {};
  var n, o, r = Ii(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (o = 0; o < i.length; o++) n = i[o], t.indexOf(n) === -1 && {}.propertyIsEnumerable.call(e, n) && (r[n] = e[n]);
  }
  return r;
}
var Ti = /* @__PURE__ */ k.createContext({}), Pi = /* @__PURE__ */ function(e) {
  ot(n, e);
  var t = it(n);
  function n() {
    return Me(this, n), t.apply(this, arguments);
  }
  return Oe(n, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), n;
}(k.Component);
function Mi(e) {
  var t = k.useReducer(function(a) {
    return a + 1;
  }, 0), n = tt(t, 2), o = n[1], r = k.useRef(e), i = Pe(function() {
    return r.current;
  }), s = Pe(function(a) {
    r.current = typeof a == "function" ? a(r.current) : a, o();
  });
  return [i, s];
}
var ye = "none", ze = "appear", Ue = "enter", Be = "leave", wn = "none", ue = "prepare", Le = "start", Ie = "active", Vt = "end", Kn = "prepared";
function xn(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit".concat(e)] = "webkit".concat(t), n["Moz".concat(e)] = "moz".concat(t), n["ms".concat(e)] = "MS".concat(t), n["O".concat(e)] = "o".concat(t.toLowerCase()), n;
}
function Oi(e, t) {
  var n = {
    animationend: xn("Animation", "AnimationEnd"),
    transitionend: xn("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete n.animationend.animation, "TransitionEvent" in t || delete n.transitionend.transition), n;
}
var Fi = Oi(st(), typeof window < "u" ? window : {}), qn = {};
if (st()) {
  var Ai = document.createElement("div");
  qn = Ai.style;
}
var Ve = {};
function Zn(e) {
  if (Ve[e])
    return Ve[e];
  var t = Fi[e];
  if (t)
    for (var n = Object.keys(t), o = n.length, r = 0; r < o; r += 1) {
      var i = n[r];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in qn)
        return Ve[e] = t[i], Ve[e];
    }
  return "";
}
var Qn = Zn("animationend"), Yn = Zn("transitionend"), Jn = !!(Qn && Yn), En = Qn || "animationend", Cn = Yn || "transitionend";
function _n(e, t) {
  if (!e) return null;
  if (ne(e) === "object") {
    var n = t.replace(/-\w/g, function(o) {
      return o[1].toUpperCase();
    });
    return e[n];
  }
  return "".concat(e, "-").concat(t);
}
const ki = function(e) {
  var t = be();
  function n(r) {
    r && (r.removeEventListener(Cn, e), r.removeEventListener(En, e));
  }
  function o(r) {
    t.current && t.current !== r && n(t.current), r && r !== t.current && (r.addEventListener(Cn, e), r.addEventListener(En, e), t.current = r);
  }
  return k.useEffect(function() {
    return function() {
      n(t.current);
    };
  }, []), [o, n];
};
var er = st() ? mr : xe, tr = function(t) {
  return +setTimeout(t, 16);
}, nr = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (tr = function(t) {
  return window.requestAnimationFrame(t);
}, nr = function(t) {
  return window.cancelAnimationFrame(t);
});
var Rn = 0, Xt = /* @__PURE__ */ new Map();
function rr(e) {
  Xt.delete(e);
}
var kt = function(t) {
  var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  Rn += 1;
  var o = Rn;
  function r(i) {
    if (i === 0)
      rr(o), t();
    else {
      var s = tr(function() {
        r(i - 1);
      });
      Xt.set(o, s);
    }
  }
  return r(n), o;
};
kt.cancel = function(e) {
  var t = Xt.get(e);
  return rr(e), nr(t);
};
const $i = function() {
  var e = k.useRef(null);
  function t() {
    kt.cancel(e.current);
  }
  function n(o) {
    var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = kt(function() {
      r <= 1 ? o({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : n(o, r - 1);
    });
    e.current = i;
  }
  return k.useEffect(function() {
    return function() {
      t();
    };
  }, []), [n, t];
};
var ji = [ue, Le, Ie, Vt], Di = [ue, Kn], or = !1, Ni = !0;
function ir(e) {
  return e === Ie || e === Vt;
}
const Hi = function(e, t, n) {
  var o = De(wn), r = le(o, 2), i = r[0], s = r[1], a = $i(), l = le(a, 2), u = l[0], p = l[1];
  function f() {
    s(ue, !0);
  }
  var d = t ? Di : ji;
  return er(function() {
    if (i !== wn && i !== Vt) {
      var m = d.indexOf(i), y = d[m + 1], b = n(i);
      b === or ? s(y, !0) : y && u(function(g) {
        function x() {
          g.isCanceled() || s(y, !0);
        }
        b === !0 ? x() : Promise.resolve(b).then(x);
      });
    }
  }, [e, i]), k.useEffect(function() {
    return function() {
      p();
    };
  }, []), [f, i];
};
function zi(e, t, n, o) {
  var r = o.motionEnter, i = r === void 0 ? !0 : r, s = o.motionAppear, a = s === void 0 ? !0 : s, l = o.motionLeave, u = l === void 0 ? !0 : l, p = o.motionDeadline, f = o.motionLeaveImmediately, d = o.onAppearPrepare, m = o.onEnterPrepare, y = o.onLeavePrepare, b = o.onAppearStart, g = o.onEnterStart, x = o.onLeaveStart, w = o.onAppearActive, S = o.onEnterActive, v = o.onLeaveActive, R = o.onAppearEnd, h = o.onEnterEnd, L = o.onLeaveEnd, C = o.onVisibleChanged, M = De(), E = le(M, 2), P = E[0], _ = E[1], O = Mi(ye), F = le(O, 2), A = F[0], H = F[1], Q = De(null), j = le(Q, 2), B = j[0], fe = j[1], X = A(), re = be(!1), U = be(null);
  function N() {
    return n();
  }
  var q = be(!1);
  function oe() {
    H(ye), fe(null, !0);
  }
  var J = Pe(function(K) {
    var V = A();
    if (V !== ye) {
      var ee = N();
      if (!(K && !K.deadline && K.target !== ee)) {
        var z = q.current, _e;
        V === ze && z ? _e = R == null ? void 0 : R(ee, K) : V === Ue && z ? _e = h == null ? void 0 : h(ee, K) : V === Be && z && (_e = L == null ? void 0 : L(ee, K)), z && _e !== !1 && oe();
      }
    }
  }), Fe = ki(J), ge = le(Fe, 1), de = ge[0], he = function(V) {
    switch (V) {
      case ze:
        return T(T(T({}, ue, d), Le, b), Ie, w);
      case Ue:
        return T(T(T({}, ue, m), Le, g), Ie, S);
      case Be:
        return T(T(T({}, ue, y), Le, x), Ie, v);
      default:
        return {};
    }
  }, pe = k.useMemo(function() {
    return he(X);
  }, [X]), Se = Hi(X, !e, function(K) {
    if (K === ue) {
      var V = pe[ue];
      return V ? V(N()) : or;
    }
    if (D in pe) {
      var ee;
      fe(((ee = pe[D]) === null || ee === void 0 ? void 0 : ee.call(pe, N(), null)) || null);
    }
    return D === Ie && X !== ye && (de(N()), p > 0 && (clearTimeout(U.current), U.current = setTimeout(function() {
      J({
        deadline: !0
      });
    }, p))), D === Kn && oe(), Ni;
  }), Ce = le(Se, 2), ie = Ce[0], D = Ce[1], se = ir(D);
  q.current = se;
  var ve = be(null);
  er(function() {
    if (!(re.current && ve.current === t)) {
      _(t);
      var K = re.current;
      re.current = !0;
      var V;
      !K && t && a && (V = ze), K && t && i && (V = Ue), (K && !t && u || !K && f && !t && u) && (V = Be);
      var ee = he(V);
      V && (e || ee[ue]) ? (H(V), ie()) : H(ye), ve.current = t;
    }
  }, [t]), xe(function() {
    // Cancel appear
    (X === ze && !a || // Cancel enter
    X === Ue && !i || // Cancel leave
    X === Be && !u) && H(ye);
  }, [a, i, u]), xe(function() {
    return function() {
      re.current = !1, clearTimeout(U.current);
    };
  }, []);
  var G = k.useRef(!1);
  xe(function() {
    P && (G.current = !0), P !== void 0 && X === ye && ((G.current || P) && (C == null || C(P)), G.current = !0);
  }, [P, X]);
  var we = B;
  return pe[ue] && D === Le && (we = I({
    transition: "none"
  }, we)), [X, D, we, P ?? t];
}
function Ui(e) {
  var t = e;
  ne(e) === "object" && (t = e.transitionSupport);
  function n(r, i) {
    return !!(r.motionName && t && i !== !1);
  }
  var o = /* @__PURE__ */ k.forwardRef(function(r, i) {
    var s = r.visible, a = s === void 0 ? !0 : s, l = r.removeOnLeave, u = l === void 0 ? !0 : l, p = r.forceRender, f = r.children, d = r.motionName, m = r.leavedClassName, y = r.eventProps, b = k.useContext(Ti), g = b.motion, x = n(r, g), w = be(), S = be();
    function v() {
      try {
        return w.current instanceof HTMLElement ? w.current : Li(S.current);
      } catch {
        return null;
      }
    }
    var R = zi(x, a, v, r), h = le(R, 4), L = h[0], C = h[1], M = h[2], E = h[3], P = k.useRef(E);
    E && (P.current = !0);
    var _ = k.useCallback(function(j) {
      w.current = j, ii(i, j);
    }, [i]), O, F = I(I({}, y), {}, {
      visible: a
    });
    if (!f)
      O = null;
    else if (L === ye)
      E ? O = f(I({}, F), _) : !u && P.current && m ? O = f(I(I({}, F), {}, {
        className: m
      }), _) : p || !u && !m ? O = f(I(I({}, F), {}, {
        style: {
          display: "none"
        }
      }), _) : O = null;
    else {
      var A;
      C === ue ? A = "prepare" : ir(C) ? A = "active" : C === Le && (A = "start");
      var H = _n(d, "".concat(L, "-").concat(A));
      O = f(I(I({}, F), {}, {
        className: te(_n(d, L), T(T({}, H, H && A), d, typeof d == "string")),
        style: M
      }), _);
    }
    if (/* @__PURE__ */ k.isValidElement(O) && si(O)) {
      var Q = ai(O);
      Q || (O = /* @__PURE__ */ k.cloneElement(O, {
        ref: _
      }));
    }
    return /* @__PURE__ */ k.createElement(Pi, {
      ref: S
    }, O);
  });
  return o.displayName = "CSSMotion", o;
}
const Bi = Ui(Jn);
var $t = "add", jt = "keep", Dt = "remove", Lt = "removed";
function Vi(e) {
  var t;
  return e && ne(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, I(I({}, t), {}, {
    key: String(t.key)
  });
}
function Nt() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(Vi);
}
function Xi() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], n = [], o = 0, r = t.length, i = Nt(e), s = Nt(t);
  i.forEach(function(u) {
    for (var p = !1, f = o; f < r; f += 1) {
      var d = s[f];
      if (d.key === u.key) {
        o < f && (n = n.concat(s.slice(o, f).map(function(m) {
          return I(I({}, m), {}, {
            status: $t
          });
        })), o = f), n.push(I(I({}, d), {}, {
          status: jt
        })), o += 1, p = !0;
        break;
      }
    }
    p || n.push(I(I({}, u), {}, {
      status: Dt
    }));
  }), o < r && (n = n.concat(s.slice(o).map(function(u) {
    return I(I({}, u), {}, {
      status: $t
    });
  })));
  var a = {};
  n.forEach(function(u) {
    var p = u.key;
    a[p] = (a[p] || 0) + 1;
  });
  var l = Object.keys(a).filter(function(u) {
    return a[u] > 1;
  });
  return l.forEach(function(u) {
    n = n.filter(function(p) {
      var f = p.key, d = p.status;
      return f !== u || d !== Dt;
    }), n.forEach(function(p) {
      p.key === u && (p.status = jt);
    });
  }), n;
}
var Wi = ["component", "children", "onVisibleChanged", "onAllRemoved"], Gi = ["status"], Ki = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function qi(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Bi, n = /* @__PURE__ */ function(o) {
    ot(i, o);
    var r = it(i);
    function i() {
      var s;
      Me(this, i);
      for (var a = arguments.length, l = new Array(a), u = 0; u < a; u++)
        l[u] = arguments[u];
      return s = r.call.apply(r, [this].concat(l)), T(Ee(s), "state", {
        keyEntities: []
      }), T(Ee(s), "removeKey", function(p) {
        s.setState(function(f) {
          var d = f.keyEntities.map(function(m) {
            return m.key !== p ? m : I(I({}, m), {}, {
              status: Lt
            });
          });
          return {
            keyEntities: d
          };
        }, function() {
          var f = s.state.keyEntities, d = f.filter(function(m) {
            var y = m.status;
            return y !== Lt;
          }).length;
          d === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return Oe(i, [{
      key: "render",
      value: function() {
        var a = this, l = this.state.keyEntities, u = this.props, p = u.component, f = u.children, d = u.onVisibleChanged;
        u.onAllRemoved;
        var m = Sn(u, Wi), y = p || k.Fragment, b = {};
        return Ki.forEach(function(g) {
          b[g] = m[g], delete m[g];
        }), delete m.keys, /* @__PURE__ */ k.createElement(y, m, l.map(function(g, x) {
          var w = g.status, S = Sn(g, Gi), v = w === $t || w === jt;
          return /* @__PURE__ */ k.createElement(t, Te({}, b, {
            key: S.key,
            visible: v,
            eventProps: S,
            onVisibleChanged: function(h) {
              d == null || d(h, {
                key: S.key
              }), h || a.removeKey(S.key);
            }
          }), function(R, h) {
            return f(I(I({}, R), {}, {
              index: x
            }), h);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, l) {
        var u = a.keys, p = l.keyEntities, f = Nt(u), d = Xi(p, f);
        return {
          keyEntities: d.filter(function(m) {
            var y = p.find(function(b) {
              var g = b.key;
              return m.key === g;
            });
            return !(y && y.status === Lt && m.status === Dt);
          })
        };
      }
    }]), i;
  }(k.Component);
  return T(n, "defaultProps", {
    component: "div"
  }), n;
}
const Zi = qi(Jn);
function Qi(e, t) {
  const {
    children: n,
    upload: o,
    rootClassName: r
  } = e, i = c.useRef(null);
  return c.useImperativeHandle(t, () => i.current), /* @__PURE__ */ c.createElement(Mn, Te({}, o, {
    showUploadList: !1,
    rootClassName: r,
    ref: i
  }), n);
}
const sr = /* @__PURE__ */ c.forwardRef(Qi), Yi = (e) => {
  const {
    componentCls: t,
    antCls: n,
    calc: o
  } = e, r = `${t}-list-card`, i = o(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [r]: {
      borderRadius: e.borderRadius,
      position: "relative",
      background: e.colorFillContent,
      borderWidth: e.lineWidth,
      borderStyle: "solid",
      borderColor: "transparent",
      flex: "none",
      // =============================== Desc ================================
      [`${r}-name,${r}-desc`]: {
        display: "flex",
        flexWrap: "nowrap",
        maxWidth: "100%"
      },
      [`${r}-ellipsis-prefix`]: {
        flex: "0 1 auto",
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      },
      [`${r}-ellipsis-suffix`]: {
        flex: "none"
      },
      // ============================= Overview ==============================
      "&-type-overview": {
        padding: o(e.paddingSM).sub(e.lineWidth).equal(),
        paddingInlineStart: o(e.padding).add(e.lineWidth).equal(),
        display: "flex",
        flexWrap: "nowrap",
        gap: e.paddingXS,
        alignItems: "flex-start",
        width: 236,
        // Icon
        [`${r}-icon`]: {
          fontSize: o(e.fontSizeLG).mul(2).equal(),
          lineHeight: 1,
          paddingTop: o(e.paddingXXS).mul(1.5).equal(),
          flex: "none"
        },
        // Content
        [`${r}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch"
        },
        [`${r}-desc`]: {
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
        [`&:not(${r}-status-error)`]: {
          border: 0
        },
        // Img
        [`${n}-image`]: {
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
        [`${r}-img-mask`]: {
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "inherit",
          background: `rgba(0, 0, 0, ${e.opacityLoading})`
        },
        // Error
        [`&${r}-status-error`]: {
          borderRadius: "inherit",
          [`img, ${r}-img-mask`]: {
            borderRadius: o(e.borderRadius).sub(e.lineWidth).equal()
          },
          [`${r}-desc`]: {
            paddingInline: e.paddingXXS
          }
        },
        // Progress
        [`${r}-progress`]: {}
      },
      // ============================ Remove Icon ============================
      [`${r}-remove`]: {
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
      [`&:hover ${r}-remove`]: {
        display: "block"
      },
      // ============================== Status ===============================
      "&-status-error": {
        borderColor: e.colorError,
        [`${r}-desc`]: {
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
          marginInlineEnd: o(e.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, Ht = {
  "&, *": {
    boxSizing: "border-box"
  }
}, Ji = (e) => {
  const {
    componentCls: t,
    calc: n,
    antCls: o
  } = e, r = `${t}-drop-area`, i = `${t}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [r]: {
      position: "absolute",
      inset: 0,
      zIndex: e.zIndexPopupBase,
      ...Ht,
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
        ...Ht,
        [`${o}-upload-wrapper ${o}-upload${o}-upload-btn`]: {
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
          gap: n(e.paddingXXS).div(2).equal()
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
}, es = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, o = `${t}-list`, r = n(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [t]: {
      position: "relative",
      width: "100%",
      ...Ht,
      // =============================== File List ===============================
      [o]: {
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
          maxHeight: n(r).mul(3).equal(),
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
          width: r,
          height: r,
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
          [`&${o}-overflow-ping-start ${o}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${o}-overflow-ping-end ${o}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        },
        "&:dir(rtl)": {
          [`&${o}-overflow-ping-end ${o}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${o}-overflow-ping-start ${o}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        }
      }
    }
  };
}, ts = (e) => {
  const {
    colorBgContainer: t
  } = e;
  return {
    colorBgPlaceholderHover: new me(t).setA(0.85).toRgbString()
  };
}, ar = _i("Attachments", (e) => {
  const t = Bt(e, {});
  return [Ji(t), es(t), Yi(t)];
}, ts), ns = (e) => e.indexOf("image/") === 0, Xe = 200;
function rs(e) {
  return new Promise((t) => {
    if (!e || !e.type || !ns(e.type)) {
      t("");
      return;
    }
    const n = new Image();
    if (n.onload = () => {
      const {
        width: o,
        height: r
      } = n, i = o / r, s = i > 1 ? Xe : Xe * i, a = i > 1 ? Xe / i : Xe, l = document.createElement("canvas");
      l.width = s, l.height = a, l.style.cssText = `position: fixed; left: 0; top: 0; width: ${s}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(l), l.getContext("2d").drawImage(n, 0, 0, s, a);
      const p = l.toDataURL();
      document.body.removeChild(l), window.URL.revokeObjectURL(n.src), t(p);
    }, n.crossOrigin = "anonymous", e.type.startsWith("image/svg+xml")) {
      const o = new FileReader();
      o.onload = () => {
        o.result && typeof o.result == "string" && (n.src = o.result);
      }, o.readAsDataURL(e);
    } else if (e.type.startsWith("image/gif")) {
      const o = new FileReader();
      o.onload = () => {
        o.result && t(o.result);
      }, o.readAsDataURL(e);
    } else
      n.src = window.URL.createObjectURL(e);
  });
}
function os() {
  return /* @__PURE__ */ c.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    //xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ c.createElement("title", null, "audio"), /* @__PURE__ */ c.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ c.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M10.7315824,7.11216117 C10.7428131,7.15148751 10.7485063,7.19218979 10.7485063,7.23309113 L10.7485063,8.07742614 C10.7484199,8.27364959 10.6183424,8.44607275 10.4296853,8.50003683 L8.32984514,9.09986306 L8.32984514,11.7071803 C8.32986605,12.5367078 7.67249692,13.217028 6.84345686,13.2454634 L6.79068592,13.2463395 C6.12766108,13.2463395 5.53916361,12.8217001 5.33010655,12.1924966 C5.1210495,11.563293 5.33842118,10.8709227 5.86959669,10.4741173 C6.40077221,10.0773119 7.12636292,10.0652587 7.67042486,10.4442027 L7.67020842,7.74937024 L7.68449368,7.74937024 C7.72405122,7.59919041 7.83988806,7.48101083 7.98924584,7.4384546 L10.1880418,6.81004755 C10.42156,6.74340323 10.6648954,6.87865515 10.7315824,7.11216117 Z M9.60714286,1.31785714 L12.9678571,4.67857143 L9.60714286,4.67857143 L9.60714286,1.31785714 Z",
    fill: "currentColor"
  })));
}
function is(e) {
  const {
    percent: t
  } = e, {
    token: n
  } = Ye.useToken();
  return /* @__PURE__ */ c.createElement(Er, {
    type: "circle",
    percent: t,
    size: n.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (o) => /* @__PURE__ */ c.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (o || 0).toFixed(0), "%")
  });
}
function ss() {
  return /* @__PURE__ */ c.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    // xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ c.createElement("title", null, "video"), /* @__PURE__ */ c.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ c.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M12.9678571,4.67857143 L9.60714286,1.31785714 L9.60714286,4.67857143 L12.9678571,4.67857143 Z M10.5379461,10.3101106 L6.68957555,13.0059749 C6.59910784,13.0693494 6.47439406,13.0473861 6.41101953,12.9569184 C6.3874624,12.9232903 6.37482581,12.8832269 6.37482581,12.8421686 L6.37482581,7.45043999 C6.37482581,7.33998304 6.46436886,7.25043999 6.57482581,7.25043999 C6.61588409,7.25043999 6.65594753,7.26307658 6.68957555,7.28663371 L10.5379461,9.98249803 C10.6284138,10.0458726 10.6503772,10.1705863 10.5870027,10.2610541 C10.5736331,10.2801392 10.5570312,10.2967411 10.5379461,10.3101106 Z",
    fill: "currentColor"
  })));
}
const It = " ", qe = "#8c8c8c", lr = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], Ln = [{
  key: "default",
  icon: /* @__PURE__ */ c.createElement(On, null),
  color: qe,
  ext: []
}, {
  key: "excel",
  icon: /* @__PURE__ */ c.createElement(Lr, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  key: "image",
  icon: /* @__PURE__ */ c.createElement(Ir, null),
  color: qe,
  ext: lr
}, {
  key: "markdown",
  icon: /* @__PURE__ */ c.createElement(Tr, null),
  color: qe,
  ext: ["md", "mdx"]
}, {
  key: "pdf",
  icon: /* @__PURE__ */ c.createElement(Pr, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  key: "ppt",
  icon: /* @__PURE__ */ c.createElement(Mr, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  key: "word",
  icon: /* @__PURE__ */ c.createElement(Or, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  key: "zip",
  icon: /* @__PURE__ */ c.createElement(Fr, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  key: "video",
  icon: /* @__PURE__ */ c.createElement(ss, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  key: "audio",
  icon: /* @__PURE__ */ c.createElement(os, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function In(e, t) {
  return t.some((n) => e.toLowerCase() === `.${n}`);
}
function as(e) {
  let t = e;
  const n = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let o = 0;
  for (; t >= 1024 && o < n.length - 1; )
    t /= 1024, o++;
  return `${t.toFixed(0)} ${n[o]}`;
}
function ls(e, t) {
  const {
    prefixCls: n,
    item: o,
    onRemove: r,
    className: i,
    style: s,
    imageProps: a,
    type: l,
    icon: u
  } = e, p = c.useContext(Ne), {
    disabled: f
  } = p || {}, {
    name: d,
    size: m,
    percent: y,
    status: b = "done",
    description: g
  } = o, {
    getPrefixCls: x
  } = Je(), w = x("attachment", n), S = `${w}-list-card`, [v, R, h] = ar(w), [L, C] = c.useMemo(() => {
    const j = d || "", B = j.match(/^(.*)\.[^.]+$/);
    return B ? [B[1], j.slice(B[1].length)] : [j, ""];
  }, [d]), M = c.useMemo(() => In(C, lr), [C]), E = c.useMemo(() => g || (b === "uploading" ? `${y || 0}%` : b === "error" ? o.response || It : m ? as(m) : It), [b, y]), [P, _] = c.useMemo(() => {
    if (u)
      if (typeof u == "string") {
        const j = Ln.find((B) => B.key === u);
        if (j)
          return [j.icon, j.color];
      } else
        return [u, void 0];
    for (const {
      ext: j,
      icon: B,
      color: fe
    } of Ln)
      if (In(C, j))
        return [B, fe];
    return [/* @__PURE__ */ c.createElement(On, {
      key: "defaultIcon"
    }), qe];
  }, [C, u]), [O, F] = c.useState();
  c.useEffect(() => {
    if (o.originFileObj) {
      let j = !0;
      return rs(o.originFileObj).then((B) => {
        j && F(B);
      }), () => {
        j = !1;
      };
    }
    F(void 0);
  }, [o.originFileObj]);
  let A = null;
  const H = o.thumbUrl || o.url || O, Q = l === "image" || l !== "file" && M && (o.originFileObj || H);
  return Q ? A = /* @__PURE__ */ c.createElement(c.Fragment, null, H && /* @__PURE__ */ c.createElement(Cr, Te({
    alt: "preview",
    src: H
  }, a)), b !== "done" && /* @__PURE__ */ c.createElement("div", {
    className: `${S}-img-mask`
  }, b === "uploading" && y !== void 0 && /* @__PURE__ */ c.createElement(is, {
    percent: y,
    prefixCls: S
  }), b === "error" && /* @__PURE__ */ c.createElement("div", {
    className: `${S}-desc`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${S}-ellipsis-prefix`
  }, E)))) : A = /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement("div", {
    className: `${S}-icon`,
    style: _ ? {
      color: _
    } : void 0
  }, P), /* @__PURE__ */ c.createElement("div", {
    className: `${S}-content`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${S}-name`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${S}-ellipsis-prefix`
  }, L ?? It), /* @__PURE__ */ c.createElement("div", {
    className: `${S}-ellipsis-suffix`
  }, C)), /* @__PURE__ */ c.createElement("div", {
    className: `${S}-desc`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${S}-ellipsis-prefix`
  }, E)))), v(/* @__PURE__ */ c.createElement("div", {
    className: te(S, {
      [`${S}-status-${b}`]: b,
      [`${S}-type-preview`]: Q,
      [`${S}-type-overview`]: !Q
    }, i, R, h),
    style: s,
    ref: t
  }, A, !f && r && /* @__PURE__ */ c.createElement("button", {
    type: "button",
    className: `${S}-remove`,
    onClick: () => {
      r(o);
    }
  }, /* @__PURE__ */ c.createElement(Rr, null))));
}
const cr = /* @__PURE__ */ c.forwardRef(ls), Tn = 1;
function cs(e) {
  const {
    prefixCls: t,
    items: n,
    onRemove: o,
    overflow: r,
    upload: i,
    listClassName: s,
    listStyle: a,
    itemClassName: l,
    uploadClassName: u,
    uploadStyle: p,
    itemStyle: f,
    imageProps: d
  } = e, m = `${t}-list`, y = c.useRef(null), [b, g] = c.useState(!1), {
    disabled: x
  } = c.useContext(Ne);
  c.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [w, S] = c.useState(!1), [v, R] = c.useState(!1), h = () => {
    const E = y.current;
    E && (r === "scrollX" ? (S(Math.abs(E.scrollLeft) >= Tn), R(E.scrollWidth - E.clientWidth - Math.abs(E.scrollLeft) >= Tn)) : r === "scrollY" && (S(E.scrollTop !== 0), R(E.scrollHeight - E.clientHeight !== E.scrollTop)));
  };
  c.useEffect(() => {
    h();
  }, [r, n.length]);
  const L = (E) => {
    const P = y.current;
    P && P.scrollTo({
      left: P.scrollLeft + E * P.clientWidth,
      behavior: "smooth"
    });
  }, C = () => {
    L(-1);
  }, M = () => {
    L(1);
  };
  return /* @__PURE__ */ c.createElement("div", {
    className: te(m, {
      [`${m}-overflow-${e.overflow}`]: r,
      [`${m}-overflow-ping-start`]: w,
      [`${m}-overflow-ping-end`]: v
    }, s),
    ref: y,
    onScroll: h,
    style: a
  }, /* @__PURE__ */ c.createElement(Zi, {
    keys: n.map((E) => ({
      key: E.uid,
      item: E
    })),
    motionName: `${m}-card-motion`,
    component: !1,
    motionAppear: b,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: E,
    item: P,
    className: _,
    style: O
  }) => /* @__PURE__ */ c.createElement(cr, {
    key: E,
    prefixCls: t,
    item: P,
    onRemove: o,
    className: te(_, l),
    imageProps: d,
    style: {
      ...O,
      ...f
    }
  })), !x && /* @__PURE__ */ c.createElement(sr, {
    upload: i
  }, /* @__PURE__ */ c.createElement(vt, {
    className: te(u, `${m}-upload-btn`),
    style: p,
    type: "dashed"
  }, /* @__PURE__ */ c.createElement(Ar, {
    className: `${m}-upload-btn-icon`
  }))), r === "scrollX" && /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement(vt, {
    size: "small",
    shape: "circle",
    className: `${m}-prev-btn`,
    icon: /* @__PURE__ */ c.createElement(kr, null),
    onClick: C
  }), /* @__PURE__ */ c.createElement(vt, {
    size: "small",
    shape: "circle",
    className: `${m}-next-btn`,
    icon: /* @__PURE__ */ c.createElement($r, null),
    onClick: M
  })));
}
function us(e, t) {
  const {
    prefixCls: n,
    placeholder: o = {},
    upload: r,
    className: i,
    style: s
  } = e, a = `${n}-placeholder`, l = o || {}, {
    disabled: u
  } = c.useContext(Ne), [p, f] = c.useState(!1), d = () => {
    f(!0);
  }, m = (g) => {
    g.currentTarget.contains(g.relatedTarget) || f(!1);
  }, y = () => {
    f(!1);
  }, b = /* @__PURE__ */ c.isValidElement(o) ? o : /* @__PURE__ */ c.createElement(_r, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ c.createElement(yt.Text, {
    className: `${a}-icon`
  }, l.icon), /* @__PURE__ */ c.createElement(yt.Title, {
    className: `${a}-title`,
    level: 5
  }, l.title), /* @__PURE__ */ c.createElement(yt.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, l.description));
  return /* @__PURE__ */ c.createElement("div", {
    className: te(a, {
      [`${a}-drag-in`]: p,
      [`${a}-disabled`]: u
    }, i),
    onDragEnter: d,
    onDragLeave: m,
    onDrop: y,
    "aria-hidden": u,
    style: s
  }, /* @__PURE__ */ c.createElement(Mn.Dragger, Te({
    showUploadList: !1
  }, r, {
    ref: t,
    style: {
      padding: 0,
      border: 0,
      background: "transparent"
    }
  }), b));
}
const fs = /* @__PURE__ */ c.forwardRef(us);
function ds(e, t) {
  const {
    prefixCls: n,
    rootClassName: o,
    rootStyle: r,
    className: i,
    style: s,
    items: a,
    children: l,
    getDropContainer: u,
    placeholder: p,
    onChange: f,
    onRemove: d,
    overflow: m,
    imageProps: y,
    disabled: b,
    maxCount: g,
    classNames: x = {},
    styles: w = {},
    ...S
  } = e, {
    getPrefixCls: v,
    direction: R
  } = Je(), h = v("attachment", n), L = ko("attachments"), {
    classNames: C,
    styles: M
  } = L, E = c.useRef(null), P = c.useRef(null);
  c.useImperativeHandle(t, () => ({
    nativeElement: E.current,
    upload: (U) => {
      var q, oe;
      const N = (oe = (q = P.current) == null ? void 0 : q.nativeElement) == null ? void 0 : oe.querySelector('input[type="file"]');
      if (N) {
        const J = new DataTransfer();
        J.items.add(U), N.files = J.files, N.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [_, O, F] = ar(h), A = te(O, F), [H, Q] = Qo([], {
    value: a
  }), j = Pe((U) => {
    Q(U.fileList), f == null || f(U);
  }), B = {
    ...S,
    fileList: H,
    maxCount: g,
    onChange: j
  }, fe = (U) => Promise.resolve(typeof d == "function" ? d(U) : d).then((N) => {
    if (N === !1)
      return;
    const q = H.filter((oe) => oe.uid !== U.uid);
    j({
      file: {
        ...U,
        status: "removed"
      },
      fileList: q
    });
  });
  let X;
  const re = (U, N, q) => {
    const oe = typeof p == "function" ? p(U) : p;
    return /* @__PURE__ */ c.createElement(fs, {
      placeholder: oe,
      upload: B,
      prefixCls: h,
      className: te(C.placeholder, x.placeholder),
      style: {
        ...M.placeholder,
        ...w.placeholder,
        ...N == null ? void 0 : N.style
      },
      ref: q
    });
  };
  if (l)
    X = /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement(sr, {
      upload: B,
      rootClassName: o,
      ref: P
    }, l), /* @__PURE__ */ c.createElement(yn, {
      getDropContainer: u,
      prefixCls: h,
      className: te(A, o)
    }, re("drop")));
  else {
    const U = H.length > 0;
    X = /* @__PURE__ */ c.createElement("div", {
      className: te(h, A, {
        [`${h}-rtl`]: R === "rtl"
      }, i, o),
      style: {
        ...r,
        ...s
      },
      dir: R || "ltr",
      ref: E
    }, /* @__PURE__ */ c.createElement(cs, {
      prefixCls: h,
      items: H,
      onRemove: fe,
      overflow: m,
      upload: B,
      listClassName: te(C.list, x.list),
      listStyle: {
        ...M.list,
        ...w.list,
        ...!U && {
          display: "none"
        }
      },
      uploadClassName: te(C.upload, x.upload),
      uploadStyle: {
        ...M.upload,
        ...w.upload
      },
      itemClassName: te(C.item, x.item),
      itemStyle: {
        ...M.item,
        ...w.item
      },
      imageProps: y
    }), re("inline", U ? {
      style: {
        display: "none"
      }
    } : {}, P), /* @__PURE__ */ c.createElement(yn, {
      getDropContainer: u || (() => E.current),
      prefixCls: h,
      className: A
    }, re("drop")));
  }
  return _(/* @__PURE__ */ c.createElement(Ne.Provider, {
    value: {
      disabled: b
    }
  }, X));
}
const ur = /* @__PURE__ */ c.forwardRef(ds);
ur.FileCard = cr;
function ps(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function ms(e, t = !1) {
  try {
    if (br(e))
      return e;
    if (t && !ps(e))
      return;
    if (typeof e == "string") {
      let n = e.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function Z(e, t) {
  return nt(() => ms(e, t), [e, t]);
}
function gs(e, t) {
  const n = nt(() => c.Children.toArray(e.originalChildren || e).filter((i) => i.props.node && !i.props.node.ignore && (!i.props.nodeSlotKey || t)).sort((i, s) => {
    if (i.props.node.slotIndex && s.props.node.slotIndex) {
      const a = ke(i.props.node.slotIndex) || 0, l = ke(s.props.node.slotIndex) || 0;
      return a - l === 0 && i.props.node.subSlotIndex && s.props.node.subSlotIndex ? (ke(i.props.node.subSlotIndex) || 0) - (ke(s.props.node.subSlotIndex) || 0) : a - l;
    }
    return 0;
  }).map((i) => i.props.node.target), [e, t]);
  return Lo(n);
}
function hs(e, t) {
  return Object.keys(e).reduce((n, o) => (e[o] !== void 0 && (n[o] = e[o]), n), {});
}
const vs = ({
  children: e,
  ...t
}) => /* @__PURE__ */ Y.jsx(Y.Fragment, {
  children: e(t)
});
function ys(e) {
  return c.createElement(vs, {
    children: e
  });
}
function Pn(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ys((n) => /* @__PURE__ */ Y.jsx(wr, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ Y.jsx($e, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ Y.jsx($e, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function ae({
  key: e,
  slots: t,
  targets: n
}, o) {
  return t[e] ? (...r) => n ? n.map((i, s) => /* @__PURE__ */ Y.jsx(c.Fragment, {
    children: Pn(i, {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ Y.jsx(Y.Fragment, {
    children: Pn(t[e], {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }) : void 0;
}
const bs = (e) => !!e.name;
function Tt(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const xs = _o(({
  slots: e,
  upload: t,
  showUploadList: n,
  progress: o,
  beforeUpload: r,
  customRequest: i,
  previewFile: s,
  isImageUrl: a,
  itemRender: l,
  iconRender: u,
  data: p,
  onChange: f,
  onValueChange: d,
  onRemove: m,
  items: y,
  setSlotParams: b,
  placeholder: g,
  getDropContainer: x,
  children: w,
  maxCount: S,
  imageProps: v,
  ...R
}) => {
  const h = Tt(v == null ? void 0 : v.preview), L = e["imageProps.preview.mask"] || e["imageProps.preview.closeIcon"] || e["imageProps.preview.toolbarRender"] || e["imageProps.preview.imageRender"] || (v == null ? void 0 : v.preview) !== !1, C = Z(h.getContainer), M = Z(h.toolbarRender), E = Z(h.imageRender), P = e["showUploadList.downloadIcon"] || e["showUploadList.removeIcon"] || e["showUploadList.previewIcon"] || e["showUploadList.extra"] || typeof n == "object", _ = Tt(n), O = e["placeholder.title"] || e["placeholder.description"] || e["placeholder.icon"] || typeof g == "object", F = Tt(g), A = Z(_.showPreviewIcon), H = Z(_.showRemoveIcon), Q = Z(_.showDownloadIcon), j = Z(r), B = Z(i), fe = Z(o == null ? void 0 : o.format), X = Z(s), re = Z(a), U = Z(l), N = Z(u), q = Z(g, !0), oe = Z(x), J = Z(p), [Fe, ge] = Ze(!1), [de, he] = Ze(y);
  xe(() => {
    he(y);
  }, [y]);
  const pe = nt(() => {
    const ie = {};
    return de.map((D) => {
      if (!bs(D)) {
        const se = D.uid || D.url || D.path;
        return ie[se] || (ie[se] = 0), ie[se]++, {
          ...D,
          name: D.orig_name || D.path,
          uid: D.uid || se + "-" + ie[se],
          status: "done"
        };
      }
      return D;
    }) || [];
  }, [de]), Se = gs(w), Ce = R.disabled || Fe;
  return /* @__PURE__ */ Y.jsxs(Y.Fragment, {
    children: [/* @__PURE__ */ Y.jsx("div", {
      style: {
        display: "none"
      },
      children: Se.length > 0 ? null : w
    }), /* @__PURE__ */ Y.jsx(ur, {
      ...R,
      disabled: Ce,
      imageProps: {
        ...v,
        preview: L ? hs({
          ...h,
          getContainer: C,
          toolbarRender: e["imageProps.preview.toolbarRender"] ? ae({
            slots: e,
            key: "imageProps.preview.toolbarRender"
          }) : M,
          imageRender: e["imageProps.preview.imageRender"] ? ae({
            slots: e,
            key: "imageProps.preview.imageRender"
          }) : E,
          ...e["imageProps.preview.mask"] || Reflect.has(h, "mask") ? {
            mask: e["imageProps.preview.mask"] ? /* @__PURE__ */ Y.jsx($e, {
              slot: e["imageProps.preview.mask"]
            }) : h.mask
          } : {},
          closeIcon: e["imageProps.preview.closeIcon"] ? /* @__PURE__ */ Y.jsx($e, {
            slot: e["imageProps.preview.closeIcon"]
          }) : h.closeIcon
        }) : !1,
        placeholder: e["imageProps.placeholder"] ? /* @__PURE__ */ Y.jsx($e, {
          slot: e["imageProps.placeholder"]
        }) : v == null ? void 0 : v.placeholder
      },
      getDropContainer: oe,
      placeholder: e.placeholder ? ae({
        slots: e,
        key: "placeholder"
      }) : O ? (...ie) => {
        var D, se, ve;
        return {
          ...F,
          icon: e["placeholder.icon"] ? (D = ae({
            slots: e,
            key: "placeholder.icon"
          })) == null ? void 0 : D(...ie) : F.icon,
          title: e["placeholder.title"] ? (se = ae({
            slots: e,
            key: "placeholder.title"
          })) == null ? void 0 : se(...ie) : F.title,
          description: e["placeholder.description"] ? (ve = ae({
            slots: e,
            key: "placeholder.description"
          })) == null ? void 0 : ve(...ie) : F.description
        };
      } : q || g,
      items: pe,
      data: J || p,
      previewFile: X,
      isImageUrl: re,
      itemRender: e.itemRender ? ae({
        slots: e,
        key: "itemRender"
      }) : U,
      iconRender: e.iconRender ? ae({
        slots: e,
        key: "iconRender"
      }) : N,
      maxCount: S,
      onChange: async (ie) => {
        try {
          const D = ie.file, se = ie.fileList, ve = pe.findIndex((G) => G.uid === D.uid);
          if (ve !== -1) {
            if (Ce)
              return;
            m == null || m(D);
            const G = de.slice();
            G.splice(ve, 1), d == null || d(G), f == null || f(G.map((we) => we.path));
          } else {
            if (j && !await j(D, se) || Ce)
              return;
            ge(!0);
            let G = se.filter((z) => z.status !== "done");
            if (S === 1)
              G = G.slice(0, 1);
            else if (G.length === 0) {
              ge(!1);
              return;
            } else if (typeof S == "number") {
              const z = S - de.length;
              G = G.slice(0, z < 0 ? 0 : z);
            }
            const we = de, K = G.map((z) => ({
              ...z,
              size: z.size,
              uid: z.uid,
              name: z.name,
              status: "uploading"
            }));
            he((z) => [...S === 1 ? [] : z, ...K]);
            const V = (await t(G.map((z) => z.originFileObj))).filter(Boolean).map((z, _e) => ({
              ...z,
              uid: K[_e].uid
            })), ee = S === 1 ? V : [...we, ...V];
            ge(!1), he(ee), d == null || d(ee), f == null || f(ee.map((z) => z.path));
          }
        } catch (D) {
          console.error(D), ge(!1);
        }
      },
      customRequest: B || Kr,
      progress: o && {
        ...o,
        format: fe
      },
      showUploadList: P ? {
        ..._,
        showDownloadIcon: Q || _.showDownloadIcon,
        showRemoveIcon: H || _.showRemoveIcon,
        showPreviewIcon: A || _.showPreviewIcon,
        downloadIcon: e["showUploadList.downloadIcon"] ? ae({
          slots: e,
          key: "showUploadList.downloadIcon"
        }) : _.downloadIcon,
        removeIcon: e["showUploadList.removeIcon"] ? ae({
          slots: e,
          key: "showUploadList.removeIcon"
        }) : _.removeIcon,
        previewIcon: e["showUploadList.previewIcon"] ? ae({
          slots: e,
          key: "showUploadList.previewIcon"
        }) : _.previewIcon,
        extra: e["showUploadList.extra"] ? ae({
          slots: e,
          key: "showUploadList.extra"
        }) : _.extra
      } : n,
      children: Se.length > 0 ? w : void 0
    })]
  });
});
export {
  xs as Attachments,
  xs as default
};
