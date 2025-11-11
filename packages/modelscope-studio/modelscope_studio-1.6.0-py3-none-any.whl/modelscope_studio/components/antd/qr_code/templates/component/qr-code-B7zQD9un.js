import { i as ce, a as N, r as ae, Z as P, g as ue, b as de } from "./Index-CHUoNOcJ.js";
const b = window.ms_globals.React, re = window.ms_globals.React.useMemo, oe = window.ms_globals.React.forwardRef, se = window.ms_globals.React.useRef, ie = window.ms_globals.React.useState, le = window.ms_globals.React.useEffect, F = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, me = window.ms_globals.internalContext.ContextPropsProvider, _e = window.ms_globals.antd.QRCode;
var pe = /\s/;
function he(t) {
  for (var e = t.length; e-- && pe.test(t.charAt(e)); )
    ;
  return e;
}
var ge = /^\s+/;
function we(t) {
  return t && t.slice(0, he(t) + 1).replace(ge, "");
}
var z = NaN, be = /^[-+]0x[0-9a-f]+$/i, Ce = /^0b[01]+$/i, ye = /^0o[0-7]+$/i, ve = parseInt;
function D(t) {
  if (typeof t == "number")
    return t;
  if (ce(t))
    return z;
  if (N(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = N(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = we(t);
  var r = Ce.test(t);
  return r || ye.test(t) ? ve(t.slice(2), r ? 2 : 8) : be.test(t) ? z : +t;
}
var L = function() {
  return ae.Date.now();
}, Ee = "Expected a function", xe = Math.max, Se = Math.min;
function Re(t, e, r) {
  var i, s, n, o, l, d, p = 0, h = !1, c = !1, g = !0;
  if (typeof t != "function")
    throw new TypeError(Ee);
  e = D(e) || 0, N(r) && (h = !!r.leading, c = "maxWait" in r, n = c ? xe(D(r.maxWait) || 0, e) : n, g = "trailing" in r ? !!r.trailing : g);
  function m(u) {
    var y = i, I = s;
    return i = s = void 0, p = u, o = t.apply(I, y), o;
  }
  function v(u) {
    return p = u, l = setTimeout(_, e), h ? m(u) : o;
  }
  function E(u) {
    var y = u - d, I = u - p, M = e - y;
    return c ? Se(M, n - I) : M;
  }
  function f(u) {
    var y = u - d, I = u - p;
    return d === void 0 || y >= e || y < 0 || c && I >= n;
  }
  function _() {
    var u = L();
    if (f(u))
      return w(u);
    l = setTimeout(_, E(u));
  }
  function w(u) {
    return l = void 0, g && i ? m(u) : (i = s = void 0, o);
  }
  function R() {
    l !== void 0 && clearTimeout(l), p = 0, i = d = s = l = void 0;
  }
  function a() {
    return l === void 0 ? o : w(L());
  }
  function x() {
    var u = L(), y = f(u);
    if (i = arguments, s = this, d = u, y) {
      if (l === void 0)
        return v(d);
      if (c)
        return clearTimeout(l), l = setTimeout(_, e), m(d);
    }
    return l === void 0 && (l = setTimeout(_, e)), o;
  }
  return x.cancel = R, x.flush = a, x;
}
var Y = {
  exports: {}
}, k = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ie = b, Pe = Symbol.for("react.element"), Te = Symbol.for("react.fragment"), Oe = Object.prototype.hasOwnProperty, ke = Ie.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Le = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Z(t, e, r) {
  var i, s = {}, n = null, o = null;
  r !== void 0 && (n = "" + r), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (o = e.ref);
  for (i in e) Oe.call(e, i) && !Le.hasOwnProperty(i) && (s[i] = e[i]);
  if (t && t.defaultProps) for (i in e = t.defaultProps, e) s[i] === void 0 && (s[i] = e[i]);
  return {
    $$typeof: Pe,
    type: t,
    key: n,
    ref: o,
    props: s,
    _owner: ke.current
  };
}
k.Fragment = Te;
k.jsx = Z;
k.jsxs = Z;
Y.exports = k;
var C = Y.exports;
const {
  SvelteComponent: je,
  assign: U,
  binding_callbacks: B,
  check_outros: Fe,
  children: $,
  claim_element: ee,
  claim_space: Ne,
  component_subscribe: G,
  compute_slots: We,
  create_slot: Ae,
  detach: S,
  element: te,
  empty: H,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Me,
  get_slot_changes: ze,
  group_outros: De,
  init: Ue,
  insert_hydration: T,
  safe_not_equal: Be,
  set_custom_element_data: ne,
  space: Ge,
  transition_in: O,
  transition_out: W,
  update_slot_base: He
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ke,
  getContext: Qe,
  onDestroy: qe,
  setContext: Ve
} = window.__gradio__svelte__internal;
function Q(t) {
  let e, r;
  const i = (
    /*#slots*/
    t[7].default
  ), s = Ae(
    i,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = te("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      e = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = $(e);
      s && s.l(o), o.forEach(S), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      T(n, e, o), s && s.m(e, null), t[9](e), r = !0;
    },
    p(n, o) {
      s && s.p && (!r || o & /*$$scope*/
      64) && He(
        s,
        i,
        n,
        /*$$scope*/
        n[6],
        r ? ze(
          i,
          /*$$scope*/
          n[6],
          o,
          null
        ) : Me(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      r || (O(s, n), r = !0);
    },
    o(n) {
      W(s, n), r = !1;
    },
    d(n) {
      n && S(e), s && s.d(n), t[9](null);
    }
  };
}
function Je(t) {
  let e, r, i, s, n = (
    /*$$slots*/
    t[4].default && Q(t)
  );
  return {
    c() {
      e = te("react-portal-target"), r = Ge(), n && n.c(), i = H(), this.h();
    },
    l(o) {
      e = ee(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(e).forEach(S), r = Ne(o), n && n.l(o), i = H(), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      T(o, e, l), t[8](e), T(o, r, l), n && n.m(o, l), T(o, i, l), s = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, l), l & /*$$slots*/
      16 && O(n, 1)) : (n = Q(o), n.c(), O(n, 1), n.m(i.parentNode, i)) : n && (De(), W(n, 1, 1, () => {
        n = null;
      }), Fe());
    },
    i(o) {
      s || (O(n), s = !0);
    },
    o(o) {
      W(n), s = !1;
    },
    d(o) {
      o && (S(e), S(r), S(i)), t[8](null), n && n.d(o);
    }
  };
}
function q(t) {
  const {
    svelteInit: e,
    ...r
  } = t;
  return r;
}
function Xe(t, e, r) {
  let i, s, {
    $$slots: n = {},
    $$scope: o
  } = e;
  const l = We(n);
  let {
    svelteInit: d
  } = e;
  const p = P(q(e)), h = P();
  G(t, h, (a) => r(0, i = a));
  const c = P();
  G(t, c, (a) => r(1, s = a));
  const g = [], m = Qe("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: E,
    subSlotIndex: f
  } = ue() || {}, _ = d({
    parent: m,
    props: p,
    target: h,
    slot: c,
    slotKey: v,
    slotIndex: E,
    subSlotIndex: f,
    onDestroy(a) {
      g.push(a);
    }
  });
  Ve("$$ms-gr-react-wrapper", _), Ke(() => {
    p.set(q(e));
  }), qe(() => {
    g.forEach((a) => a());
  });
  function w(a) {
    B[a ? "unshift" : "push"](() => {
      i = a, h.set(i);
    });
  }
  function R(a) {
    B[a ? "unshift" : "push"](() => {
      s = a, c.set(s);
    });
  }
  return t.$$set = (a) => {
    r(17, e = U(U({}, e), K(a))), "svelteInit" in a && r(5, d = a.svelteInit), "$$scope" in a && r(6, o = a.$$scope);
  }, e = K(e), [i, s, h, c, l, d, o, n, w, R];
}
class Ye extends je {
  constructor(e) {
    super(), Ue(this, e, Xe, Je, Be, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ut
} = window.__gradio__svelte__internal, V = window.ms_globals.rerender, j = window.ms_globals.tree;
function Ze(t, e = {}) {
  function r(i) {
    const s = P(), n = new Ye({
      ...i,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: t,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: e.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, d = o.parent ?? j;
          return d.nodes = [...d.nodes, l], V({
            createPortal: F,
            node: j
          }), o.onDestroy(() => {
            d.nodes = d.nodes.filter((p) => p.svelteInstance !== s), V({
              createPortal: F,
              node: j
            });
          }), l;
        },
        ...i.props
      }
    });
    return s.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((s) => {
      window.ms_globals.initialize = () => {
        s();
      };
    })), window.ms_globals.initializePromise.then(() => {
      i(r);
    });
  });
}
function $e(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function et(t, e = !1) {
  try {
    if (de(t))
      return t;
    if (e && !$e(t))
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
function tt(t, e) {
  return re(() => et(t, e), [t, e]);
}
const nt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function rt(t) {
  return t ? Object.keys(t).reduce((e, r) => {
    const i = t[r];
    return e[r] = ot(r, i), e;
  }, {}) : {};
}
function ot(t, e) {
  return typeof e == "number" && !nt.includes(t) ? e + "px" : e;
}
function A(t) {
  const e = [], r = t.cloneNode(!1);
  if (t._reactElement) {
    const s = b.Children.toArray(t._reactElement.props.children).map((n) => {
      if (b.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = A(n.props.el);
        return b.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...b.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return s.originalChildren = t._reactElement.props.children, e.push(F(b.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: s
    }), r)), {
      clonedElement: r,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((s) => {
    t.getEventListeners(s).forEach(({
      listener: o,
      type: l,
      useCapture: d
    }) => {
      r.addEventListener(l, o, d);
    });
  });
  const i = Array.from(t.childNodes);
  for (let s = 0; s < i.length; s++) {
    const n = i[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: l
      } = A(n);
      e.push(...l), r.appendChild(o);
    } else n.nodeType === 3 && r.appendChild(n.cloneNode());
  }
  return {
    clonedElement: r,
    portals: e
  };
}
function st(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const J = oe(({
  slot: t,
  clone: e,
  className: r,
  style: i,
  observeAttributes: s
}, n) => {
  const o = se(), [l, d] = ie([]), {
    forceClone: p
  } = fe(), h = p ? !0 : e;
  return le(() => {
    var E;
    if (!o.current || !t)
      return;
    let c = t;
    function g() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), st(n, f), r && f.classList.add(...r.split(" ")), i) {
        const _ = rt(i);
        Object.keys(_).forEach((w) => {
          f.style[w] = _[w];
        });
      }
    }
    let m = null, v = null;
    if (h && window.MutationObserver) {
      let f = function() {
        var a, x, u;
        (a = o.current) != null && a.contains(c) && ((x = o.current) == null || x.removeChild(c));
        const {
          portals: w,
          clonedElement: R
        } = A(t);
        c = R, d(w), c.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          g();
        }, 50), (u = o.current) == null || u.appendChild(c);
      };
      f();
      const _ = Re(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      m = new window.MutationObserver(_), m.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (E = o.current) == null || E.appendChild(c);
    return () => {
      var f, _;
      c.style.display = "", (f = o.current) != null && f.contains(c) && ((_ = o.current) == null || _.removeChild(c)), m == null || m.disconnect();
    };
  }, [t, h, r, i, n, s, p]), b.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
}), it = ({
  children: t,
  ...e
}) => /* @__PURE__ */ C.jsx(C.Fragment, {
  children: t(e)
});
function lt(t) {
  return b.createElement(it, {
    children: t
  });
}
function X(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? lt((r) => /* @__PURE__ */ C.jsx(me, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ C.jsx(J, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...r
    })
  })) : /* @__PURE__ */ C.jsx(J, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function ct({
  key: t,
  slots: e,
  targets: r
}, i) {
  return e[t] ? (...s) => r ? r.map((n, o) => /* @__PURE__ */ C.jsx(b.Fragment, {
    children: X(n, {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ C.jsx(C.Fragment, {
    children: X(e[t], {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }) : void 0;
}
const dt = Ze(({
  setSlotParams: t,
  slots: e,
  statusRender: r,
  ...i
}) => {
  const s = tt(r);
  return /* @__PURE__ */ C.jsx(_e, {
    ...i,
    statusRender: e.statusRender ? ct({
      slots: e,
      key: "statusRender"
    }) : s
  });
});
export {
  dt as QRCode,
  dt as default
};
