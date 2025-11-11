import { i as le, a as W, r as ce, Z as T, g as ae, b as ue } from "./Index-B4dj81Oe.js";
const E = window.ms_globals.React, ne = window.ms_globals.React.forwardRef, re = window.ms_globals.React.useRef, oe = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, se = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, de = window.ms_globals.internalContext.useContextPropsContext, fe = window.ms_globals.antd.Tooltip;
var me = /\s/;
function pe(e) {
  for (var t = e.length; t-- && me.test(e.charAt(t)); )
    ;
  return t;
}
var _e = /^\s+/;
function he(e) {
  return e && e.slice(0, pe(e) + 1).replace(_e, "");
}
var z = NaN, ge = /^[-+]0x[0-9a-f]+$/i, we = /^0b[01]+$/i, be = /^0o[0-7]+$/i, ye = parseInt;
function D(e) {
  if (typeof e == "number")
    return e;
  if (le(e))
    return z;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = he(e);
  var o = we.test(e);
  return o || be.test(e) ? ye(e.slice(2), o ? 2 : 8) : ge.test(e) ? z : +e;
}
var L = function() {
  return ce.Date.now();
}, Ee = "Expected a function", ve = Math.max, Ce = Math.min;
function xe(e, t, o) {
  var s, i, n, r, l, d, _ = 0, h = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(Ee);
  t = D(t) || 0, W(o) && (h = !!o.leading, c = "maxWait" in o, n = c ? ve(D(o.maxWait) || 0, t) : n, g = "trailing" in o ? !!o.trailing : g);
  function m(u) {
    var b = s, S = i;
    return s = i = void 0, _ = u, r = e.apply(S, b), r;
  }
  function y(u) {
    return _ = u, l = setTimeout(p, t), h ? m(u) : r;
  }
  function v(u) {
    var b = u - d, S = u - _, M = t - b;
    return c ? Ce(M, n - S) : M;
  }
  function f(u) {
    var b = u - d, S = u - _;
    return d === void 0 || b >= t || b < 0 || c && S >= n;
  }
  function p() {
    var u = L();
    if (f(u))
      return w(u);
    l = setTimeout(p, v(u));
  }
  function w(u) {
    return l = void 0, g && s ? m(u) : (s = i = void 0, r);
  }
  function I() {
    l !== void 0 && clearTimeout(l), _ = 0, s = d = i = l = void 0;
  }
  function a() {
    return l === void 0 ? r : w(L());
  }
  function C() {
    var u = L(), b = f(u);
    if (s = arguments, i = this, d = u, b) {
      if (l === void 0)
        return y(d);
      if (c)
        return clearTimeout(l), l = setTimeout(p, t), m(d);
    }
    return l === void 0 && (l = setTimeout(p, t)), r;
  }
  return C.cancel = I, C.flush = a, C;
}
var Y = {
  exports: {}
}, P = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ie = E, Se = Symbol.for("react.element"), Re = Symbol.for("react.fragment"), Te = Object.prototype.hasOwnProperty, Oe = Ie.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ke = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Z(e, t, o) {
  var s, i = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) Te.call(t, s) && !ke.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: Se,
    type: e,
    key: n,
    ref: r,
    props: i,
    _owner: Oe.current
  };
}
P.Fragment = Re;
P.jsx = Z;
P.jsxs = Z;
Y.exports = P;
var R = Y.exports;
const {
  SvelteComponent: Pe,
  assign: U,
  binding_callbacks: B,
  check_outros: Le,
  children: Q,
  claim_element: $,
  claim_space: Fe,
  component_subscribe: G,
  compute_slots: Ne,
  create_slot: We,
  detach: x,
  element: ee,
  empty: H,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Ae,
  get_slot_changes: je,
  group_outros: Me,
  init: ze,
  insert_hydration: O,
  safe_not_equal: De,
  set_custom_element_data: te,
  space: Ue,
  transition_in: k,
  transition_out: A,
  update_slot_base: Be
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ge,
  getContext: He,
  onDestroy: Ke,
  setContext: qe
} = window.__gradio__svelte__internal;
function q(e) {
  let t, o;
  const s = (
    /*#slots*/
    e[7].default
  ), i = We(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ee("svelte-slot"), i && i.c(), this.h();
    },
    l(n) {
      t = $(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = Q(t);
      i && i.l(r), r.forEach(x), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), i && i.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      i && i.p && (!o || r & /*$$scope*/
      64) && Be(
        i,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? je(
          s,
          /*$$scope*/
          n[6],
          r,
          null
        ) : Ae(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (k(i, n), o = !0);
    },
    o(n) {
      A(i, n), o = !1;
    },
    d(n) {
      n && x(t), i && i.d(n), e[9](null);
    }
  };
}
function Ve(e) {
  let t, o, s, i, n = (
    /*$$slots*/
    e[4].default && q(e)
  );
  return {
    c() {
      t = ee("react-portal-target"), o = Ue(), n && n.c(), s = H(), this.h();
    },
    l(r) {
      t = $(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), Q(t).forEach(x), o = Fe(r), n && n.l(r), s = H(), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      O(r, t, l), e[8](t), O(r, o, l), n && n.m(r, l), O(r, s, l), i = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = q(r), n.c(), k(n, 1), n.m(s.parentNode, s)) : n && (Me(), A(n, 1, 1, () => {
        n = null;
      }), Le());
    },
    i(r) {
      i || (k(n), i = !0);
    },
    o(r) {
      A(n), i = !1;
    },
    d(r) {
      r && (x(t), x(o), x(s)), e[8](null), n && n.d(r);
    }
  };
}
function V(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function Je(e, t, o) {
  let s, i, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Ne(n);
  let {
    svelteInit: d
  } = t;
  const _ = T(V(t)), h = T();
  G(e, h, (a) => o(0, s = a));
  const c = T();
  G(e, c, (a) => o(1, i = a));
  const g = [], m = He("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: v,
    subSlotIndex: f
  } = ae() || {}, p = d({
    parent: m,
    props: _,
    target: h,
    slot: c,
    slotKey: y,
    slotIndex: v,
    subSlotIndex: f,
    onDestroy(a) {
      g.push(a);
    }
  });
  qe("$$ms-gr-react-wrapper", p), Ge(() => {
    _.set(V(t));
  }), Ke(() => {
    g.forEach((a) => a());
  });
  function w(a) {
    B[a ? "unshift" : "push"](() => {
      s = a, h.set(s);
    });
  }
  function I(a) {
    B[a ? "unshift" : "push"](() => {
      i = a, c.set(i);
    });
  }
  return e.$$set = (a) => {
    o(17, t = U(U({}, t), K(a))), "svelteInit" in a && o(5, d = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = K(t), [s, i, h, c, l, d, r, n, w, I];
}
class Xe extends Pe {
  constructor(t) {
    super(), ze(this, t, Je, Ve, De, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: it
} = window.__gradio__svelte__internal, J = window.ms_globals.rerender, F = window.ms_globals.tree;
function Ye(e, t = {}) {
  function o(s) {
    const i = T(), n = new Xe({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, d = r.parent ?? F;
          return d.nodes = [...d.nodes, l], J({
            createPortal: N,
            node: F
          }), r.onDestroy(() => {
            d.nodes = d.nodes.filter((_) => _.svelteInstance !== i), J({
              createPortal: N,
              node: F
            });
          }), l;
        },
        ...s.props
      }
    });
    return i.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((i) => {
      window.ms_globals.initialize = () => {
        i();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(o);
    });
  });
}
const Ze = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Qe(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const s = e[o];
    return t[o] = $e(o, s), t;
  }, {}) : {};
}
function $e(e, t) {
  return typeof t == "number" && !Ze.includes(e) ? t + "px" : t;
}
function j(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const i = E.Children.toArray(e._reactElement.props.children).map((n) => {
      if (E.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = j(n.props.el);
        return E.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...E.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(N(E.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: i
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((i) => {
    e.getEventListeners(i).forEach(({
      listener: r,
      type: l,
      useCapture: d
    }) => {
      o.addEventListener(l, r, d);
    });
  });
  const s = Array.from(e.childNodes);
  for (let i = 0; i < s.length; i++) {
    const n = s[i];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = j(n);
      t.push(...l), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function et(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const tt = ne(({
  slot: e,
  clone: t,
  className: o,
  style: s,
  observeAttributes: i
}, n) => {
  const r = re(), [l, d] = oe([]), {
    forceClone: _
  } = de(), h = _ ? !0 : t;
  return ie(() => {
    var v;
    if (!r.current || !e)
      return;
    let c = e;
    function g() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), et(n, f), o && f.classList.add(...o.split(" ")), s) {
        const p = Qe(s);
        Object.keys(p).forEach((w) => {
          f.style[w] = p[w];
        });
      }
    }
    let m = null, y = null;
    if (h && window.MutationObserver) {
      let f = function() {
        var a, C, u;
        (a = r.current) != null && a.contains(c) && ((C = r.current) == null || C.removeChild(c));
        const {
          portals: w,
          clonedElement: I
        } = j(e);
        c = I, d(w), c.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          g();
        }, 50), (u = r.current) == null || u.appendChild(c);
      };
      f();
      const p = xe(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      m = new window.MutationObserver(p), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (v = r.current) == null || v.appendChild(c);
    return () => {
      var f, p;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((p = r.current) == null || p.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, h, o, s, n, i, _]), E.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function nt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function rt(e, t = !1) {
  try {
    if (ue(e))
      return e;
    if (t && !nt(e))
      return;
    if (typeof e == "string") {
      let o = e.trim();
      return o.startsWith(";") && (o = o.slice(1)), o.endsWith(";") && (o = o.slice(0, -1)), new Function(`return (...args) => (${o})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function X(e, t) {
  return se(() => rt(e, t), [e, t]);
}
const st = Ye(({
  slots: e,
  afterOpenChange: t,
  getPopupContainer: o,
  children: s,
  ...i
}) => {
  const n = X(t), r = X(o);
  return /* @__PURE__ */ R.jsx(R.Fragment, {
    children: /* @__PURE__ */ R.jsx(fe, {
      ...i,
      afterOpenChange: n,
      getPopupContainer: r,
      title: e.title ? /* @__PURE__ */ R.jsx(tt, {
        slot: e.title
      }) : i.title,
      children: s
    })
  });
});
export {
  st as Tooltip,
  st as default
};
