import { i as le, a as j, r as ce, Z as R, g as ae, b as ue } from "./Index-CI3sANxB.js";
const y = window.ms_globals.React, ne = window.ms_globals.React.forwardRef, re = window.ms_globals.React.useRef, oe = window.ms_globals.React.useState, se = window.ms_globals.React.useEffect, ie = window.ms_globals.React.useMemo, W = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, de = window.ms_globals.antd.Image;
var me = /\s/;
function pe(e) {
  for (var t = e.length; t-- && me.test(e.charAt(t)); )
    ;
  return t;
}
var _e = /^\s+/;
function ge(e) {
  return e && e.slice(0, pe(e) + 1).replace(_e, "");
}
var z = NaN, he = /^[-+]0x[0-9a-f]+$/i, we = /^0b[01]+$/i, be = /^0o[0-7]+$/i, ve = parseInt;
function D(e) {
  if (typeof e == "number")
    return e;
  if (le(e))
    return z;
  if (j(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = j(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ge(e);
  var o = we.test(e);
  return o || be.test(e) ? ve(e.slice(2), o ? 2 : 8) : he.test(e) ? z : +e;
}
var P = function() {
  return ce.Date.now();
}, ye = "Expected a function", Ee = Math.max, Ce = Math.min;
function xe(e, t, o) {
  var i, s, n, r, l, f, _ = 0, g = !1, c = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(ye);
  t = D(t) || 0, j(o) && (g = !!o.leading, c = "maxWait" in o, n = c ? Ee(D(o.maxWait) || 0, t) : n, h = "trailing" in o ? !!o.trailing : h);
  function m(u) {
    var b = i, S = s;
    return i = s = void 0, _ = u, r = e.apply(S, b), r;
  }
  function v(u) {
    return _ = u, l = setTimeout(p, t), g ? m(u) : r;
  }
  function E(u) {
    var b = u - f, S = u - _, M = t - b;
    return c ? Ce(M, n - S) : M;
  }
  function d(u) {
    var b = u - f, S = u - _;
    return f === void 0 || b >= t || b < 0 || c && S >= n;
  }
  function p() {
    var u = P();
    if (d(u))
      return w(u);
    l = setTimeout(p, E(u));
  }
  function w(u) {
    return l = void 0, h && i ? m(u) : (i = s = void 0, r);
  }
  function I() {
    l !== void 0 && clearTimeout(l), _ = 0, i = f = s = l = void 0;
  }
  function a() {
    return l === void 0 ? r : w(P());
  }
  function C() {
    var u = P(), b = d(u);
    if (i = arguments, s = this, f = u, b) {
      if (l === void 0)
        return v(f);
      if (c)
        return clearTimeout(l), l = setTimeout(p, t), m(f);
    }
    return l === void 0 && (l = setTimeout(p, t)), r;
  }
  return C.cancel = I, C.flush = a, C;
}
var Y = {
  exports: {}
}, O = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ie = y, Se = Symbol.for("react.element"), Re = Symbol.for("react.fragment"), ke = Object.prototype.hasOwnProperty, Te = Ie.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Oe = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Z(e, t, o) {
  var i, s = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) ke.call(t, i) && !Oe.hasOwnProperty(i) && (s[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) s[i] === void 0 && (s[i] = t[i]);
  return {
    $$typeof: Se,
    type: e,
    key: n,
    ref: r,
    props: s,
    _owner: Te.current
  };
}
O.Fragment = Re;
O.jsx = Z;
O.jsxs = Z;
Y.exports = O;
var L = Y.exports;
const {
  SvelteComponent: Pe,
  assign: G,
  binding_callbacks: U,
  check_outros: Le,
  children: Q,
  claim_element: $,
  claim_space: Ne,
  component_subscribe: B,
  compute_slots: We,
  create_slot: je,
  detach: x,
  element: ee,
  empty: H,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Ae,
  get_slot_changes: Fe,
  group_outros: Me,
  init: ze,
  insert_hydration: k,
  safe_not_equal: De,
  set_custom_element_data: te,
  space: Ge,
  transition_in: T,
  transition_out: A,
  update_slot_base: Ue
} = window.__gradio__svelte__internal, {
  beforeUpdate: Be,
  getContext: He,
  onDestroy: Ke,
  setContext: qe
} = window.__gradio__svelte__internal;
function q(e) {
  let t, o;
  const i = (
    /*#slots*/
    e[7].default
  ), s = je(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ee("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      t = $(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = Q(t);
      s && s.l(r), r.forEach(x), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      k(n, t, r), s && s.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      s && s.p && (!o || r & /*$$scope*/
      64) && Ue(
        s,
        i,
        n,
        /*$$scope*/
        n[6],
        o ? Fe(
          i,
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
      o || (T(s, n), o = !0);
    },
    o(n) {
      A(s, n), o = !1;
    },
    d(n) {
      n && x(t), s && s.d(n), e[9](null);
    }
  };
}
function Ve(e) {
  let t, o, i, s, n = (
    /*$$slots*/
    e[4].default && q(e)
  );
  return {
    c() {
      t = ee("react-portal-target"), o = Ge(), n && n.c(), i = H(), this.h();
    },
    l(r) {
      t = $(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), Q(t).forEach(x), o = Ne(r), n && n.l(r), i = H(), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      k(r, t, l), e[8](t), k(r, o, l), n && n.m(r, l), k(r, i, l), s = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && T(n, 1)) : (n = q(r), n.c(), T(n, 1), n.m(i.parentNode, i)) : n && (Me(), A(n, 1, 1, () => {
        n = null;
      }), Le());
    },
    i(r) {
      s || (T(n), s = !0);
    },
    o(r) {
      A(n), s = !1;
    },
    d(r) {
      r && (x(t), x(o), x(i)), e[8](null), n && n.d(r);
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
  let i, s, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = We(n);
  let {
    svelteInit: f
  } = t;
  const _ = R(V(t)), g = R();
  B(e, g, (a) => o(0, i = a));
  const c = R();
  B(e, c, (a) => o(1, s = a));
  const h = [], m = He("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: E,
    subSlotIndex: d
  } = ae() || {}, p = f({
    parent: m,
    props: _,
    target: g,
    slot: c,
    slotKey: v,
    slotIndex: E,
    subSlotIndex: d,
    onDestroy(a) {
      h.push(a);
    }
  });
  qe("$$ms-gr-react-wrapper", p), Be(() => {
    _.set(V(t));
  }), Ke(() => {
    h.forEach((a) => a());
  });
  function w(a) {
    U[a ? "unshift" : "push"](() => {
      i = a, g.set(i);
    });
  }
  function I(a) {
    U[a ? "unshift" : "push"](() => {
      s = a, c.set(s);
    });
  }
  return e.$$set = (a) => {
    o(17, t = G(G({}, t), K(a))), "svelteInit" in a && o(5, f = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = K(t), [i, s, g, c, l, f, r, n, w, I];
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
} = window.__gradio__svelte__internal, J = window.ms_globals.rerender, N = window.ms_globals.tree;
function Ye(e, t = {}) {
  function o(i) {
    const s = R(), n = new Xe({
      ...i,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, f = r.parent ?? N;
          return f.nodes = [...f.nodes, l], J({
            createPortal: W,
            node: N
          }), r.onDestroy(() => {
            f.nodes = f.nodes.filter((_) => _.svelteInstance !== s), J({
              createPortal: W,
              node: N
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
      i(o);
    });
  });
}
const Ze = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Qe(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const i = e[o];
    return t[o] = $e(o, i), t;
  }, {}) : {};
}
function $e(e, t) {
  return typeof t == "number" && !Ze.includes(e) ? t + "px" : t;
}
function F(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const s = y.Children.toArray(e._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = F(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...y.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return s.originalChildren = e._reactElement.props.children, t.push(W(y.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: s
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((s) => {
    e.getEventListeners(s).forEach(({
      listener: r,
      type: l,
      useCapture: f
    }) => {
      o.addEventListener(l, r, f);
    });
  });
  const i = Array.from(e.childNodes);
  for (let s = 0; s < i.length; s++) {
    const n = i[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = F(n);
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
const X = ne(({
  slot: e,
  clone: t,
  className: o,
  style: i,
  observeAttributes: s
}, n) => {
  const r = re(), [l, f] = oe([]), {
    forceClone: _
  } = fe(), g = _ ? !0 : t;
  return se(() => {
    var E;
    if (!r.current || !e)
      return;
    let c = e;
    function h() {
      let d = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (d = c.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), et(n, d), o && d.classList.add(...o.split(" ")), i) {
        const p = Qe(i);
        Object.keys(p).forEach((w) => {
          d.style[w] = p[w];
        });
      }
    }
    let m = null, v = null;
    if (g && window.MutationObserver) {
      let d = function() {
        var a, C, u;
        (a = r.current) != null && a.contains(c) && ((C = r.current) == null || C.removeChild(c));
        const {
          portals: w,
          clonedElement: I
        } = F(e);
        c = I, f(w), c.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          h();
        }, 50), (u = r.current) == null || u.appendChild(c);
      };
      d();
      const p = xe(() => {
        d(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      m = new window.MutationObserver(p), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", h(), (E = r.current) == null || E.appendChild(c);
    return () => {
      var d, p;
      c.style.display = "", (d = r.current) != null && d.contains(c) && ((p = r.current) == null || p.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, g, o, i, n, s, _]), y.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function tt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function nt(e, t = !1) {
  try {
    if (ue(e))
      return e;
    if (t && !tt(e))
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
function rt(e, t) {
  return ie(() => nt(e, t), [e, t]);
}
function ot(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const lt = Ye(({
  slots: e,
  preview: t,
  ...o
}) => {
  const i = ot(t), s = e["preview.mask"] || e["preview.closeIcon"] || t !== !1, n = rt(i.getContainer);
  return /* @__PURE__ */ L.jsx(de.PreviewGroup, {
    ...o,
    preview: s ? {
      ...i,
      getContainer: n,
      ...e["preview.mask"] || Reflect.has(i, "mask") ? {
        mask: e["preview.mask"] ? /* @__PURE__ */ L.jsx(X, {
          slot: e["preview.mask"]
        }) : i.mask
      } : {},
      closeIcon: e["preview.closeIcon"] ? /* @__PURE__ */ L.jsx(X, {
        slot: e["preview.closeIcon"]
      }) : i.closeIcon
    } : !1
  });
});
export {
  lt as ImagePreviewGroup,
  lt as default
};
