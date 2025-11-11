import { i as ce, a as W, r as ae, Z as O, g as ue, b as de } from "./Index-C2JyghbH.js";
const v = window.ms_globals.React, re = window.ms_globals.React.forwardRef, oe = window.ms_globals.React.useRef, ie = window.ms_globals.React.useState, se = window.ms_globals.React.useEffect, le = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, me = window.ms_globals.antd.Popover;
var pe = /\s/;
function _e(e) {
  for (var t = e.length; t-- && pe.test(e.charAt(t)); )
    ;
  return t;
}
var he = /^\s+/;
function ge(e) {
  return e && e.slice(0, _e(e) + 1).replace(he, "");
}
var z = NaN, we = /^[-+]0x[0-9a-f]+$/i, be = /^0b[01]+$/i, ye = /^0o[0-7]+$/i, ve = parseInt;
function D(e) {
  if (typeof e == "number")
    return e;
  if (ce(e))
    return z;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ge(e);
  var o = be.test(e);
  return o || ye.test(e) ? ve(e.slice(2), o ? 2 : 8) : we.test(e) ? z : +e;
}
var L = function() {
  return ae.Date.now();
}, Ee = "Expected a function", Ce = Math.max, xe = Math.min;
function Ie(e, t, o) {
  var s, i, n, r, l, d, _ = 0, h = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(Ee);
  t = D(t) || 0, W(o) && (h = !!o.leading, c = "maxWait" in o, n = c ? Ce(D(o.maxWait) || 0, t) : n, g = "trailing" in o ? !!o.trailing : g);
  function m(u) {
    var b = s, S = i;
    return s = i = void 0, _ = u, r = e.apply(S, b), r;
  }
  function y(u) {
    return _ = u, l = setTimeout(p, t), h ? m(u) : r;
  }
  function E(u) {
    var b = u - d, S = u - _, M = t - b;
    return c ? xe(M, n - S) : M;
  }
  function f(u) {
    var b = u - d, S = u - _;
    return d === void 0 || b >= t || b < 0 || c && S >= n;
  }
  function p() {
    var u = L();
    if (f(u))
      return w(u);
    l = setTimeout(p, E(u));
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
var Z = {
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
var Se = v, Re = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), Te = Object.prototype.hasOwnProperty, Pe = Se.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ke = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(e, t, o) {
  var s, i = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) Te.call(t, s) && !ke.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: Re,
    type: e,
    key: n,
    ref: r,
    props: i,
    _owner: Pe.current
  };
}
k.Fragment = Oe;
k.jsx = Q;
k.jsxs = Q;
Z.exports = k;
var R = Z.exports;
const {
  SvelteComponent: Le,
  assign: U,
  binding_callbacks: B,
  check_outros: Fe,
  children: $,
  claim_element: ee,
  claim_space: Ne,
  component_subscribe: G,
  compute_slots: We,
  create_slot: je,
  detach: x,
  element: te,
  empty: H,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Ae,
  get_slot_changes: Me,
  group_outros: ze,
  init: De,
  insert_hydration: T,
  safe_not_equal: Ue,
  set_custom_element_data: ne,
  space: Be,
  transition_in: P,
  transition_out: j,
  update_slot_base: Ge
} = window.__gradio__svelte__internal, {
  beforeUpdate: He,
  getContext: Ke,
  onDestroy: qe,
  setContext: Ve
} = window.__gradio__svelte__internal;
function q(e) {
  let t, o;
  const s = (
    /*#slots*/
    e[7].default
  ), i = je(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = te("svelte-slot"), i && i.c(), this.h();
    },
    l(n) {
      t = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = $(t);
      i && i.l(r), r.forEach(x), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      T(n, t, r), i && i.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      i && i.p && (!o || r & /*$$scope*/
      64) && Ge(
        i,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Me(
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
      o || (P(i, n), o = !0);
    },
    o(n) {
      j(i, n), o = !1;
    },
    d(n) {
      n && x(t), i && i.d(n), e[9](null);
    }
  };
}
function Je(e) {
  let t, o, s, i, n = (
    /*$$slots*/
    e[4].default && q(e)
  );
  return {
    c() {
      t = te("react-portal-target"), o = Be(), n && n.c(), s = H(), this.h();
    },
    l(r) {
      t = ee(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(t).forEach(x), o = Ne(r), n && n.l(r), s = H(), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      T(r, t, l), e[8](t), T(r, o, l), n && n.m(r, l), T(r, s, l), i = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && P(n, 1)) : (n = q(r), n.c(), P(n, 1), n.m(s.parentNode, s)) : n && (ze(), j(n, 1, 1, () => {
        n = null;
      }), Fe());
    },
    i(r) {
      i || (P(n), i = !0);
    },
    o(r) {
      j(n), i = !1;
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
function Xe(e, t, o) {
  let s, i, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = We(n);
  let {
    svelteInit: d
  } = t;
  const _ = O(V(t)), h = O();
  G(e, h, (a) => o(0, s = a));
  const c = O();
  G(e, c, (a) => o(1, i = a));
  const g = [], m = Ke("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: E,
    subSlotIndex: f
  } = ue() || {}, p = d({
    parent: m,
    props: _,
    target: h,
    slot: c,
    slotKey: y,
    slotIndex: E,
    subSlotIndex: f,
    onDestroy(a) {
      g.push(a);
    }
  });
  Ve("$$ms-gr-react-wrapper", p), He(() => {
    _.set(V(t));
  }), qe(() => {
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
class Ye extends Le {
  constructor(t) {
    super(), De(this, t, Xe, Je, Ue, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: it
} = window.__gradio__svelte__internal, J = window.ms_globals.rerender, F = window.ms_globals.tree;
function Ze(e, t = {}) {
  function o(s) {
    const i = O(), n = new Ye({
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
const Qe = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function $e(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const s = e[o];
    return t[o] = et(o, s), t;
  }, {}) : {};
}
function et(e, t) {
  return typeof t == "number" && !Qe.includes(e) ? t + "px" : t;
}
function A(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const i = v.Children.toArray(e._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = A(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...v.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(N(v.cloneElement(e._reactElement, {
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
      } = A(n);
      t.push(...l), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function tt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const X = re(({
  slot: e,
  clone: t,
  className: o,
  style: s,
  observeAttributes: i
}, n) => {
  const r = oe(), [l, d] = ie([]), {
    forceClone: _
  } = fe(), h = _ ? !0 : t;
  return se(() => {
    var E;
    if (!r.current || !e)
      return;
    let c = e;
    function g() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), tt(n, f), o && f.classList.add(...o.split(" ")), s) {
        const p = $e(s);
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
        } = A(e);
        c = I, d(w), c.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          g();
        }, 50), (u = r.current) == null || u.appendChild(c);
      };
      f();
      const p = Ie(() => {
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
      c.style.display = "contents", g(), (E = r.current) == null || E.appendChild(c);
    return () => {
      var f, p;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((p = r.current) == null || p.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, h, o, s, n, i, _]), v.createElement("react-child", {
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
    if (de(e))
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
function Y(e, t) {
  return le(() => rt(e, t), [e, t]);
}
const st = Ze(({
  slots: e,
  afterOpenChange: t,
  getPopupContainer: o,
  children: s,
  ...i
}) => {
  const n = Y(t), r = Y(o);
  return /* @__PURE__ */ R.jsx(R.Fragment, {
    children: /* @__PURE__ */ R.jsx(me, {
      ...i,
      afterOpenChange: n,
      getPopupContainer: r,
      title: e.title ? /* @__PURE__ */ R.jsx(X, {
        slot: e.title
      }) : i.title,
      content: e.content ? /* @__PURE__ */ R.jsx(X, {
        slot: e.content
      }) : i.content,
      children: s
    })
  });
});
export {
  st as Popover,
  st as default
};
