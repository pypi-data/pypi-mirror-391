var zt = (e) => {
  throw TypeError(e);
};
var Bt = (e, t, r) => t.has(e) || zt("Cannot " + r);
var de = (e, t, r) => (Bt(e, t, "read from private field"), r ? r.call(e) : t.get(e)), Vt = (e, t, r) => t.has(e) ? zt("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(e) : t.set(e, r), Ut = (e, t, r, n) => (Bt(e, t, "write to private field"), n ? n.call(e, r) : t.set(e, r), r);
import { i as Sn, a as Et, r as xn, Z as De, g as wn, b as En, c as q } from "./Index-BjH4OEQB.js";
const O = window.ms_globals.React, l = window.ms_globals.React, gn = window.ms_globals.React.forwardRef, le = window.ms_globals.React.useRef, hn = window.ms_globals.React.useState, we = window.ms_globals.React.useEffect, Mr = window.ms_globals.React.useMemo, vn = window.ms_globals.React.version, yn = window.ms_globals.React.isValidElement, bn = window.ms_globals.React.useLayoutEffect, Wt = window.ms_globals.ReactDOM, Be = window.ms_globals.ReactDOM.createPortal, Cn = window.ms_globals.internalContext.useContextPropsContext, _n = window.ms_globals.internalContext.ContextPropsProvider, Rn = window.ms_globals.antd.ConfigProvider, Ve = window.ms_globals.antd.theme, Or = window.ms_globals.antd.Upload, Tn = window.ms_globals.antd.Progress, Pn = window.ms_globals.antd.Image, ut = window.ms_globals.antd.Button, Ln = window.ms_globals.antd.Flex, ft = window.ms_globals.antd.Typography, $r = window.ms_globals.antdIcons.FileTextFilled, In = window.ms_globals.antdIcons.CloseCircleFilled, Mn = window.ms_globals.antdIcons.FileExcelFilled, On = window.ms_globals.antdIcons.FileImageFilled, $n = window.ms_globals.antdIcons.FileMarkdownFilled, An = window.ms_globals.antdIcons.FilePdfFilled, kn = window.ms_globals.antdIcons.FilePptFilled, Fn = window.ms_globals.antdIcons.FileWordFilled, jn = window.ms_globals.antdIcons.FileZipFilled, Dn = window.ms_globals.antdIcons.PlusOutlined, Nn = window.ms_globals.antdIcons.LeftOutlined, Hn = window.ms_globals.antdIcons.RightOutlined, Xt = window.ms_globals.antdCssinjs.unit, dt = window.ms_globals.antdCssinjs.token2CSSVar, Gt = window.ms_globals.antdCssinjs.useStyleRegister, zn = window.ms_globals.antdCssinjs.useCSSVarRegister, Bn = window.ms_globals.antdCssinjs.createTheme, Vn = window.ms_globals.antdCssinjs.useCacheToken;
var Un = /\s/;
function Wn(e) {
  for (var t = e.length; t-- && Un.test(e.charAt(t)); )
    ;
  return t;
}
var Xn = /^\s+/;
function Gn(e) {
  return e && e.slice(0, Wn(e) + 1).replace(Xn, "");
}
var qt = NaN, qn = /^[-+]0x[0-9a-f]+$/i, Kn = /^0b[01]+$/i, Zn = /^0o[0-7]+$/i, Qn = parseInt;
function Kt(e) {
  if (typeof e == "number")
    return e;
  if (Sn(e))
    return qt;
  if (Et(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = Et(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Gn(e);
  var r = Kn.test(e);
  return r || Zn.test(e) ? Qn(e.slice(2), r ? 2 : 8) : qn.test(e) ? qt : +e;
}
var pt = function() {
  return xn.Date.now();
}, Yn = "Expected a function", Jn = Math.max, eo = Math.min;
function to(e, t, r) {
  var n, o, i, s, a, u, c = 0, d = !1, f = !1, p = !0;
  if (typeof e != "function")
    throw new TypeError(Yn);
  t = Kt(t) || 0, Et(r) && (d = !!r.leading, f = "maxWait" in r, i = f ? Jn(Kt(r.maxWait) || 0, t) : i, p = "trailing" in r ? !!r.trailing : p);
  function m(v) {
    var P = n, C = o;
    return n = o = void 0, c = v, s = e.apply(C, P), s;
  }
  function y(v) {
    return c = v, a = setTimeout(x, t), d ? m(v) : s;
  }
  function h(v) {
    var P = v - u, C = v - c, M = t - P;
    return f ? eo(M, i - C) : M;
  }
  function g(v) {
    var P = v - u, C = v - c;
    return u === void 0 || P >= t || P < 0 || f && C >= i;
  }
  function x() {
    var v = pt();
    if (g(v))
      return w(v);
    a = setTimeout(x, h(v));
  }
  function w(v) {
    return a = void 0, p && n ? m(v) : (n = o = void 0, s);
  }
  function b() {
    a !== void 0 && clearTimeout(a), c = 0, n = u = o = a = void 0;
  }
  function S() {
    return a === void 0 ? s : w(pt());
  }
  function _() {
    var v = pt(), P = g(v);
    if (n = arguments, o = this, u = v, P) {
      if (a === void 0)
        return y(u);
      if (f)
        return clearTimeout(a), a = setTimeout(x, t), m(u);
    }
    return a === void 0 && (a = setTimeout(x, t)), s;
  }
  return _.cancel = b, _.flush = S, _;
}
var Ar = {
  exports: {}
}, Ge = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ro = l, no = Symbol.for("react.element"), oo = Symbol.for("react.fragment"), io = Object.prototype.hasOwnProperty, so = ro.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ao = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function kr(e, t, r) {
  var n, o = {}, i = null, s = null;
  r !== void 0 && (i = "" + r), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) io.call(t, n) && !ao.hasOwnProperty(n) && (o[n] = t[n]);
  if (e && e.defaultProps) for (n in t = e.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: no,
    type: e,
    key: i,
    ref: s,
    props: o,
    _owner: so.current
  };
}
Ge.Fragment = oo;
Ge.jsx = kr;
Ge.jsxs = kr;
Ar.exports = Ge;
var V = Ar.exports;
const {
  SvelteComponent: lo,
  assign: Zt,
  binding_callbacks: Qt,
  check_outros: co,
  children: Fr,
  claim_element: jr,
  claim_space: uo,
  component_subscribe: Yt,
  compute_slots: fo,
  create_slot: po,
  detach: pe,
  element: Dr,
  empty: Jt,
  exclude_internal_props: er,
  get_all_dirty_from_scope: mo,
  get_slot_changes: go,
  group_outros: ho,
  init: vo,
  insert_hydration: Ne,
  safe_not_equal: yo,
  set_custom_element_data: Nr,
  space: bo,
  transition_in: He,
  transition_out: Ct,
  update_slot_base: So
} = window.__gradio__svelte__internal, {
  beforeUpdate: xo,
  getContext: wo,
  onDestroy: Eo,
  setContext: Co
} = window.__gradio__svelte__internal;
function tr(e) {
  let t, r;
  const n = (
    /*#slots*/
    e[7].default
  ), o = po(
    n,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Dr("svelte-slot"), o && o.c(), this.h();
    },
    l(i) {
      t = jr(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = Fr(t);
      o && o.l(s), s.forEach(pe), this.h();
    },
    h() {
      Nr(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      Ne(i, t, s), o && o.m(t, null), e[9](t), r = !0;
    },
    p(i, s) {
      o && o.p && (!r || s & /*$$scope*/
      64) && So(
        o,
        n,
        i,
        /*$$scope*/
        i[6],
        r ? go(
          n,
          /*$$scope*/
          i[6],
          s,
          null
        ) : mo(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      r || (He(o, i), r = !0);
    },
    o(i) {
      Ct(o, i), r = !1;
    },
    d(i) {
      i && pe(t), o && o.d(i), e[9](null);
    }
  };
}
function _o(e) {
  let t, r, n, o, i = (
    /*$$slots*/
    e[4].default && tr(e)
  );
  return {
    c() {
      t = Dr("react-portal-target"), r = bo(), i && i.c(), n = Jt(), this.h();
    },
    l(s) {
      t = jr(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), Fr(t).forEach(pe), r = uo(s), i && i.l(s), n = Jt(), this.h();
    },
    h() {
      Nr(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      Ne(s, t, a), e[8](t), Ne(s, r, a), i && i.m(s, a), Ne(s, n, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && He(i, 1)) : (i = tr(s), i.c(), He(i, 1), i.m(n.parentNode, n)) : i && (ho(), Ct(i, 1, 1, () => {
        i = null;
      }), co());
    },
    i(s) {
      o || (He(i), o = !0);
    },
    o(s) {
      Ct(i), o = !1;
    },
    d(s) {
      s && (pe(t), pe(r), pe(n)), e[8](null), i && i.d(s);
    }
  };
}
function rr(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function Ro(e, t, r) {
  let n, o, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = fo(i);
  let {
    svelteInit: u
  } = t;
  const c = De(rr(t)), d = De();
  Yt(e, d, (S) => r(0, n = S));
  const f = De();
  Yt(e, f, (S) => r(1, o = S));
  const p = [], m = wo("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: h,
    subSlotIndex: g
  } = wn() || {}, x = u({
    parent: m,
    props: c,
    target: d,
    slot: f,
    slotKey: y,
    slotIndex: h,
    subSlotIndex: g,
    onDestroy(S) {
      p.push(S);
    }
  });
  Co("$$ms-gr-react-wrapper", x), xo(() => {
    c.set(rr(t));
  }), Eo(() => {
    p.forEach((S) => S());
  });
  function w(S) {
    Qt[S ? "unshift" : "push"](() => {
      n = S, d.set(n);
    });
  }
  function b(S) {
    Qt[S ? "unshift" : "push"](() => {
      o = S, f.set(o);
    });
  }
  return e.$$set = (S) => {
    r(17, t = Zt(Zt({}, t), er(S))), "svelteInit" in S && r(5, u = S.svelteInit), "$$scope" in S && r(6, s = S.$$scope);
  }, t = er(t), [n, o, d, f, a, u, s, i, w, b];
}
class To extends lo {
  constructor(t) {
    super(), vo(this, t, Ro, _o, yo, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Rs
} = window.__gradio__svelte__internal, nr = window.ms_globals.rerender, mt = window.ms_globals.tree;
function Po(e, t = {}) {
  function r(n) {
    const o = De(), i = new To({
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
          }, u = s.parent ?? mt;
          return u.nodes = [...u.nodes, a], nr({
            createPortal: Be,
            node: mt
          }), s.onDestroy(() => {
            u.nodes = u.nodes.filter((c) => c.svelteInstance !== o), nr({
              createPortal: Be,
              node: mt
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
const Lo = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Io(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const n = e[r];
    return t[r] = Mo(r, n), t;
  }, {}) : {};
}
function Mo(e, t) {
  return typeof t == "number" && !Lo.includes(e) ? t + "px" : t;
}
function _t(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const o = l.Children.toArray(e._reactElement.props.children).map((i) => {
      if (l.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = _t(i.props.el);
        return l.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...l.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(Be(l.cloneElement(e._reactElement, {
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
      useCapture: u
    }) => {
      r.addEventListener(a, s, u);
    });
  });
  const n = Array.from(e.childNodes);
  for (let o = 0; o < n.length; o++) {
    const i = n[o];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = _t(i);
      t.push(...a), r.appendChild(s);
    } else i.nodeType === 3 && r.appendChild(i.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function Oo(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const me = gn(({
  slot: e,
  clone: t,
  className: r,
  style: n,
  observeAttributes: o
}, i) => {
  const s = le(), [a, u] = hn([]), {
    forceClone: c
  } = Cn(), d = c ? !0 : t;
  return we(() => {
    var h;
    if (!s.current || !e)
      return;
    let f = e;
    function p() {
      let g = f;
      if (f.tagName.toLowerCase() === "svelte-slot" && f.children.length === 1 && f.children[0] && (g = f.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), Oo(i, g), r && g.classList.add(...r.split(" ")), n) {
        const x = Io(n);
        Object.keys(x).forEach((w) => {
          g.style[w] = x[w];
        });
      }
    }
    let m = null, y = null;
    if (d && window.MutationObserver) {
      let g = function() {
        var S, _, v;
        (S = s.current) != null && S.contains(f) && ((_ = s.current) == null || _.removeChild(f));
        const {
          portals: w,
          clonedElement: b
        } = _t(e);
        f = b, u(w), f.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          p();
        }, 50), (v = s.current) == null || v.appendChild(f);
      };
      g();
      const x = to(() => {
        g(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      m = new window.MutationObserver(x), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      f.style.display = "contents", p(), (h = s.current) == null || h.appendChild(f);
    return () => {
      var g, x;
      f.style.display = "", (g = s.current) != null && g.contains(f) && ((x = s.current) == null || x.removeChild(f)), m == null || m.disconnect();
    };
  }, [e, d, r, n, i, o, c]), l.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
});
function $o(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function Ao(e, t = !1) {
  try {
    if (En(e))
      return e;
    if (t && !$o(e))
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
function gt(e, t) {
  return Mr(() => Ao(e, t), [e, t]);
}
function ko(e, t) {
  return Object.keys(e).reduce((r, n) => (e[n] !== void 0 && (r[n] = e[n]), r), {});
}
const Fo = ({
  children: e,
  ...t
}) => /* @__PURE__ */ V.jsx(V.Fragment, {
  children: e(t)
});
function jo(e) {
  return l.createElement(Fo, {
    children: e
  });
}
function or(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? jo((r) => /* @__PURE__ */ V.jsx(_n, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ V.jsx(me, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...r
    })
  })) : /* @__PURE__ */ V.jsx(me, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function ir({
  key: e,
  slots: t,
  targets: r
}, n) {
  return t[e] ? (...o) => r ? r.map((i, s) => /* @__PURE__ */ V.jsx(l.Fragment, {
    children: or(i, {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ V.jsx(V.Fragment, {
    children: or(t[e], {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }) : void 0;
}
const Do = "1.6.1";
function ve() {
  return ve = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var r = arguments[t];
      for (var n in r) ({}).hasOwnProperty.call(r, n) && (e[n] = r[n]);
    }
    return e;
  }, ve.apply(null, arguments);
}
function Ee(e) {
  "@babel/helpers - typeof";
  return Ee = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, Ee(e);
}
const No = /* @__PURE__ */ l.createContext({}), Ho = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, zo = (e) => {
  const t = l.useContext(No);
  return l.useMemo(() => ({
    ...Ho,
    ...t[e]
  }), [t[e]]);
};
function Ue() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: n,
    theme: o
  } = l.useContext(Rn.ConfigContext);
  return {
    theme: o,
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: n
  };
}
function K(e) {
  "@babel/helpers - typeof";
  return K = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, K(e);
}
function Bo(e) {
  if (Array.isArray(e)) return e;
}
function Vo(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var n, o, i, s, a = [], u = !0, c = !1;
    try {
      if (i = (r = r.call(e)).next, t === 0) {
        if (Object(r) !== r) return;
        u = !1;
      } else for (; !(u = (n = i.call(r)).done) && (a.push(n.value), a.length !== t); u = !0) ;
    } catch (d) {
      c = !0, o = d;
    } finally {
      try {
        if (!u && r.return != null && (s = r.return(), Object(s) !== s)) return;
      } finally {
        if (c) throw o;
      }
    }
    return a;
  }
}
function sr(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, n = Array(t); r < t; r++) n[r] = e[r];
  return n;
}
function Uo(e, t) {
  if (e) {
    if (typeof e == "string") return sr(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? sr(e, t) : void 0;
  }
}
function Wo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function Y(e, t) {
  return Bo(e) || Vo(e, t) || Uo(e, t) || Wo();
}
function Xo(e, t) {
  if (K(e) != "object" || !e) return e;
  var r = e[Symbol.toPrimitive];
  if (r !== void 0) {
    var n = r.call(e, t);
    if (K(n) != "object") return n;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function Hr(e) {
  var t = Xo(e, "string");
  return K(t) == "symbol" ? t : t + "";
}
function T(e, t, r) {
  return (t = Hr(t)) in e ? Object.defineProperty(e, t, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = r, e;
}
function ar(e, t) {
  var r = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var n = Object.getOwnPropertySymbols(e);
    t && (n = n.filter(function(o) {
      return Object.getOwnPropertyDescriptor(e, o).enumerable;
    })), r.push.apply(r, n);
  }
  return r;
}
function R(e) {
  for (var t = 1; t < arguments.length; t++) {
    var r = arguments[t] != null ? arguments[t] : {};
    t % 2 ? ar(Object(r), !0).forEach(function(n) {
      T(e, n, r[n]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : ar(Object(r)).forEach(function(n) {
      Object.defineProperty(e, n, Object.getOwnPropertyDescriptor(r, n));
    });
  }
  return e;
}
function be(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function lr(e, t) {
  for (var r = 0; r < t.length; r++) {
    var n = t[r];
    n.enumerable = n.enumerable || !1, n.configurable = !0, "value" in n && (n.writable = !0), Object.defineProperty(e, Hr(n.key), n);
  }
}
function Se(e, t, r) {
  return t && lr(e.prototype, t), r && lr(e, r), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function fe(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function Rt(e, t) {
  return Rt = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
    return r.__proto__ = n, r;
  }, Rt(e, t);
}
function qe(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && Rt(e, t);
}
function We(e) {
  return We = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, We(e);
}
function zr() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (zr = function() {
    return !!e;
  })();
}
function Go(e, t) {
  if (t && (K(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return fe(e);
}
function Ke(e) {
  var t = zr();
  return function() {
    var r, n = We(e);
    if (t) {
      var o = We(this).constructor;
      r = Reflect.construct(n, arguments, o);
    } else r = n.apply(this, arguments);
    return Go(this, r);
  };
}
var Br = /* @__PURE__ */ Se(function e() {
  be(this, e);
}), Vr = "CALC_UNIT", qo = new RegExp(Vr, "g");
function ht(e) {
  return typeof e == "number" ? "".concat(e).concat(Vr) : e;
}
var Ko = /* @__PURE__ */ function(e) {
  qe(r, e);
  var t = Ke(r);
  function r(n, o) {
    var i;
    be(this, r), i = t.call(this), T(fe(i), "result", ""), T(fe(i), "unitlessCssVar", void 0), T(fe(i), "lowPriority", void 0);
    var s = K(n);
    return i.unitlessCssVar = o, n instanceof r ? i.result = "(".concat(n.result, ")") : s === "number" ? i.result = ht(n) : s === "string" && (i.result = n), i;
  }
  return Se(r, [{
    key: "add",
    value: function(o) {
      return o instanceof r ? this.result = "".concat(this.result, " + ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " + ").concat(ht(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof r ? this.result = "".concat(this.result, " - ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " - ").concat(ht(o))), this.lowPriority = !0, this;
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
      var i = this, s = o || {}, a = s.unit, u = !0;
      return typeof a == "boolean" ? u = a : Array.from(this.unitlessCssVar).some(function(c) {
        return i.result.includes(c);
      }) && (u = !1), this.result = this.result.replace(qo, u ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), r;
}(Br), Zo = /* @__PURE__ */ function(e) {
  qe(r, e);
  var t = Ke(r);
  function r(n) {
    var o;
    return be(this, r), o = t.call(this), T(fe(o), "result", 0), n instanceof r ? o.result = n.result : typeof n == "number" && (o.result = n), o;
  }
  return Se(r, [{
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
}(Br), Qo = function(t, r) {
  var n = t === "css" ? Ko : Zo;
  return function(o) {
    return new n(o, r);
  };
}, cr = function(t, r) {
  return "".concat([r, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function ye(e) {
  var t = O.useRef();
  t.current = e;
  var r = O.useCallback(function() {
    for (var n, o = arguments.length, i = new Array(o), s = 0; s < o; s++)
      i[s] = arguments[s];
    return (n = t.current) === null || n === void 0 ? void 0 : n.call.apply(n, [t].concat(i));
  }, []);
  return r;
}
function Yo(e) {
  if (Array.isArray(e)) return e;
}
function Jo(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var n, o, i, s, a = [], u = !0, c = !1;
    try {
      if (i = (r = r.call(e)).next, t !== 0) for (; !(u = (n = i.call(r)).done) && (a.push(n.value), a.length !== t); u = !0) ;
    } catch (d) {
      c = !0, o = d;
    } finally {
      try {
        if (!u && r.return != null && (s = r.return(), Object(s) !== s)) return;
      } finally {
        if (c) throw o;
      }
    }
    return a;
  }
}
function ur(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, n = Array(t); r < t; r++) n[r] = e[r];
  return n;
}
function ei(e, t) {
  if (e) {
    if (typeof e == "string") return ur(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? ur(e, t) : void 0;
  }
}
function ti() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function Xe(e, t) {
  return Yo(e) || Jo(e, t) || ei(e, t) || ti();
}
function Ze() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var fr = Ze() ? O.useLayoutEffect : O.useEffect, ri = function(t, r) {
  var n = O.useRef(!0);
  fr(function() {
    return t(n.current);
  }, r), fr(function() {
    return n.current = !1, function() {
      n.current = !0;
    };
  }, []);
}, dr = function(t, r) {
  ri(function(n) {
    if (!n)
      return t();
  }, r);
};
function Ce(e) {
  var t = O.useRef(!1), r = O.useState(e), n = Xe(r, 2), o = n[0], i = n[1];
  O.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, u) {
    u && t.current || i(a);
  }
  return [o, s];
}
function vt(e) {
  return e !== void 0;
}
function ni(e, t) {
  var r = t || {}, n = r.defaultValue, o = r.value, i = r.onChange, s = r.postState, a = Ce(function() {
    return vt(o) ? o : vt(n) ? typeof n == "function" ? n() : n : typeof e == "function" ? e() : e;
  }), u = Xe(a, 2), c = u[0], d = u[1], f = o !== void 0 ? o : c, p = s ? s(f) : f, m = ye(i), y = Ce([f]), h = Xe(y, 2), g = h[0], x = h[1];
  dr(function() {
    var b = g[0];
    c !== b && m(c, b);
  }, [g]), dr(function() {
    vt(o) || d(o);
  }, [o]);
  var w = ye(function(b, S) {
    d(b, S), x([f], S);
  });
  return [p, w];
}
var Ur = {
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
var At = Symbol.for("react.element"), kt = Symbol.for("react.portal"), Qe = Symbol.for("react.fragment"), Ye = Symbol.for("react.strict_mode"), Je = Symbol.for("react.profiler"), et = Symbol.for("react.provider"), tt = Symbol.for("react.context"), oi = Symbol.for("react.server_context"), rt = Symbol.for("react.forward_ref"), nt = Symbol.for("react.suspense"), ot = Symbol.for("react.suspense_list"), it = Symbol.for("react.memo"), st = Symbol.for("react.lazy"), ii = Symbol.for("react.offscreen"), Wr;
Wr = Symbol.for("react.module.reference");
function J(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case At:
        switch (e = e.type, e) {
          case Qe:
          case Je:
          case Ye:
          case nt:
          case ot:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case oi:
              case tt:
              case rt:
              case st:
              case it:
              case et:
                return e;
              default:
                return t;
            }
        }
      case kt:
        return t;
    }
  }
}
$.ContextConsumer = tt;
$.ContextProvider = et;
$.Element = At;
$.ForwardRef = rt;
$.Fragment = Qe;
$.Lazy = st;
$.Memo = it;
$.Portal = kt;
$.Profiler = Je;
$.StrictMode = Ye;
$.Suspense = nt;
$.SuspenseList = ot;
$.isAsyncMode = function() {
  return !1;
};
$.isConcurrentMode = function() {
  return !1;
};
$.isContextConsumer = function(e) {
  return J(e) === tt;
};
$.isContextProvider = function(e) {
  return J(e) === et;
};
$.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === At;
};
$.isForwardRef = function(e) {
  return J(e) === rt;
};
$.isFragment = function(e) {
  return J(e) === Qe;
};
$.isLazy = function(e) {
  return J(e) === st;
};
$.isMemo = function(e) {
  return J(e) === it;
};
$.isPortal = function(e) {
  return J(e) === kt;
};
$.isProfiler = function(e) {
  return J(e) === Je;
};
$.isStrictMode = function(e) {
  return J(e) === Ye;
};
$.isSuspense = function(e) {
  return J(e) === nt;
};
$.isSuspenseList = function(e) {
  return J(e) === ot;
};
$.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === Qe || e === Je || e === Ye || e === nt || e === ot || e === ii || typeof e == "object" && e !== null && (e.$$typeof === st || e.$$typeof === it || e.$$typeof === et || e.$$typeof === tt || e.$$typeof === rt || e.$$typeof === Wr || e.getModuleId !== void 0);
};
$.typeOf = J;
Ur.exports = $;
var yt = Ur.exports, si = Symbol.for("react.element"), ai = Symbol.for("react.transitional.element"), li = Symbol.for("react.fragment");
function ci(e) {
  return (
    // Base object type
    e && Ee(e) === "object" && // React Element type
    (e.$$typeof === si || e.$$typeof === ai) && // React Fragment type
    e.type === li
  );
}
var ui = Number(vn.split(".")[0]), fi = function(t, r) {
  typeof t == "function" ? t(r) : Ee(t) === "object" && t && "current" in t && (t.current = r);
}, di = function(t) {
  var r, n;
  if (!t)
    return !1;
  if (Xr(t) && ui >= 19)
    return !0;
  var o = yt.isMemo(t) ? t.type.type : t.type;
  return !(typeof o == "function" && !((r = o.prototype) !== null && r !== void 0 && r.render) && o.$$typeof !== yt.ForwardRef || typeof t == "function" && !((n = t.prototype) !== null && n !== void 0 && n.render) && t.$$typeof !== yt.ForwardRef);
};
function Xr(e) {
  return /* @__PURE__ */ yn(e) && !ci(e);
}
var pi = function(t) {
  if (t && Xr(t)) {
    var r = t;
    return r.props.propertyIsEnumerable("ref") ? r.props.ref : r.ref;
  }
  return null;
};
function pr(e, t, r, n) {
  var o = R({}, t[e]);
  if (n != null && n.deprecatedTokens) {
    var i = n.deprecatedTokens;
    i.forEach(function(a) {
      var u = Y(a, 2), c = u[0], d = u[1];
      if (o != null && o[c] || o != null && o[d]) {
        var f;
        (f = o[d]) !== null && f !== void 0 || (o[d] = o == null ? void 0 : o[c]);
      }
    });
  }
  var s = R(R({}, r), o);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Gr = typeof CSSINJS_STATISTIC < "u", Tt = !0;
function Ft() {
  for (var e = arguments.length, t = new Array(e), r = 0; r < e; r++)
    t[r] = arguments[r];
  if (!Gr)
    return Object.assign.apply(Object, [{}].concat(t));
  Tt = !1;
  var n = {};
  return t.forEach(function(o) {
    if (K(o) === "object") {
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
  }), Tt = !0, n;
}
var mr = {};
function mi() {
}
var gi = function(t) {
  var r, n = t, o = mi;
  return Gr && typeof Proxy < "u" && (r = /* @__PURE__ */ new Set(), n = new Proxy(t, {
    get: function(s, a) {
      if (Tt) {
        var u;
        (u = r) === null || u === void 0 || u.add(a);
      }
      return s[a];
    }
  }), o = function(s, a) {
    var u;
    mr[s] = {
      global: Array.from(r),
      component: R(R({}, (u = mr[s]) === null || u === void 0 ? void 0 : u.component), a)
    };
  }), {
    token: n,
    keys: r,
    flush: o
  };
};
function gr(e, t, r) {
  if (typeof r == "function") {
    var n;
    return r(Ft(t, (n = t[e]) !== null && n !== void 0 ? n : {}));
  }
  return r ?? {};
}
function hi(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var r = arguments.length, n = new Array(r), o = 0; o < r; o++)
        n[o] = arguments[o];
      return "max(".concat(n.map(function(i) {
        return Xt(i);
      }).join(","), ")");
    },
    min: function() {
      for (var r = arguments.length, n = new Array(r), o = 0; o < r; o++)
        n[o] = arguments[o];
      return "min(".concat(n.map(function(i) {
        return Xt(i);
      }).join(","), ")");
    }
  };
}
var vi = 1e3 * 60 * 10, yi = /* @__PURE__ */ function() {
  function e() {
    be(this, e), T(this, "map", /* @__PURE__ */ new Map()), T(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), T(this, "nextID", 0), T(this, "lastAccessBeat", /* @__PURE__ */ new Map()), T(this, "accessBeat", 0);
  }
  return Se(e, [{
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
        return i && K(i) === "object" ? "obj_".concat(n.getObjectID(i)) : "".concat(K(i), "_").concat(i);
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
          n - o > vi && (r.map.delete(i), r.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), hr = new yi();
function bi(e, t) {
  return l.useMemo(function() {
    var r = hr.get(t);
    if (r)
      return r;
    var n = e();
    return hr.set(t, n), n;
  }, t);
}
var Si = function() {
  return {};
};
function xi(e) {
  var t = e.useCSP, r = t === void 0 ? Si : t, n = e.useToken, o = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function u(p, m, y, h) {
    var g = Array.isArray(p) ? p[0] : p;
    function x(C) {
      return "".concat(String(g)).concat(C.slice(0, 1).toUpperCase()).concat(C.slice(1));
    }
    var w = (h == null ? void 0 : h.unitless) || {}, b = typeof a == "function" ? a(p) : {}, S = R(R({}, b), {}, T({}, x("zIndexPopup"), !0));
    Object.keys(w).forEach(function(C) {
      S[x(C)] = w[C];
    });
    var _ = R(R({}, h), {}, {
      unitless: S,
      prefixToken: x
    }), v = d(p, m, y, _), P = c(g, y, _);
    return function(C) {
      var M = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : C, E = v(C, M), L = Y(E, 2), I = L[1], A = P(M), F = Y(A, 2), k = F[0], N = F[1];
      return [k, I, N];
    };
  }
  function c(p, m, y) {
    var h = y.unitless, g = y.injectStyle, x = g === void 0 ? !0 : g, w = y.prefixToken, b = y.ignore, S = function(P) {
      var C = P.rootCls, M = P.cssVar, E = M === void 0 ? {} : M, L = n(), I = L.realToken;
      return zn({
        path: [p],
        prefix: E.prefix,
        key: E.key,
        unitless: h,
        ignore: b,
        token: I,
        scope: C
      }, function() {
        var A = gr(p, I, m), F = pr(p, I, A, {
          deprecatedTokens: y == null ? void 0 : y.deprecatedTokens
        });
        return Object.keys(A).forEach(function(k) {
          F[w(k)] = F[k], delete F[k];
        }), F;
      }), null;
    }, _ = function(P) {
      var C = n(), M = C.cssVar;
      return [function(E) {
        return x && M ? /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(S, {
          rootCls: P,
          cssVar: M,
          component: p
        }), E) : E;
      }, M == null ? void 0 : M.key];
    };
    return _;
  }
  function d(p, m, y) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(p) ? p : [p, p], x = Y(g, 1), w = x[0], b = g.join("-"), S = e.layer || {
      name: "antd"
    };
    return function(_) {
      var v = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : _, P = n(), C = P.theme, M = P.realToken, E = P.hashId, L = P.token, I = P.cssVar, A = o(), F = A.rootPrefixCls, k = A.iconPrefixCls, N = r(), Z = I ? "css" : "js", j = bi(function() {
        var D = /* @__PURE__ */ new Set();
        return I && Object.keys(h.unitless || {}).forEach(function(X) {
          D.add(dt(X, I.prefix)), D.add(dt(X, cr(w, I.prefix)));
        }), Qo(Z, D);
      }, [Z, w, I == null ? void 0 : I.prefix]), z = hi(Z), se = z.max, U = z.min, ee = {
        theme: C,
        token: L,
        hashId: E,
        nonce: function() {
          return N.nonce;
        },
        clientOnly: h.clientOnly,
        layer: S,
        // antd is always at top of styles
        order: h.order || -999
      };
      typeof i == "function" && Gt(R(R({}, ee), {}, {
        clientOnly: !1,
        path: ["Shared", F]
      }), function() {
        return i(L, {
          prefix: {
            rootPrefixCls: F,
            iconPrefixCls: k
          },
          csp: N
        });
      });
      var H = Gt(R(R({}, ee), {}, {
        path: [b, _, k]
      }), function() {
        if (h.injectStyle === !1)
          return [];
        var D = gi(L), X = D.token, te = D.flush, Q = gr(w, M, y), at = ".".concat(_), Re = pr(w, M, Q, {
          deprecatedTokens: h.deprecatedTokens
        });
        I && Q && K(Q) === "object" && Object.keys(Q).forEach(function(Le) {
          Q[Le] = "var(".concat(dt(Le, cr(w, I.prefix)), ")");
        });
        var Te = Ft(X, {
          componentCls: at,
          prefixCls: _,
          iconCls: ".".concat(k),
          antCls: ".".concat(F),
          calc: j,
          // @ts-ignore
          max: se,
          // @ts-ignore
          min: U
        }, I ? Q : Re), Pe = m(Te, {
          hashId: E,
          prefixCls: _,
          rootPrefixCls: F,
          iconPrefixCls: k
        });
        te(w, Re);
        var ce = typeof s == "function" ? s(Te, _, v, h.resetFont) : null;
        return [h.resetStyle === !1 ? null : ce, Pe];
      });
      return [H, E];
    };
  }
  function f(p, m, y) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = d(p, m, y, R({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, h)), x = function(b) {
      var S = b.prefixCls, _ = b.rootCls, v = _ === void 0 ? S : _;
      return g(S, v), null;
    };
    return x;
  }
  return {
    genStyleHooks: u,
    genSubStyleComponent: f,
    genComponentStyleHook: d
  };
}
const wi = {
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
}, Ei = Object.assign(Object.assign({}, wi), {
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
function bt(e, t) {
  const r = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], n = r.map((o) => parseFloat(o));
  for (let o = 0; o < 3; o += 1)
    n[o] = t(n[o] || 0, r[o] || "", o);
  return r[3] ? n[3] = r[3].includes("%") ? n[3] / 100 : n[3] : n[3] = 1, n;
}
const vr = (e, t, r) => r === 0 ? e : e / 100;
function xe(e, t) {
  const r = t || 255;
  return e > r ? r : e < 0 ? 0 : e;
}
class oe {
  constructor(t) {
    T(this, "isValid", !0), T(this, "r", 0), T(this, "g", 0), T(this, "b", 0), T(this, "a", 1), T(this, "_h", void 0), T(this, "_s", void 0), T(this, "_l", void 0), T(this, "_v", void 0), T(this, "_max", void 0), T(this, "_min", void 0), T(this, "_brightness", void 0);
    function r(n) {
      return n[0] in t && n[1] in t && n[2] in t;
    }
    if (t) if (typeof t == "string") {
      let o = function(i) {
        return n.startsWith(i);
      };
      const n = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(n) ? this.fromHexString(n) : o("rgb") ? this.fromRgbString(n) : o("hsl") ? this.fromHslString(n) : (o("hsv") || o("hsb")) && this.fromHsvString(n);
    } else if (t instanceof oe)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (r("rgb"))
      this.r = xe(t.r), this.g = xe(t.g), this.b = xe(t.b), this.a = typeof t.a == "number" ? xe(t.a, 1) : 1;
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
      t === 0 ? this._h = 0 : this._h = B(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
    const r = this._c(t), n = this.a + r.a * (1 - this.a), o = (i) => B((this[i] * this.a + r[i] * r.a * (1 - this.a)) / n);
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
      const i = B(this.a * 255).toString(16);
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
    const t = this.getHue(), r = B(this.getSaturation() * 100), n = B(this.getLightness() * 100);
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
    return o[t] = xe(r, n), o;
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
      const p = B(n * 255);
      this.r = p, this.g = p, this.b = p;
    }
    let i = 0, s = 0, a = 0;
    const u = t / 60, c = (1 - Math.abs(2 * n - 1)) * r, d = c * (1 - Math.abs(u % 2 - 1));
    u >= 0 && u < 1 ? (i = c, s = d) : u >= 1 && u < 2 ? (i = d, s = c) : u >= 2 && u < 3 ? (s = c, a = d) : u >= 3 && u < 4 ? (s = d, a = c) : u >= 4 && u < 5 ? (i = d, a = c) : u >= 5 && u < 6 && (i = c, a = d);
    const f = n - c / 2;
    this.r = B((i + f) * 255), this.g = B((s + f) * 255), this.b = B((a + f) * 255);
  }
  fromHsv({
    h: t,
    s: r,
    v: n,
    a: o
  }) {
    this._h = t % 360, this._s = r, this._v = n, this.a = typeof o == "number" ? o : 1;
    const i = B(n * 255);
    if (this.r = i, this.g = i, this.b = i, r <= 0)
      return;
    const s = t / 60, a = Math.floor(s), u = s - a, c = B(n * (1 - r) * 255), d = B(n * (1 - r * u) * 255), f = B(n * (1 - r * (1 - u)) * 255);
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
  fromHsvString(t) {
    const r = bt(t, vr);
    this.fromHsv({
      h: r[0],
      s: r[1],
      v: r[2],
      a: r[3]
    });
  }
  fromHslString(t) {
    const r = bt(t, vr);
    this.fromHsl({
      h: r[0],
      s: r[1],
      l: r[2],
      a: r[3]
    });
  }
  fromRgbString(t) {
    const r = bt(t, (n, o) => (
      // Convert percentage to number. e.g. 50% -> 128
      o.includes("%") ? B(n / 100 * 255) : n
    ));
    this.r = r[0], this.g = r[1], this.b = r[2], this.a = r[3];
  }
}
function St(e) {
  return e >= 0 && e <= 255;
}
function Oe(e, t) {
  const {
    r,
    g: n,
    b: o,
    a: i
  } = new oe(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: u
  } = new oe(t).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const d = Math.round((r - s * (1 - c)) / c), f = Math.round((n - a * (1 - c)) / c), p = Math.round((o - u * (1 - c)) / c);
    if (St(d) && St(f) && St(p))
      return new oe({
        r: d,
        g: f,
        b: p,
        a: Math.round(c * 100) / 100
      }).toRgbString();
  }
  return new oe({
    r,
    g: n,
    b: o,
    a: 1
  }).toRgbString();
}
var Ci = function(e, t) {
  var r = {};
  for (var n in e) Object.prototype.hasOwnProperty.call(e, n) && t.indexOf(n) < 0 && (r[n] = e[n]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var o = 0, n = Object.getOwnPropertySymbols(e); o < n.length; o++)
    t.indexOf(n[o]) < 0 && Object.prototype.propertyIsEnumerable.call(e, n[o]) && (r[n[o]] = e[n[o]]);
  return r;
};
function _i(e) {
  const {
    override: t
  } = e, r = Ci(e, ["override"]), n = Object.assign({}, t);
  Object.keys(Ei).forEach((p) => {
    delete n[p];
  });
  const o = Object.assign(Object.assign({}, r), n), i = 480, s = 576, a = 768, u = 992, c = 1200, d = 1600;
  if (o.motion === !1) {
    const p = "0s";
    o.motionDurationFast = p, o.motionDurationMid = p, o.motionDurationSlow = p;
  }
  return Object.assign(Object.assign(Object.assign({}, o), {
    // ============== Background ============== //
    colorFillContent: o.colorFillSecondary,
    colorFillContentHover: o.colorFill,
    colorFillAlter: o.colorFillQuaternary,
    colorBgContainerDisabled: o.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: o.colorBgContainer,
    colorSplit: Oe(o.colorBorderSecondary, o.colorBgContainer),
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
    colorErrorOutline: Oe(o.colorErrorBg, o.colorBgContainer),
    colorWarningOutline: Oe(o.colorWarningBg, o.colorBgContainer),
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
    controlOutline: Oe(o.colorPrimaryBg, o.colorBgContainer),
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
    screenMDMax: u - 1,
    screenLG: u,
    screenLGMin: u,
    screenLGMax: c - 1,
    screenXL: c,
    screenXLMin: c,
    screenXLMax: d - 1,
    screenXXL: d,
    screenXXLMin: d,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new oe("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new oe("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new oe("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const Ri = {
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
}, Ti = {
  motionBase: !0,
  motionUnit: !0
}, Pi = Bn(Ve.defaultAlgorithm), Li = {
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
}, qr = (e, t, r) => {
  const n = r.getDerivativeToken(e), {
    override: o,
    ...i
  } = t;
  let s = {
    ...n,
    override: o
  };
  return s = _i(s), i && Object.entries(i).forEach(([a, u]) => {
    const {
      theme: c,
      ...d
    } = u;
    let f = d;
    c && (f = qr({
      ...s,
      ...d
    }, {
      override: d
    }, c)), s[a] = f;
  }), s;
};
function Ii() {
  const {
    token: e,
    hashed: t,
    theme: r = Pi,
    override: n,
    cssVar: o
  } = l.useContext(Ve._internalContext), [i, s, a] = Vn(r, [Ve.defaultSeed, e], {
    salt: `${Do}-${t || ""}`,
    override: n,
    getComputedToken: qr,
    cssVar: o && {
      prefix: o.prefix,
      key: o.key,
      unitless: Ri,
      ignore: Ti,
      preserve: Li
    }
  });
  return [r, a, t ? s : "", i, o];
}
const {
  genStyleHooks: Mi
} = xi({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Ue();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, r, n, o] = Ii();
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
    } = Ue();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), _e = /* @__PURE__ */ l.createContext(null);
function yr(e) {
  const {
    getDropContainer: t,
    className: r,
    prefixCls: n,
    children: o
  } = e, {
    disabled: i
  } = l.useContext(_e), [s, a] = l.useState(), [u, c] = l.useState(null);
  if (l.useEffect(() => {
    const p = t == null ? void 0 : t();
    s !== p && a(p);
  }, [t]), l.useEffect(() => {
    if (s) {
      const p = () => {
        c(!0);
      }, m = (g) => {
        g.preventDefault();
      }, y = (g) => {
        g.relatedTarget || c(!1);
      }, h = (g) => {
        c(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", p), document.addEventListener("dragover", m), document.addEventListener("dragleave", y), document.addEventListener("drop", h), () => {
        document.removeEventListener("dragenter", p), document.removeEventListener("dragover", m), document.removeEventListener("dragleave", y), document.removeEventListener("drop", h);
      };
    }
  }, [!!s]), !(t && s && !i))
    return null;
  const f = `${n}-drop-area`;
  return /* @__PURE__ */ Be(/* @__PURE__ */ l.createElement("div", {
    className: q(f, r, {
      [`${f}-on-body`]: s.tagName === "BODY"
    }),
    style: {
      display: u ? "block" : "none"
    }
  }, o), s);
}
function br(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function Oi(e) {
  return e && Ee(e) === "object" && br(e.nativeElement) ? e.nativeElement : br(e) ? e : null;
}
function $i(e) {
  var t = Oi(e);
  if (t)
    return t;
  if (e instanceof l.Component) {
    var r;
    return (r = Wt.findDOMNode) === null || r === void 0 ? void 0 : r.call(Wt, e);
  }
  return null;
}
function Ai(e, t) {
  if (e == null) return {};
  var r = {};
  for (var n in e) if ({}.hasOwnProperty.call(e, n)) {
    if (t.indexOf(n) !== -1) continue;
    r[n] = e[n];
  }
  return r;
}
function Sr(e, t) {
  if (e == null) return {};
  var r, n, o = Ai(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (n = 0; n < i.length; n++) r = i[n], t.indexOf(r) === -1 && {}.propertyIsEnumerable.call(e, r) && (o[r] = e[r]);
  }
  return o;
}
var ki = /* @__PURE__ */ O.createContext({}), Fi = /* @__PURE__ */ function(e) {
  qe(r, e);
  var t = Ke(r);
  function r() {
    return be(this, r), t.apply(this, arguments);
  }
  return Se(r, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), r;
}(O.Component);
function ji(e) {
  var t = O.useReducer(function(a) {
    return a + 1;
  }, 0), r = Xe(t, 2), n = r[1], o = O.useRef(e), i = ye(function() {
    return o.current;
  }), s = ye(function(a) {
    o.current = typeof a == "function" ? a(o.current) : a, n();
  });
  return [i, s];
}
var ae = "none", $e = "appear", Ae = "enter", ke = "leave", xr = "none", re = "prepare", ge = "start", he = "active", jt = "end", Kr = "prepared";
function wr(e, t) {
  var r = {};
  return r[e.toLowerCase()] = t.toLowerCase(), r["Webkit".concat(e)] = "webkit".concat(t), r["Moz".concat(e)] = "moz".concat(t), r["ms".concat(e)] = "MS".concat(t), r["O".concat(e)] = "o".concat(t.toLowerCase()), r;
}
function Di(e, t) {
  var r = {
    animationend: wr("Animation", "AnimationEnd"),
    transitionend: wr("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete r.animationend.animation, "TransitionEvent" in t || delete r.transitionend.transition), r;
}
var Ni = Di(Ze(), typeof window < "u" ? window : {}), Zr = {};
if (Ze()) {
  var Hi = document.createElement("div");
  Zr = Hi.style;
}
var Fe = {};
function Qr(e) {
  if (Fe[e])
    return Fe[e];
  var t = Ni[e];
  if (t)
    for (var r = Object.keys(t), n = r.length, o = 0; o < n; o += 1) {
      var i = r[o];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in Zr)
        return Fe[e] = t[i], Fe[e];
    }
  return "";
}
var Yr = Qr("animationend"), Jr = Qr("transitionend"), en = !!(Yr && Jr), Er = Yr || "animationend", Cr = Jr || "transitionend";
function _r(e, t) {
  if (!e) return null;
  if (K(e) === "object") {
    var r = t.replace(/-\w/g, function(n) {
      return n[1].toUpperCase();
    });
    return e[r];
  }
  return "".concat(e, "-").concat(t);
}
const zi = function(e) {
  var t = le();
  function r(o) {
    o && (o.removeEventListener(Cr, e), o.removeEventListener(Er, e));
  }
  function n(o) {
    t.current && t.current !== o && r(t.current), o && o !== t.current && (o.addEventListener(Cr, e), o.addEventListener(Er, e), t.current = o);
  }
  return O.useEffect(function() {
    return function() {
      r(t.current);
    };
  }, []), [n, r];
};
var tn = Ze() ? bn : we, rn = function(t) {
  return +setTimeout(t, 16);
}, nn = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (rn = function(t) {
  return window.requestAnimationFrame(t);
}, nn = function(t) {
  return window.cancelAnimationFrame(t);
});
var Rr = 0, Dt = /* @__PURE__ */ new Map();
function on(e) {
  Dt.delete(e);
}
var Pt = function(t) {
  var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  Rr += 1;
  var n = Rr;
  function o(i) {
    if (i === 0)
      on(n), t();
    else {
      var s = rn(function() {
        o(i - 1);
      });
      Dt.set(n, s);
    }
  }
  return o(r), n;
};
Pt.cancel = function(e) {
  var t = Dt.get(e);
  return on(e), nn(t);
};
const Bi = function() {
  var e = O.useRef(null);
  function t() {
    Pt.cancel(e.current);
  }
  function r(n) {
    var o = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = Pt(function() {
      o <= 1 ? n({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : r(n, o - 1);
    });
    e.current = i;
  }
  return O.useEffect(function() {
    return function() {
      t();
    };
  }, []), [r, t];
};
var Vi = [re, ge, he, jt], Ui = [re, Kr], sn = !1, Wi = !0;
function an(e) {
  return e === he || e === jt;
}
const Xi = function(e, t, r) {
  var n = Ce(xr), o = Y(n, 2), i = o[0], s = o[1], a = Bi(), u = Y(a, 2), c = u[0], d = u[1];
  function f() {
    s(re, !0);
  }
  var p = t ? Ui : Vi;
  return tn(function() {
    if (i !== xr && i !== jt) {
      var m = p.indexOf(i), y = p[m + 1], h = r(i);
      h === sn ? s(y, !0) : y && c(function(g) {
        function x() {
          g.isCanceled() || s(y, !0);
        }
        h === !0 ? x() : Promise.resolve(h).then(x);
      });
    }
  }, [e, i]), O.useEffect(function() {
    return function() {
      d();
    };
  }, []), [f, i];
};
function Gi(e, t, r, n) {
  var o = n.motionEnter, i = o === void 0 ? !0 : o, s = n.motionAppear, a = s === void 0 ? !0 : s, u = n.motionLeave, c = u === void 0 ? !0 : u, d = n.motionDeadline, f = n.motionLeaveImmediately, p = n.onAppearPrepare, m = n.onEnterPrepare, y = n.onLeavePrepare, h = n.onAppearStart, g = n.onEnterStart, x = n.onLeaveStart, w = n.onAppearActive, b = n.onEnterActive, S = n.onLeaveActive, _ = n.onAppearEnd, v = n.onEnterEnd, P = n.onLeaveEnd, C = n.onVisibleChanged, M = Ce(), E = Y(M, 2), L = E[0], I = E[1], A = ji(ae), F = Y(A, 2), k = F[0], N = F[1], Z = Ce(null), j = Y(Z, 2), z = j[0], se = j[1], U = k(), ee = le(!1), H = le(null);
  function D() {
    return r();
  }
  var X = le(!1);
  function te() {
    N(ae), se(null, !0);
  }
  var Q = ye(function(G) {
    var W = k();
    if (W !== ae) {
      var ne = D();
      if (!(G && !G.deadline && G.target !== ne)) {
        var Ie = X.current, Me;
        W === $e && Ie ? Me = _ == null ? void 0 : _(ne, G) : W === Ae && Ie ? Me = v == null ? void 0 : v(ne, G) : W === ke && Ie && (Me = P == null ? void 0 : P(ne, G)), Ie && Me !== !1 && te();
      }
    }
  }), at = zi(Q), Re = Y(at, 1), Te = Re[0], Pe = function(W) {
    switch (W) {
      case $e:
        return T(T(T({}, re, p), ge, h), he, w);
      case Ae:
        return T(T(T({}, re, m), ge, g), he, b);
      case ke:
        return T(T(T({}, re, y), ge, x), he, S);
      default:
        return {};
    }
  }, ce = O.useMemo(function() {
    return Pe(U);
  }, [U]), Le = Xi(U, !e, function(G) {
    if (G === re) {
      var W = ce[re];
      return W ? W(D()) : sn;
    }
    if (ue in ce) {
      var ne;
      se(((ne = ce[ue]) === null || ne === void 0 ? void 0 : ne.call(ce, D(), null)) || null);
    }
    return ue === he && U !== ae && (Te(D()), d > 0 && (clearTimeout(H.current), H.current = setTimeout(function() {
      Q({
        deadline: !0
      });
    }, d))), ue === Kr && te(), Wi;
  }), Nt = Y(Le, 2), pn = Nt[0], ue = Nt[1], mn = an(ue);
  X.current = mn;
  var Ht = le(null);
  tn(function() {
    if (!(ee.current && Ht.current === t)) {
      I(t);
      var G = ee.current;
      ee.current = !0;
      var W;
      !G && t && a && (W = $e), G && t && i && (W = Ae), (G && !t && c || !G && f && !t && c) && (W = ke);
      var ne = Pe(W);
      W && (e || ne[re]) ? (N(W), pn()) : N(ae), Ht.current = t;
    }
  }, [t]), we(function() {
    // Cancel appear
    (U === $e && !a || // Cancel enter
    U === Ae && !i || // Cancel leave
    U === ke && !c) && N(ae);
  }, [a, i, c]), we(function() {
    return function() {
      ee.current = !1, clearTimeout(H.current);
    };
  }, []);
  var lt = O.useRef(!1);
  we(function() {
    L && (lt.current = !0), L !== void 0 && U === ae && ((lt.current || L) && (C == null || C(L)), lt.current = !0);
  }, [L, U]);
  var ct = z;
  return ce[re] && ue === ge && (ct = R({
    transition: "none"
  }, ct)), [U, ue, ct, L ?? t];
}
function qi(e) {
  var t = e;
  K(e) === "object" && (t = e.transitionSupport);
  function r(o, i) {
    return !!(o.motionName && t && i !== !1);
  }
  var n = /* @__PURE__ */ O.forwardRef(function(o, i) {
    var s = o.visible, a = s === void 0 ? !0 : s, u = o.removeOnLeave, c = u === void 0 ? !0 : u, d = o.forceRender, f = o.children, p = o.motionName, m = o.leavedClassName, y = o.eventProps, h = O.useContext(ki), g = h.motion, x = r(o, g), w = le(), b = le();
    function S() {
      try {
        return w.current instanceof HTMLElement ? w.current : $i(b.current);
      } catch {
        return null;
      }
    }
    var _ = Gi(x, a, S, o), v = Y(_, 4), P = v[0], C = v[1], M = v[2], E = v[3], L = O.useRef(E);
    E && (L.current = !0);
    var I = O.useCallback(function(j) {
      w.current = j, fi(i, j);
    }, [i]), A, F = R(R({}, y), {}, {
      visible: a
    });
    if (!f)
      A = null;
    else if (P === ae)
      E ? A = f(R({}, F), I) : !c && L.current && m ? A = f(R(R({}, F), {}, {
        className: m
      }), I) : d || !c && !m ? A = f(R(R({}, F), {}, {
        style: {
          display: "none"
        }
      }), I) : A = null;
    else {
      var k;
      C === re ? k = "prepare" : an(C) ? k = "active" : C === ge && (k = "start");
      var N = _r(p, "".concat(P, "-").concat(k));
      A = f(R(R({}, F), {}, {
        className: q(_r(p, P), T(T({}, N, N && k), p, typeof p == "string")),
        style: M
      }), I);
    }
    if (/* @__PURE__ */ O.isValidElement(A) && di(A)) {
      var Z = pi(A);
      Z || (A = /* @__PURE__ */ O.cloneElement(A, {
        ref: I
      }));
    }
    return /* @__PURE__ */ O.createElement(Fi, {
      ref: b
    }, A);
  });
  return n.displayName = "CSSMotion", n;
}
const Ki = qi(en);
var Lt = "add", It = "keep", Mt = "remove", xt = "removed";
function Zi(e) {
  var t;
  return e && K(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, R(R({}, t), {}, {
    key: String(t.key)
  });
}
function Ot() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(Zi);
}
function Qi() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], r = [], n = 0, o = t.length, i = Ot(e), s = Ot(t);
  i.forEach(function(c) {
    for (var d = !1, f = n; f < o; f += 1) {
      var p = s[f];
      if (p.key === c.key) {
        n < f && (r = r.concat(s.slice(n, f).map(function(m) {
          return R(R({}, m), {}, {
            status: Lt
          });
        })), n = f), r.push(R(R({}, p), {}, {
          status: It
        })), n += 1, d = !0;
        break;
      }
    }
    d || r.push(R(R({}, c), {}, {
      status: Mt
    }));
  }), n < o && (r = r.concat(s.slice(n).map(function(c) {
    return R(R({}, c), {}, {
      status: Lt
    });
  })));
  var a = {};
  r.forEach(function(c) {
    var d = c.key;
    a[d] = (a[d] || 0) + 1;
  });
  var u = Object.keys(a).filter(function(c) {
    return a[c] > 1;
  });
  return u.forEach(function(c) {
    r = r.filter(function(d) {
      var f = d.key, p = d.status;
      return f !== c || p !== Mt;
    }), r.forEach(function(d) {
      d.key === c && (d.status = It);
    });
  }), r;
}
var Yi = ["component", "children", "onVisibleChanged", "onAllRemoved"], Ji = ["status"], es = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function ts(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Ki, r = /* @__PURE__ */ function(n) {
    qe(i, n);
    var o = Ke(i);
    function i() {
      var s;
      be(this, i);
      for (var a = arguments.length, u = new Array(a), c = 0; c < a; c++)
        u[c] = arguments[c];
      return s = o.call.apply(o, [this].concat(u)), T(fe(s), "state", {
        keyEntities: []
      }), T(fe(s), "removeKey", function(d) {
        s.setState(function(f) {
          var p = f.keyEntities.map(function(m) {
            return m.key !== d ? m : R(R({}, m), {}, {
              status: xt
            });
          });
          return {
            keyEntities: p
          };
        }, function() {
          var f = s.state.keyEntities, p = f.filter(function(m) {
            var y = m.status;
            return y !== xt;
          }).length;
          p === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return Se(i, [{
      key: "render",
      value: function() {
        var a = this, u = this.state.keyEntities, c = this.props, d = c.component, f = c.children, p = c.onVisibleChanged;
        c.onAllRemoved;
        var m = Sr(c, Yi), y = d || O.Fragment, h = {};
        return es.forEach(function(g) {
          h[g] = m[g], delete m[g];
        }), delete m.keys, /* @__PURE__ */ O.createElement(y, m, u.map(function(g, x) {
          var w = g.status, b = Sr(g, Ji), S = w === Lt || w === It;
          return /* @__PURE__ */ O.createElement(t, ve({}, h, {
            key: b.key,
            visible: S,
            eventProps: b,
            onVisibleChanged: function(v) {
              p == null || p(v, {
                key: b.key
              }), v || a.removeKey(b.key);
            }
          }), function(_, v) {
            return f(R(R({}, _), {}, {
              index: x
            }), v);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, u) {
        var c = a.keys, d = u.keyEntities, f = Ot(c), p = Qi(d, f);
        return {
          keyEntities: p.filter(function(m) {
            var y = d.find(function(h) {
              var g = h.key;
              return m.key === g;
            });
            return !(y && y.status === xt && m.status === Mt);
          })
        };
      }
    }]), i;
  }(O.Component);
  return T(r, "defaultProps", {
    component: "div"
  }), r;
}
const rs = ts(en);
function ns(e, t) {
  const {
    children: r,
    upload: n,
    rootClassName: o
  } = e, i = l.useRef(null);
  return l.useImperativeHandle(t, () => i.current), /* @__PURE__ */ l.createElement(Or, ve({}, n, {
    showUploadList: !1,
    rootClassName: o,
    ref: i
  }), r);
}
const ln = /* @__PURE__ */ l.forwardRef(ns), os = (e) => {
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
}, $t = {
  "&, *": {
    boxSizing: "border-box"
  }
}, is = (e) => {
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
      ...$t,
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
        ...$t,
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
}, ss = (e) => {
  const {
    componentCls: t,
    calc: r
  } = e, n = `${t}-list`, o = r(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [t]: {
      position: "relative",
      width: "100%",
      ...$t,
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
}, as = (e) => {
  const {
    colorBgContainer: t
  } = e;
  return {
    colorBgPlaceholderHover: new oe(t).setA(0.85).toRgbString()
  };
}, cn = Mi("Attachments", (e) => {
  const t = Ft(e, {});
  return [is(t), ss(t), os(t)];
}, as), ls = (e) => e.indexOf("image/") === 0, je = 200;
function cs(e) {
  return new Promise((t) => {
    if (!e || !e.type || !ls(e.type)) {
      t("");
      return;
    }
    const r = new Image();
    if (r.onload = () => {
      const {
        width: n,
        height: o
      } = r, i = n / o, s = i > 1 ? je : je * i, a = i > 1 ? je / i : je, u = document.createElement("canvas");
      u.width = s, u.height = a, u.style.cssText = `position: fixed; left: 0; top: 0; width: ${s}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(u), u.getContext("2d").drawImage(r, 0, 0, s, a);
      const d = u.toDataURL();
      document.body.removeChild(u), window.URL.revokeObjectURL(r.src), t(d);
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
function us() {
  return /* @__PURE__ */ l.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    //xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ l.createElement("title", null, "audio"), /* @__PURE__ */ l.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ l.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M10.7315824,7.11216117 C10.7428131,7.15148751 10.7485063,7.19218979 10.7485063,7.23309113 L10.7485063,8.07742614 C10.7484199,8.27364959 10.6183424,8.44607275 10.4296853,8.50003683 L8.32984514,9.09986306 L8.32984514,11.7071803 C8.32986605,12.5367078 7.67249692,13.217028 6.84345686,13.2454634 L6.79068592,13.2463395 C6.12766108,13.2463395 5.53916361,12.8217001 5.33010655,12.1924966 C5.1210495,11.563293 5.33842118,10.8709227 5.86959669,10.4741173 C6.40077221,10.0773119 7.12636292,10.0652587 7.67042486,10.4442027 L7.67020842,7.74937024 L7.68449368,7.74937024 C7.72405122,7.59919041 7.83988806,7.48101083 7.98924584,7.4384546 L10.1880418,6.81004755 C10.42156,6.74340323 10.6648954,6.87865515 10.7315824,7.11216117 Z M9.60714286,1.31785714 L12.9678571,4.67857143 L9.60714286,4.67857143 L9.60714286,1.31785714 Z",
    fill: "currentColor"
  })));
}
function fs(e) {
  const {
    percent: t
  } = e, {
    token: r
  } = Ve.useToken();
  return /* @__PURE__ */ l.createElement(Tn, {
    type: "circle",
    percent: t,
    size: r.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (n) => /* @__PURE__ */ l.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (n || 0).toFixed(0), "%")
  });
}
function ds() {
  return /* @__PURE__ */ l.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    // xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ l.createElement("title", null, "video"), /* @__PURE__ */ l.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ l.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M12.9678571,4.67857143 L9.60714286,1.31785714 L9.60714286,4.67857143 L12.9678571,4.67857143 Z M10.5379461,10.3101106 L6.68957555,13.0059749 C6.59910784,13.0693494 6.47439406,13.0473861 6.41101953,12.9569184 C6.3874624,12.9232903 6.37482581,12.8832269 6.37482581,12.8421686 L6.37482581,7.45043999 C6.37482581,7.33998304 6.46436886,7.25043999 6.57482581,7.25043999 C6.61588409,7.25043999 6.65594753,7.26307658 6.68957555,7.28663371 L10.5379461,9.98249803 C10.6284138,10.0458726 10.6503772,10.1705863 10.5870027,10.2610541 C10.5736331,10.2801392 10.5570312,10.2967411 10.5379461,10.3101106 Z",
    fill: "currentColor"
  })));
}
const wt = " ", ze = "#8c8c8c", un = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], Tr = [{
  key: "default",
  icon: /* @__PURE__ */ l.createElement($r, null),
  color: ze,
  ext: []
}, {
  key: "excel",
  icon: /* @__PURE__ */ l.createElement(Mn, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  key: "image",
  icon: /* @__PURE__ */ l.createElement(On, null),
  color: ze,
  ext: un
}, {
  key: "markdown",
  icon: /* @__PURE__ */ l.createElement($n, null),
  color: ze,
  ext: ["md", "mdx"]
}, {
  key: "pdf",
  icon: /* @__PURE__ */ l.createElement(An, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  key: "ppt",
  icon: /* @__PURE__ */ l.createElement(kn, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  key: "word",
  icon: /* @__PURE__ */ l.createElement(Fn, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  key: "zip",
  icon: /* @__PURE__ */ l.createElement(jn, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  key: "video",
  icon: /* @__PURE__ */ l.createElement(ds, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  key: "audio",
  icon: /* @__PURE__ */ l.createElement(us, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function Pr(e, t) {
  return t.some((r) => e.toLowerCase() === `.${r}`);
}
function ps(e) {
  let t = e;
  const r = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let n = 0;
  for (; t >= 1024 && n < r.length - 1; )
    t /= 1024, n++;
  return `${t.toFixed(0)} ${r[n]}`;
}
function ms(e, t) {
  const {
    prefixCls: r,
    item: n,
    onRemove: o,
    className: i,
    style: s,
    imageProps: a,
    type: u,
    icon: c
  } = e, d = l.useContext(_e), {
    disabled: f
  } = d || {}, {
    name: p,
    size: m,
    percent: y,
    status: h = "done",
    description: g
  } = n, {
    getPrefixCls: x
  } = Ue(), w = x("attachment", r), b = `${w}-list-card`, [S, _, v] = cn(w), [P, C] = l.useMemo(() => {
    const j = p || "", z = j.match(/^(.*)\.[^.]+$/);
    return z ? [z[1], j.slice(z[1].length)] : [j, ""];
  }, [p]), M = l.useMemo(() => Pr(C, un), [C]), E = l.useMemo(() => g || (h === "uploading" ? `${y || 0}%` : h === "error" ? n.response || wt : m ? ps(m) : wt), [h, y]), [L, I] = l.useMemo(() => {
    if (c)
      if (typeof c == "string") {
        const j = Tr.find((z) => z.key === c);
        if (j)
          return [j.icon, j.color];
      } else
        return [c, void 0];
    for (const {
      ext: j,
      icon: z,
      color: se
    } of Tr)
      if (Pr(C, j))
        return [z, se];
    return [/* @__PURE__ */ l.createElement($r, {
      key: "defaultIcon"
    }), ze];
  }, [C, c]), [A, F] = l.useState();
  l.useEffect(() => {
    if (n.originFileObj) {
      let j = !0;
      return cs(n.originFileObj).then((z) => {
        j && F(z);
      }), () => {
        j = !1;
      };
    }
    F(void 0);
  }, [n.originFileObj]);
  let k = null;
  const N = n.thumbUrl || n.url || A, Z = u === "image" || u !== "file" && M && (n.originFileObj || N);
  return Z ? k = /* @__PURE__ */ l.createElement(l.Fragment, null, N && /* @__PURE__ */ l.createElement(Pn, ve({
    alt: "preview",
    src: N
  }, a)), h !== "done" && /* @__PURE__ */ l.createElement("div", {
    className: `${b}-img-mask`
  }, h === "uploading" && y !== void 0 && /* @__PURE__ */ l.createElement(fs, {
    percent: y,
    prefixCls: b
  }), h === "error" && /* @__PURE__ */ l.createElement("div", {
    className: `${b}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${b}-ellipsis-prefix`
  }, E)))) : k = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement("div", {
    className: `${b}-icon`,
    style: I ? {
      color: I
    } : void 0
  }, L), /* @__PURE__ */ l.createElement("div", {
    className: `${b}-content`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${b}-name`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${b}-ellipsis-prefix`
  }, P ?? wt), /* @__PURE__ */ l.createElement("div", {
    className: `${b}-ellipsis-suffix`
  }, C)), /* @__PURE__ */ l.createElement("div", {
    className: `${b}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${b}-ellipsis-prefix`
  }, E)))), S(/* @__PURE__ */ l.createElement("div", {
    className: q(b, {
      [`${b}-status-${h}`]: h,
      [`${b}-type-preview`]: Z,
      [`${b}-type-overview`]: !Z
    }, i, _, v),
    style: s,
    ref: t
  }, k, !f && o && /* @__PURE__ */ l.createElement("button", {
    type: "button",
    className: `${b}-remove`,
    onClick: () => {
      o(n);
    }
  }, /* @__PURE__ */ l.createElement(In, null))));
}
const fn = /* @__PURE__ */ l.forwardRef(ms), Lr = 1;
function gs(e) {
  const {
    prefixCls: t,
    items: r,
    onRemove: n,
    overflow: o,
    upload: i,
    listClassName: s,
    listStyle: a,
    itemClassName: u,
    uploadClassName: c,
    uploadStyle: d,
    itemStyle: f,
    imageProps: p
  } = e, m = `${t}-list`, y = l.useRef(null), [h, g] = l.useState(!1), {
    disabled: x
  } = l.useContext(_e);
  l.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [w, b] = l.useState(!1), [S, _] = l.useState(!1), v = () => {
    const E = y.current;
    E && (o === "scrollX" ? (b(Math.abs(E.scrollLeft) >= Lr), _(E.scrollWidth - E.clientWidth - Math.abs(E.scrollLeft) >= Lr)) : o === "scrollY" && (b(E.scrollTop !== 0), _(E.scrollHeight - E.clientHeight !== E.scrollTop)));
  };
  l.useEffect(() => {
    v();
  }, [o, r.length]);
  const P = (E) => {
    const L = y.current;
    L && L.scrollTo({
      left: L.scrollLeft + E * L.clientWidth,
      behavior: "smooth"
    });
  }, C = () => {
    P(-1);
  }, M = () => {
    P(1);
  };
  return /* @__PURE__ */ l.createElement("div", {
    className: q(m, {
      [`${m}-overflow-${e.overflow}`]: o,
      [`${m}-overflow-ping-start`]: w,
      [`${m}-overflow-ping-end`]: S
    }, s),
    ref: y,
    onScroll: v,
    style: a
  }, /* @__PURE__ */ l.createElement(rs, {
    keys: r.map((E) => ({
      key: E.uid,
      item: E
    })),
    motionName: `${m}-card-motion`,
    component: !1,
    motionAppear: h,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: E,
    item: L,
    className: I,
    style: A
  }) => /* @__PURE__ */ l.createElement(fn, {
    key: E,
    prefixCls: t,
    item: L,
    onRemove: n,
    className: q(I, u),
    imageProps: p,
    style: {
      ...A,
      ...f
    }
  })), !x && /* @__PURE__ */ l.createElement(ln, {
    upload: i
  }, /* @__PURE__ */ l.createElement(ut, {
    className: q(c, `${m}-upload-btn`),
    style: d,
    type: "dashed"
  }, /* @__PURE__ */ l.createElement(Dn, {
    className: `${m}-upload-btn-icon`
  }))), o === "scrollX" && /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(ut, {
    size: "small",
    shape: "circle",
    className: `${m}-prev-btn`,
    icon: /* @__PURE__ */ l.createElement(Nn, null),
    onClick: C
  }), /* @__PURE__ */ l.createElement(ut, {
    size: "small",
    shape: "circle",
    className: `${m}-next-btn`,
    icon: /* @__PURE__ */ l.createElement(Hn, null),
    onClick: M
  })));
}
function hs(e, t) {
  const {
    prefixCls: r,
    placeholder: n = {},
    upload: o,
    className: i,
    style: s
  } = e, a = `${r}-placeholder`, u = n || {}, {
    disabled: c
  } = l.useContext(_e), [d, f] = l.useState(!1), p = () => {
    f(!0);
  }, m = (g) => {
    g.currentTarget.contains(g.relatedTarget) || f(!1);
  }, y = () => {
    f(!1);
  }, h = /* @__PURE__ */ l.isValidElement(n) ? n : /* @__PURE__ */ l.createElement(Ln, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ l.createElement(ft.Text, {
    className: `${a}-icon`
  }, u.icon), /* @__PURE__ */ l.createElement(ft.Title, {
    className: `${a}-title`,
    level: 5
  }, u.title), /* @__PURE__ */ l.createElement(ft.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, u.description));
  return /* @__PURE__ */ l.createElement("div", {
    className: q(a, {
      [`${a}-drag-in`]: d,
      [`${a}-disabled`]: c
    }, i),
    onDragEnter: p,
    onDragLeave: m,
    onDrop: y,
    "aria-hidden": c,
    style: s
  }, /* @__PURE__ */ l.createElement(Or.Dragger, ve({
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
const vs = /* @__PURE__ */ l.forwardRef(hs);
function ys(e, t) {
  const {
    prefixCls: r,
    rootClassName: n,
    rootStyle: o,
    className: i,
    style: s,
    items: a,
    children: u,
    getDropContainer: c,
    placeholder: d,
    onChange: f,
    onRemove: p,
    overflow: m,
    imageProps: y,
    disabled: h,
    maxCount: g,
    classNames: x = {},
    styles: w = {},
    ...b
  } = e, {
    getPrefixCls: S,
    direction: _
  } = Ue(), v = S("attachment", r), P = zo("attachments"), {
    classNames: C,
    styles: M
  } = P, E = l.useRef(null), L = l.useRef(null);
  l.useImperativeHandle(t, () => ({
    nativeElement: E.current,
    upload: (H) => {
      var X, te;
      const D = (te = (X = L.current) == null ? void 0 : X.nativeElement) == null ? void 0 : te.querySelector('input[type="file"]');
      if (D) {
        const Q = new DataTransfer();
        Q.items.add(H), D.files = Q.files, D.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [I, A, F] = cn(v), k = q(A, F), [N, Z] = ni([], {
    value: a
  }), j = ye((H) => {
    Z(H.fileList), f == null || f(H);
  }), z = {
    ...b,
    fileList: N,
    maxCount: g,
    onChange: j
  }, se = (H) => Promise.resolve(typeof p == "function" ? p(H) : p).then((D) => {
    if (D === !1)
      return;
    const X = N.filter((te) => te.uid !== H.uid);
    j({
      file: {
        ...H,
        status: "removed"
      },
      fileList: X
    });
  });
  let U;
  const ee = (H, D, X) => {
    const te = typeof d == "function" ? d(H) : d;
    return /* @__PURE__ */ l.createElement(vs, {
      placeholder: te,
      upload: z,
      prefixCls: v,
      className: q(C.placeholder, x.placeholder),
      style: {
        ...M.placeholder,
        ...w.placeholder,
        ...D == null ? void 0 : D.style
      },
      ref: X
    });
  };
  if (u)
    U = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(ln, {
      upload: z,
      rootClassName: n,
      ref: L
    }, u), /* @__PURE__ */ l.createElement(yr, {
      getDropContainer: c,
      prefixCls: v,
      className: q(k, n)
    }, ee("drop")));
  else {
    const H = N.length > 0;
    U = /* @__PURE__ */ l.createElement("div", {
      className: q(v, k, {
        [`${v}-rtl`]: _ === "rtl"
      }, i, n),
      style: {
        ...o,
        ...s
      },
      dir: _ || "ltr",
      ref: E
    }, /* @__PURE__ */ l.createElement(gs, {
      prefixCls: v,
      items: N,
      onRemove: se,
      overflow: m,
      upload: z,
      listClassName: q(C.list, x.list),
      listStyle: {
        ...M.list,
        ...w.list,
        ...!H && {
          display: "none"
        }
      },
      uploadClassName: q(C.upload, x.upload),
      uploadStyle: {
        ...M.upload,
        ...w.upload
      },
      itemClassName: q(C.item, x.item),
      itemStyle: {
        ...M.item,
        ...w.item
      },
      imageProps: y
    }), ee("inline", H ? {
      style: {
        display: "none"
      }
    } : {}, L), /* @__PURE__ */ l.createElement(yr, {
      getDropContainer: c || (() => E.current),
      prefixCls: v,
      className: k
    }, ee("drop")));
  }
  return I(/* @__PURE__ */ l.createElement(_e.Provider, {
    value: {
      disabled: h
    }
  }, U));
}
const dn = /* @__PURE__ */ l.forwardRef(ys);
dn.FileCard = fn;
new Intl.Collator(0, {
  numeric: 1
}).compare;
typeof process < "u" && process.versions && process.versions.node;
var ie;
class Ts extends TransformStream {
  /** Constructs a new instance. */
  constructor(r = {
    allowCR: !1
  }) {
    super({
      transform: (n, o) => {
        for (n = de(this, ie) + n; ; ) {
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
        Ut(this, ie, n);
      },
      flush: (n) => {
        if (de(this, ie) === "") return;
        const o = r.allowCR && de(this, ie).endsWith("\r") ? de(this, ie).slice(0, -1) : de(this, ie);
        n.enqueue(o);
      }
    });
    Vt(this, ie, "");
  }
}
ie = new WeakMap();
function bs(e) {
  try {
    const t = new URL(e);
    return t.protocol === "http:" || t.protocol === "https:";
  } catch {
    return !1;
  }
}
function Ss() {
  const e = document.querySelector(".gradio-container");
  if (!e)
    return "";
  const t = e.className.match(/gradio-container-(.+)/);
  return t ? t[1] : "";
}
const xs = +Ss()[0];
function Ir(e, t, r) {
  const n = xs >= 5 ? "gradio_api/" : "";
  return e == null ? r ? `/proxy=${r}${n}file=` : `${t}${n}file=` : bs(e) ? e : r ? `/proxy=${r}${n}file=${e}` : `${t}/${n}file=${e}`;
}
const ws = ({
  item: e,
  urlRoot: t,
  urlProxyUrl: r,
  ...n
}) => {
  const o = Mr(() => e ? typeof e == "string" ? {
    url: e.startsWith("http") ? e : Ir(e, t, r),
    uid: e,
    name: e.split("/").pop()
  } : {
    ...e,
    uid: e.uid || e.path || e.url,
    name: e.name || e.orig_name || (e.url || e.path).split("/").pop(),
    url: e.url || Ir(e.path, t, r)
  } : {}, [e, r, t]);
  return /* @__PURE__ */ V.jsx(dn.FileCard, {
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
};
function Es(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const Ps = Po(({
  setSlotParams: e,
  imageProps: t,
  slots: r,
  children: n,
  ...o
}) => {
  const i = Es(t == null ? void 0 : t.preview), s = r["imageProps.preview.mask"] || r["imageProps.preview.closeIcon"] || r["imageProps.preview.toolbarRender"] || r["imageProps.preview.imageRender"] || (t == null ? void 0 : t.preview) !== !1, a = gt(i.getContainer), u = gt(i.toolbarRender), c = gt(i.imageRender);
  return /* @__PURE__ */ V.jsxs(V.Fragment, {
    children: [/* @__PURE__ */ V.jsx("div", {
      style: {
        display: "none"
      },
      children: n
    }), /* @__PURE__ */ V.jsx(ws, {
      ...o,
      icon: r.icon ? /* @__PURE__ */ V.jsx(me, {
        slot: r.icon
      }) : o.icon,
      imageProps: {
        ...t,
        preview: s ? ko({
          ...i,
          getContainer: a,
          toolbarRender: r["imageProps.preview.toolbarRender"] ? ir({
            slots: r,
            key: "imageProps.preview.toolbarRender"
          }) : u,
          imageRender: r["imageProps.preview.imageRender"] ? ir({
            slots: r,
            key: "imageProps.preview.imageRender"
          }) : c,
          ...r["imageProps.preview.mask"] || Reflect.has(i, "mask") ? {
            mask: r["imageProps.preview.mask"] ? /* @__PURE__ */ V.jsx(me, {
              slot: r["imageProps.preview.mask"]
            }) : i.mask
          } : {},
          closeIcon: r["imageProps.preview.closeIcon"] ? /* @__PURE__ */ V.jsx(me, {
            slot: r["imageProps.preview.closeIcon"]
          }) : i.closeIcon
        }) : !1,
        placeholder: r["imageProps.placeholder"] ? /* @__PURE__ */ V.jsx(me, {
          slot: r["imageProps.placeholder"]
        }) : t == null ? void 0 : t.placeholder
      }
    })]
  });
});
export {
  Ps as AttachmentsFileCard,
  Ps as default
};
